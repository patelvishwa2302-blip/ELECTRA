# ELECTRA — Full Wiring Guide

Complete connection guide for the ELECTRA medication-safety hub.

**Board:** DOIT ESP32 DEVKIT V1 (38-pin)
**Firmware:** C++ / Arduino (see `../firmware/`)

---

## 1. Modules

| Module | Interface | Voltage | Purpose |
|---|---|---|---|
| SSD1306 OLED 0.96" | I²C | 3.3 V | patient display |
| MAX30100 pulse-ox | I²C | 3.3 V | heart rate + SpO₂ |
| MFRC522 NFC reader | SPI | **3.3 V only** | reads bottle tags |
| DFPlayer Mini | UART | 3.3–5 V | audio playback |
| SG90 servo ×3 | PWM | 5 V | compartment locks |
| Speaker 4 Ω 3 W | analog | — | spoken alerts |
| LEDs, buzzer, buttons | GPIO | 3.3 V | status / input |

---

## 2. Power rails

| Rail | Feeds |
|---|---|
| **3V3** | OLED, MAX30100, MFRC522 |
| **5V (VIN)** | servos, DFPlayer |
| **GND** | common to **everything** |

> ⚠️ **MFRC522 is 3.3 V only.** 5 V will destroy it.
> ⚠️ **All grounds must be common** — ESP32, servos, DFPlayer, speaker, sensors.

If the servos twitch or the board browns out, give the servos their **own 5 V supply**
(common ground) with a **470–1000 µF** capacitor across their V+/GND.

---

## 3. Full connection table

| ESP32 GPIO | Connects to | Module pin | Notes |
|---|---|---|---|
| **21** | OLED + MAX30100 | SDA | shared I²C bus |
| **22** | OLED + MAX30100 | SCL | shared I²C bus |
| **5** | MFRC522 | SDA / SS | SPI chip-select |
| **18** | MFRC522 | SCK | SPI clock |
| **23** | MFRC522 | MOSI | SPI data out |
| **19** | MFRC522 | MISO | SPI data in |
| **15** | MFRC522 | RST | reset |
| **32** | Servo 1 | signal (orange) | compartment 1 |
| **33** | Servo 2 | signal (orange) | compartment 2 |
| **25** | Servo 3 | signal (orange) | compartment 3 |
| **14** | LED red | anode | via 220 Ω |
| **12** | LED green | anode | via 220 Ω |
| **13** | Buzzer | + | active buzzer |
| **26** | Button ANALYZE | leg 1 | other leg → GND (INPUT_PULLUP) |
| **27** | Button RESET | leg 1 | other leg → GND (INPUT_PULLUP) |
| **17** (TX) | DFPlayer | RX | **via 220 Ω resistor** |
| **16** (RX) | DFPlayer | TX | direct |
| **3V3** | OLED / MAX30100 / MFRC522 | VCC | |
| **5V** | DFPlayer / servos | VCC | |
| **GND** | all modules | GND | common |

**Audio:** DFPlayer `SPK1` and `SPK2` → the **4 Ω 3 W speaker**.

---

## 4. Subsystem diagrams

### I²C bus — OLED + MAX30100 (shared)

```
  ESP32                OLED             MAX30100
  GPIO21 ────┬────────── SDA ───────────── SDA
  GPIO22 ────┼────────── SCL ───────────── SCL
  3V3    ────┼────────── VCC ───────────── VCC
  GND    ────┴────────── GND ───────────── GND
```

> The pulse-ox and OLED share I²C. Run the sensor on its own task with an I²C mutex
> (as the firmware does) so the two do not collide.

### SPI — MFRC522 NFC reader

```
  ESP32               MFRC522
  GPIO5  ───────────── SDA (SS)
  GPIO18 ───────────── SCK
  GPIO23 ───────────── MOSI
  GPIO19 ───────────── MISO
  GPIO15 ───────────── RST
  3V3    ───────────── 3.3V      ← 3.3 V ONLY
  GND    ───────────── GND
```

### UART + audio — DFPlayer Mini

```
  ESP32 GPIO17 (TX) ──[ 220 Ω ]── DFPlayer RX
  ESP32 GPIO16 (RX) ───────────── DFPlayer TX
  ESP32 5V        ────┬────────── DFPlayer VCC
  ESP32 GND       ────┴────────── DFPlayer GND
                       │
           1000 µF capacitor across VCC–GND
           (positive leg to VCC)

  DFPlayer SPK1 ────┐
  DFPlayer SPK2 ────┴──────── 4 Ω 3 W speaker
```

> The **220 Ω** series resistor on the ESP32-TX → DFPlayer-RX line is required.
> The **1000 µF** capacitor smooths the current spikes when audio hits a loud transient.

### Servos (×3)

```
  ESP32 5V  ──┬── Servo 1 V+  (red)
              ├── Servo 2 V+  (red)
              └── Servo 3 V+  (red)

  ESP32 GND ──┬── Servo 1 GND (brown/black)
              ├── Servo 2 GND
              └── Servo 3 GND

  GPIO32 ───────── Servo 1 signal (orange)
  GPIO33 ───────── Servo 2 signal
  GPIO25 ───────── Servo 3 signal
```

### LEDs, buzzer, buttons

```
  GPIO14 ──[220 Ω]── LED red   ── GND
  GPIO12 ──[220 Ω]── LED green ── GND
  GPIO13 ─────────── Buzzer(+) ;  Buzzer(−) ── GND

  GPIO26 ─────────── Button ANALYZE ── GND     (INPUT_PULLUP)
  GPIO27 ─────────── Button RESET   ── GND     (INPUT_PULLUP)
```

---

## 5. Component notes

| Component | Value | Where | Why |
|---|---|---|---|
| Series resistor | 220 Ω – 1 kΩ | ESP32 TX → DFPlayer RX | protects the module's input |
| Decoupling cap | 1000 µF | across DFPlayer VCC–GND | smooths audio current spikes |
| Servo cap | 470–1000 µF | across servo V+–GND | prevents brownout |
| LED resistors | 220 Ω | each LED | current limiting |
| NFC stickers | NTAG213 | one per bottle | cheap, tap-to-read |

---

## 6. Common mistakes

| Symptom | Likely cause |
|---|---|
| MFRC522 dead / hot | wired to **5 V** instead of 3.3 V |
| Nothing works at all | **no common ground** between modules |
| Servos don't move | powered from **3.3 V**, or not enough current |
| Audio crackles / module heats | no 1000 µF cap, or volume set too high |
| DFPlayer reads the card but plays nothing | files not named `001.mp3…` in folder `01/`, or not CBR MP3 |
| Pulse-ox reads 0 | poor finger contact, ambient light, or the sensor starved of samples |
| Board resets when a servo moves | servos drawing from the ESP32's 5 V — give them their own supply |

---

## 7. Wiring diagram images

See the `wiring/` folder for the drawn diagrams:

- `speaker_wiring.png` — DFPlayer → speaker
- `dfplayer_power_wiring.png` — DFPlayer power + capacitor
- `dfplayer_orientation.png` — DFPlayer pin orientation
- `speaker_mount_layout.png` — physical speaker mounting
