# EXP002-C4 — Pre-Specified Cross-Study Pathway Validation

**Status:** analysis complete; broad P/M/E/A/I directional concordance is **not supported**. The frozen endpoint assigns outcomes to each axis, not a composite score. Primary EXP002 analysis includes EV_8. The separate sensitivity fit excludes EV_8. Neither C3 fit was rerun or changed.

## Frozen inputs and method

- EXP001: GSE293186 endothelial EV versus control at 72 h; 16,271 tested stable gene IDs and existing C4 GSEA results.
- EXP002: GSE251807 MSC-sEV versus DMEM at 48 h; the existing `~ batch + condition` C3 results contain 16,217 tested genes in the 16-sample primary fit and 16,104 in the 15-sample sensitivity fit.
- Local MSigDB **2026.1.Hs** GO BP, Reactome, and Hallmark GMT files match the SHA-256 values in the frozen EXP001-C4 plan. The existing `PREDEFINED` [term map](../data/metadata/skinexo_c4_term_map.csv) was not edited.
- GSEApy 1.3.1 prerank used all C3-tested genes ranked by signed DESeq2 Wald statistic; 1,000 gene-set permutations, seed 42, weight 1, and 15–500 effective gene IDs per term. Positive NES means EV-higher association. A term qualifies at GSEA FDR < 0.05, at least five leading-edge IDs, and at least 80% leading-edge Wald statistics aligned with its NES sign.
- For each axis, common eligible terms were grouped into connected components using **source gene-set symbol** Jaccard overlap ≥0.50, independent of GSEA results. Component and axis directions, and the outcome order, follow the [frozen validation endpoint](../docs/checkpoints/EXP002_VALIDATION_ENDPOINTS.md). Related terms in one component are not independent confirmations.

The primary EXP002 run had **4,892 eligible terms, 355 qualified**; the sensitivity run had **4,883 eligible terms, 331 qualified**. EXP001 and EXP002 shared 4,553 eligible terms for the primary comparison and 4,555 for the sensitivity comparison. All common eligible terms, including null results, were retained in the comparison outputs.

## Primary endpoint: P / M / E / A / I

| Axis | Common eligible terms / components | EXP001 active components | EXP002 primary active components | Primary outcome | Sensitivity outcome |
| --- | ---: | --- | --- | --- | --- |
| **P** — proliferation / cell cycle | 176 / 100 | 63 positive, 2 negative | 3 positive | **PARTIALLY_CONCORDANT** | **PARTIALLY_CONCORDANT**; 2 positive EXP002 components |
| **M** — migration / motility | 84 / 34 | 6 negative | 6 positive | **DISCORDANT** | **DISCORDANT**; 6 positive EXP002 components |
| **E** — ECM organization / remodeling | 28 / 22 | 5 negative | 0 qualified | **NOT_TESTABLE** — observed null EXP002 GSEA, not missing term coverage | **NOT_TESTABLE** — same null |
| **A** — angiogenesis / endothelial interaction | 59 / 37 | 4 negative | 7 positive | **DISCORDANT** | **DISCORDANT**; 6 positive EXP002 components |
| **I** — inflammation / immune signaling | 261 / 146 | 4 positive, 1 negative | 24 positive, 1 negative | **PARTIALLY_CONCORDANT** | **PARTIALLY_CONCORDANT**; 23 positive, 1 negative EXP002 components |

P and I share positive dominant directions but contain opposing component evidence, so neither meets the frozen `CONCORDANT` rule. The sparse EXP002 P signal (three primary components versus 65 EXP001 components) further limits interpretation. M and A have opposite dominant directions. E has adequate common term coverage but no qualified EXP002 component. **No axis is fully concordant across studies under the frozen rule.**

At the individual component level, only **one P component** is active with the same positive direction in both studies. **I has no component active in both**: its partial concordance is an axis-level dominant-direction match across different term components. M has one component active in both, with opposite directions. A has no component active in both, so its discordance is an axis-level contrast between different vascular/endothelial term components. These distinctions matter when interpreting the family-level outcomes.

The EXP002 primary and sensitivity fits retain the same outcome for every axis. Within EXP002, P, M, and A are `CONCORDANT`; I is `PARTIALLY_CONCORDANT` because both fits include a negative component alongside positive components; E remains a null `NOT_TESTABLE` result in both. This stability does not resolve the EXP001–EXP002 discordance.

