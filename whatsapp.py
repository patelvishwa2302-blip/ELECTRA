# whatsapp.py
# Electra — Caregiver WhatsApp alerts via the official Meta WhatsApp Cloud API.
#
# Why this replaced Twilio:
#   - No 30-day trial expiry (the Meta test setup lives forever)
#   - No 100-message cap (test mode is limited by RECIPIENTS, not messages: up to 5 verified numbers)
#   - No credit card, and production cost is about Rs 0.12 per alert (utility template, India)
#
# IMPORTANT: the message text is NOT in this file. Meta requires pre-approved
# "templates" for messages a business initiates. You create the template once
# in the Meta dashboard (see Electra_Part9_Meta_WhatsApp_Setup.md) and this
# code fills in its three variables: {{1}}=risk level, {{2}}=issue, {{3}}=action.
#
# main.py needs ZERO changes — same function name and arguments as before.

import os
import requests

# ─── CONFIG & TOKEN LOADER ──────────────────────────────────────────────
# Token loading order:
#   1. whatsapp_token.txt (paste your raw token here, like gemini_key.txt)
#   2. whatsapp_config.py (if you prefer python file)
#   3. Environment variable (ELECTRA_WHATSAPP_TOKEN, ELECTRA_PHONE_NUMBER_ID)
#   4. Fallback default
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _load_whatsapp_credentials():
    token = None
    phone_number_id = None

    # 1. Try reading whatsapp_token.txt
    token_txt_path = os.path.join(BASE_DIR, "whatsapp_token.txt")
    if os.path.isfile(token_txt_path):
        try:
            with open(token_txt_path, "r", encoding="utf-8") as f:
                lines = [line.strip().strip("\"'") for line in f if line.strip() and not line.strip().startswith("#")]
                for line in lines:
                    if line.startswith("WHATSAPP_TOKEN="):
                        token = line.split("=", 1)[1].strip().strip("\"'")
                    elif line.startswith("PHONE_NUMBER_ID="):
                        phone_number_id = line.split("=", 1)[1].strip().strip("\"'")
                if not token and lines:
                    token = lines[0]
                    if len(lines) > 1 and lines[1].isdigit():
                        phone_number_id = lines[1]
        except Exception as e:
            print(f"[whatsapp] Warning reading whatsapp_token.txt: {e}")

    # 2. Try importing whatsapp_config.py
    if not token or not phone_number_id:
        try:
            import whatsapp_config
            if not token and hasattr(whatsapp_config, "WHATSAPP_TOKEN") and whatsapp_config.WHATSAPP_TOKEN:
                token = str(whatsapp_config.WHATSAPP_TOKEN).strip().strip("\"'")
            if not phone_number_id and hasattr(whatsapp_config, "PHONE_NUMBER_ID") and whatsapp_config.PHONE_NUMBER_ID:
                phone_number_id = str(whatsapp_config.PHONE_NUMBER_ID).strip().strip("\"'")
        except ImportError:
            pass

    # 3. Try environment variables
    if not token:
        token = os.environ.get("ELECTRA_WHATSAPP_TOKEN", "").strip().strip("\"'")
    if not phone_number_id:
        phone_number_id = os.environ.get("ELECTRA_PHONE_NUMBER_ID", "").strip().strip("\"'")

    # 4. Fallback default
    if not token:
        token = "EAAXHRbaC37gBSyQpNCR2ZBov3jd6owj5asuA3CghjUQRfd5b32FIYkJE923DgtZCIBt1UT2KT00PrYIw5MZBZCUHcY04932lHQgStpIaveBj7jPKR62UIuPlcXG5FhBATfZBeYet0LrTw4v10ZCnzKUhBZBg7nA4ZC9R1HhF09cdTVQi49dBx7hZBWJLvHnLFe3eP1qdHrw8TWfhZAojdGUxlfY3wI1N4mQIZC6f0Wk5BUdp15jzYmDMQCZCsNHfcnI4lQzsYF2T24DhNIoDlwA96Fjeli8luZCAZD"
    if not phone_number_id:
        phone_number_id = "1258373714033641"

    return token, phone_number_id

WHATSAPP_TOKEN, PHONE_NUMBER_ID = _load_whatsapp_credentials()

TEMPLATE_NAME = "electra_alert"   # must match the template name you created in Meta
API_VERSION = "v21.0"
REMINDER_TEMPLATE = "electra_reminder"   # the dose-reminder template you just got approved


API_URL = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}/messages"
# ─────────────────────────────────────────────────────────────────────────


