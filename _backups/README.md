# FloraGuard IoT | Plant Disease Early Detection System

A modern, responsive web dashboard and IoT telemetry platform designed for **plant disease early detection** using real-time microclimate sensing, epidemiological risk algorithms (Mills Period & fungal spore germination models), Tailwind CSS, Chart.js, and a FastAPI backend.

---

## 🌟 Key Features

### 1. Header & Live Connection Status Bar
- **FastAPI Core Status**: Pulsing green connection badge displaying live backend status and latency.
- **ESP32 Node Status**: Hardware identity tracking (`ESP32-AGRI-01`) with connection heartbeats.
- **Simulation Mode Toggle**: Toggle between live hardware telemetry streaming and autonomous 3-second simulation.
- **Scenario Presets**: Instantly trigger scenarios (*Normal Growth*, *Blight Risk Warning*, *Severe Outbreak*) to demo epidemiological disease triggers without hardware.

### 2. Real-Time Telemetry Cards
Four glassmorphic telemetry cards with live values, status badges, and dynamic scale indicators:
- **Air Temperature (°C)**: Canopy ambient sensor (DHT22/BME280) with temperature threshold indicators.
- **Air Humidity (%)**: Atmospheric moisture tracking with critical high relative humidity warnings (>80% RH).
- **Soil Moisture (%)**: Root zone moisture with field capacity vs. wilting point analysis.
- **Leaf Wetness (%)**: Surface moisture resistance index—the single most critical parameter for fungal zoospore germination.

### 3. Epidemiological Disease Risk Assessment Engine
- **Circular SVG Arc Risk Meter**: Real-time calculated risk index from `0 to 100%`.
- **Mills Period & Spore Germination Viability**:
  - *Late Blight (`Phytophthora infestans`)*
  - *Downy Mildew (`Plasmopara viticola`)*
  - *Botrytis Gray Mold*
- **Actionable Agronomic Advisories**: Dynamic ventilation recommendations, irrigation rescheduling alerts, and bio-fungicide timing recommendations.

### 4. Dual-Axis Interactive Time-Series Charts (Chart.js)
- **Canopy Microclimate Dynamics**: Dual Y-axis line chart tracking **Air Temperature (°C)** vs. **Air Humidity (%)** over a sliding time window.
- **Hydrological & Foliar Moisture**: Dual Y-axis chart tracking **Soil Moisture (%)** vs. **Leaf Wetness (%)** with custom gradient fills and interactive tooltips.

### 5. Telemetry Log Table
- Live incoming packet feed displaying timestamps, all four sensor readings, calculated risk level, diagnosis, and automated actions taken.
- **Export to CSV**: Download logged data for offline agronomic analysis or reporting.
- **Clear & Filter Controls**: Table management tools.

---

## 📁 Repository Structure

```
Plant Disease Dashoboard-IoT Project/
├── index.html            # Responsive frontend dashboard (Tailwind CSS, Chart.js, Lucide Icons)
├── backend.py            # FastAPI backend with REST API and WebSocket telemetry streaming
├── esp32_firmware.ino    # Arduino C++ sketch for ESP32 with DHT22, capacitive soil, & leaf wetness sensors
├── start.bat             # Quick Windows launcher for FastAPI and dashboard
└── README.md             # Project documentation and wiring guide
```

---

## 🚀 Quick Start Guide

### Option 1: Standalone Browser Simulation (Zero Setup)
Simply double-click or open [index.html](file:///c:/Users/hp/Plant%20Disease%20Dashoboard-IoT%20Project/index.html) in any modern web browser (Google Chrome, Microsoft Edge, Firefox, Brave, Safari).
- Built-in client simulation runs automatically every 3 seconds.
- You can switch between **Normal**, **Blight Risk**, and **Severe** presets using the buttons in the header.

### Option 2: Full Stack with FastAPI Backend
1. Open PowerShell or Terminal in this folder.
2. Run the FastAPI server:
   ```powershell
   python -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload
   ```
3. Open your browser and navigate to:
   ```
   http://127.0.0.1:8000
   ```
4. Access interactive API documentation:
   ```
   http://127.0.0.1:8000/docs
   ```

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the web dashboard (`index.html`) |
| `GET` | `/api/status` | System health, uptime, and connected clients |
| `POST` | `/api/telemetry` | Ingests sensor data from ESP32, evaluates disease risk, and stores record |
| `GET` | `/api/telemetry/latest` | Fetches the most recent sensor packet with full disease diagnosis |
| `GET` | `/api/telemetry/history` | Fetches the last 30 historical records for chart initialization |
| `WS` | `/ws/telemetry` | Real-time WebSocket stream for push updates to connected dashboards |

### ESP32 POST Payload Example:
```json
{
  "device_id": "ESP32-AGRI-01",
  "temperature": 24.5,
  "humidity": 84.2,
  "soil_moisture": 66.0,
  "leaf_wetness": 89.0
}
```

---

## 🔌 ESP32 Hardware Wiring Guide

### 1. DHT11 / DHT22 Sensor Connection (3-Pin Module)
The 3-pin DHT11 breakout module (blue casing with onboard LED) connects directly to the ESP32:

| Sensor Pin Marking | Wire Function | ESP32 Pin | Description |
|---|---|---|---|
| **`+`** / `VCC` | Power (3.3V) | **`3V3`** (or `VIN` / `5V`) | Power supply for sensor and onboard LED |
| **`-`** / `GND` | Ground | **`GND`** | System ground return |
| **`S`** / `DAT` / `OUT` | Digital Data Signal | **`GPIO 4`** (`D4` / `G4`) | Single-bus bidirectional data stream |

> [!NOTE]
> 3-pin DHT11 breakout boards have a built-in pull-up resistor and power LED, so no external resistor is needed.

### 2. Full Multi-Sensor Pin Table
| Component | ESP32 Pin | Note |
|---|---|---|
| **DHT11 / DHT22 Data** | GPIO 4 | Digital canopy temperature & humidity |
| **Soil Moisture Analog Out** | GPIO 34 (ADC1_CH6) | Capacitive Soil Sensor v1.2 |
| **Leaf Wetness Sensor Grid** | GPIO 35 (ADC1_CH7) | Surface resistance / rain grid |
| **Status LED** | GPIO 2 | Blinks on telemetry transmission |
| **VCC** | 3.3V or 5V (sensor dependent) | Power rails |
| **GND** | GND | Common ground |

### 3. Testing Files
- **Instant Sensor Verification**: Flash [dht_sensor_test.ino](file:///c:/Users/hp/Plant%20Disease%20Dashoboard-IoT%20Project/dht_sensor_test.ino) to verify sensor wiring and view live temperature and humidity in the Arduino Serial Monitor (115200 baud).
- **Full Telemetry Node**: Flash [esp32_firmware.ino](file:///c:/Users/hp/Plant%20Disease%20Dashoboard-IoT%20Project/esp32_firmware.ino) to stream live microclimate data to the FastAPI backend and web dashboard.
