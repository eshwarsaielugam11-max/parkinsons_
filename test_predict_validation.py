from fastapi.testclient import TestClient
from backend.app.main import app
import backend.api.predict as predict_api
from backend.schemas.prediction import StoredPrediction, PredictionResponse, PredictionScore, ExplanationRefs
from datetime import datetime, timezone
import json

client = TestClient(app)

# Seed
rec = StoredPrediction(
    session_id="manual_test_session_999",
    patient_id="patient_xyz",
    timestamp=datetime.now(timezone.utc),
    result=PredictionResponse(
        prediction=PredictionScore(pd_probability_calibrated=0.88, confidence_score=0.92, audio_quality_score=9.1),
        explanation_refs=ExplanationRefs(gradcam_heatmap_path="s3://bucket/test.png")
    )
)
predict_api._seed_prediction(rec)

# Retrieve
res = client.get("/api/v1/predict/manual_test_session_999")
print("GET /manual_test_session_999:", res.status_code)
print(json.dumps(res.json(), indent=2))

res_hist = client.get("/api/v1/predict/patients/patient_xyz/history")
print("GET history:", res_hist.status_code)
print(json.dumps(res_hist.json(), indent=2))
