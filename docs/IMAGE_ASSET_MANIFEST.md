# Image Asset Strategy & Delivery Manifest

**Project:** Parkinson's Voice Screening & Clinical Decision Support Platform  
**Design Direction:** Midnight Clinical Intelligence (Cinematic Editorial AI-Research Photography)

---

## 1. Universal Image Prompt Style Suffix (Locked In)

Every generated visual asset follows this exact style prompt baseline:

> *Style: premium AI-research/medical-technology editorial photography blended with restrained scientific visualization elements. Color grade: primary background #080A0A, secondary #0E1110 dark charcoal; primary technology accent teal #5D9A9C, secondary teal #75B1B2, soft cyan #8EC4C1; warm analytical accent amber #D99A5B, secondary amber #E2A66A used sparingly as a highlight, never dominant. Lighting: soft volumetric light, single or dual directional source, restrained. Depth: strong cinematic depth of field, layered atmosphere. Detail: fine scientific/technical detail, subtle particles, controlled contrast, premium editorial composition, high-end AI research aesthetic, subtle film grain where appropriate. Strictly exclude: any text, logo, watermark, UI element, button, readable label, human hands, generic human figures, generic doctors, hospital stock photography, brain imagery, robots, humanoid AI figures, cyberpunk elements, neon rainbow gradients, gaming aesthetics, cheap/plastic 3D render look.*

---

## 2. Master Image Asset Manifest (9 Assets: A–I)

| ID | Asset Filename | Target Page | Redesign Phase | Aspect Ratio | Concept & Composition Summary | Conditional Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A** | `homepage_hero.webp` | Home (`/`) | **Phase 06** | `16:9` / `21:9` | Coherent vocal phonation acoustic wavefront ribbons propagating through dark volumetric space with soft teal illumination. | Standard |
| **B** | `how_it_works_acoustic.webp` | Home (`/`) | **Phase 06** | `16:9` | Multi-resolution vocal tract frequency resonance bands transitioning into computational tensor tokens. | Standard |
| **C** | `result_acoustic_embedding.webp` | Result (`/result`) | **Phase 09** | `16:9` | High-dimensional latent acoustic manifold showing clustered feature vectors and golden analytical centroid focal ray. | Standard |
| **D** | `result_attention_timeline.webp` | Result (`/result`) | **Phase 09** | `16:9` | Temporal sequence self-attention graph with subtle glowing multi-head token nodes across phonatory time slices. | Standard |
| **E** | `result_gradcam_xai.webp` | Result (`/result`) | **Phase 09** | `16:9` | ConvNeXt-V2 visual spectrogram class activation colormap with spectro-temporal gradient illumination. | Standard |
| **F** | `result_faiss_retrieval.webp` | Result / Report | **Phase 09** | `16:9` | Vector similarity k-nearest neighbor retrieval graph highlighting patient voice embedding to reference cohort. | **Conditional** (Surfaced in XAI/Report cohort evidence) |
| **G** | `home_clinical_insight.webp` | Home (`/`) | **Phase 06** | `16:9` | Precision bio-acoustic resonance analysis showing subharmonic perturbation detection in clean laboratory lighting. | Standard |
| **H** | `history_longitudinal.webp` | History (`/history`) | **Phase 11** | `16:9` | Longitudinal multi-encounter vocal stability trajectory ribbons over time with confidence bounds. | Standard |
| **I** | `footer_atmosphere.webp` | BaseLayout Footer | **Phase 12** | `21:9` | Subdued, deep obsidian ambient field with delicate floating teal luminescence and distant scientific optical horizon. | Standard |

---

## 3. Technical Delivery & Optimization Standards

All 9 images must adhere to the following technical delivery pipeline:

1. **Primary Format:** **WebP** (fallback to progressive JPEG where WebP is unavailable).
2. **Responsive Resolution Targets (`srcset`):**
   * Mobile: `480w`
   * Tablet: `768w`
   * Desktop: `1200w`
   * High-DPI / Ultra-wide: `1920w`
3. **File Size Budget:** **Target under 300 KB** at the largest served resolution (`1920w`), with sub-100KB for mobile breakpoints.
4. **Loading Strategy:**
   * **Above-the-Fold (Asset A - Hero):** Preloaded via `<link rel="preload" as="image">` with `loading="eager"` and `fetchpriority="high"`.
   * **Below-the-Fold (Assets B–I):** Native browser `loading="lazy"` and `decoding="async"`.
5. **Alt-Text Policy:**
   * Every image must include a specific, plain-language description of its visual and scientific contents.
   * Generic descriptions like *"image"*, *"graphic"*, or empty strings are strictly prohibited.

---

## 4. Scaffolded Asset Directory Structure

```text
frontend/public/assets/imagery/
├── home/
│   ├── homepage_hero.webp
│   ├── how_it_works_acoustic.webp
│   └── home_clinical_insight.webp
├── result/
│   ├── result_acoustic_embedding.webp
│   ├── result_attention_timeline.webp
│   ├── result_gradcam_xai.webp
│   └── result_faiss_retrieval.webp
├── history/
│   └── history_longitudinal.webp
└── footer/
    └── footer_atmosphere.webp
```
