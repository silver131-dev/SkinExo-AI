# SkinExo Lab visual bible — VISUAL-V1

## Brand frame

**Brand:** SkinExo Lab
**Product:** SkinExo-AI
**Canonical title:** SkinExo-AI: A Context-Aware Extracellular-Vesicle Response Platform

SkinExo-AI uses a Korean medical-aesthetic visual language in service of evidence communication. The visual balance is fixed at **65% clinical/scientific, 25% Korean medical-aesthetic, and 10% luxury editorial**. EV context, evidence, the Response Atlas, retrieval, phenotype anchors, reliability, and provenance remain the protagonists.

The system should feel calm, precise, intelligent, and restrained. It must not resemble a skincare advertisement, cosmetic storefront, cyberpunk AI dashboard, or beauty efficacy campaign.

## Palette

| Token | Hex | Semantic use |
|---|---:|---|
| Pearl White | `#F7F5F1` | Primary canvas, open space, high-legibility card surfaces |
| Warm Ivory | `#EFEAE2` | Secondary surfaces, observed-null treatment, quiet section separation |
| Soft Blush | `#EEDDD9` | Mixed or discordant visual accent, human-context transitions used sparingly |
| Mist Mint | `#DDEBE5` | Active-positive accent and context confirmation surfaces |
| Powder Aqua | `#DCE9EC` | Active-negative accent, technical panels, retrieval comparison surfaces |
| Pale Lavender | `#E8E2EE` | Not-tested/unknown accent and phenotype-layer marker |
| Champagne | `#D9C8AE` | Premium highlight, rank-one edge, fine rules, never large body text |
| Deep Ink | `#173033` | Primary text, icons, borders, data labels, accessible contrast anchor |

White or ivory text is never placed on blush, mint, aqua, lavender, or champagne. Deep Ink remains the primary text color.

## Scientific state integrity

Color is a redundant cue. Every state also has a label, symbol, border treatment, or pattern.

| Scientific state | Symbol | Surface | Non-color cue |
|---|---:|---|---|
| `ACTIVE_POSITIVE` | `↑` | Mist Mint | Solid left border and exact state text |
| `ACTIVE_NEGATIVE` | `↓` | Powder Aqua | Double left border and exact state text |
| `OBSERVED_NULL` | `∅` | Warm Ivory | Dashed border and exact state text |
| `NOT_TESTED` | `◇` | Pale Lavender | Dotted border and exact state text |
| `UNKNOWN` | `?` | Pale Lavender | Question mark and exact state text |
| `DISCORDANT` | `↕` | Soft Blush | Split-direction icon and explicit label |
| `CONTEXT_DEPENDENT` | `◌` | Neutral glass | Context label and component-specific description |

An axis summary never replaces its component records. Phenotype anchors use `◆` and remain separate from transcriptomic NES. Reliability uses dimension cards rather than one combined score.

## Material language

- **Pearl:** broad Pearl White space with subtle warm gradients.
- **Frosted glass:** translucent cards with Deep Ink hairlines and soft blur.
- **Translucent membrane:** thin concentric circles or contours may suggest vesicle membranes.
- **Soft liquid:** gradients can move slowly between mint, aqua, blush, and lavender.
- **Skin luminosity:** limited to light behavior and surface softness, without product imagery.
- **Champagne metal:** a fine edge, rule, or rank accent only.

Avoid chrome, hard neon, black gaming panels, Matrix code, heavy HUD frames, dense glow, and cosmetic packaging motifs.

## Typography

- **Primary/UI:** Inter, Avenir Next, Segoe UI, Noto Sans, or system sans-serif.
- **Code/data:** SFMono-Regular, Consolas, or Liberation Mono.
- **Hero:** large, tight tracking, restrained weight; no all-caps title.
- **Eyebrow:** 11–12 px equivalent, uppercase, 0.14–0.18 em tracking.
- **Body:** at least 16 px equivalent in the Explorer and 24 px equivalent in 1080p video.
- **Data labels:** at least 13 px in UI and 22 px in video.

Hierarchy: brand eyebrow → product name → functional title → supporting line → scientific content.

## Layout and spacing

Base spacing follows `0.35 / 0.65 / 1 / 1.5 / 2.25 / 3.5 rem`. Use 16 px, 24 px, and 36 px as the common card and section gaps. Prefer one dominant focal block per viewport.

Card radii are 10 px for evidence rows, 16 px for scientific cards, and 24 px for hero surfaces. Rounded forms suggest membranes but should never make data look playful.

## Card hierarchy

1. Selected Context
2. P/M/E/A/I Response Profile
3. Retrieved Contexts
4. WHY explanation
5. Phenotype Evidence
6. Reliability
7. Provenance

Rank-one retrieval may use a Champagne top edge. Rank is still written as text. Unknown values remain visible as **Unknown / Not documented**.

## Motion

Preferred motion uses slow float, soft dissolve, glass slide, gentle parallax, and liquid morph. UI transitions use **600–900 ms** easing; the reference curve is `cubic-bezier(0.22, 1, 0.36, 1)` at 720 ms. Honor reduced-motion preferences.

Avoid glitch, neon pulse, rapid zoom, camera shake, flashing transitions, and HUD animation.

## Human imagery

Human skin macro or face imagery is optional and limited to the opening, one brief context transition, and the ending. It cannot sit behind dense scientific text, act as the product protagonist, or imply cosmetic or therapeutic efficacy. Prefer abstract skin-light gradients or clinical material close-ups when a human image adds no scientific meaning.

## Copy tone

Use calm, precise, evidence-led language. Prefer “response similarity,” “observed context,” “component evidence,” and “reliability dimension.” Avoid “revolutionary,” “transformative,” “future of beauty,” “breakthrough skincare,” and predictive language.

The scientific turn is preserved verbatim:

> The result was not broad concordance.
>
> It was something more informative:
> context dependence.

## Accessibility minimums

- Deep Ink is the default foreground on all pale surfaces.
- Text and symbols accompany every scientific color.
- Body copy remains readable at Kaggle page width.
- Key UI labels remain readable in a 1920 × 1080 recording after platform compression.
- No information appears only on hover.
- Reduced motion is supported in the Explorer theme.
- Blush-on-ivory and champagne-on-white are decorative combinations only, never body-text combinations.

## Implementation source

The code tokens live in `app/design_tokens.py`. The Streamlit presentation consumes them without importing scientific data or retrieval logic. Frozen numerical artifacts remain the source of all displayed values.
