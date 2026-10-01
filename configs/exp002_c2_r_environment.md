# EXP002-C2 R import environment

EXP002-C2 reused the ignored local `.r-env/` R **4.3.3** / Bioconductor **3.18** environment documented in [EXP001-C3 R environment](exp001_c3_r_environment.md). This checkpoint added only Ubuntu Noble's pinned `r-bioc-tximport` **1.30.0+dfsg-1** package to that local environment; the Python `.venv` was not modified.

| Package | Version | Source | Archive SHA-256 |
| --- | --- | --- | --- |
| `r-bioc-tximport` | 1.30.0+dfsg-1 (Bioconductor tximport 1.30.0) | [Ubuntu Noble package](https://packages.ubuntu.com/noble/r-bioc-tximport), [Bioconductor tximport](https://bioconductor.org/packages/3.18/bioc/html/tximport.html) | `d4ca3ca0a18553ececc44ff50514d6759da0c31bf8adc5d1b62dbd7bbde0b5e8` |

The 89.5 KB `.deb` was downloaded to `/tmp` with `apt-get download r-bioc-tximport=1.30.0+dfsg-1`, hash-checked against the Ubuntu package metadata, then extracted with `dpkg-deb -x` into `.r-env/`. No system R installation was changed. The local R launcher is [02_run_r_aggregation.sh](../experiments/exp002/02_run_r_aggregation.sh). The R import uses `tximport(..., type="salmon", countsFromAbundance="no", ignoreTxVersion=FALSE)` with a base-R gzip importer; it preserves estimated gene counts, gene TPM, and effective lengths in an ignored `.rds` object and corresponding CSV files.

The complete C2 regeneration command is:

```bash
bash experiments/exp002/02_run_c2.sh
```

This command performs only exact-shared transcript preparation, gene aggregation, filtering, sample correlation, PCA, and figures. It does **not** run differential expression, GSEA, or cross-study validation.
