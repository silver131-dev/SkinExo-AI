# F1 Response and component schemas

One row in `data/metadata/skinexo_responses.csv` is one axis within one context. Axes are `P` proliferation/cell-cycle regulation, `M` migration/motility, `E` ECM organization/remodeling, `A` vascular/endothelial interaction, and `I` inflammation/immune signaling. These are transcriptomic term families in F1, not measured phenotypes.

| Field | Meaning |
| --- | --- |
| `response_id`, `context_id`, `axis` | Unique response and parent context |
| `direction` | Dominant qualified-component NES sign, `NO_QUALIFIED_COMPONENT`, or `UNKNOWN`; `_DOMINANT_WITH_OPPOSING_COMPONENTS` retains mixed evidence |
| `evidence_status` | Within-context `QUALIFIED`, `OBSERVED_NULL`, or `UNKNOWN` |
| `evidence_layer`, `primary_evidence_type` | `TRANSCRIPTOME` and `GSEA_PRERANK` for analyzed C4 rows |
| `representative_term_id`, `NES`, `FDR` | One auditable qualified term, chosen by lowest FDR then greatest absolute NES; blank numeric fields when none |
| `key_terms` | Semicolon-separated **all qualified** term IDs in the common eligible C4 comparison; not a new term selection |
| `component_ids` | Semicolon-separated active C4 component IDs; all eligible/inactive IDs remain in the component table |
| `leading_edge_genes` | Semicolon-separated union of stable gene IDs across the qualified `key_terms` |
| `sensitivity_status`, `phenotype_anchor_status`, `evidence_confidence` | Descriptive status, never a scalar score |
| `limitations`, `source_checkpoint` | Interpretation limits and frozen source |

The C4 qualified-term rule was fixed before EXP002: GSEA FDR < 0.05, at least five leading-edge genes, and at least 80% Wald-sign coherence. `NES` and `FDR` belong only to `representative_term_id`; they do not summarize the whole axis. Stored numeric `0.0` FDR is a finite permutation estimate, not exact zero probability. Positive NES associates a term with EV-higher genes; negative NES associates it with EV-lower genes. Neither sign asserts phenotype direction.

`data/metadata/skinexo_response_components.csv` contains the same frozen 339-component vocabulary for every analyzed context, including inactive components. `component_id` is the original C4 overlap-cluster ID within its axis; `component_entry_id` is unique per context. `mapped_term_ids` preserves all terms in that source-membership component. `qualified_term_ids`, `direction`, and `evidence_status` report each frozen primary fit. `term_evidence_json` carries per-term NES, FDR, leading-edge size and qualification, including null or ineligible terms. CTX002 additionally retains `sensitivity_direction` and `sensitivity_qualified_term_ids` from the EV_8-excluded fit. CTX003 rows were added only after EXP003-C4 and use the pre-existing component definitions. Source Jaccard threshold was 0.50; related terms in a component are not independent confirmations.

Within-context `QUALIFIED`/`OBSERVED_NULL`/`UNKNOWN` is distinct from the cross-context controlled vocabulary in [Evidence states](EVIDENCE_STATE_SCHEMA.md). A response may be locally qualified while a cross-context comparison is discordant. EXP001/EXP002 source audits remain in `outputs/exp002/c4_components_exp001_vs_primary.csv` and its sensitivity counterpart; CTX003 term evidence is traceable to `outputs/exp003/c4_gsea_all.csv` and `outputs/exp003/c4_ctx003_components.csv`.
