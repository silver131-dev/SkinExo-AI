# SkinExo-AI EXP003-C4

## Objective

Apply the prospectively frozen pathway analysis to CTX003 and determine how a third independent EV-study context changes the component-aware SkinExo interpretation. GSEA is primary, ORA is secondary, phenotype anchors remain a separate evidence layer, and the framework retains null and discordant findings.

## Why CTX003 Is a Third Context

CTX003 is GSE293956: human dermal fibroblast-derived EV at 10 ug/mL applied to primary human dermal fibroblasts for 72 h. CTX001 uses endothelial-cell EV at 72 h; CTX002 uses bone-marrow MSC small EV at 48 h. The studies, EV sources, doses, and exposure settings differ. CTX003 is independent at study level, while donor and EV-preparation independence remain unknown.

## Frozen Analysis Plan

C2 and C3 are **PASS WITH LIMITATIONS**. C4 used all 13,874 C3-tested genes ranked by signed DESeq2 Wald statistic. It did not change the C2 filter, C3 model, threshold B, P/M/E/A/I map, component vocabulary, or qualification rule. Author pathway findings were not consulted.

## GSEA Methods

The exact MSigDB **2026.1.Hs** GO Biological Process, Reactome, and Hallmark GMT files used for EXP001/EXP002 were reused with verified SHA-256 hashes. GSEApy 1.3.1 prerank used weight 1, 1,000 gene-set permutations, seed 42, and the 15–500 tested-gene effective-size rule in one combined run. A term qualifies for components when FDR < 0.05, its leading edge has at least five genes, and at least 80% of leading-edge Wald statistics agree with NES sign.

Verified symbols were available for 13,771/13,874 tested IDs. The 103 missing-symbol IDs remain in the ranked universe but cannot enter symbol-defined sets. Duplicate symbols map to every matching stable gene ID. [Ranked genes](../outputs/exp003/c4_ranked_genes.csv); [complete GSEA](../outputs/exp003/c4_gsea_all.csv).

## CTX003 Global GSEA

- Tested gene sets: **4,433**.
- FDR < 0.05: **92**.
- FDR < 0.05 with coherent leading edge: **82**.
- Secondary ORA FDR < 0.05: **102 UP**, **0 DOWN**.

ORA uses only 20 threshold-B UP genes and zero DOWN genes, so it has limited power. It cannot override ranked GSEA. 45 significant GSEA terms fall outside the frozen P/M/E/A/I map; they are retained as `POST_HOC_EXPLORATORY` and do not determine primary endpoints.

## P — Proliferation / Cell Cycle

**CTX003: OBSERVED_NULL / NO_QUALIFIED_COMPONENT.** Active components: **None**. No frozen P term met primary GSEA FDR and coherence criteria. Secondary ORA found three epithelial-proliferation terms, but the preregistered hierarchy keeps the GSEA endpoint null.

The previously shared CTX001/CTX002 component `P081` is not active in CTX003. The candidate conserved component therefore remains **two-context only**; the three-context table records `NULL_NOT_TESTABLE`. Transcriptomics does not establish proliferation.

## M — Migration / Motility

**CTX003: QUALIFIED, POSITIVE.** Active components: **M003, M010, M011, M025**.

- `GOBP_GRANULOCYTE_CHEMOTAXIS`: NES +2.563, FDR <0.001 (permutation estimate), component M003.
- `GOBP_GRANULOCYTE_MIGRATION`: NES +2.490, FDR 0.000135, component M003.
- `GOBP_CELL_CHEMOTAXIS`: NES +2.454, FDR 0.000304, component M003.
- `GOBP_LEUKOCYTE_CHEMOTAXIS`: NES +2.433, FDR 0.000434, component M003.
- `GOBP_LEUKOCYTE_MIGRATION`: NES +2.389, FDR 0.000572, component M003.
- `GOBP_MYELOID_LEUKOCYTE_MIGRATION`: NES +2.280, FDR 0.00364, component M003.
- `GOBP_NEUTROPHIL_CHEMOTAXIS`: NES +2.258, FDR 0.00525, component M003.
- `GOBP_NEUTROPHIL_MIGRATION`: NES +2.209, FDR 0.011, component M003.
- `GOBP_REGULATION_OF_GRANULOCYTE_CHEMOTAXIS`: NES +2.116, FDR 0.0281, component M025.
- `GOBP_LYMPHOCYTE_MIGRATION`: NES +2.107, FDR 0.0299, component M011.
- `GOBP_POSITIVE_REGULATION_OF_LEUKOCYTE_MIGRATION`: NES +2.086, FDR 0.0343, component M003.
- `GOBP_LYMPHOCYTE_CHEMOTAXIS`: NES +2.038, FDR 0.0447, component M010.

