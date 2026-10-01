# SkinExo-AI demo storyboard — maximum 5 minutes

**Draft only; no video has been created.** Use team-generated C2/C3/C4 figures and source credits. Keep cross-dataset validation and predictive AI as planned work.

| Time | Screen / narration | Evidence and guardrail |
|---|---|---|
| 0:00–0:30 | The problem: EV signals, multiple recipient cells, and the gap between a gene list and a repair outcome. | Use a team-created schematic; do not show external imagery without rights review. |
| 0:30–1:00 | Concept: EV source → cargo → recipient cell → molecular response → program → phenotype → evidence. | Say this is the **working framework**, with prediction still planned. |
| 1:00–1:40 | GSE293186: human dermal fibroblasts, 72 h, CTRL n=3 versus ECEV n=3; C1 data checks. | Cite GEO and the source paper. Show 58,735 rows and six samples without suggesting new data collection. |
| 1:40–2:20 | C2 [sample PCA](figures/fig01_transcriptomic_pca.png); optional small [robustness view](figures/fig02_pca_robustness.png). | PC1 86.59%, PC2 5.90%; call sample structure exploratory and avoid a causality claim. |
| 2:20–3:00 | C3 [volcano plot](figures/fig04_differential_expression_volcano.png); optional [MA plot](figures/fig03_ma_plot.png). | DESeq2, 16,271 tested; 2,032 at padj < 0.05 and |log2FC| ≥ 1. No phenotype assignment from a DEG alone. |
| 3:00–3:40 | C3.5 evidence framework: 16 records, four public datasets, explicit evidence classes and gaps. | Use a team-made evidence diagram. Explain A=0 direct and same-dataset circularity. |
| 3:40–4:30 | C4 [prespecified pathway figure](figures/fig06_prespecified_pathways.png) and [evidence map](figures/fig07_skinexo_evidence_map.png). | GSEA is primary, ORA secondary. Show ECEV-higher cell-cycle transcription without claiming proliferation. Note no angiogenesis-specific GSEA FDR < 0.05, direct A=0, and Q6 not yet testable. Cross-dataset validation and predictive AI remain TODO. |
| 4:30–5:00 | Limits and next experiment: n=3/group, one dataset, future skin-on-chip testing. | State clearly that skin-on-chip validation has **not** been performed. |

**Production TODO:** script wording, timing rehearsal, spoken source credits, accessibility captions, music/image rights, figure legibility, participant approval, and final video export.
