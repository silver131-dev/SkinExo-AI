# SkinExo-AI VISUAL-V1 quality assurance

## Scope

VISUAL-V1 changes presentation code and guidance only. It does not modify Atlas data, retrieval functions, response states, evidence classifications, reliability records, or scientific claims.

## Visual system

- [x] Palette uses only Pearl White, Warm Ivory, Soft Blush, Mist Mint, Powder Aqua, Pale Lavender, Champagne, and Deep Ink.
- [x] Explorer styles are centralized in `app/design_tokens.py`.
- [x] Pearl White is the primary canvas and Deep Ink is the primary text color.
- [x] Frosted surfaces, soft membrane forms, and Champagne accents remain restrained.
- [x] No chrome, neon, cyberpunk, gaming, Matrix-code, or dense HUD treatment is used.
- [x] Science remains visually dominant over medical-aesthetic and editorial treatments.

## Scientific state integrity

- [x] Active-positive uses `↑` plus exact state text and a solid border.
- [x] Active-negative uses `↓` plus exact state text and a double border.
- [x] Observed-null uses `∅` plus exact state text and a dashed border.
- [x] Not-tested uses `◇` plus exact state text and a dotted border.
- [x] Unknown uses `?` plus exact state text.
- [x] Mixed/discordant evidence uses `↕` plus explicit wording.
- [x] Phenotype anchors use `◆` and remain outside transcriptomic similarity.
- [x] Reliability remains dimension-by-dimension with no combined score.

## Explorer hierarchy

- [x] Selected Context appears first.
- [x] P/M/E/A/I Response Profile appears second.
- [x] Retrieved Contexts are the main comparison focal point.
- [x] WHY explains shared, discordant, query-only, target-only, and observed-null differences.
- [x] Phenotype Evidence follows retrieval and remains a separate layer.
- [x] Reliability follows phenotype and retains unknown/limited states.
- [x] Provenance remains available in an expandable panel.
- [x] Unknown metadata displays as `Unknown / Not documented`.

## Human imagery and efficacy boundary

- [x] The Explorer and README use no human face or cosmetic product imagery.
- [x] The demo guide limits future human imagery to the opening, one brief transition, and ending.
- [x] No before/after imagery is authorized.
- [x] No cosmetic efficacy, therapeutic efficacy, angiogenesis, or wound-healing prediction is implied.

## Accessibility

- [x] Deep Ink remains the foreground for all pale palette surfaces.
- [x] Scientific states use text, icons, and border patterns in addition to color.
- [x] No required evidence appears only on hover.
- [x] Reduced-motion preferences disable long transitions.
- [x] UI body and metric text remain readable at common desktop widths.
- [x] The demo guide sets 1080p safe areas and minimum playback checks.
- [ ] Final video readability at 720p playback — deferred until DEMO-V1 recording.

## Competition figure audit

| Figure | Visual status | Decision |
|---|---|---|
| `fig08_context_aware_response_atlas.png` | Clear axis labels, explicit state text, phenotype marker, reliability note | Preserve original |
| `fig09_skinexo_platform_architecture.png` | Clear implemented labels and predictive-AI boundary | Preserve original |
| `fig10_context_retrieval.png` | Readable rank, similarity, shared/discordant evidence, limitation line | Preserve original |
| `fig11_context_similarity_matrix.png` | Values printed in every cell and descriptive limitation in subtitle | Preserve original |

Presentation copies were not needed. The original project-owned figures remain unchanged, avoiding any risk of altering plotted values or scientific meaning. Kaggle and video framing rules are defined in the visual guides.

## README and Kaggle

- [x] README preserves the S2 scientific order and canonical pitch.
- [x] README adds restrained hierarchy, a concise metric strip, and figure captions.
- [x] README references only project-owned figures.
- [x] Kaggle guidance defines hero, divider, figure, caption, and thumbnail treatment.
- [x] Kaggle guidance prohibits paper-owned imagery and predictive labels.

## Motion and demo

- [x] Six scenes are locked.
- [x] Thirty keyframes are locked.
- [x] Motion is limited to slow float, dissolve, glass slide, parallax, and liquid morph.
- [x] Scene 3 preserves the scientific-turn wording.
- [x] Scene 5 preserves CTX003 → CTX002 `+0.6053` → WHY → phenotype/reliability.
- [x] Total planned duration is 5:00 maximum.
- [ ] Final video export and caption review — deferred to DEMO-V1.

## Automated integrity checks

- [x] Existing test suite passes: 17/17.
- [x] CTX003 retrieves CTX002 first at `+0.6053` and CTX001 second at `−0.2755`.
- [x] Atlas remains 3 contexts, 339 components, and 1,017 response records.
- [x] Frozen activity counts remain 139 active-positive, 19 active-negative, 852 observed-null, 7 not-tested, and 0 unknown.

## Decision

**VISUAL-V1 presentation system: PASS.** Final rendered-video accessibility remains a DEMO-V1 production check and does not alter the visual-system decision.
