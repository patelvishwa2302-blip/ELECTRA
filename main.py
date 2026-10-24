# main.py

from fastapi import FastAPI, UploadFile, File
from typing import List
from pydantic import BaseModel


from fastapi.middleware.cors import CORSMiddleware
from models import AnalyzeRequest, AnalyzeResponse, SimulateRemoveRequest, SimulateRemoveResponse
from risk_engine import analyze_medicines
from database import MEDICINES
from whatsapp import send_whatsapp_alert
from tag_registry import resolve_tag, add_pending, get_pending, enroll_tag, unenroll_tag, all_tags
from compartments import (set_from_dose, set_compartment, all_compartments,
                          compartment_for)
import json, os
from datetime import datetime
from fastapi.encoders import jsonable_encoder      # serialises the alert objects for saving


LOCK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lock_state.json")

LAST_ANALYSIS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "last_analysis.json")

# When did the box last ask for its lock state? The box polls every 10 seconds,
# so a recent poll means a box is actually connected and listening.
LAST_BOX_POLL = None


# NOTE: imported ONCE. This line used to appear twice in the file - harmless,
# but it made the file harder to read.
from scheduler import get_schedule, save_schedule, test_reminder, start_reminder_loop
from ocr import extract_medicines_from_image


class ScheduleEntry(BaseModel):
    time: str
    medicines: List[str] = []
    note: str = ""


app = FastAPI(
    title="Electra — Polypharmacy Risk API",
    description="AI-powered drug interaction detection for Indian patients",
    version="1.0.0"
)

# Allow dashboard + ESP32 to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "Electra backend running", "version": "1.0.0"}


@app.get("/medicines")
def list_medicines():
    """Return all medicines for dashboard autocomplete."""
    return {
        key: {
            "brand": val["brand"],
            "generic": val["generic"],
            "class": val["therapeutic_class"]
        }
        for key, val in MEDICINES.items()
    }


@app.get("/tags")
def list_tags():
    """Tag -> medicine map, display names for the box, and unassigned tags."""
    return all_tags()


@app.post("/enroll-tag")
def enroll_tag_endpoint(payload: dict):
    """Assign a medicine to a tag UID (the dashboard's Assign button).

    If the dashboard sends a dose time with it, remember which compartment
    that means — so the box locks the right drawer later.
    """
    result = enroll_tag(payload.get("uid", ""), payload.get("medicine", ""))
    if result.get("ok") and payload.get("dose"):
        set_from_dose(result["medicine"], payload["dose"])
        result["compartment"] = compartment_for(result["medicine"])
    return result


@app.get("/compartments")
def list_compartments():
    """Which compartment each medicine lives in (the dashboard's arrangement)."""
    return all_compartments()


@app.post("/set-compartment")
def set_compartment_endpoint(payload: dict):
    """Set where a medicine lives. Send a dose ('morning') or a number (1/2/3)."""
    med = payload.get("medicine", "")
    if payload.get("dose"):
        return set_from_dose(med, payload["dose"])
    return set_compartment(med, payload.get("compartment"))


@app.delete("/tag/{uid}")
def delete_tag(uid: str):
    """Un-assign a tag."""
    return unenroll_tag(uid)


