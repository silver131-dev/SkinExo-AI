# SkinExo-AI Response Atlas schema — F2

**Atlas version:** `F2-2026-10-01`  
**Framework version:** `F2`  
**Scope:** three verified, study-independent human dermal-fibroblast recipient contexts.

An Atlas record represents one frozen response component in one experimental context. It preserves context, axis, component identity, direction, an auditable GSEA effect estimate where tested, statistical evidence, evidence layer, linked phenotype-anchor IDs, separate reliability references, checkpoint provenance, and explicit missingness.

## Tables

| Table | Grain | Purpose |
| --- | --- | --- |
| `skinexo_component_universe.csv` | One row per stable component | Versioned 339-component vocabulary and source terms |
| `skinexo_context_features.csv` | One row per context | EV source, recipient, design, availability, and limitations |
| `skinexo_response_atlas_long.csv` | One row per context-component | Normalized retrieval-ready evidence with masks |
| `skinexo_response_matrix.csv` | One row per context; one JSON cell per component | Wide transport representation that retains state and statistics |
| `skinexo_axis_summary.csv` | One row per context-axis | Descriptive summaries; never a replacement for component records |

The component universe is frozen at `F2-2026-10-01`. Future contexts may map to it. A later discovery that requires a new or revised component must create a new vocabulary version; it must not silently change F2. For a component containing multiple frozen terms, the `source_database`, `source_term_id`, and `source_term_name` fields contain semicolon-separated aligned provenance rather than a merged biological label.

## Activity-state vocabulary

| State | Meaning | `tested_mask` | `active_mask` |
| --- | --- | ---: | ---: |
| `ACTIVE_POSITIVE` | At least one frozen mapped term qualifies and the component direction is positive | 1 | 1 |
| `ACTIVE_NEGATIVE` | At least one frozen mapped term qualifies and the component direction is negative | 1 | 1 |
| `OBSERVED_NULL` | The component has a valid tested term but no mapped term meets the frozen qualification rule | 1 | 0 |
| `NOT_TESTED` | No mapped term has an eligible numeric test in that context | 0 | 0 |
| `UNKNOWN` | The context or component evidence has not been analyzed or cannot be resolved | 0 | 0 |

`OBSERVED_NULL`, `NOT_TESTED`, and `UNKNOWN` are never interchangeable. The wide matrix stores each cell as compact JSON containing `activity_state`, `direction`, `NES`, `FDR`, `tested_mask`, and `active_mask`; missing numbers are JSON `null`, not numeric zero.

## Component-level statistic

For an active component, the representative term is the qualified mapped term with lowest FDR, then greatest absolute NES, then lexical term ID. For an observed-null component, the same deterministic rule is applied across valid tested mapped terms. `NES` and `FDR` describe that representative term; they do not imply that all terms in a multi-term component have identical effects. Untested and unknown records have blank numeric fields.

## Evidence layers and links

Transcriptomic component records use `TRANSCRIPTOME`. Phenotype anchors remain separate rows and are linked by `anchor_id` at the context-axis level; the link is not a component-specific causal claim. A linked assay never changes NES, FDR, or activity state. Reliability remains a vector of referenced rows rather than a scalar confidence score. `source_checkpoint` and `provenance` trace every record to a frozen C4 result.

## Frozen three-context interpretation

- P: `TWO_CONTEXT_SHARED_COMPONENT`; P081 is shared by CTX001/CTX002 and null in CTX003.
- M: `CONTEXT_DEPENDENT_DISCORDANT`.
- E: `NULL_NOT_TESTABLE`.
- A: `CONTEXT_DEPENDENT_DISCORDANT`.
- I: `CONSERVED_AXIS_CONTEXT_VARIANT`; CTX002/CTX003 share exact components, while CTX001 overlaps only at broad axis direction.

The broad universal EV response is `NOT_SUPPORTED`.
