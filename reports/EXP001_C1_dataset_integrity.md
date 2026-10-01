# SkinExo-AI EXP001-C1

## Dataset

GSE293186 — gene-count matrix for EXP001. This checkpoint checks data integrity only.

## Biological Design

Primary human dermal fibroblasts (*Homo sapiens*), three controls in exosome-depleted media and three samples treated with endothelial-cell-derived extracellular vesicles (ECEVs) in exosome-depleted media for 72 hours.

## Source Provenance

- [NCBI GEO series](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE293186) — design, six accessions and supplementary files.
- [NCBI GEO sample SOFT records](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE293186&targ=gsm&view=brief&form=text) — individual titles, organism, cell type, treatments and protocol.
- [Official count archive](https://ftp.ncbi.nlm.nih.gov/geo/series/GSE293nnn/GSE293186/suppl/GSE293186_gene_count.csv.gz) — downloaded to `data/raw/GSE293186_gene_count.csv.gz` (2,368,199 bytes).
- GEO also lists `GSE293186_ECEV_72hvsCTRL_72h_deg_all.csv.gz`; it was not downloaded or analyzed.

## Count Matrix Structure

- Format: gzip-compressed CSV; delimiter: comma.
- Shape: **58,735 rows × 16 columns**.
- Gene identifier: `gene_id`.
- Header: `gene_id, CTRL_72h_1, CTRL_72h_2, CTRL_72h_3, ECEV_72h_1, ECEV_72h_2, ECEV_72h_3, gene_name, gene_chr, gene_start, gene_end, gene_strand, gene_length, gene_biotype, gene_description, tf_family`.
- Six biological sample columns and nine gene-annotation columns; no normalization or filtering applied.

## Sample Mapping

| GEO sample | Count column | Condition |
| --- | --- | --- |
| GSM8878107 | CTRL_72h_1 | CTRL |
| GSM8878108 | CTRL_72h_2 | CTRL |
| GSM8878109 | CTRL_72h_3 | CTRL |
| GSM8878110 | ECEV_72h_1 | ECEV |
| GSM8878111 | ECEV_72h_2 | ECEV |
| GSM8878112 | ECEV_72h_3 | ECEV |

Full verified sample metadata is in `data/metadata/GSE293186_samples.csv`.

## Library Sizes

Sum of raw counts across every row for each sample:

| Count column | Library size |
| --- | ---: |
| CTRL_72h_1 | 23,645,819 |
| CTRL_72h_2 | 24,214,469 |
| CTRL_72h_3 | 19,055,060 |
| ECEV_72h_1 | 18,646,894 |
| ECEV_72h_2 | 19,390,686 |
| ECEV_72h_3 | 20,970,952 |

## Integrity Checks

- Gzip readable and checksum valid: **yes**
- Metadata and six-column mapping valid: **yes**
- Missing gene IDs/count values: **0**
- Non-numeric / non-integer count values: **0 / 0**
- Negative counts: **0**
- Duplicate gene IDs (beyond first occurrence): **0**
- Zero-count genes across all six samples: **26636**
- Unexpected sample columns: **none**

## Issues / Warnings

- 26636 genes have zero counts in all six samples; retained for C1

## C1 Decision

**PASS**. No biological effect is inferred at this checkpoint.
