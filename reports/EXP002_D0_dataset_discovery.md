# SkinExo-AI EXP002-D0

## Objective

Select a **genuinely independent public EV-response transcriptomic study** for future external assessment of EXP001. This checkpoint reviewed metadata only. The reference is [GSE293186](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE293186): primary human dermal fibroblasts, endothelial-cell EV versus media control, 72 h, bulk RNA-seq, three biological samples per arm. No candidate data, DEG result, pathway result, or model was generated here.

## Locked Eligibility Criteria

The [eligibility document](../docs/checkpoints/EXP002_D0_ELIGIBILITY.md) was written **before the public dataset search**. A primary dataset requires independent samples, EV/exosome exposure of fibroblast recipients, a transcriptomic readout, EV and comparator groups, public data, and sample-level information sufficient to reconstruct the contrast. Tier A is human dermal/skin fibroblast; Tier B is other human fibroblast; Tier C is another species or recipient cell and **cannot be primary replication**. Missing required metadata produce `UNCERTAIN`, rather than an assumed pass. Replicates, accessible counts, source, dose, time, and phenotype are preferences, not hidden eligibility changes.

## Search Strategy

Search date: **2026-09-30**. We began with human dermal/skin fibroblast + EV/exosome + RNA-seq/transcriptomics + control, then widened to other human fibroblasts and finally cross-context EV transcriptomics. GEO/SRA/BioProject records and linked primary papers supplied most study-level detail. Europe PMC/PubMed and publisher pages resolved paper methods; BioStudies/ArrayExpress, Mendeley Data, Zenodo, Figshare, and Dryad were also queried for public deposits. Queries, URLs, screening outcomes, and duplication checks are in the [search log](../docs/literature/EXP002_D0_SEARCH_LOG.md). This is a targeted reproducible search, not a claim that no other dataset exists.

## GSE212873 Verification

