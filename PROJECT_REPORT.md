# AMAL JYOTHI COLLEGE OF ENGINEERING, KANJIRAPPALLY
## DEPARTMENT OF COMPUTER APPLICATIONS
### 24MCAT213 - INTERNET OF THINGS (MCA 2025-27, S3)
### COMBINED ASSIGNMENT & PROJECT REPORT

---

# PROJECT TITLE: FloraGuard IoT
## Microclimate Telemetry & Plant Pathogen Early Warning System with Containerized Backend & Real-Time Dashboard

**Student Name:** ________________________  
**Register No:** ________________________  
**Course Code:** 24MCAT213 - Internet of Things  
**Date of Submission:** October 31, 2026  

---

## 1. ABSTRACT
FloraGuard IoT is an end-to-end smart agricultural microclimate telemetry and automated plant pathogen early warning system. Using an **ESP32 microcontroller**, the system acquires environmental metrics from three physical sensor nodes: ambient temperature and relative humidity via a **DHT11 sensor**, soil volumetric moisture via an **analog capacitive soil probe**, and precipitation/leaf moisture via a **conductive rain sensor grid**.

The sensor readings are packaged into structured JSON payloads and transmitted via Wi-Fi HTTP POST to a containerized **FastAPI** backend service backed by an **SQLite3 database**. An epidemiological risk calculation engine implements the agricultural **Mills Period Infection Model** to evaluate fungal late blight (*Phytophthora infestans*) and downy mildew risks in real time. The live readings and risk alerts are visualized on a modern botanical dashboard via WebSockets.

---

## 2. HARDWARE SPECIFICATIONS & CIRCUIT CONNECTIONS

### 2.1 Hardware Components
1. **ESP32 Dev Module (NodeMCU-32S / ESP-WROOM-32)**: Dual-core 240MHz Xtensa LX6 microcontroller with built-in Wi-Fi (802.11 b/g/n) and 12-bit ADC.
2. **DHT11 Sensor Module**: Digital temperature (0–50°C, ±2°C) and relative humidity (20–90% RH, ±5%) sensor.
3. **Capacitive Soil Moisture Sensor v1.2**: Corrosion-resistant analog probe measuring dielectric permittivity of soil.
4. **Rain / Leaf Wetness Detection Module**: Nickel-coated interdigital PCB tracking precipitation and dew film.

### 2.2 Pinout & Interfacing Matrix
| Sensor Module | Sensor Pin | ESP32 Pin | Function / Type |
|---|---|---|---|
| **DHT11** | VCC | 3.3V | Power (3.3V DC) |
| **DHT11** | GND | GND | Ground |
| **DHT11** | DATA / OUT | **GPIO 4** | One-Wire Digital In/Out |
| **Soil Moisture** | VCC | 3.3V | Power (3.3V DC) |
| **Soil Moisture** | GND | GND | Ground |
| **Soil Moisture** | AO (Analog Out) | **GPIO 35** | ADC1_CH7 (Analog Input) |
| **Rain Sensor** | VCC | 3.3V | Power (3.3V DC) |
| **Rain Sensor** | GND | GND | Ground |
| **Rain Sensor** | AO (Analog Out) | **GPIO 34** | ADC1_CH6 (Analog Input) |
| **Status LED** | Anode (+) | **GPIO 2** | Onboard Blue Status Indicator |

```
                 +-----------------------+
                 |       ESP32 Node      |
                 |                       |
  DHT11 (DATA) --| GPIO 4        GPIO 35 |-- Soil AO (Analog)
                 |               GPIO 34 |-- Rain AO (Analog)
                 |                GPIO 2 |-- Onboard Status LED
                 | 3.3V              GND |
                 +---+----------------+--+
                     |                |
             To Sensors (VCC)  To Sensors (GND)
```

---

## 3. DATA COMMUNICATION ARCHITECTURE

The ESP32 firmware samples the sensors every 3,000 ms (3 seconds), applies a 10-sample moving average filter on analog inputs to eliminate electrical ADC noise, and formats the data into JSON:

```json
{
  "device_id": "ESP32-AGRI-01",
  "temperature": 30.0,
  "humidity": 77.0,
  "soil_moisture": 21.6,
  "leaf_wetness": 91.1,
  "rain_intensity": 91.1,
  "source": "HARDWARE"
}
```

This payload is transmitted via HTTP POST to the backend endpoint:
`http://<SERVER_IP>:8000/api/telemetry`

---

## 4. DATABASE DESIGN & PERSISTENCE (Requirement 4)

