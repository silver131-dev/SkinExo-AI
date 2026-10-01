# SkinExo-AI EXP002-C1R

## Why C1 Required Review

[EXP002-C1](EXP002_C1_dataset_integrity.md) verified 16 GSE251807 libraries (8 MSC-sEV, 8 DMEM) and balanced allocation over two batches, but could not establish independent EV-preparation replication or the exact Salmon transcript reference. The batch-1 and batch-2 quantifications have different transcript ID sets. C1R investigates only those design and quantification issues; it does not examine differential expression, pathway results, or EXP001–EXP002 biological concordance.

Authoritative sources rechecked: [GEO GSE251807](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE251807) and its family SOFT/sample records, [BioProject PRJNA1055484](https://www.ncbi.nlm.nih.gov/bioproject/PRJNA1055484), [ENA run](https://www.ebi.ac.uk/ena/portal/api/filereport?accession=PRJNA1055484&result=read_run&fields=run_accession%2Cexperiment_accession%2Csample_accession%2Cread_count%2Cbase_count%2Cfastq_bytes%2Cfastq_md5&format=tsv) and [BioSample](https://www.ebi.ac.uk/ena/browser/view/SAMN39054792) metadata, the [Lei et al. primary article](https://doi.org/10.1038/s41598-025-04057-6) ([PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC12134064/)), and its [publisher supplementary PDF](https://static-content.springer.com/esm/art%3A10.1038%2Fs41598-025-04057-6/MediaObjects/41598_2025_4057_MOESM1_ESM.pdf). Small source copies and official [GENCODE v43](https://www.gencodegenes.org/human/release_43.html)/[v44](https://www.gencodegenes.org/human/release_44.html) transcript-ranking metadata are in Git-ignored `data/raw/exp002/`.

## Recipient Replication

**Status: PARTIALLY_VERIFIED.** The paper says that 32 NHDF RNA-seq samples were analyzed with *at least four biological replicates per treatment group* in two batches. Its RNA-seq methods say NHDFs were seeded in 6-well plates at 200,000 cells/well, treated for 48 h, harvested, and RNA extracted. GEO identifies eight DMEM and eight MSC-sEV samples, four of each in each batch. All 16 have distinct GSMs, BioSamples, SRA experiments, and SRR runs. The study documents one recipient NHDF commercial lot (PromoCell C-12302, lot 412Z029.2).

| Replication level | Evidence | C1R conclusion |
| --- | --- | --- |
| Donor | One named NHDF product lot in paper; no second donor reported | **One documented donor lot**, not 16 donors |
| Culture | RNA-seq protocol uses 6-well cultures; paper calls RNA-seq samples biological replicates | Distinct culture/well per library is **plausible and author-described**, but unique well/treatment-event IDs are not deposited |
| Treatment | 8 EV and 8 control culture samples | Separate recipient treatments are consistent with the protocol; per-well treatment and EV aliquot identifiers are unavailable |
| Sequencing | 16 distinct BioSamples/SRX/SRRs; one run per selected library | No repeated sequencing run identified; a unique accession alone does not prove unique source culture |

The two batches are author-described analysis batches with four treatment and four control libraries each. Neither GEO nor the supplement establishes that they were independent recipient-culture experiments or independent EV-preparation runs. Supplementary figure legends mentioning three biological replicates and triplicates refer to **functional assays**, not the RNA-seq library design; they must not be transferred to this comparison. Numbered `EV_1` and `DMEM_1` labels do not establish pairing.

## EV Preparation Replication

**Status: UNKNOWN for RNA-seq EV preparations.** The paper names one hBM-MSC source lot (PromoCell C-12974, lot 438Z012.1). Its Methods describe collecting conditioned medium and isolating the small-EV fraction by ultracentrifugation; GEO describes 100,000 × g pelleting and a PBS wash. The Methods quantify fraction **protein concentration by BCA**, and the RNA-seq exposure is **30 µg/mL of the MSC-sEV fraction for 48 h**. This is protein-mass normalization, not an EV particle-number dose. The EV pellets were suspended in PBS, but the RNA-seq control is described as DMEM with 1% penicillin/streptomycin; an equal PBS vehicle volume is not explicitly documented for the RNA-seq controls.

The number of independent sEV isolations used for RNA-seq, pooling, aliquot reuse, and assignment of preparations to recipient wells/batches are **unknown**. EV characterization or functional-assay replicate counts do not resolve these RNA-seq assignments. One source-cell lot is not equivalent to one EV preparation, and eight treated recipient wells are not eight independent EV preparations.

## Batch Structure

| Batch | DMEM controls | MSC-sEV | Transcript IDs per Salmon file |
| --- | ---: | ---: | ---: |
| 1 | 4 | 4 | 194,142 |
| 2 | 4 | 4 | 194,182 |

Condition is **not** fully confounded with batch. The source paper reports a batch effect in its own exploratory assessment; C1R does not reproduce or interpret that result. The batch-aligned transcript-reference difference is a technical reason to retain batch in a later statistical design, because the design matrix is balanced and condition remains estimable. It does not establish that batch captures every transcript-specific index effect.

## Salmon Reference Investigation

The GEO per-sample supplementary files have Salmon `quant.sf` fields `Name`, `Length`, `EffectiveLength`, `TPM`, `NumReads`. All IDs are **versioned Ensembl transcript IDs** (`ENST...version`), not RefSeq accessions or a mixture of identifier namespaces. Official GENCODE v44 metadata classifies the exact shared IDs across protein-coding, nonsense-mediated-decay, retained-intron, pseudogene, and other transcript types; the quantification is **not protein-coding only**. The full biotype counts are in the C1R JSON.

The paper/GEO state **GRCh38.p14**, but do not give the Salmon software version, index sequence checksum, transcriptome FASTA, Ensembl/GENCODE release, or Salmon `aux_info/meta_info.json` files. Such metadata would normally make tximeta reference identification possible; the GEO deposit contains only exported quantification tables, so original-index identity cannot be recovered from a hash. [GENCODE release history](https://www.gencodegenes.org/human/releases.html) places v43 on GRCh38.p13 and v44 on GRCh38.p14; v44 was available before the December 2023 GEO submission. This makes v44 a biologically and chronologically justified **candidate**, not proof that the authors indexed v44. The batch-specific ID sets show that one unchanged reference set was not used for every selected library.

## Transcript Universe Comparison

The complete row-level classification is [gse251807_transcript_universe_comparison.csv](../outputs/exp002/gse251807_transcript_universe_comparison.csv), generated by [01r_design_quantification_resolution.py](../experiments/exp002/01r_design_quantification_resolution.py).

| Measure | Count |
| --- | ---: |
| Batch-1 exact versioned IDs | 194,142 |
| Batch-2 exact versioned IDs | 194,182 |
| Exact intersection | 189,509 |
| Exact union | 198,815 |
| Exact intersection / union | 95.3193% |
| Exact intersection / batch 1 | 97.6136% |
| Exact intersection / batch 2 | 97.5935% |
| Shared unversioned IDs | 189,969 |
| Extra ID pairs matched only after version stripping | 460 pairs (920 CSV rows) |
| Duplicate unversioned IDs created within batch | 0 / 0 |
| Unversioned paired IDs with conflicting v43/v44 gene assignments | 1 (`ENST00000644571`) |

CSV classifications are `SHARED_EXACT` (189,509 rows), `SHARED_AFTER_VERSION_STRIP` (920 rows), `BATCH1_ONLY` (4,173 rows), and `BATCH2_ONLY` (4,213 rows). The 920 version-strip rows represent 460 two-version pairs, **not** 920 new shared biological features. No ID versions were stripped in the recommended strategy. Transcript lengths for all 189,509 exact shared IDs agreed between representative batch-1 and batch-2 files. Across all 16 libraries, exact-shared transcripts account for **97.167%–98.260%** of each Salmon `NumReads` sum; the excluded 1.740%–2.833% is batch-associated and must be documented in C2. The GEO processing metadata say paired reads were concatenated before Salmon quantification, so these estimated `NumReads` sums are not interchangeable with ENA run read/spot counts.

## tx2gene Mapping

Official [GENCODE v43 transcript rankings](https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_43/gencode.v43.transcript_rankings.txt.gz) and [v44 transcript rankings](https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/gencode.v44.transcript_rankings.txt.gz) were used as release-specific candidate `ENST.version → ENSG.version` maps. No transcript mapped to multiple genes within either inspected release. Coverage was assessed using **exact versioned IDs**, without selecting a release simply to maximize matches:

| Mapping | Assembly | Batch 1 exact mapped / unmapped | Batch 2 exact mapped / unmapped | Exact shared mapped / unmapped | Ambiguous |
| --- | --- | ---: | ---: | ---: | ---: |
| GENCODE v43 | GRCh38.p13 | 193,764 / 378 | 191,108 / 3,074 | 189,509 / 0 | 0 |
| GENCODE v44 | GRCh38.p14 | 192,832 / 1,310 | 194,182 / 0 | 189,509 / 0 | 0 |

**Resolution:** all 189,509 exact shared transcripts have an unambiguous GENCODE v44 gene assignment. This resolves a **restricted tx2gene route**, while the authors' original index release remains unverified. One version-differing pair changes gene assignment between v43 and v44 (`ENST00000644571.1` vs `.2`), which is a concrete reason not to silently remove version suffixes. No gene-level matrix was generated in C1R.

## Harmonization Strategies

| Strategy | Statistical validity and information loss | Annotation uncertainty | DESeq2 suitability | External-validation suitability |
| --- | --- | --- | --- | --- |
| **A — exact shared transcript set + GENCODE v44 gene map** | Reproducible 189,509-ID intersection; drops 1.740%–2.833% of each sample's Salmon `NumReads` sum. Different original Salmon indexes can still influence estimates of retained transcripts. | Exact IDs/lengths and all shared-ID gene mappings verified in v44; original index not proven. | **Conditional:** tximport-style import of estimated counts with appropriate length handling and batch term could support a restricted later count-based analysis; document reference sensitivity. These are **estimated gene-level counts**, not raw integer gene counts. | **Best limited route** for the predeclared EV-vs-DMEM comparison; preserve batch and one-donor limitations. |
| **B — version-normalized shared set + authoritative map** | Adds only 460 transcript pairs; no within-batch duplicate base IDs, but one cross-release gene-assignment conflict and changed transcript versions. | Version stripping loses distinctions; v43 is p13 while v44 is p14. | **Not recommended** without a pair-by-pair reconciliation and sensitivity analysis. | Small gain does not justify added ambiguity for primary route. |
| **C — author normalized gene matrix** | Uses already-normalized 32-sample gene values; no original count variance model. | Author's gene mapping/normalization provenance is limited. | **No** — never treat as original or tximport gene counts. | Descriptive, non-count-based comparison only; weaker technical traceability. |

`tximport` is the established route for importing Salmon estimates to gene-level matrices with [documented length handling](https://bioconductor.org/packages/release/bioc/vignettes/tximport/inst/doc/tximport.html). This checkpoint selects **Strategy A for C2 planning**; it does not generate a count matrix, choose a DE threshold, fit DESeq2, or assert that index mismatch has no impact. A future pipeline should distinguish Salmon `NumReads` estimates, tximport-derived **estimated gene-level counts**, and original integer gene counts. The original index hashes and reference FASTA would be needed to close the provenance gap fully.

## EV_8 Review

**Classification: NO_OBVIOUS_ISSUE at metadata/depth level.** `EV_8` is linked to one BioSample (`SAMN39054792`), SRA experiment (`SRX22996563`), and run (`SRR27319309`); no duplicate run was found. ENA reports `read_count = 54,035,352`, 1.837 times the median of the 16 selected runs. Its Salmon `NumReads` sum is **95,330,727**, 1.812 times the selected median. These are distinct measures, but their similar **relative** ratios support deeper sequencing as the immediate explanation for the high Salmon sum; no technical problem is confirmed and the sample is retained. FASTQ quality, composition, and sample-level QC were not assessed in C1R.

## Statistical Unit

The **working unit** is one author-described biological replicate: a recipient NHDF culture/well with its own library, nested in the single documented recipient donor lot. This is provisional because well-to-library treatment-event IDs are not provided. It estimates a response in this donor/EV-source context if the culture assignments are independent. It cannot estimate variation among human donors or independent EV preparations. The 16 libraries are not 16 independent donor-level replicates.

## Statistical Design

**Recommended provisional count-based design:** `~ batch + condition`. The 4/4 allocation in each batch makes condition estimable while allowing a batch term; reference/index change and the paper's batch note support retaining it. `~ condition` would leave the documented batch distinction unmodeled. No paired-design, donor, or EV-preparation term can be justified from current sample metadata. Before any later DE, C2 should verify strategy-A import, batch-aware quality metrics, and sample independence assumptions without selecting a design for stronger significance.

## Generalization Boundaries

- **Recipient donor level:** NO. One commercial NHDF donor lot is documented.
- **EV preparation level:** NO. Isolation count and per-well assignment are unknown.
- **EV source-cell donor level:** NO. One source-cell lot is documented.
- **Culture level:** LIMITED, conditional on the author-described biological replicates corresponding to independent recipient cultures.
- **EXP001 comparison:** a different EV source (MSC vs endothelial) and exposure time (48 vs 72 h) prevent same-perturbation replication claims.
- **Vehicle:** PBS carried with sEV pellets may differ from the stated RNA-seq DMEM-only control; volume matching is unverified.

## Backup Dataset Readiness

[GSE212873](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE212873) remains a plausible Tier-A backup with human dermal recipient fibroblasts, two donor lines, EV/PBS comparators, and 24 h exposure. It may offer stronger recipient-donor coverage, but its deposited processed GEO files are bigWig tracks rather than a ready small gene-count matrix; a count-based analysis would require raw-read reconstruction and further design checks. No GSE212873 data were downloaded or analyzed here. It is **not immediately easier to reconstruct** than the restricted GSE251807 route.

## GO / LIMITED-GO / NO-GO Decision

**LIMITED_GO — C1R RESULT: PASS.** The GSM/BioSample/SRX/SRR mapping is reliable; four EV and four controls occur in each batch; recipient culture is a defensible *provisional* statistical unit; and every exact shared transcript maps unambiguously to an authoritative GRCh38.p14 GENCODE v44 gene ID. Strategy A defines a reproducible **restricted technical route** for EXP002-C2 QC and statistical-analysis planning. It is not a verified reconstruction of the authors' original transcriptome index and it does not remove donor or EV-preparation limitations.

The limited decision explicitly prevents claims of donor-level or EV-preparation-level replication. Remaining work before a later count-based DE analysis is to implement and audit the exact-shared import, quantify batch/index sensitivity, evaluate the high-depth sample in sample-level QC, and seek original index and EV-preparation provenance where possible. If these checks fail, change the downstream decision to NO_GO. C1R performed **no DE, PCA interpretation, GSEA, EXP001 concordance, or modeling**.
