# SkinExo-AI demo visual guide — VISUAL-V1

**Format:** six scenes, 30 keyframes, maximum 5:00
**Scientific source of truth:** `submission/demo_storyboard.md`
**Visual balance:** 65% clinical/scientific · 25% Korean medical-aesthetic · 10% luxury editorial

The six-scene structure consolidates the S2 storyboard’s live Explorer and evidence blocks into one uninterrupted product demonstration from 2:20–4:10. No scientific content, result, or claim boundary changes; the consolidation removes a visual interruption before phenotype and reliability are shown.

## Global production rules

- Master at 1920 × 1080; keep all essential text inside a 160 px horizontal safe area.
- Use Pearl White as the dominant canvas and Deep Ink as the dominant text color.
- Use project-generated figures and the live Explorer only.
- Use 600–900 ms soft dissolves, glass slides, slow float, or liquid morph.
- No glitch, fast zoom, flashing text, camera shake, or cyberpunk HUD.
- Human imagery is optional only in Scene 1, one brief transition, and the Scene 6 ending.
- Captions remain on screen long enough to read and never cover scientific values.

## Scene 1 — THE PROBLEM · 0:00–0:35

**Composition:** one question, three separated study cards, ample negative space.
**Background:** Pearl White with a faint Soft Blush edge light; optional abstract skin macro for no more than three seconds.
**Motion:** slow focus pull and gentle glass slide.
**Text hierarchy:** `SKINEXO LAB` eyebrow → project title → problem line.
**Scientific content:** EV studies are often isolated; EV source, dose, duration, recipient, and design differ.
**Transition:** the three study cards drift into a shared context grid.

| Keyframe | Time | Visual and motion | On-screen text / evidence |
|---:|---:|---|---|
| 01 | 0:00 | Pearl field; one translucent membrane slowly resolves | `SKINEXO LAB` |
| 02 | 0:05 | Product title dissolves in, centered | `SkinExo-AI` |
| 03 | 0:10 | Three study cards enter from separate directions | `EV source · recipient · dose · duration · design` |
| 04 | 0:20 | Cards remain separated; context fields highlight one at a time | `Most EV studies are analyzed in isolation.` |
| 05 | 0:29 | Cards align but retain distinct labels | `How can heterogeneous responses be compared without erasing context?` |

## Scene 2 — THREE EV CONTEXTS · 0:35–1:05

**Composition:** CTX001, CTX002, and CTX003 as equal clinical specimen cards.
**Background:** Pearl White to Powder Aqua gradient.
**Motion:** soft lateral card slide; no hierarchy based on desired result.
**Text hierarchy:** scene title → context ID → EV source → shared recipient and duration.
**Scientific content:** three study-level independent contexts; donor and EV-preparation independence are not implied.
**Transition:** context cards compress into the Response Atlas columns.

| Keyframe | Time | Visual and motion | On-screen text / evidence |
|---:|---:|---|---|
| 06 | 0:35 | Scene label and three empty card shells appear | `THREE EV CONTEXTS` |
| 07 | 0:40 | CTX001 fills with endothelial EV and 72 h | `CTX001 · GSE293186` |
| 08 | 0:46 | CTX002 fills with bone-marrow MSC sEV and 48 h | `CTX002 · GSE251807` |
| 09 | 0:52 | CTX003 fills with dermal fibroblast EV and 72 h | `CTX003 · GSE293956` |
| 10 | 0:59 | A common recipient line links the cards; limitation remains below | `Human dermal fibroblast recipient · study-level independence` |

## Scene 3 — THE SCIENTIFIC TURN · 1:05–1:45

**Composition:** one quiet statement at a time, followed by the five-axis outcome.
**Background:** Warm Ivory with a restrained Soft Blush to Pale Lavender liquid morph.
**Motion:** 850 ms dissolve; no dramatic impact effect.
**Text hierarchy:** scientific sentence → result status → five-axis summary.
**Scientific content:** broad concordance was not supported; context dependence is informative.
**Transition:** the five axis letters settle into the Atlas rows.

| Keyframe | Time | Visual and motion | On-screen text / evidence |
|---:|---:|---|---|
| 11 | 1:05 | The three context cards fade to outlines | `We tested whether a broad response repeated.` |
| 12 | 1:13 | First hero line appears alone | `The result was not broad concordance.` |
| 13 | 1:23 | First line softens; second line resolves below | `It was something more informative:` |
| 14 | 1:29 | `context dependence.` appears in Deep Ink with Champagne rule | `context dependence.` |
| 15 | 1:36 | P/M/E/A/I summary enters with text labels and state symbols | `P two-context only · M/A discordant · E null · I axis/context variant` |

