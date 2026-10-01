# SkinExo-AI EXP001-C3

## Objective

Identify genes with evidence of differential expression between ECEV-treated and control primary human dermal fibroblasts after 72 hours.

## Dataset

- [NCBI GEO GSE293186](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE293186): six samples, three CTRL and three ECEV.
- C1 and C2 checkpoints: **PASS**. C3 reads the official raw integer count matrix and verified sample metadata, not log-CPM or the author DEG table.
- Gene ID (`gene_id`) is the stable row key. `gene_name` in the source matrix is preserved as `gene_symbol`; description, biotype, location, length and TF family are also preserved when available. Symbols may repeat across gene IDs.

## Statistical Framework

[DESeq2](https://bioconductor.org/packages/release/bioc/vignettes/DESeq2/inst/doc/DESeq2.html) negative-binomial count model, standard dispersion estimation, Wald test, and Benjamini–Hochberg adjusted p-values. R **R version 4.3.3 (2024-02-29)**, Bioconductor **3.18**, DESeq2 **1.42.0**. Package manifest and local setup are documented in `configs/exp001_c3_r_environment.md`.

## Filtering

- Genes before filtering: **58,735**.
- Fixed label-blind rule: **raw count >= 10 in at least 3 of 6 samples**.
- Genes after filtering and tested: **16,271**.
- Filtering was selected before examining differential-expression results. DESeq2's result-level independent filtering remains at its standard setting.

## Design

`design = ~ condition` with CTRL as the reference. All six biological samples are included; no sample was removed.

## Contrast Definition

`results(dds, contrast = c("condition", "ECEV", "CTRL"))`. **Positive log2FoldChange means higher expression in ECEV; negative means lower expression in ECEV.** Fold changes are unshrunken DESeq2 estimates.

## Differential Expression Results

- [Complete DE result table](../outputs/exp001/differential_expression_all.csv): **16,271** tested genes, sorted by padj with NA last.
- Threshold A (`padj < 0.05`): **6,612** genes.
- Threshold B (`padj < 0.05` and `|log2FC| >= 1`): **2,032** genes. [Threshold-B table](../outputs/exp001/differential_expression_significant.csv).
- Threshold B up/down: **995** / **1,037**.
- NA p-values / padj values: **0 / 0**.

## Upregulated Genes

Top 10 ECEV-higher genes by adjusted p-value among threshold-B genes (not manually selected):

| Gene ID | Symbol | log2FC | padj |
| --- | --- | ---: | ---: |
| ENSG00000019991 | HGF | +3.645 | 1.08e-217 |
| ENSG00000006468 | ETV1 | +3.212 | 7.9e-202 |
| ENSG00000131747 | TOP2A | +2.047 | 4.1e-172 |
| ENSG00000158747 | NBL1 | +1.978 | 7.84e-160 |
| ENSG00000149948 | HMGA2 | +2.054 | 3.04e-157 |
| ENSG00000139289 | PHLDA1 | +2.635 | 1.66e-137 |
| ENSG00000216775 | AL109918.1 | +2.906 | 1.91e-135 |
| ENSG00000141469 | SLC14A1 | +2.633 | 3.67e-135 |
| ENSG00000117724 | CENPF | +2.079 | 2.95e-133 |
| ENSG00000166825 | ANPEP | +2.209 | 1.69e-131 |

## Downregulated Genes

Top 10 ECEV-lower genes by adjusted p-value among threshold-B genes (not manually selected):

| Gene ID | Symbol | log2FC | padj |
| --- | --- | ---: | ---: |
| ENSG00000135069 | PSAT1 | -3.198 | 0 (underflow) |
| ENSG00000091986 | CCDC80 | -2.631 | 1.58e-186 |
| ENSG00000149591 | TAGLN | -2.216 | 8.69e-185 |
| ENSG00000180914 | OXTR | -3.034 | 2.61e-175 |
| ENSG00000151892 | GFRA1 | -5.032 | 5.11e-172 |
| ENSG00000115461 | IGFBP5 | -2.392 | 7.93e-171 |
| ENSG00000155511 | GRIA1 | -2.330 | 1.16e-156 |
| ENSG00000128165 | ADM2 | -3.885 | 2.46e-154 |
| ENSG00000151012 | SLC7A11 | -2.148 | 1.41e-150 |
| ENSG00000153993 | SEMA3D | -4.630 | 4.91e-146 |

## MA Plot

[Figure 5](../outputs/exp001/figures/fig05_ma_plot.png) shows DESeq2 mean normalized counts versus log2 fold change. Blue marks padj < 0.05. The y-axis spans **-9.018 to 9.018**, covering every finite fold change; no extreme gene was clipped.

## Volcano Plot

[Figure 6](../outputs/exp001/figures/fig06_volcano.png) plots log2FC against −log10(padj); up/down colors apply threshold B. Labels are the 10 most adjusted-significant threshold-B genes. One padj is numerically zero from floating-point underflow and is shown at a plotting floor of **1.08e-218**, one order of magnitude below the smallest positive padj. This changes its display coordinate only.

## Heatmap

[Figure 7](../outputs/exp001/figures/fig07_de_heatmap.png) shows the top **30** threshold-B genes by padj. Values use blind DESeq2 variance-stabilizing transformation, then row z-scores for display. Gene rows are clustered with average linkage and Euclidean distance; all six sample labels remain in metadata order. The heatmap is visualization, not a statistical test.

## Author DEG Concordance

Only after saving our DESeq2 result, the [official GEO author archive](https://ftp.ncbi.nlm.nih.gov/geo/series/GSE293nnn/GSE293186/suppl/GSE293186_ECEV_72hvsCTRL_72h_deg_all.csv.gz) was read for QA. It has **2,095** rows; empirically every row has padj < 0.05 and |log2FC| ≥ 1. It is a thresholded subset, not a complete author test table. The author per-sample raw count columns match the GEO count matrix in all compared cells (**0** mismatches).

- Author rows also tested by us: **1,952**; author rows excluded by our count filter: **143**.
- Pearson / Spearman correlation of shared log2FC: **1.000000 / 0.999999**.
- Fold-change direction concordance: **100.0%** of shared genes.
- Median / maximum absolute log2FC difference: **0.0012 / 0.0332**.
- Threshold-A overlap among shared genes: **1,951**. Threshold-B overlap: **1,949**; Jaccard index **0.895**.
- Our threshold-B genes absent from the author file: **83**. Author threshold-B genes absent from our significant table: **146** (143 not tested after our filter; 3 tested but below our threshold B).
- [Per-gene concordance table](../outputs/exp001/author_deg_concordance.csv) retains both result sets without overwriting our DE output.

These set differences are consistent with differing prefiltering and possibly DESeq2 processing choices; the author file does not document a complete analysis configuration, so their precise cause cannot be assigned here. Concordance checks external consistency and is **not independent biological validation**.

## Limitations

- **n=3 biological replicates per condition** limits precision and makes individual samples influential.
- Differential expression describes an association in this experimental comparison; transcriptomic differences alone do not establish wound-healing benefit.
- Large unshrunken log2FC values, especially at low expression, should be interpreted cautiously.
- The author archive is thresholded and cannot support a complete comparison of nonsignificant genes or the authors' total tested-gene universe.
- No GO, KEGG, Reactome, GSEA, SkinExo scoring, or AI modeling was performed.

## C3 Decision

**PASS**. The independent count-based analysis completed, and author-table QA found no raw-count mismatch and strong directional agreement. This decision does not establish treatment causality or wound-healing benefit.
