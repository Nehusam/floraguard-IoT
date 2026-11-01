"""
FloraGuard IoT - FastAPI Backend
Plant Disease Early Detection & Microclimate Telemetry Service
Version: 3.0.0
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import io
import json
import math
import os
import random
import sqlite3
from typing import Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# ========================================================
# Pydantic Schemas
# ========================================================
class TelemetryPayload(BaseModel):
    device_id: str = Field(default="ESP32-AGRI-01", description="ESP32 hardware device identifier")
    temperature: float = Field(..., ge=-20.0, le=60.0, description="Air temperature in Celsius")
    humidity: float = Field(..., ge=0.0, le=100.0, description="Relative humidity in percent")
    soil_moisture: float = Field(default=0.0, ge=0.0, le=100.0, description="Soil volumetric moisture in percent")
    leaf_wetness: float = Field(default=0.0, ge=0.0, le=100.0, description="Rain / leaf wetness sensor reading in percent")
    rain_intensity: float = Field(default=0.0, ge=0.0, le=100.0, description="Rain sensor intensity (alias for leaf_wetness)")
    timestamp: Optional[str] = None
    source: Optional[str] = Field(default="HARDWARE", description="HARDWARE or SIMULATION")

class DiseaseRiskReport(BaseModel):
    risk_score: int
    risk_level: str
    diagnosis: str
    action_title: str
    action_desc: str
    recommendations: List[str]
    blight_factor: int
    mildew_factor: int
    botrytis_factor: int
    algorithm_notice: str = "Environmental microclimate estimation model (Mills Period baseline), not a physical laboratory diagnosis."

class ModePayload(BaseModel):
    mode: str = Field(..., description="'HARDWARE' or 'SIMULATION'")

# ========================================================
# SQLite Database Setup (Assignment Requirement 4)
# ========================================================
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "floraguard.db")

def init_db():
    """Initializes the SQLite database with telemetry table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            soil_moisture REAL NOT NULL,
            leaf_wetness REAL NOT NULL,
            rain_intensity REAL NOT NULL,
            risk_score INTEGER NOT NULL,
            risk_level TEXT NOT NULL,
            diagnosis TEXT NOT NULL,
            source TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_created ON sensor_telemetry (created_at DESC)")
    conn.commit()
    conn.close()

