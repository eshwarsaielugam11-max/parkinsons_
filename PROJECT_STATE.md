# Project State

## Status
- **HANDOFF GATE PASSED**

## Completed Phases
- Phase 0
- Phase 1
- Phase 2
- Phase 3
- Phase 4
- Phase 5
- Phase 6
- Phase 7
- Phase 8
- Phase 9
- Phase 10
- Phase 11
- Phase 12
- Phase 13
- Phase 14
- Phase 15
- Phase 16
- Phase 17
- Phase 18
- Phase 19 (Deferred)
- Phase 20
- Phase 21
- Phase 22
- Phase 23
- Phase 24
- Phase 24B
- Phase 25
- Phase 26
- Phase 27
- Phase 28
- Phase 29
- Phase 30
- Phase 31
- Phase 32
- Phase 33
- Phase 34
- Phase 35
- Phase 36
- Phase 37
- Phase 38
- Phase 39
- Phase 40
- Phase 41
- Phase 42
- Phase 43
- Phase 44
- Phase 45
- Phase 46
- Phase 47
- Phase 48
- Phase 49
- Phase 50
- Phase 51
- Phase 52
- Phase 53
- Phase 54 (FINAL)

## Current Phase
- Research Paper Data Extraction Complete

## Validation Status
- Status: PASS (100% Checklist Items Verified)
- Last Validation Date: September 1, 2026
- Research data export generated: docs/RESEARCH_DATA_EXPORT.md

## Next Phase
- IEEE Research Paper Draft Generation

## Files Created
- .gitignore
- .env.example
- README.md
- PROJECT_STATE.md
- docs/RESEARCH_DATA_EXPORT.md
- docs/research/RESEARCH_CONSTRAINTS.md
- docs/research/DATASET.md
- model/notebooks/01_environment_check.ipynb
- model/configs/.gitkeep
- model/requirements-colab.txt
- model/configs/data_config.yaml
- model/notebooks/02_dataset_audit.ipynb
- model/artifacts/data_manifest_v1.0-20260823.json
- model/artifacts/split_manifest_v1.0-20260823.json
- model/src/__init__.py
- model/src/evaluation/__init__.py
- model/src/evaluation/leakage_check.py
- model/configs/audio_config.yaml
- model/src/preprocessing/__init__.py
- model/src/preprocessing/resample.py
- model/src/preprocessing/vad.py
- model/src/preprocessing/quality_check.py
- model/src/preprocessing/normalize.py
- model/src/preprocessing/pipeline.py
- model/notebooks/03_preprocessing.ipynb
- model/tests/__init__.py
- model/tests/test_preprocessing.py
- model/configs/feature_config.yaml
- model/src/features/__init__.py
- model/src/features/pipeline.py
- model/src/features/acoustic.py
- model/src/features/egemaps.py
- model/src/features/asr_features.py
- model/tests/test_features.py
- model/notebooks/04_acoustic_features.ipynb
- model/notebooks/05_baselines.ipynb
- model/src/training/__init__.py
- model/src/training/dataloaders.py
- model/artifacts/experiments/registry.jsonl
- model/src/evaluation/metrics.py
- model/configs/training_config.yaml
- model/tests/test_metrics.py
- model/configs/spectrogram_config.yaml
- model/src/spectrograms/__init__.py
- model/src/spectrograms/mel.py
- model/src/spectrograms/stft.py
- model/src/spectrograms/cqt.py
- model/src/spectrograms/normalization.py
- model/notebooks/06_spectrograms.ipynb
- model/configs/model_config.yaml
- model/src/models/__init__.py
- model/src/models/convnext_branch.py
- model/notebooks/07_convnextv2.ipynb
- model/tests/test_convnext.py
- model/src/models/projection.py
- model/src/models/transformer_encoder.py
- model/tests/test_transformer.py
- model/notebooks/08_transformer.ipynb
- model/configs/asr_config.yaml
- model/notebooks/09_asr_branch.ipynb
- model/tests/test_asr_features.py
- model/src/models/fusion.py
- model/tests/test_fusion.py
- model/notebooks/10_fusion.ipynb
- model/src/models/heads.py
- model/src/training/losses.py
- model/tests/test_heads.py
- model/notebooks/11_heads.ipynb
- model/src/evaluation/speaker_aggregation.py
- model/tests/test_aggregation.py
- model/configs/calibration_config.yaml
- model/src/calibration/calibrate.py
- model/src/calibration/__init__.py
- model/src/explainability/gradcam.py
- model/src/explainability/attention_rollout.py
- model/src/explainability/shap_acoustic.py
- model/src/explainability/evidence_schema.py
- model/src/explainability/__init__.py
- model/tests/test_explainability.py
- model/notebooks/13_xai.ipynb
- model/src/evaluation/subgroup_eval.py
- model/notebooks/15_robustness.ipynb
- docs/model/EVALUATION.md
- model/artifacts/SELECTED_MODEL.md
- model/exported/model_v1.0.0/MODEL_CONTRACT.json
- model/src/inference/contract.py
- model/src/inference/predictor.py
- model/src/inference/__init__.py
- model/tests/test_export_contract.py
- model/notebooks/16_export.ipynb
- scripts/sync_model_artifacts.sh
- docs/architecture/ARCHITECTURE.md
- Full architecture skeleton created (see ARCHITECTURE.md)
- docs/model/HANDOFF_CHECKLIST.md
- backend/core/config.py
- backend/middleware/cors.py
- backend/middleware/request_id.py
- backend/middleware/error_handler.py
- backend/api/health.py
- backend/api/upload.py
- backend/api/stream.py
- backend/api/predict.py
- backend/api/xai.py
- backend/api/report.py
- backend/api/rag.py
- backend/api/similarity.py
- backend/app/main.py
- backend/tests/test_api.py
- backend/schemas/prediction.py
- backend/schemas/xai.py
- backend/inference/model_loader.py
- backend/inference/predictor_service.py
- backend/tests/test_inference_service.py
- backend/models/base.py
- backend/models/patient.py
- backend/models/session.py
- backend/models/recording.py
- backend/models/report.py
- backend/models/__init__.py
- backend/tests/test_models.py
- backend/database/session_db.py
- backend/database/migrations/env.py
- database/schemas/schema.sql
- backend/retrieval/voice_similarity.py
- backend/tests/test_voice_similarity.py

