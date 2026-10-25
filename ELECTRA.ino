/* ============================================================================
   ELECTRA — COMPLETE BOX FIRMWARE  (Yashasvi's part)   [CORRECTED + INTEGRATED]
   ----------------------------------------------------------------------------
   This single file makes EVERY component work together:
     RFID tap  ·  OLED  ·  servos (locks)  ·  DFPlayer speaker  ·  LEDs/buzzer
     pulse-ox  ·  WiFi  ·  backend (/tags, /schedule, /analyze, /lock-state)

   FIXES / FEATURES IN THIS VERSION
     FIX 1  Pulse-ox sampled CONTINUOUSLY (loop + delayPump) - it worked solo
            but not in the full build because update() was only called inside
            monitorVitals().  KEY FIX.
     FIX 2  Speaker clip numbers corrected to match SD files 001.mp3..013.mp3.
     FIX 3  OLED monitoring line missing a newline (" bpm""SpO2: " joined).
     FIX 4  Tag-map JSON buffer enlarged.
     FIX 5  Long blocking delays replaced with delayPump() so the pulse-ox
            keeps sampling during beeps, reminders and alerts.
     FIX 6  /analyze HTTP timeouts raised (fixes "HTTP error -11").
     FIX 7  Timeouts raised on /tags and /schedule too.
     FIX 8  Removed the duplicate tag-map/schedule download at boot.
     FEAT 9  TAG-NAME SYNC: processResponse() now refreshes the local tag table
             from the backend's tag_names map, so names never go stale.
     FEAT 10 COMPARTMENT LOCK: the OLED names the held-back medicine (hold_backs).
     FEAT 11 COMPARTMENT LOCK: pollLockState() lets the caregiver unlock from the
             dashboard; it only ever OPENS, never locks.
     FEAT 12 COMPARTMENT LOCK: RESET is now a deliberate 5-second long press, so
             a compartment cannot be opened by an accidental brush.
     FEAT 13 BOOT REPORT + startup clip: prints whether the pulse-ox and speaker
             initialised, and plays the 'safe' clip so you can hear it works.
     FIX 14 Pulse-ox init retried up to 3 times.
     FIX 15 Sensor re-initialised before monitoring (clears the FIFO after the
            long /analyze HTTP pause).
     FIX 16 Live pulse-ox values printed to Serial every 3 s for diagnosis.
     FIX 17 Pulse-ox moved to its OWN FreeRTOS task on core 1, guarded by an I2C
            mutex, and the I2C clock raised to 400 kHz. This is THE FIX for
            "reads in the bisection test but not in the full build" - the main
            loop's blocking (OLED writes, RFID reads, HTTP) could no longer
            starve the sensor's ~10 ms sampling window.
     FIX 18 The monitor screen no longer re-initialises the sensor before
            monitoring (FIX 15 did, which discarded the readings the sensor had
            already acquired and left the monitor blank). HR and SpO2 are now
            shown on separate, clearly-labelled OLED lines.
     FIX 19 STABLE VITALS: the MAX30100's raw output is jumpy, so readings are
            rejected unless they are physiological (HR 40-180, SpO2 70-100),
            collected into a rolling window, and shown as the window AVERAGE.
            A number only appears once a full window of valid samples exists.
     FIX 20 Remote-tunnel support: the ngrok-skip-browser-warning header is sent
            on every request, the /analyze JSON buffer is larger, and a parse
            failure now prints the body length and first 250 chars to Serial.
     FIX 21 /analyze now follows HTTP redirects and prints the HTTP status code
            and the response length so the cause is visible on the Serial Monitor.
     FIX 22 HTTPS support: ngrok answers http:// with a 307 redirect to https://.
            httpBegin() now picks a TLS client automatically when the URL is
            https:// (with setInsecure), so the same firmware works on http (LAN)
            and https (remote tunnel).
     FIX 23 Servo open/closed angles are now ANGLE_OPEN / ANGLE_CLOSED (swap them
            if a compartment works backwards), and the firmware prints the
            backend's lock_compartments and every LOCK it performs.

   ----------------------------------------------------------------------------
   SD CARD (DFPlayer): folder "01", files named 001.mp3 ... 013.mp3 (3 digits).
      001 bleeding        006 serotonin      011 locked
      002 kidney          007 respiratory    012 safe
      003 sedation        008 duplicate      013 emergency
      004 qt              009 therapeutic
      005 hypoglycaemia   010 controlled

   LIBRARIES: MFRC522 · Adafruit SSD1306 · Adafruit GFX · ArduinoJson ·
              ESP32Servo · MAX30100lib · DFRobotDFPlayerMini
   BOARD: "ESP32 Dev Module"
   ============================================================================ */

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <SPI.h>
#include <MFRC522.h>
#include <ESP32Servo.h>
#include "MAX30100_PulseOximeter.h"
#include "DFRobotDFPlayerMini.h"
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <freertos/semphr.h>

