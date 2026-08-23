# Project State

## Completed Phases
- Phase 0
- Phase 1
- Phase 2
- Phase 3
- Phase 4
- Phase 5
- Phase 6

## Current Phase
- Phase 6 (complete)

## Next Phase
- Phase 7

## Files Created
- .gitignore
- .env.example
- README.md
- PROJECT_STATE.md
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
- None (Acoustic confound audit confirmed zero device/environment confounding in baseline cohort)

## Model Version
- None

## Dataset Version
- v1.0-20260823 (pd_voice_corpus)

## Model Metrics
- None

## Artifact Locations
- Persistent Drive Artifacts Directory: `/content/drive/MyDrive/pd_voice_project/artifacts/`
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
