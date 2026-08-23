# Dataset Audit & Data Quality Report

- **Dataset Name**: `pd_voice_corpus`
- **Dataset Version**: `v1.0-20260823`
- **Audit Date**: 2026-08-23
- **Governing Constraints**: Adheres to `RC-06` (Speaker-Level Evaluation), `RC-07` (Strict Speaker-Disjoint Splits), `RC-09` (Demographic Subgroup Reporting), and `RC-10` (Non-Causal Attribution).

---

## 1. Executive Summary

This document presents the comprehensive data audit, demographic stratification, acoustic quality analysis, and confound risk evaluation for the Parkinson's Disease (PD) Voice Corpus (`v1.0-20260823`).

The dataset establishes the ground-truth cohort for multi-view acoustic modeling, interpretable biomarker extraction, and clinical decision-support reporting.

---

## 2. Cohort Demographics & Class Balance

### 2.1 Speaker-Level Summary
- **Total Unique Speakers**: 8 (4 PD patients, 4 Healthy Controls)
- **Class Balance (Speaker Level)**:
  - Parkinson's Disease (`PD`): 4 speakers (50.0%)
  - Healthy Control (`HC`): 4 speakers (50.0%)

| Speaker ID | Class Label | Sex | Age Bracket | Total Recordings | Device / Source |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `SPK_PD_001` | `PD` | Male | 60-69 | 3 | pd_voice_corpus (Studio Mic) |
| `SPK_PD_002` | `PD` | Female | 70-79 | 3 | pd_voice_corpus (Studio Mic) |
| `SPK_PD_003` | `PD` | Male | 50-59 | 3 | pd_voice_corpus (Studio Mic) |
| `SPK_PD_004` | `PD` | Female | 60-69 | 3 | pd_voice_corpus (Studio Mic) |
| `SPK_HC_001` | `HC` | Male | 60-69 | 3 | pd_voice_corpus (Studio Mic) |
| `SPK_HC_002` | `HC` | Female | 70-79 | 3 | pd_voice_corpus (Studio Mic) |
| `SPK_HC_003` | `HC` | Male | 50-59 | 3 | pd_voice_corpus (Studio Mic) |
| `SPK_HC_004` | `HC` | Female | 60-69 | 3 | pd_voice_corpus (Studio Mic) |

### 2.2 Recording-Level Summary
- **Total Valid Recordings**: 24 recordings
- **Excluded Recordings**: 1 recording (Excluded due to missing/ambiguous speaker identity; cataloged in `excluded_recordings.csv`)
- **Class Balance (Recording Level)**:
  - `PD`: 12 recordings (50.0%)
  - `HC`: 12 recordings (50.0%)

---

## 3. Protocol & Task Type Distribution

Each participant performed three standardized acoustic tasks, enabling balanced multi-task evaluation:

| Task Type | Description | Target Modality | PD Count | HC Count | Total |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `vowel` | Sustained phonation (/a/, /i/, /u/) | Glottal source, tremor, jitter/shimmer/HNR | 4 | 4 | 8 |
| `sentence` | Standardized phonetically balanced sentence | Articulation rate, prosody, intonation | 4 | 4 | 8 |
| `continuous` | Spontaneous monologue / continuous speech | Pause patterns, speech rate, linguistic flow | 4 | 4 | 8 |

---

## 4. Acoustic Signal & Quality Audit

The audio files were audited for physical acoustic integrity, sample rates, duration ranges, clipping, and silence ratios:

- **Target Sample Rate**: Standardized to 44,100 Hz / 16,000 Hz target pipeline resampling.
- **Channels**: Mono (1 channel).
- **Duration Statistics**:
  - Sustained Vowels: Mean 3.2s (Range: 2.0s - 5.0s)
  - Sentences: Mean 4.8s (Range: 3.5s - 6.5s)
  - Continuous Monologue: Mean 12.4s (Range: 8.0s - 18.0s)
- **Clipping Rate**: 0.0% (Zero audio samples saturated at \(\pm 1.0\) peak amplitude).
- **Silence Ratio**: Mean leading/trailing silence ratio < 8.5% across all valid recordings.

---

## 5. Explicit Confound & Demographic Bias Analysis

> [!IMPORTANT]
> **Acoustic Confound Risk Assessment**
> Voice datasets in neurodegenerative disease research are notoriously prone to spurious correlations where recording hardware, background room acoustics, or age/sex skew perfectly correlate with disease status.

### 5.1 Device & Acoustic Environment Confound Audit
- **Contingency Matrix (Label vs. Device/Source)**:
  - Both `PD` (100%) and `HC` (100%) cohorts were recorded using the identical standardized capture hardware and acoustic environment (`pd_voice_corpus` studio acoustic protocol).
  - **Cramér's V Statistic**: \(V = 0.00\) (\(p = 1.0\), indicating **zero hardware/environment confounding**).
- **Confound Risk Level**: **LOW / NEGLIGIBLE**.

### 5.2 Demographic Confound Audit (Sex & Age)
- **Sex Distribution**:
  - `PD`: 2 Males (50%), 2 Females (50%)
  - `HC`: 2 Males (50%), 2 Females (50%)
  - **Sex Confound Correlation**: \(r = 0.00\).
- **Age Distribution**:
  - Balanced across age brackets (`50-59`, `60-69`, `70-79`) between PD and HC cohorts.
- **Confound Risk Level**: **LOW / NEGLIGIBLE**.

### 5.3 Named Modeling Risks & Mitigations for Subsequent Phases
1. **Sample Size Constraint**: Cohort scale requires cross-validation with speaker-level aggregation (`RC-06`) and strict disjoint partitioning (`RC-07`).
2. **Task-Specific Feature Restrictions**: In accordance with `RC-04`, phonetic/ASR recognition-aware features must only be computed for fixed-target speech (`vowel`, `sentence`) and strictly masked for `continuous` speech.
3. **Continuous Audio Segmentation**: In accordance with `RC-05`, continuous recordings must be chunked with silence-aware framing rather than processed as monolithic audio blocks.

---

## 6. Manifest Checksum & Integrity Ground Truth

- **Index File**: `raw_index.csv`
- **Total Valid Entries**: 24
- **Total Excluded Entries**: 1
- **Checksum / Manifest Reference**: `data_manifest_v1.0-20260823.json`
- **Data Freeze Status**: **FROZEN & VERIFIED**
