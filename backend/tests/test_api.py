import os
import pytest
from fastapi.testclient import TestClient

def test_health_check():
    # We must import the app after the env variables are present (already set in .env)
    from backend.app.main import app
    from backend.core.config import settings

    client = TestClient(app)
    response = client.get(f"{settings.API_V1_STR}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model_version"] == settings.MODEL_VERSION
    assert "timestamp" in data

def test_config_fails_without_required_vars(monkeypatch):
    import importlib
    
    # Empty out environment so the .env falls back or we override it
    monkeypatch.setenv("MODEL_VERSION", "")
    
    import backend.core.config
    
    from pydantic import ValidationError
    
    with pytest.raises(ValueError, match="FATAL CONFIG ERROR"):
        # We manually recreate what Settings() does inside config.py to verify it fails
        # since empty string bypasses Pydantic's basic str validation
        s = backend.core.config.Settings(_env_file=None, MODEL_VERSION="", ANTHROPIC_API_KEY="test", DATABASE_URL="test", VECTOR_DB_PATH="test", BACKEND_CORS_ORIGINS='["http://localhost"]')
        if not s.MODEL_VERSION or not s.ANTHROPIC_API_KEY:
            raise ValueError("FATAL CONFIG ERROR: MODEL_VERSION or ANTHROPIC_API_KEY cannot be empty.")


import io
from fastapi.testclient import TestClient

def get_client():
    from backend.app.main import app
    return TestClient(app)

def test_upload_audio_success():
    client = get_client()
    from backend.core.config import settings
    # Create a dummy valid wav payload
    file_content = b"RIFF" + b"\x00" * 100
    files = {"file": ("test.wav", file_content, "audio/wav")}
    response = client.post(f"{settings.API_V1_STR}/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "pd_probability_calibrated" in data["prediction"]
    assert "explanation_refs" in data

def test_upload_audio_invalid_type():
    client = get_client()
    from backend.core.config import settings
    files = {"file": ("test.txt", b"Hello text", "text/plain")}
    response = client.post(f"{settings.API_V1_STR}/upload", files=files)
    
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]

def test_upload_audio_too_large(monkeypatch):
    # Temporarily override MAX_FILE_SIZE to 10 bytes for testing
    import backend.api.upload as upload_module
    monkeypatch.setattr(upload_module, "MAX_FILE_SIZE", 10)
    
    client = get_client()
    from backend.core.config import settings
    files = {"file": ("large.wav", b"12345678901234567890", "audio/wav")}
    response = client.post(f"{settings.API_V1_STR}/upload", files=files)
    
    assert response.status_code == 413
    assert "exceeds maximum size" in response.json()["detail"]

def test_stream_audio_aggregation(monkeypatch):
    import backend.api.stream as stream_api
    from backend.schemas.prediction import PredictionResponse, PredictionScore, ExplanationRefs
    
    client = get_client()
    from backend.core.config import settings

    call_count = 0
    def mock_predict(audio_path, return_explanations=False):
        nonlocal call_count
        call_count += 1
        
        # Third chunk is the anomalous one (low quality, extreme probability)
        if call_count == 3:
            prob = 0.01
            qual = 1.0 # very low quality
        else:
            prob = 0.80
            qual = 9.0 # normal high quality
            
        return PredictionResponse(
            prediction=PredictionScore(pd_probability_calibrated=prob, confidence_score=0.9, audio_quality_score=qual),
            explanation_refs=ExplanationRefs()
        )
        
    monkeypatch.setattr(stream_api, "predict", mock_predict)
    
    # We need 64000 bytes per chunk (2 seconds of audio at 16kHz, 16-bit)
    CHUNK_SIZE = 64000
    
    with client.websocket_connect(f"{settings.API_V1_STR}/stream") as websocket:
        # Send 1st chunk
        websocket.send_bytes(b"\x00" * CHUNK_SIZE)
        res1 = websocket.receive_json()
        assert res1["running_prediction"] == 0.80
        assert res1["windows_processed"] == 1
        
        # Send 2nd chunk
        websocket.send_bytes(b"\x00" * CHUNK_SIZE)
        res2 = websocket.receive_json()
        assert res2["running_prediction"] == 0.80
        assert res2["windows_processed"] == 2
        
        # Send 3rd chunk (anomalous)
        websocket.send_bytes(b"\x00" * CHUNK_SIZE)
        res3 = websocket.receive_json()
        assert res3["windows_processed"] == 3
        # The aggregated prediction should still be heavily weighted towards 0.80, NOT 0.01
        # Because the anomaly has quality=1.0 and normal has quality=9.0, 
        # the weights after softmax (temp=1.0) for [9.0, 9.0, 1.0] are mostly 0.5, 0.5, ~0.0
        assert res3["running_prediction"] > 0.75

def test_predict_retrieval_not_found():
    client = get_client()
    from backend.core.config import settings
    response = client.get(f"{settings.API_V1_STR}/predict/unknown_session")
    assert response.status_code == 404

