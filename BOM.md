# ELECTRA — Bill of Materials

Approximate Indian retail prices (2025–26). Total ≈ **₹1,700 – ₹2,000**.

| # | Component | Qty | Approx. cost | Purpose |
|---|---|---|---|---|
| 1 | ESP32 DevKit V1 (DOIT, 38-pin) | 1 | ₹350 | controller |
| 2 | MFRC522 RFID/NFC reader | 1 | ₹120 | reads bottle tags |
| 3 | MAX30100 pulse-ox sensor | 1 | ₹180 | heart rate + SpO₂ |
| 4 | SSD1306 OLED 0.96" I²C | 1 | ₹150 | patient display |
| 5 | SG90 micro servo | 3 | ₹150 | compartment locks |
| 6 | DFPlayer Mini MP3 module | 1 | ₹150 | audio playback |
| 7 | microSD card (2 GB, FAT32) | 1 | ₹150 | voice clips |
| 8 | Speaker (4 Ω, 3 W) | 1 | ₹100 | spoken alerts |
| 9 | RFID/NFC stickers (NTAG213) | 10 | ₹150 | one per medicine bottle |
| 10 | Active buzzer | 1 | ₹20 | audible alert |
| 11 | LEDs (red + green) + resistors | 2 | ₹20 | status |
| 12 | Push buttons | 2 | ₹20 | ANALYZE / RESET |
| 13 | Resistor 220 Ω (DFPlayer RX) | 1 | ₹5 | protects the module |
| 14 | Electrolytic capacitor 1000 µF | 1 | ₹20 | smooths the DFPlayer supply |
| 15 | Jumper wires + perfboard | — | ₹150 | assembly |
| 16 | Cardboard / 3D-printed enclosure | 1 | ₹100 | the box + compartments |

---

## Notes

- The **NFC stickers are the key cost lever** — one per medicine bottle, and they cost
  almost nothing, which is why the design uses NFC rather than barcodes or cameras.
- A **bigger, more sensitive 4 Ω speaker** noticeably improves loudness at the same
  amplifier power — worth the upgrade if the demo room is large.
- Everything here is **off-the-shelf**; nothing is custom-fabricated except the box.
