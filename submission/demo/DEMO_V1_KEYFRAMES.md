# SkinExo-AI DEMO-V1 keyframe lock

**Count:** exactly 30 keyframes — five per scene.
**Runtime:** 4:55.
**Claim vocabulary:** `SUPPORTED`, `SUPPORTED_WITH_LIMITATIONS`, `NOT_SUPPORTED`, `FUTURE`.

## Scene 1 — THE PROBLEM · 0:00–0:35

| ID | Timestamp | Duration | Visual | On-screen text | Voiceover cue | Motion | Transition | Source artifact | Scientific claim | Claim status |
|---|---:|---:|---|---|---|---|---|---|---|---|
| KF01 | 0:00 | 0:06 | Pearl field with one translucent EV membrane; optional non-identifying skin-light texture | `SKINEXO LAB` | “Extracellular vesicles carry biological signals between cells…” | Slow float | Soft dissolve from black | New motion graphic; `SKINEXO_VISUAL_BIBLE.md` | EVs carry biological signals between cells. | SUPPORTED |
| KF02 | 0:06 | 0:06 | EV particles cross a soft cell-membrane boundary | `Biological signals, different contexts` | “…but their effects are usually studied one experiment at a time.” | Gentle parallax | Glass slide | New motion graphic; narrative contract | EV studies are commonly analyzed in isolation. | SUPPORTED |
| KF03 | 0:12 | 0:08 | Five evidence labels orbit three separated study cards | `EV source · recipient · dose · time` | “EV source, recipient cell, dose, duration, and study design can all differ.” | Slow float | Soft dissolve | `S2_NARRATIVE_CONTRACT.md` | Experimental context includes the displayed design dimensions. | SUPPORTED |
| KF04 | 0:20 | 0:08 | Study cards remain visually separated by translucent dividers | `Evidence remains fragmented` | “That makes response evidence difficult to compare without losing the context…” | Glass slide | Liquid morph | Narrative contract | Heterogeneous study context complicates comparison. | SUPPORTED |
| KF05 | 0:28 | 0:07 | SkinExo-AI question appears beside context/response symbols | `Which responses truly repeat?` | “SkinExo-AI asks a focused question…” | Soft dissolve | Cards align into grid | `S2_NARRATIVE_CONTRACT.md` | The platform compares conserved, dependent, absent, and discordant responses. | SUPPORTED |

## Scene 2 — THREE EV CONTEXTS · 0:35–1:05

| ID | Timestamp | Duration | Visual | On-screen text | Voiceover cue | Motion | Transition | Source artifact | Scientific claim | Claim status |
|---|---:|---:|---|---|---|---|---|---|---|---|
| KF06 | 0:35 | 0:05 | Three equal frosted context-card shells | `Three verified study contexts` | “We structured three public, study-level independent contexts.” | Glass slide | Soft dissolve | `skinexo_context_features.csv` | Three verified study-level independent contexts are represented. | SUPPORTED_WITH_LIMITATIONS |
| KF07 | 0:40 | 0:06 | CTX001 card fills with endothelial EV and recipient labels | `CTX001 · Endothelial EV · 72 h` | “CTX001 uses endothelial-cell-derived EVs…” | Slow data reveal | Horizontal slide | `skinexo_context_features.csv` | CTX001 source, recipient class, and duration. | SUPPORTED |
| KF08 | 0:46 | 0:06 | CTX002 card fills with bone-marrow MSC sEV labels | `CTX002 · MSC sEV · 48 h` | “CTX002 uses bone-marrow mesenchymal-stromal-cell small EVs…” | Slow data reveal | Horizontal slide | `skinexo_context_features.csv` | CTX002 source, recipient class, and duration. | SUPPORTED |
| KF09 | 0:52 | 0:07 | CTX003 card fills with hDF EV labels | `CTX003 · hDF EV · 72 h` | “CTX003 uses human dermal-fibroblast-derived EVs…” | Slow data reveal | Horizontal slide | `skinexo_context_features.csv` | CTX003 source, recipient class, and duration. | SUPPORTED |
| KF10 | 0:59 | 0:06 | Shared recipient line links cards; design differences remain visible | `Shared recipient class ≠ identical design` | “These studies share a recipient biological class, but they are not experimentally identical.” | Gentle line draw | Compress into axes | Context features; reliability metadata | Study independence does not establish donor or EV-preparation replication. | SUPPORTED_WITH_LIMITATIONS |

