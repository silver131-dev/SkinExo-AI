# SkinExo-AI DEV-C1

**Date:** 2026-10-01

**Checkpoint purpose:** local freeze of EXP002-D0 through C4 and the academic-network harvest.
**Parent checkpoint:** DEV-C0, `bccfbaf7ff77f23c4952ac150bfe1269f19d0949` — *SkinExo-AI v0.1: freeze EXP001 C1-C4 and submission scaffold*.

## Frozen Research

| Checkpoint | Frozen status | Evidence |
| --- | --- | --- |
| EXP002-D0 | **PASS** | [Discovery report](../../reports/EXP002_D0_dataset_discovery.md), [machine-readable result](../../outputs/exp002/exp002_d0_dataset_discovery.json), and [search log](../literature/EXP002_D0_SEARCH_LOG.md) |
| EXP002-C1 | **REVIEW REQUIRED** | [Integrity report](../../reports/EXP002_C1_dataset_integrity.md) and [result](../../outputs/exp002/exp002_c1_integrity.json) |
| EXP002-C1R | **PASS / LIMITED_GO** | [Design and quantification resolution](../../reports/EXP002_C1R_design_quantification_resolution.md) and [result](../../outputs/exp002/exp002_c1r_resolution.json) |
| EXP002-C2 | **PASS WITH LIMITATIONS** after C2R | [C2 QC report](../../reports/EXP002_C2_sample_qc_analysis_plan.md), [frozen analysis plan](EXP002_C2_ANALYSIS_PLAN.md), and [C2R resolution](../../reports/EXP002_C2R_EV8_technical_review.md). The historical C2 JSON remains `REVIEW REQUIRED`; C2R explicitly resolved that gate. |
| EXP002-C2R | **PASS; EV_8 RETAINED** | [Technical review](../../reports/EXP002_C2R_EV8_technical_review.md) and [result](../../outputs/exp002/exp002_c2r_ev8_review.json) |
| EXP002-C3 | **PASS WITH SENSITIVITY WARNING** | [Differential-expression report](../../reports/EXP002_C3_differential_expression.md) and [result](../../outputs/exp002/exp002_c3_de.json) |
| EXP002-C4 | **COMPLETE** | [Pre-specified pathway report](../../reports/EXP002_C4_cross_study_pathway_validation.md), [result](../../outputs/exp002/exp002_c4_pathways.json), and [frozen validation endpoints](EXP002_VALIDATION_ENDPOINTS.md) |

EXP002 uses GSE251807: 8 MSC-sEV and 8 DMEM control recipient libraries in two balanced batches, one documented recipient donor lot, and an **unknown number/assignment of independent EV preparations**. The primary design remains `~ batch + condition`, with **EV_8 retained**. The EV_8-excluded fit is sensitivity evidence, not a replacement primary analysis. This is an independent-study, same-cell-type **external transcriptomic comparison**, not donor-level or EV-preparation-level replication.

## EXP002-C3 Values

| Measure | Primary, 16 samples | EV_8-excluded sensitivity, 15 samples |
| --- | ---: | ---: |
| Genes tested | 16,217 | 16,104 |
| `padj < 0.05` | 1,884 | 1,970 |
| Threshold B: `padj < 0.05` and `\|log2FC\| ≥ 1` | 66 | 65 |
| Threshold-B up | 52 | 49 |
| Threshold-B down | 14 | 16 |

Primary versus sensitivity: log2FC Pearson **0.8822**, Spearman **0.9534**, direction concordance **92.04%**, median absolute Δlog2FC **0.0302**, and 95th-percentile absolute Δlog2FC **0.1655**. The Pearson result triggered the frozen sensitivity warning; no technical defect justified removing EV_8 from the primary fit.

## EXP002-C4 Outcome

**Broad five-axis concordance: NOT SUPPORTED.** GSEA was the primary evidence, using the frozen EXP001-C4 MSigDB 2026.1.Hs definitions and pre-specified term map. The EXP002 sensitivity fit did **not** change any final axis classification.

| Axis | Frozen outcome | Component-level interpretation |
| --- | --- | --- |
| **P** — proliferation / cell cycle | `PARTIALLY_CONCORDANT` | At least one **shared active component** has the same positive direction across EXP001 and EXP002; opposing evidence prevents full concordance. |
| **M** — migration / motility | `DISCORDANT` | Opposite dominant GSEA directions. |
| **E** — ECM organization / remodeling | `NOT_TESTABLE` | Common terms were eligible, but pre-specified EXP002 GSEA yielded no qualified ECM component: an **observed null**, not missing coverage. |
| **A** — angiogenesis / endothelial interaction | `DISCORDANT` | Opposite dominant vascular/endothelial term-family directions; **no direct angiogenesis phenotype claim** follows. |
| **I** — inflammation / immune signaling | `PARTIALLY_CONCORDANT` | Positive dominant directions arise from **different active components** in the two studies; there is no shared active inflammatory component. This is weaker/different evidence from P. |

Neither cross-study GSEA concordance nor individual NES signs establish universal EV response, therapeutic efficacy, increased proliferation/migration, wound healing, angiogenesis, regeneration, or predictive AI. The C4 result is a mixed scientific outcome and was not rewritten to improve the competition story.

## Academic Network Harvest

DEV-C1 froze **27 literature records audited**, including **20 primary/method studies**. The public checkpoint retains citations and verified provenance only. Licensed publication files and access-specific records are outside the public release and must not be committed or redistributed. CTX003 public-source details are preserved in the [EXP003-D0 source log](../literature/EXP003_D0_SOURCE_LOG.md).

The Liu article's **GSE293956** recipient-cell transcriptomics and **GSE293957** hDF-EV miRNA profiling are public GEO datasets for later retrieval. No new GEO data were downloaded or analyzed during DEV-C1. Raw/processed EXP002 data, GENCODE sources, MSigDB caches, `.venv/`, and `.r-env/` remain ignored.

## Strategic Transition

SkinExo-AI is **planning a transition** from a single-study or broad EV-response analysis toward **A Context-Aware Extracellular-Vesicle Response Platform**. The empirical reason is that EXP001 versus EXP002 did **not** support broad five-axis concordance. The planned framework will distinguish shared/conserved response components, axis-level thematic overlap, context-dependent responses, discordant responses, null/not-testable evidence, and sensitivity-dependent conclusions. Competition positioning is a context-aware EV response framework/platform, grounded in a rigorous multi-study transcriptomic evidence engine. An interpretable response representation and retrieval component are **planned, not implemented**. The present work is not a foundation model, digital twin, deep-learning model, or therapeutic predictor.

Formal framework work belongs to **FRAMEWORK-F1 after DEV-C1**. DEV-C1 does not begin EXP003, retrieval, app construction, or a broad rewrite of submission materials.