// ============================================================
// 1. CONFIGURATION
// ============================================================
const char* WIFI_SSID  = "Airtel_Namu";
const char* WIFI_PASS  = "Satvik@9327132765";

// NO trailing slash. The IP must be the LAPTOP's IP on the same hotspot.
const char* BACKEND_BASE = "https://tinfoil-punctured-busload.ngrok-free.dev";
const char* DEVICE_ID    = "electra-001";

// ============================================================
// 2. PIN DEFINITIONS
// ============================================================
#define OLED_SDA     21
#define OLED_SCL     22
#define RFID_SS       5
#define RFID_RST     15
#define SERVO_1      32
#define SERVO_2      33
#define SERVO_3      25
#define LED_RED      14
#define LED_GREEN    12
#define BUZZER       13
#define BTN_ANALYZE  26
#define BTN_RESET    27
#define DF_RX        16      // ESP32 RX  <- DFPlayer TX
#define DF_TX        17      // ESP32 TX  -> DFPlayer RX (through 1k ohm)

// ============================================================
// 2b. SPEAKER CLIP NUMBERS  (match folder "01": 001.mp3 ... 013.mp3)
// ============================================================
#define CLIP_BLEEDING      1
#define CLIP_KIDNEY        2
#define CLIP_SEDATION      3
#define CLIP_QT            4
#define CLIP_HYPO          5
#define CLIP_SEROTONIN     6
#define CLIP_RESPIRATORY   7
#define CLIP_DUPLICATE     8
#define CLIP_THERAPEUTIC   9
#define CLIP_CONTROLLED    10
#define CLIP_LOCKED        11
#define CLIP_SAFE          12
#define CLIP_EMERGENCY     13
// If you add a dedicated reminder voice, name it 014.mp3 and set this to 14.
#define CLIP_REMINDER      12

// ============================================================
// 3. OBJECTS
// ============================================================
Adafruit_SSD1306 oled(128, 64, &Wire, -1);
MFRC522 rfid(RFID_SS, RFID_RST);
Servo servo1, servo2, servo3;
PulseOximeter pulseOx;
DFRobotDFPlayerMini player;
HardwareSerial dfSerial(2);
bool speakerReady = false;
bool pulseOxReady = false;      // FIX 1: track whether the sensor began OK
SemaphoreHandle_t i2cMutex = nullptr;   // FIX 17: guards the shared I2C bus

// FIX 17: the pulse-ox runs in its OWN task on core 1, so the main loop's
// blocking (OLED writes, RFID reads, HTTP) can no longer starve its sampling.
void oxTask(void *pv) {
  for (;;) {
    if (pulseOxReady && i2cMutex &&
        xSemaphoreTake(i2cMutex, portMAX_DELAY) == pdTRUE) {
      pulseOx.update();
      xSemaphoreGive(i2cMutex);
    }
    vTaskDelay(4 / portTICK_PERIOD_MS);   // sample every ~4 ms
  }
}

// FIX 22: TLS + plain clients, and a helper that picks the right one from the URL.
// ngrok answers http:// with a 307 redirect to https://, so the remote backend is
// https. This lets the SAME firmware talk to http (finale LAN) and https (remote).
WiFiClientSecure tlsClient;
WiFiClient       plainClient;

void httpBegin(HTTPClient &http, const String &url) {
  if (url.startsWith("https://")) http.begin(tlsClient, url);
  else                            http.begin(plainClient, url);
}

// ============================================================
// 4. GLOBALS
// ============================================================
String tappedUIDs[10];
String tappedNames[10];
int tappedCompartments[10];
int medCount = 0;
bool isAnalyzing = false;
bool isMonitoring = false;

const int MAX_TAGS = 40;
String tagUIDs[MAX_TAGS];
String tagBrands[MAX_TAGS];
int tagCount = 0;

struct Reminder { String time; String meds; String note; bool fired; };
Reminder reminders[10];
int reminderCount = 0;
String lastReminderDay = "";
unsigned long lastReminderCheck = 0;

unsigned long lastLockPoll = 0;      // FEAT 11: caregiver unlock polling

// FIX 19: rolling window for stable vitals
#define VIT_WINDOW 6
int  vitHr[VIT_WINDOW];
int  vitSp[VIT_WINDOW];
int  vitCount = 0;

struct Patient {
  int age; bool diabetes; bool hypertension; bool ckd;
  String kidney_fn; String caregiver_ph;
};
Patient demoPatient = {72, true, true, true, "mild", "+918849065660"};