def save_telemetry_to_db(record: Dict):
    """Persists a telemetry reading into SQLite database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sensor_telemetry (
                device_id, temperature, humidity, soil_moisture,
                leaf_wetness, rain_intensity, risk_score, risk_level,
                diagnosis, source, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record["device_id"],
            record["temperature"],
            record["humidity"],
            record["soil_moisture"],
            record["leaf_wetness"],
            record.get("rain_intensity", record["leaf_wetness"]),
            record["risk"]["risk_score"],
            record["risk"]["risk_level"],
            record["risk"]["diagnosis"],
            record["source"],
            record["timestamp"]
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB Error] Failed to write telemetry: {e}")

# Call DB initialization on import
init_db()

# ========================================================
# In-Memory State & Ring Buffers
# ========================================================
MAX_HISTORY = 100
telemetry_history: List[Dict] = []
active_connections: List[WebSocket] = []
backend_start_time = datetime.now()

# Operating Mode: "SIMULATION" or "HARDWARE"
operating_mode = "HARDWARE"
simulation_task: Optional[asyncio.Task] = None

# Hardware Node Tracking
last_hardware_seen: Optional[datetime] = None
last_hardware_device_id: Optional[str] = None
HARDWARE_TIMEOUT_SECONDS = 12

# Configurable Epidemiological Risk Thresholds (Mills Period Model)
RISK_THRESHOLDS = {
    "leaf_wetness_high": 70.0,
    "leaf_wetness_mid": 40.0,
    "humidity_high": 80.0,
    "humidity_mid": 60.0,
    "temp_opt_min": 18.0,
    "temp_opt_max": 27.0,
    "temp_perm_min": 14.0,
    "temp_perm_max": 32.0,
}

def compute_disease_risk(temp: float, humidity: float, leaf_wetness: float) -> DiseaseRiskReport:
    """
    Mills Period & Microclimate Infection Risk Algorithm
    Calculates environmental fungal pathogen viability (Phytophthora infestans & Downy Mildew).
    Note: Environmental microclimate indicator, not confirmed biological diagnosis.
    """
    score = 0.0

    # 1. Leaf wetness factor (critical for fungal spore penetration)
    if leaf_wetness >= RISK_THRESHOLDS["leaf_wetness_high"]:
        score += 30.0 + ((leaf_wetness - RISK_THRESHOLDS["leaf_wetness_high"]) / 30.0) * 15.0
    elif leaf_wetness >= RISK_THRESHOLDS["leaf_wetness_mid"]:
        score += 15.0 + ((leaf_wetness - RISK_THRESHOLDS["leaf_wetness_mid"]) / 30.0) * 15.0
    else:
        score += (leaf_wetness / RISK_THRESHOLDS["leaf_wetness_mid"]) * 15.0

    # 2. Relative Humidity factor
    if humidity >= RISK_THRESHOLDS["humidity_high"]:
        score += 25.0 + ((humidity - RISK_THRESHOLDS["humidity_high"]) / 20.0) * 10.0
    elif humidity >= RISK_THRESHOLDS["humidity_mid"]:
        score += 10.0 + ((humidity - RISK_THRESHOLDS["humidity_mid"]) / 20.0) * 15.0
    else:
        score += (humidity / RISK_THRESHOLDS["humidity_mid"]) * 10.0

    # 3. Temperature incubation suitability
    if RISK_THRESHOLDS["temp_opt_min"] <= temp <= RISK_THRESHOLDS["temp_opt_max"]:
        score += 20.0  # Optimal fungal growth zone
    elif RISK_THRESHOLDS["temp_perm_min"] <= temp <= RISK_THRESHOLDS["temp_perm_max"]:
        score += 10.0
    else:
        score += 3.0

    final_score = min(100, max(0, int(round(score))))

    if final_score >= 71:
        level = "HIGH"
        diagnosis = "Severe Fungal Blight Risk"
        action_title = "Critical Disease Alert"
        action_desc = f"Extended leaf wetness ({leaf_wetness:.1f}%) and ambient RH ({humidity:.1f}%) enable spore germination within 4-6 hours."
        recs = [
            "Activate greenhouse exhaust & cross-flow ventilation immediately.",
            "Cease overhead sprinkler cycles; switch to sub-surface drip.",
            "Inspect underside of leaves for visible water-soaked lesions or white mildew mycelium.",
            "Apply preventative bio-fungicide (Trichoderma or Copper spray) within 6 hours."
        ]
    elif final_score >= 41:
        level = "MODERATE"
        diagnosis = "Mildew Warning"
        action_title = "Elevated Spore Incubation"
        action_desc = f"Relative humidity ({humidity:.1f}%) has risen above threshold. Fungal spores can attach to leaf surfaces."
        recs = [
            "Increase canopy air circulation fan speed by 25%.",
            "Monitor foliage for visible white powdery/downy spots over next 3 hours.",
            "Check soil moisture and ensure adequate root zone drainage.",
            "Avoid overhead irrigation during evening hours."
        ]
    else:
        level = "LOW"
        diagnosis = "Optimal Microclimate"
        action_title = "Microclimate Healthy"
        action_desc = "Foliar and atmospheric parameters are within safe agronomic baseline. Low pathogen viability."
        recs = [
            "Maintain standard automated irrigation cycles.",
            "Routine air circulation active.",
            "Regular visual leaf scout protocol.",
            "No chemical or biological fungicide required."
        ]

    blight = min(100, int(round(final_score * 1.05)))
    mildew = min(100, int(round(humidity * 0.9)))
    botrytis = min(100, int(round((leaf_wetness * 0.4) + (humidity * 0.35))))

    return DiseaseRiskReport(
        risk_score=final_score,
        risk_level=level,
        diagnosis=diagnosis,
        action_title=action_title,
        action_desc=action_desc,
        recommendations=recs,
        blight_factor=blight,
        mildew_factor=mildew,
        botrytis_factor=botrytis
    )

def is_hardware_active() -> bool:
    """Check if a real ESP32 node has transmitted within the timeout window."""
    if last_hardware_seen is None:
        return False
    return (datetime.now() - last_hardware_seen).total_seconds() < HARDWARE_TIMEOUT_SECONDS

async def broadcast_telemetry(packet: Dict):
    """Broadcast new telemetry to all connected WebSockets."""
    dead_connections = []
    for ws in list(active_connections):
        try:
            await ws.send_json(packet)
        except Exception:
            dead_connections.append(ws)
    for dead in dead_connections:
        if dead in active_connections:
            active_connections.remove(dead)

# ========================================================
# Background Simulation Task
# ========================================================
async def internal_simulator():
    """Generates realistic telemetry ONLY when operating_mode == 'SIMULATION'."""
    while True:
        try:
            if operating_mode == "SIMULATION":
                # Fluctuating realistic demo values
                temp = round(23.5 + random.uniform(-1.5, 1.5), 1)
                hum = round(78.0 + random.uniform(-4.0, 4.0), 1)
                soil = round(64.5 + random.uniform(-2.5, 2.5), 1)
                leaf = round(68.0 + random.uniform(-6.0, 6.0), 1)

                ts = datetime.now().strftime("%H:%M:%S")
                risk = compute_disease_risk(temp, hum, leaf)

                record = {
                    "device_id": "SIMULATOR-NODE",
                    "temperature": temp,
                    "humidity": hum,
                    "soil_moisture": soil,
                    "leaf_wetness": leaf,
                    "rain_intensity": leaf,
                    "timestamp": ts,
                    "source": "SIMULATION",
                    "is_simulated": True,
                    "risk": risk.model_dump()
                }

                telemetry_history.append(record)
                if len(telemetry_history) > MAX_HISTORY:
                    telemetry_history.pop(0)

                await broadcast_telemetry(record)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[Simulator Warning] {e}")

        await asyncio.sleep(3)

# ========================================================
# Lifespan Management (Startup & Shutdown)
# ========================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    global simulation_task
    # Startup: populate latest hardware records from SQLite database so charts have immediate history
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sensor_telemetry ORDER BY id DESC LIMIT 15")
        rows = cursor.fetchall()
        conn.close()
        for r in reversed(rows):
            rain_val = r["rain_intensity"] if "rain_intensity" in r.keys() else r["leaf_wetness"]
            risk_calc = compute_disease_risk(r["temperature"], r["humidity"], rain_val)
            telemetry_history.append({
                "device_id": r["device_id"],
                "temperature": r["temperature"],
                "humidity": r["humidity"],
                "soil_moisture": r["soil_moisture"],
                "leaf_wetness": rain_val,
                "rain_intensity": rain_val,
                "timestamp": r["timestamp"],
                "source": r["source"],
                "is_simulated": (r["source"] != "HARDWARE"),
                "risk": risk_calc.model_dump()
            })
    except Exception as db_err:
        print(f"[DB Init Load Warning] {db_err}")

    # Fallback if DB empty: create neutral baseline records
    if not telemetry_history:
        now = datetime.now()
        for i in range(5, 0, -1):
            ts = (now - timedelta(seconds=i*3)).strftime("%H:%M:%S")
            temp, hum, soil, leaf = 25.0, 65.0, 50.0, 20.0
            risk = compute_disease_risk(temp, hum, leaf)
            telemetry_history.append({
                "device_id": "ESP32-AGRI-01",
                "temperature": temp,
                "humidity": hum,
                "soil_moisture": soil,
                "leaf_wetness": leaf,
                "rain_intensity": leaf,
                "timestamp": ts,
                "source": "HARDWARE",
                "is_simulated": False,
                "risk": risk.model_dump()
            })

    # Start simulation worker
    simulation_task = asyncio.create_task(internal_simulator())
    yield
    # Shutdown: clean up background task
    if simulation_task and not simulation_task.done():
        simulation_task.cancel()
        try:
            await simulation_task
        except asyncio.CancelledError:
            pass

app = FastAPI(
    title="FloraGuard IoT Telemetry & Disease Detection API",
    description="Microclimate sensor ingestion, epidemiological fungal risk engine, and leaf disease AI.",
    version="3.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================================
# REST Endpoints
# ========================================================

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serves the dashboard index.html directly from FastAPI."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return HTMLResponse("<h1>FloraGuard IoT Dashboard index.html not found</h1>", status_code=404)

@app.get("/api/status")
async def get_system_status():
    """System health check, mode status, and connection info."""
    uptime_seconds = int((datetime.now() - backend_start_time).total_seconds())
    hw_active = is_hardware_active()
    return {
        "status": "online",
        "service": "FloraGuard IoT FastAPI Backend",
        "version": "3.0.0",
        "operating_mode": operating_mode,
        "hardware_connected": hw_active,
        "last_hardware_seen": last_hardware_seen.isoformat() if last_hardware_seen else None,
        "active_device_id": last_hardware_device_id if hw_active else None,
        "uptime_seconds": uptime_seconds,
        "history_count": len(telemetry_history),
        "active_ws_clients": len(active_connections),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/mode")
async def get_operating_mode():
    """Returns current operating mode (HARDWARE or SIMULATION)."""
    return {
        "mode": operating_mode,
        "hardware_active": is_hardware_active(),
        "last_hardware_seen": last_hardware_seen.isoformat() if last_hardware_seen else None,
        "active_device_id": last_hardware_device_id
    }

@app.post("/api/mode")
async def set_operating_mode(payload: ModePayload):
    """Switch between HARDWARE and SIMULATION mode."""
    global operating_mode
    mode = payload.mode.upper()
    if mode not in ["HARDWARE", "SIMULATION"]:
        raise HTTPException(status_code=400, detail="Mode must be 'HARDWARE' or 'SIMULATION'")
    operating_mode = mode
    return {
        "status": "success",
        "mode": operating_mode,
        "message": f"Operating mode switched to {operating_mode}"
    }

@app.post("/api/telemetry")
async def ingest_telemetry(payload: TelemetryPayload):
    """
    Hardware endpoint called by ESP32 via HTTP POST.
    Validates sensor values, evaluates disease risk, stores record, and broadcasts to WebSocket clients.
    """
    global last_hardware_seen, last_hardware_device_id, operating_mode

    # Mark hardware active
    is_hw = (payload.source == "HARDWARE")
    if is_hw:
        last_hardware_seen = datetime.now()
        last_hardware_device_id = payload.device_id
        # Automatically switch to HARDWARE mode when physical device sends data
        if operating_mode == "SIMULATION":
            operating_mode = "HARDWARE"

    ts = payload.timestamp or datetime.now().strftime("%H:%M:%S")
    # rain_intensity is an alias for leaf_wetness (rain sensor)
    rain = max(payload.leaf_wetness, payload.rain_intensity)
    risk = compute_disease_risk(payload.temperature, payload.humidity, rain)

    record = {
        "device_id": payload.device_id,
        "temperature": payload.temperature,
        "humidity": payload.humidity,
        "soil_moisture": payload.soil_moisture,
        "leaf_wetness": rain,
        "rain_intensity": rain,
        "timestamp": ts,
        "source": payload.source,
        "is_simulated": not is_hw,
        "risk": risk.model_dump()
    }

    telemetry_history.append(record)
    if len(telemetry_history) > MAX_HISTORY:
        telemetry_history.pop(0)

    # Persist to SQLite Database
    save_telemetry_to_db(record)

    # Broadcast via WebSocket
    await broadcast_telemetry(record)

    return {
        "status": "success",
        "message": "Telemetry processed & evaluated",
        "mode": operating_mode,
        "is_simulated": not is_hw,
        "risk_level": risk.risk_level,
        "risk_score": risk.risk_score,
        "diagnosis": risk.diagnosis
    }

@app.get("/api/telemetry/latest")
async def get_latest_telemetry():
    """Returns the most recent telemetry packet."""
    if not telemetry_history:
        starter_risk = compute_disease_risk(24.0, 65.0, 20.0)
        return {
            "device_id": "STARTER-NODE",
            "temperature": 24.0,
            "humidity": 65.0,
            "soil_moisture": 60.0,
            "leaf_wetness": 20.0,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "source": "SIMULATION",
            "is_simulated": True,
            "risk": starter_risk.model_dump()
        }
    return telemetry_history[-1]

@app.get("/api/telemetry/history")
async def get_telemetry_history(limit: int = 30):
    """Returns recent history for initial charts hydration."""
    return telemetry_history[-limit:]

@app.get("/api/database/records")
async def get_database_records(limit: int = 50, source: Optional[str] = None):
    """
    Assignment Requirement 4 (Database Support):
    Query persistent telemetry data directly from SQLite database.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if source:
            cursor.execute(
                "SELECT * FROM sensor_telemetry WHERE source = ? ORDER BY id DESC LIMIT ?",
                (source.upper(), limit)
            )
        else:
            cursor.execute(
                "SELECT * FROM sensor_telemetry ORDER BY id DESC LIMIT ?",
                (limit,)
            )
        
        rows = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) FROM sensor_telemetry")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sensor_telemetry WHERE source = 'HARDWARE'")
        hw_count = cursor.fetchone()[0]
        
        conn.close()
        
        records = [dict(row) for row in rows]
        return {
            "status": "success",
            "database": "SQLite3",
            "file": os.path.basename(DB_PATH),
            "total_records": total_count,
            "hardware_records": hw_count,
            "limit": limit,
            "records": records
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")


# ========================================================
# Database Viewer Page (Presentation-friendly)
# ========================================================
@app.get("/database", response_class=HTMLResponse)
async def database_viewer():
    """Serves a clean, visual database viewer page for presentations."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FloraGuard - Database Viewer</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; background: #f0f4f0; color: #1a2e1a; }
  .header { background: linear-gradient(135deg, #1a5c2e, #2d8a4e); color: white; padding: 20px 32px; display: flex; justify-content: space-between; align-items: center; }
  .header h1 { font-size: 22px; font-weight: 600; }
  .header h1 span { background: #ff9800; color: #fff; font-size: 10px; padding: 2px 8px; border-radius: 10px; margin-left: 8px; vertical-align: middle; }
  .header .back-link { color: rgba(255,255,255,0.85); text-decoration: none; font-size: 14px; }
  .header .back-link:hover { color: #fff; }
  .stats-bar { display: flex; gap: 16px; padding: 20px 32px; flex-wrap: wrap; }
  .stat-card { background: white; border-radius: 12px; padding: 16px 24px; flex: 1; min-width: 160px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
  .stat-card .label { font-size: 12px; color: #666; text-transform: uppercase; letter-spacing: 0.5px; }
  .stat-card .value { font-size: 28px; font-weight: 700; color: #1a5c2e; margin-top: 4px; }
  .stat-card .sub { font-size: 12px; color: #999; margin-top: 2px; }
  .controls { padding: 0 32px 16px; display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
  .controls select, .controls input { padding: 8px 14px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; background: white; }
  .controls button { padding: 8px 20px; background: #1a5c2e; color: white; border: none; border-radius: 8px; font-size: 14px; cursor: pointer; }
  .controls button:hover { background: #2d8a4e; }
  .controls .refresh-btn { background: #ff9800; }
  .controls .refresh-btn:hover { background: #f57c00; }
  .table-wrap { padding: 0 32px 32px; overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
  th { background: #1a5c2e; color: white; padding: 12px 16px; text-align: left; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; position: sticky; top: 0; }
  td { padding: 10px 16px; border-bottom: 1px solid #f0f0f0; font-size: 14px; }
  tr:hover td { background: #f8fdf8; }
  .risk-badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }
  .risk-LOW { background: #e8f5e9; color: #2e7d32; }
  .risk-MODERATE { background: #fff3e0; color: #e65100; }
  .risk-HIGH { background: #ffebee; color: #c62828; }
  .risk-CRITICAL { background: #f44336; color: white; }
  .source-badge { display: inline-block; padding: 2px 8px; border-radius: 8px; font-size: 11px; font-weight: 600; }
  .source-HARDWARE { background: #e3f2fd; color: #1565c0; }
  .source-SIMULATION { background: #f3e5f5; color: #7b1fa2; }
  .empty-msg { text-align: center; padding: 60px; color: #999; font-size: 16px; }
  @media (max-width: 768px) { .stats-bar { flex-direction: column; } .table-wrap { padding: 0 12px 20px; } th, td { padding: 8px 10px; font-size: 12px; } }
</style>
</head>
<body>

<div class="header">
  <h1>FloraGuard <span>DATABASE</span></h1>
  <a class="back-link" href="/">Back to Dashboard</a>
</div>

<div class="stats-bar" id="stats">
  <div class="stat-card"><div class="label">Total Records</div><div class="value" id="totalRecords">--</div><div class="sub">All telemetry entries</div></div>
  <div class="stat-card"><div class="label">Hardware Records</div><div class="value" id="hwRecords">--</div><div class="sub">From ESP32 sensors</div></div>
  <div class="stat-card"><div class="label">Database</div><div class="value" style="font-size:20px" id="dbName">SQLite3</div><div class="sub" id="dbFile">floraguard.db</div></div>
  <div class="stat-card"><div class="label">Last Updated</div><div class="value" style="font-size:18px" id="lastUpdated">--</div><div class="sub">Most recent entry</div></div>
</div>

<div class="controls">
  <select id="sourceFilter">
    <option value="">All Sources</option>
    <option value="HARDWARE">Hardware Only</option>
    <option value="SIMULATION">Simulation Only</option>
  </select>
  <select id="limitSelect">
    <option value="20">20 rows</option>
    <option value="50" selected>50 rows</option>
    <option value="100">100 rows</option>
    <option value="200">200 rows</option>
  </select>
  <button onclick="loadData()">Apply Filter</button>
  <button class="refresh-btn" onclick="loadData()">Refresh</button>
</div>

<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>ID</th><th>Device</th><th>Temp (C)</th><th>Humidity (%)</th><th>Soil (%)</th><th>Rain (%)</th><th>Risk</th><th>Level</th><th>Diagnosis</th><th>Source</th><th>Timestamp</th>
      </tr>
    </thead>
    <tbody id="tableBody">
      <tr><td colspan="11" class="empty-msg">Loading...</td></tr>
    </tbody>
  </table>
</div>

<script>
async function loadData() {
  const source = document.getElementById('sourceFilter').value;
  const limit = document.getElementById('limitSelect').value;
  let url = '/api/database/records?limit=' + limit;
  if (source) url += '&source=' + source;
  try {
    const res = await fetch(url);
    const data = await res.json();
    document.getElementById('totalRecords').textContent = data.total_records.toLocaleString();
    document.getElementById('hwRecords').textContent = data.hardware_records.toLocaleString();
    document.getElementById('dbFile').textContent = data.file;
    const tbody = document.getElementById('tableBody');
    if (!data.records || data.records.length === 0) {
      tbody.innerHTML = '<tr><td colspan="11" class="empty-msg">No records found</td></tr>';
      document.getElementById('lastUpdated').textContent = '--';
      return;
    }
    document.getElementById('lastUpdated').textContent = data.records[0].created_at || data.records[0].timestamp || '--';
    tbody.innerHTML = data.records.map(r => '<tr>'
      + '<td>' + r.id + '</td>'
      + '<td>' + r.device_id + '</td>'
      + '<td>' + r.temperature + '</td>'
      + '<td>' + r.humidity + '</td>'
      + '<td>' + r.soil_moisture + '</td>'
      + '<td>' + r.rain_intensity + '</td>'
      + '<td>' + r.risk_score + '/100</td>'
      + '<td><span class="risk-badge risk-' + r.risk_level + '">' + r.risk_level + '</span></td>'
      + '<td>' + (r.diagnosis || '--') + '</td>'
      + '<td><span class="source-badge source-' + r.source + '">' + r.source + '</span></td>'
      + '<td>' + (r.created_at || r.timestamp) + '</td>'
      + '</tr>').join('');
  } catch(e) {
    document.getElementById('tableBody').innerHTML = '<tr><td colspan="11" class="empty-msg">Error: ' + e.message + '</td></tr>';
  }
}
loadData();
setInterval(loadData, 10000);
</script>
</body>
</html>"""


# ========================================================
# WebSocket Endpoint for Live Updates
# ========================================================
@app.websocket("/ws/telemetry")
async def websocket_telemetry_stream(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        # Send latest point on connect if available
        if telemetry_history:
            await websocket.send_json(telemetry_history[-1])
        while True:
            # Keep socket alive and respond to client ping/messages
            msg = await websocket.receive_text()
            if msg == "ping":
                await websocket.send_text("pong")
    except (WebSocketDisconnect, Exception):
        if websocket in active_connections:
            active_connections.remove(websocket)

# ========================================================
# Main Entry Point
# ========================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
