# SkinExo-AI: A Context-Aware Extracellular-Vesicle Response Platform

SkinExo-AI transforms isolated extracellular-vesicle studies into a context-aware response atlas that retrieves and explains conserved, context-dependent, discordant, and uncertain cellular responses.

## Abstract

**SkinExo-AI: A Context-Aware Extracellular-Vesicle Response Platform** converts isolated extracellular-vesicle (EV) transcriptomic studies into a structured, comparable, and explainable response representation. We analyzed three study-level independent human dermal fibroblast contexts that differ in EV source, dose, duration, and design. A broad universal EV transcriptomic response was **not supported**. SkinExo-AI therefore preserves response evidence at the component level, distinguishes observed nulls from missing evidence, and keeps phenotype anchors and reliability dimensions separate from transcriptomic similarity. The implemented v0.3 system contains a reproducible evidence engine, context normalization, an F2 Response Atlas with 3 contexts, 339 components, and 1,017 context-component records, an R1 mask-aware retrieval baseline with deterministic WHY explanations, and an offline Streamlit Explorer. The system supports cross-study interpretation and research prioritization; it is not a trained predictive model and does not establish therapeutic efficacy.

![SkinExo-AI platform architecture](figures/fig09_skinexo_platform_architecture.png)

## 1. Problem

EV studies are commonly analyzed one at a time. Yet an observed response depends on the EV source, recipient cell, species, dose, duration, experimental system, assay, and statistical design. Pathway labels add another ambiguity: two studies can activate the same broad biological axis through different components, while a missing or null result can be incorrectly treated as evidence of similarity.

SkinExo-AI addresses this comparison problem. Its canonical question is: given an EV source and biological context, which recipient-cell response programs are conserved at the component level, conserved only at a broader axis level, context-dependent, discordant, null/not testable, or sensitivity-dependent?

## 2. Design Principles

The platform follows six rules:

1. **Context precedes comparison.** EV source, recipient, dose, time, species, study, and evidence layer remain attached to every response.
2. **Components remain identifiable.** Components within P/M/E/A/I are not interchangeable simply because they share an axis.
3. **Missingness is explicit.** `OBSERVED_NULL`, `NOT_TESTED`, and `UNKNOWN` have different meanings.
4. **Evidence layers remain separate.** A transcriptomic pathway is not a demonstrated phenotype, and a cargo target is not causal regulation.
5. **Similarity and reliability remain separate.** Retrieval does not hide design limitations inside one confidence score.
6. **Negative results are retained.** The framework can reject or narrow a provisional cross-context hypothesis.

## 3. Data and Contexts

All contexts use public study data and have human dermal fibroblast recipients. They are independent at the **study level**; donor and EV-preparation independence are incomplete or unknown.

| Context | Public dataset | EV source → recipient | Duration | Analysis samples |
|---|---|---|---:|---:|
| CTX001 | GSE293186 | Endothelial-cell-derived EV → primary human dermal fibroblast | 72 h | 3 EV, 3 control |
| CTX002 | GSE251807 | Human bone-marrow MSC small EV → primary normal human dermal fibroblast | 48 h | 8 EV, 8 control |
| CTX003 | GSE293956 | Human dermal fibroblast-derived EV → primary human dermal fibroblast | 72 h | 3 EV, 3 control |

CTX003 used 10 µg/mL EV protein according to the primary study; the numeric dose was not encoded in GEO metadata. CTX003 control medium/vehicle, recipient donor mapping, pairing, and EV-preparation mapping remain unknown. These uncertainties are preserved rather than resolved by inference.

## 4. Reproducible Evidence Engine

Study-specific checkpoints verified public metadata, sample mapping, count integrity, unsupervised sample quality, and statistical design before biological interpretation. DE designs and filters were frozen prospectively. Count-based differential expression used DESeq2, followed by ranked GSEA using the DESeq2 Wald statistic and a fixed MSigDB 2026.1.Hs release spanning GO Biological Process, Reactome, and Hallmark. ORA, where used, was secondary.

