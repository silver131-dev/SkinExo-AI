# EXP003-C3 R environment

EXP003-C3 reuses the repository's ignored, pinned R environment documented for EXP001-C3: R **4.3.3**, Bioconductor **3.18**, DESeq2 **1.42.0**, and jsonlite **1.8.8**. The exact downloaded Ubuntu package versions and SHA-256 digests remain recorded in [exp001_c3_r_packages.tsv](exp001_c3_r_packages.tsv); no package was installed or upgraded for EXP003-C3.

The relocated environment is launched through [03_run_r.sh](../experiments/exp003/03_run_r.sh), which sets its local `R_HOME`, `R_LIBS_SITE`, and library paths. [03_run_c3.sh](../experiments/exp003/03_run_c3.sh) reproduces preparation, the frozen DESeq2 fit, and independent artifact generation.

The model uses official raw integer counts after the C2-frozen condition-blind filter. Display annotation comes from the official GENCODE v44 GRCh38.p14 comprehensive chromosome/patch/haplotype/scaffold GTF already present in the ignored raw-data cache. Its source checksum and mapping coverage are recorded in [exp003_c3_annotation_source.json](exp003_c3_annotation_source.json). The annotation does not alter the tested-gene universe.

No author DEG table, gene-set resource, EXP001 result, or EXP002 result is read by the C3 pipeline.
