# ELECTRA — Firmware

ESP32 firmware for the ELECTRA medication-safety hub.

**Board:** DOIT ESP32 DEVKIT V1
**Core:** Arduino ESP32
**Language:** C++

---

## Files

| File | Purpose |
|---|---|
| `ELECTRA_complete_firmware.ino` | the full system — the one you flash |
| `ELECTRA_speaker_module.ino` | speaker / DFPlayer module in isolation |
| `DFPlayer_speaker_test.ino` | standalone speaker test (for wiring checks) |
| `secrets.example.h` | template for credentials — copy to `secrets.h` |

---

## ⚠️ Set up your credentials first

The sketch must **not** contain your Wi-Fi password. Create `secrets.h` (git-ignored):

```cpp
// firmware/secrets.h   <- DO NOT COMMIT
#pragma once
#define WIFI_SSID     "your-wifi-name"
#define WIFI_PASS     "your-wifi-password"
#define BACKEND_BASE  "http://192.168.1.100:8000"
#define DEVICE_ID     "electra-001"
```

Then in the sketch:
```cpp
#include "secrets.h"
```

`secrets.example.h` (the placeholder version) **is** committed.

> **Remote testing tip:** if the backend is behind an ngrok tunnel, set
> `BACKEND_BASE` to the **`https://…`** URL — ngrok redirects plain `http://`
> with a 307, and the firmware handles both automatically.

---

## Libraries required

Install via Arduino IDE → Library Manager:

| Library | Author | For |
|---|---|---|
| `MFRC522` | GithubCommunity | NFC/RFID reader |
| `Adafruit SSD1306` + `Adafruit GFX` | Adafruit | OLED display |
| `ESP32Servo` | Kevin Harrington | the three servo locks |
| `DFRobotDFPlayerMini` | DFRobot | spoken alerts |
| `MAX30100lib` | oxullo | pulse-ox (HR + SpO₂) |
| `ArduinoJson` | Benoit Blanchon | parsing the backend reply |

**Board settings:** `DOIT ESP32 DEVKIT V1` · upload speed 921600 · 115200 baud Serial Monitor.

---

## Pin map (summary)

| Function | GPIO |
|---|---|
| OLED SDA / SCL | 21 / 22 |
| RFID SS / RST | 5 / 15 |
| Servo 1 / 2 / 3 | 32 / 33 / 25 |
| LED red / green | 14 / 12 |
| Buzzer | 13 |
| Button ANALYZE / RESET | 26 / 27 |
| DFPlayer RX / TX | 16 / 17 |

Full table: [`../hardware/PINOUT.md`](../hardware/PINOUT.md)

---

## SD card (for the DFPlayer)

- **FAT32**, folder `01/`, files named `001.mp3` … `013.mp3` (3 digits)
- Clips must be **128 kbps CBR, 44.1 kHz** (VBR clips fail to play)

Clip mapping: [`../voice/README.md`](../voice/README.md)

---

## What the firmware does

1. Connects to Wi-Fi, fetches the **tag map** and **schedule** from the backend
2. Waits for an NFC tap — shows the medicine name on the OLED
3. On **ANALYZE**: sends the tapped medicines + patient profile to `/analyze`
4. Acts on the reply — colour LED, buzzer, **spoken warning**, **servo locks the unsafe compartment**
5. **Stable-vitals filter** on the pulse-ox (rejects non-physiological values, averages a rolling window)
6. Polls `/lock-state` so a caregiver can unlock from the dashboard

---

## Notable design decisions

- **Pulse-ox runs on its own FreeRTOS task** (core 1) with an I²C mutex — without this, the WiFi/HTTP work starved it and it produced no readings.
- **`httpBegin()` helper** picks a plain or TLS client from the URL scheme, so the same firmware works on `http://` (LAN) and `https://` (remote tunnel).
- **Stable-vitals filter:** readings outside HR 40–180 / SpO₂ 70–100 are discarded; the display shows the average of the last 6 valid samples, so it only reports once it has real data.
- **5-second RESET hold** — the lock cannot be opened by an accidental brush.
- **Offline-safe:** the rules and the locks work without the backend; the server adds the dashboard and explanations.
