# EXP002-D0 public dataset search log

Search date: **2026-09-30**. Eligibility was locked first in [EXP002_D0_ELIGIBILITY.md](../checkpoints/EXP002_D0_ELIGIBILITY.md). This is metadata discovery only; no candidate omics file was downloaded or analyzed. Search-engine indexing is imperfect, so absence from this log is not proof of absence from all repositories.

## Search progression and queries

1. **Same cell and tissue first.** Searched NCBI GEO, its linked SRA/BioProject records, PubMed, Europe PMC, and publisher pages using `"extracellular vesicle" fibroblast RNA-seq`, `exosome fibroblast RNA-seq`, `extracellular vesicle dermal fibroblast transcriptome`, `exosome dermal fibroblast transcriptome`, `EV skin fibroblast RNA sequencing`, `MSC exosome fibroblast RNA-seq`, `endothelial EV fibroblast transcriptome`, and `fibroblast extracellular vesicle treatment RNA-seq`. Additional GEO-specific searches included `"dermal fibroblasts" "extracellular vesicles" "RNA-seq"`, `"human dermal fibroblasts" "exosomes" "GSE"`, and `"fibroblasts treated with exosomes" RNA-seq SRA BioProject`.
2. **Broadened only after identifying and evaluating the same-cell candidates.** Searched human non-skin fibroblasts, human skin-cell EV responses, other human EV transcriptomics, nonhuman fibroblast EV responses, and different recipient cells. The Tier A candidates did not reproduce the EXP001 endothelial source **and** 72-h exposure with an immediately verified comparison; the HUVEC-source Dryad study has unresolved column mapping. This justified broadening to document alternatives.
3. **Other repositories.** Searched BioStudies/ArrayExpress (EMBL-EBI), Mendeley Data, Zenodo, Figshare, and Dryad with the same fibroblast/EV/transcriptomic combinations and inspected linked primary-paper data statements. No additional clearly superior sample-resolved Tier A comparison was verified in those searches. Dryad exposed an important HUVEC EV study; Mendeley confirmed the prior rat-macrophage record. Search results from these repositories were screened against the locked criteria, not treated as automatically eligible.

## Authoritative records inspected

| Canonical study | Accessions and provenance | Screening outcome |
|---|---|---|
| S001 | [GSE251807](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE251807), [sample GSM7988510](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM7988510), [primary paper](https://doi.org/10.1038/s41598-025-04057-6); SRA BioProject PRJNA1055484 | Tier A. Eight MSC-sEV and eight media controls across two batches; public sample-level Salmon quantification and SRA. |
| S002 | [GSE212873](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE212873), [primary paper](https://doi.org/10.1038/s41598-022-26217-8); PRJNA877679 | Tier A. Two primary dermal donor lines; core EV/PBS contrast at 24 h. GEO processed tracks are bigWig rather than a small count matrix. |
| S003 | [GSE279511](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE279511), [fibroblast GSM8574446](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM8574446), [linked publisher paper](https://www.sciencedirect.com/science/article/abs/pii/S0022202X24029592); PRJNA1173165 | **Excluded from EV-only replication.** The GSM protocol explicitly says recipient cells were incubated for 72 h with collected concentrated melanoma **conditioned medium**, despite an “EV treatment” characteristic. Three samples/arm and raw counts are available, but an EV-specific effect is not isolatable from this contrast. |
| S004 | [Dryad DOI 10.5061/dryad.b2rbnzsmj](https://datadryad.org/dataset/doi:10.5061/dryad.b2rbnzsmj), [primary paper](https://doi.org/10.1126/sciadv.adh1168), SRA PRJNA910343; Zenodo 10.5281/zenodo.7941469 is associated code, **not a second study** | **UNCERTAIN**. Primary human dermal fibroblast, HUVEC EV arm, controls, raw-count table. Dryad README download returned HTTP 403 during discovery; HUVEC sample-to-count-column map remains unverified. No large table downloaded. |
| S005 | [GSE116176](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE116176); PRJNA477548 | Tier B. Immortalized stomach fibroblast array, two samples per arm. |
| S006 | [GSE158623](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE158623), [GSE158624 SuperSeries](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE158624), [primary paper](https://doi.org/10.1002/jev2.12124); PRJNA665998 | Tier B. Primary lung fibroblast RNA-seq; one library per condition and time. SuperSeries is not a second dataset. |
| S007 | [GSE271672](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE271672) | Tier C only. Rabbit scar tissue, miRNA readout, three controls and three EV-treated samples. |
| S008 | [Mendeley DOI 10.17632/gm29wd7b94.1](https://data.mendeley.com/datasets/gm29wd7b94/1) | **UNCERTAIN** data reuse; rat bone-marrow macrophages with LPS and MSC-sEV, n=3/group. Recipient is not fibroblast, so at most Tier C even if sample files resolve. |
| S009 | [GSE141814](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE141814) | Excluded as EV replication. Two pooled mouse wound scRNA libraries with fibrotic/regenerative fates, no EV perturbation. The C3.5 reanalysis reuses these samples. |
| S010 | [scGeneScope official dataset](https://huggingface.co/datasets/altoslabs/scGeneScope), [official code](https://github.com/altoslabs/scGeneScope) | Excluded as biological EV replication. U2-OS chemical perturbations; possible methods reference only. |
| S011 | [GSE184084](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE184084) | Excluded. Profiles RNA **inside fibroblast-secreted EVs**, not recipient fibroblast response. |
| S012 | [PubMed PMID 34203413](https://pubmed.ncbi.nlm.nih.gov/34203413/) | Excluded. RNA-seq in this paper used trophoblast **conditioned medium** on scratch-wounded fibroblasts; an isolated-exosome transcriptomic contrast was not verified. |
| S013 | [GSE293186](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE293186), PRJNA1243317 | Excluded: EXP001 itself. GEO and BioProject identify the same six samples. |
| S014 | [publisher paper](https://doi.org/10.3389/fcell.2020.613583) linking GSE157022 | **UNCERTAIN** sample mapping. Mouse 3T3-L1 recipient, at most Tier C; GEO sample-level fields were not established in this pass. |

## Duplicates, exclusions, unresolved metadata

- GSE158624 contains GSE158623 and EV-miRNA GSE156572; count the recipient-cell RNA-seq once under S006.
- Dryad, SRA PRJNA910343, the Hagey paper, and its Zenodo code all describe S004, not four biological studies.
- GSE293186 and PRJNA1243317 are the frozen EXP001 study. Its author DEG table is not an external dataset.
- GSE141814 and the later fibrotic/regenerative single-cell reanalysis use the same pooled libraries.
- GSE279511's paper also links GSE279329; no independent fibroblast validation is inferred from that second accession.
- **Unresolved before EXP002-C1:** S001 donor-level independence, exact Salmon transcript-to-gene reconstruction and gene identifiers; S002 raw-count reconstruction and donor/sample metadata check; S004 Dryad column-to-treatment map and exact HUVEC contrast; S008 file listing; S014 GEO sample map. S003's stated protocol is sufficient to exclude an EV-only contrast. No unknown value was filled from analogy.