CTX003 directly opposes CTX001 at components `M003` and `M025`. It shares a positive broad-axis direction with CTX002 but no exact active M component. The three-context interpretation remains **DISCORDANT**. The 24 h scratch assay is a separate functional anchor and does not set 72 h GSEA significance.

## E — ECM Organization / Remodeling

**CTX003: OBSERVED_NULL / NO_QUALIFIED_COMPONENT.** Active components: **None**. No frozen E term met primary GSEA or secondary ORA FDR criteria. With CTX002 also null and CTX001 carrying the only qualified E components, the three-context endpoint remains **NULL_NOT_TESTABLE**. Mouse scar and collagen outcomes remain separate `IN_VIVO` evidence and do not establish a fibroblast ECM transcriptomic phenotype.

## A — Vascular / Endothelial Interaction

**CTX003: QUALIFIED, POSITIVE.** Active component: **A008**.

- `GOBP_ENDOTHELIAL_CELL_APOPTOTIC_PROCESS`: NES +2.322, FDR 0.00237, component A008.

`A008` is negative in CTX001 and positive in CTX003, a direct component-level discordance. CTX003 broadly aligns with positive CTX002 A-axis activity through different components. The three-context interpretation is **DISCORDANT**. Endothelial-apoptosis transcriptional association is not angiogenesis, neovascularization, or therapeutic vascular benefit.

## I — Inflammation / Immune Signaling

**CTX003: QUALIFIED, POSITIVE.** Active components: **I004, I008, I009, I012, I015, I025, I041, I043, I044, I076, I080, I093, I102, I108, I111, I112, I114, I115, I116, I117, I118, I123, I131, I136, I142, I144, I145**.

Top frozen qualified terms:

- `HALLMARK_INFLAMMATORY_RESPONSE`: NES +2.787, FDR <0.001 (permutation estimate), component I115.
- `HALLMARK_INTERFERON_GAMMA_RESPONSE`: NES +2.574, FDR <0.001 (permutation estimate), component I117.
- `HALLMARK_TNFA_SIGNALING_VIA_NFKB`: NES +2.866, FDR <0.001 (permutation estimate), component I118.
- `GOBP_LEUKOCYTE_CHEMOTAXIS`: NES +2.433, FDR 0.000434, component I041.
- `GOBP_HUMORAL_IMMUNE_RESPONSE`: NES +2.435, FDR 0.000467, component I015.
- `GOBP_ANTIMICROBIAL_HUMORAL_IMMUNE_RESPONSE_MEDIATED_BY_ANTIMICROBIAL_PEPTIDE`: NES +2.396, FDR 0.000531, component I004.
- `GOBP_LEUKOCYTE_MIGRATION`: NES +2.389, FDR 0.000572, component I041.
- `REACTOME_INTERLEUKIN_10_SIGNALING`: NES +2.380, FDR 0.000607, component I131.
- `HALLMARK_ALLOGRAFT_REJECTION`: NES +2.311, FDR 0.00282, component I111.
- `GOBP_TOLL_LIKE_RECEPTOR_SIGNALING_PATHWAY`: NES +2.301, FDR 0.00312, component I108.
- `GOBP_MYELOID_LEUKOCYTE_MIGRATION`: NES +2.280, FDR 0.00364, component I041.
- `HALLMARK_IL6_JAK_STAT3_SIGNALING`: NES +2.276, FDR 0.00378, component I114.

