# EXP002-C2 — Frozen differential-expression plan

**Frozen before EXP002 differential-expression results.** Dataset: GSE251807. C1R permits only a restricted Strategy-A analysis. This plan does not report or infer an EV effect.

## Input and statistical unit

- Use the **189,509 exact shared versioned ENST IDs** across both batches; exclude batch-specific and version-normalized-only IDs.
- Map these IDs exactly to gene IDs with the **compatible** GENCODE v44 (GRCh38.p14) transcript-to-gene table. The authors' original Salmon index is unknown; do not state that they used GENCODE v44.
- Import the filtered Salmon `NumReads`, TPM, and effective lengths with **tximport 1.30.0**, `countsFromAbundance="no"`, exact `tx2gene`, and no transcript-version stripping. The resulting gene counts are **estimated gene-level counts derived from Salmon**, not original integer gene counts.
- Use the tximport object, including its gene-length information/offset, in a DESeq2-compatible count-based framework. Do not submit log-CPM, TPM, or the author-normalized matrix as DESeq2 raw counts. If the tximport object cannot be imported faithfully into a count-based framework, stop and revise the statistical plan **before** inspecting treatment results.
- The working statistical unit is one author-described recipient-cell culture/well/library within **one** NHDF donor lot. EV-preparation independence is unknown. No donor-level or EV-preparation-level generalization is available.

## Primary C3 model and contrast

- Primary inclusion: all 16 mapped libraries, 8 MSC-sEV and 8 DMEM controls; no automatic EV_8 exclusion.
- Pre-DE low-count filter: estimated gene count **≥10 in at least 4 of the 16 libraries**, independent of condition labels. This may differ from the C2 visualization filter.
- Primary design: **`~ batch + condition`**. Batch is included because two balanced processing batches and distinct transcript-reference universes are documented. Do not add a donor, EV-preparation, or pairing term without verified sample-level assignments.
- Reference condition: `CTRL_DMEM`. Contrast: `MSC_sEV` versus `CTRL_DMEM`. Positive log2 fold change means higher estimated expression after MSC-sEV exposure.
- Preferred future framework: DESeq2 standard size-factor/dispersion estimation and Wald testing, using the tximport gene-length information. Use Benjamini–Hochberg adjusted p-values.
- Prespecified result summaries: **A** `padj < 0.05`; **B** `padj < 0.05` and `abs(log2FC) >= 1`. Within B report up (`log2FC >= 1`) and down (`log2FC <= -1`) separately. Do not change thresholds to produce a desired result.
- Report every tested gene and missing adjusted p-value, plus the number excluded by the prefilter. Preserve sample/batch identity and the exact software versions.

## Technical checks that can stop C3

The C2 checkpoint must verify nonnegative finite tximport counts, equality of gene totals and retained transcript estimates, sample mapping, full-rank batch/condition allocation, and sample QC. A serious sample-identity or reference artifact would stop DE and trigger a documented design review. If one sample is suspect, keep all 16 in the primary model unless objective technical evidence justifies exclusion; any leave-one-sample-out run is labeled sensitivity analysis, never a replacement for the primary result.

## EXP002-C2R EV_8 technical adjudication and sensitivity plan

**Added before C3 DE, GSEA, and cross-study biological results.** C2R checked the EV_8 GSM → BioSample → SRA experiment/run → GEO Salmon file → project metadata chain, sequencing depth, quantified totals, expression distribution, correlations, and PCA distances. No affirmative technical defect was found. EV_8 is **RETAINED** despite persistent PCA extremeness. C2's original `REVIEW REQUIRED` record remains a historical checkpoint; [C2R](../../reports/EXP002_C2R_EV8_technical_review.md) resolves the sample issue to **PASS WITH LIMITATIONS**. C1R remains **LIMITED_GO**.

- **Primary C3:** all 16 libraries, 8 `MSC_sEV` and 8 `CTRL_DMEM`; exact-shared tximport estimated gene counts and gene-length offsets; low-count filter estimated count ≥10 in at least 4 libraries; `~ batch + condition`; `MSC_sEV` versus `CTRL_DMEM`. This is the analysis used for primary DE summaries and any later primary GSEA/validation endpoint.
- **Sensitivity C3:** omit only `EV_8`, leaving 15 libraries (7 EV, 8 control; batch 2 has 3 EV and 4 control). Use the same count-based framework, input construction, filtering rule (≥10 in at least 4 retained libraries), model, contrast, thresholds, and gene-set resources. It measures dependence on EV_8 and must never replace the 16-sample primary analysis because of a more favorable result. Compare effects on the intersection of genes tested in both fits and report filtering differences.
- Freeze robustness metrics: Pearson and Spearman correlation of log2FC over shared tested stable gene IDs with finite estimates; sign concordance over the same IDs (report zero or missing exclusions); overlap count **and Jaccard** for `padj < 0.05` sets and for `padj < 0.05 & abs(log2FC) >= 1` sets; P/M/E/A/I GSEA axis-direction stability under the existing [validation endpoint rules](EXP002_VALIDATION_ENDPOINTS.md); and Pearson/Spearman GSEA NES correlation over common eligible gene sets. Report non-significant and discordant findings, the number of common genes/sets, and NA exclusions. The sensitivity findings are robustness evidence only.
- **Batch interaction:** The primary target is the average MSC-sEV effect across two balanced batches. The additive `~ batch + condition` model remains primary. Two batches and one donor lot do not justify adding `batch:condition` to the primary model solely from PCA separation. No model choice will be made from C3 significance. The 15-sample sensitivity design remains full-rank despite mild imbalance.
- Technical exclusion requires affirmative identity, duplication, corruption, incompatible-library, or independently corroborated quantification failure evidence. High library size, PCA extremeness, and later treatment separation are insufficient. Criteria were frozen in [C2R technical criteria](../../configs/exp002_c2r_technical_criteria.json) before the review metrics were calculated.

## Claim boundary

Any future DE result estimates a conditional transcriptional contrast in one recipient donor-lot context under an MSC-sEV preparation structure that is not fully known. It cannot by itself establish wound-healing benefit, donor-level reproducibility, EV-preparation reproducibility, or concordance with EXP001. Cross-study validation follows the separately frozen [validation endpoints](EXP002_VALIDATION_ENDPOINTS.md).
