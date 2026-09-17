from pydantic import BaseModel, Field
from typing import Optional, Dict, List

class PredictionScore(BaseModel):
    pd_probability_calibrated: float = Field(..., ge=0.0, le=1.0)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    audio_quality_score: float = Field(..., ge=0.0, le=10.0)

class ExplanationRefs(BaseModel):
    gradcam_heatmap_path: Optional[str] = None
    acoustic_shap_values: Optional[Dict[str, float]] = None
    temporal_attention: Optional[List[float]] = None

class PredictionResponse(BaseModel):
    prediction: PredictionScore
    explanation_refs: ExplanationRefs

from datetime import datetime

class StoredPrediction(BaseModel):
    session_id: str
    patient_id: Optional[str] = None
    timestamp: datetime
    result: PredictionResponse

class PatientHistoryResponse(BaseModel):
    patient_id: str
    history: List[StoredPrediction]
