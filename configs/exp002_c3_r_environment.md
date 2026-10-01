# EXP002-C3 R and annotation environment

EXP002-C3 reused the repository's ignored `.r-env/` installation: **R 4.3.3**, **Bioconductor 3.18**, **DESeq2 1.42.0**, and **tximport 1.30.0**. The R/DESeq2 package set and SHA-256 manifest are in [exp001_c3_r_environment.md](exp001_c3_r_environment.md) and [exp001_c3_r_packages.tsv](exp001_c3_r_packages.tsv). tximport's pinned Ubuntu package and checksum are recorded in [exp002_c2_r_environment.md](exp002_c2_r_environment.md). No package was installed or upgraded for C3, and the Python `.venv` was unchanged.

The C2 `tximport_shared_gencode_v44.rds` object contains the **37,307 × 16** estimated gene count, TPM, and abundance-weighted effective-length matrices from the **189,509 exact-shared versioned transcripts**. `countsFromAbundance="no"`. `DESeqDataSetFromTximport` rounds fractional estimated counts internally and retains `avgTxLength`; DESeq2 then constructs positive gene-length-aware normalization factors. The count representation is **not original integer gene counts**. The original author Salmon index release remains unverified.

For symbols and gene biotypes, C3 used the official [GENCODE v44 chromosome/patch/haplotype/scaffold GTF](https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/gencode.v44.chr_patch_hapl_scaff.annotation.gtf.gz), matching the compatible GRCh38.p14 release. Its SHA-256 is recorded in [exp002_c3_annotation_source.json](exp002_c3_annotation_source.json). The gene-feature extractor found **70,116** unique annotated gene IDs and exact IDs for all **37,307** genes in the tximport object. The initially inspected main-chromosome GTF covered only 33,973 of these IDs; the complete scaffold GTF was therefore used for annotation. Both source GTF files and the extracted annotation CSV remain Git-ignored under `data/raw/exp002/` and `data/processed/exp002/`. Gene symbols are labels; `gene_id` remains the DE row identifier.

From the repository root, after C2 and C2R inputs exist and the official complete GTF has been placed in `data/raw/exp002/`, regenerate C3 with:

```bash
bash experiments/exp002/03_run_c3.sh
```

The orchestrator extracts annotation, runs a no-fit tximport/DESeq2 preflight, fits the frozen primary and sensitivity models, then creates robustness summaries and figures. It reads no EXP001 results and performs no GSEA. The sensitivity guide was written in [exp002_c3_robustness_plan.json](exp002_c3_robustness_plan.json) before either model was fitted.
