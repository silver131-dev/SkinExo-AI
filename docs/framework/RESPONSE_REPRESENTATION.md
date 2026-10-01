# F2 retrieval-ready response representation

**Status:** representation ready and consumed by the implemented RETRIEVAL-R1 baseline. PCA retrieval and prediction are not implemented.

## Feature unit

The primary unit is a stable F2 response component. Each context-component record supplies a representative GSEA NES where a valid mapped term was tested. Component IDs, axes, direction, FDR, activity state, evidence layer, phenotype links, reliability references, and provenance remain attached.

For multi-term components, F2 deterministically selects the qualified term with lowest FDR, then greatest absolute NES, then lexical term ID. If the component is observed null, selection uses all valid tested terms. This rule provides one auditable component value without merging distinct components or treating overlapping terms as independent confirmation.

## Numeric value and masks

For a tested component:

```text
response_value = representative GSEA NES
tested_mask = 1
active_mask = 1 when ACTIVE_POSITIVE or ACTIVE_NEGATIVE, otherwise 0
```

For `NOT_TESTED` or `UNKNOWN`:

```text
response_value = missing
tested_mask = 0
active_mask = 0
```

Missing values must not be silently imputed as zero. `OBSERVED_NULL` retains its observed NES and FDR with `tested_mask = 1` and `active_mask = 0`. This separates evidence of nonqualification from unavailable evidence.

## RETRIEVAL-R1 use

R1 operates only over mutually tested stable components and reports the number and identity of comparable components. It uses raw representative NES, requires at least two components for primary and axis cosine, and returns an explicit undefined state for insufficient overlap. Reliability dimensions and phenotype anchors remain visible alongside similarity and are not folded into the numeric similarity value.

Axis summaries are display aids. Phenotype IDs are contextual axis links and do not assert that every linked component causes or measures the phenotype. Retrieval must retain component identity so P081 two-context support, M/A discordance, and I axis-level context variation cannot be collapsed into generic axis scores.
