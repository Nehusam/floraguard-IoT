# FloraGuard IoT | Plant Disease Detection & Early Warning System

A comprehensive, end-to-end IoT and Machine Learning platform engineered for **agricultural microclimate monitoring, epidemiological fungal disease risk scoring, and automated plant leaf vision diagnostics**.

---

## 🌟 System Architecture Overview

```
 [ DHT11 Air Temp/Hum ]        [ Capacitive Soil Sensor ]      [ Leaf Wetness Grid ]
       (GPIO 4)                          (GPIO 34)                     (GPIO 35)
          │                                  │                             │
          └──────────────────────────┬───────┴─────────────────────────────┘
                                     ▼
                            ┌───────────────────┐
                            │    ESP32 Node     │
                            │  (esp32_firmware) │
                            └─────────┬─────────┘
                                      │ Wi-Fi / HTTP POST JSON
                                      ▼
                      ┌───────────────────────────────┐
                      │   FastAPI Python Backend      │
                      │        (backend.py)           │
                      └───────┬───────────────┬───────┘
                              │               │
            ┌─────────────────┴─┐           ┌─┴─────────────────────────┐
            ▼                   ▼           ▼                           ▼
   [ Mills Period Risk ]  [Ring Buffer]  [Vision AI Classifier]  [WebSocket Stream]
   (Epidemiological Engine) (100 packets)  (/api/predict-image)     (/ws/telemetry)
            │                   │           │                           │
            └───────────────────┴─────┬─────┴───────────────────────────┘
                                      ▼
                        ┌───────────────────────────┐
                        │    FloraGuard Dashboard   │
                        │       (index.html)        │
                        └───────────────────────────┘
```

---

## 📁 Repository Structure

```
Plant Disease Dashoboard-IoT Project/
├── index.html            # Integrated botanical dashboard (Tailwind CSS, Chart.js, Lucide Icons)
├── backend.py            # FastAPI backend with REST API, WebSocket streaming & Leaf Vision AI
├── esp32_firmware.ino    # Production ESP32 firmware with noise filtering & offline fallback
├── dht_sensor_test.ino   # Standalone DHT11 hardware diagnostic test sketch
├── test_integration.py   # Automated integration test suite (100% test coverage)
├── requirements.txt      # Python dependencies (FastAPI, Pillow, NumPy, etc.)
├── start.bat             # One-click Windows startup & dependency checker
├── _backups/             # Archived original project files
└── README.md             # Complete technical & setup documentation
```

---

## 🔌 Hardware Wiring Guide

### 1. DHT11 / DHT22 Sensor Connection (3-Pin Breakout Module)
| Module Silkscreen | Wire Function | ESP32 Pin | Note |
|---|---|---|---|
| **`+`** / `VCC` | Power (3.3V) | **`3V3`** (or `VIN`) | Module onboard power LED will light up red |
| **`-`** / `GND` | Ground | **`GND`** | System common ground |
| **`S`** / `DAT` / `OUT` | Digital Data Bus | **`GPIO 4`** (`D4`) | Single-bus bidirectional data signal |

> [!NOTE]
> 3-pin DHT breakout modules have an onboard SMD pull-up resistor, eliminating the need for external breadboard resistors.

### 2. Multi-Sensor Pin Mapping
| Sensor Component | ESP32 GPIO Pin | Channel | Signal Type |
|---|---|---|---|
| **DHT11 Data** | **GPIO 4** | Digital I/O | Single-bus pulse train |
| **Soil Moisture Sensor** | **GPIO 34** | ADC1_CH6 | Analog (0 – 3.3V) |
| **Leaf Wetness Grid** | **GPIO 35** | ADC1_CH7 | Analog (0 – 3.3V) |
| **Status LED** | **GPIO 2** | Digital Out | Telemetry heartbeat flash |

---

## 💻 Software & Library Setup

### 1. Python Environment Installation
1. Ensure Python 3.10+ is installed.
2. In the project folder, install all required packages:
   ```powershell
   pip install -r requirements.txt
   ```
   *Dependencies: `fastapi`, `uvicorn`, `pydantic`, `python-multipart`, `pillow`, `numpy`, `requests`.*

### 2. Arduino IDE Libraries (for ESP32)
1. Open **Arduino IDE**.
2. Go to **Sketch > Include Library > Manage Libraries...** (or `Ctrl + Shift + I`).
3. Search and install:
   - **`DHT sensor library`** by Adafruit (Click "Install All" to install *Adafruit Unified Sensor* dependency).
   - **`ArduinoJson`** by Benoit Blanchon (v6 or v7).
4. If you have not yet installed the ESP32 board core:
   - Go to **Boards Manager** (left icon) and install **`esp32` by Espressif Systems**.

---

## 🚀 Step-by-Step Running Instructions

