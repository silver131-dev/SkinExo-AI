# F1 phenotype anchor schema

`data/metadata/skinexo_phenotype_anchors.csv` stores measured or author-reported assays separately from transcriptomic response rows. An anchor may share a context and broad axis while differing in species, model, time, dose, and evidence layer. It does not automatically validate a GSEA term.

| Field | Meaning |
| --- | --- |
| `anchor_id`, `context_id`, `axis` | Unique anchor, associated study context, and broad question |
| `phenotype`, `assay` | What was measured and how |
| `species`, `recipient_or_model` | Actual assay species and experimental model, independently of context species |
| `treatment`, `dose`, `time` | Assay exposure, which may differ from omics exposure |
| `replicate_information` | Verified replicate description or `UNKNOWN` |
| `effect_direction`, `effect_summary`, `statistical_support` | Reported observation; `UNKNOWN` if precise direction or statistics were not verified |
| `evidence_level` | Controlled evidence layer: `FUNCTIONAL_ASSAY` or `IN_VIVO` here |
| `causal_status` | `ASSOCIATED`, `PREDICTED`, `FUNCTIONALLY_SUPPORTED`, or `CAUSALLY_VALIDATED` |
| `source`, `limitations` | Paper and local verification trail, plus limits |

`FUNCTIONALLY_SUPPORTED` means an EV-treated functional assay reported a corresponding readout. It does not establish which cargo molecule or transcriptomic pathway caused the result. `CAUSALLY_VALIDATED` requires a specific causal perturbation and rescue or equivalent direct evidence, and no F1 anchor receives it. `ASSOCIATED` is used where the endpoint is documented but its direction and statistics are not encoded. `PREDICTED` is reserved for modeled claims and is not assigned to these assays.

CTX003 hDF CCK-8 and scratch assays are human cell-culture anchors at 24 h. The CCK-8 signal is a viability/metabolic proxy; scratch closure can involve proliferation as well as motility. The planned hDF RNA-seq exposure is 72 h. Mouse closure, scar, and collagen rows are `Mus musculus` whole-wound `IN_VIVO` evidence and are not human fibroblast phenotype evidence or transcriptomic-axis validation. See the [Liu et al. primary record](https://pubmed.ncbi.nlm.nih.gov/40728022/) and [EXP003-D0 source log](../literature/EXP003_D0_SOURCE_LOG.md).