// ============================================================
// 5. SMALL HELPERS
// ============================================================
void setLED(bool red, bool green) {
  digitalWrite(LED_RED,   red   ? HIGH : LOW);
  digitalWrite(LED_GREEN, green ? HIGH : LOW);
}

// FIX 1 + FIX 5: a delay that KEEPS the pulse-ox sampling.
// Use this everywhere instead of delay() so the sensor never misses its window.
void delayPump(unsigned long ms) {
  // FIX 17: the pulse-ox now has its own task, so a plain delay is fine here.
  delay(ms);
}

void beep(int ms) {
  tone(BUZZER, 1000, ms);
  delayPump(ms + 40);            // FIX 5
}

// FIX 23: servo open/closed angles.
// If a compartment CLOSES when it should open (or stays open when it should
// close), just SWAP these two numbers. 0/90 is the usual setup; some linkages
// need 0/180 instead - try that if 90 doesn't fully close the drawer.
#define ANGLE_OPEN    0
#define ANGLE_CLOSED  90

void unlockAll() {
  servo1.write(ANGLE_OPEN);
  servo2.write(ANGLE_OPEN);
  servo3.write(ANGLE_OPEN);
}

void lockServo(int c) {
  Serial.printf("LOCK compartment %d -> %d deg\n", c, ANGLE_CLOSED);   // FIX 23: proves it ran
  if (c == 1) servo1.write(ANGLE_CLOSED);
  if (c == 2) servo2.write(ANGLE_CLOSED);
  if (c == 3) servo3.write(ANGLE_CLOSED);
}

void oledShow(String l1, String l2 = "", String l3 = "", String l4 = "") {
  // FIX 17: hold the I2C mutex so this never collides with the pulse-ox task
  if (i2cMutex && xSemaphoreTake(i2cMutex, portMAX_DELAY) == pdTRUE) {
    oled.clearDisplay();
    oled.setTextSize(1);
    oled.setTextColor(WHITE);
    oled.setCursor(0, 0);
    oled.println(l1);
    if (l2 != "") oled.println(l2);
    if (l3 != "") oled.println(l3);
    if (l4 != "") oled.println(l4);
    oled.display();
    xSemaphoreGive(i2cMutex);
  }
}

bool alreadyScanned(String uid) {
  for (int i = 0; i < medCount; i++) if (tappedUIDs[i] == uid) return true;
  return false;
}

String prettyKey(String k) {
  k.replace("_", " ");
  String out = "";
  bool cap = true;
  for (int i = 0; i < (int)k.length(); i++) {
    char c = k[i];
    if (c == ' ') { cap = true; out += c; }
    else if (cap) { out += (char)toupper(c); cap = false; }
    else out += c;
  }
  return out;
}

int compartmentFor(String brand) {
  String b = brand; b.toLowerCase();
  if (b.indexOf("voveran") >= 0 || b.indexOf("dynapar") >= 0) return 3;
  return 1;
}

// ============================================================
// 6. TAG MAP
// ============================================================
void downloadTagMap() {
  tagCount = 0;
  if (WiFi.status() != WL_CONNECTED) { Serial.println("Tag map: no WiFi"); return; }

  HTTPClient http;
  http.setConnectTimeout(10000);   // FIX 7: don't give up too early
  http.setTimeout(15000);          // read timeout
  httpBegin(http, String(BACKEND_BASE) + "/tags");   // FIX 22
  http.addHeader("ngrok-skip-browser-warning", "true");   // FIX 20
  int code = http.GET();

  if (code == 200) {
    String body = http.getString();
    DynamicJsonDocument doc(8192);             // FIX 4: heap-allocated, 40 tags fit
    if (!deserializeJson(doc, body)) {
      JsonObject disp = doc["display"].as<JsonObject>();
      if (!disp.isNull()) {
        for (JsonPair kv : disp) {
          if (tagCount >= MAX_TAGS) break;
          tagUIDs[tagCount]   = String(kv.key().c_str());
          tagBrands[tagCount] = kv.value().as<String>();
          tagCount++;
        }
      }
      if (tagCount == 0) {
        JsonObject mp = doc["map"].as<JsonObject>();
        for (JsonPair kv : mp) {
          if (tagCount >= MAX_TAGS) break;
          tagUIDs[tagCount]   = String(kv.key().c_str());
          tagBrands[tagCount] = prettyKey(kv.value().as<String>());
          tagCount++;
        }
      }
    }
  }
  http.end();
  Serial.printf("Tag map: %d tags loaded\n", tagCount);
}

