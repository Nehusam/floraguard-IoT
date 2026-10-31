/*
 * =========================================================================
 * FloraGuard IoT - ESP32 Plant Disease Early Detection Node Firmware
 * =========================================================================
 * 
 * Hardware Sensors:
 * - DHT11: Ambient Temperature & Relative Humidity (Pin GPIO 4)
 * - Capacitive Soil Moisture Sensor: Analog Soil Moisture (Pin ADC GPIO 35)
 * - Rain / Leaf Wetness Sensor: Precipitation detection (Pin ADC GPIO 34)
 * - Status LED: Pin GPIO 2 (Blinks on sampling and telemetry transmission)
 * 
 * Communication:
 * - Wi-Fi Station Mode with auto-reconnect
 * - HTTP POST JSON payload to FastAPI backend (/api/telemetry)
 * - Robust offline fallback (Serial sampling continues if Wi-Fi is unavailable)
 * 
 * Required Arduino Libraries:
 * 1. "DHT sensor library" by Adafruit
 * 2. "Adafruit Unified Sensor" by Adafruit
 * 3. "ArduinoJson" (v6 or v7) by Benoit Blanchon
 * =========================================================================
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// =========================================================================
// 1. CONFIGURATION PARAMETERS (Adjust to match your network & setup)
// =========================================================================

// Wi-Fi Credentials
const char* WIFI_SSID     = "Nehu's M02s";             // Wi-Fi SSID
const char* WIFI_PASSWORD = "nkeu5653";               // Wi-Fi Password

// Backend Server Configuration
// Replace with your computer's Wi-Fi IPv4 address (e.g., "http://192.168.1.100:8000/api/telemetry")
const char* SERVER_URL    = "http://192.168.98.227:8000/api/telemetry";

// Hardware Identity & Timing
#define DEVICE_ID               "ESP32-AGRI-01"
#define TELEMETRY_INTERVAL_MS   3000   // Sampling interval in milliseconds (min 2000 for DHT11)
#define ANALOG_SAMPLE_COUNT     10     // Number of ADC samples for noise-filtered moving average

// Hardware Pin Assignments
#define DHTPIN                  4      // DHT11 Data pin (GPIO 4)
#define DHTTYPE                 DHT11  // Sensor type: DHT11 (Blue module) or DHT22 (White)
#define SOIL_PIN                35     // Soil moisture sensor AO → GPIO 35
#define LEAF_PIN                34     // Rain / leaf wetness sensor AO → GPIO 34
#define LED_PIN                 2      // Onboard status LED

// Sensor Enable Flags (Set to false if a sensor is physically not connected yet)
#define ENABLE_SOIL_SENSOR      true   // Set to false if soil sensor is not yet wired
#define ENABLE_LEAF_SENSOR      true   // Set to false if leaf sensor is not yet wired

// Analog Sensor Calibration Constants (12-bit ADC range: 0 - 4095)
// Calibrate these numbers by checking dry air vs water readings in Serial Monitor
const int SOIL_DRY  = 3200;   // Soil sensor in dry air  → 0% moisture
const int SOIL_WET  = 1200;   // Soil sensor submerged   → 100% moisture
const int LEAF_DRY  = 4000;   // Rain sensor fully dry   → 0% rain
const int LEAF_WET  = 500;    // Rain sensor soaking wet → 100% rain

// =========================================================================
// 2. HARDWARE INSTANCES & GLOBALS
// =========================================================================

DHT dht(DHTPIN, DHTTYPE);
unsigned long lastTelemetryTime = 0;
bool wifiConfigured = false;
int telemetrySequence = 0;

// =========================================================================
// 3. HELPER FUNCTIONS
// =========================================================================

/**
 * Filtered ADC reader: Takes multiple samples with jitter rejection to 
 * eliminate electrical noise spikes common on ESP32 analog inputs.
 */
int readFilteredADC(int pin) {
  long sum = 0;
  for (int i = 0; i < ANALOG_SAMPLE_COUNT; i++) {
    sum += analogRead(pin);
    delay(5);
  }
  return (int)(sum / ANALOG_SAMPLE_COUNT);
}

/**
 * Soil Moisture calculation with division-by-zero protection and clamping.
 */
float readSoilMoisture() {
  if (!ENABLE_SOIL_SENSOR) return 0.0;
  
  int raw = readFilteredADC(SOIL_PIN);
  if (SOIL_DRY == SOIL_WET) return 0.0; // Avoid division by zero
  
  float pct = (float)(raw - SOIL_DRY) * 100.0 / (float)(SOIL_WET - SOIL_DRY);
  return constrain(pct, 0.0, 100.0);
}

/**
 * Leaf Wetness calculation with division-by-zero protection and clamping.
 */
float readLeafWetness() {
  if (!ENABLE_LEAF_SENSOR) return 0.0;

  int raw = readFilteredADC(LEAF_PIN);
  if (LEAF_DRY == LEAF_WET) return 0.0; // Avoid division by zero

  // Resistance decreases when water droplets bridge the interdigital grid
  float pct = (float)(raw - LEAF_DRY) * 100.0 / (float)(LEAF_WET - LEAF_DRY);
  return constrain(pct, 0.0, 100.0);
}

