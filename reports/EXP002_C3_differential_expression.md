# SkinExo-AI EXP002-C3

## Objective

Estimate the MSC-sEV-associated gene-expression contrast in GSE251807 and quantify its dependence on EV_8. This checkpoint includes two frozen DESeq2 fits and gene-level sensitivity metrics only. It does not compare EXP002 with EXP001 or run GSEA.

## Dataset Constraints

GSE251807 includes 16 author-described recipient NHDF cultures/libraries: 8 MSC-sEV and 8 DMEM controls, split into two batches of 4 per arm. Recipient cells come from one documented donor lot, and EV-preparation independence is unknown. EXP002-C1R remains `LIMITED_GO`; EXP002-C2 was resolved by C2R to `PASS WITH LIMITATIONS` after retaining EV_8.

## Estimated Count Representation

Input is the C2 tximport object from **189,509 exact-shared versioned ENST transcripts**, mapped through compatible **GENCODE v44 / GRCh38.p14**. It supplies estimated gene counts, TPM, and sample-specific abundance-weighted effective gene lengths. `countsFromAbundance="no"`; `DESeqDataSetFromTximport` internally rounds fractional estimated counts and carries `avgTxLength` into gene-length-aware normalization factors. **These are estimated gene-level counts, not original integer gene counts.** The original author Salmon index release is unverified. The author-normalized matrix and EXP001 files were not DE inputs. Annotation source: GENCODE v44 official chromosome/patch/haplotype/scaffold GTF gene features (compatible mapping; original Salmon index unknown).

