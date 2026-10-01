# Public data availability

## Public accessions

SkinExo-AI v0.3 represents three analyzed transcriptomic contexts:

| Context | Public dataset | Role |
|---|---|---|
| CTX001 | NCBI GEO `GSE293186` | Endothelial-cell-derived EV → primary human dermal fibroblast, 72 h |
| CTX002 | NCBI GEO `GSE251807` | Bone-marrow MSC small EV → primary human dermal fibroblast, 48 h |
| CTX003 | NCBI GEO `GSE293956` | Human dermal fibroblast-derived EV → human dermal fibroblast, 72 h |

`GSE293957` is registered as the same-study hDF-EV miRNA cargo companion. It remains **available but unanalyzed** and is not used to create cargo-response causal links.

## What this repository does not redistribute

The public working tree excludes:

- raw FASTQ, SRA, BAM, or CRAM files;
- official full gene-count and transcript-quantification matrices;
- licensed publication PDFs;
- MSigDB GMT collection files and other large reference annotations;
- institutional-access records, authentication material, and local environments.

Raw and processed inputs remain available from their original public repositories where permitted. Source URLs, accessions, checksums, sample mappings, and analysis roles are recorded in checkpoint reports and metadata.

## Included derived artifacts

The repository includes project-generated, trackable artifacts needed to inspect and reproduce the competition result:

- differential-expression and ranked-enrichment result tables;
- small QC summaries and project-generated plots;
- normalized context, response, phenotype, and reliability metadata;
- the F2 component universe and long-form Response Atlas;
- R1 response matrices, masks, similarities, and explanations; and
- F1/F2/R1/A1 machine-readable checkpoint manifests.

These are derived analysis results, not source sequencing archives or full input expression matrices. The offline Explorer consumes only the Atlas, checkpoint, phenotype, and reliability artifacts listed in `app/data_loader.py`.

## Runtime boundary

The Explorer and retrieval CLI require no raw omics data, count matrix, publication PDF, institutional network, or internet connection. Re-running the upstream biological analyses is a separate workflow that requires users to obtain public inputs and permitted gene-set resources from their original sources.
