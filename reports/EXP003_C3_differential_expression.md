# SkinExo-AI EXP003-C3

## Objective

Estimate the hDF-EV-associated transcriptomic contrast in CTX003 using the design and low-expression filter frozen before viewing differential-expression results. This checkpoint performs DE only. It does not run pathway analysis or compare CTX003 biologically with CTX001 or CTX002.

## Frozen C2 Design

- Samples: **6**, comprising **3 hDF-EV** and **3 control** libraries.
- Primary design: **`~ condition`**.
- Contrast: **hDF-EV versus control**.
- Positive log2 fold change: **higher expression in hDF-EV-treated hDF**.
- Frozen filter: **CPM ≥ 1 in at least 3 of 6 samples**.
- Threshold A: `padj < 0.05`.
- Threshold B: `padj < 0.05 AND |log2FC| >= 1`.
- Batch: `NOT_DOCUMENTED`; pairing: `NO_EVIDENCE / UNKNOWN`.

No batch, donor, pairing, or replicate-label covariate was introduced. The author DEG findings were not read or used to select any parameter.

## Input Matrix

The unchanged official `GSE293956_hDF_total_count.txt.gz` source was reconstructed with the validated C1 parser. It contains **1,048,575** physical data rows, of which **60,675** have valid nonblank biological gene identifiers and **987,900** form the confirmed contiguous trailing structural-padding block. Parsing retained all zero-count biological genes and removed only blank-identifier blank/NA padding.

Counts are complete nonnegative integers with unique versionless Ensembl gene IDs. The source checksum remained `f30d382112d04c9e3f147fc350f8f58e6306da414a617b5cd4dd52c1fd8ec76d`.

GENCODE v44 / GRCh38.p14 official comprehensive GTF gene features were used only for display annotation through exact versionless stable-ID matching. Symbols were available for **13,771/13,874** tested genes. The original count-generation annotation release is unknown, and annotation did not alter the analysis universe.

## Filtering

- Genes before DE filtering: **60,675**.
- Frozen condition-blind rule: **CPM >= 1 in at least 3 of 6 samples**.
- Genes retained and tested: **13,874**.

The count agrees exactly with C2. No alternate filter was selected after viewing results.

## Statistical Framework

DESeq2 negative-binomial GLM with standard size-factor and dispersion estimation, Wald testing, and Benjamini–Hochberg adjusted p-values. The fit used **R version 4.3.3 (2024-02-29)**, Bioconductor **3.18**, and DESeq2 **1.42.0**.

`results(dds, contrast = c("condition", "HDF_EV", "CONTROL"), alpha = 0.05, pAdjustMethod = "BH")` was evaluated with standard Cook's-distance handling and independent filtering. Fold changes are unshrunken DESeq2 estimates.

## Differential Expression

- [Complete DE table](../outputs/exp003/differential_expression_all.csv): **13,874** genes.
- Threshold A (`padj < 0.05`): **25** genes.
- [Threshold-B table](../outputs/exp003/differential_expression_significant.csv): **20** genes.
- Threshold-B higher in hDF-EV: **20**.
- Threshold-B lower in hDF-EV: **0**.
- NA p-values / adjusted p-values: **0 / 0**.

Top hDF-EV-higher threshold-B genes by adjusted p-value, ties by stable gene ID:

| Rank | Gene ID | Symbol | baseMean | log2FC | padj |
| ---: | --- | --- | ---: | ---: | ---: |
| 1 | ENSG00000112096 | UNMAPPED | 7584.24 | +2.234 | 7.27e-73 |
| 2 | ENSG00000124875 | CXCL6 | 404.31 | +2.659 | 1.83e-53 |
| 3 | ENSG00000163739 | CXCL1 | 102.26 | +3.090 | 5.56e-23 |
| 4 | ENSG00000090339 | ICAM1 | 111.36 | +2.370 | 1.49e-17 |
| 5 | ENSG00000118503 | TNFAIP3 | 242.11 | +1.495 | 5.8e-15 |
| 6 | ENSG00000125730 | C3 | 3387.46 | +1.718 | 5.47e-14 |
| 7 | ENSG00000138821 | SLC39A8 | 606.06 | +1.141 | 5.44e-11 |
| 8 | ENSG00000108691 | CCL2 | 428.57 | +2.032 | 9.9e-11 |
| 9 | ENSG00000100906 | NFKBIA | 421.21 | +1.124 | 2.45e-09 |
| 10 | ENSG00000135373 | EHF | 94.14 | +1.963 | 1.47e-08 |

