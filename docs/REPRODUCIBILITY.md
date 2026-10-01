# SkinExo-AI reproducibility guide

This guide identifies the inputs and commands used for EXP001-C1 through C4. It records the completed analysis; DEV-C0 does not rerun it. Work from the repository root and inspect each checkpoint before proceeding to the next.

## Inputs and environments

- Obtain the official GSE293186 [gene-count archive](https://ftp.ncbi.nlm.nih.gov/geo/series/GSE293nnn/GSE293186/suppl/GSE293186_gene_count.csv.gz) as `data/raw/GSE293186_gene_count.csv.gz`. Obtain the [author DEG archive](https://ftp.ncbi.nlm.nih.gov/geo/series/GSE293nnn/GSE293186/suppl/GSE293186_ECEV_72hvsCTRL_72h_deg_all.csv.gz) only for C3 concordance after the independent DESeq2 result. Both are ignored by Git. [Provenance](compliance/DATA_PROVENANCE.md) and [sample metadata](../data/metadata/GSE293186_samples.csv) record the comparison.
- Python 3.12.3 and pinned packages are recorded in [requirements.txt](../requirements.txt). The local `.venv/` is ignored; use its Python when reproducing these commands.
- C3 requires R 4.3.3, Bioconductor 3.18, and DESeq2 1.42.0. See the [R environment procedure](../configs/exp001_c3_r_environment.md), [resolved package manifest](../configs/exp001_c3_r_packages.tsv), and [R launcher](../experiments/exp001/03_run_r.sh). The local `.r-env/` is ignored.
- C4 uses MSigDB v2026.1.Hs GO Biological Process, Reactome, and Hallmark symbol GMT files. Obtain them from the official URLs and verify SHA-256 values in the [gene-set manifest](../outputs/exp001/c4_gene_set_manifest.json). Cache them at the file names in [the C4 plan](../configs/exp001_c4_frozen_plan.json) under ignored `data/raw/c4_gene_sets/`. The plan records GSEApy 1.3.1 and all C4 settings.

## Checkpoint commands

```bash
.venv/bin/python experiments/exp001/01_dataset_integrity.py
.venv/bin/python experiments/exp001/02_sample_qc.py
bash experiments/exp001/03_run_c3.sh
.venv/bin/python experiments/exp001/03_5_build_evidence.py
.venv/bin/python experiments/exp001/04_pathway_analysis.py prepare
.venv/bin/python experiments/exp001/04_pathway_analysis.py analyze
```

| Checkpoint | Reproducibility detail | Result record |
|---|---|---|
| C1 | Validates gzip count matrix and exact six-column GEO mapping. | [C1 report](../reports/EXP001_C1_dataset_integrity.md), [checkpoint](../outputs/exp001/exp001_c1_integrity.json) |
| C2 | Unsupervised primary filter: CPM ≥ 1 in ≥ 2 samples. Uses full raw library totals for CPM and log2(CPM + 1) for exploratory correlations/PCA. | [C2 report](../reports/EXP001_C2_sample_qc.md), [checkpoint](../outputs/exp001/exp001_c2_qc.json) |
| C3 | Raw integer counts; count ≥ 10 in ≥ 3 samples; `design = ~ condition`, CTRL reference, ECEV versus CTRL Wald contrast. Author DEG data are used only after fitting for concordance. | [C3 report](../reports/EXP001_C3_differential_expression.md), [checkpoint](../outputs/exp001/exp001_c3_de.json) |
| C3.5 | Curated paper, evidence, and dataset records are encoded in the source script and [matrix](../data/metadata/skinexo_evidence_matrix.csv), with [dataset catalog](../data/metadata/skinexo_dataset_catalog.csv). Rerunning the script regenerates files; it does **not** independently repeat literature verification. | [C3.5 report](../reports/EXP001_C3_5_evidence_framework.md), [checkpoint](../outputs/exp001/exp001_c3_5_evidence.json) |
| C4 | DESeq2 Wald statistic ranks all 16,271 C3-tested gene IDs. ORA uses those IDs as background. The frozen plan records the term map, GSEA settings, correction to a Q5 lexical false match, source names, and checksums. GSEA is primary; ORA secondary. | [C4 report](../reports/EXP001_C4_pathway_analysis.md), [checkpoint](../outputs/exp001/exp001_c4_pathways.json) |

The external regenerative-like and fibrotic-like signatures required for Q6 were not verified, so Q6 was not tested. The authors' table and same-study literature cannot independently validate EXP001. No predictive model is present.
