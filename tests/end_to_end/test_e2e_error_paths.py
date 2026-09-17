import os
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.app.main import app

FIXTURES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../fixtures"))

@pytest.fixture
def client():
    return TestClient(app)

def test_rejected_quality_audio_path(client):
    """
    E2E Error Path 1: Silent / Suboptimal Audio Quality
    - Uploads silent audio fixture
    - Asserts that audio quality assessment flags the signal
    """
    silent_path = os.path.join(FIXTURES_DIR, "silent_rejected.wav")
    assert os.path.exists(silent_path)

    with open(silent_path, "rb") as f:
        file_bytes = f.read()

    res = client.post(
        "/api/v1/upload",
        files={"file": ("silent_rejected.wav", file_bytes, "audio/wav")},
        data={"patient_id": "patient_silent_001"},
    )
    assert res.status_code == 200
    pred = res.json()["prediction"]
    # Silent audio should receive lower audio quality score
    assert "audio_quality_score" in pred
    assert pred["audio_quality_score"] <= 10.0

def test_oversized_audio_upload_rejection(client):
    """
    E2E Error Path 2: Upload exceeding 25MB limit
    - Attempts upload with payload > 25MB
    - Asserts HTTP 413 Content Too Large
    """
    # Create 26MB dummy byte stream
    oversized_bytes = b"0" * (26 * 1024 * 1024)
    res = client.post(
        "/api/v1/upload",
        files={"file": ("large_file.wav", oversized_bytes, "audio/wav")},
    )
    assert res.status_code == 413
    assert "exceeds maximum size" in res.text

def test_unsupported_audio_format_rejection(client):
    """
    E2E Error Path 3: Unsupported MIME / Content Type
    - Attempts upload with text/plain or application/octet-stream
    - Asserts HTTP 400 Bad Request
    """
    res = client.post(
        "/api/v1/upload",
        files={"file": ("script.sh", b"#!/bin/bash\necho hello", "text/plain")},
    )
    assert res.status_code == 400
    assert "Unsupported file type" in res.text

def test_nonexistent_session_queries(client):
    """
    E2E Error Path 4: Nonexistent Session IDs
    - Queries /predict/{session_id}, /xai/{session_id}, /report/{session_id} for unknown session
    - Asserts clean HTTP 404 Not Found
    """
    fake_session = "sess_nonexistent_0000"

    res_pred = client.get(f"/api/v1/predict/{fake_session}")
    assert res_pred.status_code == 404

    res_xai = client.get(f"/api/v1/xai/{fake_session}")
    assert res_xai.status_code == 404

    res_rep = client.get(f"/api/v1/report/{fake_session}")
    assert res_rep.status_code == 404

def test_report_degraded_fallback_on_validator_failure(client):
    """
    E2E Error Path 5: Report Validator Failure & Degraded Fallback
    - Seeds a valid prediction session
    - Simulates LLM generating corrupted/unparseable report text
    - Asserts backend returns clean HTTP 500 with 'Report generation degraded'
    """
    clean_path = os.path.join(FIXTURES_DIR, "clean_sample.wav")
    with open(clean_path, "rb") as f:
        file_bytes = f.read()

    upload_res = client.post(
        "/api/v1/upload",
        files={"file": ("clean.wav", file_bytes, "audio/wav")},
        data={"patient_id": "patient_degraded_test"},
    )
    assert upload_res.status_code == 200

    # Retrieve created session_id
    history_res = client.get("/api/v1/predict/patients/patient_degraded_test/history")
    session_id = history_res.json()["history"][-1]["session_id"]

    # Mock LLM to return invalid hallucinated text that fails validation
    with patch("backend.api.report.generate_report", return_value="INVALID UNFORMATTED OUTPUT"):
        res = client.post(f"/api/v1/report/{session_id}")
        assert res.status_code == 500
        assert "Report generation degraded – numeric results only" in res.text