### 1. Launch the Backend & Dashboard (One-Click)
Double-click [`start.bat`](file:///c:/Users/hp/Plant%20Disease%20Dashoboard-IoT%20Project/start.bat).
The script automatically:
- Checks your Python version.
- Activates virtual environments (if detected).
- Installs any missing dependencies from `requirements.txt`.
- Checks for port conflicts.
- Starts FastAPI on `http://0.0.0.0:8000`.
- Launches your default web browser to `http://127.0.0.1:8000`.

*Or run manually via terminal:*
```powershell
python -m uvicorn backend:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Standalone DHT11 Sensor Hardware Test
Before configuring Wi-Fi:
1. Open [`dht_sensor_test.ino`](file:///c:/Users/hp/Plant%20Disease%20Dashoboard-IoT%20Project/dht_sensor_test.ino) in Arduino IDE.
2. Select your board (**ESP32 Dev Module**) and your **COM port**.
3. Upload and open the **Serial Monitor** at **115200 baud**.
4. You will see live, real-time temperature and humidity readings every 2 seconds.

### 3. Flash the Full Production Firmware
1. Open [`esp32_firmware.ino`](file:///c:/Users/hp/Plant%20Disease%20Dashoboard-IoT%20Project/esp32_firmware.ino).
2. Update lines 32–37 with your Wi-Fi credentials and computer's IPv4 address:
   ```cpp
   const char* WIFI_SSID     = "YOUR_WIFI_NAME";
   const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
   const char* SERVER_URL    = "http://192.168.X.X:8000/api/telemetry";
   ```
3. If soil or leaf sensors are not yet plugged in, leave `ENABLE_SOIL_SENSOR` and `ENABLE_LEAF_SENSOR` set to `true` or set to `false`. The firmware safely handles disconnected analog pins with zero division protection.
4. Click **Upload**.
5. The ESP32 will connect to Wi-Fi and immediately stream live telemetry to the dashboard via HTTP POST!

---

## 🍃 AI Leaf Disease Vision Classification

The dashboard includes a dedicated **AI Plant Disease Vision Classifier**:
1. Navigate to the **AI Plant Disease Vision Classifier** card on the dashboard.
2. Drag and drop or browse for a plant leaf photo (JPEG, PNG, WEBP).
3. Click **Analyze Leaf Health**.
4. The system executes:
   - **Chlorophyll & Necrosis Segmentation**: Analyzes healthy green ratios, chlorosis (yellowing), and necrotic lesion indices.
   - **Pathogen Identification**: Maps lesion morphology to PlantVillage profiles (*Tomato Early/Late Blight*, *Potato Blight*, *Apple Scab*, *Corn Rust*, etc.).
   - **Environmental Telemetry Cross-Correlation**: Evaluates current ambient humidity and leaf surface wetness against pathogen germination criteria.
   - **Agronomic Prescriptions**: Delivers immediate cultural, biological, and chemical prevention and treatment advisories.

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the web dashboard (`index.html`) |
| `GET` | `/api/status` | System health, operating mode, ESP32 status & client count |
| `GET` | `/api/mode` | Returns current operating mode (`HARDWARE` or `SIMULATION`) |
| `POST` | `/api/mode` | Switches operating mode (`{"mode": "HARDWARE" \| "SIMULATION"}`) |
| `POST` | `/api/telemetry` | Ingests sensor readings from ESP32, runs Mills Period risk scoring |
| `GET` | `/api/telemetry/latest` | Returns the most recent telemetry packet |
| `GET` | `/api/telemetry/history` | Returns historical records for chart initialization |
| `POST` | `/api/predict-image` | Uploads plant leaf image and returns AI pathogen diagnosis |
| `WS` | `/ws/telemetry` | Zero-latency WebSocket stream for real-time dashboard updates |

---

## 🛠️ Common Errors & Troubleshooting

1. **"The monitor configuration is missing" / "Could not connect to COM7"**:
   - Cause: Arduino IDE has not finished installing the ESP32 core package in the background.
   - Solution: Wait until the progress bar in the bottom right finishes and says `Installed esp32`. Then select **Tools > Board > ESP32 Dev Module** and re-select **COM7**.
2. **Sensor readings report `NaN` in Serial Monitor**:
   - Check that sensor `#define DHTTYPE` is set to `DHT11` (for blue sensor).
   - Ensure the Data (`S`) jumper wire is firmly connected to **GPIO 4**.
   - Check that the module's red LED is lit (verifying 3.3V and GND).
3. **ESP32 reports `[HTTP ERROR -1]`**:
   - Cause: The ESP32 cannot reach the computer's IP address.
   - Solution: Verify your computer and ESP32 are connected to the exact same Wi-Fi network (2.4GHz), and make sure Windows Firewall allows inbound connections on port 8000.
