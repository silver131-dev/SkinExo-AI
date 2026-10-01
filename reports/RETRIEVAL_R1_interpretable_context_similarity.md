# SkinExo-AI RETRIEVAL-R1

## Objective

Implement a reproducible retrieval baseline that ranks known F2 contexts by shared-tested transcriptomic component response while preserving component identity, missingness, phenotype anchors, reliability, and provenance.

## Why Retrieval Instead of Prediction

Only three verified contexts exist. R1 retrieves and explains observed evidence; it has no learned parameters and does not estimate outcomes for an unseen treatment, patient, or study.

## Input Atlas

R1 requires F2 validation PASS and consumes Atlas `F2-2026-10-01`: three contexts, 339 frozen components, explicit activity states, five phenotype anchors, and 39 reliability records. It does not rerun DE or GSEA.

## Missingness Semantics

`NOT_TESTED` and `UNKNOWN` are excluded using the shared-tested mask and are never converted to zero. `OBSERVED_NULL` remains a tested NES observation in primary similarity but is excluded from active-response similarity unless the other context makes the component active.

## Primary Similarity

For each pair, R1 restricts both raw representative NES vectors to components tested in both contexts and computes cosine similarity. At least two shared-tested components are required; insufficient overlap returns an explicit undefined status.

| Pair | Primary cosine | Active-union cosine | Shared tested | Shared active | Directional concordance |
| --- | ---: | ---: | ---: | ---: | ---: |
| CTX001 / CTX002 | -0.1749 | +0.0108 | 339 | 2 | 0.500 |
| CTX001 / CTX003 | -0.2755 | -0.2302 | 332 | 3 | 0.000 |
| CTX002 / CTX003 | +0.6053 | +0.8563 | 332 | 9 | 1.000 |

## Active-Response Similarity

The secondary active-union cosine uses mutually tested components active in either context. This reduces domination by components that were jointly tested but did not qualify. It does not replace the primary metric.

## Directional Concordance

Directional concordance is the fraction of shared-active components with the same active direction. Jointly null components are excluded. Same- and opposite-direction counts remain visible with the fraction.

## Axis-Aware Similarity

P, M, E, A, and I cosine summaries use their own mutually tested components and a minimum overlap of two. Axis explanations also expose shared-active, same-direction, and opposite-direction component counts. Component evidence remains the primary explanatory unit.

## Explanation Engine

For every ordered query-target pair, components are classified as shared positive, shared negative, discordant, query-only active, target-only active, or observed-null differences. Within each class, the top ten are ranked by `abs(query NES) + abs(target NES)`, with component ID as a deterministic tie break.

## Phenotype Evidence

Phenotype anchors are attached to query and target explanations. CTX003 P CCK-8 and M scratch anchors are 24 h functional evidence, separate from the 72 h transcriptome; mouse anchors remain in-vivo different-model evidence. Phenotypes do not enter either cosine.

## Reliability

All 13 reliability dimensions per context are attached without aggregation. Study independence, donor/preparation independence, sample QC, batch, pairing, control, diagnostics, sensitivity, and phenotype support remain separate from similarity.

## Leave-One-Context-Out Demonstration

- CTX001: #1 CTX002 (-0.175), #2 CTX003 (-0.275)
- CTX002: #1 CTX003 (+0.605), #2 CTX001 (-0.175)
- CTX003: #1 CTX002 (+0.605), #2 CTX001 (-0.275)

Each context is used as a query and the other two are ranked. This is a descriptive behavior demonstration, not train/test evaluation or predictive validation.

## Frozen Global NES Correlations

The F2 global Pearson/Spearman values are CTX001/CTX002 -0.0773/-0.1318, CTX001/CTX003 -0.1692/-0.1767, and CTX002/CTX003 +0.1878/+0.1945. Both summaries qualitatively place CTX002/CTX003 as the positive pair and CTX001 against the later contexts as negative, while R1 cosine separates those pairs more strongly. Correlation centers each vector and measures covariation; cosine measures angular alignment from zero on the F2 component representation. Shared-set definitions also differ. R1 was not tuned to reproduce correlation ordering.

## Sanity Tests

- identical_vector_cosine_one: **PASS**
- sign_reversal_cosine_negative_one: **PASS**
- nonoverlap_is_undefined: **PASS**
- jointly_null_not_active_similarity: **PASS**
- not_tested_excluded_not_zero: **PASS**
- unknown_excluded_not_zero: **PASS**
- ordered_explanations_reproducible: **PASS**

## Limitations

Only three contexts exist; all reliability limits from F2 remain. Component NES values use deterministic representative terms, context pairs can have different tested masks, and retrieval ranks cannot establish biological generalization, treatment efficacy, or prediction accuracy.

## Competition Role

R1 demonstrates how the Atlas supports interpretable evidence retrieval: each rank exposes shared, discordant, null, phenotype, reliability, and provenance information.

## R1 Decision

**PASS.** Six ordered retrievals, leave-one-context-out demonstrations, explanation records, phenotype/reliability attachments, and all sanity tests completed. No predictive model was trained.
