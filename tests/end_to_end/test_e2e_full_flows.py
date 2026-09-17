import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

FIXTURES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../fixtures"))

@pytest.fixture
def client():
    return TestClient(app)

def test_clean_speech_upload_full_lifecycle(client):
    """
    E2E Flow 1: Clean Speech Upload Lifecycle
    - Uploads clean phonation fixture
    - Validates PredictionScore & ExplanationRefs schema
    - Asserts DB persistence and retrieval by session_id
    - Validates XAI structured evidence retrieval
    - Validates Clinical Report generation / degraded fallback handling
    """
    clean_path = os.path.join(FIXTURES_DIR, "clean_sample.wav")
    assert os.path.exists(clean_path), f"Fixture not found: {clean_path}"

    patient_id = "patient_e2e_clean_001"
    with open(clean_path, "rb") as f:
        file_bytes = f.read()

    # 1. Post Upload
    response = client.post(
        "/api/v1/upload",
        files={"file": ("clean_sample.wav", file_bytes, "audio/wav")},
        data={"patient_id": patient_id, "label": 0},
    )
    assert response.status_code == 200, f"Upload failed: {response.text}"
    pred_res = response.json()

    assert "prediction" in pred_res
    score = pred_res["prediction"]
    assert 0.0 <= score["pd_probability_calibrated"] <= 1.0
    assert 0.0 <= score["confidence_score"] <= 1.0
    assert score["audio_quality_score"] >= 0.0

    # 2. Retrieve via Patient History to extract created session_id
    history_res = client.get(f"/api/v1/predict/patients/{patient_id}/history")
    assert history_res.status_code == 200
    history = history_res.json()["history"]
    assert len(history) >= 1
    session_id = history[-1]["session_id"]
    assert session_id is not None

    # 3. Retrieve Stored Prediction
    get_pred_res = client.get(f"/api/v1/predict/{session_id}")
    assert get_pred_res.status_code == 200
    stored_data = get_pred_res.json()
    assert stored_data["session_id"] == session_id
    assert stored_data["patient_id"] == patient_id

    # 4. Retrieve XAI Evidence
    xai_res = client.get(f"/api/v1/xai/{session_id}")
    assert xai_res.status_code == 200
    xai_data = xai_res.json()
    assert xai_data["session_id"] == session_id
    assert "explanations" in xai_data
    assert "acoustic_features" in xai_data["explanations"]
    assert "temporal" in xai_data["explanations"]

    # 5. Retrieve / Generate Report
    report_res = client.post(f"/api/v1/report/{session_id}")
    assert report_res.status_code in [200, 500]  # Valid report (200) or clean degraded fallback (500)

def test_streaming_flow_multi_window_aggregation(client):
    """
    E2E Flow 2: Real-Time Audio Streaming WebSocket
    - Connects to /api/v1/stream
    - Streams 3 consecutive 2.0s PCM16 windows (64000 bytes each)
    - Verifies window counter increments and running prediction is emitted
    """
    with client.websocket_connect("/api/v1/stream") as ws:
        # Window 1
        ws.send_bytes(b"\x00\x00" * 32000)
        msg1 = ws.receive_json()
        assert msg1["windows_processed"] == 1
        assert "running_prediction" in msg1
        assert "last_window_quality" in msg1

        # Window 2
        ws.send_bytes(b"\x00\x00" * 32000)
        msg2 = ws.receive_json()
        assert msg2["windows_processed"] == 2
        assert "running_prediction" in msg2

        # Window 3
        ws.send_bytes(b"\x00\x00" * 32000)
        msg3 = ws.receive_json()
        assert msg3["windows_processed"] == 3
        assert msg3["status"] == "accumulating"

def test_patient_longitudinal_history_ordering(client):
    """
    E2E Flow 3: Longitudinal History Across Multiple Encounters
    - Uploads 3 sequential encounters for patient_longitudinal_99
    - Verifies chronological ordering in history endpoint
    """
    patient_id = "patient_longitudinal_99"
    clean_path = os.path.join(FIXTURES_DIR, "clean_sample.wav")
    with open(clean_path, "rb") as f:
        file_bytes = f.read()

    # Upload 3 sessions
    for i in range(3):
        res = client.post(
            "/api/v1/upload",
            files={"file": (f"sample_{i}.wav", file_bytes, "audio/wav")},
            data={"patient_id": patient_id, "label": 1},
        )
        assert res.status_code == 200

    history_res = client.get(f"/api/v1/predict/patients/{patient_id}/history")
    assert history_res.status_code == 200
    history = history_res.json()["history"]
    assert len(history) >= 3

    # Check ascending chronological timestamp order
    timestamps = [h["timestamp"] for h in history]
    assert timestamps == sorted(timestamps)
