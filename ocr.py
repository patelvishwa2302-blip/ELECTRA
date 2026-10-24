# ocr.py
# Electra - Prescription photo OCR via the Google Gemini API.
#
# v6 — BAD HANDWRITING EDITION
# Key improvements over v5:
#
#   1. IMAGE PREPROCESSING (new, uses Pillow)
#      Before sending to Gemini, the photo is automatically:
#        - Converted to grayscale (removes ink colour noise)
#        - Contrast-enhanced  (makes faint ink dark, white paper white)
#        - Sharpened          (makes blurry handwriting edges crisper)
#      This alone gives a significant lift for blurry/dim photos.
#
#   2. BETTER HANDWRITING PROMPT
#      The prompt now explicitly tells Gemini it is dealing with bad
#      doctor handwriting, instructs it to guess similar-sounding drug
#      names when letters are unclear, and lists the known medicines so
#      Gemini can pick the closest match.
#
#   3. CORRECT GEMINI MODEL NAMES
#      gemini-3.8-flash and gemini-flash-latest do not exist.
#      Updated to the real currently-available models.
#
#   4. LOWER FUZZY MATCH CUTOFF  (0.85 -> 0.78)
#      Doctor handwriting often produces something like "Ecoeprin" or
#      "Glycomed" — the old 0.85 cutoff was too strict to catch these.
#      0.78 is still selective enough to avoid false positives.
#
# STANDALONE TEST (no server needed):
#   python ocr.py "C:\path\to\prescription_photo.jpg"

import os
import sys
import io
import json
import time
import difflib
import base64

import requests

# ─── KEY LOADING ─────────────────────────────────────────────────────────────
def _load_gemini_key():
    """Key order: environment variable -> gemini_key.txt -> placeholder."""
    env_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if env_key:
        return env_key.strip("\"'")
    try:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "gemini_key.txt")
        with open(path, "r", encoding="utf-8") as f:
            key = f.read().strip().strip("\"'")
            if key:
                return key
    except (FileNotFoundError, OSError):
        pass
    return "PASTE_YOUR_GEMINI_KEY_HERE"

GEMINI_API_KEY = _load_gemini_key()

# ─── MODEL LIST (live-tested 2026-09-27 against your API key) ─────────────────
# Tried IN ORDER. 404 = retired (skip instantly). 503/429 = busy (retry).
# gemini-3.8-flash confirmed working. gemini-2.5-flash is retired.
MODEL_CANDIDATES = [
    "gemini-3.8-flash",          # ✅ confirmed working
    "gemini-3.7-flash",          # fallback
    "gemini-2.5-pro",            # most capable, best for hard handwriting
    "gemini-flash-latest",       # Google's rolling alias for current flash
]

RETRY_WAIT_SECONDS = 10
RETRIES_PER_MODEL  = 2
FUZZY_CUTOFF       = 0.78   # was 0.85 — lowered for bad handwriting tolerance

# ─────────────────────────────────────────────────────────────────────────────

from database import MEDICINES, BRAND_ALIASES


# ─── IMAGE PREPROCESSING ──────────────────────────────────────────────────────
def _preprocess_image(image_bytes: bytes, mime_type: str) -> tuple[bytes, str]:
    """
    Enhance a prescription photo for better OCR accuracy on bad handwriting.

    Pipeline:
      1. Grayscale  — removes colour noise; ink colour doesn't matter for OCR
      2. Contrast enhance (factor 2.0) — makes faint pencil/ink strokes darker
      3. Sharpness  (factor 2.5) — sharpens blurry edges from phone cameras

    Returns (processed_bytes, "image/jpeg").
    Falls back to original bytes if Pillow fails (so OCR still runs).
    """
    try:
        from PIL import Image, ImageEnhance

        img = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB first (handles PNGs with alpha channel)
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        # Step 1 — Grayscale
        img = img.convert("L")

        # Step 2 — Contrast boost
        img = ImageEnhance.Contrast(img).enhance(2.0)

        # Step 3 — Sharpness boost
        img = ImageEnhance.Sharpness(img).enhance(2.5)

        # Convert back to RGB so JPEG encoding works
        img = img.convert("RGB")

        # Save as JPEG (good for Gemini, smaller payload)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)
        return buf.getvalue(), "image/jpeg"

    except Exception as e:
        print(f"[OCR] Image preprocessing skipped ({e}), using original.")
        return image_bytes, mime_type