EXP001 established internal analytical reproducibility against an author result after the SkinExo analysis was saved. EXP002 added an independent study context, explicit batch handling, and a prespecified sensitivity analysis. EXP003 was onboarded, quality checked, and analyzed under a frozen design before testing the third-context questions. The complete checkpoint reports and machine-readable results remain the source of detailed numerical evidence.

## 5. Context-Aware Response Framework

Each response links:

```text
Context → Axis → Component → Direction → Evidence layer
        → Reliability dimensions → Cross-context state → Provenance
```

The five axes are P (proliferation/cell cycle), M (migration/motility), E (ECM organization/remodeling), A (vascular/endothelial interaction), and I (inflammation/immune signaling). Axis summaries support navigation, while the component records carry the comparison evidence.

This distinction matters. “Same inflammatory axis” does not mean “same inflammatory component.” Collapsing both into a positive I label would erase the biological structure observed across contexts.

## 6. Three-Context Response Atlas

Atlas F2-2026-10-01 freezes a universe of **339 response components** across the five axes. Three contexts produce **1,017 context-component records**:

| Activity state | Records | Meaning |
|---|---:|---|
| `ACTIVE_POSITIVE` | 139 | Tested component met the frozen activity rule with positive direction |
| `ACTIVE_NEGATIVE` | 19 | Tested component met the frozen activity rule with negative direction |
| `OBSERVED_NULL` | 852 | Tested, but did not qualify as active |
| `NOT_TESTED` | 7 | No comparable test exists for that context-component record |
| `UNKNOWN` | 0 | State cannot yet be resolved |

Observed null is evidence that a component was tested without qualifying activity. It is not the same as missing evidence. This distinction is retained in both the long-form Atlas and the retrieval masks.

![Three-context Response Atlas](figures/fig08_context_aware_response_atlas.png)

## 7. Scientific Findings

The headline result is that a broad universal EV transcriptomic response is **not supported** across the three contexts.

### P

CTX001 and CTX002 share P081, an APC/C-related mitotic protein degradation component, in the same active direction. This supported a provisional two-context conserved-component hypothesis. CTX003 returned `OBSERVED_NULL` across the frozen P mapping. P081 is therefore `TWO_CONTEXT_SHARED_COMPONENT`, not a three-context or universal response.

This is an important validation outcome: the prospective third context did not confirm the provisional P hypothesis, and the representation retained that non-generalization.

### M

Migration/motility is `CONTEXT_DEPENDENT_DISCORDANT`. CTX001 contains negative mapped M activity, CTX002 has a different response structure, and CTX003 adds qualified positive components. The 24-hour CTX003 scratch assay is a separate phenotype anchor and cannot change the 72-hour transcriptomic state.

### E

ECM organization/remodeling remains `NULL_NOT_TESTABLE` in the three-context interpretation. CTX003 is observed null across the frozen E mapping. Mouse scar length and collagen deposition are different-model in-vivo anchors and do not establish a human fibroblast ECM transcriptomic response or scar benefit.

### A

Vascular/endothelial interaction is `CONTEXT_DEPENDENT_DISCORDANT`. CTX003 contains a qualified positive A component, while the cross-context structures remain discordant. This is transcriptomic annotation evidence. It does not demonstrate angiogenesis, neovascularization, or therapeutic vascular benefit.

### I

Inflammation/immune signaling is `CONSERVED_AXIS_CONTEXT_VARIANT`. CTX002 and CTX003 share nine exact active inflammatory components in the same direction, including interferon, interleukin, inflammatory-response, and TNF/NF-κB-related sets. CTX001 has broader positive inflammatory-axis evidence through a different component structure, plus one negative component.

Thus, the I result is conserved at the broad axis level with context variation. It is not exact component conservation across all three contexts. This **same axis ≠ same component** distinction is a central contribution of SkinExo-AI.

## 8. Response Representation

The quantitative feature for a tested component is its GSEA normalized enrichment score (NES). Two masks accompany it:

- `tested_mask` distinguishes measured evidence from `NOT_TESTED` and `UNKNOWN`;
- `active_mask` distinguishes qualifying active responses from tested observed-null responses.

Missing or untested components are never silently imputed as biological zero. Observed-null records retain their NES and state, allowing the primary comparison to use tested evidence while active-response comparisons focus on the union of qualifying components.

