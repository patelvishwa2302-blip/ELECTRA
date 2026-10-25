// ---------------------------------------------------------------------------
//  ELECTRA — credentials template
//
//  Copy this file to  secrets.h  and fill in YOUR values.
//  secrets.h is listed in .gitignore — NEVER commit your real credentials.
// ---------------------------------------------------------------------------
#pragma once

// ---- Wi-Fi the ESP32 joins ----
#define WIFI_SSID      "your-wifi-name"
#define WIFI_PASS      "your-wifi-password"

// ---- Backend address ----
//   On the local network:   "http://192.168.1.100:8000"
//   Behind an ngrok tunnel: "https://your-tunnel.ngrok-free.app"   (https!)
#define BACKEND_BASE   "http://192.168.1.100:8000"

// ---- Device identity ----
#define DEVICE_ID      "electra-001"
