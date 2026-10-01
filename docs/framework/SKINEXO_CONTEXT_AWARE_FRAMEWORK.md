# SkinExo-AI Context-Aware EV Response Framework — F1

**Source freeze:** DEV-C1, `dc3d813b2e0d9c2b6dbc6a098f646d315cd901b9`. **Scientific question:** Given an EV source and biological context, which recipient-cell programs recur at the same component, recur only at an axis, depend on context, oppose one another, or remain null, untestable, sensitivity dependent, or unknown?

## Evidence model

`Context → Response axis → mapped Component → directional term evidence → Evidence layer → Reliability dimensions → Cross-context state`.

Contexts contain design metadata. Responses contain one axis per context. Components retain the C4 source-membership clusters and all eligible mapped terms, including inactive ones. [Cross-context states](EVIDENCE_STATE_SCHEMA.md) describe two-context evidence and never overwrite frozen C4 labels. The normalized tables are in `data/metadata/`; [schemas](CONTEXT_SCHEMA.md), [responses](RESPONSE_SCHEMA.md), [anchors](PHENOTYPE_ANCHOR_SCHEMA.md), [comparison rules](CONTEXT_COMPARISON_SCHEMA.md), and [reliability](RELIABILITY_SCHEMA.md) define their interpretation.

Evidence layers are `TRANSCRIPTOME`, `FUNCTIONAL_ASSAY`, `IN_VIVO`, `CARGO`, `LITERATURE`, and `SENSITIVITY`. They are complementary, not automatically equivalent. A pathway association is not a demonstrated phenotype; an author-reported phenotype is not an F1 transcriptomic state; a predicted miRNA target is not causal regulation. The frozen EV_8 exclusion is a sensitivity layer, not a replacement primary fit. `GSE293957` is registered as `CARGO`, `AVAILABLE_NOT_ANALYZED`, hDF-EV miRNA profiling by Affymetrix miRNA-4 array, and a future EXP006 candidate. No cargo-response causal link is encoded.

## Worked example: one shared P component

1. **Context:** CTX001 is GSE293186, endothelial EV versus control in primary human dermal fibroblasts after 72 h. CTX002 is GSE251807, bone-marrow MSC small EV versus DMEM in primary human dermal fibroblasts after 48 h; CTX002 has one documented recipient donor lot and unknown EV-preparation independence.
2. **Axis/component:** P is proliferation/cell-cycle regulation. Frozen C4 component **P081** groups three related Reactome APC/C and mitotic-entry terms by source gene-set membership overlap. It is active positive in both contexts; the qualified term sets differ.
3. **Direction/evidence:** In CTX001, `REACTOME_ACTIVATION_OF_APC_C_AND_APC_C_CDC20_MEDIATED_DEGRADATION_OF_MITOTIC_PROTEINS` has NES **+2.284698120223465**, FDR **9.01824938830592e-06**. In CTX002 primary, `REACTOME_FBXL7_DOWN_REGULATES_AURKA_DURING_MITOTIC_ENTRY_AND_IN_EARLY_MITOSIS` has NES **+1.9257618928580629**, FDR **0.016904712921542**. Both are frozen `TRANSCRIPTOME` GSEA results from the P081 component, not proliferation assay readouts. P081 remains positive in the EV_8-excluded sensitivity fit.
4. **Reliability:** The studies are independent, but EV sources and exposure times differ; CTX002 does not replicate recipient donors, and independent EV preparations are unknown. Related terms within P081 are not separate independent confirmations. Other P components include opposing evidence.
5. **Cross-context state:** `CONSERVED_COMPONENT` is a **candidate two-context component-level finding**. Frozen EXP002-C4 still labels the full P axis `PARTIALLY_CONCORDANT`. F1 does not call the entire P axis universally conserved or infer increased proliferation from NES.

For contrast, I is `CONSERVED_AXIS` only: both studies have positive dominant inflammatory/immune directions but **zero shared active I components**. M and A are `DISCORDANT`; E is `NULL_NOT_TESTABLE` because common eligible ECM terms exist yet EXP002 has no qualified E component. The [C4 report](../../reports/EXP002_C4_cross_study_pathway_validation.md) remains the numerical source.

## Platform architecture

