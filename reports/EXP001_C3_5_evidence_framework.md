# SkinExo-AI EXP001-C3.5

## Objective

Freeze a source-verified evidence framework for future C4 questions about proliferation (P), migration (M), ECM remodeling (E), angiogenesis (A), inflammation (I), and regenerative versus fibrotic context. This checkpoint maps literature and data provenance; it does **not** perform enrichment or score C3 genes.

## C1-C3 Evidence Summary

C1, C2 and C3 passed. The unchanged C3 comparison is **ECEV 72 h versus CTRL 72 h**, with positive log2 fold change meaning higher expression after ECEV exposure. Of 16,271 genes tested, 6,612 had adjusted p < 0.05 and 2,032 met adjusted p < 0.05 plus absolute log2 fold change ≥ 1 (995 up, 1,037 down). Strongest by adjusted p among threshold-B up genes: HGF, ETV1, TOP2A, NBL1, HMGA2, PHLDA1, AL109918.1, SLC14A1, CENPF, ANPEP. Strongest down genes: PSAT1, CCDC80, TAGLN, OXTR, GFRA1, IGFBP5, GRIA1, ADM2, SLC7A11, SEMA3D. The author DEG archive shares 1,952 tested genes with ours; log2FC Pearson r = 0.999999791 and direction concordance = 100%. Because that archive is thresholded and derived from the same dataset, this is computational consistency, **not biological validation**. Exact values are preserved in `outputs/exp001/c3_evidence_summary.json`; C3 files were read only.

## Literature Verification

The 15 supplied candidates and mandatory GSE293186 primary study were checked against publisher/proceedings, PubMed, PMC/Europe PMC, GEO, and official dataset hosts. **16/16 records were identifiable after correction; five candidate records needed correction.** Nine are primary research or primary computational/dataset papers; seven are reviews (including one systematic review). Bibliographic fields, source URLs, article type, model, dataset availability, and `NA` for unverified fields are in `data/metadata/skinexo_evidence_matrix.csv`. The source-by-source audit is [mechanistic evidence](../docs/literature/skinexo_mechanistic_evidence.md).

