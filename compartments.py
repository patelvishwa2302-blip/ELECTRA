# compartments.py
# Electra — which compartment each medicine lives in.
#
# WHY THIS IS A SEPARATE STORE (and not a field in database.py):
#   The compartment is NOT a property of the medicine. Voveran could sit in
#   drawer 3 in one home and drawer 1 in another. It is a property of THIS
#   box's arrangement, so it is set from the dashboard when a tag is assigned,
#   and kept here — next to tag_map.json, which is the same kind of fact.
#
# THE DOSE TIME DECIDES THE COMPARTMENT. That mapping lives in ONE place,
# below. Change it here and the whole system follows.

import json
import os
import threading

_HERE = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(_HERE, "compartments.json")
_lock = threading.Lock()

# ─── the one place the dose -> compartment rule lives ────────────────────
DOSE_TO_COMPARTMENT = {
    "morning":   1,
    "afternoon": 2,
    "evening":   2,
    "night":     3,
}
COMPARTMENT_TO_DOSE = {
    1: "Morning",
    2: "Afternoon / Evening",
    3: "Night",
}
DEFAULT_COMPARTMENT = 3        # used when we do not know where a medicine lives


def _load():
    """medicine_key -> compartment, restored from disk on every call."""
    if not os.path.exists(FILE):
        return {}
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save(mapping):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)


# ─── what the risk engine calls ──────────────────────────────────────────
def compartment_for(medicine_key, default=DEFAULT_COMPARTMENT):
    """Which compartment holds this medicine.

    Falls back to DEFAULT_COMPARTMENT (3) when we have not been told — which
    is exactly what the engine did before this existed, so nothing breaks if
    the dashboard has not set anything yet.
    """
    with _lock:
        try:
            return int(_load().get(str(medicine_key), default))
        except (TypeError, ValueError):
            return default


# ─── what the dashboard calls ────────────────────────────────────────────
def set_compartment(medicine_key, compartment):
    """Record where a medicine lives. compartment must be 1, 2 or 3."""
    try:
        c = int(compartment)
    except (TypeError, ValueError):
        return {"ok": False, "error": "compartment must be 1, 2 or 3"}
    if c not in (1, 2, 3):
        return {"ok": False, "error": "compartment must be 1, 2 or 3"}

    with _lock:
        m = _load()
        m[str(medicine_key)] = c
        _save(m)
    return {"ok": True, "medicine": medicine_key, "compartment": c,
            "dose": COMPARTMENT_TO_DOSE.get(c, "")}


def set_from_dose(medicine_key, dose):
    """Set the compartment from a dose time — 'morning', 'afternoon', 'night'."""
    c = DOSE_TO_COMPARTMENT.get(str(dose).strip().lower())
    if not c:
        return {"ok": False,
                "error": "dose must be one of: " + ", ".join(sorted(DOSE_TO_COMPARTMENT))}
    return set_compartment(medicine_key, c)


def clear_compartment(medicine_key):
    with _lock:
        m = _load()
        m.pop(str(medicine_key), None)
        _save(m)
    return {"ok": True, "medicine": medicine_key, "compartment": None}


def all_compartments():
    """Everything the dashboard needs to show and set the arrangement."""
    with _lock:
        m = dict(_load())
    return {
        "compartments": m,
        "labels": {str(k): v for k, v in COMPARTMENT_TO_DOSE.items()},
        "doses": DOSE_TO_COMPARTMENT,
        "default": DEFAULT_COMPARTMENT,
    }
