# Mock/Stub Implementation Audit Report (Phase T1)

## Overview
This report details the current state of the Parkinson's voice prediction model implementation. It identifies exactly which files contain real architecture code vs. mock/stub logic. This gap report serves as the foundation for the upcoming training phases (T2-T12).

## 1. Branch Implementations

### Branch 1: Acoustic / eGeMAPS
* **Implementation File(s)**: `model/src/features/egemaps.py`, `model/src/features/acoustic.py`, `model/src/features/pipeline.py`
* **Status**: **REAL**. The code uses the `opensmile` library (FeatureSet.eGeMAPSv02) to extract legitimate acoustic features (Jitter, Shimmer, HNR, etc.).
* **What's Missing**: It is not currently invoked during the inference pipeline. The pipeline currently calls a mock method `_extract_acoustic()` instead of executing this real pipeline.

### Branch 2: Visual Spectrogram / ConvNeXt-V2
* **Implementation File(s)**: `model/src/spectrograms/mel.py`, `model/src/spectrograms/stft.py`, `model/src/spectrograms/cqt.py`, `model/src/models/convnext_branch.py`
* **Status**: **REAL**. The spectrogram generation uses real DSP logic (via `librosa` or equivalent). The neural network branch (`convnext_branch.py`) correctly uses `timm` to load a ConvNeXt-V2 backbone based on configuration.
* **What's Missing**: Spectrogram generation and model forward passes are bypassed during inference.

### Branch 3: Temporal Transformer
* **Implementation File(s)**: `model/src/models/transformer_encoder.py`
* **Status**: **REAL**. Implements a legitimate multi-head self-attention PyTorch module designed to accept the sequence of windowed embeddings.
* **What's Missing**: Unused in the current prediction flow.

### Branch 4: Self-Supervised ASR
* **Implementation File(s)**: `model/src/features/asr_features.py`
* **Status**: **REAL**. The file integrates `faster-whisper` to transcribe audio, compute word timestamps, Levenshtein distances (WER/CER), and speaking rate/pause structure. 
* **What's Missing**: Unused in the current prediction flow.

## 2. Fusion & Calibration

### Fusion MLP
* **Implementation File(s)**: `model/src/models/fusion.py`, `model/src/models/heads.py`, `model/src/models/projection.py`
* **Status**: **REAL**. The PyTorch `MultimodalFusionModel` correctly concatenates (or gates) the `deep_rep`, `ac_rep`, and `as_rep` embeddings and pushes them through a classifier head.
* **What's Missing**: The fusion model is never instantiated or called in the local prediction endpoint.

### Isotonic Calibration Layer
* **Implementation File(s)**: `model/src/calibration/calibrate.py`
* **Status**: **REAL**. Contains valid `sklearn` implementations for both Isotonic Regression and Platt Scaling (Logistic Regression), alongside robust serialization logic.
* **What's Missing**: Calibration is not applied during inference; a hardcoded probability is returned instead.

## 3. Explainability (XAI) Methods

### SHAP (Acoustic Features)
* **Implementation File(s)**: `model/src/explainability/shap_acoustic.py`
* **Status**: **REAL**. Wraps `shap.KernelExplainer` or `shap.DeepExplainer` to compute feature attributions.
* **What's Missing**: Hardcoded mock dictionary `{"jitter": 0.05}` is returned in the API instead of computing SHAP.

### Grad-CAM (Visual Spectrograms)
* **Implementation File(s)**: `model/src/explainability/gradcam.py`
* **Status**: **REAL**. Implements gradient-weighted class activation mapping for the ConvNeXt branch.
* **What's Missing**: Bypassed; API returns a hardcoded string `"heatmap.png"`.

### Attention Rollout (Temporal Sequence)
* **Implementation File(s)**: `model/src/explainability/attention_rollout.py`
* **Status**: **REAL**. Accurately implements attention graph traversal (`compute_attention_rollout`) to find token importance.
* **What's Missing**: Bypassed; API returns a mock array `[0.1, 0.9]`.

## 4. Code Path Trace & Mock Injection Points

When a request arrives, the backend API (`backend/inference/predictor_service.py`) calls `get_predictor()`, which returns a singleton `Predictor`. The `Predictor.predict()` method is where the entire execution is stubbed.

**Exact Mock Injections (`model/src/inference/predictor.py`):**
1. **Preprocessing**: Line 36 (`def _preprocess`). Returns `{"waveform": [0.0]*16000, "quality": 9.0}`.
2. **Acoustic Extraction**: Line 40 (`def _extract_acoustic`). Returns `[0.0]*38`.
3. **ASR Extraction**: Line 44 (`def _extract_asr`). Returns `[0.0]*7`.
4. **Spectrogram Extraction**: Line 48 (`def _extract_spectrograms`). Returns dict of `None`.
5. **Model Forward Pass Bypass**: Line 68-72 (`if self.model_loaded: pass`). Skips actual `self.model(...)` execution.
6. **Hardcoded Prediction**: Lines 74-77. Injects `pd_prob = 0.82` and `confidence = 0.95`.
7. **Hardcoded XAI References**: Lines 86-89. Injects mock SHAP, Grad-CAM, and Attention outputs.
8. **Hardcoded Vector Embedding**: Line 113. Injects `res["_internal_embedding"] = [0.1] * 128`.

## 5. Model Weights Status

* **Status**: NO REAL WEIGHTS EXIST.
* **Locations Checked**: 
  * `docs/model/exported/model_v1.0.0/weights.pt`
  * `model/exported/model_v1.0.0/weights.pt`
* **Finding**: Both files exist but are exactly **0 bytes**. They are placeholder files. The real weights must be generated in the upcoming training phases.

## 6. Integration Point (T12 Swap Point)

The single point of integration to switch from mock to real execution is:
**`model/src/inference/predictor.py`**

To operationalize the model, the `Predictor` class must be rewritten to:
1. Load the real `weights.pt` using `torch.load()`.
2. Delete the internal mock `_extract_*` methods and replace them with imports from `model.src.features.pipeline` and `model.src.preprocessing.pipeline`.
3. Delete the hardcoded `pd_prob = 0.82` assignments and execute `out = self.model(...)`.
4. Apply the real calibration using `apply_calibration()` from `model.src.calibration.calibrate`.
