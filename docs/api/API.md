# REST & WebSocket API Specification

## 1. Overview & Base URL

- **Base URL**: `http://localhost:8000/api/v1`
- **Protocol**: HTTP/1.1 & WebSockets (`ws://`)
- **Authentication**: Bearer Token / Session API Key (configured via reverse proxy headers in production)
- **CORS Allowed Origins**: Configured via `BACKEND_CORS_ORIGINS`

---

## 2. Endpoints Reference

### 2.1 System Health & Monitoring
- **`GET /api/v1/health`**
  - **Description**: Returns application health status, model version, SQL database connectivity, and Chroma vector DB heartbeat.
  - **Response (`200 OK`)**:
    ```json
    {
      "status": "healthy",
      "model_version": "model_v1.0.0",
      "timestamp": "2026-08-23T18:00:00.000Z",
      "services": {
        "database": "connected",
        "vector_db": "connected"
      }
    }
    ```

---

### 2.2 Audio Upload & Inference
- **`POST /api/v1/upload`**
  - **Description**: Uploads an audio file for inference, XAI feature extraction, and optional database persistence.
  - **Content-Type**: `multipart/form-data`
  - **Parameters**:
    - `file` (File, required): Audio recording (`.wav`, `.mp3`, `.m4a`, $\le 25\text{MB}$).
    - `patient_id` (string, optional): Unique patient identifier.
    - `label` (integer, optional): Ground truth label ($0$ or $1$) for research tracking.
  - **Response (`200 OK`)**:
    ```json
    {
      "prediction": {
        "pd_probability_calibrated": 0.784,
        "confidence_score": 0.912,
        "audio_quality_score": 8.95
      },
      "explanation_refs": {
        "gradcam_heatmap_path": "/artifacts/heatmaps/sess_123.png",
        "acoustic_shap_values": { "Micro-Pitch Variation": 0.14 },
        "temporal_attention": [0.2, 0.7, 0.4]
      }
    }
    ```
  - **Error Codes**: `400 Bad Request` (invalid format), `413 Content Too Large` ($>25\text{MB}$).

---

### 2.3 Real-Time Audio Streaming WebSocket
- **`WebSocket /api/v1/stream`**
  - **Description**: Bidirectional stream accepting 16kHz 16-bit mono PCM chunks and returning running prediction updates.
  - **Client Frame**: Binary raw PCM16 bytes ($64,000\text{ bytes} \approx 2.0\text{s}$).
  - **Server Message (`JSON`)**:
    ```json
    {
      "session_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
      "windows_processed": 3,
      "running_prediction": 0.762,
      "last_window_quality": 8.4,
      "status": "accumulating"
    }
    ```

---

### 2.4 Stored Predictions & Patient History
- **`GET /api/v1/predict/{session_id}`**
  - **Description**: Retrieves stored prediction score and explanation references for a session.
  - **Response (`200 OK`)**: `StoredPrediction` schema object.
  - **Error Codes**: `404 Not Found`.

- **`GET /api/v1/predict/patients/{patient_id}/history`**
  - **Description**: Retrieves chronological longitudinal history of all encounters for a patient.
  - **Response (`200 OK`)**:
    ```json
    {
      "patient_id": "PAT-001",
      "history": [
        {
          "session_id": "sess_101",
          "timestamp": "2026-03-01T10:00:00Z",
          "pd_probability_calibrated": 0.38,
          "confidence_score": 0.88,
          "audio_quality_score": 8.5
        }
      ]
    }
    ```

---

### 2.5 Explainability Evidence
- **`GET /api/v1/xai/{session_id}`**
  - **Description**: Returns structured explainability evidence (SHAP acoustic features, Grad-CAM formant anchors, temporal rollout).
  - **Response (`200 OK`)**: `StructuredEvidenceResponse` schema object.

---

### 2.6 Clinical Report Generation
- **`POST /api/v1/report/{session_id}`** & **`GET /api/v1/report/{session_id}`**
  - **Description**: Generates or retrieves an LLM-synthesized clinical screening document validated against strict Pydantic schemas.
  - **Response (`200 OK`)**: `ReportSchema` document or `{ "report": "...", "validated": { ... } }`.
  - **Degraded Response (`500 Internal Server Error`)**: Returns `"Report generation degraded – numeric results only."` when LLM validation constraints fail.
