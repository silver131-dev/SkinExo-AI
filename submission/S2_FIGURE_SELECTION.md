# SkinExo-AI S2 figure selection

## Final core set

| Order | Figure | Use | Claim supported | Key limitation |
|---|---|---|---|---|
| 1 | `fig09_skinexo_platform_architecture.png` | README, Technical Report, Kaggle Writeup, opening video section | Public studies flow through context normalization, reproducible analysis, Atlas, evidence/reliability, retrieval, and Explorer. | Use the PUBLIC-GITHUB-V1 version that marks R1 and A1 implemented; predictive AI remains absent. |
| 2 | `fig08_context_aware_response_atlas.png` | Technical Report, Kaggle Writeup, science section of video | The same fibroblast recipient exhibits different P/M/E/A/I response structures across three EV contexts. | Axis summaries sit above component records; null and phenotype layers must remain visibly distinct. |
| 3 | `fig10_context_retrieval.png` | Technical Report, Kaggle Writeup, live-demo setup | CTX003 retrieves CTX002 first and exposes shared and discordant response components. | Descriptive three-context demonstration; no prediction accuracy. |
| 4 | `fig11_context_similarity_matrix.png` | Technical Report or appendix; optional video transition | Pairwise mask-aware NES cosine across the three contexts. | n=3; pair-specific shared-tested masks; descriptive baseline. |

## Optional supporting figure

`fig06_prespecified_pathways.png` may be used once in the Technical Report to show how source-level GSEA evidence enters the response framework. It should not lead the competition story and must retain the transcriptome-not-phenotype limitation.

## Figures excluded from the primary story

Figures 01–05 and 07 remain valid provenance artifacts but are not part of the core competition sequence. Showing multiple single-study QC, DE, and evidence plots would obscure the implemented platform and overemphasize EXP001. They may be retained in a technical appendix or repository.

## Rights and provenance

All selected figures are generated from project analyses and tracked artifacts. No publication-owned figure is selected. Source artifacts, scripts, claims, and limitations are recorded in `submission/figures/FIGURE_MANIFEST.md`.