The backend utilizes an **SQLite3 relational database** (`floraguard.db`) for long-term historical storage of sensor readings and computed epidemiological diagnoses.

### 4.1 Relational Schema: `sensor_telemetry` Table
| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique sequence identifier |
| `device_id` | TEXT | NOT NULL | Microcontroller hardware identifier |
| `temperature` | REAL | NOT NULL | Ambient canopy air temperature (°C) |
| `humidity` | REAL | NOT NULL | Canopy relative humidity (% RH) |
| `soil_moisture` | REAL | NOT NULL | Volumetric soil moisture (%) |
| `leaf_wetness` | REAL | NOT NULL | Surface film wetness index (%) |
| `rain_intensity` | REAL | NOT NULL | Precipitation intensity index (%) |
| `risk_score` | INTEGER | NOT NULL | Pathogen risk index (0–100 scale) |
| `risk_level` | TEXT | NOT NULL | LOW / MODERATE / HIGH risk classification |
| `diagnosis` | TEXT | NOT NULL | Evaluated epidemiological plant threat |
| `source` | TEXT | NOT NULL | HARDWARE or SIMULATION |
| `timestamp` | TEXT | NOT NULL | Sample collection timestamp (HH:MM:SS) |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Server ingestion datetime |

### 4.2 Database API Endpoint
A dedicated REST endpoint allows querying the stored database records:
- **`GET /api/database/records?limit=50&source=HARDWARE`**
- Returns record counts, total entries, and JSON structured records.

---

## 5. CONTAINERIZATION (DOCKER) (Requirement 3)

The backend service is containerized using **Docker** and orchestrated with **Docker Compose**, ensuring reproducible deployment across any operating environment.

### 5.1 Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/
EXPOSE 8000
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 5.2 Deployment Command
```bash
docker compose up -d --build
```
This launches `floraguard_iot_service` with port `8000` mapped and the `floraguard.db` mounted on a persistent volume.

---

## 6. REAL-TIME DASHBOARD (Requirement 5)

The dashboard is built using standard HTML5, Tailwind CSS, Lucide Icons, and Chart.js.
- **WebSocket Streaming (`/ws/telemetry`):** Automatically pushes real-time telemetry packets to connected browser sessions without polling overhead.
- **Microclimate Cards:** 4 real-time parameter cards (Air Temp, Relative Humidity, Soil Moisture, Rain Intensity).
- **Disease Assessment Engine:** Computes fungal blight risk using Mills Period baseline and provides immediate remediation guidelines.
- **Dual Visual Charts:** Real-time historical line charts for Atmospheric (Temp vs Humidity) and Hydrological (Soil vs Rain) readings.
- **AI Leaf Vision Classifier:** Integrated computer vision model for diagnosing diseased plant leaves from photographs.

---

## 7. TESTING, DEMONSTRATION & RESULTS (Requirement 6)

| Test Case | Procedure | Expected Output | Result |
|---|---|---|:---:|
| **TC-01** | Power ESP32 & Connect to Wi-Fi AP | ESP32 obtains IP, Serial prints "Connected successfully!" | **PASS** |
| **TC-02** | Read DHT11 Temperature & Humidity | Serial Monitor displays valid °C and % values (non-NaN) | **PASS** |
| **TC-03** | Submerge Soil Moisture Probe in Water | Analog ADC drops; moisture percentage increases >70% | **PASS** |
| **TC-04** | Drip Water Droplets onto Rain Sensor Grid | ADC changes; Rain Intensity reading rises >80% | **PASS** |
| **TC-05** | HTTP POST to Backend `/api/telemetry` | HTTP 200 response; payload ingested & validated | **PASS** |
| **TC-06** | Database Record Persistence | SQLite records created in `floraguard.db` table | **PASS** |
| **TC-07** | Dashboard WebSocket Broadcast | Dashboard badge switches to "LIVE HARDWARE DATA" | **PASS** |

---

## 8. CONCLUSION & OBSERVATIONS
All requirements specified in the MCA IoT assignment have been successfully fulfilled:
1. **Sensors Interfaced:** Multi-sensor array with DHT11, soil moisture, and rain detection operational on ESP32.
2. **Communication:** Reliable Wi-Fi HTTP POST communication with automatic reconnection.
3. **Containerization:** Production-ready `Dockerfile` and `docker-compose.yml` for multi-platform deployment.
4. **Database:** Robust SQLite3 database with structured relational schema and audit logging.
5. **Dashboard:** High-performance responsive web dashboard featuring live WebSocket telemetry and automated plant disease risk analytics.

