from fastapi.testclient import TestClient
from backend.app.main import app
import backend.api.predict as predict_api
from backend.schemas.prediction import StoredPrediction, PredictionResponse, PredictionScore, ExplanationRefs
from datetime import datetime, timezone
import json

client = TestClient(app)

rec = StoredPrediction(
    session_id="xai_manual_test_123",
    patient_id="patient_xyz",
    timestamp=datetime.now(timezone.utc),
    result=PredictionResponse(
        prediction=PredictionScore(pd_probability_calibrated=0.88, confidence_score=0.92, audio_quality_score=9.1),
        explanation_refs=ExplanationRefs(
            gradcam_heatmap_path="s3://bucket/test.png",
            acoustic_shap_values={"jitter": 0.05, "shimmer": 0.02, "hnr": -0.01},
            temporal_attention=[0.1, 0.8, 0.1]
        )
    )
)
predict_api._seed_prediction(rec)

res = client.get("/api/v1/xai/xai_manual_test_123")
print("GET /xai/xai_manual_test_123:", res.status_code)
print(json.dumps(res.json(), indent=2))
