# SkinExo-AI DEV-C0

**Date:** 2026-09-30

**Purpose:** First reproducible local Git checkpoint; scientific result files are frozen as already verified.
**Next planned checkpoint:** EXP002-D0 — Independent Human Fibroblast EV Dataset Discovery.

## Verified checkpoints

- EXP001-C1 — PASS
- EXP001-C2 — PASS
- EXP001-C3 — PASS
- EXP001-C3.5 — PASS
- EXP001-C4 — PASS
- SUBMISSION-S1 — PASS (draft scaffold, not final submission)

## Frozen results

| Checkpoint | Record |
|---|---|
| C1 | 58,735 gene rows; 6 biological samples; CTRL 3; ECEV 3. |
| C2 | 14,755 QC-retained genes; PC1 86.59%; PC2 5.90%. PCA is exploratory. |
| C3 | 16,271 genes tested; 6,612 with padj < 0.05; 2,032 with padj < 0.05 and \|log2FC\| ≥ 1; 995 up; 1,037 down; same-dataset author log2FC concordance Pearson r = 0.99999979. |
| C3.5 | 16 literature records verified; 4 public datasets cataloged. |
| C4 | 16,271 ranked genes; MSigDB 2026.1.Hs; GSEA primary and ORA secondary. Q1 supported at cell-cycle transcriptomic-program level; Q2 and Q3 supported at transcriptomic-association level; Q4 supported for broader vascular/endothelial associations while angiogenesis itself remains unsupported; Q5 supported at transcriptomic-association level; Q6 not yet testable without separate external regenerative-like and fibrotic-like signatures. |

The primary comparison is ECEV 72 h versus CTRL 72 h in primary human dermal fibroblasts (n=3 per condition). Positive log2 fold change means higher expression in ECEV. Full methods, limits, and result tables are in the checkpoint [reports](../../reports/) and [JSON files](../../outputs/exp001/). [Reproducibility instructions](../REPRODUCIBILITY.md) identify source files and ignored external inputs.

## Claim boundary

This checkpoint does **not** demonstrate improved wound healing, regeneration, anti-fibrotic activity, angiogenesis, therapeutic efficacy, predictive AI, or generalization. Pathway enrichment is transcriptomic association, not direct phenotype evidence. The author DEG comparison uses the same source data and is not independent biological validation.

## Repository boundary

Commit source code, curated metadata, reports, submission drafts, compliance records, small result tables, and team-generated figures. Keep GEO raw archives, MSigDB GMT caches, processed matrices, Python/R environments, and temporary files outside version control. No remote, push, release tag, or EXP002 work belongs to DEV-C0.