Example qualified terms illustrate the directional contrast without selecting new axes: EXP001 `GOBP_NEGATIVE_CHEMOTAXIS` has NES −2.12 (FDR 0.0015), while EXP002 primary migration-associated terms include `GOBP_POSITIVE_REGULATION_OF_CELL_MIGRATION_INVOLVED_IN_SPROUTING_ANGIOGENESIS` at NES +2.13 (FDR 0.0036). EXP001's qualified A terms are vascular-associated smooth-muscle proliferation and endothelial apoptosis terms with negative NES; EXP002's A terms include vascular development and VEGF-production terms with positive NES. These are transcriptomic associations. A pathway name containing “angiogenesis” is **not a direct angiogenesis assay**, and the EXP001 C3.5 direct angiogenesis evidence count remains zero.

## Secondary descriptive endpoints

| Comparison | Common eligible NES terms | NES Pearson / Spearman | Shared tested gene IDs | Gene-level sign agreement | log2FC Pearson / Spearman |
| --- | ---: | ---: | ---: | ---: | ---: |
| EXP001 vs EXP002 primary | 4,553 | −0.077 / −0.132 | 13,138 | 48.39% | −0.052 / −0.047 |
| EXP001 vs EXP002 sensitivity | 4,555 | −0.048 / −0.097 | 13,109 | 49.42% | −0.037 / −0.035 |
| EXP002 primary vs sensitivity | 4,881 | +0.911 / +0.958 | 16,104 | 92.04% | +0.882 / +0.953 |

The cross-study global NES and gene-level correlations are near zero or slightly negative; they do not supply an independent broad-concordance signal. Within EXP002, the high NES correlation supports fit-level stability. NES correlations by GO BP, Reactome, Hallmark, and each frozen axis are stored in the machine-readable summary. Gene-level comparison includes nonsignificant tested genes; zero-effect exclusions were zero. EXP001 had 3,133 tested IDs absent from the EXP002 primary universe and EXP002 had 3,079 absent from EXP001. The shared-ID subset must not be confused with either full tested universe.

There were **40** common eligible terms with qualified leading edges in both EXP001 and EXP002 primary, with median leading-edge Jaccard **0.282**. The sensitivity comparison had **41**, median **0.337**. Across the two EXP002 fits, **277** terms qualified in both, median Jaccard **0.846**. The complete per-term tables retain `QUALIFIED_FIRST_ONLY`, `QUALIFIED_SECOND_ONLY`, and `NOT_QUALIFIED_EITHER` statuses as well as the qualified-both overlap distribution. Overlapping pathways and components are dependent; these numbers are descriptive. With only two independent studies, pathway retrieval performance is not estimable.

## Interpretation and limits

EXP002-C4 completes the pre-specified comparison but **does not support a broad claim that the five EV-response program directions replicate across the two studies**. P and I show limited, qualified same-direction evidence; M and A are discordant; E is null in EXP002. The sensitivity analysis does not change these assignments. Do not replace the primary 16-sample fit with the EV_8-excluded fit or revise the term families in response to this result.

The studies use different EV sources and exposure durations, and EXP002 documents only one recipient donor lot; EV-preparation independence remains unknown. NES sign alone does not show beneficial phenotype, increased migration, angiogenesis, wound closure, or regeneration. Functional phenotypes require their own evidence. This checkpoint does not start predictive AI or analyze the public Liu et al. GEO datasets.

## Audit files

- [Machine-readable C4 summary](../outputs/exp002/exp002_c4_pathways.json) records input hashes, axis outcomes, NES correlations by subset, leading-edge summaries, and shared-gene metrics.
- `outputs/exp002/c4_gsea_{primary,sensitivity}_all.csv` hold all eligible GSEA terms; `c4_term_coverage_{primary,sensitivity}.csv` hold all source terms and eligibility.
- `outputs/exp002/c4_axes_*.csv`, `c4_components_*.csv`, `c4_common_terms_*.csv`, and `c4_leading_edge_overlap_*.csv` give the full three-comparison audit trail, including null or non-qualified terms.
- [C4 runner](../experiments/exp002/04_cross_study_pathways.py) reads frozen C3 and EXP001-C4 artifacts. No files were committed or pushed.
