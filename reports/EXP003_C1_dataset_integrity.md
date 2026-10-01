# SkinExo-AI EXP003-C1

## Objective

Verify the official GSE293956 human dermal fibroblast count matrix and determine whether its valid biological portion is technically suitable for later count-based differential expression. C1 performs dataset-integrity checks only. It does not filter genes, normalize counts, run sample QC/PCA, fit a statistical model, test differential expression, analyze pathways, inspect HaCaT counts, or alter CTX003 response states.

## Source

The sole expression input is the official NCBI GEO supplementary file [GSE293956_hDF_total_count.txt.gz](https://ftp.ncbi.nlm.nih.gov/geo/series/GSE293nnn/GSE293956/suppl/GSE293956_hDF_total_count.txt.gz), downloaded unchanged to the Git-ignored path `data/raw/exp003/GSE293956_hDF_total_count.txt.gz`. No HaCaT matrix, FASTQ, `RAW.tar`, or GSE293957 cargo data were downloaded.

- HTTP availability: **200 OK**
- Compressed file size: **491,697 bytes**
- Gzip integrity: **PASS**
- SHA-256: `f30d382112d04c9e3f147fc350f8f58e6306da414a617b5cd4dd52c1fd8ec76d`
- Git ignore rule: `.gitignore:3`, `data/raw/*`

The original gzip file was not rewritten. All structural handling is implemented in the [C1 integrity script](../experiments/exp003/01_dataset_integrity.py).

## Matrix Structure

The file is tab-delimited with seven columns: gene identifier `name` plus six expression columns.

```text
name  hdfcon-2  hdfcon-3  hdfexo10-2  hdfexo10-3  hdfcon  hdfexo10
```

The physical file contains **1,048,575 data lines**, exactly the Excel worksheet row limit minus one header row. The populated biological block contains **60,675 gene rows**. Physical data rows **60,676 through 1,048,575** are a contiguous **987,900-row structural padding block**. Every padding row has the single uniform expression-cell pattern:

```text
gene ID: blank
hdfcon-2: blank
hdfcon-3: blank
hdfexo10-2: blank
hdfexo10-3: blank
hdfcon: #N/A
hdfexo10: #N/A
```

There are no blank-identifier rows within the valid block and no populated row after padding begins. This establishes worksheet padding rather than missing biological observations.

The reproducible parsing rule excludes a row only when it is in the contiguous trailing block, its gene identifier is blank, and every expression cell is blank or an explicit NA token (`NA`, `N/A`, `#N/A`, or `NULL`). Any non-padding row after the block begins is an error. Every row with a nonblank gene identifier is retained, including genes with six zero counts. The parser does not modify the source or create a filtered biological matrix.

The matrix has no annotation columns. GEO describes the supplementary content as raw counts per sample, and all valid values are nonnegative integers. C1 therefore classifies the values as **raw-integer-count compatible**. It does not infer the exact gene-counting software beyond GEO's reported GRCh38/HISAT2 processing provenance.

## Sample Mapping

All six expression columns map one-to-one to the six D0 hDF records in [GSE293956_samples.csv](../data/metadata/GSE293956_samples.csv). Conditions come from authoritative GEO sample metadata, not column position.

| Matrix column | GEO sample | GSM | SRR | BioSample | Condition | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `hdfcon-2` | `hDF_con_2` | GSM8895187 | SRR33006698 | SAMN47817690 | CONTROL | VERIFIED |
| `hdfcon-3` | `hDF_con_3` | GSM8895188 | SRR33006697 | SAMN47817689 | CONTROL | VERIFIED |
| `hdfexo10-2` | `hDF_EVs_2` | GSM8895190 | SRR33006695 | SAMN47817687 | HDF_EV | VERIFIED |
| `hdfexo10-3` | `hDF_EVs_3` | GSM8895191 | SRR33006694 | SAMN47817686 | HDF_EV | VERIFIED |
| `hdfcon` | `hDF_con_1` | GSM8895186 | SRR33006699 | SAMN47817691 | CONTROL | VERIFIED |
| `hdfexo10` | `hDF_EVs_1` | GSM8895189 | SRR33006696 | SAMN47817688 | HDF_EV | VERIFIED |

The `-2` and `-3` labels explicitly match replicate labels 2 and 3 within each GEO arm. The unsuffixed control and EV columns map to the only remaining label, replicate 1, within their respective arms. This is an unambiguous one-to-one arm/label mapping, but it is not a deposited explicit column-to-GSM key and does not prove replicate independence. The machine-readable result is [c1_sample_mapping.csv](../outputs/exp003/c1_sample_mapping.csv).

## hDF-only Verification

The expression header contains only `hdfcon` and `hdfexo10` labels: three control and three hDF-EV columns. It contains no HaCaT-named column and matches the separate hDF file described by all six hDF GEO sample records. The HaCaT matrix was not needed to resolve an ambiguity and was not downloaded.

## Count Integrity

Checks on the **60,675 valid gene rows** found:

| Check | Count |
| --- | ---: |
| Missing expression values | 0 |
| Negative values | 0 |
| Nonnumeric values | 0 |
| Noninteger values | 0 |
| Malformed-width rows | 0 |

The `#N/A` values in the 987,900 padding rows are documented as physical worksheet structure and are not counted as biological expression values. No value was rounded or imputed.

## Gene Identifiers

The `name` column contains **60,675 unique, nonmissing, versionless Ensembl gene IDs** matching `ENSG` followed by digits. Duplicate identifiers: **0**. Missing identifiers in the valid matrix: **0**. No annotation mapping was performed.

## Zero-Count Structure

- Genes with zero counts across all six samples: **29,470**
- Genes with a nonzero count in at least one sample: **31,205**
- Total valid gene rows: **60,675**

All-zero gene rows remain part of the original biological matrix and are not filtered at C1. They cannot match the padding rule because they carry nonblank Ensembl IDs.

## Library Sizes

Raw column sums, before filtering or normalization:

| Sample | Condition | Library size |
| --- | --- | ---: |
| hDF_con_1 | CONTROL | 14,756,355 |
| hDF_con_2 | CONTROL | 16,185,815 |
| hDF_con_3 | CONTROL | 15,651,359 |
| hDF_EVs_1 | HDF_EV | 15,728,751 |
| hDF_EVs_2 | HDF_EV | 16,580,504 |
| hDF_EVs_3 | HDF_EV | 16,735,394 |

Minimum: **14,756,355**. Maximum: **16,735,394**. Maximum/minimum ratio: **1.1341143528**. These are descriptive integrity totals only. The machine-readable table is [c1_library_sizes.csv](../outputs/exp003/c1_library_sizes.csv).

## Duplicate Checks

Sample column names are unique. No pair of the six valid count vectors is exactly identical. Exact duplicate sample columns: **0**. Duplicate Ensembl gene IDs: **0**. Correlation and broader sample-quality assessment are outside C1.

## Metadata Concordance

The valid matrix agrees with GEO and D0: six hDF libraries, three hDF-EV and three controls, kept separate from six HaCaT libraries in the full series. The `exo10` label is consistent with the paper's 10 µg/mL exposure, while numeric dose remains paper-derived because GEO does not state it numerically. The paper reports 72 h and GEO reports three days. No mismatch in cell type, arm count, or duration was identified.

The physical Excel-sized padding was not described in GEO. It is now recorded explicitly and handled deterministically without changing the deposited file or removing any identified gene.

## Biological Design Limitations

- Recipient donor count, pooling, identities, and donor-to-library mapping remain **UNKNOWN**.
- Independent EV preparation count, pooling, and preparation-to-library mapping remain **UNKNOWN**.
- Exact RNA-seq control medium, vehicle, and recipient EV-depleted-serum status remain **UNKNOWN**.
- Pairing and batch structure remain **UNKNOWN**.
- Numbered sample labels and distinct archive accessions do not establish independent donor or EV-preparation replication.
- The unsuffixed matrix columns are mapped to replicate-1 labels by one-to-one elimination within each arm, not an explicit deposited key.

These limitations constrain the later statistical design and biological generalization but do not invalidate the clean count values at C1.

## DE Suitability

**SUITABLE_WITH_LIMITATIONS.** After removal of the strictly defined structural padding during parsing, the matrix supplies six unambiguously mapped hDF columns with unique versionless Ensembl IDs and complete nonnegative integer counts. It is technically suitable for a later count-based DE workflow. C2 must assess sample quality and statistical design while retaining the unresolved donor, EV-preparation, control, pairing, and batch limitations.

## C1 Decision

**PASS.** The official hDF matrix passes gzip, sample mapping, cell-type, count-value, identifier, library-size, and exact-duplicate integrity checks. The original source remains unchanged and ignored. [The C1 checkpoint JSON](../outputs/exp003/exp003_c1_integrity.json) records both **1,048,575 original physical data rows** and **60,675 valid biological gene rows**, plus the 987,900-row padding audit. CTX003 remains `PLANNED` and `AVAILABLE_NOT_ANALYZED`; no transcriptomic response state was populated. Work stops before EXP003-C2.
