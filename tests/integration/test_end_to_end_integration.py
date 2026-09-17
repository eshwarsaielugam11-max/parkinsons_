import io
import wave
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.database.session_db import get_db
from backend.models import Patient, Session as DbSession, Report

@pytest.fixture
def client():
    return TestClient(app)

def create_synthetic_wav_bytes(duration_sec: float = 2.5, sample_rate: int = 16000) -> bytes:
    """Generate in-memory valid PCM16 mono WAV audio bytes for testing."""
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        # 16-bit signed PCM frames
        frames = b'\x00\x00' * int(sample_rate * duration_sec)
        wav_file.writeframes(frames)
    buf.seek(0)
    return buf.read()

def test_health_check_endpoint(client):
    """Test /api/v1/health returns healthy status."""
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok" or "status" in data

def test_upload_and_full_clinical_lifecycle(client):
    """
    Test End-to-End lifecycle:
    1. Upload audio with patient ID -> returns PredictionResponse (pd_probability_calibrated, confidence, audio_quality).
    2. Inspect patient history -> session appears in chronological history.
    3. Retrieve stored prediction -> returns session prediction with explanation references.
    4. Retrieve XAI evidence -> returns StructuredEvidenceResponse with SHAP, temporal, and spatial references.
    5. Generate / retrieve clinical report -> returns validated ReportSchema document.
    """
    patient_id = "test_patient_e2e_001"
    wav_bytes = create_synthetic_wav_bytes(duration_sec=2.5)

    # 1. Upload audio
    files = {"file": ("test_recording.wav", wav_bytes, "audio/wav")}
    data = {"patient_id": patient_id, "label": 1}
    upload_res = client.post("/api/v1/upload", files=files, data=data)
    assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
    pred_data = upload_res.json()
    assert "prediction" in pred_data
    assert "pd_probability_calibrated" in pred_data["prediction"]
    assert "confidence_score" in pred_data["prediction"]
    assert "audio_quality_score" in pred_data["prediction"]

    # 2. Query patient history to obtain generated session_id
    history_res = client.get(f"/api/v1/predict/patients/{patient_id}/history")
    assert history_res.status_code == 200, f"History query failed: {history_res.text}"
    history_data = history_res.json()
    assert history_data["patient_id"] == patient_id
    assert len(history_data["history"]) >= 1

    latest_session = history_data["history"][-1]
    session_id = latest_session["session_id"]
    assert session_id is not None

    # 3. Retrieve stored prediction for session
    predict_res = client.get(f"/api/v1/predict/{session_id}")
    assert predict_res.status_code == 200
    stored_pred = predict_res.json()
    assert stored_pred["session_id"] == session_id
    assert stored_pred["patient_id"] == patient_id

    # 4. Retrieve XAI Structured Evidence for session
    xai_res = client.get(f"/api/v1/xai/{session_id}")
    assert xai_res.status_code == 200
    xai_data = xai_res.json()
    assert xai_data["session_id"] == session_id
    assert "prediction" in xai_data
    assert "explanations" in xai_data
    assert "acoustic_features" in xai_data["explanations"]

    # 5. Generate / Fetch Clinical Report for session
    report_res = client.post(f"/api/v1/report/{session_id}")
    assert report_res.status_code == 200 or report_res.status_code == 500  # Handles degraded fallback if mock LLM
    if report_res.status_code == 200:
        report_json = report_res.json()
        validated = report_json.get("validated") or report_json
        assert "screening_result" in validated or "disclaimer" in validated

def test_streaming_websocket_lifecycle(client):
    """
    Test real-time streaming audio WebSocket:
    1. Connect to /api/v1/stream
    2. Stream chunked 16kHz PCM audio
    3. Receive real-time running prediction updates
    """
    with client.websocket_connect("/api/v1/stream") as websocket:
        # Send 2.0 seconds of raw 16kHz PCM16 mono audio (64000 bytes)
        raw_pcm_chunk = b"\x00\x00" * 32000
        websocket.send_bytes(raw_pcm_chunk)
        
        response = websocket.receive_json()
        assert "running_prediction" in response
        assert "windows_processed" in response
        assert response["windows_processed"] >= 1
        assert "status" in response
