"""
test_ocr_live.py  —  quick smoke test: sends a tiny white image to Gemini
to confirm the model responds, without needing a real prescription photo.
"""
import io, base64, requests, os

def load_key():
    env = os.environ.get("GEMINI_API_KEY", "").strip()
    if env: return env.strip("\"'")
    try:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gemini_key.txt")
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip().strip("\"'")
    except Exception: pass
    return None

from PIL import Image

key = load_key()
print(f"Key loaded: {key[:8]}...{key[-4:]}\n")

# Create a tiny white image with text "Ecosprin 75"
from PIL import ImageDraw, ImageFont
img = Image.new("RGB", (300, 80), color=(255, 255, 255))
draw = ImageDraw.Draw(img)
draw.text((10, 25), "Tab. Ecosprin 75mg", fill=(0, 0, 0))
buf = io.BytesIO()
img.save(buf, format="JPEG", quality=90)
img_bytes = buf.getvalue()
b64 = base64.b64encode(img_bytes).decode("utf-8")

models = ["gemini-2.5-flash", "gemini-3.8-flash", "gemini-2.5-pro"]

for model in models:
    print(f"Testing {model}... ", end="", flush=True)
    payload = {
        "contents": [{"parts": [
            {"text": 'Read the medicine name in this image. Return only a JSON array like ["Ecosprin 75"].'},
            {"inline_data": {"mime_type": "image/jpeg", "data": b64}}
        ]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 256}
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    r = requests.post(url, json=payload, timeout=30)
    if r.status_code == 200:
        try:
            text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            print(f"OK! Response: {text.strip()[:80]}")
            print(f"\n  --> '{model}' works. This is your primary model.\n")
            break
        except Exception as e:
            print(f"Response parse error: {e}")
    else:
        print(f"HTTP {r.status_code} - {r.text[:100]}")
