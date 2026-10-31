/*
 * =========================================================================
 * FloraGuard IoT - DHT11 Temperature & Humidity Sensor Test Sketch
 * =========================================================================
 * 
 * Purpose:
 * Standalone verification sketch to test your DHT11 temperature & humidity
 * sensor with the ESP32 without requiring Wi-Fi or backend server setup.
 * 
 * Hardware Connections (3-pin DHT11 Module):
 * -------------------------------------------------------------
 *  DHT11 Module Pin  |  ESP32 Pin   | Description
 * -------------------------------------------------------------
 *  VCC / '+'         |  3V3 (or VIN) | Power (3.3V recommended)
 *  GND / '-'         |  GND          | Ground
 *  DATA / 'S' / OUT  |  GPIO 4 (D4)  | Digital Signal Pin
 * -------------------------------------------------------------
 * 
 * Required Arduino Libraries:
 * 1. "DHT sensor library" by Adafruit
 * 2. "Adafruit Unified Sensor" by Adafruit
 * 
 * How to run:
 * 1. Open this file in Arduino IDE.
 * 2. Select Board: "ESP32 Dev Module" (or your specific ESP32 board).
 * 3. Select Port: COM port of your connected ESP32.
 * 4. Click Upload.
 * 5. Open Serial Monitor (Ctrl + Shift + M) and set baud rate to 115200.
 * =========================================================================
 */

#include <DHT.h>

// Pin Definitions
#define DHTPIN 4        // Digital GPIO connected to DHT11 Data pin (Change if you used another pin, e.g. 15, 5, 18)
#define DHTTYPE DHT11   // Sensor type: DHT11 (Blue module)
#define LED_PIN 2       // Onboard blue status LED on most ESP32 boards

DHT dht(DHTPIN, DHTTYPE);

int sampleCount = 0;

void setup() {
  Serial.begin(115200);
  delay(1000); // Allow serial monitor to initialize

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  Serial.println("\n========================================================");
  Serial.println("   FloraGuard IoT - DHT11 Sensor Diagnostic Utility    ");
  Serial.println("========================================================");
  Serial.printf("Configured Data Pin : GPIO %d\n", DHTPIN);
  Serial.println("Configured Sensor   : DHT11 (Blue Module)");
  Serial.println("Initializing DHT sensor...");

  dht.begin();
  
  // Quick self-test LED flash
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(100);
    digitalWrite(LED_PIN, LOW);
    delay(100);
  }

  Serial.println("Starting continuous sensor readings every 2 seconds...\n");
  Serial.println("-------------------------------------------------------------------------");
  Serial.println(" # | Status | Temp (°C) | Temp (°F) | Humidity (%) | Heat Index (°C)");
  Serial.println("-------------------------------------------------------------------------");
}

void loop() {
  // Blink LED to indicate read attempt
  digitalWrite(LED_PIN, HIGH);
  delay(50);
  digitalWrite(LED_PIN, LOW);

  sampleCount++;

  // Reading temperature or humidity takes about 250 milliseconds!
  float humidity = dht.readHumidity();
  float tempC = dht.readTemperature();
  float tempF = dht.readTemperature(true); // Read Fahrenheit

  // Check if any reads failed
  if (isnan(humidity) || isnan(tempC)) {
    Serial.printf("[%03d] [FAIL] ❌ Unable to read from DHT11 sensor!\n", sampleCount);
    Serial.println("       --> Troubleshooting checks:");
    Serial.println("           1. Verify DATA/'S' wire is in GPIO 4 (or update DHTPIN in code).");
    Serial.println("           2. Verify VCC/`+` is connected to 3V3 (or VIN) and sensor LED is ON.");
    Serial.println("           3. Verify GND/`-` is connected to ESP32 GND.");
    Serial.println("           4. Ensure female jumper wires are pressed firmly into the pins.\n");
  } else {
    // Compute heat index in Celsius
    float heatIndexC = dht.computeHeatIndex(tempC, humidity, false);

    Serial.printf("[%03d] [ OK ]   %5.1f °C  |  %5.1f °F  |    %5.1f %%   |    %5.1f °C\n",
                  sampleCount, tempC, tempF, humidity, heatIndexC);
  }

  // DHT11 requires at least 1.5 - 2.0 seconds between samples
  delay(2000);
}