Global pathway correlations are secondary descriptions: Pearson/Spearman are −0.0773/−0.1318 for CTX001–CTX002, −0.1692/−0.1767 for CTX001–CTX003, and +0.1878/+0.1945 for CTX002–CTX003. These correlations do not measure prediction performance.

## 9. Interpretable Retrieval

R1 retrieves known contexts using **mask-aware NES cosine** over components tested in both contexts. A secondary active-union cosine restricts the comparison to components active in either context, provided they were tested in both. Directional concordance excludes jointly null components.

| Pair | Primary response similarity | Active-union cosine | Shared active | Directional concordance |
|---|---:|---:|---:|---:|
| CTX001–CTX002 | −0.1749 | +0.0108 | 2 | 0.500 |
| CTX001–CTX003 | −0.2755 | −0.2302 | 3 | 0.000 |
| CTX002–CTX003 | +0.6053 | +0.8563 | 9 | 1.000 |

For every ordered query-target pair, the WHY engine reports shared positive and negative components, discordant components, query-only and target-only active components, observed-null differences, and axis-specific comparisons. Explanations follow deterministic ranking rules rather than manually selected examples. Phenotype anchors and reliability dimensions are attached after retrieval and do not alter similarity.

![CTX003 context retrieval](figures/fig10_context_retrieval.png)

![Three-context response similarity](figures/fig11_context_similarity_matrix.png)

These results demonstrate retrieval behavior among three observed contexts. They are not accuracy, AUC, a train/test evaluation, or evidence of predictive generalization.

## 10. Interactive Explorer

Explorer A2 is implemented in Streamlit 1.64.0. Its Demo Mode follows **Context → Response → Retrieve → Explain → Evidence**, with dimension-level reliability and uncertainty visible alongside the results. A user can select a context, inspect its experimental metadata and P/M/E/A/I profile, explore response components, retrieve other **observed** contexts, open deterministic WHY explanations, and inspect phenotype, reliability, and provenance separately. Research Mode retains the detailed A1 interface.

