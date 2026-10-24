# tag_registry.py
# Electra - live NFC tag registry (Option 3: enroll tags on the spot)
#
# WHAT THIS DOES
#   The tag -> medicine table now lives HERE (in tag_map.json, created
#   automatically next to this file) instead of inside the firmware.
#   The box sends the raw tag UID; this module resolves it to a medicine.
#   An unknown tag is remembered as "pending" so the dashboard can ask
#   "which medicine is this?" and save the answer in seconds.
#
#   The map starts EMPTY. No medicine is pre-assigned to any tag.
#
# USED BY main.py:
#   from tag_registry import resolve_tag, add_pending, get_pending, enroll_tag, all_tags

import json
import os
import threading

_HERE = os.path.dirname(os.path.abspath(__file__))
MAP_FILE = os.path.join(_HERE, "tag_map.json")

# NOTHING IS PRE-CODED. The tag map starts EMPTY on purpose: the dashboard
# (or a hand edit of tag_map.json) is the only thing that decides what a tag
# means. Delete tag_map.json any time to start from zero again.
_DEFAULT_MAP = {}

_lock = threading.Lock()
_pending = []          # UIDs tapped but not yet enrolled (most recent first)


def _norm(uid):
    """Normalise a UID to the 'XX XX XX XX' uppercase form."""
    return " ".join(str(uid).strip().upper().split())


def _load():
    if not os.path.exists(MAP_FILE):
        _save(dict(_DEFAULT_MAP))
        return dict(_DEFAULT_MAP)
    try:
        with open(MAP_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {_norm(k): v for k, v in data.items()}
    except Exception:
        return dict(_DEFAULT_MAP)


def _save(mapping):
    with open(MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)


def resolve_tag(uid):
    """Return the medicine key for a tag UID, or None if not enrolled."""
    with _lock:
        return _load().get(_norm(uid))


def add_pending(uid):
    """Remember a UID that was tapped but is not enrolled yet."""
    global _pending
    u = _norm(uid)
    with _lock:
        if u and u not in _pending:
            _pending.insert(0, u)
            del _pending[10:]          # keep only the last 10


def get_pending():
    with _lock:
        return list(_pending)


def clear_pending(uid=None):
    global _pending
    with _lock:
        if uid is None:
            _pending = []
        else:
            _pending = [u for u in _pending if u != _norm(uid)]


def enroll_tag(uid, medicine_key):
    """Assign a medicine to a tag. Accepts a database key or a brand name."""
    from database import MEDICINES
    global _pending

    key = str(medicine_key).strip()
    if key not in MEDICINES:
        match = None
        for k, v in MEDICINES.items():
            if v["brand"].lower() == key.lower() or k.lower() == key.lower():
                match = k
                break
        if not match:
            return {"ok": False,
                    "error": "'%s' is not in the medicine database" % medicine_key}
        key = match

    u = _norm(uid)
    if not u:
        return {"ok": False, "error": "empty tag UID"}

    with _lock:
        m = _load()
        m[u] = key
        _save(m)
        _pending = [p for p in _pending if p != u]

    return {"ok": True, "uid": u, "medicine": key,
            "brand": MEDICINES[key]["brand"]}


def unenroll_tag(uid):
    u = _norm(uid)
    with _lock:
        m = _load()
def unenroll_tag(uid):
    u = _norm(uid)
    removed = False
    with _lock:
        m = _load()
        if u in m:
            del m[u]
            _save(m)
            removed = True
    # add_pending() takes the same lock, so it must be called AFTER the
    # with-block above has released it. Calling it inside would deadlock.
    if removed:
        add_pending(u)
        return {"ok": True, "uid": u}
    return {"ok": False, "error": "tag not enrolled"}




def display_map():
    """UID -> brand name (this is what the box shows on its OLED screen)."""
    from database import MEDICINES
    with _lock:
        m = _load()
    out = {}
    for uid, key in m.items():
        brand = MEDICINES.get(key, {}).get("brand", key)
        out[uid] = brand
    return out


def all_tags():
    """Everything the dashboard and the box need in one call."""
    with _lock:
        m = _load()
        pend = list(_pending)
    return {"map": m, "display": display_map(), "pending": pend}
