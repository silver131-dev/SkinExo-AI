# SkinExo-AI S2 narrative contract

## Canonical identity

**Title:** SkinExo-AI: A Context-Aware Extracellular-Vesicle Response Platform

**One-line pitch:** SkinExo-AI transforms isolated extracellular-vesicle studies into a context-aware response atlas that retrieves and explains conserved, context-dependent, discordant, and uncertain cellular responses.

These two lines are the canonical competition identity. Public prose may shorten “extracellular-vesicle” to “EV” after defining it, but must not replace “Response Atlas,” “response component,” or “response similarity” with predictive language.

## The one competition story

1. Extracellular-vesicle studies are usually analyzed in isolation.
2. EV source, recipient cell, dose, duration, study design, and evidence layer make results difficult to compare.
3. SkinExo-AI first tested whether a broadly reproducible EV-associated fibroblast response existed.
4. Across three study-level independent contexts, a broad universal transcriptomic response was **not supported**.
5. That negative result motivated a context-aware representation rather than a generic EV signature.
6. The F2 Response Atlas represents evidence at the response-component level and preserves broad axis summaries without treating components within an axis as interchangeable.
7. The Atlas explicitly preserves active positive, active negative, observed-null, not-tested, and unknown states, plus separate phenotype anchors, reliability dimensions, and provenance.
8. R1 retrieves observed contexts using mask-aware NES cosine over components tested in both contexts. It explains shared, discordant, and context-specific components. Phenotype and reliability evidence remain outside the similarity score.
9. Explorer A2 exposes the Atlas, observed-context retrieval, WHY explanations, phenotype evidence, reliability, and provenance in an offline Streamlit Demo Mode, while retaining the detailed Research Mode.
10. SkinExo-AI v0.3 is a research-support platform. It is not a trained predictive model or a therapeutic predictor.

## Scientific anchor

The strongest validation story is prospective non-generalization. CTX001 and CTX002 shared the active P081 proliferation/cell-cycle component in the same direction, creating a provisional two-context hypothesis. The prespecified CTX003 analysis returned `OBSERVED_NULL` across the frozen P mapping. The framework retained the null rather than forcing confirmation. P081 is therefore a **two-context shared component**, not a universal response.

The major representation contribution is the distinction between a broad axis and an exact component. For I, CTX002 and CTX003 share nine exact active inflammatory components in the same direction. CTX001 points in the same broad inflammatory-axis direction through a different active component structure. The three-context conclusion is `CONSERVED_AXIS_CONTEXT_VARIANT`, not component conservation across all three.

## Frozen headline values

- Atlas: F2-2026-10-01.
- Verified contexts: 3.
- Axes: 5.
- Response components: 339.
- Context-component records: 1,017.
- Activity states: 139 active positive, 19 active negative, 852 observed null, 7 not tested, 0 unknown.
- Primary retrieval metric: mask-aware NES cosine.
- Pairwise response similarities: CTX001–CTX002 −0.1749; CTX001–CTX003 −0.2755; CTX002–CTX003 +0.6053.
- CTX002–CTX003 active-union cosine: +0.8563; 9 shared active components; directional concordance 1.000.
- Explorer: Streamlit 1.64.0; offline; default CTX003 query ranks CTX002 first and CTX001 second.
- Automated repository tests, including retrieval and Explorer: 22/22 pass.

## Evidence boundaries

- The three contexts are independent at the study level. Donor and EV-preparation independence are incomplete or unknown and must not be inferred.
- Transcriptomic enrichment is not a demonstrated phenotype.
- CTX003 CCK-8 and scratch assays are 24-hour phenotype anchors; CTX003 RNA-seq is at 72 hours.
- Mouse wound, scar, and collagen observations are an in-vivo, different-model layer.
- Phenotype anchors do not enter the R1 similarity calculation.
- Similarity and reliability are separate. No aggregate confidence score is used.
- Correlations and cosine values are descriptive metrics across three contexts, not accuracy, AUC, or predictive performance.

## Forbidden claims

Competition material must not describe v0.3 as a predictive AI model, trained machine-learning model, foundation model, digital twin, therapeutic efficacy predictor, wound-healing predictor, universal EV model, causal cargo-response model, or proof of angiogenesis. It must not claim independent-donor or independent EV-preparation replication.

## Canonical closing

**SkinExo-AI does not assume a universal EV response. It retrieves and explains context-dependent response patterns while keeping evidence, missingness, phenotype anchors, reliability, and provenance visible.**
