# SkinExo-AI EXPLORER-A2 — Product Demo Mode

## Objective

Transform the Explorer from a metadata-first research report into a product narrative that lets a first-time judge identify what happened in CTX003, which observed context is most similar, why it was retrieved, and what evidence and limitations bound the interpretation. A2 is presentation-only; it does not change F2 science or R1 retrieval.

## User-review problem

The A1 audit found the scientific content complete but the hierarchy inverted. Nine metadata cards and a dense limitation warning preceded the biological result; schema enums dominated axis cards; component tables appeared before retrieval; the core WHY explanation was closed; phenotype and reliability were long-form; and the golden path required report-like scrolling.

The audited A1 sections were classified as follows:

- **Product-critical:** context selection, P/M/E/A/I states, R1 ranking and explanations, phenotype separation, reliability dimensions, and provenance.
- **Advanced / research:** complete metadata, full component explorer, all retrieval metrics, axis tables, phenotype records, reliability records, and technical provenance.
- **Redundant in Demo Mode:** repeated context identity, nine top-level metadata cards, the dominant limitation paragraph, enum-first status labels, component tables before retrieval, and repeated metric blocks.

## Design decisions

A2 changes the hierarchy to finding → retrieval → explanation → evidence → details. It uses the same `ExplorerData`, F2 Atlas, and R1 retrieval functions as A1. A restrained journey strip communicates Context → Response → Retrieve → Explain → Evidence without restricting navigation. The global palette, calm clinical tone, color-independent state patterns, and VISUAL-V1 identity are preserved.

The installed official Streamlit development skill guided the use of native containers, a segmented mode control, URL-bound mode/context state, compact expanders, native AppTest coverage, and project-level Streamlit theming. Existing custom CSS remains because the project explicitly requires a branded presentation system.

## Demo Mode

Demo Mode is the default and opens on CTX003. The 1920×1080 first screen contains the product identity, selected context, recipient, essential experimental conditions, Biological Summary, full Response Signature, observed-null axes, and a visible cue toward retrieval. Secondary metadata is available through Experimental details.

The continuous golden path is:

1. CTX003 context hero.
2. Biological Summary.
3. Response Signature / Primary Findings.
4. CTX002 retrieval hero with response similarity `+0.6053`.
5. WHY THIS MATCH, open by default.
6. Evidence Snapshot.
7. Reliability Snapshot.
8. Advanced research details and provenance on demand.

## Research Mode

Research Mode preserves the A1 interface and access to complete context metadata, five-axis summaries, component evidence, retrieval rankings, full explanations, phenotype anchors, all reliability dimensions, and provenance. Response Atlas and Context Similarity remain separate deeper views. Internal enums remain available where useful for technical traceability, but no longer dominate the primary user journey.

## Biological Summary

`app/presentation.py` implements a deterministic summary generator over structured runtime data. For CTX003 it reports the inflammatory / immune-signaling response as the largest active response family with 27 active components; migration and vascular/endothelial interaction as active; proliferation and ECM remodeling as observed null; and CTX002 as the closest observed context.

The summary contains no stochastic step, LLM, external API, causal language, phenotype inference, predictive claim, or aggregate confidence score.

## Response Signature

The five-row signature reverses the A1 hierarchy so human-readable biological names precede P/M/E/A/I identifiers. It displays:

- Proliferation · P · Observed null · 0 active.
- Migration · M · Positive · 4 active.
- ECM Remodeling · E · Observed null · 0 active.
- Vascular / Endothelial Interaction · A · Positive · 1 active.
- Immune Signaling · I · Positive · 27 active.

Text, symbols, counts, and border patterns encode state in addition to color. Observed null and not tested remain distinct.

## Retrieval Hero

The primary retrieved context is presented as a product moment:

- CTX002 · Bone-Marrow MSC sEV → Human Dermal Fibroblast.
- Response similarity `+0.6053`.
- 9 shared active components.
- 100% directional agreement.
- Active-union similarity `+0.8563`.

Cosine values remain decimals. Only directional concordance is shown as a percentage because it is explicitly a proportion. Retrieval is labeled descriptive among observed contexts, not predictive.

## WHY THIS MATCH

The Demo Mode explanation is visible by default and uses the existing R1 explanation object. It shows a deterministic sentence for nine shared active components with the same direction, the stored highest axis-level NES agreement, actual shared component names from the frozen component universe, query-specific activity, target-specific activity, and active/observed-null differences.