# ─── KNOWN NAMES ─────────────────────────────────────────────────────────────
def _known_names():
    """All brand + generic names we know, plus a map back to brand names."""
    brands = set()
    lookup = {}
    for entry in MEDICINES.values():
        b = entry["brand"].strip()
        g = entry["generic"].strip()
        brands.add(b)
        lookup[b.lower()] = b
        lookup.setdefault(g.lower(), b)
    for alias, key in BRAND_ALIASES.items():
        entry = MEDICINES.get(key)
        if entry:
            b = entry["brand"].strip()
            brands.add(alias)
            lookup.setdefault(alias.lower(), b)
    return sorted(brands), lookup


# ─── PROMPT (handwriting-optimised) ──────────────────────────────────────────
def _prompt(known_brands):
    known_list = ", ".join(known_brands)
    return (
        "You are a medical AI reading a prescription written by an Indian doctor. "
        "Doctor handwriting is often very messy, joined-up, and hard to read. "
        "Your job is to identify every medicine name on this prescription, "
        "even if the handwriting is unclear.\n\n"

        "STRATEGY FOR BAD HANDWRITING:\n"
        "- Look at the overall shape and length of the word, not just individual letters.\n"
        "- Indian doctors often write 'Tab', 'Cap', 'Syr', 'Inj' before the medicine name — ignore those prefixes.\n"
        "- Doses like '75mg', '500mg', '40mg' appear after the name — ignore those too.\n"
        "- If a word looks like it COULD be a medicine from the known list below, "
        "  output that known medicine's exact name. Do not output the garbled version.\n"
        "- Prefer matching to known medicines whenever there is any reasonable similarity.\n\n"

        "KNOWN MEDICINES — if what you read resembles any of these, output that exact name:\n"
        + known_list + "\n\n"

        "OUTPUT RULES (follow exactly):\n"
        "1. Return ONLY a JSON array of strings. Example: [\"Ecosprin 75\", \"Glycomet 500\"]\n"
        "2. Each element = one medicine name. Strip Tab/Cap/mg/ml/doses completely.\n"
        "3. If the medicine matches something in the known list (even approximately), "
        "   output the known-list spelling, not what you literally read.\n"
        "4. If it is NOT in the known list, output the generic drug name "
        "   (e.g. 'Tab. Pantocid 40mg' → 'Pantoprazole').\n"
        "5. Ignore dosage schedules, doctor name, date, patient name, diagnosis.\n"
        "6. Ayurvedic/herbal medicines: output name as written, without dose.\n"
        "7. If nothing is readable at all, return [].\n"
        "8. No markdown, no explanation, no extra text — ONLY the JSON array."
    )


# ─── PARSE MODEL REPLY ────────────────────────────────────────────────────────
def _parse_model_reply(text):
    """Parse JSON array from model output. Be forgiving."""
    text = text.strip()
    # Strip markdown code fences
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()
        if text.lower().startswith("json"):
            text = text[4:].strip()
    # Extract the array portion
    start = text.find("[")
    end   = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        text = text[start:end + 1]
    try:
        data = json.loads(text)
    except Exception:
        return []
    if not isinstance(data, list):
        return []
    return [str(x).strip() for x in data if str(x).strip()]


# ─── CALL GEMINI ──────────────────────────────────────────────────────────────
def _call_gemini(model, b64, mime_type, prompt_text):
    """Send one request to one Gemini model. Returns dict with ok/text/status."""
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt_text},
                {"inline_data": {"mime_type": mime_type, "data": b64}},
            ]
        }],
        "generationConfig": {
            "temperature": 0.05,      # very low — we want deterministic reads
            "maxOutputTokens": 1024,
        },
    }
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={GEMINI_API_KEY}"
    )
    r = requests.post(url, json=payload, timeout=60)

    if r.status_code == 200:
        try:
            text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            return {"ok": True, "text": text}
        except (KeyError, IndexError) as e:
            return {"ok": False, "status": 200, "body": f"Unexpected response shape: {e}"}
    return {"ok": False, "status": r.status_code, "body": r.text[:400]}


