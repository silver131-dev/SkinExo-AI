# EXP003 — Frozen third-context validation endpoints

**Frozen before EXP003 differential expression, pathway analysis, and biological comparison.** CTX003 is a third experimental context: human dermal fibroblast-derived EV applied to human dermal fibroblasts for 72 h. Its results must be represented before they are compared with CTX001 or CTX002, and a null or discordant result must remain visible.

## Primary future question

Does CTX003 strengthen, refine, or contradict the context-aware interpretation derived from CTX001 and CTX002?

This is a component-aware question. A shared broad axis does not establish replication of a lower-level component, and different components within one axis are not interchangeable. Comparison must preserve EV source, recipient, species, dose, time, study, evidence layer, and reliability dimensions.

## Fixed CTX003 evidence construction

- Use the C2-frozen DESeq2 contrast `HDF_EV` versus `CONTROL`; positive Wald statistic and log2 fold change mean higher expression in hDF-EV-treated cells.
- Use the C2-frozen MSigDB 2026.1.Hs GO Biological Process, Reactome, and Hallmark resources, the existing P/M/E/A/I term map, and the existing component identities.
- Primary transcriptomic program evidence is GSEA ranked by the DESeq2 Wald statistic. ORA is secondary/supportive only.
- Preserve qualified, null, untestable, discordant, and sensitivity-dependent evidence. Do not add favorable pathways or change mappings after reviewing CTX003.
- Cross-context interpretation begins only after CTX003 C3 and C4 pass. C2 creates no CTX003 response state.

## Axis endpoints

### P — Proliferation / Cell-Cycle Regulation

Test whether the candidate `CONSERVED_COMPONENT` interpretation from CTX001 versus CTX002 persists in CTX003. The endpoint is exact mapped-component identity and direction. A different active P component may support broad P-axis activity but cannot make the entire axis universally conserved. Absence of qualified evidence remains null/not testable rather than failed phenotype validation.

### M — Migration / Motility

The frozen CTX001-versus-CTX002 state is `DISCORDANT`. Determine whether CTX003 supports a component and direction seen in either prior context, shows another context-dependent response, provides directly incompatible comparable evidence, or remains null/not testable. Do not force CTX003 to choose one prior study as correct.

### E — ECM Organization / Remodeling

The frozen CTX001-versus-CTX002 state is `NULL_NOT_TESTABLE`. Determine whether CTX003 supplies qualified component-level evidence where the earlier pair lacked a valid comparison, or whether E remains null/not testable. New CTX003 evidence does not retroactively convert the previous null into agreement.

### A — Vascular / Endothelial Interaction

The frozen CTX001-versus-CTX002 state is `DISCORDANT`. Determine whether CTX003 supports a comparable component/direction from either context, reinforces context dependence or discordance, or remains null/not testable. A broad vascular association is not direct evidence of angiogenesis.

### I — Inflammation / Immune Signaling

The frozen CTX001-versus-CTX002 state is `CONSERVED_AXIS`, with different active components and no shared active component. Determine whether CTX003 matches an exact active component from either context, shows broad I-axis overlap through a different component, provides discordant comparable evidence, or has no qualified evidence. Axis-level thematic overlap must not be labeled component-level replication.

## Comparison hierarchy

Apply the F1 comparison hierarchy without redefining it:

1. Same mapped component and same direction: candidate `CONSERVED_COMPONENT` evidence.
2. Same broad axis through different active components: candidate `CONSERVED_AXIS` evidence.
3. Meaningful contextual difference without direct opposition: `CONTEXT_DEPENDENT`.
4. Comparable incompatible or opposing evidence: `DISCORDANT`.
5. Absent, null, or insufficient comparable evidence: `NULL_NOT_TESTABLE`.
6. A conclusion that materially changes under a preregistered sensitivity analysis: `SENSITIVITY_DEPENDENT`.

Evidence from three analyzed contexts can strengthen a candidate interpretation but does not establish universal EV-response biology.

## Phenotype-anchor rule

- **P functional anchor:** hDF CCK-8 at 24 h.
- **M functional anchor:** hDF scratch assay at 24 h.
- **Transcriptome:** hDF RNA-seq at 72 h.

The assays use the same recipient and EV source but a different time point. They remain a separate `FUNCTIONAL_ASSAY` layer and may support plausibility only. ERK1/ERK2 qPCR is targeted molecular evidence and does not replace the preregistered P component analysis.

Mouse wound closure, scar length, and collagen deposition remain `IN_VIVO` evidence in a different species/model. Cytokine-array and cargo evidence remain separate layers. Predicted or observed cargo associations do not establish causal regulation.

## Reliability rule

Interpret every future CTX003 comparison with these fixed limitations: n = 3 per condition; donor identity and independence unknown; EV-preparation identity and independence unknown; pairing unknown; batch not documented; control medium/vehicle unknown; unexplained dominant PC1 sample structure. Agreement cannot be promoted to independent-donor or EV-preparation-level replication.

## Claim boundary

CTX003 may support a third context-specific transcriptomic observation. It cannot by itself justify therapeutic prediction, phenotype prediction, universal EV-response generalization, or causal cargo-response links. Negative, null, discordant, and uncertain findings are valid outcomes and must not trigger endpoint changes.
