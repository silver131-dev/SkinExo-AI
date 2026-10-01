# EXP002 — Frozen cross-study validation endpoints

**Frozen before EXP002 differential-expression, GSEA, and EXP001–EXP002 concordance results.** This is an analysis plan, not a validation result. The primary question is whether **pre-specified transcriptomic program directions** recur in primary human dermal fibroblasts across two independent studies with **different EV sources and exposure times**. It is **not** whether the same individual genes pass an adjusted-p threshold.

## Fixed inputs and direction

- EXP001: GSE293186, endothelial EV versus CTRL, 72 h; positive signed DESeq2 Wald statistic means higher after endothelial EV exposure.
- EXP002: GSE251807, MSC-sEV versus DMEM, 48 h; positive signed DESeq2 Wald statistic will mean higher after MSC-sEV exposure.
- Gene-set source: the same **MSigDB human 2026.1.Hs** GO Biological Process, Reactome, and Hallmark collections used in EXP001-C4, subject to their license. Use exact stable term IDs and the existing [PREDEFINED Q1–Q5 term map](../../data/metadata/skinexo_c4_term_map.csv); do not add or drop terms because of EXP002 results. Restrict each study's analysis to its tested-gene universe; cross-study comparisons use the **common set of eligible term IDs**, fixed by each universe and the original 15–500 effective-gene-size rule, never by observed significance.
- Map gene sets to stable gene IDs through documented authoritative gene-symbol metadata. Preserve and audit symbol-to-multiple-gene mappings; never select one duplicate gene because of its DE result.
- Rank **all C3-tested genes** in each study by signed DESeq2 Wald statistic, not adjusted p-value or a significance-only subset. GSEA is the **primary** program-level evidence. Positive NES means association with EV-higher genes; negative NES means association with EV-lower genes, with no implied beneficial phenotype.
- Retain the EXP001-C4 leading-edge coherence rule: at least **5** leading-edge genes and at least **80%** of their Wald statistics aligned in sign with NES. A term is qualified when GSEA FDR < 0.05 and the leading edge is coherent. Report non-qualified and null terms as well.

## Primary endpoint: P / M / E / A / I direction

| Axis | Prespecified term family |
| --- | --- |
| P | Q1 — Proliferation / cell-cycle regulation |
| M | Q2 — Migration / motility |
| E | Q3 — ECM organization and remodeling |
| A | Q4 — Angiogenesis / endothelial interaction |
| I | Q5 — Inflammation / immune signaling |

**Redundancy rule, fixed before EXP002 results:** Within each axis, build a graph of common eligible terms from their **source gene-set memberships**, with an edge when Jaccard gene overlap is ≥0.50. Each connected component is one related-term family for interpretation. Graph construction uses no DE or GSEA result. For each study, a component is active if at least one term is qualified; its direction is the sign of the median NES of its qualified terms. A component with median NES exactly zero or mixed qualified signs that prevent a clear median is recorded as mixed. Related GO terms within one component are **not independent confirmations**.

For each axis, define its dominant direction from the active component directions: positive or negative when at least two thirds of nonmixed active components have that sign; otherwise mixed. Save each component's term IDs, NES, FDR, and leading-edge size so this can be audited. Assign one of the only allowed outcomes:

- **CONCORDANT:** both studies have qualified components, the same nonmixed dominant direction, and no active component in either study points in the opposite direction.
- **PARTIALLY_CONCORDANT:** both have qualified components and a matching dominant direction but also opposing/mixed component evidence; or at least one matching same-direction component when an axis is mixed.
- **DISCORDANT:** both have qualified components and opposite nonmixed dominant directions, or no same-direction active component across studies when the dominant directions are mixed; preserve this finding without redefining the axis.
- **NOT_TESTABLE:** no common eligible terms or no qualified component in one or both studies. State separately whether this reflects missing coverage or an observed **null GSEA result**; do not silently treat a null as agreement.

Apply the rules in this order: `NOT_TESTABLE`, `CONCORDANT`, opposite-dominant `DISCORDANT`, `PARTIALLY_CONCORDANT` when at least one same-direction component remains, and otherwise `DISCORDANT`. This fixes the treatment of mixed evidence before the EXP002 results exist.

Report all five axis outcomes, the evidence by term family, and the number of eligible/qualified components. No composite numeric SkinExo score is defined. A broad Q4 vascular/endothelial association must be distinguished from **angiogenesis itself**; the existing C3.5 direct angiogenesis evidence count remains zero and enrichment does not create direct phenotype evidence.

## Secondary endpoints — never substitute for the primary endpoint

1. **GSEA NES correlation:** Pearson and Spearman correlation of NES over the exact common eligible gene-set IDs, with database/axis subsets reported transparently. Overlapping sets are dependent; correlations are descriptive.
2. **Leading-edge gene overlap:** Jaccard overlap of stable gene IDs for the same pre-specified common eligible term, only where both studies have a qualified leading edge. Report the full distribution and missing/not-qualified terms; do not report only the best overlaps.
3. **Gene-level directional concordance:** Fraction of shared **tested** stable gene IDs with the same log2FC sign, plus Pearson/Spearman log2FC correlation. Include nonsignificant genes; do not require shared DEG status for the primary estimate. Report annotation/coverage exclusions.
4. **Global response similarity:** Spearman correlation of signed Wald statistics on shared tested stable gene IDs, interpreted descriptively and separately from pathway concordance.
5. **Pathway-level clustering/retrieval:** correlation distance (`1 − Pearson r`) on a shared eligible NES vector, with complete input term list and no supervised feature selection. With only two studies, retrieval performance is **not estimable**; treat any two-study display as descriptive until additional independent datasets exist.

No secondary endpoint may be promoted to primary because it looks more favorable. ORA, if run later, is secondary supporting evidence and must use each study's tested-gene universe.

## EXP002-C2R sensitivity addendum — frozen before C3

EV_8 was **retained** after technical review. The **all-16-sample** `~ batch + condition` fit is the EXP002 primary result for this endpoint. A separate **15-sample** fit omitting EV_8 is a robustness check, not a substitute primary analysis. Apply the same frozen P/M/E/A/I term families, GSEA ranking and qualification rules, gene-set release, and axis outcome logic to both fits. Report whether each axis's qualified direction is stable, including axes that are null, mixed, or untestable in either fit. Do not reinterpret an axis or promote a secondary endpoint if the sensitivity fit looks more favorable.

The seven C2R robustness measures are frozen in [the C2 analysis plan](EXP002_C2_ANALYSIS_PLAN.md): Pearson/Spearman log2FC correlations, gene-level sign concordance, two significance-set overlaps, P/M/E/A/I GSEA direction stability, and GSEA NES correlation. These compare the two EXP002 fits only. The independent EXP001-versus-EXP002 primary endpoint above is unchanged. The original EXP002-C1R **LIMITED_GO** generalization limits remain in force.

## Claim boundaries

If the primary endpoint supports directional concordance, the maximum justified claim is: **“Independent-study, same-cell-type external validation identified concordant transcriptomic programs across distinct EV sources.”** The wording is conditional on the actual future result and documented technical checks.

Do **not** claim independent-donor validation, EV-preparation-level replication, universal EV biology, therapeutic efficacy, increased proliferation, angiogenesis, regeneration, or wound closure from cross-study transcriptomic concordance. EXP002 uses one documented recipient donor lot and an unknown EV-preparation structure. If axes are discordant or untestable, retain and report that outcome; do not change term families, thresholds, endpoints, or EV-response narrative to rescue concordance.
