# SkinExo-AI

**Technical report — submission draft.** Current evidence ends at EXP001-C4. Sections marked TODO have no result yet. The project title, final abstract, and submission claims require participant review.

## Abstract

SkinExo-AI is developing an evidence-linked approach to study how extracellular vesicles (EVs) influence recipient skin-cell states. As an initial case study, we analyzed public RNA-seq data from primary human dermal fibroblasts exposed for 72 hours to endothelial-cell-derived EVs (ECEVs) or control conditions in [GSE293186](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE293186). Dataset integrity and sample-level quality checks passed. An independent DESeq2 analysis tested 16,271 genes and identified 2,032 genes at adjusted p < 0.05 and |log2 fold change| ≥ 1, with 995 higher and 1,037 lower in ECEV samples. A source-verified framework classified 16 literature records and four public datasets. Prespecified ranked enrichment found cell-cycle, chemotaxis, ECM, vascular/endothelial, and immune-annotation associations, with substantial limits on phenotype interpretation. Cross-dataset validation, predictive AI, and phenotype validation remain unfinished.

## 1. Problem and Motivation

EVs are cell-released particles that can carry molecular signals to recipient cells. Skin repair involves fibroblasts, keratinocytes, endothelial cells, immune cells, and extracellular matrix (ECM) remodeling. An observed molecular response in one recipient cell type is difficult to connect reliably to a tissue-level repair phenotype because studies differ in EV source, recipient model, assay, species, and time point. SkinExo-AI aims to make those links traceable to experimental evidence and to show where evidence is absent or conflicting.

## 2. Project Concept

Working architecture: **EV source → EV cargo → recipient cell → transcriptomic response → biological program → phenotype → supporting evidence**. The current implementation covers a verified EXP001 transcriptomic analysis, prespecified pathway analysis, and an evidence framework. Prediction and automated explainability components are **planned, not implemented**.

## 3. Dataset

