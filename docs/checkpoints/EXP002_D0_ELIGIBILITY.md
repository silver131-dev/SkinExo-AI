# EXP002-D0 locked dataset eligibility

**Locked on:** 2026-09-30, before the EXP002 public dataset search.  
**Reference:** EXP001 GSE293186, human primary dermal fibroblasts, endothelial-cell-derived EV exposure for 72 h versus control, bulk RNA-seq.  
**Purpose:** Identify an independent public comparison suitable for external validation. This document defines selection before candidate inspection; it does not authorize analysis or data download.

## Required for a primary EXP002 dataset

All eight conditions must be verified from a repository record, primary paper, or linked official supplementary metadata:

1. A study and biological samples independent of GSE293186; a reanalysis, mirror, or supplementary copy of those samples fails.
2. Extracellular-vesicle or exosome exposure is the perturbation applied to recipient cells, not merely EV secretion by those cells.
3. Fibroblasts are the recipient cells, with their tissue and species identifiable.
4. A transcriptomic readout is available (RNA-seq or expression microarray); distinguish bulk, single-cell, and platform.
5. An EV-treatment group exists.
6. A control or comparator group exists.
7. Reusable public expression data are accessible from a named repository or official supplement; record whether raw reads, processed expression, and raw counts are actually available.
8. Sample-level metadata identify treatment and control samples sufficiently to reconstruct the comparison, including a sample-to-file map or explicit accessions.

An unknown required condition is **UNCERTAIN**, not an assumed pass. A documented failure is **INELIGIBLE**. Cell-line and non-dermal fibroblast experiments can satisfy the required criteria but have lower biological comparability. Biological replicates are preferred; a single sample per arm cannot support robust gene-level validation and must be flagged.

## Tiers and suitability

- **Tier A / ELIGIBLE_A:** Independent human dermal or skin fibroblast EV-treatment transcriptomics with an identifiable comparator and public sample-resolved data.
- **Tier B / ELIGIBLE_B:** Independent human fibroblast EV-treatment transcriptomics meeting the same requirements, but recipient tissue is not dermal/skin or is not verified as such.
- **Tier C / ELIGIBLE_C:** EV-response transcriptomics in another species or a non-fibroblast recipient, with comparator and public sample-resolved data. Tier C is **not** primary EXP002 replication; it may support a secondary cross-context question.
- **INELIGIBLE:** Any required element is demonstrably absent, including studies measuring EV-producing fibroblasts rather than EV-treated recipients, no transcriptomic data, no comparator, or reuse of GSE293186 samples.
- **UNCERTAIN:** Plausible candidate with unresolved required metadata or inaccessible sample-to-file mapping. Do not recommend as primary until resolved.

## Preferred, not mandatory

Human species; dermal/skin tissue; primary fibroblasts; biological replicates; raw counts or reads from which counts can be reconstructed; documented EV source and type; dose; exposure duration; functional phenotype in the same study; primary research paper. A complete sample-level design and independent biological replicates are especially important for directional gene-level concordance.

## Qualitative comparison and validation value

Compare species, recipient identity, tissue, EV source, EV type, dose, time, omics platform, and design with **MATCH**, **PARTIAL_MATCH**, **MISMATCH**, or **UNKNOWN**. Assess possible gene-direction, pathway, P/M/E/A/I, regenerative/fibrotic, and general EV-response validation as **STRONG**, **MODERATE**, **WEAK**, or **NOT_APPROPRIATE**, with a reason. No numeric score, condition-label-driven search, or outcome-driven choice is allowed. Matching samples and metadata take priority over a suggestive title.