## Scene 4 — THE RESPONSE ATLAS · 1:45–2:20

**Composition:** full `fig08_context_aware_response_atlas.png`, then two readable detail crops without altering the figure.
**Background:** Pearl White frame with Deep Ink caption.
**Motion:** slow 5% parallax and glass-window crop; never zoom past readable resolution.
**Text hierarchy:** `Response Atlas` → 3 contexts / 339 components / 1,017 records → axis/component distinction.
**Scientific content:** explicit active, observed-null, and not-tested states; phenotype and reliability remain separate.
**Transition:** the CTX003 Atlas column expands into the live Explorer.

| Keyframe | Time | Visual and motion | On-screen text / evidence |
|---:|---:|---|---|
| 16 | 1:45 | Atlas figure enters inside a frosted frame | `THREE-CONTEXT RESPONSE ATLAS` |
| 17 | 1:51 | Metric strip appears beneath the unchanged figure | `3 contexts · 339 components · 1,017 records` |
| 18 | 1:58 | Focus window moves to CTX003 P and E | `OBSERVED_NULL is evidence, not missingness.` |
| 19 | 2:05 | Focus moves to I across all contexts | `Same axis ≠ same component.` |
| 20 | 2:13 | CTX003 column gains a thin Champagne outline | `Open CTX003 in the Explorer` |

## Scene 5 — LIVE EXPLORER / RETRIEVAL · 2:20–4:10

**Composition:** live Streamlit recording; selected context first, retrieval as the visual centerpiece, WHY evidence underneath.
**Background:** the implemented Pearl White Explorer theme.
**Motion:** real scroll at a steady pace; pause after every click; avoid cursor circles or rapid pans.
**Text hierarchy:** CTX003 → response profile → retrieved contexts → WHY → phenotype/reliability.
**Scientific content:** frozen R1 similarity and explanations; phenotype and reliability are attached, not scored.
**Transition:** provenance closes and the architecture returns.

| Keyframe | Time | Visual and motion | On-screen text / evidence |
|---:|---:|---|---|
| 21 | 2:20 | Open Explorer at default CTX003; hold context card | `hDF EV → hDF · 10 µg/mL · 72 h` |
| 22 | 2:38 | Scroll to P/M/E/A/I; open P, then I | `P: observed null · I: active component evidence` |
| 23 | 2:58 | Scroll to retrieval cards; pause on both ranks | `CTX002 rank 1 +0.6053 · CTX001 rank 2 −0.2755` |
| 24 | 3:20 | Open WHY for CTX002; show shared then context-specific components | `9 shared active · directional concordance 1.000 · differences retained` |
| 25 | 3:47 | Continue to phenotype and reliability cards | `CCK-8 / scratch: 24 h · transcriptome: 72 h · donor/preparation uncertainty visible` |

## Scene 6 — EVIDENCE, RELIABILITY & VISION · 4:10–5:00

**Composition:** provenance, tests, offline boundary, then final product lockup.
**Background:** Pearl White with Mist Mint and Pale Lavender membrane light; optional brief human skin-light image only at the final transition.
**Motion:** slow glass slide to architecture, then a calm dissolve to the closing line.
**Text hierarchy:** evidence traceability → reproducibility → present boundary → future → closing statement.
**Scientific content:** 17/17 tests, public provenance, offline runtime, no predictive model, future work clearly labeled.
**Transition:** none; hold the final frame for two seconds.

| Keyframe | Time | Visual and motion | On-screen text / evidence |
|---:|---:|---|---|
| 26 | 4:10 | Expand Evidence Provenance in the live Explorer | `Dataset · checkpoint · method · MSigDB release` |
| 27 | 4:20 | Show test command/result and offline boundary | `17/17 tests pass · no raw data or internet at runtime` |
| 28 | 4:30 | Architecture figure returns, unchanged | `Atlas · retrieval · Explorer: implemented` |
| 29 | 4:40 | Future items appear in a separate Pale Lavender panel | `Future: more contexts · prospective validation · cargo integration` |
| 30 | 4:50 | Final lockup; membrane drifts slowly behind clear text | `SkinExo-AI does not assume a universal EV response. Context matters.` |

## Recording legibility gate

- CTX002 `+0.6053` and CTX001 `−0.2755` must remain readable after export.
- `Response similarity` must be visible; `prediction score` must never appear.
- The different-timepoint label must be visible with the CCK-8 and scratch anchors.
- Unknown donor and EV-preparation independence must be visible in the reliability scene.
- Use captions and test the final video at 720p playback before upload.