EXP001 uses [NCBI GEO GSE293186](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE293186), associated with [Yuan et al., *Journal of Investigative Dermatology*, DOI 10.1016/j.jid.2025.10.584](https://pubmed.ncbi.nlm.nih.gov/41161638/). The official [gene-count archive](https://ftp.ncbi.nlm.nih.gov/geo/series/GSE293nnn/GSE293186/suppl/GSE293186_gene_count.csv.gz) is the primary computational input. The official [author DEG archive](https://ftp.ncbi.nlm.nih.gov/geo/series/GSE293nnn/GSE293186/suppl/GSE293186_ECEV_72hvsCTRL_72h_deg_all.csv.gz) was used **only after our DE analysis** for a concordance check. The two archives remain local under ignored `data/raw/` and must not be redistributed in the public repository. See [data provenance](../docs/compliance/DATA_PROVENANCE.md).

## 4. EXP001 Experimental Design

Primary human dermal fibroblasts, 72-hour comparison: **CTRL n=3** (GSM8878107–GSM8878109) versus **ECEV n=3** (GSM8878110–GSM8878112). The exact count-column mapping is in [GSE293186_samples.csv](../data/metadata/GSE293186_samples.csv). Positive log2 fold change below means higher expression in ECEV relative to CTRL.

## 5. Data Integrity

[C1](../reports/EXP001_C1_dataset_integrity.md) passed: 58,735 gene rows, six biological samples, three CTRL and three ECEV, `gene_id` as the stable identifier, zero missing count values, zero negative counts, zero duplicate gene IDs, and 26,636 genes with zero counts in all six samples. These are data-integrity results, not expression filtering or biological findings.

## 6. Sample-Level QC

[C2](../reports/EXP001_C2_sample_qc.md) used the unsupervised primary filter **CPM ≥ 1 in at least two samples**, retaining **14,755** genes for sample-level QC. Filtered log2(CPM + 1) data gave mean Pearson correlations of **0.9961** within CTRL, **0.9923** within ECEV, and **0.9532** between conditions. Sample PCA explained **86.59%** on PC1 and **5.90%** on PC2. [PCA](figures/fig01_transcriptomic_pca.png) and [robustness views](figures/fig02_pca_robustness.png) are exploratory; visual separation does not establish treatment causality. CPM/log-CPM was used for QC and plotting, not as the differential-expression model input.

## 7. Differential Expression

[C3](../reports/EXP001_C3_differential_expression.md) used raw integer counts with **DESeq2 1.42.0**, **R 4.3.3**, and **Bioconductor 3.18**. The contrast was ECEV versus CTRL with CTRL as reference. A prespecified count filter yielded **16,271 genes tested**. **6,612** had Benjamini–Hochberg adjusted p < 0.05; **2,032** additionally had |log2 fold change| ≥ 1 (**995 up**, **1,037 down**). These are differential transcript abundance results. The [MA plot](figures/fig03_ma_plot.png), [volcano plot](figures/fig04_differential_expression_volcano.png), and [heatmap](figures/fig05_de_heatmap.png) visualize the analysis; the heatmap's selected genes are not an independent statistical test. No individual gene is assigned a skin-repair role from differential expression alone.

## 8. Analytical Reproducibility

The source study's thresholded DEG table and our result shared **1,952** genes tested by us. Their log2 fold changes had **Pearson r = 0.99999979** and **100% direction concordance**. At the C3 threshold of adjusted p < 0.05 and |log2FC| ≥ 1, the tables shared **1,949** genes (**Jaccard = 0.895**, rounded). The source archive is a thresholded subset; filtering differences limit complete comparison. **This is analytical concordance with the source study, not independent biological validation.**

## 9. Evidence Framework

[C3.5](../reports/EXP001_C3_5_evidence_framework.md) verified **16 literature records** (including the EXP001 primary paper): **9 primary research/methods records** and **7 reviews**. It cataloged **four uniquely identified public datasets**. Study-level `DIRECT` evidence counts were **P=3**, **M=2**, **E=3**, **A=0**, **I=2**. One of the two I studies measured inflammation in a skin-chip model without EV treatment. No directly measured EV-induced angiogenesis endpoint was established in this screened set, so A remains zero; endothelial EV origin or review discussion is not a substitute for an assay. Different EV sources, cell types, and wound models are coded explicitly in the [evidence matrix](../data/metadata/skinexo_evidence_matrix.csv).

## 10. Biological Pathway Analysis

[C4](../reports/EXP001_C4_pathway_analysis.md) tested the unchanged C3 contrast against the C3.5 questions. All **16,271** C3-tested gene IDs formed the ORA background and DESeq2 Wald-statistic ranking. [MSigDB 2026.1.Hs](https://docs.gsea-msigdb.org/MSigDB/Release_Notes/MSigDB_2026.1.Hs/) GO Biological Process, Reactome, and Hallmark supplied **4,600** eligible sets after restricting to tested genes and size 15–500. Preranked GSEA was the **primary** pathway-level evidence; UP/DOWN hypergeometric ORA was secondary. Across all sets, **640** GSEA sets had estimated FDR < 0.05; ORA found **301 UP** and **438 DOWN** sets at adjusted p < 0.05. Overlapping terms are not independent findings.

The prespecified mapping yielded a strong ECEV-higher **cell-cycle transcriptional program** (Hallmark E2F Targets NES +3.18; G2M Checkpoint +3.01; both estimated FDR < 0.001), which does **not** establish increased proliferation. Mapped ECEV-lower terms included negative chemotaxis (NES −2.12, FDR 0.0015), collagen fibril organization (−1.99, 0.0145), and vascular-associated smooth-muscle proliferation (−2.06, 0.00524). An ECEV-higher IL-12/JAK–STAT annotation had NES +1.85, FDR 0.00359. These term labels do not establish fibroblast migration, collagen deposition, angiogenesis, or immune-cell behavior. No angiogenesis-named mapped term reached GSEA FDR < 0.05, and C3.5 had zero direct angiogenesis studies. Q6 was **not yet testable**: separate verified external regenerative-like and fibrotic-like directional signatures are still needed. [Pathway figure](figures/fig06_prespecified_pathways.png) and [evidence map](figures/fig07_skinexo_evidence_map.png) show the qualified results; complete tables and leading edges are in C4 outputs.

## 11. Cross-Dataset Validation

**TODO.** The dataset catalog identifies candidates, but no external dataset has been analyzed to validate the EXP001 response.

## 12. Predictive AI

**TODO.** No predictive model, performance estimate, or AI-derived skin-repair score has been produced.

## 13. Explainability

**Implemented now:** an auditable chain connecting study IDs, source links, EV source/cargo, recipient cells, measured programs, regenerative/fibrotic context, and evidence class (`SAME_DATASET`, external evidence, review synthesis, or hypothesis). The [19-gene bridge](../outputs/exp001/c3_literature_bridge.csv) retains absent evidence rather than assigning a role by name or DEG direction. C4 adds a reproducible, prespecified gene-set map, full ORA/GSEA tables, leading-edge genes, and a qualified evidence-integration table. **Planned:** externally tested model outputs and phenotype evidence. This architecture is not an explanation of a trained predictor.

## 14. Reliability and Limitations

The main RNA-seq comparison has **n=3 biological replicates per condition** and only one primary EXP001 dataset. Bulk RNA-seq averages across the sampled cell population. The strong author-table concordance reuses the same source data and is not independent validation. Literature evidence is heterogeneous across species, EV sources, recipient cells, and endpoints. Direct angiogenesis evidence is currently absent in the screened set. **17 of 19** inspected C3 genes had insufficient gene-specific evidence in that set; one had same-study direct evidence and one indirect external context. Visual PCA structure, differential expression, and gene-set enrichment do not demonstrate a wound-healing benefit. GSEA uses gene-set permutations and has finite p-value resolution; pathway labels and overlapping GO terms require contextual review. Q6 remains untested.

## 15. Reproducibility

Run C1, C2, and C3 using the existing scripts in `experiments/exp001/`: `01_dataset_integrity.py`, `02_sample_qc.py`, and `03_run_c3.sh` (which calls the R DESeq2 script and Python artifact builder). `03_5_build_evidence.py` regenerates the curated C3.5 CSV/JSON outputs from unchanged C3 artifacts. `04_pathway_analysis.py prepare` and `analyze` reproduce C4 using the source files and SHA-256 hashes documented in [the C4 manifest](../outputs/exp001/c4_gene_set_manifest.json). The Python environment is recorded in [requirements.txt](../requirements.txt); R/Bioconductor versions, package hashes, and setup are in [exp001_c3_r_environment.md](../configs/exp001_c3_r_environment.md) and [exp001_c3_r_packages.tsv](../configs/exp001_c3_r_packages.tsv). Source archives and GMT files must be obtained from the documented providers; they are excluded from Git.

## 16. Future Experimental Validation

**Planned only:** a skin-on-chip or comparable skin model could test selected, prespecified EV-response hypotheses using measured phenotypes. No skin-on-chip validation has been performed by this project.

## 17. Conclusion

The completed work establishes a documented, reproducible analysis of a public six-sample ECEV/CTRL fibroblast dataset, prespecified pathway-level associations, and a cautious literature framework. It does not establish a predictive AI system, independent cross-dataset replication, a causal pathway mechanism, or therapeutic benefit.
