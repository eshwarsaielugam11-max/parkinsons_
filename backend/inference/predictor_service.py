import time
import uuid
from backend.inference.model_loader import get_predictor
from backend.schemas.prediction import PredictionResponse
from backend.core.config import settings
from backend.core.logging import log_inference_metrics

def predict(audio_bytes_or_path, return_explanations: bool = False, session_id: str = None) -> PredictionResponse:
    """
    Wraps the underlying ML Predictor service, validating input/output through
    our strict Pydantic schema to ensure CONTRACT compliance at the API edge.
    Times the inference cycle and emits privacy-safe observability logs.
    """
    start_time = time.perf_counter()
    predictor = get_predictor()
    
    result_dict = predictor.predict(audio_bytes_or_path, return_explanations=return_explanations)
    latency_ms = (time.perf_counter() - start_time) * 1000.0

    pred_res = PredictionResponse(**result_dict)
    
    # Emit privacy-safe structured inference log
    sid = session_id or str(uuid.uuid4())
    log_inference_metrics(
        session_id=sid,
        model_version=settings.MODEL_VERSION,
        latency_ms=latency_ms,
        audio_quality_score=pred_res.prediction.audio_quality_score,
        calibrated_prob=pred_res.prediction.pd_probability_calibrated,
        confidence=pred_res.prediction.confidence_score,
        timing_breakdown={"inference_total_ms": round(latency_ms, 2)}
    )

    return pred_res

def predict_with_embedding(audio_bytes_or_path, return_explanations: bool = False, session_id: str = None):
    """
    Internal use only: returns both the strictly validated PredictionResponse 
    and the deep representation embedding for Phase 34 vector similarity indexing.
    """
    start_time = time.perf_counter()
    predictor = get_predictor()
    
    result_dict = predictor.predict(audio_bytes_or_path, return_explanations=return_explanations)
    latency_ms = (time.perf_counter() - start_time) * 1000.0

    embedding = result_dict.get("_internal_embedding", [])
    pred_res = PredictionResponse(**result_dict)

    sid = session_id or str(uuid.uuid4())
    log_inference_metrics(
        session_id=sid,
        model_version=settings.MODEL_VERSION,
        latency_ms=latency_ms,
        audio_quality_score=pred_res.prediction.audio_quality_score,
        calibrated_prob=pred_res.prediction.pd_probability_calibrated,
        confidence=pred_res.prediction.confidence_score,
        timing_breakdown={"inference_total_ms": round(latency_ms, 2)}
    )

    return pred_res, embedding