# ═══════════════════════════════════════════════════════════════════════════
#  ANALYZE  —  THE FIX THAT MATTERS
#
#  This used to be `async def analyze(...)`. It is now a plain `def`.
#
#  WHY THIS MATTERS:
#  The function body has NO `await` in it. Everything in it is blocking -
#  the rule engine, and especially the WhatsApp HTTP call, which can take
#  several seconds.
#
#  An `async def` with no `await` runs ON the server's event loop. So while
#  one request waits for WhatsApp, the whole server stops - no other request
#  is served. That is what caused the box's "HTTP error -11" timeouts: the
#  box's own request, or another one, would sit waiting.
#
#  A plain `def` is run by FastAPI in a worker thread instead. Blocking is
#  then fine - other requests are served normally. This is the correct form
#  for a synchronous function.
# ═══════════════════════════════════════════════════════════════════════════
@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    """Main analysis endpoint — called by ESP32 firmware and web dashboard."""
    # --- NFC tags are resolved through the live tag map (tag_map.json) ---
    pending_tags = []
    if request.scanned_tags:
        medicines = []
        for uid in request.scanned_tags:
            key = resolve_tag(uid)
            if key:
                medicines.append(key)
            else:
                add_pending(uid)          # so the dashboard can show it
                pending_tags.append(uid)
        seen, unique = set(), []
        for m in medicines:
            if m.lower() not in seen:
                seen.add(m.lower())
                unique.append(m)
        medicines = unique
    else:
        medicines = list(request.scanned_medicines)

    result = analyze_medicines(
        scanned_brands=medicines,
        ayurvedic_list=request.ayurvedic_medicines,
        food_list=request.foods,
        patient=request.patient
    )
    result["pending_tags"] = pending_tags

    # If tags were tapped but none is assigned, do NOT claim "all safe".
    if pending_tags and not medicines:
        result["overall_risk"] = "moderate"
        result["display_text"] = "UNKNOWN TAG\nAssign it on\nthe dashboard"

    # WhatsApp alert on HIGH/CRITICAL
    whatsapp_sent = False
    if result["overall_risk"] in ["high", "critical"] and request.patient.caregiver_phone:
        top_alert = result["alerts"][0] if result["alerts"] else None
        if top_alert:
            summary = f"{top_alert.name}: {', '.join(top_alert.medicines_involved[:2])}"
            whatsapp_sent = send_whatsapp_alert(
                phone=request.patient.caregiver_phone,
                risk_level=result["overall_risk"].upper(),
                summary=summary,
                action=top_alert.action
            )

    result["whatsapp_sent"] = whatsapp_sent

    # send the current tag names back, so the box's local copy never goes stale
    result["tag_names"] = all_tags()["display"]

    # ── save this analysis, so the dashboard can show what the BOX just did ──
    # jsonable_encoder is needed because the alerts are objects, not plain dicts.
    try:
        with open(LAST_ANALYSIS_FILE, "w", encoding="utf-8") as f:
            json.dump(jsonable_encoder({
                **result,
                "analysed_at": datetime.now().isoformat(),
                "source": getattr(request, "device_id", "unknown"),
            }), f, indent=2)
    except Exception as e:
        print("could not save last analysis:", e)

    # ── record the lock, so the caregiver can clear it and the box can see that ──
    # WITHOUT THIS the dashboard never learns a lock happened, and the Unlock
    # button has nothing to clear.
    if result.get("lock_compartments"):
        with open(LOCK_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "locked": result["lock_compartments"],
                "hold_backs": result.get("hold_backs", []),
                "locked_at": datetime.now().isoformat(),
            }, f, indent=2)

    return result


# Same reason as /analyze: no `await` in the body, so a plain def.
@app.post("/simulate-remove", response_model=SimulateRemoveResponse)
def simulate_remove(request: SimulateRemoveRequest):
    """Deprescribing simulator — what happens if we remove one medicine?"""
    # Original analysis
    original = analyze_medicines(
        scanned_brands=request.scanned_medicines,
        ayurvedic_list=request.ayurvedic_medicines,
        food_list=request.foods,
        patient=request.patient
    )

    # Analysis with medicine removed
    filtered = [m for m in request.scanned_medicines
                if request.remove_medicine.lower() not in m.lower()]
    new_result = analyze_medicines(
        scanned_brands=filtered,
        ayurvedic_list=request.ayurvedic_medicines,
        food_list=request.foods,
        patient=request.patient
    )

    # Find a suitable alternative
    alternatives = {
        "nsaid": "Paracetamol 500mg (Crocin)",
        "benzodiazepine": "Low-dose Melatonin or CBT for insomnia",
        "antihistamine": "Montelukast (Montair) — non-sedating",
        "opioid": "Tramadol + Paracetamol combination at lower dose"
    }
    suggested_alt = None
    for cls, alt in alternatives.items():
        if cls in request.remove_medicine.lower():
            suggested_alt = alt

    return {
        "original_risk": original["overall_risk"],
        "new_risk": new_result["overall_risk"],
        "deprescribe_result": {
            "removed_medicine": request.remove_medicine,
            "new_severity": new_result["overall_risk"],
            "risk_reduction": f"{original['overall_risk'].upper()} → {new_result['overall_risk'].upper()}",
            "suggested_alternative": suggested_alt
        },
        "all_original_alerts": original["alerts"],
        "remaining_alerts": new_result["alerts"]
    }


