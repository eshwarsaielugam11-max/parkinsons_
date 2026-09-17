# Explainable AI (XAI) Architecture

## 1. Overview & Multi-Perspective Interpretability

To provide clinically actionable transparency rather than black-box probabilities, the system produces three complementary, synchronized explainability modalities for every inference session:

```mermaid
flowchart TD
    A[Multimodal Model Prediction] --> B1[1. Spatial Saliency: Grad-CAM on Spectrograms]
    A --> B2[2. Temporal Relevance: Attention Timeline Rollout]
    A --> B3[3. Feature Attribution: Kernel SHAP on Acoustic Biomarkers]
    B1 & B2 & B3 --> C[Structured Evidence Object /api/v1/xai/{session_id}]
    C --> D1[Frontend Interactive Visualizers]
    C --> D2[RAG Prompt Context for Clinical Report Synthesis]
```

---

## 2. XAI Modalities & Algorithms

### 1. Grad-CAM Spatial Heatmap (`model/src/explainability/gradcam.py`)
- **Target Layer**: Final convolutional stage of the ConvNeXt-V2 backbone (`stage4.blocks[-1]`).
- **Mechanism**: Computes gradients of the target class logit with respect to spatial feature maps, applying ReLU activation to isolate positive contributing time-frequency regions.
- **Formant & Harmonics Localization**: Highlights acoustic energy anomalies (e.g. harmonic breakdown in upper formants $F_2 - F_4$, subharmonic pitch breaks).

### 2. Temporal Attention Timeline (`model/src/explainability/attention.py`)
- **Mechanism**: Aggregates attention weight matrices across all Transformer attention heads and layers using Attention Rollout.
- **Output**: Per-window relative importance score ($\sum w_i = 1.0$) across the duration of the recording, identifying specific phonation segments (e.g., vocal tremor spikes or speech arrest).

### 3. Signed Acoustic SHAP Attribution (`model/src/explainability/shap_values.py`)
- **Mechanism**: Kernel SHAP computed over 88 eGeMAPS acoustic features against a background reference cohort of 100 healthy voice baselines.
- **Color Coding**:
  - **Red ($>0$)**: Pushing prediction toward Elevated Parkinson's Risk.
  - **Blue ($<0$)**: Contributing toward Healthy Norms.

---

## 3. Clinical Acoustic Terminology Glossary

The XAI subsystem maps complex bioacoustic metrics into plain, minimally-jargon language for clinicians and patients:

| Acoustic Feature | Clinical Term | Plain-Language Interpretation |
|---|---|---|
| `jitterLocal` | Micro-Pitch Variation | Cycle-to-cycle frequency irregularity indicating subtle vocal cord vibration instability. |
| `shimmerLocal` | Micro-Amplitude Variation | Cycle-to-cycle loudness perturbation reflecting laryngeal muscle weakness or tremor. |
| `HNR` | Harmonics-to-Noise Ratio | Ratio of pure vocal tone to breathiness or hoarseness; lower values denote voice breathiness. |
| `F1_bandwidth` | First Formant Bandwidth | Resonance sharpness related to pharyngeal and vocal tract constriction stability. |
| `F2_frequency` | Second Formant Frequency | Articulatory tongue body positioning during vowel production. |
| `spectralFlux` | Spectral Timbre Flux | Rate of acoustic spectrum changes over consecutive time frames. |