The interface explicitly notes that agreement at a broad response axis does not imply conservation of every active component. A compact drill-down exposes the complete R1 component groups and axis-level metrics.

## Evidence Snapshot

Transcriptomic evidence, phenotype anchors, and reliability remain separate. For CTX003 the snapshot makes the timing mismatch immediately visible:

- Transcriptomic response: 72 h.
- CCK-8 phenotype anchor: 24 h.
- Scratch-assay phenotype anchor: 24 h.

Phenotype anchors are labeled explanatory and not causal; they do not enter retrieval similarity.

## Reliability Snapshot

Nine high-priority dimensions are visible in a compact grid, with all thirteen available in the detailed view. The panel preserves the stored states and details for study independence, recipient donor, EV preparation, batch, pairing, control definition, sample QC, model diagnostics, and phenotype timing. Unknown and limited evidence are intentionally visible. No combined reliability category, percentage, or score is computed.

## Scientific safeguards

- EXP001, EXP002, EXP003, DESeq2, and GSEA were not rerun.
- Atlas values, response components, masks, classifications, provenance, and frozen claims were not changed.
- R1 remains the only retrieval implementation used by the UI.
- `OBSERVED_NULL` remains tested evidence and is not merged with `NOT_TESTED`.
- Phenotype evidence remains outside transcriptomic similarity.
- The broad universal EV-response claim remains not supported.
- Frozen framework distinctions remain accessible in Response Atlas and Research Mode.
- No predictive AI, LLM, agent, confidence score, evidence score, radar chart, new context, or new scientific axis was added.

## Accessibility

The primary state presentation uses text, symbols, active-component counts, and distinct solid/dashed/dotted/double border patterns. Contrast follows the Deep Ink / Pearl White palette. Controls retain visible labels and keyboard-compatible native Streamlit behavior. The 1920×1080 captures have no horizontal overflow or clipped primary similarity value.

## Offline behavior

Normal Explorer runtime remains fully offline. It requires tracked metadata, F2 manifests, and R1 artifacts only. Raw GEO data, processed count matrices, licensed PDFs, internet access, external APIs, and the locally installed Streamlit skill are not runtime dependencies. A2 adds no Python runtime dependency.

## Tests

The suite now contains 22 passing tests. New tests cover the exact CTX003 states and active counts, deterministic summary language, CTX002 ranking, `+0.6053`, `+0.8563`, nine shared active components, `1.000` directional concordance, observed-null/not-tested display separation, and absence of an aggregate confidence score.

The A2 validator also checks AppTest rendering, frozen Atlas totals, claim-language exclusions, offline artifact closure, and the unchanged R1 version.

## Numerical regression

Validated values:

- 3 contexts, 339 components, 1,017 response records.
- 139 active positive, 19 active negative, 852 observed null, 7 not tested.
- CTX003 P/M/E/A/I active counts: 0 / 4 / 0 / 1 / 27.
- CTX003 → CTX002: `+0.6053`.
- CTX003 → CTX001: `-0.2755`.
- Active-union similarity: `+0.8563`.
- Shared active components: 9.
- Directional concordance: `1.000`.

No unexpected numerical change was detected.

## Known limitations

The Atlas contains only three observed contexts. Similarity is descriptive and has no predictive validation. Donor independence, EV-preparation independence, pairing, and control definition remain unknown for CTX003; batch, sample QC, model diagnostics, annotation certainty, phenotype timing, cross-context replication, and pathway evidence remain limited in their recorded dimensions. The first-screen and scroll experience is optimized for 1920×1080 desktop, not mobile. Streamlit's minimal header area remains part of the page, although developer, Deploy, and onboarding controls are absent in the captured Demo Mode.

## User-review items

User review is required before A2 is frozen for video recut. Review:

- landing screen hierarchy and first-screen comprehension;
- Response Signature wording and density;
- Retrieval Hero prominence;
- visible WHY explanation and shared-component names;
- phenotype timing separation;
- reliability grid readability;
- Research Mode continuity;
- the A2 contact sheet at `submission/demo/production/review/EXPLORER_A2_CONTACT_SHEET.png`.

A2 passes implementation and validation gates but remains **REVIEW REQUIRED** for visual approval before DEMO-V2 production.
