# F1 Context schema

A context is an experimental EV perturbation environment, not a biological result. One row in `data/metadata/skinexo_contexts.csv` represents the specified recipient, EV source, treatment/control, time, and omics contrast. `context_id` is stable; `dataset_id` is a repository accession and is not assumed to identify a single contrast. The `role` field links to the project experiment.

| Field | Meaning |
| --- | --- |
| `context_id`, `dataset_id`, `study_id`, `role` | Identity and provenance |
| `study_status` | `VERIFIED`, `PLANNED`, or `EXCLUDED`; `PLANNED` means SkinExo analysis is planned, even if a source paper is published |
| `species` | Recipient species for this omics contrast |
| `recipient_cell`, `recipient_tissue`, `recipient_primary_or_cell_line`, `recipient_donor_count` | Recipient identity and independent-donor information |
| `ev_source_cell`, `ev_source_tissue`, `ev_type`, `ev_preparation_count` | EV source and preparation independence |
| `dose`, `duration_h`, `experimental_system` | Exposure and model |
| `omics_type`, `omics_platform` | Measured modality and platform |
| `treatment`, `control` | Exact comparison arms when verified |
| `sample_count`, `treatment_n`, `control_n`, `batch_count`, `statistical_design` | Contrast size, batches, and fitted design |
| `data_status` | `ANALYZED`, `AVAILABLE_NOT_ANALYZED`, `METADATA_ONLY`, or `UNAVAILABLE` |
| `phenotype_available`, `cargo_data_available` | Availability, not evidence of a causal link |
| `evidence_status` | `FROZEN_C4` or `UNKNOWN` at F1 |
| `major_limitations`, `source_provenance` | Explicit uncertainty and traceable sources |

`UNKNOWN` is required for unverified scalar/design values. A sample count must describe the selected contrast, not a whole GEO series. EXP003-D0 established 6 hDF libraries (3 EV, 3 control) for CTX003 within a 12-sample series that also contains 6 HaCaT libraries; the two recipients remain separate. A documented donor lot is not a donor-replication estimate. An EV source-cell lot is not an independent EV preparation. `source_provenance` uses semicolon-separated local paths and public URLs.

CTX001 and CTX002 were the verified analyzed contexts at F1. CTX003 entered F1 as planned and was promoted to `VERIFIED` / `ANALYZED` only after EXP003-C1 through C4 passed. The selected CTX003 contrast remains the six hDF libraries; the HaCaT libraries are outside CTX003. Its author-reported assays remain in the separate phenotype table. See [DEV-C1](../checkpoints/DEV_C1_MANIFEST.md), [EXP001-C1](../../reports/EXP001_C1_dataset_integrity.md), [EXP002-C1R](../../reports/EXP002_C1R_design_quantification_resolution.md), [EXP003-D0](../../reports/EXP003_D0_context_onboarding.md), and [EXP003-C4](../../reports/EXP003_C4_third_context_pathway_test.md).