CTX003 shares nine positive components with CTX002: `I111`, `I114`, `I115`, `I116`, `I117`, `I118`, `I131`, `I136`, and `I144`. It shares no exact active I component with CTX001, although all three contexts have positive-dominant I-axis activity. The result is **CONSERVED_AXIS_CONTEXT_VARIANT**: component-level recurrence for CTX002/CTX003 and broad thematic overlap only with CTX001. It is not a universal positive inflammatory label.

## Phenotype Anchors

- P: author-reported hDF CCK-8 at 24 h; same EV source/recipient, different time from 72 h RNA-seq.
- M: author-reported hDF scratch assay at 24 h; same EV source/recipient, different time.
- Mouse wound closure, scar length, and collagen deposition: different species/model `IN_VIVO` evidence.
- No phenotype anchor changes a GSEA FDR, component direction, or null result.

## CTX001 vs CTX003

P and E are `NULL_NOT_TESTABLE` because CTX003 has no qualified component. M is `DISCORDANT` through opposite `M003`/`M025`; A is `DISCORDANT` through opposite `A008`; I is `CONSERVED_AXIS` with different active components.

## CTX002 vs CTX003

P and E are `NULL_NOT_TESTABLE`. M and A are `CONSERVED_AXIS` through positive but different components. I is `CONSERVED_COMPONENT` through nine exact positive components. These pairwise states remain bounded to their observed contexts.

## Three-Context Interpretation

| Axis | CTX003 state | Active CTX003 components | Three-context interpretation |
| --- | --- | --- | --- |
| P | Observed null | None | NULL_NOT_TESTABLE; P081 remains two-context only |
| M | Positive | M003, M010, M011, M025 | DISCORDANT |
| E | Observed null | None | NULL_NOT_TESTABLE |
| A | Positive | A008 | DISCORDANT |
| I | Positive | I004, I008, I009, I012, I015, I025, I041, I043, I044, I076, I080, I093, I102, I108, I111, I112, I114, I115, I116, I117, I118, I123, I131, I136, I142, I144, I145 | CONSERVED_AXIS_CONTEXT_VARIANT |

Across three contexts, selected response components show reproducible or context-dependent patterns. A broad universal EV response is **not supported**.

## Global NES Similarity

Secondary descriptive correlations over pairwise shared eligible gene sets:

- CTX001 vs CTX002: n=4,553, Pearson -0.0773, Spearman -0.1318.
- CTX001 vs CTX003: n=4,382, Pearson -0.1692, Spearman -0.1767.
- CTX002 vs CTX003: n=4,383, Pearson +0.1878, Spearman +0.1945.

The correlations are weak, with CTX001 negatively related to both later contexts and CTX002/CTX003 weakly positive. They do not determine axis endpoints and are not machine learning or retrieval performance. [Three-context response map](../outputs/exp003/figures/fig09_three_context_response_map.png).

## Reliability

CTX003 has n=3 per condition; donor count, EV-preparation count, pairing, and exact control medium/vehicle are unknown; batch is not documented; the dominant replicate-label-associated PC1 structure remains unexplained. C3 had no convergence failure, Cook cutoff exceedance, or missing p-value, but those diagnostics do not resolve design metadata. Gene-set permutations do not represent sample-label uncertainty. Phenotype anchors differ in time or model.

## Claim Boundaries

This analysis does not establish a universal EV response, therapeutic efficacy, independent-donor replication, EV-preparation-level replication, causal cargo-response mechanisms, human wound-healing efficacy, or angiogenic activity. GSE293957 was not analyzed. No fourth transcriptomic context, retrieval system, or predictive model was added.

## C4 Decision

**PASS WITH LIMITATIONS.** The frozen ranking, gene-set release, GSEA workflow, component map, and third-context endpoints executed completely. The framework was updated only after interpretation was frozen. Reliability limits remain material, null results remain explicit, and the broad five-axis universal-response hypothesis remains unsupported.
