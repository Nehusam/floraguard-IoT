"""
FloraGuard IoT - Automated Test Suite
Verifies API endpoints, risk engine, telemetry validation, and vision classification.
"""

import asyncio
import io
import sys
from PIL import Image
from fastapi import UploadFile, HTTPException

import backend

async def run_all_tests():
    print("=" * 65)
    print("  FloraGuard IoT - Automated Integration Test Suite")
    print("=" * 65)
    passed = 0
    total = 0

    # ----------------------------------------------------
    # TEST 1: System Status & Initial State
    # ----------------------------------------------------
    total += 1
    print("\n[TEST 1] Verifying System Status Endpoint...")
    status = await backend.get_system_status()
    assert status["status"] == "online", f"Expected 'online', got {status['status']}"
    assert "uptime_seconds" in status
    print(f"  -> Service: {status['service']} (v{status['version']})")
    print(f"  -> Mode: {status['operating_mode']} | Hardware Connected: {status['hardware_connected']}")
    print("  [PASS] System Status verified.")
    passed += 1

    # ----------------------------------------------------
    # TEST 2: Operating Mode Switching
    # ----------------------------------------------------
    total += 1
    print("\n[TEST 2] Verifying Operating Mode Switch...")
    res = await backend.set_operating_mode(backend.ModePayload(mode="SIMULATION"))
    assert res["mode"] == "SIMULATION"
    res2 = await backend.set_operating_mode(backend.ModePayload(mode="HARDWARE"))
    assert res2["mode"] == "HARDWARE"
    mode_info = await backend.get_operating_mode()
    assert mode_info["mode"] == "HARDWARE"
    print("  [PASS] Operating mode switching (SIMULATION <-> HARDWARE) verified.")
    passed += 1

    # ----------------------------------------------------
    # TEST 3: Hardware Telemetry Ingestion & Risk Engine
    # ----------------------------------------------------
    total += 1
    print("\n[TEST 3] Verifying Hardware Telemetry Ingestion (ESP32-AGRI-01)...")
    payload = backend.TelemetryPayload(
        device_id="ESP32-AGRI-01",
        temperature=25.4,
        humidity=88.5,
        soil_moisture=65.0,
        leaf_wetness=84.0,
        source="HARDWARE"
    )
    ingest_res = await backend.ingest_telemetry(payload)
    assert ingest_res["status"] == "success"
    assert ingest_res["mode"] == "HARDWARE"
    assert ingest_res["is_simulated"] is False
    assert ingest_res["risk_level"] in ["HIGH", "MODERATE", "LOW"]
    print(f"  -> Ingested Hardware Packet: Temp=25.4°C, Hum=88.5%, Leaf=84.0%")
    print(f"  -> Calculated Risk: {ingest_res['risk_score']}/100 ({ingest_res['risk_level']}) - {ingest_res['diagnosis']}")
    assert backend.is_hardware_active() is True, "Hardware should be detected as active!"
    print("  [PASS] Hardware telemetry ingestion and risk calculation verified.")
    passed += 1

    # ----------------------------------------------------
    # TEST 4: Telemetry Ring Buffer & History
    # ----------------------------------------------------
    total += 1
    print("\n[TEST 4] Verifying Telemetry History & Latest Endpoint...")
    latest = await backend.get_latest_telemetry()
    assert latest["device_id"] == "ESP32-AGRI-01"
    assert latest["source"] == "HARDWARE"
    assert latest["is_simulated"] is False
    history = await backend.get_telemetry_history(limit=10)
    assert len(history) > 0
    print(f"  -> Ring Buffer History Count: {len(history)} records")
    print(f"  -> Latest Record Timestamp: {latest['timestamp']} (Source: {latest['source']})")
    print("  [PASS] Telemetry history and ring buffer verified.")
    passed += 1

    # ----------------------------------------------------
    # TEST 5: Plant Disease Vision AI Classifier (Healthy Leaf)
    # ----------------------------------------------------
    total += 1
    print("\n[TEST 5] Testing Vision AI: Healthy Tomato Leaf Image...")
    healthy_img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    buf = io.BytesIO()
    healthy_img.save(buf, format="JPEG")
    buf.seek(0)
    upload_file = UploadFile(filename="healthy_tomato.jpg", file=buf)
    pred = await backend.predict_plant_disease(upload_file)
    assert pred.is_healthy is True
    assert "Healthy" in pred.predicted_class
    print(f"  -> Result: {pred.predicted_class} (Confidence: {pred.confidence}%)")
    print(f"  -> Is Healthy: {pred.is_healthy}")
    print(f"  -> Environmental Correlation: {pred.environmental_correlation}")
    print("  [PASS] Healthy leaf classification verified.")
    passed += 1

    # ----------------------------------------------------
    # TEST 6: Plant Disease Vision AI Classifier (Diseased/Necrotic Leaf)
    # ----------------------------------------------------
    total += 1
    print("\n[TEST 6] Testing Vision AI: Diseased/Blight Leaf Image...")
    diseased_img = Image.new("RGB", (224, 224), color=(110, 50, 20))
    buf2 = io.BytesIO()
    diseased_img.save(buf2, format="JPEG")
    buf2.seek(0)
    upload_file2 = UploadFile(filename="blight_leaf.jpg", file=buf2)
    pred2 = await backend.predict_plant_disease(upload_file2)
    assert pred2.is_healthy is False
    assert len(pred2.symptoms) > 0
    assert len(pred2.treatment) > 0
    print(f"  -> Result: {pred2.predicted_class} (Confidence: {pred2.confidence}%)")
    print(f"  -> Pathogen Symptoms: {pred2.symptoms[0]}")
    print(f"  -> Action Protocol: {pred2.treatment[0]}")
    print("  [PASS] Diseased leaf classification & treatment recommendation verified.")
    passed += 1

    # ----------------------------------------------------
    # TEST 7: Invalid File Handling
    # ----------------------------------------------------
    total += 1
    print("\n[TEST 7] Verifying Invalid File Format Rejection...")
    dummy_buf = io.BytesIO(b"not an image file")
    bad_file = UploadFile(filename="test.txt", file=dummy_buf)
    try:
        await backend.predict_plant_disease(bad_file)
        raise AssertionError("Should have raised HTTPException 400 for bad extension!")
    except HTTPException as e:
        assert e.status_code == 400
        print(f"  -> Successfully caught invalid upload: {e.detail}")
    print("  [PASS] Invalid file rejection verified.")
    passed += 1

    print("\n" + "=" * 65)
    print(f"  TEST SUMMARY: {passed}/{total} tests PASSED (100% SUCCESS)")
    print("=" * 65)

if __name__ == "__main__":
    asyncio.run(run_all_tests())

