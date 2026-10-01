# EXP001-C3 R environment

This checkpoint ran on Ubuntu 24.04 (amd64) with R **4.3.3**, Bioconductor **3.18**, and DESeq2 **1.42.0**. The DESeq2 package was Ubuntu's pinned `r-bioc-deseq2` build of the Bioconductor 3.18 release. The complete set of 80 downloaded `.deb` packages and SHA-256 digests is recorded in [exp001_c3_r_packages.tsv](exp001_c3_r_packages.tsv). The packages were extracted into the repository's ignored `.r-env/` directory; the existing Python `.venv` was not changed.

The top-level packages requested from the Ubuntu 24.04 archive were:

| Package | Ubuntu package version |
| --- | --- |
| `r-base-core` | `4.3.3-2build2` |
| `r-bioc-deseq2` | `1.42.0+dfsg-1` |
| `r-bioc-biocversion` | `3.18.1-1` |
| `r-cran-biocmanager` | `1.30.22+dfsg-2` |
| `r-cran-jsonlite` | `1.8.8+dfsg-1` |

On this unprivileged host, `apt-get --download-only --no-install-recommends` used a copy of `/var/lib/dpkg/status` and a user-owned archive cache. The resolved packages were extracted with `dpkg-deb -x` into `.r-env/`; no system R installation or Python package change was made. The package manifest captures the exact resolved versions and archive digests. Before reusing downloaded archives, verify their SHA-256 values against that manifest.

The download request was:

```bash
mkdir -p /tmp/skinexo-apt-cache/partial
cp /var/lib/dpkg/status /tmp/skinexo-dpkg-status
apt-get --assume-yes --download-only --no-install-recommends \
  -o Dir::State::status=/tmp/skinexo-dpkg-status \
  -o Dir::Cache::archives=/tmp/skinexo-apt-cache \
  install \
  r-base-core=4.3.3-2build2 \
  r-bioc-deseq2=1.42.0+dfsg-1 \
  r-bioc-biocversion=3.18.1-1 \
  r-cran-biocmanager=1.30.22+dfsg-2 \
  r-cran-jsonlite=1.8.8+dfsg-1
```

The exact dependency versions selected at execution time are in the manifest. A future Ubuntu mirror may choose newer dependencies; compare all downloaded archive hashes with the manifest before treating a later environment as identical.

Ubuntu's R package contains absolute `/etc/R` links. For the relocated environment, its configuration files were linked to the extracted `.r-env/etc/R` files and `Renviron.ucf` was copied there as `Renviron`. The packaged `Rscript` executable expects `/usr/lib/R`; [03_run_r.sh](../experiments/exp001/03_run_r.sh) instead launches the extracted R engine with local `R_HOME`, `R_LIBS_SITE`, and library paths.

To regenerate C3 from the two official GEO archives and the passed C1/C2 checkpoints:

```bash
bash experiments/exp001/03_run_c3.sh
```

The orchestrator runs [03_differential_expression.R](../experiments/exp001/03_differential_expression.R) first. That step reads only the count matrix and sample metadata, performs DESeq2, and saves the independent results. Then [03_c3_artifacts.py](../experiments/exp001/03_c3_artifacts.py) produces the remaining figures, author concordance, checkpoint JSON, and report. The author table is never an input to the DESeq2 model.

Official package references: [Bioconductor DESeq2](https://bioconductor.org/packages/3.18/bioc/html/DESeq2.html), [Bioconductor 3.18 release](https://bioconductor.org/news/bioc_3_18_release/), and [Ubuntu package archive](https://packages.ubuntu.com/noble/r-bioc-deseq2).