/**
 * Connects or reconnects to Wi-Fi with non-blocking timeout.
 */
void checkWiFiConnection() {
  if (strcmp(WIFI_SSID, "YOUR_WIFI_SSID") == 0) {
    // Default placeholder not updated by user
    return;
  }

  if (WiFi.status() == WL_CONNECTED) {
    return;
  }

  Serial.println("[WiFi] Establishing connection to AP...");
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 15) {
    delay(400);
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    Serial.print(".");
    attempts++;
  }

  digitalWrite(LED_PIN, LOW);
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WiFi] Connected successfully!");
    Serial.print("[WiFi] IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n[WiFi Warning] Connection timed out. Running in Offline Serial Mode.");
  }
}

/**
 * Sends JSON telemetry packet to FastAPI backend via HTTP POST.
 */
void sendTelemetry(float temp, float hum, float soil, float leaf) {
  if (WiFi.status() != WL_CONNECTED) {
    return; // Operating offline, skip HTTP post
  }

  HTTPClient http;
  http.begin(SERVER_URL);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(2500); // 2.5 second network timeout

  // Build JSON Document
  StaticJsonDocument<256> doc;
  doc["device_id"]     = DEVICE_ID;
  doc["temperature"]   = serialized(String(temp, 1));
  doc["humidity"]      = serialized(String(hum, 1));
  doc["soil_moisture"] = serialized(String(soil, 1));
  doc["leaf_wetness"]  = serialized(String(leaf, 1));   // rain sensor → leaf_wetness field
  doc["rain_intensity"]= serialized(String(leaf, 1));   // also sent as rain_intensity
  doc["source"]        = "HARDWARE";

  String requestBody;
  serializeJson(doc, requestBody);

  digitalWrite(LED_PIN, HIGH);
  int httpCode = http.POST(requestBody);

  if (httpCode > 0) {
    Serial.printf("[HTTP %d] Telemetry pushed: %s\n", httpCode, requestBody.c_str());
  } else {
    Serial.printf("[HTTP Err %d] %s (Target: %s)\n", httpCode, http.errorToString(httpCode).c_str(), SERVER_URL);
  }

  http.end();
  digitalWrite(LED_PIN, LOW);
}

// =========================================================================
// 4. MAIN SETUP
// =========================================================================

void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  // Configure ADC resolution
  analogReadResolution(12); // 12-bit (0-4095)

  Serial.println("\n========================================================");
  Serial.println("  FloraGuard IoT - ESP32 Plant Disease Telemetry Node   ");
  Serial.println("========================================================");
  Serial.printf("Device Identifier: %s\n", DEVICE_ID);
  Serial.printf("DHT11 Signal Pin : GPIO %d\n", DHTPIN);
  Serial.printf("Soil Moisture Pin: GPIO %d (Enabled: %s)\n", SOIL_PIN, ENABLE_SOIL_SENSOR ? "YES" : "NO");
  Serial.printf("Leaf Wetness Pin : GPIO %d (Enabled: %s)\n", LEAF_PIN, ENABLE_LEAF_SENSOR ? "YES" : "NO");

  // Initialize DHT sensor
  dht.begin();

  // Test Wi-Fi if credentials are provided
  checkWiFiConnection();
  
  Serial.println("[System Ready] Starting telemetry loop...\n");
}

// =========================================================================
// 5. MAIN LOOP
// =========================================================================

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - lastTelemetryTime >= TELEMETRY_INTERVAL_MS) {
    lastTelemetryTime = currentMillis;
    telemetrySequence++;

    // Blink status LED on sample
    digitalWrite(LED_PIN, HIGH);
    delay(40);
    digitalWrite(LED_PIN, LOW);

    // 1. Read DHT11 Sensor
    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature();

    // 2. Read Soil Moisture & Leaf Wetness
    float soilMoisture = readSoilMoisture();
    float leafWetness = readLeafWetness();

    // 3. Handle DHT read failure
    if (isnan(humidity) || isnan(temperature)) {
      Serial.printf("[%03d] [DHT Error] Could not read from DHT11 on GPIO %d!\n", telemetrySequence, DHTPIN);
      Serial.println("      -> Check that the Data/'S' wire is plugged into GPIO 4 and 3.3V is connected.");
      return;
    }

    // 4. Print readable Telemetry Log to Serial Monitor
    Serial.printf("[%03d] Temp: %4.1f°C | Hum: %4.1f%% | Soil: %4.1f%% | Rain: %4.1f%% | Wi-Fi: %s\n",
                  telemetrySequence,
                  temperature,
                  humidity,
                  soilMoisture,
                  leafWetness,
                  (WiFi.status() == WL_CONNECTED) ? "ONLINE" : "OFFLINE");

    // 5. Reconnect Wi-Fi periodically if configured but dropped
    if (strcmp(WIFI_SSID, "YOUR_WIFI_SSID") != 0 && WiFi.status() != WL_CONNECTED) {
      checkWiFiConnection();
    }

    // 6. Transmit to FastAPI Backend
    sendTelemetry(temperature, humidity, soilMoisture, leafWetness);
  }
}