```text
DATA SOURCES                    IMPLEMENTED: frozen EXP001/EXP002; CTX003 metadata
  ↓
CONTEXT NORMALIZATION           IMPLEMENTED: F1 context/phenotype/cargo registry
  ↓
REPRODUCIBLE ANALYSIS           IMPLEMENTED: frozen EXP001/EXP002 C1–C4 only
  ↓
RESPONSE OBJECTS                IMPLEMENTED: F1 axis and component tables
  ↓
COMPONENT-AWARE COMPARISON      IMPLEMENTED: CTX001 versus CTX002 table
  ↓
EVIDENCE / RELIABILITY          IMPLEMENTED: F1 vocabulary and separate dimensions
  ↓
RESPONSE REPRESENTATION         PLANNED: standardized retrieval vector
  ↓
RETRIEVAL                       PLANNED
  ↓
EXPLORER / DEMO                 PLANNED
```

The planned [retrieval contract](RETRIEVAL_CONTRACT.md) specifies source/recipient/species/dose/time/response-vector input and nearest-context/evidence/reliability output. No retrieval, Explorer, or predictive AI is implemented at F1.

## Boundaries

Broad five-axis EXP001-versus-EXP002 concordance was **not supported**. F1 preserves the mixed result and negative evidence. CTX003 has study-design metadata and separate author-reported phenotype anchors only. Its P/M/E/A/I transcriptomic states remain `UNKNOWN` pending EXP003. No GSE293956/GSE293957 files were downloaded or analyzed for F1, and no molecular cargo mechanism is inferred.

## F2 status transition

The text above is the preserved F1 checkpoint description. After EXP003-C1 through C4 passed with documented limitations, F2 promoted CTX003 to a verified analyzed context and transformed all three frozen C4 results into Atlas version `F2-2026-10-01`. The [Atlas schema](ATLAS_SCHEMA.md) and [response representation](RESPONSE_REPRESENTATION.md) define the stable 339-component universe, explicit null/missingness states, context features, phenotype links, and reliability references.

F2 implements the pipeline through Response Atlas, component-aware evidence, and reliability. Retrieval and Explorer remain next-stage work; predictive AI remains unimplemented. The F1 manifest, report, and original pairwise interpretation remain provenance and are not rewritten as F2 results.

## R1 status transition

RETRIEVAL-R1 implements the first retrieval baseline over the unchanged F2 Atlas. It uses mask-aware cosine on mutually tested component NES, with secondary active-union cosine, directional concordance, and axis-aware summaries. Ordered explanations attach component differences, phenotype anchors, reliability dimensions, and provenance without incorporating phenotype or reliability into similarity.

```text
PUBLIC EV STUDIES              IMPLEMENTED
  ↓
CONTEXT NORMALIZATION          IMPLEMENTED
  ↓
REPRODUCIBLE ANALYSIS          IMPLEMENTED
  ↓
RESPONSE ATLAS                 IMPLEMENTED — F2
  ↓
COMPONENT EVIDENCE/RELIABILITY IMPLEMENTED
  ↓
RETRIEVAL                      IMPLEMENTED — R1 baseline
  ↓
EXPLORER                       PLANNED
```

R1 has no fitted parameters and makes no predictive claim. Predictive AI is **NOT IMPLEMENTED**. See the [R1 specification](RETRIEVAL_R1_SPEC.md) and [R1 report](../../reports/RETRIEVAL_R1_interpretable_context_similarity.md).

## A1 status transition

EXPLORER-A1 implements the local judge-facing Streamlit interface over F2 and R1. It provides context selection, experimental metadata, P/M/E/A/I summaries, component evidence, runtime retrieval, deterministic WHY explanations, axis comparisons, separate phenotype and reliability panels, and expandable provenance. Normal operation uses only trackable repository artifacts and requires no raw data, licensed PDF, institutional access, or internet connection.

Current platform status:

- Response Atlas: **IMPLEMENTED — F2**
- Retrieval: **IMPLEMENTED — R1**
- Explorer: **IMPLEMENTED — A1**
- Predictive AI: **NOT IMPLEMENTED**
- Agent: **NOT IMPLEMENTED**

Launch locally with `streamlit run app/streamlit_app.py`. A1 remains a descriptive competition demonstration over three observed contexts.