## Scene 3 — THE SCIENTIFIC TURN · 1:05–1:45

| ID | Timestamp | Duration | Visual | On-screen text | Voiceover cue | Motion | Transition | Source artifact | Scientific claim | Claim status |
|---|---:|---:|---|---|---|---|---|---|---|---|
| KF11 | 1:05 | 0:08 | P/M/E/A/I letters enter with neutral outlines and labels | `Test: does a broad response repeat?` | “We first tested whether a broadly reproducible EV-associated response existed.” | Slow float | Soft dissolve | `EXP003_VALIDATION_ENDPOINTS.md` | Broad response conservation was tested prospectively. | SUPPORTED |
| KF12 | 1:13 | 0:10 | All secondary elements recede; hero line appears alone | `The result was not broad concordance.` | Exact same sentence | 850 ms dissolve | Hold, no flourish | F2 manifest; EXP003-C4 | A broad universal response is not supported. | NOT_SUPPORTED |
| KF13 | 1:23 | 0:06 | Champagne rule reveals the second hero line | `Something more informative:` | “It was something more informative…” | Soft dissolve | Liquid morph | F2 report | The observed pattern is context-aware rather than universal. | SUPPORTED |
| KF14 | 1:29 | 0:07 | `context dependence.` resolves in Deep Ink | `context dependence.` | “…context dependence.” | Slow focus | Axis cards return | F2 manifest | Multiple axes vary across contexts. | SUPPORTED |
| KF15 | 1:36 | 0:09 | Five labeled axis cards show text, icons, and border patterns | `P two-context · M/A discordant · E null · I variant` | Narration names the frozen P/M/E/A/I interpretations. | Gentle stagger | Cards settle into Atlas rows | `framework_f2_atlas.json`; `fig08` | Frozen three-context interpretations for P/M/E/A/I. | SUPPORTED |

## Scene 4 — THE RESPONSE ATLAS · 1:45–2:20

| ID | Timestamp | Duration | Visual | On-screen text | Voiceover cue | Motion | Transition | Source artifact | Scientific claim | Claim status |
|---|---:|---:|---|---|---|---|---|---|---|---|
| KF16 | 1:45 | 0:06 | Context → Axis → Component pipeline assembles | `Context → Axis → Component` | “That result motivated the Response Atlas.” | Glass slide | Soft dissolve | `ATLAS_SCHEMA.md`; `fig09` | The Atlas represents evidence at context, axis, and component levels. | SUPPORTED |
| KF17 | 1:51 | 0:07 | Metric strip appears over a restrained Atlas motif | `3 contexts · 339 components · 1,017 records` | Narration states the three frozen Atlas counts. | Number fade-in | Parallax to fig08 | `framework_f2_atlas.json` | Frozen Atlas size. | SUPPORTED |
| KF18 | 1:58 | 0:07 | Unchanged fig08 appears in Pearl White frame | `Direction · evidence · phenotype · reliability` | “Each record links context, axis, component…” | Gentle parallax | Frosted focus window | `fig08_context_aware_response_atlas.png` | Atlas records preserve statistical and evidence dimensions. | SUPPORTED |
| KF19 | 2:05 | 0:08 | Two cards compare `OBSERVED_NULL` and `NOT_TESTED` using text and patterns | `OBSERVED_NULL ≠ NOT_TESTED` | Narration defines both states. | Glass split | Soft dissolve | `ATLAS_SCHEMA.md`; response atlas long table | Observed null and not tested have distinct semantics. | SUPPORTED |
| KF20 | 2:13 | 0:07 | CTX003 column expands toward an Explorer window | `Missing evidence is never biological zero` | “Neither is silently converted to biological zero.” | Liquid morph | Match cut to live UI | `RESPONSE_REPRESENTATION.md` | Retrieval preserves explicit tested masks. | SUPPORTED |

## Scene 5 — LIVE EXPLORER · 2:20–3:55

