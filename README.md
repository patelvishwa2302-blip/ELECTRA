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
* **Physical Intervention:** If a critical risk is detected (e.g., a bleeding risk or accidental duplicate medication), the system physically locks the specific medicine drawer, flashes a red warning LED, sounds a localized Hindi audio warning, and sends an emergency WhatsApp alert to the caregiver.

---

## ✨ Key Features

* 🧠 **Advanced Clinical Rules Engine:** Evaluates 29 distinct safety rules, covering severe drug-drug interactions, food conflicts, pregnancy/lactation risks, and patient-specific contraindications.
* 🏷️ **Dynamic NFC Provisioning:** A live tag-mapping system allows caregivers to instantly assign or reassign NFC tags to specific generic or brand medicines via the web dashboard—without editing a single line of hardware code.
* 🔒 **Automated Hardware Defense:** Uses precision servo motors to physically lock the compartment containing the dangerous medication, preventing accidental ingestion.
* 🗣️ **Localized Audio Warnings:** Integrates a DFPlayer Mini to provide immediate, rule-specific spoken warnings in Hindi (e.g., specific alerts for kidney strain or bleeding risks).
* ⏰ **Synchronized Dose Scheduling:** An NTP-synced scheduling system triggers physical hardware alarms and sends WhatsApp reminders to caregivers at the exact prescribed minute.
* ❤️ **Live Vitals Monitoring:** Features an integrated MAX30100 pulse oximeter running on a dedicated FreeRTOS core to continuously sample, average, and display patient SpO2 and BPM on an OLED screen without blocking the I2C bus.

---

## 🏗️ Architecture & Data Flow

Electra is built as a distributed, multi-node system to ensure stability, responsiveness, and separation of concerns.

| Component | Tech Stack | Role & Responsibility | Lead Developer |
| :--- | :--- | :--- | :--- |
| **The Command Dashboard** | HTML, CSS, JavaScript | The frontend UI. Handles live NFC tag enrollment, dose scheduling, patient profile configuration, and visual analysis rendering.|
| **The Virtual Brain** | Python, FastAPI | The backend server. Runs the clinical rule algorithms, manages the live tag map, and handles the WhatsApp API integration.|
| **The IoT Edge Hub** | C++, ESP32 (Arduino) | The physical hardware. Manages I2C/SPI buses for the OLED, RFID scanner, servos, DFPlayer speaker, and pulse oximeter via FreeRTOS.|

---

## 🚀 Installation & Quick Start

**1. Clone the Repository**
```bash
git clone [https://github.com/patelvishwa2302-blip/Electra.git](https://github.com/patelvishwa2302-blip/Electra.git)
cd Electra
