/*
 * =========================================================================
 * FloraGuard IoT - ESP32 Plant Disease Early Detection Firmware
 * =========================================================================
 * 
 * Hardware Sensors:
 * - DHT11 / DHT22: Air Temperature & Relative Humidity (Pin D4)
 * - Capacitive Soil Moisture Sensor v1.2: Analog Soil Moisture (Pin ADC34)
 * - Leaf Wetness Sensor / Interdigital Grid: Foliar Surface Moisture (Pin ADC35)
 * - Status LED: Pin D2 (Blinks on telemetry transmission)
 * 
 * Telemetry Protocol:
 * - Sends JSON payload via HTTP POST to FastAPI backend (/api/telemetry)
 * =========================================================================
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// WiFi Configuration
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// FastAPI Server Address (Your computer's current Wi-Fi IPv4 address)
const char* serverUrl = "http://192.168.98.227:8000/api/telemetry";

// Pin Definitions
#define DHTPIN 4
#define DHTTYPE DHT11    // Set to DHT11 for blue sensor module (use DHT22 for white AM2302)
#define SOIL_PIN 34
#define LEAF_PIN 35
#define LED_PIN 2

DHT dht(DHTPIN, DHTTYPE);

// Calibration constants (Calibrate in dry air vs immersed in water)
const int SOIL_DRY = 3200;   // 0% moisture (dry air)
const int SOIL_WET = 1400;   // 100% moisture (submerged)
const int LEAF_DRY = 4095;   // 0% wetness (dry surface)
const int LEAF_WET = 1200;   // 100% wetness (water droplet layer)

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  dht.begin();

  Serial.println("\n[FloraGuard] Starting ESP32 Plant Telemetry Node...");
  Serial.printf("[Sensor] DHT11 configured on GPIO %d\n", DHTPIN);

  // Connect to WiFi with timeout (does not freeze if testing offline)
  WiFi.begin(ssid, password);
  Serial.print("[WiFi] Connecting to ");
  Serial.print(ssid);

  int wifiAttempts = 0;
  const int maxAttempts = 20; // 10 seconds timeout

  while (WiFi.status() != WL_CONNECTED && wifiAttempts < maxAttempts) {
    delay(500);
    Serial.print(".");
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    wifiAttempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    digitalWrite(LED_PIN, LOW);
    Serial.println("\n[WiFi] Connected! IP Address: " + WiFi.localIP().toString());
  } else {
    digitalWrite(LED_PIN, LOW);
    Serial.println("\n[WiFi Warning] WiFi connection timed out or credentials not configured.");
    Serial.println("[Offline Test Mode] Continuing local sensor sampling over Serial Monitor...");
  }
}

float readSoilMoisture() {
  int raw = analogRead(SOIL_PIN);
  float pct = map(raw, SOIL_DRY, SOIL_WET, 0, 100);
  return constrain(pct, 0.0, 100.0);
}

float readLeafWetness() {
  int raw = analogRead(LEAF_PIN);
  // Lower resistance with water droplets across the grid
  float pct = map(raw, LEAF_DRY, LEAF_WET, 0, 100);
  return constrain(pct, 0.0, 100.0);
}

void sendTelemetry(float temp, float hum, float soil, float leaf) {
  if (WiFi.status() != WL_CONNECTED) {
    // In offline testing mode or lost connection; skip HTTP transmission
    return;
  }

  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");

  // Create JSON document
  StaticJsonDocument<256> doc;
  doc["device_id"] = "ESP32-AGRI-01";
  doc["temperature"] = temp;
  doc["humidity"] = hum;
  doc["soil_moisture"] = soil;
  doc["leaf_wetness"] = leaf;

  String requestBody;
  serializeJson(doc, requestBody);

  digitalWrite(LED_PIN, HIGH);
  int httpResponseCode = http.POST(requestBody);

  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.printf("[HTTP %d] Telemetry transmitted successfully: %s\n", httpResponseCode, requestBody.c_str());
  } else {
    Serial.printf("[HTTP ERROR %d] Post failed: %s\n", httpResponseCode, http.errorToString(httpResponseCode).c_str());
  }

  http.end();
  digitalWrite(LED_PIN, LOW);
}

void loop() {
  // Read sensors
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  float soilMoisture = readSoilMoisture();
  float leafWetness = readLeafWetness();

  // Validate DHT reading
  if (isnan(humidity) || isnan(temperature)) {
    Serial.printf("[Sensor Error] Failed to read from DHT11 on GPIO %d! Check signal wire & 3.3V.\n", DHTPIN);
    delay(2000);
    return;
  }

  Serial.printf("[Telemetry] Temp: %.1f°C | Hum: %.1f%% | Soil: %.1f%% | LeafWetness: %.1f%%\n",
                temperature, humidity, soilMoisture, leafWetness);

  // Send packet to FastAPI backend
  sendTelemetry(temperature, humidity, soilMoisture, leafWetness);

  // Sampling interval: 3 seconds
  delay(3000);
}