| ID | Timestamp | Duration | Visual | On-screen text | Voiceover cue | Motion | Transition | Source artifact | Scientific claim | Claim status |
|---|---:|---:|---|---|---|---|---|---|---|---|
| KF21 | 2:20 | 0:15 | Real Explorer opens at default CTX003; context card held steady | `CTX003 · hDF EV → hDF` | “Now we open the offline Explorer at its default query, CTX003.” | Real UI; no added zoom | Slow scroll | Live `app/streamlit_app.py` | Default context and displayed metadata come from tracked artifacts. | SUPPORTED |
| KF22 | 2:35 | 0:17 | Real P/M/E/A/I overview, then component evidence | `Observed nulls remain visible` | Narration describes the CTX003 response profile. | Real scroll with pauses | Scroll to retrieval | Live Explorer; axis summary | CTX003 P/E null and M/A/I active structure. | SUPPORTED |
| KF23 | 2:52 | 0:18 | Real retrieval cards; both ranks fully readable | `CTX002 +0.6053 · CTX001 −0.2755` | Narration gives the two frozen response similarities and boundary. | Cursor rests; no overlay animation | Click CTX002 WHY | Live Explorer; `retrieval_r1.json` | CTX003 retrieval ranking and mask-aware NES cosine values. | SUPPORTED_WITH_LIMITATIONS |
| KF24 | 3:10 | 0:22 | Real WHY panel shows shared, discordant, and context-specific sections | `9 shared active · concordance 1.000` | Narration gives shared-active, directional, and active-union evidence. | Controlled scroll | Continue down page | Live Explorer; `r1_explanations.json` | CTX002–CTX003 explanation and active-union `+0.8563`. | SUPPORTED_WITH_LIMITATIONS |
| KF25 | 3:32 | 0:23 | Real phenotype cards followed by reliability dimension cards | `24 h phenotype · 72 h transcriptome` | Narration separates CCK-8/scratch anchors and reliability from similarity. | Slow scroll; hold unknown fields | Soft dissolve to provenance | Live Explorer; phenotype and reliability tables | Phenotype time mismatch and donor/preparation uncertainty remain visible and unscored. | SUPPORTED_WITH_LIMITATIONS |

## Scene 6 — EVIDENCE, RELIABILITY & VISION · 3:55–4:55

| ID | Timestamp | Duration | Visual | On-screen text | Voiceover cue | Motion | Transition | Source artifact | Scientific claim | Claim status |
|---|---:|---:|---|---|---|---|---|---|---|---|
| KF26 | 3:55 | 0:12 | Real Evidence Provenance panel shows dataset, checkpoint, method, release | `Evidence remains traceable` | “Every displayed interpretation traces to a public dataset…” | Real UI hold | Glass slide | Live Explorer; provenance metadata | Displayed interpretations retain provenance. | SUPPORTED |
| KF27 | 4:07 | 0:12 | Test result and offline dependency boundary on a clean technical card | `17/17 tests · offline runtime` | Narration states test and runtime boundary. | Soft dissolve | Architecture enters | Test suite; `explorer_a1.json` | Tests pass and normal Explorer runtime is offline. | SUPPORTED_WITH_LIMITATIONS |
| KF28 | 4:19 | 0:12 | Unchanged architecture figure with implemented stages highlighted | `Atlas · retrieval · Explorer: implemented` | “SkinExo-AI version zero point three is a research-support platform…” | Gentle parallax | Pale Lavender future panel | `fig09_skinexo_platform_architecture.png` | Current system boundary; predictive AI is not implemented. | SUPPORTED |
| KF29 | 4:31 | 0:12 | Concept-only cargo → response → phenotype path and Organ-on-Chip outline labeled FUTURE | `FUTURE · cargo → response → phenotype` | Narration describes future cargo, prospective, and Organ-on-Chip work. | Slow line draw | Soft dissolve | Claim dictionary; generative prompt pack | Cargo integration and Organ-on-Chip are future directions. | FUTURE |
| KF30 | 4:43 | 0:12 | Final SkinExo-AI lockup with minimal EV membrane motif and optional GitHub URL | `SkinExo-AI · Context matters.` | Canonical closing narration. | Slow float; final two seconds static | End | Narrative contract; frozen GitHub URL | SkinExo-AI retrieves and explains context-dependent patterns without assuming universality. | SUPPORTED |

## Count check

- Scene 1: KF01–KF05 — 5
- Scene 2: KF06–KF10 — 5
- Scene 3: KF11–KF15 — 5
- Scene 4: KF16–KF20 — 5
- Scene 5: KF21–KF25 — 5
- Scene 6: KF26–KF30 — 5
- **Total: 30**
