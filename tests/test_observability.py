import os
import json
import logging
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.core.logging import (
    AudioPrivacyFilter,
    StructuredJsonFormatter,
    log_inference_metrics,
    log_rag_retrieval,
    log_llm_report_metrics,
)

FIXTURES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures"))

@pytest.fixture
def client():
    return TestClient(app)

def test_extended_health_endpoint(client):
    """Assert extended /health endpoint reports model version, DB, and Vector DB connectivity."""
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["healthy", "ok", "degraded"]
    assert "model_version" in data
    assert "services" in data
    assert data["services"]["database"] == "connected"
    assert data["services"]["vector_db"] == "connected"

def test_request_id_correlation_and_latency_header(client):
    """Assert incoming requests receive X-Request-ID header correlation."""
    custom_req_id = "req-test-trace-9912"
    res = client.get("/api/v1/health", headers={"X-Request-ID": custom_req_id})
    assert res.status_code == 200
    assert res.headers.get("X-Request-ID") == custom_req_id

def test_audio_privacy_filter_redaction():
    """Assert AudioPrivacyFilter suppresses raw audio binary buffers and base64 strings."""
    privacy_filter = AudioPrivacyFilter()

    # 1. Binary audio record
    raw_bytes = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00"
    record1 = logging.LogRecord("test", logging.INFO, "", 0, raw_bytes, (), None)
    privacy_filter.filter(record1)
    assert "[BINARY_AUDIO_BYTES_REDACTED" in record1.msg
    assert "RIFF" not in record1.msg

    # 2. Text containing base64 audio header
    text_with_audio = "Here is data:audio/wav;base64,UklGRiQAAABXQVZFZ..."
    record2 = logging.LogRecord("test", logging.INFO, "", 0, text_with_audio, (), None)
    privacy_filter.filter(record2)
    assert "[AUDIO_DATA_REDACTED_FOR_PRIVACY" in record2.msg
    assert "UklGRi" not in record2.msg

def test_inference_observability_no_raw_audio_leakage(client, caplog):
    """
    Assert that executing an inference flow emits structured metrics
    and DOES NOT leak raw audio byte buffers or raw audio arrays.
    """
    clean_path = os.path.join(FIXTURES_DIR, "clean_sample.wav")
    assert os.path.exists(clean_path)

    with open(clean_path, "rb") as f:
        file_bytes = f.read()

    with caplog.at_level(logging.INFO):
        res = client.post(
            "/api/v1/upload",
            files={"file": ("clean_sample.wav", file_bytes, "audio/wav")},
            data={"patient_id": "pat_obs_001"},
            headers={"X-Request-ID": "obs-trace-session-1234"},
        )
        assert res.status_code == 200

    # Inspect all captured logs
    all_log_text = " ".join(rec.getMessage() for rec in caplog.records)

    # 1. Confirm absence of raw audio signatures
    assert "RIFF" not in all_log_text
    assert "WAVEfmt" not in all_log_text
    assert "data:audio" not in all_log_text

    # 2. Confirm presence of structured inference metrics
    inference_records = [
        rec for rec in caplog.records
        if hasattr(rec, "structured_data") and rec.structured_data.get("event_type") == "INFERENCE_METRICS"
    ]
    assert len(inference_records) >= 1
    metrics = inference_records[0].structured_data
    assert "total_inference_latency_ms" in metrics
    assert "model_version" in metrics
    assert "audio_quality_score" in metrics
    assert "calibrated_probability" in metrics
    assert metrics["audio_quality_score"] >= 0.0

def test_structured_json_formatter():
    """Assert StructuredJsonFormatter produces valid JSON with required observability schema."""
    formatter = StructuredJsonFormatter()
    record = logging.LogRecord("pd_voice.test", logging.INFO, "", 0, "Test diagnostic message", (), None)
    record.structured_data = {"event_type": "UNIT_TEST", "latency_ms": 12.34}

    json_output = formatter.format(record)
    parsed = json.loads(json_output)

    assert parsed["level"] == "INFO"
    assert parsed["logger"] == "pd_voice.test"
    assert parsed["message"] == "Test diagnostic message"
    assert parsed["event_type"] == "UNIT_TEST"
    assert parsed["latency_ms"] == 12.34
    assert "timestamp" in parsed