[GEO GSE212873](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE212873) and the [primary Scientific Reports paper](https://doi.org/10.1038/s41598-022-26217-8) describe EVs produced by **primary human dermal fibroblasts**, then applied to recipient dermal fibroblasts. Unstimulated donor cells yield control EVs; FGF2-exposed donor cells yield FGF2-bearing EVs. Core RNA-seq treatments are PBS, control EV, FGF2 EV, and soluble FGF2 for **24 h** in **two dermal fibroblast donor lines**. The paper states **2 × 10¹⁰ particles** for the EV RNA-seq arms and 100 ng/mL soluble FGF2; other antibody/IgG pretreatment samples bring the GEO series to **16** samples. GEO links SRA/BioProject **PRJNA877679**; raw reads are available, while its series supplement consists of bigWig tracks rather than an immediately reusable small gene-count matrix. The paper reports in vitro proliferation/migration assays and a separate mouse wound experiment; those results cannot be transferred to EXP001. The GEO title includes a wound-healing suffix absent from the shorter published article title.

**Status: `ELIGIBLE_A`, secondary candidate.** It is independent of GSE293186 by study, authorship, accession, and experimental sample provenance. The **control-EV versus PBS** contrast addresses EV exposure; **FGF2-EV versus control-EV** addresses an EV-source/cargo modification and must not be described as the same contrast. Two donor lines and lack of a small count matrix limit immediate gene-level validation.

## Tier A Candidates

| Study | Verified comparison and public material | Key limitation |
|---|---|---|
| **[GSE251807](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE251807)** — selected primary | Primary normal human dermal fibroblasts, human bone-marrow MSC small EV (**30 µg/mL, 48 h**) versus DMEM vehicle; **8 sEV and 8 control libraries**, balanced across two batches. GEO provides SRA reads, per-sample Salmon `quant.sf`, and a normalized-count table. [Primary paper](https://doi.org/10.1038/s41598-025-04057-6) reports migration/proliferation assays. | EV producer is MSC rather than endothelial; 48 versus 72 h; a directly verified **integer gene-count matrix** is not available in the GEO listing. Salmon `NumReads` need transcript-to-gene aggregation and must be inspected before count-based analysis. The number of independent recipient donors is unverified. |
| **[GSE212873](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE212873)** | Primary dermal fibroblast EV exposure, two donor lines, core PBS/control-EV/FGF2-EV/soluble-FGF2 arms at 24 h; SRA available. | Only two donor lines for core comparison; processed GEO files are bigWig; EV producer and cargo context differ. |

An additional [Hagey et al. study](https://doi.org/10.1126/sciadv.adh1168) is **not counted as eligible yet**. Its [Dryad deposit](https://datadryad.org/dataset/doi:10.5061/dryad.b2rbnzsmj) lists a human raw-count table, and the paper describes primary human dermal fibroblasts (GM08402), **HUVEC EVs among 12 EV sources**, 24-h treatment, five untreated and five buffer controls, and triplicate source-dose arms (20, 2,000, 200,000 particles/cell). The HUVEC-to-count-column map could not be independently inspected from the accessible metadata: Dryad's small README download returned HTTP 403. Its 26.6 MB count file was deliberately not downloaded. It is **`UNCERTAIN`** under the frozen rule requiring reconstructable sample-level comparison, despite strong potential source comparability.

## Tier B Candidates

| Study | Why Tier B | Validation constraint |
|---|---|---|
| [GSE116176](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE116176) | Human stomach fibroblasts treated with gastric-cancer EVs for five days; PBS and no-treatment controls; eight Agilent microarrays total. | Recipient cells were **immortalized** after derivation, cancer context, only two samples per group, and array rather than RNA-seq. |
| [GSE158623](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE158623) | Primary human lung fibroblasts treated with bronchial-epithelial EVs (10 µg/mL) or PBS at 24 or 48 h; bulk RNA-seq. | One RNA-seq library per group/time. Useful for metadata context but insufficient for robust independent gene-level statistics. [GSE158624](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE158624) is its SuperSeries, not a replicate study. |

## Tier C Candidates

[GSE271672](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE271672) has three rabbit control and three adipose-MSC-exosome-treated **scar-tissue small-RNA** samples. It is a public EV intervention with a comparator, but the mixed tissue, species, and miRNA readout rule out direct fibroblast mRNA replication. Tier C is cross-context only.

The prior [Mendeley 10.17632/gm29wd7b94.1](https://data.mendeley.com/datasets/gm29wd7b94/1) record really is **rat bone-marrow MSC-sEV → LPS-primed rat bone-marrow macrophage RNA-seq**, 30 µg/mL for 48 h, **n=3/group** across untreated, LPS, and LPS+sEV groups. Public deposit metadata did not expose a sample-to-file map in this review, so the record is `UNCERTAIN` for reuse; biologically it would be Tier C, never primary EXP002 fibroblast replication. The [GSE157022-linked primary paper](https://doi.org/10.3389/fcell.2020.613583) describes EV-treated mouse 3T3-L1 cells, but sample-level GEO metadata were not resolved here; this too remains `UNCERTAIN` and at most Tier C.

## Excluded Candidates

- [GSE141814](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE141814): mouse regenerative versus fibrotic wound scRNA-seq, **no EV treatment**. It may remain wound-fate reference context; its later literature reanalysis is not a second dataset.
- [scGeneScope](https://huggingface.co/datasets/altoslabs/scGeneScope): U2-OS chemical perturbation and imaging/scRNA-seq, no EV or fibroblast recipient. It is a methodological resource only.
- [GSE279511](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE279511): three untreated and three treated primary dermal-fibroblast RNA-seq libraries with raw counts, but the [GSM protocol](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM8574446) says **concentrated A375 melanoma conditioned medium** was incubated with recipients for **72 h**. The sample characteristic calls it “EV treatment”; that label does not establish an isolated-EV-only effect. Excluded under the locked perturbation criterion.
- [GSE184084](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE184084): small-RNA profiles **inside EVs secreted by** senescent versus nonsenescent dermal fibroblasts; no EV-treated fibroblast transcriptome.
- [Trophoblast secretome study](https://pubmed.ncbi.nlm.nih.gov/34203413/): isolated exosomes were assayed functionally, but the reported RNA-seq contrast used **trophoblast conditioned medium** on scratch-wounded dermal fibroblasts. An isolated-exosome transcriptomic comparison was not verified.
- [GSE293186](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE293186): the EXP001 source itself, so it cannot validate EXP001 independently.

## Dataset Duplication Check

Canonical `study_id` in the [candidate table](../data/metadata/exp002_dataset_candidates.csv) prevents accession aliases from being counted as new experiments: GSE158624/GSE158623, SRA+Dryad+Zenodo for the Hagey study, and GEO+BioProject for GSE293186. The C3.5 paper analyzing GSE141814 reuses the original pooled samples. GSE279511 and its linked GSE279329 were not counted as two fibroblast EV studies. None of the recommended datasets is a reprocessing of GSE293186 based on the source records, paper linkage, and different sample accessions; exact donor overlap across unrelated studies is not independently knowable.

## Comparability to GSE293186

`MATCH`, `PARTIAL_MATCH`, `MISMATCH`, and `UNKNOWN` values for **species, recipient cell, tissue, EV source/type, dose, time, platform, and design** appear for each eligible/uncertain study in the candidate CSV. The decisive comparisons are:

| Candidate | Species / recipient / tissue | EV source | Time | Design / data |
|---|---|---|---|---|
| GSE251807 | MATCH / MATCH / MATCH | MISMATCH: MSC vs endothelial | PARTIAL_MATCH: 48 vs 72 h | Two balanced batches, 8/arm, quant files; gene-level counts require reconstruction. |
| GSE212873 | MATCH / MATCH / MATCH | MISMATCH: dermal fibroblast vs endothelial | MISMATCH: 24 vs 72 h | Two donor lines; SRA reconstruction needed. |
| GSE279511 (excluded) | MATCH / MATCH / MATCH | MISMATCH: melanoma vs endothelial | MATCH: 72 h | 3/arm and raw counts; actual treatment is concentrated conditioned medium, so an EV-only effect is unidentifiable. |
| Hagey/Dryad | MATCH / MATCH / MATCH | MATCH: HUVEC arm | MISMATCH: 24 vs 72 h | Triplicate culture arms and raw-count table, but sample column map unverified. |

“Source match” for HUVEC refers to endothelial origin, **not** proven equivalence of EV isolation, cargo, dose, donor, or biological context. No comparison uses an arbitrary numerical score.

## Validation Value

The CSV records `STRONG`, `MODERATE`, `WEAK`, or `NOT_APPROPRIATE` for gene-level direction, pathway programs, P/M/E/A/I programs, regenerative/fibrotic context, and general EV response, with rationale. **GSE251807** is strongest for comparing *directional programs* in the same human dermal recipient under a different EV source; gene-level concordance is only **moderate potential** until counts, mapping, donor structure, and batch are checked. **GSE212873** may test whether some dermal fibroblast EV-response programs recur under autologous/FGF2-bearing EVs, but its two donor lines weaken gene-level claims. **Hagey/Dryad** could test source-matched endothelial EV response once its HUVEC samples are mapped. GSE279511 has no EV-only validation value under its stated conditioned-medium protocol. None of these experiments can validate wound closure, therapeutic efficacy, scarless regeneration, or an EXP001 72-h endothelial-specific causal mechanism from transcriptomics alone.

## Recommended Primary EXP002 Dataset

**GSE251807 — Tier A.** It meets all eight locked primary criteria in the public GEO record: independent study; EV perturbation applied to fibroblasts; bulk transcriptomics; an explicit media control; public SRA and processed sample-level quantification; and reconstructable treatment, batch, and comparator metadata. The **8-versus-8 balanced two-batch** design gives a clearer prospective analytical comparison than the two-donor GSE212873 core contrast. Select it for **EXP002-C1 integrity**, subject to checking exact sample files, gene identifiers, donor/batch relationships, and Salmon transcript-to-gene aggregation. The EV source and exposure time differ from EXP001, so any concordance would support cross-source dermal fibroblast response generalization rather than same-perturbation replication. The published migration result is context only, not an EXP002 validation outcome.

## Recommended Secondary Cross-Context Dataset

**GSE212873 — Tier A, secondary dermal EV context.** Its autologous/control and FGF2-EV arms probe a distinct source/cargo context in two human dermal donor lines, while remaining weak for standalone gene-level reproducibility. **Hagey/Dryad** is a high-priority *unresolved* source-matched follow-up, not currently promoted to a selected validation dataset. If its HUVEC/control column map can be verified, it may become the more source-comparable secondary study.

## Risks

- The selected study uses **MSC**, not endothelial, EVs and samples at **48**, not 72, h. A different direction for a gene would not automatically contradict EXP001.
- The selected eight libraries per arm may be culture replicates from a **single commercial recipient donor lot**; donor-level generalization is unverified.
- GEO lists per-sample Salmon quantification and normalized counts, not an independently verified integer gene-count matrix. Count reconstruction and gene-ID provenance are an EXP002-C1 task, not a D0 result.
- GSE279511 must stay excluded from EV-specific validation because its treatment was concentrated conditioned medium; Hagey has an inaccessible README and unverified count-column mapping; GSE212873 requires raw read processing for counts.
- Discovery coverage is finite. A future newly released or better annotated same-cell/source study could supersede this recommendation without changing the locked criteria.

## D0 Decision

**PASS — a scientifically usable independent Tier A primary dataset was identified for an integrity checkpoint.** This is a dataset-selection result, **not completion of independent validation**. No candidate omics matrix was downloaded or analyzed; next work is EXP002-C1 on the selected dataset only after accepting the documented contrasts and limits.
