# SkinExo-AI EXP001-C4

## Objective

Identify transcriptomic program associations with the ECEV-versus-CTRL response in primary human dermal fibroblasts. Enrichment is association, not a directly measured repair phenotype.

## Pre-Specified Questions

C3.5 froze Q1 cell cycle/proliferation, Q2 migration/motility, Q3 ECM organization/remodeling, Q4 angiogenic/endothelial interaction, Q5 inflammatory/immune response, and Q6 external regenerative-like versus fibrotic-like programs. The exact source releases, keyword rules, thresholds, status logic, and figure-selection rule were frozen in [`exp001_c4_frozen_plan.json`](../configs/exp001_c4_frozen_plan.json) before enrichment. GSEA is the **primary** pathway-level evidence; ORA is secondary.

## Input Data

C3 and C3.5 checkpoints passed. The unchanged C3 DESeq2 all-gene and threshold-B tables were read. C3/C3.5 outputs were not modified. The ECEV-versus-CTRL contrast uses CTRL as reference; positive Wald statistic and log2FC mean higher expression in ECEV.

## Gene Universe

ORA background: **16,271 C3-tested gene IDs**. All had a nonblank gene symbol; 11 symbols represented 25 gene IDs. Symbol-to-gene-set mapping retained every gene ID, including duplicates. 11,860 IDs occur in at least one of the three source collections; 4,411 occur in none and are listed in [`c4_unmapped_gene_ids.csv`](../outputs/exp001/c4_unmapped_gene_ids.csv). Sets were restricted to tested IDs; eligible effective sizes were 15–500. The tested universe, rather than the whole genome, was used for ORA.

## Gene Ranking

All **16,271** tested gene IDs were ranked by the DESeq2 Wald `stat` descending, with gene_id as a deterministic tie rule (no ties occurred). No significance filter or adjusted-p ranking was used. [`c4_ranked_genes.csv`](../outputs/exp001/c4_ranked_genes.csv) preserves the ranking and C3 values.

## Gene-Set Sources

