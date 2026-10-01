# Data provenance — SkinExo-AI submission draft

## Primary public dataset

- **Accession:** [NCBI GEO GSE293186](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE293186).
- **Source type:** third-party public research dataset, not team-generated data.
- **Associated publication:** [Yuan et al., *Journal of Investigative Dermatology*, DOI 10.1016/j.jid.2025.10.584](https://pubmed.ncbi.nlm.nih.gov/41161638/).
- **EXP001 comparison:** primary human dermal fibroblasts at 72 h, CTRL GSM8878107–GSM8878109 versus ECEV GSM8878110–GSM8878112. Verified column-level mapping is in [GSE293186_samples.csv](../../data/metadata/GSE293186_samples.csv).

| Official GEO supplementary file | Local role | Source URL |
|---|---|---|
| `GSE293186_gene_count.csv.gz` | **Primary computational input**: raw integer count matrix for C1 integrity, C2 QC, and C3 independent DESeq2 analysis. | [NCBI GEO archive](https://ftp.ncbi.nlm.nih.gov/geo/series/GSE293nnn/GSE293186/suppl/GSE293186_gene_count.csv.gz) |
| `GSE293186_ECEV_72hvsCTRL_72h_deg_all.csv.gz` | **QA / concordance only**: read after our C3 DE result was completed; never used to fit DESeq2 or select C3 reporting thresholds. | [NCBI GEO archive](https://ftp.ncbi.nlm.nih.gov/geo/series/GSE293nnn/GSE293186/suppl/GSE293186_ECEV_72hvsCTRL_72h_deg_all.csv.gz) |

The author table is a thresholded subset of the source study. High log2FC agreement with it is same-dataset analytical consistency, not independent biological validation. See [C3 report](../../reports/EXP001_C3_differential_expression.md).

## Other literature and dataset leads

The C3.5 [evidence matrix](../../data/metadata/skinexo_evidence_matrix.csv) and [dataset catalog](../../data/metadata/skinexo_dataset_catalog.csv) record external paper IDs, repository accessions, URLs, and model limitations. They were discovered as metadata only in C3.5. No external omics dataset was downloaded or analyzed for this submission scaffold.

## C4 gene-set definitions

C4 uses only the human [MSigDB v2026.1.Hs](https://docs.gsea-msigdb.org/MSigDB/Release_Notes/MSigDB_2026.1.Hs/) GO Biological Process (C5), Reactome (C2), and Hallmark (H) symbol GMT collections. The official collection/download page is [MSigDB Human Collections](https://www.gsea-msigdb.org/gsea/msigdb/collections.jsp). Exact direct-source URLs, file names, SHA-256 checksums, set counts, mapping rates, and release details are in [c4_gene_set_manifest.json](../../outputs/exp001/c4_gene_set_manifest.json). The three GMT files are cached under ignored `data/raw/c4_gene_sets/` and are **not copied into the public repository**. [MSigDB's license page](https://www.gsea-msigdb.org/gsea/msigdb_license_terms.jsp) states CC BY 4.0 base terms with additional terms for some collections; the user-facing publication should cite the source and review the current terms. No KEGG or external regenerative/fibrotic signature file was used.

## Redistribution and publication

Official biological archives remain under `data/raw/`, which is ignored by `.gitignore`; processed matrices and local environments are also ignored. The public repository should carry source code, small metadata, and team-generated plots rather than rehost raw GEO archives. **TODO:** review GEO record terms, source-paper figure rights, dataset licenses, and final repository contents before publication. This document records provenance and does not decide legal reuse rights.
