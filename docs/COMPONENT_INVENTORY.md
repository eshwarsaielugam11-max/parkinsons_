# Component Inventory & Redesign Phase Roadmap

This inventory maps every existing UI component identified in `docs/AUDIT_REPORT.md` to its designated redesign phase (Prompts 06–12).

---

## Component Mapping Matrix

| Component Name | File Path | Current Page(s) Using It | Redesign Phase Responsible | Key Restyling Objectives |
| :--- | :--- | :--- | :--- | :--- |
| **`BaseLayout`** | `frontend/src/layouts/BaseLayout.tsx` | All 6 Routes (`/`, `/record`, `/upload`, `/result`, `/report`, `/history`) | **Phase 06** | Implement floating pill nav, ambient backdrop lighting, restrained footer disclaimer. |
| **`Recorder`** | `frontend/src/components/Recorder.tsx` | Record (`/record`) | **Phase 07** | Real-time oscillogram waveform styling, circular state timer, pill action controls. |
| **`QualityIndicator`** | `frontend/src/components/QualityIndicator.tsx` | Record (`/record`), Upload (`/upload`) | **Phase 07 & Phase 08** | Ambient SNR meter, glass surface enclosure, clinical quality threshold status. |
| **`ProbabilityGauge`** | `frontend/src/components/ProbabilityGauge.tsx` | Result (`/result`) | **Phase 09** | Asymmetric hero arc gauge, calibrated confidence interval bracket, risk typography. |
| **`SpectrogramHeatmap`** | `frontend/src/components/SpectrogramHeatmap.tsx` | Result (`/result`) | **Phase 09** | Grad-CAM activation colormap overlay, Mel/STFT toggle pills, spectro-temporal canvas. |
| **`AttentionTimeline`** | `frontend/src/components/AttentionTimeline.tsx` | Result (`/result`) | **Phase 09** | Transformer token multi-head attention bars, interactive hover tooltip scrubbers. |
| **`ShapChart`** | `frontend/src/components/ShapChart.tsx` | Result (`/result`) | **Phase 09** | Horizontal biomarker waterfall bars, preserve exact signed direction convention (`#ef4444` risk vs `#3b82f6` healthy). |
| **`ReportView`** | `frontend/src/components/ReportView.tsx` | Report (`/report`) | **Phase 10** | High-density clinical executive summary layout, print-optimized document view, FAISS cohort card. |
| **`LongitudinalChart`** | `frontend/src/components/LongitudinalChart.tsx` | History (`/history`) | **Phase 11** | Longitudinal trajectory line, 95% confidence ribbon Area, noise artifact outlier markers. |

---

## Page-Level Architecture Roadmap

| Page / Route | File Path | Phase Responsible | Core View Role / Dominant Visual Idea |
| :--- | :--- | :--- | :--- |
| **Home (`/`)** | `frontend/src/pages/Home/Home.tsx` | **Phase 06** | Cinematic editorial hero, single focal CTA, science trust manifesto. |
| **Record (`/record`)** | `frontend/src/pages/Record/Record.tsx` | **Phase 07** | Focused acoustic acquisition stage, live stream telemetry pane. |
| **Upload (`/upload`)** | `frontend/src/pages/Upload/Upload.tsx` | **Phase 08** | Drag-and-drop acoustic ingestion target, file validation feedback. |
| **Result (`/result`)** | `frontend/src/pages/Result/Result.tsx` | **Phase 09** | Probability gauge focal hero, progressive XAI biomarker disclosure. |
| **Report (`/report`)** | `frontend/src/pages/Report/Report.tsx` | **Phase 10** | Clinical decision-support dossier, formal regulatory disclaimer banner. |
| **History (`/history`)** | `frontend/src/pages/History/History.tsx` | **Phase 11** | Longitudinal multi-session trend analysis, cohort search drawer. |
| **Global Refinements & XAI** | Global Styles & Cross-cutting components | **Phase 12** | Complete cross-view polish, motion micro-interactions, responsive validation. |