String tagBrandFor(String uid) {
  for (int i = 0; i < tagCount; i++) if (tagUIDs[i] == uid) return tagBrands[i];
  return "";
}

// ============================================================
// 7. SPEAKER (DFPlayer)
// ============================================================
void setupSpeaker() {
  dfSerial.begin(9600, SERIAL_8N1, DF_RX, DF_TX);
  delay(600);
  speakerReady = player.begin(dfSerial, false, false);
  if (!speakerReady) {
    delay(400);
    speakerReady = player.begin(dfSerial, true, true);
  }
  if (speakerReady) {
    player.volume(28);
    Serial.println("Speaker ready");
  } else {
    Serial.println("Speaker: DFPlayer not found (check GND, 5V, TX/RX cross, resistor)");
  }
}

void playClip(int n) {
  if (!speakerReady) return;
  player.playFolder(1, n);
}

// FIX 2: clip numbers now match folder "01" files 001.mp3 ... 013.mp3
void sayResult(String ruleId, String risk) {
  if (!speakerReady) return;
  if (risk == "low") return;                       // silence when all is well

  int clip = 0;
  if      (ruleId == "BLEED-001")    clip = CLIP_BLEEDING;
  else if (ruleId == "KID-001")      clip = CLIP_KIDNEY;
  else if (ruleId == "SED-001")      clip = CLIP_SEDATION;
  else if (ruleId == "RESP-001")     clip = CLIP_RESPIRATORY;
  else if (ruleId == "QT-001")       clip = CLIP_QT;
  else if (ruleId == "DUP-001")      clip = CLIP_DUPLICATE;
  else if (ruleId == "SERO-001")     clip = CLIP_SEROTONIN;
  else if (ruleId == "AYUR-DYNAMIC") clip = CLIP_CONTROLLED;

  if (clip == 0) {                                  // fallback by seriousness
    if      (risk == "critical") clip = CLIP_EMERGENCY;
    else if (risk == "high")     clip = CLIP_LOCKED;
    else                         clip = CLIP_SAFE;
  }
  playClip(clip);
}

// ============================================================
// 8. DOSE REMINDERS
// ============================================================
void setupClock() {
  configTime(19800, 0, "pool.ntp.org", "time.nist.gov");   // IST = UTC+5:30
  Serial.print("Getting the time");
  struct tm t;
  for (int i = 0; i < 20; i++) {
    if (getLocalTime(&t, 500)) { Serial.println(" ok"); return; }
    Serial.print(".");
  }
  Serial.println(" failed - reminders need WiFi for the time");
}

