# Non-Negotiable Research Constraints and Architectural Rules

This document records the foundational research conclusions and architectural constraints governing this project. Every constraint in this document is an absolute, non-negotiable requirement. No subsequent phase, refactor, optimization, or pull request may bypass, alter, or silently violate these rules.

---

## The 14 Core Constraints

### Constraint 1: Interpretable Acoustic Feature Branch
- **Rule ID**: `RC-01-INTERPRETABLE-BRANCH`
- **Rule**: Traditional acoustic biomarkers—specifically MFCCs, pitch/fundamental frequency (\(F_0\)), jitter, shimmer, and Harmonics-to-Noise Ratio (HNR)—must be extracted, preserved, and fed through a dedicated interpretable feature branch.
- **Rationale**: Deep embeddings alone lack clinical transparency. Retaining explicit acoustic measures allows clinicians to inspect physiologically grounded vocal characteristics.
- **Verification / Testable Check**: The feature extraction pipeline must export explicit numeric vectors for MFCCs, \(F_0\), jitter, shimmer, and HNR alongside deep feature representations. Unit tests must assert non-null output vectors for all 5 feature groups on valid audio input.

---

### Constraint 2: SHAP for Acoustic Feature Attribution
- **Rule ID**: `RC-02-SHAP-ATTRIBUTION`
- **Rule**: SHAP (SHapley Additive exPlanations) is the standard attribution method for computing and explaining feature importance across the tabular/acoustic biomarker branch.
- **Rationale**: SHAP provides mathematically consistent, game-theoretic local and global feature attribution that aligns with clinical explainability standards.
- **Verification / Testable Check**: All explainability modules computing acoustic feature importances must invoke TreeSHAP or KernelSHAP and generate valid SHAP values matching the input feature dimensions.

---

### Constraint 3: Complementary Multi-View Representations (Mel / STFT / CQT)
- **Rule ID**: `RC-03-MULTIVIEW-TIME-FREQ`
- **Rule**: Time-frequency representations—specifically Log-Mel Spectrograms, Short-Time Fourier Transform (STFT/linear spectrograms), and Constant-Q Transform (CQT)—must be retained as complementary views rather than collapsed into a single representation.
- **Rationale**: Mel filterbanks capture perceptual auditory scales, linear STFT preserves harmonic structures across high frequencies, and CQT provides logarithmically spaced frequency resolution ideal for pitch and low-frequency glottal dynamics.
- **Verification / Testable Check**: Preprocessing must generate distinct Mel, STFT, and CQT tensors. The multi-view neural backbones must accept and process all three modalities.

---

### Constraint 4: Recognition-Aware Features Restricted to Fixed-Target Speech
- **Rule ID**: `RC-04-RECOGNITION-FIXED-TARGET-ONLY`
- **Rule**: ASR-based or phonetic recognition-aware features (e.g., phonetic duration, phone posterior probabilities, word error alignment) may only be computed and utilized when processing fixed-target speech protocols (e.g., standardized sustained vowels, standard read phonetically balanced passages). They must NOT be applied to unconstrained free continuous speech where lexical variability acts as a confound.
- **Rationale**: Lexical content variability in free continuous speech invalidates acoustic-phonetic alignment and introduces semantic confounding.
- **Verification / Testable Check**: Pipeline configurations must enforce task-type assertions: if input task is unconstrained speech, phonetic alignment modules must either be disabled or throw a configuration error.

---

### Constraint 5: Windowing of Continuous Speech
- **Rule ID**: `RC-05-CONTINUOUS-SPEECH-WINDOWING`
- **Rule**: Continuous speech recordings must be segmented into uniform or silence-bounded overlapping/non-overlapping temporal windows (chunks) prior to feature extraction/inference, rather than being ingested or pooled as a single unstructured audio blob.
- **Rationale**: Uniform windowing preserves local temporal dynamics, limits memory bottlenecks, enables artifact/silence filtering, and allows segment-level confidence aggregation.
- **Verification / Testable Check**: Continuous speech inputs exceeding the window length threshold \(T_{\text{max}}\) must pass through a windowing/framing preprocessor that outputs a sequence of shape `[N_windows, Window_Length]`.

