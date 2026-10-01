# SkinExo-AI EXP002-C1

## Objective

Verify the independent GSE251807 experiment, its biological replication, and the integrity of its sample-resolved quantification **before** any differential-expression or pathway analysis. This checkpoint does not assess EV effects.

## Study Provenance

- **Study:** “Investigation of gene expression changes in normal human dermal fibroblasts after exposure to bone marrow mesenchymal stromal cell secretome,” [GSE251807, NCBI GEO](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE251807); [BioProject PRJNA1055484](https://www.ncbi.nlm.nih.gov/bioproject/PRJNA1055484); [ENA run metadata](https://www.ebi.ac.uk/ena/portal/api/filereport?accession=PRJNA1055484&result=read_run&fields=run_accession%2Cexperiment_accession%2Csample_accession%2Csecondary_sample_accession%2Cstudy_accession%2Clibrary_strategy%2Clibrary_source%2Clibrary_selection%2Cinstrument_model%2Crun_alias%2Cexperiment_alias&format=tsv).
- **Primary paper:** Lei R, da Silva TB, Cui Z, Ye H. “Small extracellular vesicles from human bone marrow mesenchymal stromal cells enhance migration and regulate reparative gene expression in dermal fibroblasts.” *Scientific Reports* 15, 19383 (2025). [DOI 10.1038/s41598-025-04057-6](https://doi.org/10.1038/s41598-025-04057-6); [PMID 40461530](https://pubmed.ncbi.nlm.nih.gov/40461530/); [PMCID PMC12134064](https://pmc.ncbi.nlm.nih.gov/articles/PMC12134064/).
- **Organism / recipient:** *Homo sapiens*, primary normal human dermal fibroblasts (NHDFs), adult skin. The paper identifies PromoCell C-12302, lot 412Z029.2, passages 6–8 for RNA sequencing.
- **EV source / type:** Human bone-marrow mesenchymal stromal cells, PromoCell C-12974, lot 438Z012.1; small extracellular vesicle fraction (MSC-sEV).
- **Treatment:** MSC-sEV fraction at 30 µg/mL for 48 h in DMEM with 1% penicillin/streptomycin; comparator is the same medium without the fraction. Dose is reported as mass concentration of the secretome fraction, not a particle-number dose.
- **Readout:** Bulk RNA-seq. ENA describes RNA-Seq, transcriptomic source, cDNA selection, and Illumina NovaSeq 6000. The paper reports sequencing through Novogene and Salmon quantification through Galaxy Europe. The Salmon version and exact indexed transcriptome were not deposited.

The official GEO family SOFT record, ENA run report, 16 GEO per-sample quantifications, and the GEO normalized-count supplement were inspected locally under ignored `data/raw/exp002/`. The reproducible source URL for each quantification is in `data/metadata/GSE251807_samples.csv`. No FASTQ/SRA sequencing archive was downloaded.

## Independence from EXP001

GSE251807 is a different accession and publication from EXP001 GSE293186, with a bone-marrow MSC-sEV source, 48 h exposure, and a documented NHDF cell lot. EXP001 uses endothelial EVs at 72 h. No shared GSM, SRR, or reported donor lot was identified. It is an independent **study**, not an independent-donor replication of EXP001, and its different EV source/time limit direct comparability.

## Biological Design

The full GEO series contains 32 RNA-seq libraries across multiple secretome arms. This checkpoint selects exactly the 16 libraries needed for the predeclared MSC-sEV versus DMEM comparison: 8 MSC-sEV and 8 DMEM controls. The paper reports at least four biological replicates per treatment group and two analysis batches. The 16 selected libraries are balanced across batches:

| Batch | DMEM control | MSC-sEV | Total |
| --- | ---: | ---: | ---: |
| 1 | 4 | 4 | 8 |
| 2 | 4 | 4 | 8 |

The same **one documented recipient donor lot** and **one documented EV-source donor lot** underpin the comparison. Sixteen libraries must not be described as 16 independent human donors or 16 independent EV preparations.

## Sample Mapping

The table links GEO GSMs to ENA/SRA runs and official Salmon files. “Estimated fragments” is the sum of Salmon `NumReads`, rounded for display; it is not raw sequencing read depth. Full file URLs, BioSample IDs, and SRA experiment IDs are in the CSV metadata.

| GSM | SRR | Name | Condition | Batch | Estimated fragments |
| --- | --- | --- | --- | ---: | ---: |
| GSM7988505 | SRR27319328 | DMEM_1 | CTRL_DMEM | 1 | 46,177,469 |
| GSM7988506 | SRR27319327 | DMEM_2 | CTRL_DMEM | 1 | 54,866,028 |
| GSM7988507 | SRR27319326 | DMEM_3 | CTRL_DMEM | 1 | 47,900,707 |
| GSM7988508 | SRR27319325 | DMEM_4 | CTRL_DMEM | 1 | 38,368,803 |
| GSM7988509 | SRR27319324 | EV_1 | MSC_sEV | 1 | 44,915,445 |
| GSM7988510 | SRR27319323 | EV_2 | MSC_sEV | 1 | 48,625,091 |
| GSM7988511 | SRR27319322 | EV_3 | MSC_sEV | 1 | 39,674,793 |
| GSM7988512 | SRR27319321 | EV_4 | MSC_sEV | 1 | 51,905,207 |
| GSM7988517 | SRR27319316 | DMEM_5 | CTRL_DMEM | 2 | 69,206,920 |
| GSM7988518 | SRR27319315 | DMEM_6 | CTRL_DMEM | 2 | 61,427,144 |
| GSM7988519 | SRR27319314 | DMEM_7 | CTRL_DMEM | 2 | 58,674,360 |
| GSM7988520 | SRR27319313 | DMEM_8 | CTRL_DMEM | 2 | 50,633,880 |
| GSM7988521 | SRR27319312 | EV_5 | MSC_sEV | 2 | 61,341,207 |
| GSM7988522 | SRR27319311 | EV_6 | MSC_sEV | 2 | 57,186,322 |
| GSM7988523 | SRR27319310 | EV_7 | MSC_sEV | 2 | 53,348,085 |
| GSM7988524 | SRR27319309 | EV_8 | MSC_sEV | 2 | 95,330,727 |

Each of the 16 libraries has a unique GSM, BioSample, SRA experiment, and SRR run in the inspected records. There is one run per library. Sample suffixes such as `DMEM_1` and `EV_1` are **not** documented pairing keys.

## Recipient Donors

The primary paper identifies one adult NHDF product lot (412Z029.2). The individual donor's demographic/identifier metadata are not disclosed. Thus the verifiable donor count is **one documented lot**. The 16 author-described biological replicates appear to be separate recipient-cell cultures/wells within that lot; the exact well-to-library records were not deposited.

## EV Source

The source is one documented hBM-MSC product lot (438Z012.1). The number of independently isolated MSC-sEV preparations, and which preparation was applied to each RNA-seq well, are **unknown**. EV characterization replicates elsewhere in the paper do not establish independent EV preparations for these 16 RNA-seq libraries.

## Batch Structure

GEO labels batch 1 and batch 2 for every sample. Each contains four DMEM and four MSC-sEV libraries. The publication acknowledges a batch effect and includes batch in its analysis design; that is provenance, not a new result generated here. The quantification files themselves also differ systematically in their transcript identifier sets by batch (see below).

## Biological vs Technical Replication

The paper calls the RNA-seq samples biological replicates. Here the **provisional experimental unit** is a separately cultured NHDF well/sample, nested within one recipient donor lot. The deposit identifies no repeated sequencing of one BioSample or SRA experiment among the selected libraries, so **zero technical replicates are identified**; undisclosed split libraries or shared EV aliquots cannot be excluded. No recipient-donor replication and no confirmed independent EV-preparation replication are available. A matched/paired EV-control design is **not documented**.

## Quantification

All 16 official per-sample GEO files are readable gzip TSV files with columns `Name`, `Length`, `EffectiveLength`, `TPM`, and `NumReads`. `Name` is a **versioned Ensembl transcript ID** (ENST), and `NumReads` contains fractional Salmon estimates. These are transcript estimates, not original integer gene counts. The separate 32-sample GEO `GSE251807_normalised_counts.csv.gz` has ENSG rows and fractional normalized values; it is **not** suitable as raw count input.

Within each batch, all eight files have identical transcript ID sets. Across batches, they differ:

| Check | Batch 1 | Batch 2 |
| --- | ---: | ---: |
| Transcripts per file | 194,142 | 194,182 |
| Exact versioned IDs shared across batches | 189,509 | 189,509 |
| IDs exclusive to that batch | 4,633 | 4,673 |

For shared IDs in representative files, transcript lengths agreed; the ID-set difference remains substantive. It is consistent with differing transcriptome/index definitions, but the precise cause is **unverified**. No cross-batch matrix was constructed by assuming row-order or ID equivalence.

Across selected files: 0 missing, 0 nonnumeric, 0 negative quantified values, and 0 duplicate transcript IDs within a file. The sums of estimated assigned fragments range from 38,368,803 to 95,330,727 (median 52,626,646; max/min 2.48). `EV_8` is 1.81 times the median and merits sequencing-depth QC in C2; it has not been removed.

## Transcript-to-Gene Mapping

The paper gives reference **genome assembly GRCh38.p14**, but not the exact Salmon transcriptome index, GENCODE/Ensembl annotation release, versioned transcript-to-gene map, or Salmon version. A GRCh38.p14 genome designation alone does not identify the transcriptome used for Salmon. The two batch-specific transcript ID sets further prevent assuming one common version-matched mapping. **No gene-level count estimates were reconstructed in C1.** A future tximport-style reconstruction would require the correct per-batch transcript-to-gene provenance and an explicit harmonization strategy; fractional Salmon estimates must not be presented as raw integer counts.

## Statistical Unit

**Provisional primary unit:** one independently cultured recipient NHDF well/sample, within the single documented recipient donor lot. The unit is provisional because culture-well assignments and EV-preparation independence were not supplied at sample level. Donor is a fixed source context, not a replicated random effect. The deposited library count is not the donor-level sample size.

## Candidate Statistical Design

For a later count-based comparison, `~ batch + condition` is a **provisional candidate** because both conditions occur in both batches. It is not fitted or tested here. A paired/donor model is not justified from the available mapping; with one recipient donor lot, a donor term cannot estimate between-donor effects. The formula must be revisited after the reference/index and EV-preparation structure are clarified.

## Integrity Checks

| Check | Result |
| --- | --- |
| Expected / verified selected libraries | 16 / 16 |
| Condition mapping | 8 MSC-sEV / 8 DMEM; verified against GEO titles and characteristics |
| Batch allocation | 4 + 4 in each of two batches |
| Unique GSM / BioSample / SRX / SRR | Yes, 16 each |
| Official per-sample quantification complete/readable | Yes, 16 / 16 |
| Missing / nonnumeric / negative values | 0 / 0 / 0 |
| Duplicate transcript IDs within files | 0 |
| Identical transcript ID set **within** batch | Yes |
| Identical transcript ID set **between** batches | **No** |
| Condition fully confounded with batch | No |
| Condition fully confounded with recipient donor | No; only one donor lot in both arms, so donor effect cannot be estimated |
| Missing matched controls | No at group/batch level; individual pairing not established |
| Treatment allocation across batches | Balanced |

## Confounding Assessment

Condition and batch are not fully confounded by allocation. The transcript-reference change is **batch-aligned**, so any downstream gene-level reconstruction must account for a technical definition difference correlated with batch. Condition and recipient donor are not confounded because both arms use the same documented donor lot; the experiment nevertheless cannot show generalization across human donors. Unknown EV-preparation assignment may produce unrecognized preparation-level pseudoreplication or confounding. Sample-number matching cannot resolve it.

## Limitations

- One documented recipient donor lot and one documented EV-source lot; donor-level generalization is not available.
- Independent EV isolation count and application map are unknown.
- Batch-specific transcript sets and absent exact index/annotation metadata block a verified tx2gene mapping.
- Salmon `NumReads` are fractional estimates; the GEO gene-level supplement is normalized, not raw counts.
- One high assigned-fragment total (`EV_8`) requires later QC; no sample was removed.
- Independence from EXP001 is at the study/dataset level; EV source and treatment duration differ.

## C1 Decision

**REVIEW REQUIRED.** The 16 selected files are intact and the condition/batch layout is clear, but the batch-specific transcript references and unresolved EV-preparation/culture-unit detail prevent a fully verified gene-level reconstruction and final statistical design. Next action: obtain exact Salmon index/annotation and EV-preparation-to-library provenance from official records or authors, then reassess C1 before EXP002-C2. No differential expression, pathway analysis, or EXP001–EXP002 comparison was performed.
