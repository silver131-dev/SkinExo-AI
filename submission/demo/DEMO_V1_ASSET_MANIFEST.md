# SkinExo-AI DEMO-V1 asset manifest

## Status vocabulary

- **READY:** exists and passed provenance/readability review.
- **SPEC READY:** specification is frozen; production file does not yet exist.
- **RECORDING REQUIRED:** must be captured from the committed Explorer.
- **OPTIONAL READY:** available as a backup, but not required in the locked cut.

## Existing project assets

| Scene / keyframe | Class | Filename | Source | Copyright status | Needed | Ready |
|---|---|---|---|---|---|---|
| S4 · KF18 | EXISTING_PROJECT_ASSET | `submission/figures/fig08_context_aware_response_atlas.png` | F2 Atlas artifacts; `experiments/framework/02_build_atlas.py` | Project-generated; underlying data retain source terms | YES | READY |
| S6 · KF28 | EXISTING_PROJECT_ASSET | `submission/figures/fig09_skinexo_platform_architecture.png` | Project release artifacts; `experiments/release/02_update_public_architecture_figure.py` | Project-generated | YES | READY |
| Backup for S5 | EXISTING_PROJECT_ASSET | `submission/figures/fig10_context_retrieval.png` | R1 retrieval artifacts; `experiments/retrieval/01_build_retrieval.py` | Project-generated | NO — live Explorer preferred | OPTIONAL READY |
| Backup transition | EXISTING_PROJECT_ASSET | `submission/figures/fig11_context_similarity_matrix.png` | R1 pairwise matrix; `experiments/retrieval/01_build_retrieval.py` | Project-generated | NO — live retrieval cards preferred | OPTIONAL READY |

No publication-owned figure, licensed PDF image, or paper screenshot is permitted.

## Explorer recording

| Scene / keyframe | Class | Filename | Source | Copyright status | Needed | Ready |
|---|---|---|---|---|---|---|
| S5–S6 · KF21–KF26 | EXPLORER_RECORDING | `scene05_explorer_ctx003_master_1920x1080.mov` | Real Streamlit app at the frozen VISUAL-V1 commit | Project-generated UI recording | YES | RECORDING REQUIRED |

One continuous master recording is required. Edit selects may be duplicated from that master without counting as new source assets.

## New motion graphics

| Scene / keyframe | Class | Filename | Source | Copyright status | Needed | Ready |
|---|---|---|---|---|---|---|
| S1 · KF01–KF05 | NEW_MOTION_GRAPHIC | `mg01_problem_context_cards.mov` | Built from project design tokens and text lock | Original project production | YES | SPEC READY |
| S2 · KF06–KF10 | NEW_MOTION_GRAPHIC | `mg02_three_context_cards.mov` | Context metadata; project vector cards | Original project production | YES | SPEC READY |
| S3 · KF11–KF15 | NEW_MOTION_GRAPHIC | `mg03_scientific_turn.mov` | Frozen F2 interpretations and hero lines | Original project production | YES | SPEC READY |
| S4 · KF16–KF20 | NEW_MOTION_GRAPHIC | `mg04_atlas_representation.mov` | Atlas schema plus unchanged fig08 | Original project production | YES | SPEC READY |
| S6 · KF27–KF29 | NEW_MOTION_GRAPHIC | `mg05_evidence_future.mov` | Test results, fig09, FUTURE concepts | Original project production | YES | SPEC READY |
| S6 · KF30 | NEW_MOTION_GRAPHIC | `mg06_final_lockup.mov` | Canonical title and frozen GitHub URL | Original project production | YES | SPEC READY |

## New generated visual plates

| Scene / keyframe | Class | Filename | Source | Copyright status | Needed | Ready |
|---|---|---|---|---|---|---|
| S1 · KF01 | NEW_GENERATED_VISUAL | `gv01_biological_skin_membrane_16x9.png` | Prompt GV01 in `DEMO_V1_GENERATIVE_VISUAL_PROMPTS.md` | Must be newly generated; no artist imitation | YES | SPEC READY |
| S1 · KF02 | NEW_GENERATED_VISUAL | `gv02_translucent_ev_membrane_16x9.png` | Prompt GV02 | Must be newly generated; no external logo or text | YES | SPEC READY |
| S2 · KF06–KF10 | NEW_GENERATED_VISUAL | `gv03_three_ev_context_streams_16x9.png` | Prompt GV03 | Must be newly generated; abstract scientific concept | YES | SPEC READY |
| S6 · KF29–KF30 | NEW_GENERATED_VISUAL | `gv04_cargo_response_phenotype_16x9.png` | Prompt GV04 | Must be newly generated; FUTURE concept only | YES | SPEC READY |

Generated plates are backgrounds or conceptual motifs. They may not contain scientific labels, data values, faces as protagonists, treatment outcomes, or efficacy implications. All labels are added as project-owned motion graphics.

## Text-only assets

| Scene / keyframe | Class | Filename | Source | Copyright status | Needed | Ready |
|---|---|---|---|---|---|---|
| All | TEXT_ONLY | `DEMO_V1_NARRATION.md` | S2 narrative contract and claim dictionary | Project-authored | YES | READY |
| All | TEXT_ONLY | `DEMO_V1_CAPTIONS.md` | Verbatim narration segmentation | Project-authored | YES | READY |
| All | TEXT_ONLY | `DEMO_V1_ONSCREEN_TEXT.md` | Frozen keyframe copy | Project-authored | YES | READY |
| All | TEXT_ONLY | `DEMO_V1_KEYFRAMES.md` | D1 keyframe lock | Project-authored | YES | READY |
| S5 | TEXT_ONLY | `EXPLORER_RECORDING_PLAN.md` | A1 UI and VISUAL-V1 hierarchy | Project-authored | YES | READY |
| All | TEXT_ONLY | `DEMO_V1_MOTION_PLAN.md` | VISUAL-V1 motion language | Project-authored | YES | READY |
| All | TEXT_ONLY | `DEMO_V1_EDIT_PLAN.md` | D1 timeline | Project-authored | YES | READY |

## Audio policy

Narration and captions are required. Music and sound effects are not required assets. If music is added later, it must be an original or properly licensed instrumental bed with documented terms, no vocals, and no scientific implication; otherwise use clean narration only.

## Counts

- Existing project assets reviewed: **4**
- Existing project assets required in the locked cut: **2**
- Explorer master recordings required: **1**
- New motion graphics required: **6**
- New generated visual plates required: **4**
- Required text-only production assets: **7**
