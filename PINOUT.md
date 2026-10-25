# ELECTRA — Pin Map

**Board:** DOIT ESP32 DEVKIT V1 (38-pin)

---

## Full pin assignment

| Module | Signal | ESP32 GPIO | Notes |
|---|---|---|---|
| **SSD1306 OLED** | SDA | 21 | I²C |
| | SCL | 22 | I²C |
| **MFRC522 NFC** | SDA / SS | 5 | SPI chip-select |
| | SCK | 18 | SPI clock |
| | MOSI | 23 | SPI data out |
| | MISO | 19 | SPI data in |
| | RST | 15 | reset |
| | 3.3V / GND | 3V3 / GND | **3.3 V only** |
| **Servo 1** (compartment 1) | signal | 32 | |
| **Servo 2** (compartment 2) | signal | 33 | |
| **Servo 3** (compartment 3) | signal | 25 | |
| **LED red** | anode | 14 | via resistor |
| **LED green** | anode | 12 | via resistor |
| **Buzzer** | + | 13 | active buzzer |
| **Button ANALYZE** | to GND | 26 | INPUT_PULLUP |
| **Button RESET** | to GND | 27 | INPUT_PULLUP |
| **DFPlayer Mini** | RX (module) | 17 (ESP32 TX) | via **220 Ω** resistor |
| | TX (module) | 16 (ESP32 RX) | direct |
| **MAX30100 pulse-ox** | SDA / SCL | 21 / 22 | shares the OLED I²C bus |
| **microSD (RFID)** | — | shares SPI | |

---

## Wiring notes

- **MAX30100 shares I²C (21/22) with the OLED.** The firmware runs the pulse-ox on a
  dedicated FreeRTOS task with an I²C mutex at 400 kHz, so the two do not collide.
- **DFPlayer RX needs a series resistor (~220 Ω–1 kΩ)** on the ESP32 TX → module RX line.
- **Servos want a solid 5 V supply.** If they twitch or the board browns out, give the
  servos their own 5 V supply with a **common ground** and a **470–1000 µF** capacitor
  across the servo V+/GND.
- **All grounds must be common** — ESP32, servos, DFPlayer, speaker, sensors.
- **MFRC522 is 3.3 V only.** 5 V will destroy it.

---

## Power

| Rail | Supplies |
|---|---|
| 3V3 | MFRC522, MAX30100, OLED |
| 5V (VIN) | Servos, DFPlayer |
| GND | common to everything |

A **1000 µF electrolytic capacitor** (positive leg to VCC) across the DFPlayer supply
smooths the current spikes when the speaker hits a loud transient.
