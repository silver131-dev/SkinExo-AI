# SkinExo-AI EXP002-C2

## Objective

Build an auditable gene-level representation from GSE251807's 16 Salmon quantifications, assess sample integrity and structure **without** fitting a treatment model, and freeze the later DE and cross-study endpoints. This checkpoint performs no differential expression, enrichment, EXP001–EXP002 biological comparison, or model training.

## C1R Constraints

[EXP002-C1R](EXP002_C1R_design_quantification_resolution.md) yielded **LIMITED_GO**: 8 MSC-sEV and 8 DMEM-control libraries, balanced 4/4 in each of two batches; one documented recipient donor lot; unknown independent EV-preparation count; differing Salmon transcript universes; and 189,509 exact shared ENST IDs. The original author Salmon index release remains unverified. [GENCODE v44](https://www.gencodegenes.org/human/release_44.html) is a **compatible authoritative mapping** for the exact shared IDs, not a verified description of the index the authors used.

## Transcript Harmonization

The frozen Strategy A uses **only the 189,509 exact shared versioned transcript IDs**. No batch-specific ID or version-normalized-only ID enters C2. [02_prepare_shared_quant.py](../experiments/exp002/02_prepare_shared_quant.py) filters each official `quant.sf` export to exactly those IDs, sorts them into the same order, and derives an exact `ENST.version → ENSG.version` map from the ignored GENCODE v44 transcript-ranking file. All filtered Salmon tables, the tx2gene table, and the manifest are in ignored `data/processed/exp002/`. No raw biological file or gene-expression matrix is intended for Git.

## Gene-Level Aggregation

Bioconductor **tximport 1.30.0** (`type="salmon"`, `countsFromAbundance="no"`, exact `tx2gene`, `ignoreTxVersion=FALSE`) aggregated transcript `NumReads` estimates to **37,307 genes × 16 samples**. The local R 4.3.3 / Bioconductor 3.18 environment and pinned package archive are documented in [exp002_c2_r_environment.md](../configs/exp002_c2_r_environment.md). The ignored `tximport_shared_gencode_v44.rds` preserves gene-level estimated counts, TPM abundance, and average effective-length information; corresponding ignored CSVs are provided for QC. These are **estimated gene-level counts derived from Salmon transcript quantification**, not original integer gene counts.

All 189,509 shared transcripts mapped exactly, with **0 unmapped** and **0 ambiguous** transcript-to-gene assignments. Transcripts per mapped gene ranged from 1 to 192 (median 1). Each gene-level count sum matched the retained transcript `NumReads` sum to rounding tolerance. The full [aggregation QC table](../outputs/exp002/exp002_c2_aggregation_qc.csv) records each sample's source and retained totals, TPM sums, mapping counts, and information loss.

## Information Loss

Strategy A retained **97.1670%–98.2596%** of each sample's Salmon `NumReads` sum, excluding **1.7404%–2.8330%**. The excluded fraction differs by batch, so the retained estimates are a restricted representation and the original index discrepancy remains a technical limitation. Salmon `NumReads` sums and ENA run `read_count` have different meanings under the deposited paired-read processing description; they are compared only as **within-measure relative depths**. No TPM renormalization was used for the count-based representation.

## Filtering

The candidate filters and primary choice were fixed in [exp002_c2_qc_plan.json](../configs/exp002_c2_qc_plan.json) **before PCA**. None uses condition or batch labels to select genes.

| Rule | Unsupervised criterion | Genes retained |
| --- | --- | ---: |
| A | Estimated gene count ≥10 in ≥4 of 16 samples | 16,217 |
| B | CPM ≥1 in ≥2 of 16 samples | 14,046 |
| **C — primary** | **CPM ≥1 in ≥4 of 16 samples** | **13,724** |

Rule C is library-size-aware and requires expression in at least one quarter of libraries, without consulting EV/control separation. It is a **QC visualization filter**, not necessarily the later DE low-count rule. [filtering_summary.csv](../outputs/exp002/filtering_summary.csv) preserves all candidates. The 13,724 retained genes were transformed as **log2(library-size CPM + 1)** for correlation and PCA only. This transformation is not a replacement for tximport-aware, count-based DE modeling.

## Sample QC

All 16 mapped gene columns are present, uniquely identified, finite, and nonnegative. Estimated gene-count totals range from **37.68 million** to **92.72 million** (median **51.44 million**, max/min **2.46**); [fig01_library_size.png](../outputs/exp002/figures/fig01_library_size.png) displays every sample by condition and batch. The maximum belongs to `EV_8` and triggers the frozen >1.75× median depth-review rule. No library was removed. Differences in estimated-count totals do not establish a biological effect.

## Correlation

Pearson correlation across the **filtered log2(CPM + 1)** matrix is saved in [sample_correlation.csv](../outputs/exp002/sample_correlation.csv) and shown in [fig02_sample_correlation.png](../outputs/exp002/figures/fig02_sample_correlation.png). Group summaries are descriptive; no significance tests compare them.

| Pair category | Mean Pearson r |
| --- | ---: |
| Within MSC-sEV | 0.9649 |
| Within DMEM control | 0.9688 |
| Within batch 1 | 0.9874 |
| Within batch 2 | 0.9882 |
| Between batches | 0.9487 |

Within-batch correlations exceed between-batch correlations, consistent with a substantial batch contribution. `EV_8` averages **0.9845** correlation with `EV_5`–`EV_7`; their pairwise correlations with one another are about **0.99**. Thus `EV_8` is somewhat less similar to its nearest matched group, though still highly correlated. The predeclared >0.05 drop below the EV-group median **was not met**.

## PCA

PCA fitted **samples as observations, genes as features**, using the 13,724 filtered genes. Neither condition nor batch labels were supplied to the fit. [pca_coordinates.csv](../outputs/exp002/pca_coordinates.csv) and [fig03_pca.png](../outputs/exp002/figures/fig03_pca.png) show all 16 samples, colored by condition and shaped by batch. PC1 explains **66.09%** and PC2 **6.62%** of variance.

Labels applied **after** fitting show that PC1 aligns strongly with batch (descriptive eta-squared **0.991**), while PC2 aligns with condition (descriptive eta-squared **0.919**). These are sample-structure descriptions, **not** treatment-effect tests, biological validation, or evidence that EV exposure caused a repair phenotype. The strong PC1 batch alignment supports retaining the batch term in the frozen later design.

## PCA Robustness

The same unsupervised PCA was repeated on all filtered genes, the top 5,000 variable genes, and the top 2,000 variable genes. Variance ranking used all samples without condition labels. [pca_robustness.csv](../outputs/exp002/pca_robustness.csv) and [fig04_pca_robustness.png](../outputs/exp002/figures/fig04_pca_robustness.png) retain every coordinate.

| Feature set | PC1 | PC2 | Spearman correlation of pairwise sample distances versus all genes | Descriptive PC1 batch eta-squared |
| --- | ---: | ---: | ---: | ---: |
| All 13,724 | 66.09% | 6.62% | 1.000 | 0.991 |
| Top 5,000 variable | 68.74% | 5.87% | 0.986 | 0.992 |
| Top 2,000 variable | 67.29% | 5.68% | 0.949 | 0.993 |

Batch dominance on PC1 and the isolated `EV_8` position persist across all three feature choices. These concordant QC views do not make the treatment contrast causal or remove technical confounding concerns.

## EV_8

**QC_REVIEW_NEEDED; retained.** ENA reports `read_count = 54,035,352` for its one recorded run, **1.837×** the selected median. Its tximport estimated gene-count total is **92,722,948**, **1.803×** the median; these relative depth ratios are consistent. Its mean within-EV Pearson correlation is **0.9637**, without triggering the correlation threshold. In PC1–PC2, however, its nearest-neighbor distance is **5.20×** the median nearest-neighbor distance; the same isolated position appears with 5,000 and 2,000 variable genes. Higher read depth alone is therefore insufficient to close the sample-level question. No duplicate run or confirmed technical defect has been found, and the sample remains in all C2 matrices and figures.

Before C3, review available run-level and source records for library preparation or sample-identity issues, and assess whether the sample remains an outlier under appropriate C2 technical QC. A future sensitivity fit, if needed, must be labeled secondary; do not remove `EV_8` merely to improve separation or significance.

## Batch Assessment

Both conditions occur in both batches, so **condition and batch are not fully confounded**. Nonetheless, correlation and unsupervised PCA show a strong batch-aligned structure. The design **`~ batch + condition` remains recommended** for later count-based analysis; `~ condition` would omit a known major design factor. This decision uses metadata and sample QC, not DE results. A batch term cannot repair every gene-specific consequence of different original Salmon indexes, so reference sensitivity must remain visible in C3.

## Frozen DE Plan

The conditional [EXP002-C2 analysis plan](../docs/checkpoints/EXP002_C2_ANALYSIS_PLAN.md) fixes the unit, Strategy-A tximport representation, `~ batch + condition` design, `MSC_sEV` versus `CTRL_DMEM` sign convention, and reporting thresholds **A** `padj < 0.05` and **B** `padj < 0.05 & |log2FC| ≥ 1`. It specifies a separate, unsupervised C3 low-count rule and DESeq2-compatible count-based framework using gene-length information. No DE model was fitted. **C2 is REVIEW REQUIRED**, so C3 must wait for the `EV_8` QC question to be resolved or explicitly bounded.

## Frozen Cross-Study Validation Endpoints

The [validation endpoint document](../docs/checkpoints/EXP002_VALIDATION_ENDPOINTS.md) fixes the **primary endpoint** as directional concordance of pre-specified P/M/E/A/I GSEA program families across EXP001 and EXP002. It retains `CONCORDANT`, `PARTIALLY_CONCORDANT`, `DISCORDANT`, and `NOT_TESTABLE` outcomes, a condition-independent term map, a redundancy rule, and explicit null reporting. Secondary endpoints are NES correlation across shared sets, leading-edge overlap, gene-level directional concordance, global signed-Wald similarity, and pathway-level clustering/retrieval (descriptive with only two studies). No EXP002 GSEA or EXP001–EXP002 concordance was calculated in C2.

## Claim Boundaries

Even if a later primary endpoint is concordant, the strongest potential statement is independent-study, same-cell-type **transcriptomic program** concordance across distinct EV sources. This dataset cannot supply independent-donor or EV-preparation-level validation, universal EV biology, wound-healing efficacy, angiogenesis, or regeneration claims. A discordant result remains a valid result. The current C2 checkpoint **does not mark independent validation complete**.

## Limitations

- One documented recipient donor lot; independent EV-preparation count and per-well assignment unknown.
- Original Salmon indexes unverified and batch-specific transcript sets differ; Strategy A excludes a small, batch-associated fraction of estimates.
- `EV_8` is an unsupervised PCA outlier despite higher depth tracking ENA metadata; no technical defect is confirmed.
- The RNA-seq EV vehicle/PBS matching to DMEM controls is not fully documented.
- PCA, Pearson correlations, and log-CPM are exploratory QC, not count-based treatment inference.
- No sample was removed, no differential expression was run, and no cross-study biological result was examined.

## C2 Decision

**REVIEW REQUIRED.** The 37,307-gene tximport representation is reproducible and complete, with 13,724 genes retained for QC, and the balanced design supports a provisional batch-adjusted model. The strong batch structure and persistent `EV_8` PCA outlier require explicit technical review before C3. The [machine-readable checkpoint](../outputs/exp002/exp002_c2_qc.json) sets `overall_pass=false`; it does not invalidate the frozen analysis/validation plans or justify deleting a sample. STOP before differential expression.
