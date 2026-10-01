# F1 reliability schema

Reliability is a vector of documented dimensions, not one arbitrary score. `data/metadata/skinexo_reliability.csv` stores one row per context and dimension: `reliability_id`, `context_id`, `dimension`, `status`, `detail`, and `source_provenance`. Status is `VERIFIED`, `LIMITED`, `UNKNOWN`, or `NOT_APPLICABLE`. No weighted sum or rank is defined at F1.

| Dimension | CTX001 at F1 | CTX002 at F1 | CTX003 at F1 |
| --- | --- | --- | --- |
| Study independence | Independent study versus CTX002 | Independent study versus CTX001 | Separate Liu study; no SkinExo analysis |
| Recipient-donor independence | UNKNOWN | LIMITED: one documented donor lot | UNKNOWN |
| EV-preparation independence | UNKNOWN | UNKNOWN | UNKNOWN |
| Batch adjustment | `~ condition`; batch metadata UNKNOWN | VERIFIED: `~ batch + condition`, two balanced batches | UNKNOWN |
| Sample QC | C1/C2 passed; 3+3 selected samples | C1R/C2R review completed; 8+8 primary, EV_8 retained | NOT_APPLICABLE before C1 integrity/QC |
| Sensitivity stability | NOT_APPLICABLE in F1 cross-study sensitivity | Five C4 axis outcomes stable after EV_8 exclusion; C3 effect-tail warning persists | UNKNOWN |
| Annotation certainty | Frozen MSigDB 2026.1.Hs and term map; overlap-dependent components | Same term map; transcript harmonization has documented limits | UNKNOWN |
| Phenotype support | Primary study reports assays; no F1 anchor imported | UNKNOWN at F1 | Author-reported hDF and mouse assays, separate from RNA-seq |
| Cross-context replication | P shared candidate component; I thematic axis only; M/A discordant; E untestable | Same comparison, with single-donor limitation | UNKNOWN |

Evidence for the first two columns is in the frozen [EXP001-C4](../../reports/EXP001_C4_pathway_analysis.md), [EXP002-C1R](../../reports/EXP002_C1R_design_quantification_resolution.md), [EXP002-C3](../../reports/EXP002_C3_differential_expression.md), and [EXP002-C4](../../reports/EXP002_C4_cross_study_pathway_validation.md) reports. CTX003 phenotype provenance is the [Liu primary study](https://pubmed.ncbi.nlm.nih.gov/40728022/) and [EXP003-D0 source log](../literature/EXP003_D0_SOURCE_LOG.md).

For machine-readable F1 use, the original nine dimensions are in `skinexo_reliability.csv`; design fields are in `skinexo_contexts.csv`; sensitivity and annotation detail is in response/component rows; cross-context limits and outcome stability are in comparison rows; direct assay support is in anchors. Future releases must not infer unknown preparation/donor counts or collapse these dimensions into a score.

## Post EXP003-C4 extension

EXP003-C4 adds `pairing_certainty`, `control_certainty`, `model_diagnostics`, and `pathway_evidence` as explicit dimensions for all contexts so the registry remains rectangular. CTX003 records its independent study provenance and passing integrity/model diagnostics while retaining `UNKNOWN` donor independence, EV preparation independence, pairing, batch certainty, and control certainty. Its dominant unexplained PC1 structure remains in `sample_qc` and `model_diagnostics`; successful DESeq2/GSEA execution does not erase that limitation. No combined reliability score is computed.