The primary paper is [Yuan et al., *Journal of Investigative Dermatology*, 2026, DOI 10.1016/j.jid.2025.10.584](https://pubmed.ncbi.nlm.nih.gov/41161638/) (P00). Its [GEO series GSE293186](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE293186) is exactly the EXP001 source. Its additional assays and mouse experiments offer within-study context, not an independent replicate of our RNA-seq result.

## Corrected Literature Records

| ID | Correction | Authoritative check |
|---|---|---|
| L04 | Journal year is **2026**, not supplied 2025. | [PubMed](https://pubmed.ncbi.nlm.nih.gov/42137193/) |
| L05 | Full title ends **“by promoting M2 macrophage polarization through p38 MAPK inhibition.”** | [PubMed](https://pubmed.ncbi.nlm.nih.gov/41209696/) |
| L10 | Full title ends **“Wound Healing Fates.”** | [PubMed](https://pubmed.ncbi.nlm.nih.gov/35664010/) |
| L11 | Supplied PMCID **PMC11647520** belongs to Kang et al.'s *Epidermal stem cell-derived exosomes improve wound healing by promoting the proliferation and migration of human skin fibroblasts*. The supplied scarless-versus-fibrotic title was not verified against that PMCID. The actual PMCID article is retained as corrected L11. | [PubMed](https://pubmed.ncbi.nlm.nih.gov/39687464/) |
| L15 | Official listing is **ICML 2026 FM4LS workshop**, not ICLR-related. A DOI was not verified. | [Workshop accepted papers](https://icml2026fm4ls.github.io/pages/accepted-paper.html) |

For L12, the verified main-article DOI is **10.1038/s41592-024-02528-8**, distinct from its author-correction DOI. [PubMed PMID 39639168](https://pubmed.ncbi.nlm.nih.gov/39639168/) lists the article in *Nature Methods* 2025. This filled a missing candidate DOI, so it was not counted among corrections.

## SkinExo Evidence Taxonomy

`DIRECT` = the paper experimentally measures or directly analyzes the phenotype/program in its model. `INDIRECT` = supporting context without direct measurement of the target in the relevant model. `NOT_ASSESSED` = insufficient evidence. `CONFLICTING` = relevant findings lack one consistent interpretation. A direct code does not mean the phenotype has the same direction as EXP001, nor that another model transfers to fibroblasts. Reviews are marked `REVIEW_SYNTHESIS`; primary articles are marked `PRIMARY_EXPERIMENT`, with L10 explicitly a secondary reanalysis and L13–L15 computational studies. The required circularity classes are `SAME_DATASET`, `RELATED_EXTERNAL_EVIDENCE`, `INDEPENDENT_EXTERNAL_EVIDENCE`, `REVIEW_SYNTHESIS`, and `HYPOTHESIS`.

## P/M/E/A/I Evidence Matrix

The following is a compact view of direct/indirect **study-level** evidence. The CSV carries all 16 rows and explicit codes. Review topic mentions do not become `DIRECT` or `INDIRECT` axis evidence.

| Study | P | M | E | A | I | Model caveat |
|---|---|---|---|---|---|---|
| P00 | DIRECT | DIRECT | DIRECT | NOT_ASSESSED | NOT_ASSESSED | Same primary study as EXP001; fibroblast assays and mouse wound. |
| L05 | NOT_ASSESSED | NOT_ASSESSED | NOT_ASSESSED | NOT_ASSESSED | DIRECT | Rat macrophages and diabetic rat wound; EV plus GelMA in vivo. |
| L06 | DIRECT | NOT_ASSESSED | DIRECT | NOT_ASSESSED | NOT_ASSESSED | Human primary cells and reconstructed skin; collagen IV/fibrillin-1, not scarless repair. |
| L08 | NOT_ASSESSED | NOT_ASSESSED | NOT_ASSESSED | NOT_ASSESSED | DIRECT | TNF-α/dexamethasone skin chip; **no EV intervention**. |
| L10 | INDIRECT | INDIRECT | INDIRECT | INDIRECT | INDIRECT | Direct regenerative/fibrotic *state* comparison in mouse; no EV; two pooled libraries. |
| L11 | DIRECT | DIRECT | DIRECT | NOT_ASSESSED | NOT_ASSESSED | External epidermal-stem-cell exosomes; human fibroblast assays and mouse wound. |
| L13–L15 | NOT_ASSESSED | NOT_ASSESSED | NOT_ASSESSED | NOT_ASSESSED | NOT_ASSESSED | Imaging/transcriptomic methods in non-skin cell systems. |

Direct study-level counts: P=3, M=2, E=3, A=0, I=2. Of the two direct I studies, one (L08) is a non-EV assay model. No screened primary study directly measured EV-induced angiogenesis in the EXP001 recipient-cell setting; endothelial origin alone is insufficient.

## Regenerative vs Fibrotic Framework

L10 directly analyzes different mouse wound fates and fibroblast/macrophage states using [GSE141814](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE141814), but it did not test EV exposure. P00 observed more collagen density and fibroblast quantity in mouse **scar tissue**; we code fibrotic context as indirect, not a regenerative benefit. L05's improved diabetic wound closure and L11's fibroblast growth/migration are repair phenotypes, yet neither establishes scarless regeneration. L06 measured skin thickness and ECM markers in reconstructed skin, which is a biomarker context, not a wound-fate experiment. Increased collagen cannot be assumed regenerative; reduced inflammatory markers cannot be assumed to improve healing without timing, tissue, and outcome context. No numerical regenerative/fibrotic score was calculated.

## Public Dataset Landscape

Four uniquely identified public data resources were cataloged in `data/metadata/skinexo_dataset_catalog.csv`:

| Resource | Reuse opportunity | Key constraint |
|---|---|---|
| [GSE293186](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE293186) | EXP001; possible mechanistic hypothesis source for EXP006 | `SAME_DATASET`, not external validation. |
| [Mendeley 10.17632/gm29wd7b94.1](https://data.mendeley.com/datasets/gm29wd7b94/1) | EXP002/EXP004/EXP006: rat EV–macrophage response | Three conditions, n=3 each (nine samples); not a human fibroblast replication. Raw/processed file types remain unverified. |
| [GSE141814](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE141814) | EXP004: regenerative/fibrotic wound-state context | Mouse, **two pooled scRNA-seq libraries** each assembled from 6–8 wounds; not two replicated groups. L10 reanalyzes these data. |
| [altoslabs/scGeneScope](https://huggingface.co/datasets/altoslabs/scGeneScope) | EXP003/EXP005: multimodal method benchmark | U2-OS chemical perturbations, not skin/EV. Treatment-matched modalities are not cell-paired; official code describes very large raw downloads and a noncommercial license. |

L06 has article/supplementary data but no public omics repository accession verified. L08 and L11 state data are available upon reasonable request. L13 reuses public Cell Painting/RxRx/L1000 datasets but no unique accession was verified here; L15 reuses scGeneScope and is not a fifth independent dataset. Public metadata discovery only; no large dataset downloaded.

## C3 Gene-to-Literature Bridge

`outputs/exp001/c3_literature_bridge.csv` contains the **19 requested symbols**, their unchanged C3 log2FC/padj, axis codes, regenerative/fibrotic context, evidence class, source IDs, and negative/uncertain notes. The symbol lookup was required to resolve to exactly one C3 `gene_id` per entry; C3 results were not recomputed. One gene has direct same-study mechanistic evidence: **ETV1** in P00, which is **not independent C3 validation**. **TAGLN** has indirect context as a pericyte marker in L10's mouse wound reanalysis; this does not establish the meaning of decreased TAGLN in ECEV-treated human fibroblasts. The remaining 17 have insufficient gene-specific evidence in this screened set. Zero were confidently labeled conflicting; this means conflict was not demonstrated by the limited screen, not that contradictory literature does not exist. No C3 direction was used to choose a supporting citation.

## Circularity Risks

1. P00, its DEG table, and GSE293186 are the same study/data family; numerical concordance or mechanistic agreement cannot be called independent validation.
2. Reviews that cite P00 or any included primary article cannot increase independent experiment counts.
3. Choosing C4 terms after examining the C3 DEG list would create a post hoc story; freeze questions and databases now.
4. Choosing only genes that fit a skin-repair narrative would hide discordant and unassessed results; the 19-gene bridge retains `NOT_ASSESSED` codes.
5. L10 reuses GSE141814; L15 reuses scGeneScope. Shared raw data cannot be counted twice as independent datasets.

## Pre-Specified C4 Questions

| ID | Question | Future method and candidate database |
|---|---|---|
| Q1 | Are cell-cycle/proliferation programs represented in the ECEV response? | ORA and GSEA; GO Biological Process, Reactome, MSigDB Hallmark. |
| Q2 | Are migration/motility programs represented? | ORA and GSEA; GO Biological Process, Reactome. |
| Q3 | Are ECM organization/remodeling programs altered, and in which direction? | ORA and GSEA; GO Biological Process, Reactome. |
| Q4 | Are angiogenic/endothelial-interaction programs represented? | ORA and GSEA; GO Biological Process, Reactome. This is a question, not an asserted observed phenotype. |
| Q5 | Are inflammatory/immune-response programs altered in fibroblasts? | ORA and GSEA; GO Biological Process, Reactome, MSigDB Hallmark. |
| Q6 | Does the ranked response overlap externally defined regenerative/fibrotic skin-repair programs? | GSEA; ORA as sensitivity; independently defined signatures plus GO/Reactome context. |

## Recommended C4 Analysis Plan

Freeze gene-set sources, releases, identifier mapping, and a DE-tested-gene universe **before** C4 execution. Use threshold-B DEGs for over-representation analysis (ORA) with the 16,271 C3-tested genes as the eligible background, and use an unfiltered-by-significance C3 ranking for GSEA, with a prespecified ranking statistic and tie rule. Run directional analyses where supported, correct for multiple testing, report null results, and distinguish enrichment from measured phenotype. For Q6, define signatures externally, account for human–mouse ortholog mapping and pooled L10/GSE141814 design, and avoid using the P00 DEG table as a signature to validate itself. KEGG is not needed for these six questions at present. **None of these analyses was run in C3.5.**

## Limitations

The scope is 15 supplied records plus the primary paper, not a systematic gene-by-gene literature review. Citation metadata and article availability were verified; some repository file formats and study sample counts remain `NA`. Several studies use different EV sources, species, recipient cells, interventions, or endpoints from EXP001. The primary paper's additional assays do not change the n=3 per group RNA-seq uncertainty. The matrix describes reported measurements and leaves causal transfers as hypotheses. C4 may refine the evidence inventory, but changes to the frozen questions should be declared before looking at enrichment results.

## C3.5 Decision

**PASS — evidence framework and C4 questions documented.** This is a documentation/QA pass, not evidence that ECEVs improve skin repair or that C3 genes belong to particular wound-healing pathways. No enrichment, scoring, or machine learning was performed.