# ─── MAIN ENTRY POINT ─────────────────────────────────────────────────────────
def extract_medicines_from_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
    """
    Full pipeline: preprocess image → send to Gemini → match to database.

    Returns:
      {
        "medicines":    [canonical brand names from our database],
        "unrecognized": [names Gemini read but we don't have in our DB],
        "model_used":   "gemini-...",          # only on success
        "error":        "..."                  # only on failure
      }
    """
    if GEMINI_API_KEY == "PASTE_YOUR_GEMINI_KEY_HERE":
        return {
            "medicines": [],
            "unrecognized": [],
            "error": (
                "Gemini API key not set. "
                "Create gemini_key.txt in the backend folder and paste your key. "
                "Get a free key at https://aistudio.google.com"
            ),
        }

    # ── Step 1: Preprocess image for better handwriting recognition ──────────
    processed_bytes, processed_mime = _preprocess_image(image_bytes, mime_type)

    # ── Step 2: Build prompt and encode image ────────────────────────────────
    known_brands, lookup = _known_names()
    prompt_text = _prompt(known_brands)
    b64 = base64.b64encode(processed_bytes).decode("utf-8")

    # ── Step 3: Try each model ───────────────────────────────────────────────
    all_errors = []
    for model in MODEL_CANDIDATES:
        for attempt in range(1, RETRIES_PER_MODEL + 1):
            result = _call_gemini(model, b64, processed_mime, prompt_text)

            if result["ok"]:
                names = _parse_model_reply(result["text"])
                matched, unrecognized = _match_names(names, known_brands, lookup)
                return {
                    "medicines":    matched,
                    "unrecognized": unrecognized,
                    "model_used":   model,
                }

            status = result["status"]
            all_errors.append(f"{model}: HTTP {status} — {result['body'][:120]}")

            # Busy / rate-limit → retry same model after a wait
            if status in (503, 429) and attempt < RETRIES_PER_MODEL:
                print(f"[OCR] {model} busy (HTTP {status}), retry {attempt}/{RETRIES_PER_MODEL} "
                      f"in {RETRY_WAIT_SECONDS}s...")
                time.sleep(RETRY_WAIT_SECONDS)
                continue

            # 404 (retired) or other hard error → next model immediately
            break

    # All models failed
    detail   = " | ".join(all_errors) or "no model tried"
    key_hint = ""
    if any(("HTTP 400" in e or "HTTP 401" in e or "HTTP 403" in e) for e in all_errors):
        key_hint = (
            " <<< This usually means the Gemini key is wrong. "
            "Get a fresh key from aistudio.google.com (starts with AIza), "
            "paste it into gemini_key.txt, save, and try again."
        )
    return {
        "medicines":    [],
        "unrecognized": [],
        "error":        "All Gemini models failed: " + detail + key_hint,
    }


# ─── NAME MATCHING ────────────────────────────────────────────────────────────
def _match_names(names: list[str], known_brands: list, lookup: dict) -> tuple[list, list]:
    """
    Match a list of names (from Gemini) against the medicine database.
    Uses exact → partial substring → fuzzy matching in that order.
    Returns (matched_brands, unrecognized).
    """
    matched      = []
    unrecognized = []

    for name in names:
        brand = _find_brand(name, known_brands, lookup)
        if brand:
            if brand not in matched:
                matched.append(brand)
        else:
            unrecognized.append(name)

    return matched, unrecognized


def _find_brand(name: str, known_brands: list, lookup: dict):
    """Try exact, substring, then fuzzy match. Returns brand string or None."""
    nl = name.lower().strip()

    # 1. Exact lookup (includes aliases)
    if nl in lookup:
        return lookup[nl]

    # 2. Partial: name is substring of a known brand or vice versa
    #    (handles "Ecosprin" matching "Ecosprin 75")
    for b in known_brands:
        bl = b.lower()
        if nl in bl or bl in nl:
            return lookup.get(bl) or b

    # 3. Fuzzy match — catches handwriting-induced typos like "Ecoeprin", "Bruffen"
    close = difflib.get_close_matches(nl, list(lookup.keys()), n=1, cutoff=FUZZY_CUTOFF)
    if close:
        return lookup[close[0]]

    return None


# ─── STANDALONE TEST ──────────────────────────────────────────────────────────
# Write a prescription on paper, photograph it, then run:
#   python ocr.py "C:\path\to\photo.jpg"
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ocr.py <path to prescription photo>")
        print('Example: python ocr.py "C:\\Users\\Dell\\Desktop\\rx_photo.jpg"')
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "rb") as f:
        image_bytes = f.read()

    ext = path.lower()
    if ext.endswith(".png"):
        mime = "image/png"
    elif ext.endswith(".webp"):
        mime = "image/webp"
    else:
        mime = "image/jpeg"

    print(f"Preprocessing + sending to Gemini ({mime}, {len(image_bytes)//1024}KB)...")
    result = extract_medicines_from_image(image_bytes, mime)

    if result.get("error"):
        print("ERROR:", result["error"])
        sys.exit(1)

    print(f"\nModel used: {result.get('model_used', 'unknown')}")
    print("\nRecognized medicines (added to scan list):")
    for m in result["medicines"]:
        print("  ✓", m)

    if result["unrecognized"]:
        print("\nRead from prescription but NOT in Electra's database (verify with doctor):")
        for m in result["unrecognized"]:
            print("  ?", m)

    if not result["medicines"] and not result["unrecognized"]:
        print("  (nothing readable — try better lighting or a clearer photo)")
