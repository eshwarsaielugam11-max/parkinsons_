# System Architecture Design

This document outlines the final project folder tree and the file-by-file responsibility map for the entire Parkinson's Disease Voice Classification system. It serves as the master structural blueprint.

## VIEW A: Final Project Folder Tree

*Note: Notebook numbers have been slightly adjusted to match the actual execution sequence up to Phase 22. The model export version is specifically `model_v1.0.0`.*

```text
project-root/
├── README.md
├── CHANGELOG.md
├── LICENSE
├── .gitignore
├── .env.example
├── docker-compose.yml
├── PROJECT_STATE.md
│
├── docs/
│   ├── architecture/ARCHITECTURE.md
│   ├── model/MODEL_CARD.md
│   ├── model/TRAINING.md
│   ├── model/EVALUATION.md
│   ├── model/XAI.md
│   ├── api/API.md
│   ├── rag/RAG.md
│   ├── rag/LLM.md
│   ├── deployment/DEPLOYMENT.md
│   ├── research/DATASET.md
│   ├── testing/TESTING.md
│   └── SECURITY.md
│
├── model/
│   ├── notebooks/
│   │   ├── 01_environment_check.ipynb
│   │   ├── 02_dataset_audit.ipynb
│   │   ├── 03_preprocessing.ipynb
│   │   ├── 04_acoustic_features.ipynb
│   │   ├── 05_baselines.ipynb
│   │   ├── 06_spectrograms.ipynb
│   │   ├── 07_convnextv2.ipynb
│   │   ├── 08_transformer.ipynb
│   │   ├── 09_asr_branch.ipynb
│   │   ├── 10_fusion.ipynb
│   │   ├── 11_heads.ipynb
│   │   ├── 12_calibration.ipynb
│   │   ├── 13_xai.ipynb
│   │   ├── 15_robustness.ipynb
│   │   └── 16_export.ipynb
│   ├── configs/
│   │   ├── data_config.yaml
│   │   ├── audio_config.yaml
│   │   ├── spectrogram_config.yaml
│   │   ├── model_config.yaml
│   │   ├── training_config.yaml
│   │   └── calibration_config.yaml
│   ├── src/
│   │   ├── preprocessing/{resample.py, vad.py, quality_check.py, normalize.py}
│   │   ├── audio/{augmentation.py}
│   │   ├── spectrograms/{mel.py, stft.py, cqt.py}
│   │   ├── features/{acoustic.py, egemaps.py, asr_features.py}
│   │   ├── models/{convnext_branch.py, projection.py, transformer_encoder.py, fusion.py, heads.py}
│   │   ├── training/{losses.py, dataloaders.py}
│   │   ├── evaluation/{metrics.py, speaker_aggregation.py, subgroup_eval.py}
│   │   ├── calibration/{calibrate.py}
│   │   ├── explainability/{gradcam.py, attention_rollout.py, shap_acoustic.py}
│   │   └── inference/{predictor.py, contract.py}
│   ├── checkpoints/
│   ├── artifacts/
│   ├── exported/
│   │   ├── model_v1.0.0/
│   │   │   ├── weights.pt
│   │   │   ├── model_config.json
│   │   │   ├── preprocessing_config.json
│   │   │   ├── calibration.json
│   │   │   ├── feature_scalers.pkl
│   │   │   ├── label_map.json
│   │   │   └── MODEL_CONTRACT.json
│   └── tests/{test_preprocessing.py, test_features.py, test_model_forward.py, test_leakage.py, test_export_contract.py}
│
├── backend/
│   ├── app/main.py
│   ├── api/{upload.py, stream.py, predict.py, xai.py, report.py, rag.py, similarity.py, health.py}
│   ├── core/{config.py, security.py, logging.py}
│   ├── models/{patient.py, session.py, recording.py, report.py}
│   ├── schemas/{prediction.py, xai.py, report.py, session.py}
│   ├── services/{preprocessing_service.py, feature_service.py}
│   ├── inference/{model_loader.py, predictor_service.py}
│   ├── rag/{retriever.py, prompt_builder.py, llm_client.py, output_validator.py}
│   ├── retrieval/{voice_similarity.py, clinical_evidence.py}
│   ├── database/{session_db.py, migrations/}
│   ├── middleware/{cors.py, error_handler.py, request_id.py}
│   ├── utils/
│   └── tests/{test_api.py, test_inference_service.py, test_rag.py}
│
├── frontend/
│   ├── src/
│   │   ├── components/{Recorder, QualityIndicator, ProbabilityGauge, SpectrogramHeatmap, AttentionTimeline, ShapChart, ReportView, LongitudinalChart}
│   │   ├── pages/{Home, Record, Upload, Result, Report, History}
│   │   ├── layouts/
│   │   ├── hooks/{useMicStream.ts, usePrediction.ts}
│   │   ├── services/api.ts
│   │   ├── state/
│   │   ├── types/
│   │   └── utils/
│   └── tests/
│
├── rag/
│   ├── ingestion/{fetch_sources.py, verify_sources.py}
│   ├── documents/
│   ├── chunking/chunker.py
│   ├── embeddings/embedder.py
│   ├── retrieval/reranker.py
│   ├── prompts/report_prompt_template.md
│   ├── evaluation/rag_eval.py
│   └── schemas/document_metadata.json
│
├── database/
│   ├── schemas/schema.sql
│   ├── migrations/
│   └── seeds/
│
├── scripts/{setup_env.sh, run_backend.sh, run_frontend.sh, sync_model_artifacts.sh}
│
├── deployment/
│   ├── local/docker-compose.local.yml
│   ├── docker/{Dockerfile.backend, Dockerfile.frontend}
│   └── production/
│
└── tests/
    ├── integration/
    ├── end_to_end/
    └── fixtures/
```

