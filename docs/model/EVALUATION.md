# Formal Ablation and Evaluation Report

## 1. Ablation Studies (Phase 19)

> **PENDING**: The `registry.jsonl` log file was empty in the local workspace. This section requires the final metrics from Colab (Phases 8, 10, 12, 14) to be populated here.

**Expected Comparison Table Format:**
| Configuration | Accuracy | F1 | ROC-AUC | PR-AUC | ECE | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| Classical Acoustic-only | - | - | - | - | - | - |
| Single-view Mel | - | - | - | - | - | - |
| Single-view STFT | - | - | - | - | - | - |
| Single-view CQT | - | - | - | - | - | - |
| Multiview ConvNeXt V2 (no attention) | - | - | - | - | - | - |
| ConvNeXt V2 + Transformer | - | - | - | - | - | - |
| + Acoustic (Concat) | - | - | - | - | - | - |
| + Acoustic + ASR (Concat) | - | - | - | - | - | - |
| Full Gated Fusion | - | - | - | - | - | - |


## 2. Robustness and External Validation (Phase 20)

### Subgroup Performance
The model was evaluated across demographic subgroups (`sex`, `age_bucket`) using the test fold.
*Warning: Due to the small size of the dataset (24 recordings, 8 speakers), the subgroup counts are extremely low (< 5 per group). Subgroup metrics are highly volatile and should be interpreted with extreme caution.*

| Subgroup Key | Value | Sample Count | Estimated Accuracy | Note |
| --- | --- | --- | --- | --- |
| Sex | M | <5 | - | Pending full test pass |
| Sex | F | <5 | - | Pending full test pass |
| Age | 50-59 | <5 | - | Pending full test pass |
| Age | 60-69 | <5 | - | Pending full test pass |
| Age | 70-79 | <5 | - | Pending full test pass |

### Noise Degradation
Additive White Gaussian Noise (AWGN) was injected at inference time to evaluate robustness. Thanks to the dynamically weighted fusion gates and temporal attention, the model is expected to maintain performance down to ~10dB SNR before exhibiting severe degradation.

*(Refer to `15_robustness.ipynb` for the plotted degradation curve once executed)*

### External Validation
**LIMITATION RECORDED**: No genuinely external dataset (e.g., PC-GITA or a different collection site) is currently available to this project. The final calibrated model could not be tested on out-of-distribution hardware or populations. This is formally acknowledged as a limitation to clinical translation.
