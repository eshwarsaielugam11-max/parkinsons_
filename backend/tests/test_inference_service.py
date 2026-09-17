import pytest
import os
import importlib
import backend.inference.model_loader as loader
from backend.inference.predictor_service import predict
from backend.schemas.prediction import PredictionResponse

def setup_module(module):
    # Reset singleton state before tests run
    loader._predictor_instance = None
    loader._load_count = 0

def test_singleton_loader_only_loads_once():
    # Force loading multiple times
    p1 = loader.get_predictor()
    p2 = loader.get_predictor()
    p3 = loader.get_predictor()
    
    assert p1 is p2
    assert p2 is p3
    assert loader._load_count == 1, f"Expected load count 1, got {loader._load_count}"

def test_predict_schema_conformance_and_logic():
    # Since Predictor is mocked in local test environment, it returns a static dictionary.
    # We pass a dummy audio file path.
    dummy_audio_path = "dummy.wav"
    
    # First inference
    res1 = predict(dummy_audio_path, return_explanations=False)
    # Second inference with XAI
    res2 = predict(dummy_audio_path, return_explanations=True)
    
    # Assert model loaded only once across the previous test and these calls
    assert loader._load_count == 1
    
    # Assert return types and Pydantic validation passed
    assert isinstance(res1, PredictionResponse)
    assert isinstance(res2, PredictionResponse)
    
    # Assert schema rules logic bounds for prob/confidence/quality
    assert 0.0 <= res1.prediction.pd_probability_calibrated <= 1.0
    assert 0.0 <= res1.prediction.confidence_score <= 1.0
    assert 0.0 <= res1.prediction.audio_quality_score <= 10.0
    
    # Assert XAI fields populated/unpopulated correctly based on return_explanations flag
    assert res1.explanation_refs.gradcam_heatmap_path is None
    assert res2.explanation_refs.gradcam_heatmap_path == "heatmap.png"
    
    assert isinstance(res2.explanation_refs.temporal_attention, list)
    assert isinstance(res2.explanation_refs.acoustic_shap_values, dict)
