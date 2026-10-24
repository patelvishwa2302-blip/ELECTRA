# 💊 Electra: Smart Polypharmacy Safety System

Electra is an integrated, privacy-first medical IoT ecosystem designed to protect elderly patients from dangerous polypharmacy (multiple-medication) combinations. Built for real-world deployment, this system combines physical NFC tag scanning with a live clinical rules engine to automatically detect risks, lock physical medicine compartments, and alert caregivers before a harmful dose is taken.

---

## 📖 The Problem vs. The Solution

**The Problem**
Elderly patients managing multiple prescriptions face a high risk of accidental double-doses, drug-drug interactions, and contraindications with existing health conditions (like kidney disease, hypertension, or heart failure). Traditional medication apps rely on manual entry, which is prone to user error and often ignored by elderly users.

**The Solution**
Electra introduces a zero-friction, hardware-assisted safety net:
* **Instant Recognition:** Patients simply tap a medicine bottle (fitted with an NFC sticker) against the Electra edge device.
* **Predictive Clinical Analysis:** The FastAPI backend instantly cross-references the scanned medicines against 29 clinical safety rules, Ayurvedic herb interactions, and the patient's specific health profile.
* **Physical Intervention:** If a critical risk is detected, the system physically locks the specific medicine drawer, flashes a red warning LED, sounds a localized Hindi audio warning, and sends an emergency WhatsApp alert to the caregiver.

---

## ✨ Key Features

* 🧠 **Advanced Clinical Rules Engine:** Evaluates 29 distinct safety rules, covering severe drug-drug interactions, food conflicts, and patient-specific contraindications.
* 🏷️ **Dynamic NFC Provisioning:** A live tag-mapping system allows caregivers to instantly assign or reassign NFC tags via the web dashboard—without editing hardware code.
* 🔒 **Automated Hardware Defense:** Uses precision servo motors to physically lock the compartment containing the dangerous medication.
* 🗣️ **Localized Audio Warnings:** Integrates a DFPlayer Mini to provide immediate, rule-specific spoken warnings in Hindi.
* ⏰ **Synchronized Dose Scheduling:** An NTP-synced scheduling system triggers hardware alarms and sends WhatsApp reminders to caregivers at the exact prescribed minute.
* ❤️ **Live Vitals Monitoring:** Features an integrated MAX30100 pulse oximeter running on a dedicated FreeRTOS core to sample and display SpO2 and BPM on an OLED screen.

---

## 🏗️ Architecture & Data Flow

Electra is built as a distributed, multi-node system to ensure stability, responsiveness, and separation of concerns.

| Component | Tech Stack | Role & Responsibility |
| :--- | :--- | :--- |
| **The Command Dashboard** | HTML, CSS, JavaScript | The frontend UI. Handles live NFC tag enrollment, dose scheduling, patient profile configuration, and visual analysis rendering. |
| **The Virtual Brain** | Python, FastAPI | The backend server. Runs the clinical rule algorithms, manages the live tag map, and handles the WhatsApp API integration. |
| **The IoT Edge Hub** | C++, ESP32 (Arduino) | The physical hardware. Manages I2C/SPI buses for the OLED, RFID scanner, servos, DFPlayer speaker, and pulse oximeter via FreeRTOS. |

---

## 🚀 Installation & Quick Start

*(Electra is designed to run completely locally on your own machine and edge network without complex database setups.)*

**1. Clone the Repository**
```bash
git clone [https://github.com/patelvishwa2302-blip/Electra.git](https://github.com/patelvishwa2302-blip/Electra.git)
cd Electra
```

**2. Install Dependencies**
Ensure Python 3.9+ is installed, then navigate to the backend folder and run:
```bash
pip install fastapi uvicorn
```

**3. Run the Virtual Brain (Backend)**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

**4. Run the Command Dashboard**
Open `index.html` from the Frontend folder in any web browser to connect to the local server.

---

## 🎮 Interactive Demo Guide

Once the dashboard opens in your browser (`http://localhost:8000`) and the ESP32 is powered on:

1. **Watch the Baseline** — Scan a single, safe medicine. Observe the OLED display the name and the Green LED light up in the "Safe" zone.
2. **Trigger a Hazard** — Click the **Assign** button on the dashboard to map a new NFC tag, then scan two conflicting medicines.
3. **Observe the IoT Defense:**
   * Watch the **Red LED** flash and the **Buzzer** sound the alarm.
   * Hear the **DFPlayer Mini** announce the specific bleeding risk warning in Hindi.
   * See the **Servo Motor** physically lock Compartment 3 to prevent access.
   * Read the automated **WhatsApp Alert** on the caregiver's phone.

---

## 🛠️ Built With

| Library / Tech | Purpose |
| :--- | :--- |
| [FastAPI](https://fastapi.tiangolo.com/) | High-performance backend server and clinical rule engine |
| [FreeRTOS](https://www.freertos.org/) | Multi-tasking on the ESP32 to keep vitals sampling uninterrupted |
| [ESP32Servo](https://madhephaestus.github.io/ESP32Servo/) | Hardware PWM control for the physical compartment locks |
| [DFPlayer Mini](https://wiki.dfrobot.com/DFPlayer_Mini_SKU_DFR0299) | Localized Hindi audio warnings mapped from SD card files |
| Vanilla HTML/JS | Lightweight, reactive web frontend without heavy frameworks |

---

## 🎯 Conclusion

Electra proves that smart healthcare IoT can prevent fatal polypharmacy errors. By combining a predictive clinical rule engine with physical hardware locks and localized audio warnings, it creates a self-healing medication management system.f-healing medication management system.
