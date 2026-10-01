# EXP003-C2 — Frozen analysis plan

**Frozen before EXP003 differential-expression or pathway results.** Dataset: GSE293956. Context: CTX003, hDF-EV-treated human dermal fibroblasts versus control-labeled human dermal fibroblasts after 72 h. This plan estimates a conditional transcriptomic contrast. It does not establish a phenotype, donor-level response, EV-preparation-level response, or cross-context conservation.

## Input and parser boundary

- Primary input: official GEO raw integer gene-count matrix `GSE293956_hDF_total_count.txt.gz` with SHA-256 `f30d382112d04c9e3f147fc350f8f58e6306da414a617b5cd4dd52c1fd8ec76d`.
- Apply the validated C1 rule exactly: exclude only the single contiguous trailing block whose identifier is blank and whose six expression cells are blank or `NA`, `N/A`, `#N/A`, or `NULL`. Retain every row with a nonblank gene identifier, including every all-zero biological row.
- The unchanged source has 1,048,575 physical data rows. The parser returns 60,675 unique, versionless Ensembl gene rows and excludes 987,900 structural padding rows.
- All six verified hDF libraries are retained: three `HDF_EV` and three `CONTROL`. HaCaT data are outside CTX003 and outside this plan.

## Frozen low-expression rule

Before PCA was fitted, the primary QC filter and future C3 testing filter were fixed as:

> **CPM ≥ 1 in at least 3 of the 6 libraries.**

CPM denominators are the raw column sums across all 60,675 valid biological rows. The rule uses no condition labels. C2 found that it retains 13,874 genes. This rule will be applied to the untransformed raw count matrix before constructing the C3 DESeq2 dataset. It must not be changed after reviewing C3 results.

The alternatives evaluated descriptively in C2 were CPM ≥ 0.5 in at least 3 libraries, CPM ≥ 1 in at least 2, and CPM ≥ 2 in at least 3. Their retention counts do not select the primary rule and are recorded in `outputs/exp003/filtering_summary.csv`.

## QC representation

C2 sample QC uses `log2(CPM + 1)` on the 13,874 primary-filtered genes. Pearson sample correlation and PCA use this representation. PCA centers each feature, does not scale genes to unit variance, and fits samples as observations without condition labels. Top-variable-gene robustness sets are selected solely by across-sample variance.

This transformation is only a QC representation. C3 will use untransformed integer counts in its count model.

## Statistical unit and unresolved design

The operational statistical unit is one RNA-seq library. The number and identity of recipient donors are unknown. The number and mapping of independent EV preparations are unknown. Sample pairing is not documented, so replicate numbers do not define pairs. No authoritative batch variable is documented, so GSM order, matrix-column order, replicate numbering, or PCA position cannot be converted into a batch covariate.

C2 found stable latent structure on PC1: the two replicate-1-labeled samples are separated from the four replicate-2/3-labeled samples. Each side contains EV and control libraries, and no single library dominates the structure. Because no authoritative factor explains this pattern, it remains descriptive and is not assigned as donor, batch, or pairing.

## Frozen primary differential-expression model

- Framework: DESeq2 negative-binomial count model.
- Primary design: `~ condition`.
- Condition reference: `CONTROL`.
- Contrast: `HDF_EV` versus `CONTROL`.
- Positive log2 fold change: higher expression in hDF-EV-treated hDF.
- Input: official raw integer counts after the frozen CPM filter.
- Normalization and inference: standard DESeq2 size-factor and dispersion estimation, Wald test, Benjamini–Hochberg adjusted p-values, and standard result-level independent filtering. Report the exact DESeq2 and R versions at C3.
- Fold-change reporting: unshrunken DESeq2 estimates unless a separately labeled visualization later uses shrinkage. Any such visualization cannot replace the primary estimates.
- No pairing, donor, EV-preparation, or batch term is permitted without new authoritative sample-level metadata. A post-QC latent axis is not sufficient evidence for such a term.

The design is frozen as `~ condition` because treatment is the only documented sample-level design factor. If authoritative metadata later establishes a required covariate before C3 is run, C3 must stop for a documented design review instead of silently changing the model.

## Frozen reporting thresholds

- **A:** `padj < 0.05`.
- **B:** `padj < 0.05 AND |log2FC| >= 1`.

Within B, report higher-in-EV and lower-in-EV genes separately. Report all tested genes, missing adjusted p-values, and the number removed by the frozen prefilter. Do not change these thresholds after seeing the C3 result.

## Frozen pathway plan

Pathway analysis begins only after C3 is complete. Its primary method is preranked GSEA over all C3-tested genes ordered by the signed DESeq2 Wald statistic. Positive ranking values and positive NES mean association with genes higher in hDF-EV; they do not imply a beneficial phenotype.

- Release: **MSigDB 2026.1.Hs**.
- Collections: GO Biological Process, Reactome, and Hallmark.
- Existing collection files and SHA-256 checksums: use the exact resources recorded in `configs/exp001_c4_frozen_plan.json`.
- Existing axis map: use `data/metadata/skinexo_c4_term_map.csv` and the F1 P/M/E/A/I response/component definitions without adding terms because of CTX003 results.
- Gene-set size: retain the established 15–500 effective tested-gene range.
- GSEA settings: gene-set permutations, weight 1, 1,000 permutations, seed 42, and FDR < 0.05, matching the established project plan.
- Leading-edge qualification: at least five leading-edge gene IDs and at least 80% with Wald-statistic sign aligned with NES, matching the existing project rule.
- ORA: secondary and supportive only, using the C3-tested gene universe and the frozen threshold-B higher/lower sets. ORA cannot override the primary GSEA result.

Any later software-version adjustment required for compatibility must preserve the resources, ranking, thresholds, seed, and qualification rules and must be documented before C4 is executed.

## Phenotype evidence boundary

The hDF CCK-8 proliferation/viability and scratch-migration assays are functional-assay evidence at 24 h. The CTX003 transcriptome is measured at 72 h. Functional evidence may support biological plausibility but cannot be treated as identical-timepoint transcriptomic validation.

Mouse wound closure, scar length, and collagen deposition are an `IN_VIVO` evidence layer in a different species and model. They are not direct human-fibroblast transcriptomic validation. No phenotype result changes the DE model, filter, pathway term map, or significance threshold.

## Reliability limits fixed before C3

- Three libraries per condition.
- Recipient donor count and donor-to-library mapping: `UNKNOWN`.
- Independent EV preparation count and preparation-to-library mapping: `UNKNOWN`.
- Pairing: `NO_EVIDENCE / UNKNOWN`.
- Batch: `NOT_DOCUMENTED`.
- Exact RNA-seq control medium and vehicle: `UNKNOWN`.
- No donor-level or EV-preparation-level generalization.
- Stable unexplained PC1 structure remains a design limitation even if later treatment estimates are strong.

These limits remain in force regardless of PCA separation, DEG count, pathway significance, or agreement with another context.

## Stop boundary

EXP003-C2 performs sample QC and preregistration only. No differential-expression fit, GSEA, ORA, CTX003 biological response assignment, or CTX001/CTX002 biological comparison is part of this checkpoint.
