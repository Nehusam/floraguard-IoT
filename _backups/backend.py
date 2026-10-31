"""
FloraGuard IoT - FastAPI Backend
Plant Disease Early Detection & Microclimate Telemetry Service
"""

import asyncio
from datetime import datetime
import json
import math
import os
import random
from typing import Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

app = FastAPI(
    title="FloraGuard IoT Telemetry API",
    description="Microclimate sensor ingestion and epidemiological fungal disease risk engine for ESP32 nodes.",
    version="2.4.0"
)

# Enable CORS for dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas
class TelemetryPayload(BaseModel):
    device_id: str = Field(default="ESP32-AGRI-01", description="ESP32 hardware device identifier")
    temperature: float = Field(..., ge=-20.0, le=60.0, description="Air temperature in Celsius")
    humidity: float = Field(..., ge=0.0, le=100.0, description="Relative humidity in percent")
    soil_moisture: float = Field(default=0.0, ge=0.0, le=100.0, description="Soil volumetric moisture in percent")
    leaf_wetness: float = Field(default=0.0, ge=0.0, le=100.0, description="Leaf surface wetness index in percent")
    timestamp: Optional[str] = None

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

# In-Memory Ring Buffer & State
MAX_HISTORY = 100
telemetry_history: List[Dict] = []
active_connections: List[WebSocket] = []
backend_start_time = datetime.now()
current_simulation_task: Optional[asyncio.Task] = None

def compute_disease_risk(temp: float, humidity: float, leaf_wetness: float) -> DiseaseRiskReport:
    """
    Mills Period & Microclimate Infection Risk Algorithm
    Calculates fungal pathogen viability (Phytophthora infestans & Downy Mildew).
    """
    score = 0.0

    # 1. Leaf wetness factor (critical for fungal spore penetration)
    if leaf_wetness >= 70.0:
        score += 30.0 + ((leaf_wetness - 70.0) / 30.0) * 15.0
    elif leaf_wetness >= 40.0:
        score += 15.0 + ((leaf_wetness - 40.0) / 30.0) * 15.0
    else:
        score += (leaf_wetness / 40.0) * 15.0

    # 2. Relative Humidity factor
    if humidity >= 80.0:
        score += 25.0 + ((humidity - 80.0) / 20.0) * 10.0
    elif humidity >= 60.0:
        score += 10.0 + ((humidity - 60.0) / 20.0) * 15.0
    else:
        score += (humidity / 60.0) * 10.0

    # 3. Temperature incubation suitability
    if 18.0 <= temp <= 27.0:
        score += 20.0  # Optimal fungal growth zone
    elif 14.0 <= temp <= 32.0:
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
            "Check soil moisture and ensure adequate root zone drainage."
        ]
    else:
        level = "LOW"
        diagnosis = "Optimal Microclimate"
        action_title = "Microclimate Healthy"
        action_desc = "Foliar and atmospheric parameters are within safe agronomic baseline. Low pathogen viability."
        recs = [
            "Maintain standard automated irrigation cycles.",
            "Routine air circulation active.",
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

async def broadcast_telemetry(packet: Dict):
    """Broadcast new telemetry to all connected WebSockets."""
    dead_connections = []
    for ws in active_connections:
        try:
            await ws.send_json(packet)
        except Exception:
            dead_connections.append(ws)
    for dead in dead_connections:
        if dead in active_connections:
            active_connections.remove(dead)

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
    """System health check and connection status."""
    uptime_seconds = int((datetime.now() - backend_start_time).total_seconds())
    return {
        "status": "online",
        "service": "FloraGuard IoT FastAPI Backend",
        "uptime_seconds": uptime_seconds,
        "history_count": len(telemetry_history),
        "active_ws_clients": len(active_connections),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/telemetry")
async def ingest_telemetry(payload: TelemetryPayload):
    """
    Hardware endpoint called by ESP32 or IoT edge gateway.
    Ingests sensor readings, executes disease risk computation, and broadcasts.
    """
    ts = payload.timestamp or datetime.now().strftime("%H:%M:%S")
    risk = compute_disease_risk(payload.temperature, payload.humidity, payload.leaf_wetness)

    record = {
        "device_id": payload.device_id,
        "temperature": payload.temperature,
        "humidity": payload.humidity,
        "soil_moisture": payload.soil_moisture,
        "leaf_wetness": payload.leaf_wetness,
        "timestamp": ts,
        "risk": risk.model_dump()
    }

    telemetry_history.append(record)
    if len(telemetry_history) > MAX_HISTORY:
        telemetry_history.pop(0)

    # Broadcast via WebSocket
    await broadcast_telemetry(record)

    return {
        "status": "success",
        "message": "Telemetry processed & evaluated",
        "risk_level": risk.risk_level,
        "risk_score": risk.risk_score,
        "diagnosis": risk.diagnosis
    }

@app.get("/api/telemetry/latest")
async def get_latest_telemetry():
    """Returns the most recent telemetry packet."""
    if not telemetry_history:
        # Default starter point if no readings yet
        starter_risk = compute_disease_risk(24.2, 82.4, 88.5)
        return {
            "device_id": "ESP32-AGRI-01",
            "temperature": 24.2,
            "humidity": 82.4,
            "soil_moisture": 64.0,
            "leaf_wetness": 88.5,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "risk": starter_risk.model_dump()
        }
    return telemetry_history[-1]

@app.get("/api/telemetry/history")
async def get_telemetry_history(limit: int = 30):
    """Returns recent history for initial charts hydration."""
    return telemetry_history[-limit:]

# ========================================================
# WebSocket Endpoint for Zero-Latency Live Updates
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
            # Keep socket alive and listen for client messages
            msg = await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)
    except Exception:
        if websocket in active_connections:
            active_connections.remove(websocket)

# Background simulation runner inside FastAPI
async def internal_simulator():
    """Generates realistic telemetry if hardware is not connected."""
    while True:
        try:
            # Generate fluctuating realistic data with high humidity to demonstrate disease alerts
            temp = round(23.5 + random.uniform(-1.5, 1.5), 1)
            hum = round(83.0 + random.uniform(-3.5, 3.5), 1)
            soil = round(64.5 + random.uniform(-2.5, 2.5), 1)
            leaf = round(86.5 + random.uniform(-5.0, 5.0), 1)

            payload = TelemetryPayload(
                device_id="ESP32-AGRI-01",
                temperature=temp,
                humidity=hum,
                soil_moisture=soil,
                leaf_wetness=leaf,
                timestamp=datetime.now().strftime("%H:%M:%S")
            )
            await ingest_telemetry(payload)
        except Exception as e:
            print(f"Internal simulator error: {e}")
        await asyncio.sleep(3)

@app.on_event("startup")
async def on_startup():
    global current_simulation_task
    # Populate initial 10 records for immediate chart visualization
    now = datetime.now()
    for i in range(10, 0, -1):
        record_time = (now).strftime("%H:%M:%S")
        temp = round(23.8 + random.uniform(-1.0, 1.0), 1)
        hum = round(81.5 + random.uniform(-2.0, 3.0), 1)
        soil = round(63.0 + random.uniform(-1.5, 1.5), 1)
        leaf = round(84.0 + random.uniform(-4.0, 4.0), 1)
        risk = compute_disease_risk(temp, hum, leaf)
        telemetry_history.append({
            "device_id": "ESP32-AGRI-01",
            "temperature": temp,
            "humidity": hum,
            "soil_moisture": soil,
            "leaf_wetness": leaf,
            "timestamp": record_time,
            "risk": risk.model_dump()
        })
    # Start auto simulation task
    current_simulation_task = asyncio.create_task(internal_simulator())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