def send_whatsapp_alert(phone: str, risk_level: str, summary: str, action: str) -> bool:
    """
    Send the caregiver alert via WhatsApp Cloud API.

    Called by main.py exactly as before:
        send_whatsapp_alert(phone=..., risk_level=..., summary=..., action=...)

    Returns True if WhatsApp accepted the message, False otherwise.
    """
    token, phone_number_id = _load_whatsapp_credentials()
    api_url = f"https://graph.facebook.com/{API_VERSION}/{phone_number_id}/messages"

    if token in ("PASTE_YOUR_TOKEN_HERE", "") or phone_number_id in ("PASTE_YOUR_PHONE_NUMBER_ID", ""):
        print("WhatsApp skipped: token / phone number ID not configured yet.")
        return False

    # Accept "+919876543210" or "919876543210"
    to = phone.strip().replace(" ", "")
    if not to.startswith("+"):
        to = "+" + to

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": TEMPLATE_NAME,
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": risk_level},
                        {"type": "text", "text": summary},
                        {"type": "text", "text": action},
                    ],
                }
            ],
        },
    }

    try:
        r = requests.post(api_url, headers=headers, json=payload, timeout=10)
        if r.status_code == 200:
            print(f"WhatsApp sent to {to}: message id {r.json().get('messages', [{}])[0].get('id', 'ok')}")
            return True
        # Meta puts the exact reason in the response body — print it, it tells you what to fix
        print(f"WhatsApp failed ({r.status_code}): {r.text}")
        return False
    except Exception as e:
        print(f"WhatsApp failed: {e}")
        return False


def send_whatsapp_reminder(phone: str, medicines: str, note: str = "") -> bool:
    """
    Send a DOSE REMINDER via the approved "electra_reminder" template.

    Different from the alert template — this one has TWO variables:
        {{1}} = the medicines   e.g. "Glycomet 500, Ecosprin 75"
        {{2}} = the note        e.g. "Take with breakfast"

    Called by scheduler.py's background reminder loop.

    Returns True if WhatsApp accepted the message, False otherwise.
    """
    token, phone_number_id = _load_whatsapp_credentials()
    api_url = f"https://graph.facebook.com/{API_VERSION}/{phone_number_id}/messages"

    if token in ("PASTE_YOUR_TOKEN_HERE", "") or phone_number_id in ("PASTE_YOUR_PHONE_NUMBER_ID", ""):
        print("WhatsApp reminder skipped: token / phone number ID not configured yet.")
        return False

    if not phone:
        print("WhatsApp reminder skipped: no caregiver number.")
        return False

    # Accept "+919876543210" or "919876543210"
    to = phone.strip().replace(" ", "")
    if not to.startswith("+"):
        to = "+" + to

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": REMINDER_TEMPLATE,
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": medicines},
                        {"type": "text", "text": note if note else "Take as prescribed"},
                    ],
                }
            ],
        },
    }

    try:
        r = requests.post(api_url, headers=headers, json=payload, timeout=10)
        if r.status_code == 200:
            print(f"WhatsApp reminder sent to {to}: message id {r.json().get('messages', [{}])[0].get('id', 'ok')}")
            return True
        # Meta puts the exact reason in the response body — print it, it tells you what to fix
        print(f"WhatsApp reminder failed ({r.status_code}): {r.text}")
        if "132000" in r.text:
            print("   -> variable count mismatch: the approved 'electra_reminder' template "
                  "does not have exactly 2 variables. Add or remove one entry in the "
                  "parameters list above to match it.")
        elif "132001" in r.text:
            print("   -> template name or language not found. Check the exact template "
                  "name and its language code in WhatsApp Manager.")
        elif "190" in r.text or "expired" in r.text.lower():
            print("   -> the token has expired. Paste a fresh one into whatsapp_token.txt "
                  "(it dies every 24 hours).")
        return False
    except Exception as e:
        print(f"WhatsApp reminder failed: {e}")
        return False


# ─── STANDALONE TEST ────────────────────────────────────────────────────
# Run this file directly to test WITHOUT going through /analyze:
#   (venv) PS ...\backend> python whatsapp.py
# If the teammate's phone buzzes with an Electra alert, Part 9 is done.
if __name__ == "__main__":
    ok = send_whatsapp_alert(
        phone="+918849065660",  # ← change to your teammate's verified number
        risk_level="HIGH",
        summary="Antiplatelet + NSAID: Ecosprin 75 + Brufen 400",
        action="Ask the doctor if Brufen can be replaced with Crocin.",
    )
    print("SENT - check the phone!" if ok else "FAILED - read the error message above")
