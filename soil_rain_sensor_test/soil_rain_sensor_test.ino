/*
 * =========================================================================
 * FloraGuard IoT - Soil Moisture & Rain Sensor Test Sketch
 * =========================================================================
 *
 * Purpose:
 * Standalone diagnostic sketch to test your soil moisture sensor and
 * rain sensor with the ESP32. No Wi-Fi or backend required.
 *
 * Hardware Connections:
 * -------------------------------------------------------
 * Soil Moisture Sensor  | ESP32 Pin | Description
 * ----------------------|-----------|------------------
 * VCC                   | 3.3V      | Power
 * GND                   | GND       | Ground
 * AO (Analog Out)       | GPIO 35   | Analog signal
 *
 * Rain Sensor           | ESP32 Pin | Description
 * ----------------------|-----------|------------------
 * VCC                   | 3.3V      | Power
 * GND                   | GND       | Ground
 * AO (Analog Out)       | GPIO 34   | Analog signal
 *
 * NOTE: GPIO 34 and 35 are INPUT-ONLY pins on ESP32 — perfect for ADC.
 *       Do NOT connect them to 5V — use 3.3V only!
 *
 * Baud Rate: 115200
 * =========================================================================
 */

// =========================================================================
// PIN DEFINITIONS
// =========================================================================
#define SOIL_PIN        35      // Soil moisture sensor AO → GPIO 35
#define RAIN_PIN        34      // Rain sensor AO → GPIO 34
#define STATUS_LED      2       // Onboard blue LED (GPIO 2)

// =========================================================================
// CALIBRATION VALUES
// =========================================================================
// These are default values. Calibrate them using the raw ADC readings
// shown in Serial Monitor (see CALIBRATION section in setup instructions).

// Soil sensor: 0 ADC = fully submerged in water, 4095 = bone dry air
#define SOIL_DRY        3200    // Raw ADC value when sensor is in dry air
#define SOIL_WET        1200    // Raw ADC value when sensor is in water

// Rain sensor: 0 ADC = soaking wet, 4095 = completely dry
#define RAIN_DRY        4000    // Raw ADC value when sensor is dry
#define RAIN_WET        500     // Raw ADC value when sensor is covered in water

// Number of ADC samples to average (reduces noise)
#define SAMPLE_COUNT    10

// =========================================================================
// HELPER: Read averaged ADC value
// =========================================================================
int readAveragedADC(int pin) {
  long sum = 0;
  for (int i = 0; i < SAMPLE_COUNT; i++) {
    sum += analogRead(pin);
    delay(5);
  }
  return (int)(sum / SAMPLE_COUNT);
}

// =========================================================================
// HELPER: Map raw ADC to 0–100% moisture (clamped)
// =========================================================================
int rawToPercent(int raw, int dryVal, int wetVal) {
  // Map: dryVal → 0%, wetVal → 100%
  int pct = map(raw, dryVal, wetVal, 0, 100);
  return constrain(pct, 0, 100);
}

// =========================================================================
// HELPER: LED blink
// =========================================================================
void blinkLED(int times, int delayMs = 150) {
  for (int i = 0; i < times; i++) {
    digitalWrite(STATUS_LED, HIGH);
    delay(delayMs);
    digitalWrite(STATUS_LED, LOW);
    delay(delayMs);
  }
}

// =========================================================================
// SETUP
// =========================================================================
void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(STATUS_LED, OUTPUT);
  pinMode(SOIL_PIN, INPUT);
  pinMode(RAIN_PIN, INPUT);

  // Startup: 3 quick blinks
  blinkLED(3, 100);

  Serial.println();
  Serial.println("==========================================================");
  Serial.println("  FloraGuard IoT - Soil Moisture & Rain Sensor Test");
  Serial.println("==========================================================");
  Serial.println("  Soil Sensor  → GPIO 35");
  Serial.println("  Rain Sensor  → GPIO 34");
  Serial.println("  Baud Rate    → 115200");
  Serial.println("==========================================================");
  Serial.println();
  Serial.println("CALIBRATION TIP:");
  Serial.println("  Watch 'Raw ADC' values:");
  Serial.println("  - Put soil sensor in DRY air → note raw value → set SOIL_DRY");
  Serial.println("  - Put soil sensor in WATER   → note raw value → set SOIL_WET");
  Serial.println("  - Keep rain sensor DRY       → note raw value → set RAIN_DRY");
  Serial.println("  - Drip water on rain sensor  → note raw value → set RAIN_WET");
  Serial.println();
  Serial.println("----------------------------------------------------------");
  Serial.printf("  %-6s | %-8s | %-8s | %-20s\n",
                "Count", "Sensor", "Raw ADC", "Reading");
  Serial.println("----------------------------------------------------------");

  delay(2000);
}

// =========================================================================
// MAIN LOOP
// =========================================================================
int count = 0;

void loop() {
  count++;

  // --- Read sensors ---
  int soilRaw  = readAveragedADC(SOIL_PIN);
  int rainRaw  = readAveragedADC(RAIN_PIN);

  int soilPct  = rawToPercent(soilRaw, SOIL_DRY, SOIL_WET);
  int rainPct  = rawToPercent(rainRaw, RAIN_DRY, RAIN_WET);

  // --- Soil moisture label ---
  String soilLabel;
  if      (soilPct < 20) soilLabel = "VERY DRY  ⚠️";
  else if (soilPct < 40) soilLabel = "DRY";
  else if (soilPct < 65) soilLabel = "OPTIMAL ✅";
  else if (soilPct < 85) soilLabel = "WET";
  else                    soilLabel = "SATURATED";

  // --- Rain intensity label ---
  String rainLabel;
  if      (rainPct < 10) rainLabel = "DRY / NO RAIN";
  else if (rainPct < 35) rainLabel = "LIGHT DRIZZLE";
  else if (rainPct < 65) rainLabel = "MODERATE RAIN";
  else if (rainPct < 85) rainLabel = "HEAVY RAIN";
  else                    rainLabel = "FLOODING ⚠️";

  // --- Print soil reading ---
  Serial.printf("[%03d] | SOIL     | ADC:%-4d  | %d%% Moisture — %s\n",
                count, soilRaw, soilPct, soilLabel.c_str());

  // --- Print rain reading ---
  Serial.printf("[%03d] | RAIN     | ADC:%-4d  | %d%% Wetness  — %s\n",
                count, rainRaw, rainPct, rainLabel.c_str());

  Serial.println("----------------------------------------------------------");

  // Blink LED once per reading cycle
  blinkLED(1);

  delay(2000);  // Read every 2 seconds
}