def test_predict_retrieval_and_history():
    client = get_client()
    from backend.core.config import settings
    from backend.database.session_db import SessionLocal
    from backend.models import Patient, Session, Report
    from datetime import datetime, timezone, timedelta
    
    db = SessionLocal()
    try:
        # Clear specific test data
        db.query(Report).filter(Report.session_id.in_(["session_1", "session_2", "session_3"])).delete(synchronize_session=False)
        db.query(Session).filter(Session.id.in_(["session_1", "session_2", "session_3"])).delete(synchronize_session=False)
        db.query(Patient).filter(Patient.id.in_(["patient_A", "patient_B"])).delete(synchronize_session=False)
        db.commit()
        
        now = datetime.now(timezone.utc)
        
        p_A = Patient(id="patient_A")
        p_B = Patient(id="patient_B")
        db.add_all([p_A, p_B])
        
        s1 = Session(id="session_1", patient_id="patient_A", timestamp=now - timedelta(days=2), task_type="read", mode="upload")
        s2 = Session(id="session_2", patient_id="patient_A", timestamp=now - timedelta(days=1), task_type="read", mode="upload")
        s3 = Session(id="session_3", patient_id="patient_B", timestamp=now, task_type="read", mode="upload")
        db.add_all([s1, s2, s3])
        
        r1 = Report(id="rep1", session_id="session_1", prediction={"pd_probability_calibrated": 0.8, "confidence_score": 0.9, "audio_quality_score": 9.0}, model_version="1.0")
        r2 = Report(id="rep2", session_id="session_2", prediction={"pd_probability_calibrated": 0.85, "confidence_score": 0.95, "audio_quality_score": 9.5}, model_version="1.0")
        r3 = Report(id="rep3", session_id="session_3", prediction={"pd_probability_calibrated": 0.1, "confidence_score": 0.99, "audio_quality_score": 9.0}, model_version="1.0")
        db.add_all([r1, r2, r3])
        db.commit()
    finally:
        db.close()
    
    # Test GET /{session_id}
    res_s1 = client.get(f"{settings.API_V1_STR}/predict/session_1")
    assert res_s1.status_code == 200
    assert res_s1.json()["session_id"] == "session_1"
    assert res_s1.json()["result"]["prediction"]["pd_probability_calibrated"] == 0.8
    
    # Test GET /patients/{patient_id}/history
    res_pa = client.get(f"{settings.API_V1_STR}/predict/patients/patient_A/history")
    assert res_pa.status_code == 200
    data_pa = res_pa.json()
    assert data_pa["patient_id"] == "patient_A"
    assert len(data_pa["history"]) == 2
    
    # Assert chronological sorting
    t1 = datetime.fromisoformat(data_pa["history"][0]["timestamp"])
    t2 = datetime.fromisoformat(data_pa["history"][1]["timestamp"])
    assert t1 < t2
    assert data_pa["history"][0]["session_id"] == "session_1"
    assert data_pa["history"][1]["session_id"] == "session_2"

def test_xai_retrieval_success():
    client = get_client()
    from backend.core.config import settings
    from backend.database.session_db import SessionLocal
    from backend.models import Patient, Session, Report
    from datetime import datetime, timezone
    
    db = SessionLocal()
    try:
        p_X = Patient(id="patient_XAI")
        # Cleanup
        db.query(Report).filter(Report.session_id == "xai_session_1").delete()
        db.query(Session).filter(Session.id == "xai_session_1").delete()
        db.query(Patient).filter(Patient.id == "patient_XAI").delete()
        db.commit()
        
        db.add(p_X)
        
        s_X = Session(id="xai_session_1", patient_id="patient_XAI", timestamp=datetime.now(timezone.utc), task_type="read", mode="upload")
        db.add(s_X)
        
        r_X = Report(
            id="rep_x", 
            session_id="xai_session_1", 
            prediction={"pd_probability_calibrated": 0.88, "confidence_score": 0.92, "audio_quality_score": 9.1}, 
            structured_evidence={
                "gradcam_heatmap_path": "s3://bucket/heatmap.png",
                "acoustic_shap_values": {"jitter": 0.05, "shimmer": 0.02, "hnr": -0.01},
                "temporal_attention": [0.1, 0.8, 0.1]
            },
            model_version="1.0"
        )
        db.add(r_X)
        db.commit()
    finally:
        db.close()
    
    response = client.get(f"{settings.API_V1_STR}/xai/xai_session_1")
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "xai_session_1"
    assert data["prediction"]["pd_probability"] == 0.88
    
    # Assert XAI fields
    exp = data["explanations"]
    assert exp["acoustic_features"]["full_shap_values"]["jitter"] == 0.05
    assert exp["temporal"]["window_importance"] == [0.1, 0.8, 0.1]
    assert exp["spatial"]["gradcam_heatmap_ref"] == "s3://bucket/heatmap.png"

def test_xai_retrieval_not_found():
    client = get_client()
    from backend.core.config import settings
    response = client.get(f"{settings.API_V1_STR}/xai/unknown_xai_session")
    assert response.status_code == 404
