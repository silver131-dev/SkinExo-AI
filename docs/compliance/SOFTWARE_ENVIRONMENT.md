# Software environment and reproducibility references

This document points to the existing environment records. No package was installed, upgraded, or reinstalled for Submission-S1.

## Python

- Existing virtual environment: `.venv/`, Python **3.12.3** as queried for S1.
- Pinned package snapshot: [requirements.txt](../../requirements.txt). Relevant entries include pandas 3.0.6, NumPy 2.5.3, SciPy 1.18.1, scikit-learn 1.9.1, and Matplotlib 3.11.2.
- C4 added **GSEApy 1.3.1** plus its pinned HTTP dependencies to the existing `.venv`; no separate virtual environment was created. GSEApy provides the established preranked GSEA implementation. ORA uses SciPy's hypergeometric distribution and the recorded Benjamini–Hochberg correction in the C4 script.
- C1/C2 and C3/C3.5 artifact scripts are in `experiments/exp001/`.

## R / Bioconductor

- C3 recorded **R 4.3.3**, **Bioconductor 3.18**, **DESeq2 1.42.0**.
- Reproducible setup and run instructions: [exp001_c3_r_environment.md](../../configs/exp001_c3_r_environment.md).
- Resolved package versions and downloaded archive SHA-256 values: [exp001_c3_r_packages.tsv](../../configs/exp001_c3_r_packages.tsv).
- Local extracted runtime: ignored `.r-env/`; entry point for C3 is `bash experiments/exp001/03_run_c3.sh` after obtaining and verifying official GEO inputs.

## Inputs and outputs

The [data provenance record](DATA_PROVENANCE.md) identifies official GEO URLs and distinct input roles. The checkpoint files under `outputs/exp001/` and reports under `reports/` record the completed analysis. C3.5 metadata regeneration uses `python experiments/exp001/03_5_build_evidence.py`; its literature classifications are curated source records, so rerunning the script does not constitute fresh literature verification. No C1–C3 script was run during S1.

C4 uses [exp001_c4_frozen_plan.json](../../configs/exp001_c4_frozen_plan.json), the official GMTs cached in ignored `data/raw/c4_gene_sets/`, and `python experiments/exp001/04_pathway_analysis.py prepare` followed by `python experiments/exp001/04_pathway_analysis.py analyze`. The prepare step writes the ranked list, gene-set manifest, and predefined term map before any enrichment computation. Source file hashes are checked at runtime. Gene-set permutation settings are frozen in the plan.

**TODO before public release:** test the published instructions from a clean checkout with separately acquired GEO inputs, verify archive hashes where applicable, and resolve which derived outputs are appropriate to publish.
