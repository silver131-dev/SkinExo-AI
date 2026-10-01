# SkinExo-AI EXP003-D0

## Objective

Determine whether GSE293956 can supply CTX003, an hDF-EV → primary human dermal fibroblast RNA-seq context. This is a metadata, design, and eligibility checkpoint. No count matrix, FASTQ, or cargo measurements were analyzed; no CTX003 P/M/E/A/I transcriptomic result was assigned.

## Study Provenance

[GEO GSE293956](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE293956) is titled *Mechanism of action of hDF-EVs on fibroblasts and keratinocytes [RNA-seq]*. Its submitters include Minjie Liu, Ganqin Ye, and Ruiyang Li, matching the [Liu et al. primary paper](https://pubmed.ncbi.nlm.nih.gov/40728022/) (DOI [10.1002/cbin.70063](https://doi.org/10.1002/cbin.70063)). GEO links [BioProject PRJNA1247494](https://www.ncbi.nlm.nih.gov/bioproject/PRJNA1247494); the official ENA BioProject record also cross-references `GSE293956` and `SRP576981`. GEO is public from 30 April 2026. Small official [GEO/ENA metadata snapshots](../data/metadata/exp003_d0_sources/) support the [sample table](../data/metadata/GSE293956_samples.csv). The locally held licensed article was consulted for methods; it remains Git-ignored and is not copied or quoted here.

## GSE293956

Organism: *Homo sapiens*. Library strategy: RNA-Seq with poly(A) mRNA selection and cDNA libraries, according to GEO sample records. Platform: Illumina NovaSeq 6000, `GPL24676`; reference assembly reported as GRCh38, with HISAT2 v2.1.0 in GEO's processing description. There are 12 distinct GSM, SRX, BioSample, and SRR identifiers, each with one listed ENA run and paired FASTQ links. Distinct accession numbers establish deposited libraries, not independent recipient donors, culture events, or EV preparations.

## Sample Structure

| Recipient | GEO sample names | Control | hDF-EV | Total | Processed matrix |
| --- | --- | ---: | ---: | ---: | --- |
| hDF | `hDF_con_1..3`, `hDF_EVs_1..3` | 3 | 3 | 6 | `GSE293956_hDF_total_count.txt.gz` |
| HaCaT | `HaCaT_con_1..3`, `HaCaT_EVs_1..3` | 3 | 3 | 6 | `GSE293956_HaCaT_total_count.txt.gz` |

The [all-sample table](../data/metadata/GSE293956_samples.csv) records GSM, SRX, SRR, BioSample, BioProject, cell type, arm, run links, processed-file mapping, and unresolved design fields. The suffixes 1–3 are labels only. No pairing or independence is inferred from matching suffixes.

## hDF Context

CTX003 selects only the six **primary hDF** libraries: three GEO `EVs` and three GEO `control`. The paper describes purified hDF-EV treatment at 10 µg/mL for 72 h. GEO says cells were co-cultured with purified EVs for three days but gives no numeric dose in sample or series metadata. The intended contrast is hDF-EV-treated hDF against same-cell-type control. Its statistical formula is not yet chosen; pairing and batch structure are unknown.

## HaCaT Context

The six HaCaT keratinocyte libraries also contain three controls and three hDF-EV samples. HaCaT is an immortalized cell line, a distinct recipient system. It is **not pooled with hDF** and receives no new context ID at D0. A later keratinocyte context would require its own design review.

## EV Source

The paper's methods describe hDFs isolated from pediatric preputial dermis and cultured through passages 3–5 for EV production. Source-cell conditioned medium was collected after 72 h in EV-depleted-serum medium. FBS was filtered at 0.22 µm and ultracentrifuged at 120,000 g for 18 h to prepare EV-depleted serum. Conditioned medium was cleared at 2,000 g for 10 min and 10,000 g for 30 min, filtered at 0.22 µm, then subjected to two 120,000 g, 90 min ultracentrifugations with a PBS wash. TEM, NTA, positive CD9/TSG101 and negative βIII-tubulin Western blot markers are reported. EV protein mass was measured by BCA. The methods explicitly describe −80°C aliquot storage for **fluorescently labeled EVs**; storage of the unlabeled preparation used for RNA-seq is not established by that sentence. No number or mapping of independent EV isolations to RNA-seq libraries is reported.

## Dose and Duration

The paper specifies **10 µg/mL for 72 h** for recipient RNA-seq; the µg dose is based on EV protein concentration by BCA, not particle number. GEO independently supports a three-day exposure but omits the numeric dose. EV source collection for 72 h is a separate interval from recipient exposure. The 24 h functional-assay exposures must not be treated as the RNA-seq time point.

## Control Definition

GEO calls the hDF controls `control`; the paper's results describe them as untreated controls. Neither source specifies the **exact RNA-seq recipient control medium**, an equal-volume PBS vehicle, or whether EV-depleted serum was used in recipient RNA-seq control wells. The paper documents EV-depleted serum for EV production and explicitly for the scratch-assay control, but that does not establish the RNA-seq control recipe. CTX003 therefore records **no EV exposure; medium/vehicle/recipient-serum status UNKNOWN**. This unresolved detail is material for C1.

## Donor Structure

The paper describes hDF isolation from healthy children's preputial specimens, but reports no donor count or donor-to-library assignments for these six RNA-seq samples. Pooling is not documented. The 12 GEO sample records have no donor attribute, and the checked BioSample control record likewise has no donor identifier. The number of independent recipient donors, potential pooling, and whether EV source and recipient share a donor remain **UNKNOWN**. The three libraries per arm must not be called independent-donor replication.

## EV Preparation Structure

The isolation method is described, but the number of independent EV preparations, any pooling, and preparation-to-recipient-library assignment are **UNKNOWN**. Distinct SRR/BioSample IDs are not preparation-level replication. The source passage range and EV characterization do not resolve this independence question.

## Sequencing Data

| Resource | Availability | Size/format | Scope and limitation |
| --- | --- | --- | --- |
| `GSE293956_hDF_total_count.txt.gz` | GEO listed, HTTP 200 | 491,697 compressed bytes; gzip text | Author-described raw gene counts for hDF samples; header and integer/sample structure reserved for C1 |
| `GSE293956_HaCaT_total_count.txt.gz` | GEO listed, HTTP 200 | 467,504 compressed bytes; gzip text | Separate HaCaT counts; excluded from CTX003 |
| 12 paired FASTQ run pairs | ENA/SRA listed | FASTQ.gz; 2.92–3.60 GB per pair in ENA metadata | Public raw reads; no FASTQ downloaded |
| Normalized counts / TPM / FPKM | Not listed among GEO series supplements | UNKNOWN | Do not assume present |
| DEG tables / other matrices | Not listed among GEO series supplements | UNKNOWN | Author figures/results are not SkinExo computed data |

The GEO sample records name the corresponding `hDF_total_count.txt` or `HaCaT_total_count.txt` and state raw counts per sample. They do not individually host supplementary files. The two matrices were **not downloaded or inspected** at D0; sample-resolved structure and adequacy remain to be checked at C1. GEO's standard `GSE293956_RAW.tar` path returned HTTP 404, which does not negate SRA/ENA raw read availability.

## Preferred Reconstruction Route

**A — official raw gene-count matrix** is preferred, specifically the hDF file, subject to C1 checks of header-to-GSM mapping, integer/nonnegative counts, stable gene identifiers, annotation, missingness, and file integrity. **B — official sample-level quantification** is not separately listed; the matrix may satisfy the same practical need. **C — reconstruction from public FASTQ** remains a fallback if A fails technical checks and would require a declared reference/annotation. **D — author normalized matrix only** is neither listed nor preferred. No large download or reconstruction began.

## Independence from CTX001 / CTX002

`INDEPENDENT` at the **study/dataset level** from both CTX001/GSE293186 and CTX002/GSE251807: distinct publications and author teams, accession/BioProject/sample/run sets, and EV-source designs. CTX003 uses hDF-derived EV, compared with endothelial EV in CTX001 and bone-marrow MSC small EV in CTX002. No documented data reuse was found. Independence of recipient donors or EV preparations **across studies** is unverified and is not implied by study independence.

## Phenotype Anchor Linkage

This is a design-link audit, not a phenotype result analysis. The [onboarding JSON](../outputs/exp003/exp003_d0_context_onboarding.json) records all classifications.

| Paper assay | Link to 72 h hDF RNA-seq context | Reason |
| --- | --- | --- |
| CCK-8 hDF viability/proliferation | `SAME_EV_DIFFERENT_TIME` | Same hDF recipient and hDF-EV source, graded doses including 10 µg/mL, **24 h** |
| hDF scratch migration | `SAME_EV_DIFFERENT_TIME` | Same recipient/source and 10 µg/mL, **24 h** |
| hDF ERK1/ERK2 qPCR | `SAME_EV_DIFFERENT_TIME` | Same recipient/source and 10 µg/mL, **24 h** targeted mRNA assay |
| Mouse wound closure | `SAME_EV_DIFFERENT_MODEL` | Mouse whole-wound model, days 0–8; different dose basis |
| Mouse scar length and collagen deposition | `SAME_EV_DIFFERENT_MODEL` | Mouse wound histology, day 14 |
| Cytokine array | `SAME_EV_DIFFERENT_MODEL` | Mouse wound tissue growth-factor array, day 1 |

These assays do not populate CTX003 transcriptomic axes. Mouse data are not human hDF phenotype evidence.

## GSE293957 Cargo Companion

[GEO GSE293957](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE293957) is the same Liu submitter group and hDF-EV source. Its official brief record lists **three** samples (`GSM8895198`–`GSM8895200`), Affymetrix miRNA-4 array `GPL19117`, and BioProject `PRJNA1247495`. It is `AVAILABLE_NOT_ANALYZED` cargo. The exact EV-preparation linkage to GSE293956 recipient libraries is **UNKNOWN**. The paper uses “miRNA sequencing” language while its methods and GEO identify an array; F1's array label is retained. No cargo data were analyzed or causally linked.

## Framework Compatibility

CTX003 meets the required F1 context criteria: EV perturbation, primary human dermal fibroblast recipient, a same-cell-type control arm, whole-transcriptome RNA-seq, public raw and processed data, reconstructable GSM→SRX→SRR/BioSample mapping, and independent study provenance. Its [context row](../data/metadata/skinexo_contexts.csv) now has 6 hDF samples (3+3), platform, source tissue, paper-supported dose, and explicit unknowns. `study_status=PLANNED`, `data_status=AVAILABLE_NOT_ANALYZED`, and `evidence_status=UNKNOWN` remain. Framework validation passes with all five CTX003 response placeholders unknown and no CTX003 biological comparison.

## Limitations

- Exact hDF RNA-seq control medium, PBS vehicle matching, and recipient EV-depleted-serum status are unknown.
- Recipient donor count, pooling, identities, and donor-to-library assignment are unknown.
- Independent EV preparation count, pooling, and preparation-to-library assignment are unknown.
- GEO confirms three days but omits the paper's numeric 10 µg/mL dose.
- Sample labels and distinct archive accessions do not prove biological independence or pairing.
- The official hDF count matrix is listed but uninspected; C1 must verify its actual structure and integrity.

## Eligibility Decision

**ELIGIBLE_WITH_LIMITATIONS; D0 PASS.** The hDF comparison is sufficiently mapped and publicly reconstructable to proceed to EXP003-C1 dataset integrity. D0 does not authorize an inferred donor-level claim, a fixed DE design, or any transcriptomic biological comparison.