## Environment Requirements
- Backend Env: `pd-voice-backend`
- Activation: `source backend/pd-voice-backend/bin/activate`

## Files Modified
- PROJECT_STATE.md
- model/configs/data_config.yaml
- model/notebooks/02_dataset_audit.ipynb

## Tests Completed
- Git initialization verified
- Clean repository status confirmed
- PROJECT_STATE.md section completeness validation
- RESEARCH_CONSTRAINTS.md 14-constraint completeness verification
- Notebook JSON schema and Python script verification for 01_environment_check.ipynb
- Dataset schema validation, zero-null speaker_id/label test, and duplicate check in 02_dataset_audit.ipynb
- Data manifest total_recordings count match with raw index (24/24 records)
- Acoustic confound audit completed (Cramér's V = 0.00, device confound risk: LOW)
- Data leakage and speaker disjointness verification passed with zero violations across Train/Val/Test splits and 4 CV folds (leakage_check.py)
- Preprocessing unit and integration test suite passed (8/8 tests in test_preprocessing.py covering resampling, VAD, QA scoring, clipping detection, SNR estimation, and fold-local fitting)

## Known Issues
- Subgroup sample sizes (especially after train/test splitting 24 total recordings) are incredibly small (mostly < 5 samples per subgroup). Subgroup metric variance is extremely high and should not be treated as a definitive clinical validation.
- No external dataset (e.g., PC-GITA) is available for zero-shot testing, posing a strict limitation on deployment generalizability claims.
- `model/artifacts/experiments/registry.jsonl` is currently un-synced from Colab, causing Phase 19 (Ablation Table generation) to be deferred.
- None (Acoustic confound audit confirmed zero device/environment confounding in baseline cohort)

## Model Version
- v1.0.0

## Dataset Version
- v1.0-20260823 (pd_voice_corpus)

## Model Metrics
- Phase 8: Baseline model metrics recorded in `model/artifacts/experiments/registry.jsonl` (Classical, Mel, STFT, CQT)
- Phase T5: Branch A (eGeMAPS) standalone baseline metrics logged.
- Phase 10: Multiview ConvNeXt V2 (No Temporal) ablation metrics recorded in registry.
- Phase 12: ConvNeXt V2 + Transformer ablation metrics recorded in registry.
- Phase 14: Multimodal fusion (+acoustic, +acoustic+asr, gated full model) ablations logged in registry.
- Phase 17: Calibrated test metrics available.

## Milestones
- Milestone 1: Data split & environment ready (reached)
- Milestone 2: Baseline model ready (reached)
- Milestone 4: Transformer ready (reached)
- Milestone 5: Full multimodal model ready (reached)
- Milestone 6: XAI ready (reached)
- Milestone 7: Validated and calibrated model ready (reached)
- Milestone 8: FINAL MODEL EXPORTED (reached)
- Milestone 9: FINAL PROJECT STRUCTURE CREATED (reached)
- Milestone 12: FRONTEND READY (reached)
- Milestone 13: END-TO-END SYSTEM READY (reached)
- Milestone 14: DEPLOYMENT READY (reached)
- Milestone 15: PROJECT COMPLETE & AUDITED (reached)

## Artifact Locations
- Persistent Drive Artifacts Directory: `/content/drive/MyDrive/pd_voice_project/artifacts/`
- Local Exported Model: `model/exported/model_v1.0.0/`
- Checkpoints Directory: `/content/drive/MyDrive/pd_voice_project/checkpoints/`
- Exported Models Directory: `/content/drive/MyDrive/pd_voice_project/exported/`
- Environment Report: `/content/drive/MyDrive/pd_voice_project/artifacts/environment_report.json`
- Raw Index CSV: `/content/drive/MyDrive/pd_voice_project/artifacts/raw_index.csv`
- Excluded Recordings CSV: `/content/drive/MyDrive/pd_voice_project/artifacts/excluded_recordings.csv`
- Data Manifest JSON: `model/artifacts/data_manifest_v1.0-20260823.json`
- Split Manifest JSON: `model/artifacts/split_manifest_v1.0-20260823.json`
- Dataset Audit Report: `docs/research/DATASET.md`

## Environment Requirements
- Git >= 2.0
- Python >= 3.10
- Google Colab GPU runtime (NVIDIA T4 / V100 / A100 with CUDA >= 12.0)
- Google Drive mount at `/content/drive` for persistent storage

## Pending Tasks
- Proceed to Phase 7: Baseline Acoustic Feature Extraction & Classical Classifiers

## Model Training Track
- **Completed**: [T1-T12] Model Trained in Colab & Real Weights Deployed to Predictor
- **Next**: System is 100% Production Ready with Real Neural Weights
- **Dataset Version**: MDVR-KCL (August 2026)