The [Bioconductor tximport workflow](https://bioconductor.org/packages/3.18/bioc/vignettes/tximport/inst/doc/tximport.html) documents this counts-plus-length-offset route; [DESeq2](https://bioconductor.org/packages/3.18/bioc/html/DESeq2.html) implements the negative-binomial model.

## Statistical Framework

R **R version 4.3.3 (2024-02-29)**; Bioconductor **3.18**; DESeq2 **1.42.0**; tximport **1.30.0**. Both fits used standard DESeq2 dispersion estimation, Wald testing, default Cook's handling and independent filtering, and Benjamini–Hochberg adjustment. No ordinary t-test or log-CPM outcome test was used.

## Frozen Design

Primary: all **16** samples, including EV_8; design `~ batch + condition`. Sensitivity: **15** samples excluding EV_8; the same additive design and framework. Reference is `CTRL_DMEM`; contrast is `MSC_sEV` versus `CTRL_DMEM`. **Positive log2FC means higher estimated expression after MSC-sEV exposure.** The scientific target is the average condition effect across batches. No batch × condition interaction was fitted. Both design matrices were full rank before fitting. The EV_8 inclusion decision was frozen before results.

## Filtering

Before each fit, apply the frozen condition-blind rule: **Salmon estimated gene count >= 10 in at least 4 included libraries**. From **37,307** mapped genes, **16,217** entered the primary fit and **16,104** the sensitivity fit. Different retained-gene counts reflect the omitted library; all comparisons below use the **16,104** shared tested genes with finite effects. Threshold A is `padj < 0.05`; threshold B adds `|log2FC| >= 1`. Neither filter nor threshold was tuned to DEG results.

## Primary Differential Expression

The 16-sample fit yielded **1,884** genes at threshold A and **66** at threshold B (**52** higher; **14** lower in MSC-sEV). [Complete results](../outputs/exp002/differential_expression_primary_all.csv) retain all tested genes, including null and NA-adjusted-p results; [threshold-B results](../outputs/exp002/differential_expression_primary_significant.csv) are a reporting subset.

The first ten threshold-B rows by adjusted p-value, with no manual biological selection, are:

| gene_id | gene_symbol | log2FC | padj |
| --- | --- | ---: | ---: |
| ENSG00000115738.10 | ID2 | 1.414 | 7.74e-49 |
| ENSG00000159167.12 | STC1 | 1.163 | 2.47e-26 |
| ENSG00000123358.20 | NR4A1 | 1.190 | 4.38e-19 |
| ENSG00000117152.14 | RGS4 | 1.701 | 5.85e-19 |
| ENSG00000172817.4 | CYP7B1 | 1.490 | 6.72e-19 |
| ENSG00000239474.7 | KLHL41 | -1.138 | 3.56e-17 |
| ENSG00000123700.5 | KCNJ2 | 1.167 | 1.28e-13 |
| ENSG00000162496.9 | DHRS3 | 1.411 | 9.64e-13 |
| ENSG00000118523.6 | CCN2 | 1.626 | 2.14e-12 |
| ENSG00000120129.6 | DUSP1 | 1.137 | 2.52e-11 |

These are statistical results, not evidence of a skin-repair phenotype.

## Sensitivity Differential Expression

The 15-sample fit yielded **1,970** genes at threshold A and **65** at threshold B (**49** higher; **16** lower). [Complete](../outputs/exp002/differential_expression_sensitivity_all.csv) and [threshold-B](../outputs/exp002/differential_expression_sensitivity_significant.csv) tables are separate. This fit does **not** replace the primary result, regardless of DEG count.

## Primary vs Sensitivity Robustness

Over **16,104** shared tested genes with finite log2FC, Pearson `r = 0.8822` and Spearman `ρ = 0.9534`. Direction concordance among **16,104** genes with nonzero effects in both fits is **0.9204**; **0** exact-zero effects were excluded. The fixed magnitude subset, `|log2FC| >= 1` in either fit, contains **405** genes and has direction concordance **0.9852**. This cutoff comes from the previously frozen threshold-B magnitude, not from the observed sensitivity result.

| Significance-set overlap | Intersection | Union | Jaccard |
| --- | ---: | ---: | ---: |
| `padj < 0.05` | 1,635 | 2,219 | 0.7368 |
| `padj < 0.05 & |log2FC| >= 1` | 53 | 78 | 0.6795 |

These overlaps are descriptive and change with sample size and power. P/M/E/A/I GSEA direction stability and NES correlation remain **PENDING_C4**.

## EV_8 Influence

The median absolute primary-versus-sensitivity log2FC difference is **0.0302**; the 95th percentile is **0.1655**. There are **1,282** sign reversals among nonzero finite effects, **94** genes with `|Δlog2FC| >= 0.5` (**0.58%** of shared genes), and **36** with `|Δlog2FC| >= 1` (**0.22%**). The predeclared sensitivity-warning guide crossed: log2fc_pearson. Pearson falls below the guide, while median and 95th-percentile changes remain small; the warning reflects an unstable effect tail rather than a broad change across most genes. Biological influence is **not** a retrospective technical reason to exclude EV_8.

## Model Diagnostics

Both fits had finite positive dispersions and gene-length-aware normalization factors. Primary median dispersion: **0.01875** (95th percentile **0.6131**); sensitivity median **0.01645** (95th percentile **0.5663**). Primary and sensitivity Cook's-distance diagnostic exceedance genes: **37** and **30**. EV_8 has **9** of the primary fit's **51** flagged gene–sample observations; these are model diagnostics, not a retrospective technical-exclusion rule. DESeq2 nominal p-value NAs: **37** and **30**; adjusted-p NAs: **1,601** and **1,587**, mostly from standard independent filtering of finite p-values. Count-replacement assay detected: primary **False**, sensitivity **False**. These diagnostics document standard DESeq2 behavior; no sample was manually removed and no outlier-handling default was changed.

Primary nominal p-value histogram counts in bins 0–0.1 through 0.9–1.0: **5005, 1798, 1467, 1254, 1231, 1140, 1093, 1095, 1030, 1067**. [Primary MA plot](../outputs/exp002/figures/fig05_primary_ma_plot.png) covers the full finite log2FC range. [Primary volcano](../outputs/exp002/figures/fig06_primary_volcano.png) uses threshold B and labels the first eight threshold-B genes by padj. There were **0** zero-padj points; the plotting floor is 7.74e-50 and affects only such points. [Effect comparison](../outputs/exp002/figures/fig07_primary_vs_sensitivity_log2fc.png) shows all shared finite genes and the identity line in the full-range panel; the second panel explicitly zooms to ±2 log2FC for readability. No selected EXP001 genes were highlighted.

## Limitations

- One documented recipient NHDF donor lot; no donor-level generalization
- Independent EV-preparation count and assignment unknown
- The original Salmon index release is unverified; GENCODE v44 is compatible, not proven original
- Gene counts are estimated from Salmon transcript quantification, not original integer gene counts
- The two batches had different transcript universes; Strategy A retains only 189,509 exact-shared transcripts
- EV_8 remains a PCA outlier, but no technical defect was demonstrated; primary includes it
- No EXP001-versus-EXP002 biological validation or pathway comparison was performed in C3

## C3 Decision

**PASS WITH SENSITIVITY WARNING.** The count-based batch-adjusted models are technically interpretable under the restricted C1R design. At least one preregistered effect-sensitivity guide threshold was crossed; report both fits and retain EV_8 in the primary. Independent-study DE is complete; **cross-study biological validation has not been performed**. GSEA and EXP001 comparison are reserved for EXP002-C4.