void downloadSchedule() {
  reminderCount = 0;
  if (WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;
  http.setConnectTimeout(10000);   // FIX 7
  http.setTimeout(15000);
  httpBegin(http, String(BACKEND_BASE) + "/schedule");   // FIX 22
  http.addHeader("ngrok-skip-browser-warning", "true");   // FIX 20
  int code = http.GET();

  if (code == 200) {
    String body = http.getString();
    DynamicJsonDocument doc(3072);
    if (!deserializeJson(doc, body)) {
      for (JsonObject r : doc.as<JsonArray>()) {
        if (reminderCount >= 10) break;
        reminders[reminderCount].time  = r["time"].as<String>();
        reminders[reminderCount].note  = r["note"].as<String>();
        String meds = "";
        for (JsonVariant m : r["medicines"].as<JsonArray>()) {
          if (meds != "") meds += ", ";
          meds += m.as<String>();
        }
        reminders[reminderCount].meds  = meds;
        reminders[reminderCount].fired = false;
        reminderCount++;
      }
    }
  }
  http.end();
  Serial.printf("Schedule: %d reminder times loaded\n", reminderCount);
}

void fireReminder(int i) {
  Serial.println("REMINDER: " + reminders[i].time);
  setLED(true, true);
  oledShow("TIME TO TAKE", reminders[i].meds,
           reminders[i].note, "Take as prescribed");
  for (int b = 0; b < 3; b++) beep(250);
  if (speakerReady) playClip(CLIP_REMINDER);
  delayPump(4000);                        // FIX 5
  setLED(false, true);
  oledShow("Electra Ready", "Tap medicine", "bottles one by one");
}

void checkReminders() {
  if (reminderCount == 0) return;
  struct tm t;
  if (!getLocalTime(&t, 100)) return;

  char hhmm[6];  strftime(hhmm, sizeof(hhmm), "%H:%M", &t);
  char day[12];  strftime(day,  sizeof(day),  "%Y-%m-%d", &t);

  if (lastReminderDay != String(day)) {
    lastReminderDay = String(day);
    for (int i = 0; i < reminderCount; i++) reminders[i].fired = false;
  }
  for (int i = 0; i < reminderCount; i++) {
    if (!reminders[i].fired && reminders[i].time == String(hhmm)) {
      reminders[i].fired = true;
      fireReminder(i);
    }
  }
}

// ============================================================
// 9. THE ANALYSIS REQUEST
// ============================================================
String buildRequestBody() {
  DynamicJsonDocument doc(2048);
  doc["device_id"] = DEVICE_ID;

  JsonArray tags = doc.createNestedArray("scanned_tags");
  for (int i = 0; i < medCount; i++) tags.add(tappedUIDs[i]);

  doc.createNestedArray("scanned_medicines");
  JsonArray ayur = doc.createNestedArray("ayurvedic_medicines");
  ayur.add("Ashwagandha");
  doc.createNestedArray("foods");

  JsonObject patient = doc.createNestedObject("patient");
  patient["age"]              = demoPatient.age;
  patient["diabetes"]         = demoPatient.diabetes;
  patient["hypertension"]     = demoPatient.hypertension;
  patient["ckd"]              = demoPatient.ckd;
  patient["kidney_function"]  = demoPatient.kidney_fn;
  patient["liver_disease"]    = false;
  patient["caregiver_phone"]  = demoPatient.caregiver_ph;

  String body;
  serializeJson(doc, body);
  return body;
}

void monitorVitals();   // forward declaration

void processResponse(String jsonResponse) {
  DynamicJsonDocument doc(20480);   // FIX 20: bigger - the reply carries tag_names too
  DeserializationError err = deserializeJson(doc, jsonResponse);
  if (err) {
    // FIX 20: show WHAT came back, so we can tell a truncated body from HTML
    Serial.printf("PARSE ERROR: %s | body length = %d\n", err.c_str(), jsonResponse.length());
    Serial.print("First 250 chars: ");
    Serial.println(jsonResponse.substring(0, 250));
    oledShow("Parse error", "See Serial", "for details");
    return;
  }

  String risk      = doc["overall_risk"].as<String>();
  String dispText  = doc["display_text"].as<String>();
  bool   doBuzzer  = doc["buzzer"].as<bool>();
  JsonArray locks  = doc["lock_compartments"].as<JsonArray>();
  JsonArray alerts = doc["alerts"].as<JsonArray>();

  // ── FEAT 9: refresh the local tag names from the backend's reply ──────────
  // The backend re-resolves every tag on every analysis, so copying its answer
  // back here keeps our copy of "which tag is which medicine" fresh.
  JsonObject names = doc["tag_names"].as<JsonObject>();
  for (JsonPair kv : names) {
    String uid   = String(kv.key().c_str());
    String brand = kv.value().as<String>();
    bool found = false;
    for (int i = 0; i < tagCount; i++) {
      if (tagUIDs[i] == uid) { tagBrands[i] = brand; found = true; break; }
    }
    if (!found && tagCount < MAX_TAGS) {      // a tag we had not downloaded yet
      tagUIDs[tagCount]   = uid;
      tagBrands[tagCount] = brand;
      tagCount++;
    }
  }

  if (risk == "low")           setLED(false, true);
  else if (risk == "moderate") setLED(true, true);
  else                         setLED(true, false);

  Serial.print("lock_compartments from backend: ");   // FIX 23: what did the backend ask for?
  serializeJson(locks, Serial);
  Serial.println();
  for (JsonVariant c : locks) lockServo(c.as<int>());

  // ── FEAT 10 + 12: name the medicine being held back ───────────────────────
  JsonArray hb = doc["hold_backs"].as<JsonArray>();
  if (hb.size() > 0) {
    String med    = hb[0]["medicine"].as<String>();
    String reason = hb[0]["reason"].as<String>();
    int    drawer = hb[0]["compartment"].as<int>();
    if (reason.length() > 20) reason = reason.substring(0, 20);
    Serial.println("Hold back: " + med + " - " + reason + " (drawer " + String(drawer) + ")");
    oledShow("DO NOT TAKE", med, "Drawer " + String(drawer) + " LOCKED", "Hold RESET 5s");
    delayPump(2500);
  }

  if (doBuzzer) { for (int i = 0; i < 5; i++) { beep(200); delayPump(120); } }   // FIX 5
  else          { beep(100); }

  int a = dispText.indexOf('\n');
  int b = dispText.indexOf('\n', a + 1);
  int c = dispText.indexOf('\n', b + 1);
  String l1 = (a != -1) ? dispText.substring(0, a) : dispText;
  String l2 = (a != -1) ? dispText.substring(a + 1, (b != -1 ? b : dispText.length())) : "";
  String l3 = (b != -1) ? dispText.substring(b + 1, (c != -1 ? c : dispText.length())) : "";
  String l4 = (c != -1) ? dispText.substring(c + 1) : "";
  oledShow(l1, l2, l3, l4);

  String topRule = alerts.size() ? alerts[0]["rule_id"].as<String>() : "";
  sayResult(topRule, risk);

  if (risk == "high" || risk == "critical") {
    delayPump(3000);                     // FIX 5
    // FIX 18: no sensor re-init here any more. The oxTask keeps sampling on
    // core 1 even during the /analyze HTTP call, so the FIFO never overflows -
    // and re-initialising here discarded the readings the sensor had already
    // acquired, which is why the monitor screen stayed blank.
    monitorVitals();
  }
}

void analyzeAndAct() {
  if (medCount == 0) {
    oledShow("No medicines", "scanned yet.", "Tap a bottle.");
    return;
  }
  isAnalyzing = true;
  oledShow("Analyzing...", "Checking " + String(medCount) + " items");

  HTTPClient http;
  // FIX 6: /analyze runs the rule engine (and possibly an LLM), so it can take
  // much longer than the 5 s default. Raise BOTH timeouts or you get
  // "HTTP error -11" (HTTPC_ERROR_READ_TIMEOUT).
  http.setConnectTimeout(10000);   // 10 s to establish the connection
  http.setTimeout(30000);          // 30 s to wait for the reply
  httpBegin(http, String(BACKEND_BASE) + "/analyze");   // FIX 22
  http.addHeader("Content-Type", "application/json");
  http.addHeader("ngrok-skip-browser-warning", "true");   // FIX 20
  http.setFollowRedirects(HTTPC_STRICT_FOLLOW_REDIRECTS);  // FIX 21: follow 301/302
  String reqBody = buildRequestBody();
  Serial.println("ANALYZE body: " + reqBody);
  int code = http.POST(reqBody);
  Serial.printf("ANALYZE HTTP code: %d\n", code);           // FIX 21: what status came back

  if (code > 0) {
    String response = http.getString();
    Serial.printf("Response length: %d\n", response.length());   // FIX 21
    Serial.println("Response: " + response);
    processResponse(response);
  } else {
    oledShow("Cannot reach", "the backend", String(code));
    Serial.printf("HTTP error %d\n", code);
  }
  http.end();
  isAnalyzing = false;
}

// ============================================================
// 9b. CAREGIVER UNLOCK POLL  (FEAT 11)
//     The caregiver unlocks from the dashboard. We poll for that and OPEN only -
//     locking always happens in response to an analysis, never here.
// ============================================================
void pollLockState() {
  if (WiFi.status() != WL_CONNECTED) return;
  HTTPClient http;
  http.setConnectTimeout(4000);
  http.setTimeout(4000);
  httpBegin(http, String(BACKEND_BASE) + "/lock-state");   // FIX 22
  http.addHeader("ngrok-skip-browser-warning", "true");   // FIX 20
  if (http.GET() == 200) {
    DynamicJsonDocument doc(1024);
    if (!deserializeJson(doc, http.getString())) {
      bool want[4] = {false, false, false, false};
      for (JsonVariant c : doc["locked"].as<JsonArray>()) {
        int n = c.as<int>();
        if (n >= 1 && n <= 3) want[n] = true;
      }
      if (!want[1]) servo1.write(ANGLE_OPEN);
      if (!want[2]) servo2.write(ANGLE_OPEN);
      if (!want[3]) servo3.write(ANGLE_OPEN);
    }
  }
  http.end();
}

// ============================================================
// 10. PULSE-OX MONITORING
// ============================================================
// FIX 19: turn the MAX30100's jumpy raw output into a stable reading.
//   - reject anything outside a physiological range (HR 40-180, SpO2 70-100)
//   - keep a rolling window of the last few valid samples
//   - only report once the window is full, and report the AVERAGE
bool readStableVitals(int &hrOut, int &spo2Out) {
  float hr = pulseOx.getHeartRate();
  uint8_t sp = pulseOx.getSpO2();

  if (hr < 40 || hr > 180) return false;      // reject nonsense
  if (sp < 70 || sp > 100) return false;

  if (vitCount < VIT_WINDOW) {
    vitHr[vitCount] = (int)hr;
    vitSp[vitCount] = sp;
    vitCount++;
  } else {
    for (int i = 1; i < VIT_WINDOW; i++) {
      vitHr[i-1] = vitHr[i];
      vitSp[i-1] = vitSp[i];
    }
    vitHr[VIT_WINDOW-1] = (int)hr;
    vitSp[VIT_WINDOW-1] = sp;
  }
  if (vitCount < VIT_WINDOW) return false;    // need a full window

  int hs = 0, ss = 0;
  for (int i = 0; i < VIT_WINDOW; i++) { hs += vitHr[i]; ss += vitSp[i]; }
  hrOut   = hs / VIT_WINDOW;
  spo2Out = ss / VIT_WINDOW;
  return true;
}

void monitorVitals() {
  isMonitoring = true;
  vitCount = 0;                    // FIX 19: fresh window for this session
  oledShow("MONITORING", "Place finger on", "sensor below", "RESET to stop");
  unsigned long lastUpdate = 0;

  while(isMonitoring) {
    // FIX 17: oxTask samples the sensor continuously, so here we only read
    // the latest values (no update() call - that would race the task).
    if (millis() - lastLockPoll > 10000) {
      lastLockPoll = millis();
      pollLockState();
    }
    if (digitalRead(BTN_RESET) == LOW) { isMonitoring = false; break; }

    if (millis() - lastUpdate > 500) {
      lastUpdate = millis();
      float rawHr = pulseOx.getHeartRate();
      uint8_t rawSp = pulseOx.getSpO2();
      Serial.printf("MONITOR raw HR=%.1f SpO2=%d\n", rawHr, rawSp);

      int hr, spo2;
      // FIX 19: only show a reading once we have a full window of
      // physiological values (see readStableVitals)
      if (readStableVitals(hr, spo2)) {
        Serial.printf("MONITOR stable HR=%d SpO2=%d\n", hr, spo2);
        oledShow("VITALS MONITOR",
                 "HR:   " + String(hr) + " bpm",
                 "SpO2: " + String(spo2) + " %",
                 "RESET to stop");
        if (spo2 < 92) {
          oledShow("LOW SpO2!", "SpO2: " + String(spo2) + " %",
                   "Seek help", "RESET to stop");
          while (digitalRead(BTN_RESET) != LOW) { beep(300); delayPump(100); }   // FIX 5
          break;
        }
      } else {
        oledShow("MONITORING", "Reading...", "Hold finger still", "RESET to stop");
      }
    }
    delay(5);
  }
  oledShow("Electra Ready", "Tap medicine", "bottles one by one");
}

// ============================================================
// 11. RESET
// ============================================================
void resetAll() {
  medCount = 0;
  isAnalyzing = false;
  isMonitoring = false;
  unlockAll();
  {
    HTTPClient h;
    h.setConnectTimeout(3000);
    h.setTimeout(3000);
    h.begin(String(BACKEND_BASE) + "/unlock");
    h.POST("");
    h.end();
  }
  setLED(false, true);
  beep(100);
  downloadTagMap();
  downloadSchedule();
  oledShow("Reset done.", "Tap bottles to", "start again.");
  delayPump(1500);                     // FIX 5
  oledShow("Electra Ready", "Tap medicine", "bottles one by one");
}

// ============================================================
// 12. SETUP
// ============================================================
void setup() {
  Serial.begin(115200);
  delay(300);
  i2cMutex = xSemaphoreCreateMutex();      // FIX 17
  tlsClient.setInsecure();                 // FIX 22: accept the cert (ESP32 has no CA store)

  pinMode(LED_RED, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(BUZZER, OUTPUT);
  pinMode(BTN_ANALYZE, INPUT_PULLUP);
  pinMode(BTN_RESET, INPUT_PULLUP);

  Wire.begin(OLED_SDA, OLED_SCL);

  oled.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  oledShow("Electra booting...");

  SPI.begin();
  rfid.PCD_Init();

  servo1.attach(SERVO_1);
  servo2.attach(SERVO_2);
  servo3.attach(SERVO_3);
  unlockAll();

  // Pulse-ox: bring the sensor up on the I2C bus.
  // (Kept at 100 kHz as in your original - if readings are unreliable you can
  //  try Wire.setClock(400000); the MAX30100/30102 also support 400 kHz.)
  Wire.setClock(400000);   // FIX 17: faster bus -> OLED writes block for less time
  // FIX 14: retry the sensor init a few times - the first attempt can fail
  // if the I2C bus is still settling right after the OLED/SPI start.
  for (int attempt = 1; attempt <= 3 && !pulseOxReady; attempt++) {
    pulseOxReady = pulseOx.begin();
    if (!pulseOxReady) { Serial.printf("Pulse-ox begin attempt %d failed\n", attempt); delay(500); }
  }
  if (!pulseOxReady) {
    oledShow("Note:", "Pulse-ox not", "connected");
    Serial.println("MAX30100/30102 not found - check wiring");
    delay(1200);
  } else {
    Serial.println("Pulse-ox ready");
  }
  // FIX 17: start the dedicated pulse-ox sampling task on core 1
  xTaskCreatePinnedToCore(oxTask, "oxTask", 4096, NULL, 2, NULL, 1);

  setupSpeaker();

  WiFi.begin(WIFI_SSID, WIFI_PASS);
  oledShow("Connecting", "Wi-Fi...");
  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries < 30) { delay(500); tries++; }
  if (WiFi.status() != WL_CONNECTED) {
    oledShow("Wi-Fi failed", "Restarting...");
    delay(2000);
    ESP.restart();
  }
  Serial.print("WiFi ok, IP: ");
  Serial.println(WiFi.localIP());

  setupClock();

  // FEAT 13: BOOT REPORT + a startup clip, so you can SEE and HEAR that the
  // sensor and the speaker came up before you tap anything. If either says
  // FAIL, that component never initialised - fix it before debugging further.
  Serial.println("=== BOOT REPORT ===");
  Serial.print("Pulse-ox: "); Serial.println(pulseOxReady ? "OK" : "FAIL");
  Serial.print("Speaker:  "); Serial.println(speakerReady ? "OK" : "FAIL");
  Serial.print("Tags:     "); Serial.println(tagCount);
  if (speakerReady) { player.volume(28); player.playFolder(1, CLIP_SAFE); delayPump(2500); }

  // FIX 8: resetAll() already downloads the tag map + schedule, so the
  // calls that used to sit here made it download twice at every boot.
  resetAll();
}

// ============================================================
// 13. LOOP
// ============================================================
void loop() {
  // FIX 1: keep the pulse-ox sampling on EVERY pass. This is the key fix -
  // the MAX30100/30102 needs update() called continuously, or its FIFO
  // overflows and monitorVitals() later gets no data.
  // FIX 17: the pulse-ox is sampled by its own task now (see oxTask above),
  // so the loop no longer needs to call update().

  // FIX 16: PULSE-OX DEBUG - print the live values every 3 s so you can see
  // whether the sensor produces ANY readings while the box is running.
  // If these stay 0.0 / 0 even with a finger pressed, the sensor itself is the
  // problem. If they move, the sensor works and the fault is timing/power.
  static unsigned long lastOxPrint = 0;
  if (pulseOxReady && millis() - lastOxPrint > 3000) {
    lastOxPrint = millis();
    Serial.printf("Pulse-ox: HR=%.1f  SpO2=%d\n", pulseOx.getHeartRate(), pulseOx.getSpO2());
  }

  // dose reminders - checked every 15 seconds
  if (millis() - lastReminderCheck > 15000) {
    lastReminderCheck = millis();
    if (!isAnalyzing && !isMonitoring) checkReminders();
  }

  // FEAT 11: poll the caregiver's unlock state every 10 seconds
  if (millis() - lastLockPoll > 10000) {
    lastLockPoll = millis();
    if (!isAnalyzing && !isMonitoring) pollLockState();
  }

  if (isAnalyzing || isMonitoring) return;

  // ---- a tag was tapped ----
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    String uid = "";
    for (byte i = 0; i < rfid.uid.size; i++) {
      uid += (rfid.uid.uidByte[i] < 0x10 ? " 0" : " ");
      uid += String(rfid.uid.uidByte[i], HEX);
    }
    uid.trim();
    uid.toUpperCase();
    rfid.PICC_HaltA();

    if (!alreadyScanned(uid) && medCount < 10) {
      String brand = tagBrandFor(uid);
      if (brand == "") brand = "Unknown tag";

      tappedUIDs[medCount]         = uid;
      tappedNames[medCount]        = brand;
      tappedCompartments[medCount] = compartmentFor(brand);
      medCount++;

      beep(100);
      if (brand == "Unknown tag")
        oledShow("Unknown tag", "Assign it on", "the dashboard");
      else
        oledShow("Scanned: " + String(medCount), brand);
    }
  }

  // ---- ANALYZE button ----
  if (digitalRead(BTN_ANALYZE) == LOW) {
    delay(50);
    if (digitalRead(BTN_ANALYZE) == LOW) {
      analyzeAndAct();
      while (digitalRead(BTN_ANALYZE) == LOW);
    }
  }

  // ---- RESET button (FEAT 12: must be held 5 seconds) ----
  // A quick tap does nothing, so the compartment cannot be opened by an
  // accidental brush.
  if (digitalRead(BTN_RESET) == LOW) {
    unsigned long held = millis();
    while (digitalRead(BTN_RESET) == LOW && millis() - held < 5000) delay(50);
    if (millis() - held >= 5000) {
      oledShow("RESET", "Unlocking...");
      resetAll();
      while (digitalRead(BTN_RESET) == LOW);
    }
  }
}