Top hDF-EV-lower threshold-B genes by adjusted p-value:

No genes met threshold B in this direction.

The absence of threshold-B downregulated genes was retained; thresholds were not relaxed. The gene list is a statistical contrast and has not been converted into P/M/E/A/I evidence.

[Figure 5](../outputs/exp003/figures/fig05_ma_plot.png) shows mean normalized count versus unshrunken log2 fold change over the full finite range. [Figure 6](../outputs/exp003/figures/fig06_volcano.png) uses threshold B for classes. Volcano labels are the ten smallest adjusted p-values among threshold-B genes, ties by gene ID, without manual biological selection.

## Model Diagnostics

- Dispersion fit: **parametric**; final median **0.03681**, 95th percentile **0.1188**, range **0.008952–3.506**.
- Nonfinite gene estimates / fitted trends: **0 / 0**.
- Nonconverged coefficient fits: **0**.
- Cook's diagnostic cutoff: **18**; genes/observations exceeding it: **0 / 0**.
- Count replacements: **none**; no p-value was set to NA by outlier handling.
- P-value decile counts from `[0,0.1)` through `[0.9,1]`: **274, 348, 566, 783, 1035, 1367, 1769, 2198, 2625, 2909**; median finite p-value **0.7361**.
- Independent filtering: enabled, baseMean threshold **11.1436**, theta **0**; finite p-values with NA padj: **0**.

The parametric dispersion fit completed with finite estimates and full coefficient convergence. Size factors were close to one. The right-heavy p-value distribution does not show a broad anti-conservative shift; a small low-p-value tail supplies the significant calls.

## Replicate-Label Structure

C2 PC1 replicate-label-associated structure remains unexplained. hDF_EVs_1 had the largest Cook-maximum attribution (6,023/13,874 genes; 43.4%), but no Cook's distance exceeded the DESeq2 diagnostic cutoff (18), no p-value was suppressed, and all 20 threshold-B genes had every EV normalized count above every control normalized count. The suffix labels were not modeled as batch or pairing.

The higher Cook-maximum attribution for the replicate-1-labeled samples preserves the C2 reliability concern. It does not establish a batch or pair, and no alternative model was fitted. The lack of Cook cutoff exceedances and the direction consistency across all six normalized libraries indicate that the threshold-B calls are not attributable solely to one sample. This check is descriptive and does not remove the underlying design uncertainty.

## Reliability Limitations

- n = 3 libraries per condition.
- Recipient donor count and donor-to-library mapping are unknown.
- EV-preparation independence and preparation-to-library mapping are unknown.
- Pairing is unknown; matching suffixes were not modeled as pairs.
- Batch is not documented; no batch term was fitted.
- Exact control medium and vehicle are unknown.
- The dominant C2 PC1 replicate-label-associated structure remains unexplained.
- The original count-generation annotation release is unknown.
- No donor-level or EV-preparation-level generalization is supported.
- No pathway or cross-context validation has yet been performed.

## Claim Boundaries

These results estimate a conditional six-library transcriptomic contrast at 72 h. They do not demonstrate proliferation, migration, ECM remodeling, vascular interaction, inflammation, wound healing, therapeutic efficacy, cargo causality, donor-level reproducibility, or cross-context conservation. Pathway interpretation is reserved for EXP003-C4 under the frozen endpoint plan.

The primary SkinExo result was saved without accessing or comparing author-reported DEG results. Author agreement is not part of the C3 decision.

## C3 Decision

**PASS WITH LIMITATIONS.** The frozen model fit reproducibly, all 13,874 genes produced finite p-values, dispersion estimation and coefficient fitting completed, and no Cook's-distance cutoff exceedance or critical single-sample failure occurred. Biological interpretation remains materially limited by the unexplained PC1 structure and unresolved donor, EV-preparation, pairing, batch, and control-medium metadata.

CTX003 remains `PLANNED`; its P/M/E/A/I transcriptomic response states remain `UNKNOWN`.
