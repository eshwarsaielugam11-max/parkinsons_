# Phase T2: Public Dataset Sourcing Plan

## Overview
This document evaluates candidate public Parkinson's Disease (PD) voice datasets. Because three of our four architectural branches (Visual Spectrogram/ConvNeXt, Temporal Transformer, and Self-Supervised ASR) strictly require **raw audio**, we cannot rely solely on feature-only datasets. This plan outlines primary, secondary, and supplementary data sources, establishing a clear access pathway for Phase T3.

---

## 1. Candidate Dataset Evaluation

### A. MDVR-KCL (King's College London Mobile Device Voice Recordings)
* **Content Type**: Raw Audio (.wav)
* **Task Type**: Sustained vowels (/a/, /o/, /u/), read text, and spontaneous dialogue.
* **Size**: 37 PD patients + 33 Healthy Controls (HC) (~70 total subjects).
* **Access Mechanism**: Instant download via Zenodo.
* **License Terms**: Open license (Creative Commons / CC BY 4.0 or similar).
* **Suitability**: **High**. Provides the exact raw audio needed for Branches A, B, and C. The no-friction access makes it the ideal starting point.

### B. Italian Parkinson's Voice and Speech (Dimauro et al.)
* **Content Type**: Raw Audio
* **Task Type**: Vowels, words, and sentences.
* **Size**: ~50 subjects (PD + HC).
* **Access Mechanism**: Free registration required via IEEE DataPort.
* **License Terms**: IEEE DataPort standard usage terms (research use).
* **Suitability**: **Medium**. Good supplementary raw audio, but requires registration overhead.

### C. PC-GITA (Colombian Spanish PD Speech Corpus)
* **Content Type**: Raw Audio
* **Task Type**: Comprehensive (Sustained vowels, diadochokinetic (DDK) tasks, sentences, spontaneous speech).
* **Size**: 50 PD + 50 HC (100 total subjects).
* **Access Mechanism**: Formal data-use-agreement request to the GITA research group.
* **License Terms**: Restricted academic/research use.
* **Suitability**: **High (but Slow Track)**. The presence of explicit DDK tasks makes it highly valuable for Branch D (ASR dysdiadochokinesia detection), but the access delay makes it unsuitable as an immediate primary blocker.

### D. UCI ML Repository "Parkinson's Disease Classification" (Sakar et al., 2018)
* **Content Type**: Pre-extracted acoustic features only (NO raw audio).
* **Task Type**: Vowels, words, and non-word repetition (features only).
* **Size**: ~252 subjects/recordings.
* **Access Mechanism**: Instant download.
* **License Terms**: Open access.
* **Suitability**: **Low**. Can only supplement/pretrain Branch A (Acoustic/eGeMAPS). Cannot be used for Branches B, C, or D.

---

## 2. Concrete Sourcing Recommendation

### Primary Strategy: Start with MDVR-KCL
We will proceed with **MDVR-KCL** as our primary dataset to bootstrap the training pipeline immediately. 
* It fulfills the raw audio requirement.
* It requires zero administrative waiting time (Zenodo instant download).
* It directly supports Branch A (eGeMAPS), Branch B (ConvNeXt-V2), and Branch C (Temporal Transformer).

### Branch D (ASR) Strategy & Fallback
Branch D relies on detecting articulatory sluggishness (dysdiadochokinesia). While MDVR-KCL lacks explicit rapid DDK tasks (e.g., "pa-ta-ka"), its **read text and spontaneous dialogue** tasks serve as an adequate proxy for assessing general articulatory precision and pause structure using `faster-whisper`.
* **Parallel Track**: We will initiate the formal request for **PC-GITA** immediately. Once access is granted, we will supplement Branch D with PC-GITA's explicit DDK recordings. MDVR-KCL's reading tasks will prevent Branch D from being blocked in the interim.

---

## 3. Dataset Size Risk & Mitigation Strategy

### The Risk
Public PD voice datasets are notoriously small (tens to low hundreds of subjects). Using heavy multimodal deep learning models (ConvNeXt + Transformers) on ~70 subjects presents a **severe risk of overfitting**. The model may memorize the acoustic environment or patient identity rather than generalizing pathological markers.

### Mitigation Plan (For Phase T9: Training Config)
To ensure robust generalization, Phase T9 will implement strict constraints:
1. **Model Capacity Reduction**: Use the smallest available ConvNeXt variant (e.g., `convnextv2_femto` or `atto`) and a shallow Transformer sequence layer.
2. **Heavy Regularization**: High dropout rates, aggressive weight decay, and stochastic depth (DropPath).
3. **Cross-Validation**: We must abandon the standard static single train/test split. The pipeline will implement **k-fold cross-validation** (e.g., 5-fold or 10-fold) with strict patient-level separation to guarantee unbiased evaluation.
4. **Early Layer Freezing**: Pretrained weights from ImageNet (ConvNeXt) will remain largely frozen, fine-tuning only the late projection heads and MLP fusion layers.