# This one STAYS async - it genuinely awaits the file read.
@app.post("/scan-prescription")
async def scan_prescription(image: UploadFile = File(...)):
    """Prescription photo OCR - reads medicine names via Gemini."""
    contents = await image.read()
    return extract_medicines_from_image(contents, image.content_type)


# ══════════════ DOSE REMINDERS ══════════════

@app.get("/schedule")
def list_schedule():
    """The dose times the family set on the dashboard."""
    return get_schedule()


@app.post("/schedule")
def set_schedule(payload: List[ScheduleEntry]):
    """Save the whole schedule (the dashboard sends the list)."""
    return save_schedule([entry.model_dump() for entry in payload])


@app.post("/schedule/test")
def send_test_reminder():
    """Send a WhatsApp reminder right now (demos / token checks)."""
    return test_reminder()


# ══════════════ COMPARTMENT LOCK ══════════════

@app.get("/lock-state")
def lock_state():
    """What the BOX polls: which compartments are locked right now.

    A lock clears itself after 30 minutes, so nobody is ever stranded
    without their medicines. That is deliberate — a lock with no way out
    is dangerous.
    """
    global LAST_BOX_POLL
    LAST_BOX_POLL = datetime.now()      # a box just checked in

    try:
        with open(LOCK_FILE, encoding="utf-8") as f:
            state = json.load(f)
    except Exception:
        state = {"locked": [], "hold_backs": []}

    locked_at = state.get("locked_at")
    if locked_at:
        try:
            age = (datetime.now() - datetime.fromisoformat(locked_at)).total_seconds()
            if age > 1800:                      # 30 minutes
                state = {"locked": [], "hold_backs": [], "auto_released": True}
                with open(LOCK_FILE, "w", encoding="utf-8") as f:
                    json.dump(state, f, indent=2)
        except Exception:
            pass
    return state


@app.post("/unlock")
def unlock():
    """The caregiver opens it again from the dashboard."""
    state = {"locked": [], "hold_backs": [],
             "unlocked_at": datetime.now().isoformat()}
    with open(LOCK_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    return {"ok": True, "locked": []}


@app.get("/last-analysis")
def last_analysis():
    """The most recent analysis - whoever ran it, the box or the dashboard."""
    try:
        with open(LAST_ANALYSIS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"none": True}


@app.get("/box-status")
def box_status():
    """Is a box actually connected?

    The box polls /lock-state every 10 seconds. If it has polled recently, a
    real box is listening - which means a lock it is showing is a REAL lock,
    not just a recommendation.

    The window is 60 seconds, not 30: the box polls every 10 s, so 60 gives
    room for one slow poll without the dashboard flickering to "no box".
    """
    if LAST_BOX_POLL is None:
        return {"connected": False, "seconds_ago": None}
    secs = int((datetime.now() - LAST_BOX_POLL).total_seconds())
    return {"connected": secs <= 60, "seconds_ago": secs}


# ══════════════ START THE BACKGROUND LOOP LAST ══════════════
# This starts the reminder thread. It used to sit in the middle of the file,
# which meant the thread could start before the routes above were defined.
start_reminder_loop()