---

### Constraint 6: Speaker-Level Evaluation
- **Rule ID**: `RC-06-SPEAKER-LEVEL-EVAL`
- **Rule**: All model metrics, validation scores, test benchmarks, and threshold selections must be computed at the speaker (patient) level, aggregating segment-level predictions per subject before calculating classification/regression metrics.
- **Rationale**: Frame-level or clip-level evaluation artificially inflates sample size, skews true clinical utility, and correlates heavily with utterance length.
- **Verification / Testable Check**: Evaluation scripts must calculate metrics (AUROC, Sensitivity, Specificity, F1) grouped by `speaker_id` / `patient_id`. An assertion error must trigger if metrics are reported purely on un-aggregated frame/chunk counts.

---

### Constraint 7: Strict Patient/Speaker Disjoint Splits
- **Rule ID**: `RC-07-SPEAKER-DISJOINT-SPLITS`
- **Rule**: No participant (speaker/patient) may appear in more than one split (e.g., train, validation, and test sets must be strictly mutually disjoint with respect to `speaker_id`).
- **Rationale**: Data leakage across splits results in memorization of speaker identity, acoustic channel, and microphone characteristics, producing falsely optimistic performance estimates.
- **Verification / Testable Check**: Automated data validation tests must verify:
  \[
  \text{Set}(\text{train\_speakers}) \cap \text{Set}(\text{val\_speakers}) \cap \text{Set}(\text{test\_speakers}) = \emptyset
  \]
  Any non-empty intersection must immediately fail dataset split creation and CI pipelines.

---

### Constraint 8: Fold-Local Preprocessing and Fitting
- **Rule ID**: `RC-08-FOLD-LOCAL-PREPROCESSING`
- **Rule**: All fitted statistics—including feature scalers (mean, variance, min-max), imputers, decision thresholds, calibration mappings (Platt scaling, isotonic regression), and multi-modal fusion weights—must be fitted exclusively on the training fold and applied out-of-sample to validation/test folds.
- **Rationale**: Fitting normalization parameters or decision thresholds across full datasets introduces statistical data leakage and invalidates generalizability claims.
- **Verification / Testable Check**: Preprocessing pipelines must adhere to scikit-learn style `fit_transform` on train splits and strict `transform` only on validation/test splits. Unit tests must verify that validation statistics are not accessed during model fitting.

---

### Constraint 9: Demographic and Recording Subgroup Reporting
- **Rule ID**: `RC-09-SUBGROUP-CONFOUND-REPORTING`
- **Rule**: Performance metrics must be audited and reported across demographic subgroups (e.g., sex, age groups) and recording-condition cohorts (e.g., microphone hardware, acoustic environment, sampling rate).
- **Rationale**: Speech and audio models are susceptible to demographic and acoustic confounding, which can mask poor performance on vulnerable or under-represented sub-populations.
- **Verification / Testable Check**: Evaluation summary reports must generate stratified sub-tables displaying sample size, Sensitivity, Specificity, and AUROC for each metadata subgroup category.

---

### Constraint 10: Non-Causal Presentation of Model Attribution
- **Rule ID**: `RC-10-NON-CAUSAL-ATTRIBUTION`
- **Rule**: Model attributions, feature importance scores (e.g., SHAP, saliency maps), and acoustic correlations must never be presented, labeled, or phrased as causal clinical evidence or definitive physiological proof.
- **Rationale**: Statistical associations in machine learning models reflect correlations in the dataset and do not establish medical causality or biological etiology.
- **Verification / Testable Check**: All generated summaries, UI text templates, and clinical report schemas must explicitly state statistical association disclaimers and avoid causal assertions (e.g., "features associated with prediction" vs. "features that caused the condition").

---

