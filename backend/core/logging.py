import json
import logging
import time
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Optional, Dict, Any

# ContextVar for request-level correlation ID
request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)

def set_current_request_id(req_id: Optional[str]):
    request_id_ctx.set(req_id)

def get_current_request_id() -> Optional[str]:
    return request_id_ctx.get()

# Audio privacy filter to intercept and strip raw binary/audio payload leaks
class AudioPrivacyFilter(logging.Filter):
    """
    Ensures raw audio data (byte buffers, base64 audio strings, RIFF headers)
    are strictly suppressed and never written into persistent logs.
    """
    SENSITIVE_AUDIO_SIGNATURES = [
        "RIFF", "WAVE", "data:audio", "audio/wav;base64", "audio/mpeg;base64"
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            for sig in self.SENSITIVE_AUDIO_SIGNATURES:
                if sig in record.msg:
                    record.msg = f"[AUDIO_DATA_REDACTED_FOR_PRIVACY: {sig} signature detected]"
        elif isinstance(record.msg, bytes):
            record.msg = f"[BINARY_AUDIO_BYTES_REDACTED ({len(record.msg)} bytes)]"
        return True


class StructuredJsonFormatter(logging.Formatter):
    """
    Formats log records into machine-readable JSON objects with
    correlated request ID, ISO8601 timestamp, logger name, and metadata.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "request_id": get_current_request_id(),
            "message": record.getMessage(),
        }

        # Attach custom structured attributes if provided via extra
        if hasattr(record, "structured_data") and isinstance(record.structured_data, dict):
            log_entry.update(record.structured_data)

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def setup_structured_logging(level: int = logging.INFO):
    """Initializes root and app loggers with structured JSON formatting and privacy filters."""
    root_logger = logging.getLogger()
    
    # Remove default plain handlers if re-initializing
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler()
    handler.setFormatter(StructuredJsonFormatter())
    handler.addFilter(AudioPrivacyFilter())
    root_logger.addHandler(handler)
    root_logger.setLevel(level)


# Specialized Structured Event Loggers
app_logger = logging.getLogger("pd_voice.app")
inference_logger = logging.getLogger("pd_voice.inference")
rag_logger = logging.getLogger("pd_voice.rag")

def log_inference_metrics(
    session_id: str,
    model_version: str,
    latency_ms: float,
    audio_quality_score: float,
    calibrated_prob: float,
    confidence: float,
    timing_breakdown: Optional[Dict[str, float]] = None,
):
    """Structured inference log (NEVER logs raw audio bytes or local file paths)."""
    inference_logger.info(
        f"Inference completed for session {session_id}",
        extra={
            "structured_data": {
                "event_type": "INFERENCE_METRICS",
                "session_id": session_id,
                "model_version": model_version,
                "total_inference_latency_ms": round(latency_ms, 2),
                "audio_quality_score": round(audio_quality_score, 2),
                "calibrated_probability": round(calibrated_prob, 4),
                "confidence_score": round(confidence, 4),
                "timing_breakdown": timing_breakdown or {},
            }
        }
    )

def log_rag_retrieval(
    session_id: str,
    query_text: str,
    latency_ms: float,
    chunks_retrieved: int,
):
    """Structured RAG retrieval diagnostic log."""
    rag_logger.info(
        f"RAG retrieval completed for session {session_id}",
        extra={
            "structured_data": {
                "event_type": "RAG_RETRIEVAL",
                "session_id": session_id,
                "retrieval_latency_ms": round(latency_ms, 2),
                "chunks_count": chunks_retrieved,
                "query_preview": query_text[:80] if query_text else "",
            }
        }
    )

def log_llm_report_metrics(
    session_id: str,
    model: str,
    latency_ms: float,
    validation_status: str,
    retry_count: int = 0,
):
    """Structured LLM report generation and validation metrics."""
    rag_logger.info(
        f"Clinical report generation completed for session {session_id} (status: {validation_status})",
        extra={
            "structured_data": {
                "event_type": "LLM_REPORT_METRICS",
                "session_id": session_id,
                "llm_model": model,
                "generation_latency_ms": round(latency_ms, 2),
                "validation_status": validation_status,
                "retry_count": retry_count,
            }
        }
    )
