# scheduler.py
# Electra - dose reminders: the box's alarm times + the WhatsApp reminder sender.
#
# WHAT THIS DOES
#   1. Stores the family's dose times in schedule.json (next to this file).
#   2. Runs a background loop that sends the WhatsApp reminder when a dose is due.
#   3. Lets the dashboard read/save the schedule and fire a test reminder.
#
# The BOX gets its alarm times from GET /schedule (the firmware downloads them).

import datetime
import json
import os
import threading
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
SCHEDULE_FILE = os.path.join(_HERE, "schedule.json")

_lock = threading.Lock()
_fired = {}                 # {"2026-10-20 08:00": True} - already sent today
_started = False

DEFAULT_CAREGIVER = "+918849065660"


def _load():
    if not os.path.exists(SCHEDULE_FILE):
        _save([])
        return []
    try:
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save(entries):
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


def get_schedule():
    with _lock:
        return _load()


def save_schedule(entries):
    """entries: [{"time":"08:00","medicines":["Glycomet 500"],"note":"with breakfast"}]"""
    clean = []
    for e in entries or []:
        t = str(e.get("time", "")).strip()
        if not t or ":" not in t:
            continue
        clean.append({
            "time": t[:5],                                  # "HH:MM"
            "medicines": [str(m) for m in e.get("medicines", [])],
            "note": str(e.get("note", "")),
        })
    clean.sort(key=lambda x: x["time"])
    with _lock:
        _save(clean)
    return {"ok": True, "count": len(clean), "schedule": clean}


def send_reminder(entry, caregiver_phone=None):
    """Send one WhatsApp reminder for a schedule entry.

    Prefers the approved "electra_reminder" template (clean reminder wording).
    If that function isn't in whatsapp.py yet, it falls back to the alert
    template with reminder-friendly wording, so reminders never stop working.
    """
    meds = ", ".join(entry.get("medicines", [])) or "your medicines"
    note = entry.get("note") or ""
    phone = caregiver_phone or DEFAULT_CAREGIVER

    # 1. preferred — the dedicated reminder template
    try:
        from whatsapp import send_whatsapp_reminder
        return send_whatsapp_reminder(phone, meds, note)
    except ImportError:
        pass

    # 2. fallback — the alert template, reworded to read like a reminder
    from whatsapp import send_whatsapp_alert
    action = ("Take " + note) if note else "Take as prescribed"
    return send_whatsapp_alert(
        phone=phone,
        risk_level="\u23f0 REMINDER",
        summary="Time to take " + meds,
        action=action,
    )


def test_reminder(medicines=None, caregiver_phone=None):
    """Send a reminder right now - for the demo and for checking the token."""
    now = datetime.datetime.now().strftime("%H:%M")
    entry = {"time": now,
             "medicines": medicines or ["Glycomet 500"],
             "note": "with breakfast"}
    ok = send_reminder(entry, caregiver_phone)
    return {"ok": bool(ok), "sent": entry["medicines"], "at": now}


def fired_today():
    today = datetime.date.today().isoformat()
    return [k for k in _fired if k.startswith(today)]


def _loop(interval=30):
    while True:
        try:
            now = datetime.datetime.now()
            key = now.strftime("%Y-%m-%d %H:%M")
            for entry in get_schedule():
                if entry.get("time") == now.strftime("%H:%M"):
                    k = now.strftime("%Y-%m-%d") + " " + entry["time"]
                    if not _fired.get(k):
                        _fired[k] = True
                        print("[reminder] sending WhatsApp reminder for "
                              + ", ".join(entry.get("medicines", [])))
                        send_reminder(entry)
        except Exception as e:
            print("[reminder] error:", e)
        time.sleep(interval)


def start_reminder_loop(interval=30):
    """Start the background reminder thread. Call once from main.py."""
    global _started
    if _started:
        return
    _started = True
    threading.Thread(target=_loop, args=(interval,), daemon=True).start()
    print("[reminder] background reminder loop started (every %ss)" % interval)