### Constraint 11: Mandatory Calibration and Uncertainty Estimation
- **Rule ID**: `RC-11-CALIBRATION-UNCERTAINTY`
- **Rule**: Every screening output must produce both a calibrated probability score (e.g., via temperature scaling or isotonic regression) and an explicit uncertainty metric (e.g., prediction intervals, entropy, or ensemble variance).
- **Rationale**: Uncalibrated raw softmax scores produce overconfident misclassifications in clinical screening contexts where well-calibrated risk probabilities and abstention indicators are critical.
- **Verification / Testable Check**: Inference response schemas must mandate both `calibrated_risk_score` (bounded \([0.0, 1.0]\)) and `uncertainty_score` fields. Schema validators must reject responses missing either metric.

---

### Constraint 12: Environmental, Noise, and Device Shift Robustness Testing
- **Rule ID**: `RC-12-ROBUSTNESS-BENCHMARKING`
- **Rule**: The system must be formally evaluated against noise injections (e.g., additive background noise at varying SNRs), microphone frequency response perturbations, and sample rate downsampling.
- **Rationale**: Audio screening tools deployed in real-world clinic or telemedicine environments encounter severe acoustic domain shifts.
- **Verification / Testable Check**: Test suites must include an automated stress test benchmarking performance drop (\(\Delta\text{AUROC}\)) across specified SNR levels (e.g., 20dB, 10dB, 0dB).

---

### Constraint 13: Grounded Report Generation via RAG
- **Rule ID**: `RC-13-RAG-GROUNDED-REPORTS`
- **Rule**: All clinical decision-support narratives, summaries, and recommendations generated by language models must be strictly grounded using Retrieval-Augmented Generation (RAG) referencing indexed medical guidelines, trial protocols, and validated study literature.
- **Rationale**: Unbounded LLM generation produces hallucinations and unverified medical advice. Grounding guarantees citations and traceable provenance for clinical text.
- **Verification / Testable Check**: Generated reports must contain citation references linked directly to retrieved source documents. Report synthesis prompts must explicitly enforce context-grounded extraction.

---

### Constraint 14: LLM Strictly as Narrator, Never as Classifier
- **Rule ID**: `RC-14-LLM-NOT-CLASSIFIER`
- **Rule**: The Large Language Model (LLM) acts exclusively as an explainer, summarizer, and reporting interface. The LLM must NEVER perform numeric classification, compute risk scores, or alter/override the quantitative probabilities produced by the calibrated acoustic models.
- **Rationale**: LLMs are non-deterministic, poorly calibrated numerical estimators, and prone to conversational sycophancy. Risk quantification must remain strictly anchored in deterministic, validated acoustic models.
- **Verification / Testable Check**: The pipeline architecture must decouple acoustic inference from report generation: the acoustic model outputs immutable numeric tensors/floats that are passed as read-only context to the LLM. The final API payload must source its risk scores directly from the acoustic pipeline.

---

## Governance and Enforcement Summary

| Constraint ID | Focus Area | Mandatory Enforcement Mechanism |
| :--- | :--- | :--- |
| `RC-01` | Acoustic Features | Pipeline extraction test for MFCC, \(F_0\), Jitter, Shimmer, HNR |
| `RC-02` | Explainability | Unit test verifying SHAP explainer integration |
| `RC-03` | Representations | Tensors for Mel, STFT, CQT generated & ingested |
| `RC-04` | Task Protocols | Task-type assertion guard on phonetic feature extractor |
| `RC-05` | Audio Windowing | Input segmenter test on continuous audio recordings |
| `RC-06` | Evaluation Unit | Aggregation by `speaker_id` enforced in evaluation metrics |
| `RC-07` | Data Integrity | Zero speaker overlap assertion across train/val/test splits |
| `RC-08` | Leakage Prevention | Strict fold-local `fit_transform` / `transform` execution |
| `RC-09` | Fairness & Bias | Stratified subgroup performance audit reports |
| `RC-10` | Clinical Safety | Template linting for non-causal language |
| `RC-11` | Risk Reliability | Mandatory calibrated risk and uncertainty output fields |
| `RC-12` | Domain Robustness | Automated SNR perturbation test suite |
| `RC-13` | Report Validity | Citation verification on RAG report outputs |
| `RC-14` | System Integrity | Read-only score injection; LLM cannot alter risk values |