The default query is CTX003. The engine computes CTX002 as rank 1 at +0.6053 and CTX001 as rank 2 at −0.2755. The order is not hard-coded in the interface. This is retrieval over observed study contexts, **not prediction for unseen contexts**. The Explorer runs offline from tracked derived artifacts and requires no raw GEO data, licensed publication PDF, institutional network, or internet connection at runtime. The [Final Demo Video](https://youtu.be/optVRKKDNec) shows the real Explorer product section.

## 11. Phenotype Evidence

Phenotype anchors are a separate evidence layer. For CTX003:

- P: human dermal fibroblast CCK-8 readout at 24 h;
- M: human dermal fibroblast scratch assay at 24 h;
- transcriptome: RNA-seq at 72 h;
- other anchors: mouse wound closure, scar length, and collagen deposition in a different in-vivo model.

The cell-culture anchors share the EV source and recipient with CTX003 but differ in time. Scratch closure can reflect both motility and proliferation. Mouse outcomes are not direct human fibroblast transcriptomic validation. No phenotype value is merged into NES or retrieval similarity.

## 12. Reliability and Provenance

The Atlas records reliability dimension by dimension: study independence, recipient-donor independence, EV-preparation independence, sample QC, batch certainty, pairing certainty, control certainty, model diagnostics, sensitivity evidence, phenotype support, annotation certainty, pathway evidence, and cross-context replication. It does not create an opaque aggregate confidence score.

Key limitations include n=3 per condition in CTX001 and CTX003; one documented recipient donor lot in CTX002; unknown donor structure in CTX001 and CTX003; incomplete or unknown EV-preparation independence; pairing and batch uncertainty where applicable; CTX003 control-definition uncertainty; and unexplained dominant replicate-label-associated PC1 structure in CTX003. These limitations remain visible even when model diagnostics or pathway evidence pass.

Each context, response, phenotype anchor, reliability record, retrieval result, and figure links to a checkpoint or source artifact. Public accessions identify the external biological data; third-party resources retain their original terms.

## 13. Validation

Validation occurs at several levels:

- **EXP001:** count integrity, unsupervised QC, frozen DE/GSEA, and internal analytical concordance.
- **EXP002:** independent-study comparison, batch-aware primary model, EV_8 technical review, and prespecified sensitivity analysis.
- **EXP003:** metadata onboarding, structural count-matrix validation, prospectively frozen QC/design, DE diagnostics, and a third-context pathway test.
- **Framework:** F1 schema validation and F2 Atlas validation, including component references and null/missing distinctions.
- **Retrieval:** seven synthetic sanity tests covering identity, sign reversal, insufficient overlap, jointly null states, `NOT_TESTED`, `UNKNOWN`, and deterministic explanations.
- **Explorer:** 22/22 retrieval and Explorer tests, three-context and 339-component closure, default ranking verification, and local server health.

The strongest scientific validation is falsification: CTX003 did not extend the two-context P component, and the framework recorded `OBSERVED_NULL` rather than redefining the axis or threshold.

## 14. Reproducibility

The repository includes frozen analysis plans, study metadata, source and release hashes, analysis scripts, complete derived tables, framework schemas, tests, reports, and project-generated figures. MSigDB is fixed at 2026.1.Hs for the Atlas analyses. Git checkpoints preserve development provenance.

The clean-root `public-v1` branch is published at https://github.com/silver131-dev/SkinExo-AI; its root commit is `1e768499c86d52245058059568e4b7a48cf6faa4`. Original SkinExo-AI source code is MIT licensed in that public snapshot. GEO/NCBI data, MSigDB, GENCODE, publications, third-party software, and other external resources retain their own licenses and terms. The public snapshot excludes raw omics, processed biological input matrices, licensed PDFs, credentials, private registration data, and institutional-only material.

## 15. Limitations

- Only three verified contexts are represented.
- Study-level independence does not establish donor-level or EV-preparation-level replication.
- Sample sizes and metadata completeness differ among contexts.
- CTX003’s dominant PC1 structure is unexplained and limits biological interpretation.
- Axis and pathway terms are transcriptomic associations, not causal mechanisms or phenotypes.
- Phenotype anchors differ in time or model.
- GSEA component mappings depend on a fixed database release and frozen mapping rules.
- Retrieval is descriptive and has no conventional predictive validation.
- No cargo-response causality, therapeutic efficacy, angiogenesis, or human wound-healing effect is established.

## 16. Competition Impact

SkinExo-AI addresses EV research fragmentation by making context, disagreement, negative evidence, reliability, and provenance queryable in one system. Researchers can identify which observed context is closest, inspect why, locate discordant or context-specific components, and judge the evidence limits before choosing follow-up experiments. The impact is improved cross-study comparability, evidence traceability, and research prioritization. Clinical impact has not been demonstrated.

## 17. Future Work

The maturity boundary is explicit:

- **TODAY — IMPLEMENTED:** observed Response Atlas, observed-context retrieval, component-level explanation, phenotype evidence, dimension-level reliability, and provenance in Explorer A2.
- **NEXT — FUTURE / NOT CURRENTLY IMPLEMENTED:** evidence-guided EV candidate screening to prioritize experimentally profiled candidates for laboratory validation; this is not efficacy prediction.
- **FUTURE — NOT YET IMPLEMENTED:** response prediction for unseen contexts, conditional on Atlas expansion, predictive modeling, and prospective validation.
- **LONG-TERM VISION — NOT IMPLEMENTED:** a conceptual Skin–EV Response Digital Twin for research prioritization, not a clinical, patient-specific, treatment-prescribing, or validated predictive system.

Supporting future research directions include:

- analyze the GSE293957 cargo companion under a separate checkpoint;
- evaluate cargo → response → phenotype hypotheses without assuming causality;
- add versioned EV contexts without silently changing the F2 component universe;
- perform prospective experimental validation;
- connect selected hypotheses to Organ-on-Chip or other tissue-level systems; and
- evaluate predictive modeling only after the context base and prospective validation are sufficient.

SkinExo-AI v0.3 does not assume a universal EV response. It retrieves and explains context-dependent response patterns while keeping evidence, missingness, phenotype anchors, reliability, and provenance visible.