[MSigDB human v2026.1.Hs](https://www.gsea-msigdb.org/gsea/msigdb/collections.jsp) supplied all three collections. The [release notes](https://docs.gsea-msigdb.org/MSigDB/Release_Notes/MSigDB_2026.1.Hs/) record the underlying GO and Reactome versions. Exact GMT URLs and SHA-256 hashes are preserved in [`c4_gene_set_manifest.json`](../outputs/exp001/c4_gene_set_manifest.json); the small GMT files are cached under Git-ignored `data/raw/c4_gene_sets/`. Source gene sets are not checked into the repository. Of 9,427 source sets, 4,600 had 15–500 C3-tested gene IDs and were analyzed. The source release details are: GO BP — GO-basic 2025-10-10; NCBI gene2go 2025-12-14 per MSigDB 2026.1 notes; Reactome — Reactome architecture release 95 per MSigDB 2026.1 notes; Hallmark — MSigDB Hallmark 2026.1.Hs. Consult the [MSigDB license](https://www.gsea-msigdb.org/gsea/msigdb_license_terms.jsp) before redistribution.

The initial predefined Q5 lexical pattern accidentally matched `CYTOKINESIS` through the prefix `CYTOKINE`. The documented QA correction required `CYTOKINE` to end or be followed by an underscore; it removed cell-division false positives from Q5 irrespective of significance. No question, threshold, or additional term family changed; the complete analysis was rerun. The correction is recorded in the frozen-plan JSON and checkpoint.

## ORA

Hypergeometric upper-tail tests used the 16,271 tested IDs, separately for **995 UP** and **1,037 DOWN** threshold-B genes. Benjamini–Hochberg correction was applied across all 4,600 eligible terms from all three collections separately per direction. Complete eligible-term tables, including nonsignificant terms and zero overlaps: [`UP`](../outputs/exp001/c4_ora_up_all.csv) and [`DOWN`](../outputs/exp001/c4_ora_down_all.csv). Significant terms at FDR < 0.05: **301 UP**, **438 DOWN**. ORA is secondary to the ranked analysis; overlapping gene sets are not independent findings.

## GSEA

GSEApy **1.3.1** preranked GSEA used all 16,271 Wald statistics, weighted running score (weight 1), 1,000 gene-set permutations, seed 42, and a single combined three-collection run so reported FDR is estimated across the combined tested sets. Complete results: [`c4_gsea_all.csv`](../outputs/exp001/c4_gsea_all.csv), with NES, nominal p, FDR, and leading-edge IDs/symbols. **640** sets have FDR < 0.05. Positive NES associates a set with ECEV-higher genes; negative NES with ECEV-lower genes. It does **not** indicate beneficial or harmful repair. Permutation p-values have finite resolution; numeric zeros in estimated nominal p or FDR are displayed as <0.001 in figures/text, not exact zero probability. Gene-set permutations do not capture all uncertainty from n=3/group. Leading-edge coherence was prespecified as ≥5 genes and ≥80% Wald-stat sign agreement with NES.

## Q1 — Proliferation / Cell Cycle

**PRE-SPECIFIED. Status: SUPPORTED.** Mapped Proliferation / cell cycle gene sets show ranked transcriptomic association; this does not demonstrate the corresponding cellular phenotype.

GSEA primary: 116 significant mapped terms; 116 coherent leading edges. ORA secondary: UP 97 significant mapped terms; DOWN 11 significant mapped terms.

- GSEA Hallmark `HALLMARK_E2F_TARGETS`: NES +3.177, FDR <0.001 (permutation estimate), leading edge n=130, same-sign fraction 1.00.
- GSEA Hallmark `HALLMARK_G2M_CHECKPOINT`: NES +3.013, FDR <0.001 (permutation estimate), leading edge n=118, same-sign fraction 1.00.
- GSEA Reactome `REACTOME_CELL_CYCLE_MITOTIC`: NES +2.861, FDR <0.001 (permutation estimate), leading edge n=240, same-sign fraction 1.00.

Literature coding: DIRECT 3, INDIRECT 1; independent external DIRECT 2. n=3/condition; competitive gene-set association; overlapping terms; no direct phenotype measurement by C4. Cell-cycle transcription is distinct from experimentally measured proliferation.

E2F/G2M and related leading edges support a **cell-cycle transcriptional program** among ECEV-higher genes. C4 did not measure cell division or proliferation. These overlapping sets are related annotations, not independent confirmations.

## Q2 — Migration / Motility

**PRE-SPECIFIED. Status: SUPPORTED.** Mapped Migration / motility gene sets show ranked transcriptomic association; this does not demonstrate the corresponding cellular phenotype.

GSEA primary: 7 significant mapped terms; 7 coherent leading edges. ORA secondary: UP 8 significant mapped terms; DOWN 20 significant mapped terms.

- GSEA GO_BP `GOBP_NEGATIVE_CHEMOTAXIS`: NES -2.125, FDR 0.0015, leading edge n=21, same-sign fraction 1.00.
- GSEA GO_BP `GOBP_REGULATION_OF_CHEMOTAXIS`: NES -1.935, FDR 0.0242, leading edge n=49, same-sign fraction 1.00.
- GSEA GO_BP `GOBP_REGULATION_OF_GRANULOCYTE_CHEMOTAXIS`: NES -1.901, FDR 0.0281, leading edge n=11, same-sign fraction 1.00.

Literature coding: DIRECT 2, INDIRECT 1; independent external DIRECT 1. n=3/condition; competitive gene-set association; overlapping terms; no direct phenotype measurement by C4.

The strongest mapped terms concern **chemotaxis regulation**, including negative chemotaxis, among ECEV-lower genes. This is not a direct fibroblast migration assay and does not establish increased or decreased cell motility.

## Q3 — ECM Organization / Remodeling

**PRE-SPECIFIED. Status: SUPPORTED.** Mapped ECM organization / remodeling gene sets show ranked transcriptomic association; this does not demonstrate the corresponding cellular phenotype.

GSEA primary: 5 significant mapped terms; 5 coherent leading edges. ORA secondary: UP 4 significant mapped terms; DOWN 15 significant mapped terms.

- GSEA GO_BP `GOBP_COLLAGEN_FIBRIL_ORGANIZATION`: NES -1.995, FDR 0.0145, leading edge n=31, same-sign fraction 1.00.
- GSEA Reactome `REACTOME_EXTRACELLULAR_MATRIX_ORGANIZATION`: NES -1.949, FDR 0.0232, leading edge n=90, same-sign fraction 1.00.
- GSEA Reactome `REACTOME_NON_INTEGRIN_MEMBRANE_ECM_INTERACTIONS`: NES -1.933, FDR 0.0237, leading edge n=31, same-sign fraction 1.00.

Literature coding: DIRECT 3, INDIRECT 1; independent external DIRECT 2. n=3/condition; competitive gene-set association; overlapping terms; no direct phenotype measurement by C4.

Collagen-fibril and ECM-organization terms show negative NES, associating them with ECEV-lower genes. This does not measure collagen deposition, matrix architecture, or scar outcome in C4.

## Q4 — Angiogenesis / Endothelial Interaction

**PRE-SPECIFIED. Status: SUPPORTED.** Mapped Angiogenesis / endothelial interaction gene sets show ranked transcriptomic association; this does not demonstrate the corresponding cellular phenotype.

GSEA primary: 4 significant mapped terms; 4 coherent leading edges. ORA secondary: UP 2 significant mapped terms; DOWN 12 significant mapped terms.

- GSEA GO_BP `GOBP_VASCULAR_ASSOCIATED_SMOOTH_MUSCLE_CELL_PROLIFERATION`: NES -2.065, FDR 0.00524, leading edge n=22, same-sign fraction 1.00.
- GSEA GO_BP `GOBP_POSITIVE_REGULATION_OF_ENDOTHELIAL_CELL_APOPTOTIC_PROCESS`: NES -1.904, FDR 0.0278, leading edge n=11, same-sign fraction 1.00.
- GSEA GO_BP `GOBP_ENDOTHELIAL_CELL_APOPTOTIC_PROCESS`: NES -1.860, FDR 0.032, leading edge n=20, same-sign fraction 1.00.

Literature coding: DIRECT 0, INDIRECT 1; independent external DIRECT 0. n=3/condition; competitive gene-set association; overlapping terms; no direct phenotype measurement by C4. C3.5 direct angiogenesis study count is zero; pathway association cannot establish angiogenesis.

The significant predefined Q4 terms concern vascular-associated smooth-muscle proliferation and endothelial-cell apoptosis; **no term containing `ANGIOGENESIS` reached GSEA FDR < 0.05** (9 eligible angiogenesis-named terms checked). Q4's rule-based `SUPPORTED` status applies only to the broad vascular/endothelial transcriptomic family. Angiogenesis itself and an angiogenic phenotype remain unsupported by this analysis; C3.5 direct angiogenesis evidence is zero.

## Q5 — Inflammation / Immune Response

**PRE-SPECIFIED. Status: SUPPORTED.** Mapped Inflammation / immune response gene sets show ranked transcriptomic association; this does not demonstrate the corresponding cellular phenotype.

GSEA primary: 7 significant mapped terms; 7 coherent leading edges. ORA secondary: UP 14 significant mapped terms; DOWN 14 significant mapped terms.

- GSEA Reactome `REACTOME_GENE_AND_PROTEIN_EXPRESSION_BY_JAK_STAT_SIGNALING_AFTER_INTERLEUKIN_12_STIMULATION`: NES +1.850, FDR 0.00359, leading edge n=15, same-sign fraction 1.00.
- GSEA GO_BP `GOBP_SOMATIC_DIVERSIFICATION_OF_IMMUNE_RECEPTORS_VIA_SOMATIC_MUTATION`: NES +1.635, FDR 0.0321, leading edge n=6, same-sign fraction 1.00.
- GSEA Reactome `REACTOME_INTERLEUKIN_12_SIGNALING`: NES +1.630, FDR 0.0333, leading edge n=15, same-sign fraction 1.00.

Literature coding: DIRECT 2, INDIRECT 1; independent external DIRECT 2. n=3/condition; competitive gene-set association; overlapping terms; no direct phenotype measurement by C4.

The strongest remaining Q5 terms include IL-12/JAK–STAT and immune-receptor annotations. Such gene-set labels in bulk fibroblast RNA-seq do not demonstrate immune-cell behavior or a beneficial inflammatory state. The cell-division `CYTOKINESIS` false matches were removed by the documented mapping QA correction.

## Q6 — Regenerative vs Fibrotic Programs

**PRE-SPECIFIED; NOT YET TESTABLE.** Regenerative-like and fibrotic-like require **separate externally defined directional signatures**. C3.5 verified GSE141814, but it has one pooled mouse scRNA-seq library per fate and no validated signed signatures were cataloged. Deriving a signature would require additional external analysis and species/ortholog handling, so neither GSEA nor ORA was run for Q6. The two contexts were not treated as opposite ends of a single score.

## Evidence Integration

[`c4_evidence_integration.csv`](../outputs/exp001/c4_evidence_integration.csv) combines mapped GSEA (primary), ORA (secondary), and C3.5 direct/indirect literature counts. A `SUPPORTED` label refers only to a transcriptomic program association with coherent GSEA plus same-direction ORA; it never denotes experimentally verified proliferation, migration, ECM change, angiogenesis, inflammation, or wound healing. P00 is the same source study as GSE293186 and is not independent validation. Literature counts span different models and may include non-EV experiments. The pathway and evidence-map figures encode the differences: [Figure 8](../outputs/exp001/figures/fig08_pathway_enrichment.png), [Figure 9](../outputs/exp001/figures/fig09_skinexo_evidence_map.png). Figure 8 uses the frozen FDR/|NES| and leading-edge Jaccard >0.5 redundancy rule within each question; all terms remain in the result tables.

## Post-Hoc Exploratory Findings

**None promoted to a biological claim.** Unmapped significant terms remain in the complete ORA/GSEA tables. Any later narrative about them must be labeled `POSTHOC_EXPLORATORY` and cannot change the frozen Q1–Q6 interpretation.

## Limitations

n=3 biological replicates per condition; one bulk RNA-seq experiment; overlapping and annotation-dependent gene sets; gene-set permutation uncertainty; symbol mapping from C3 annotations; no new phenotype assay. Q4's C3.5 literature direct angiogenesis count remains zero even if vascular terms enrich. Cell-cycle transcription is not proof of increased proliferation. The GSE293186 primary paper and author DEG archive are same-dataset evidence, not independent validation. Q6 is untested. No SkinExo numerical score or machine-learning model was produced.

## C4 Decision

**PASS** for the prespecified pathway-analysis checkpoint, with Q6 explicitly `NOT_YET_TESTABLE`. This decision assesses execution and documentation, not therapeutic efficacy or validation of any phenotype.