## VIEW B: File-by-File Responsibility Map

| File Path | Purpose | Inputs | Outputs | Dependencies | Created In | Modified In | Owner | Test File |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Model / Inference (Phases 1 - 22)** | | | | | | | | |
| `model/src/preprocessing/vad.py` | Silence trim + VAD | raw audio | voiced segments | `audio_config.yaml` | Phase 6 | N/A | Model | `test_preprocessing.py` |
| `model/src/spectrograms/*.py` | 3-view spectrogram generation | preprocessed windows | 3 tensors per window | `spectrogram_config.yaml` | Phase 9 | N/A | Model | N/A |
| `model/src/models/convnext_branch.py` | Per-view ConvNeXt V2 feature extractor | spectrogram tensor | embedding | timm pretrained weights | Phase 10 | N/A | Model | `test_model_forward.py` |
| `model/src/models/transformer_encoder.py`| Temporal modeling | token sequence | pooled representation | Phase 11 tokens | Phase 12 | N/A | Model | `test_model_forward.py` |
| `model/src/models/fusion.py` | Gated multimodal fusion | deep + acoustic + ASR reps| fused representation | Phases 10-13 | Phase 14 | N/A | Model | `test_model_forward.py` |
| `model/src/models/heads.py` | PD/severity/quality/uncertainty | fused representation | prediction dict | Phase 14 | Phase 15 | N/A | Model | `test_model_forward.py` |
| `model/src/evaluation/speaker_aggregation.py` | Window→session→speaker rollup | window predictions | speaker-level metrics | Phase 5 splits | Phase 16 | N/A | Model | N/A |
| `model/src/calibration/calibrate.py` | Probability calibration | val logits | `calibration.json` | Phase 15/16 | Phase 17 | N/A | Model | N/A |
| `model/src/explainability/*.py` | 3 XAI channels | model + inputs | structured evidence JSON | Phases 10,12,7 | Phase 18 | N/A | Model | N/A |
| `model/exported/model_v1.0.0/MODEL_CONTRACT.json`| Formal I/O contract | None | Backend contract schema | Phase 22 | N/A | Model | `test_export_contract.py`|
| `model/src/inference/predictor.py` | Standalone Python Predictor | raw audio | dict | Preprocessing, models | Phase 22 | N/A | Model | `test_export_contract.py`|
| **Backend Core & Architecture (Phases 25 - 28)** | | | | | | | | |
| `backend/app/main.py` | FastAPI App entrypoint | config, routes | REST API app | `backend/core/` | Phase 25 | Phase 31 | Backend | `test_api.py` |
| `backend/core/config.py` | App configuration loading | `.env` variables | Settings object | none | Phase 25 | N/A | Backend | N/A |
| `backend/core/security.py` | Auth and security headers | HTTP request | HTTP responses | FastAPI | Phase 25 | N/A | Backend | `test_api.py` |
| `backend/core/logging.py` | Structured logging | logs | log stream | `logging` | Phase 25 | N/A | Backend | N/A |
| `backend/middleware/cors.py` | CORS policy | request | response | FastAPI | Phase 25 | N/A | Backend | N/A |
| `backend/middleware/error_handler.py`| Global exception handling | Exception | JSON Response | FastAPI | Phase 25 | N/A | Backend | `test_api.py` |
| `backend/middleware/request_id.py` | Request tracing | request | response header | uuid | Phase 25 | N/A | Backend | N/A |
| `backend/database/session_db.py` | DB connection pool | connection string | SessionMaker | SQLAlchemy | Phase 26 | N/A | DB | N/A |
| `backend/database/migrations/` | Alembic schemas | ORM models | DB schema | SQLAlchemy | Phase 26 | N/A | DB | N/A |
| `backend/models/*.py` | ORM SQL entities | DB Session | DB Row | SQLAlchemy | Phase 26 | N/A | DB | N/A |
| `backend/schemas/*.py` | API Pydantic schemas | JSON requests | validated objects| Pydantic | Phase 27 | Phase 29 | Backend | N/A |
| `backend/inference/model_loader.py` | Loads exported model payload | `MODEL_VERSION` | `Predictor` class | `MODEL_CONTRACT.json` | Phase 27 | N/A | Backend | `test_inference_service.py`|
| `backend/inference/predictor_service.py`| Service orchestrator | audio bytes | schema payload | `model_loader.py` | Phase 28 | N/A | Backend | `test_inference_service.py`|
| `backend/services/preprocessing_service.py`| Audio ingestion logic | raw audio bytes| sanitized audio bytes | Audio config | Phase 28 | N/A | Backend | N/A |
| `backend/services/feature_service.py`| Extraction cache/db wrapper | preprocessed | DB features | `predictor_service` | Phase 28 | N/A | Backend | N/A |
| **Backend API (Phases 29 - 31)** | | | | | | | | |
| `backend/api/upload.py` | REST Upload Endpoint | POST wav | 200 JSON | `predictor_service` | Phase 29 | N/A | Backend | `test_api.py` |
| `backend/api/stream.py` | WebSocket streaming inference | WebSocket Chunks | WS Events | `predictor_service` | Phase 29 | N/A | Backend | `test_api.py` |
| `backend/api/predict.py` | REST batch predict | Audio Payload | prediction JSON | `predictor_service` | Phase 29 | N/A | Backend | `test_api.py` |
| `backend/api/health.py` | API Healthcheck | GET | 200 JSON | none | Phase 29 | N/A | Backend | `test_api.py` |
| `backend/api/xai.py` | Fetch Explainability artifacts | session_id | image/JSON | DB | Phase 30 | N/A | Backend | `test_api.py` |
| `backend/retrieval/voice_similarity.py`| Vector search on embeddings | acoustic feats | similar patients | Vector DB | Phase 31 | N/A | Backend | N/A |
| `backend/api/similarity.py` | Expose voice similarity | session_id | patient list JSON | `voice_similarity` | Phase 31 | N/A | Backend | `test_api.py` |
| **RAG Ingestion (Phases 32 - 34)** | | | | | | | | |
| `rag/schemas/document_metadata.json`| Schema for RAG metadata | n/a | JSON schema | none | Phase 32 | N/A | RAG | N/A |
| `rag/ingestion/fetch_sources.py` | Download clinical PDFs | URIs | PDF files | none | Phase 33 | N/A | RAG | N/A |
| `rag/ingestion/verify_sources.py` | Validates hash/integrity | PDF files | Logs | none | Phase 33 | N/A | RAG | N/A |
| `rag/chunking/chunker.py` | Text splitting | text | text chunks | Langchain | Phase 34 | N/A | RAG | N/A |
| `rag/embeddings/embedder.py` | Text embeddings | text chunks | Vector arrays | SentenceTransformers | Phase 34 | N/A | RAG | N/A |
| **RAG Retrieval & Reporting (Phases 35 - 38)** | | | | | | | | |
| `rag/retrieval/reranker.py` | Cross-encoder reranking | initial vectors | reranked docs | CrossEncoder | Phase 35 | N/A | RAG | N/A |
| `rag/prompts/report_prompt_template.md`| System Prompt | Variables | Prompt String | none | Phase 36 | N/A | RAG | N/A |
| `backend/rag/retriever.py` | Clinical evidence retrieval | query context | ranked chunks | `reranker.py` | Phase 36 | N/A | RAG | `test_rag.py` |
| `backend/rag/llm_client.py` | Calls LLM for report text | struct evidence | draft report | `report_prompt` | Phase 37 | N/A | RAG | `test_rag.py` |
| `backend/rag/output_validator.py` | Rejects hallucinatory LLM text | LLM draft | validated report | Validation heuristics| Phase 38 | N/A | RAG | `test_rag.py` |
| `backend/api/report.py` | REST Report Endpoint | session_id | Markdown text | `output_validator` | Phase 38 | N/A | Backend | `test_api.py` |
| `backend/api/rag.py` | General RAG Query API | Text query | RAG response | `llm_client` | Phase 38 | N/A | Backend | `test_api.py` |
| `rag/evaluation/rag_eval.py` | Ground-truth testing | queries | ROUGE/BLEU | datasets | Phase 38 | N/A | RAG | N/A |
| **Frontend Core (Phases 39 - 41)** | | | | | | | | |
| `frontend/src/types/` | TS Interfaces | `MODEL_CONTRACT.json`| TS Types | none | Phase 39 | Phase 42 | Frontend | N/A |
| `frontend/src/state/` | Global application state | User actions | State object | Redux/Zustand | Phase 39 | Phase 46 | Frontend | N/A |
| `frontend/src/services/api.ts` | Axios client for backend | JSON payload | TS promises | Axios | Phase 40 | Phase 46 | Frontend | N/A |
| `frontend/src/hooks/useMicStream.ts` | Mic capture + WebSocket | MediaStream | WS audio frames| Backend Phase 29 | Phase 41 | N/A | Frontend | N/A |
| `frontend/src/hooks/usePrediction.ts`| REST Predict Wrapper | Audio Blob | `PredictionOut` | `api.ts` | Phase 41 | N/A | Frontend | N/A |
| **Frontend Visualization (Phases 42 - 45)** | | | | | | | | |
| `frontend/src/components/QualityIndicator`| Audio SNR bar | WS quality score | UI Element | `useMicStream` | Phase 42 | N/A | Frontend | N/A |
| `frontend/src/components/ProbabilityGauge`| Circular PD likelihood | `pd_probability` | UI Element | none | Phase 43 | N/A | Frontend | N/A |
| `frontend/src/components/SpectrogramHeatmap`| Renders Grad-CAM overlay | XAI API image | UI Element | Backend Phase 30 | Phase 44 | N/A | Frontend | N/A |
| `frontend/src/components/AttentionTimeline`| Temporal attention bar | XAI timeline | UI Element | Backend Phase 30 | Phase 44 | N/A | Frontend | N/A |
| `frontend/src/components/ShapChart` | Acoustic SHAP values | SHAP JSON | D3 Bar Chart | Backend Phase 30 | Phase 45 | N/A | Frontend | N/A |
| `frontend/src/components/ReportView` | Renders Markdown report | API JSON | React Markdown | Backend Phase 38 | Phase 45 | N/A | Frontend | N/A |
| `frontend/src/components/LongitudinalChart`| Historic progression | API History | Line Chart | none | Phase 45 | N/A | Frontend | N/A |
| `frontend/src/components/Recorder` | Generic record button | UI clicks | Audio Blob | none | Phase 45 | N/A | Frontend | N/A |
| **Frontend Routing & Pages (Phases 46 - 48)** | | | | | | | | |
| `frontend/src/layouts/` | Navbars & Footers | Router | DOM Structure | none | Phase 46 | N/A | Frontend | N/A |
| `frontend/src/pages/Home` | Landing Page | User | UI | none | Phase 46 | N/A | Frontend | N/A |
| `frontend/src/pages/Record` | Live Streaming Page | User | UI | `useMicStream` | Phase 47 | N/A | Frontend | N/A |
| `frontend/src/pages/Upload` | Static Upload Page | User | UI | `usePrediction` | Phase 47 | N/A | Frontend | N/A |
| `frontend/src/pages/Result` | Dashboard (Gauges/Heatmaps)| Session ID | UI | Vis Components | Phase 48 | N/A | Frontend | N/A |
| `frontend/src/pages/Report` | Clinical Report view | Session ID | UI | `ReportView` | Phase 48 | N/A | Frontend | N/A |
| `frontend/src/pages/History`| History list/longitudinal | User ID | UI | API | Phase 48 | N/A | Frontend | N/A |
| **Database & Deployment (Phases 49 - 54)** | | | | | | | | |
| `database/schemas/schema.sql` | Postgres init script | none | Tables | DB Engine | Phase 49 | N/A | DevOps | N/A |
| `database/migrations/` | Alembic/Flyway | DB scripts | Migrated DB | `schema.sql` | Phase 49 | N/A | DevOps | N/A |
| `database/seeds/` | Mock patient data | JSON | Populated DB | none | Phase 49 | N/A | DevOps | N/A |
| `deployment/local/docker-compose.local.yml`| Local Dev Environment | Images | Running Stack | Docker | Phase 50 | N/A | DevOps | N/A |
| `deployment/docker/Dockerfile.backend` | Backend Image | Repo | Image | `backend/` | Phase 50 | N/A | DevOps | N/A |
| `deployment/docker/Dockerfile.frontend`| Frontend Image | Repo | Image | `frontend/` | Phase 50 | N/A | DevOps | N/A |
| `deployment/production/` | K8s YAMLs / Helm | Configs | Cluster | K8s | Phase 51 | N/A | DevOps | N/A |
| `scripts/setup_env.sh` | Local bootstrap script | .env template | .env config | none | Phase 52 | N/A | DevOps | N/A |
| `scripts/run_backend.sh` | Uvicorn launch script | Repo | Running Server | Backend | Phase 52 | N/A | DevOps | N/A |
| `scripts/run_frontend.sh` | Npm start script | Repo | Running Webapp | Frontend | Phase 52 | N/A | DevOps | N/A |
| `tests/integration/` | End-to-end API logic | HTTP reqs | Pass/Fail | Backend API | Phase 53 | N/A | QA | N/A |
| `tests/end_to_end/` | Playwright/Cypress UI | Browser | Pass/Fail | Webapp | Phase 53 | N/A | QA | N/A |
| `tests/fixtures/` | Mock audio/DB payloads | test reqs | data | none | Phase 54 | N/A | QA | N/A |
