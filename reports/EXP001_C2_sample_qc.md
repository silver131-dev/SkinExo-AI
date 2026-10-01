# SkinExo-AI EXP001-C2

## Objective

Assess whether the six GSE293186 RNA-seq samples are suitable for later analysis and describe their sample-level structure. No biological effect is tested here.

## Input Data

- C1 checkpoint: **PASS**; [C1 integrity report](EXP001_C1_dataset_integrity.md).
- [NCBI GEO series](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE293186) and the official gene-count matrix, with sample mapping from `data/metadata/GSE293186_samples.csv`.
- 58,735 original genes; 26,636 all-sample zero-count genes; 32,099 genes with at least one nonzero count; six samples (3 CTRL, 3 ECEV).

## Filtering

All rules were evaluated on raw counts or library-size CPM without condition labels:

| Rule | Definition | Genes retained |
| --- | --- | ---: |
| A | count >= 10 in at least 2 samples | 16,906 |
| B | count >= 10 in at least 3 samples | 16,271 |
| C | CPM >= 1 in at least 2 samples | 14,755 |

**Primary rule: C: CPM >= 1 in at least 2 samples**, retaining **14,755** genes. With six samples and library sizes spanning 18,646,894–24,214,469, a CPM threshold accounts for sequencing-depth differences and expression in two samples avoids retaining one-sample signals. This rule was chosen without examining CTRL/ECEV separation. The filtered raw counts are saved unchanged. The [edgeR user guide](https://bioconductor.org/packages/release/bioc/vignettes/edgeR/inst/doc/edgeRUsersGuide.pdf) motivates filtering low-expression genes and using CPM to account for library size; this fixed C2 rule is not an edgeR `filterByExpr` run.

## Normalization for QC

CPM = raw count / **original full-library count total** × 1,000,000. Correlation and PCA use log2(CPM + 1) for the filtered genes. CPM and log-CPM here are for QC and visualization only. They do not replace DESeq2 or TMM normalization for differential expression. C3 requires an appropriate count-based statistical framework using raw counts; see the [DESeq2 documentation](https://bioconductor.org/packages/release/bioc/vignettes/DESeq2/inst/doc/DESeq2.html).

## Library Size QC

| Sample | Raw-count library size |
| --- | ---: |
| CTRL_72h_1 | 23,645,819 |
| CTRL_72h_2 | 24,214,469 |
| CTRL_72h_3 | 19,055,060 |
| ECEV_72h_1 | 18,646,894 |
| ECEV_72h_2 | 19,390,686 |
| ECEV_72h_3 | 20,970,952 |

Minimum **18,646,894**; maximum **24,214,469**; median **20,180,819**; max/min ratio **1.299**. [Figure 1](../outputs/exp001/figures/fig01_library_size.png). Library size is a technical QC quantity, not evidence of a biological effect.

## Sample Correlation

Pearson correlation of filtered log2(CPM + 1), calculated across genes: mean within CTRL **0.9961**, mean within ECEV **0.9923**, mean between conditions **0.9532**. These are descriptive summaries; no significance tests were run. [Correlation matrix](../outputs/exp001/sample_correlation.csv) and [Figure 2](../outputs/exp001/figures/fig02_sample_correlation.png).

## PCA

Samples are observations and filtered genes are features. Condition labels entered the plot only after fitting PCA. PC1 explains **86.59%** and PC2 **5.90%** of variance.

| Sample | Condition | PC1 | PC2 |
| --- | --- | ---: | ---: |
| CTRL_72h_1 | CTRL | -37.378 | 0.681 |
| CTRL_72h_2 | CTRL | -37.391 | -0.863 |
| CTRL_72h_3 | CTRL | -40.596 | -4.166 |
| ECEV_72h_1 | ECEV | 47.293 | -15.537 |
| ECEV_72h_2 | ECEV | 27.461 | 18.910 |
| ECEV_72h_3 | ECEV | 40.611 | 0.974 |

[Coordinates](../outputs/exp001/pca_coordinates.csv) and [Figure 3](../outputs/exp001/figures/fig03_pca.png).

## PCA Robustness

Variable genes were ranked by variance across all six log-CPM sample values, without condition labels. PCA was refit independently for each feature set. The distance-rank correlation compares the 15 sample-pair distances in the first two PCs to the all-filtered result; nearest-neighbor agreement is a second descriptive stability check. PCA axes can rotate or flip, so raw PC signs are not compared.

| Feature set | Genes | PC1 | PC2 | Distance-rank Spearman vs all | Same nearest neighbor vs all | Nearest neighbor in same condition |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| all filtered | 14,755 | 86.6% | 5.9% | 1.000 | 6/6 | 6/6 |
| top 5000 variable | 5,000 | 91.0% | 4.3% | 1.000 | 6/6 | 6/6 |
| top 2000 variable | 2,000 | 95.1% | 2.6% | 1.000 | 6/6 | 6/6 |

[Robustness coordinates](../outputs/exp001/pca_robustness.csv) and [Figure 4](../outputs/exp001/figures/fig04_pca_robustness.png). The sample layout is stable across the three unsupervised feature sets: all six nearest neighbors match the all-gene PCA, and sample-pair distance ranks remain similar. CTRL and ECEV occupy distinct regions in these plots. These comparisons are descriptive and do not establish treatment causality.

## Sample-Level Warnings

- No sample crossed the prespecified heuristic flags for library size, mean correlation, replicate consistency, PCA isolation, or PCA distance-rank instability.

No sample was removed. Heuristic flags are prompts for review, not formal outlier tests.

## Limitations

- **n = 6** (three samples per condition) is small, so sample-level summaries and outlier heuristics are unstable.
- PCA is exploratory; visual separation does not establish treatment causality.
- CPM/log-CPM is used for QC and visualization; differential expression requires separate count-based modeling in C3.
- Pairwise correlations and PCA distances are descriptive; no differential-expression testing, pathway analysis, gene-set scoring, or supervised modeling was performed.

## C2 Decision

**PASS**. The decision reflects the stated sample-level QC heuristics only.
