from pydantic import BaseModel
from typing import Dict, List, Optional

class XAIPredictionContext(BaseModel):
    pd_probability: float
    confidence: float
    audio_quality_score: float

class TopContributor(BaseModel):
    feature: str
    shap_value: float

class AcousticFeaturesXAI(BaseModel):
    base_value: float
    top_contributors: List[TopContributor]
    full_shap_values: Dict[str, float]

class TemporalXAI(BaseModel):
    window_importance: List[float]
    key_windows: List[int]

class SpatialXAI(BaseModel):
    gradcam_heatmap_ref: Optional[str]

class Explanations(BaseModel):
    acoustic_features: AcousticFeaturesXAI
    temporal: TemporalXAI
    spatial: SpatialXAI

class StructuredEvidenceResponse(BaseModel):
    session_id: str
    prediction: XAIPredictionContext
    explanations: Explanations
