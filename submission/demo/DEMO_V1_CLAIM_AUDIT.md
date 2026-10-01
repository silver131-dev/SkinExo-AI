# SkinExo-AI DEMO-V1 narration claim audit

Every narration sentence is mapped below in spoken order. Status terms follow `submission/S2_CLAIM_DICTIONARY.md`. No sentence is classified outside the controlled vocabulary.

## Scene 1

| ID | Narration sentence | Status | Evidence / boundary |
|---|---|---|---|
| N01 | Extracellular vesicles carry biological signals between cells, but their effects are usually studied one experiment at a time. | SUPPORTED | S2 problem statement and study-isolation framing; no efficacy claim. |
| N02 | EV source, recipient cell, dose, duration, and study design can all differ. | SUPPORTED | Context schema and F2 context features. |
| N03 | That makes response evidence difficult to compare without losing the context that produced it. | SUPPORTED | S2 problem and context-aware representation rationale. |
| N04 | SkinExo-AI asks a focused question: when the recipient is a human dermal fibroblast, which response programs repeat across EV contexts, which depend on context, and where is the evidence absent or discordant? | SUPPORTED | Narrative contract; framework core scientific question. |

## Scene 2

| ID | Narration sentence | Status | Evidence / boundary |
|---|---|---|---|
| N05 | We structured three public, study-level independent contexts. | SUPPORTED_WITH_LIMITATIONS | F2 context features; independence is study-level only. |
| N06 | CTX001 uses endothelial-cell-derived EVs with primary human dermal fibroblasts at seventy-two hours. | SUPPORTED | `skinexo_context_features.csv`, CTX001. |
| N07 | CTX002 uses bone-marrow mesenchymal-stromal-cell small EVs with primary human dermal fibroblasts at forty-eight hours. | SUPPORTED | `skinexo_context_features.csv`, CTX002. |
| N08 | CTX003 uses human dermal-fibroblast-derived EVs with human dermal fibroblasts at seventy-two hours. | SUPPORTED | `skinexo_context_features.csv`, CTX003. |
| N09 | These studies share a recipient biological class, but they are not experimentally identical. | SUPPORTED | Context-feature differences in EV source, time, dose, and design. |
| N10 | Study independence does not establish donor-level or EV-preparation-level replication. | SUPPORTED_WITH_LIMITATIONS | Reliability records and claim dictionary limitation. |

## Scene 3

| ID | Narration sentence | Status | Evidence / boundary |
|---|---|---|---|
| N11 | We first tested whether a broadly reproducible EV-associated response existed. | SUPPORTED | EXP002/EXP003 prospective validation endpoints. |
| N12 | The result was not broad concordance. | NOT_SUPPORTED | F2: broad universal EV response `NOT_SUPPORTED`. |
| N13 | It was something more informative: context dependence. | SUPPORTED | F2 M/A interpretations and component-level differences. |
| N14 | Proliferation retained one shared component in CTX001 and CTX002, but that component did not extend to CTX003. | SUPPORTED | P interpretation `TWO_CONTEXT_SHARED_COMPONENT`; CTX003 observed null. |
| N15 | Migration and vascular or endothelial interaction were context-dependent and discordant. | SUPPORTED | M and A interpretation `CONTEXT_DEPENDENT_DISCORDANT`. |
| N16 | ECM organization remained null or not testable in the three-context interpretation. | SUPPORTED | E interpretation `NULL_NOT_TESTABLE`. |
| N17 | Inflammation showed a conserved broad axis with context-varying components. | SUPPORTED | I interpretation `CONSERVED_AXIS_CONTEXT_VARIANT`. |
| N18 | CTX002 and CTX003 shared exact inflammatory components, while CTX001 reached the same broad axis through a different component structure. | SUPPORTED | F2 Atlas and R1 explanations. |
| N19 | Same axis does not mean same component. | SUPPORTED | Component-aware framework distinction, demonstrated by I. |

## Scene 4

| ID | Narration sentence | Status | Evidence / boundary |
|---|---|---|---|
| N20 | That result motivated the Response Atlas. | SUPPORTED | F1/F2 reports and narrative contract. |
| N21 | The Atlas contains three verified contexts, three hundred thirty-nine stable response components, and one thousand seventeen context-component records. | SUPPORTED | `framework_f2_atlas.json`. |
| N22 | Each record links context, axis, component, direction, statistical evidence, phenotype support, reliability, and provenance. | SUPPORTED | `ATLAS_SCHEMA.md` and Atlas long-table fields. |
| N23 | It also preserves missingness. | SUPPORTED | F2 activity-state and tested-mask schema. |
| N24 | Observed null means a component was tested but did not qualify as active. | SUPPORTED | F2 controlled activity-state definition. |
| N25 | Not tested means comparable evidence is unavailable. | SUPPORTED | F2 controlled activity-state definition. |
| N26 | Those states are not interchangeable, and neither is silently converted to biological zero. | SUPPORTED | `RESPONSE_REPRESENTATION.md`; R1 mask policy and sanity tests. |

## Scene 5

| ID | Narration sentence | Status | Evidence / boundary |
|---|---|---|---|
| N27 | Now we open the offline Explorer at its default query, CTX003. | SUPPORTED | `explorer_a1.json`; Explorer test. |
| N28 | The context card keeps EV source, recipient, dose, duration, dataset, and unresolved limitations visible. | SUPPORTED | Implemented A1 UI and context loader. |
| N29 | Its response profile preserves observed-null proliferation and ECM evidence alongside active migration, vascular-interaction, and inflammatory components. | SUPPORTED | CTX003 F2 axis summary and Atlas records. |
| N30 | Retrieval compares components tested in both contexts using mask-aware NES cosine. | SUPPORTED | R1 specification and implementation. |
| N31 | For CTX003, CTX002 ranks first with response similarity plus zero point six zero five three. | SUPPORTED | `retrieval_r1.json`; descriptive metric only. |
| N32 | CTX001 ranks second at minus zero point two seven five five. | SUPPORTED | `retrieval_r1.json`; descriptive metric only. |
| N33 | These are descriptive response similarities, not probabilities or prediction accuracy. | SUPPORTED | Claim dictionary predictive-performance boundary. |
| N34 | The WHY panel explains the ranking. | SUPPORTED | R1 deterministic explanation engine and A1 UI. |
| N35 | CTX002 and CTX003 share nine active components in the same direction, with directional concordance of one point zero zero zero. | SUPPORTED_WITH_LIMITATIONS | R1 pairwise record; n=3 contexts and descriptive retrieval. |
| N36 | Active-union cosine is plus zero point eight five six three. | SUPPORTED_WITH_LIMITATIONS | R1 pairwise record; secondary descriptive metric. |
| N37 | The Explorer also exposes discordant, query-only, target-only, and observed-null differences instead of hiding them behind one number. | SUPPORTED | R1 explanation schema and implemented WHY panel. |
| N38 | Phenotype evidence remains separate. | SUPPORTED | F1/F2 evidence-layer rules; phenotype is unscored in R1. |
| N39 | CTX003 includes CCK-8 and scratch-assay anchors at twenty-four hours, while its transcriptome is measured at seventy-two hours. | SUPPORTED_WITH_LIMITATIONS | Phenotype anchor table; different-timepoint limitation. |
| N40 | Reliability is shown dimension by dimension, including unknown donor and EV-preparation independence. | SUPPORTED_WITH_LIMITATIONS | CTX003 reliability records; no independent-donor/preparation claim. |
| N41 | Neither layer changes the similarity score. | SUPPORTED | R1 specification and implementation. |

## Scene 6

| ID | Narration sentence | Status | Evidence / boundary |
|---|---|---|---|
| N42 | Every displayed interpretation traces to a public dataset, frozen checkpoint, analysis method, and gene-set release. | SUPPORTED | Atlas provenance and Explorer provenance panel. |
| N43 | The Explorer runs from tracked derived artifacts without raw sequencing data, licensed publications, or internet access at runtime. | SUPPORTED | A1 offline artifact closure tests and checkpoint. |
| N44 | Seventeen of seventeen retrieval and Explorer tests pass. | SUPPORTED | Current test suite result. |
| N45 | This validates deterministic behavior and artifact closure; it is not predictive validation. | SUPPORTED | Test scope and claim dictionary boundary. |
| N46 | SkinExo-AI version zero point three is a research-support platform, not a trained predictive model or therapeutic predictor. | SUPPORTED | Implemented-system boundary and forbidden-claims list. |
| N47 | Future work may add versioned EV contexts, analyze the deferred cargo dataset, and test cargo-to-response-to-phenotype hypotheses without presuming causality. | FUTURE | GSE293957 remains unanalyzed; claim dictionary future wording. |
| N48 | Prospective experiments and future Organ-on-Chip integration could then evaluate context-specific hypotheses. | FUTURE | Claim dictionary future directions. |
| N49 | SkinExo-AI does not assume a universal EV response. | NOT_SUPPORTED | Universal response `NOT_SUPPORTED` across three analyzed contexts. |
| N50 | It retrieves and explains context-dependent response patterns while keeping evidence, phenotype anchors, reliability, missingness, and provenance visible. | SUPPORTED | F2, R1, and A1 implemented capabilities. |
| N51 | Context matters. | SUPPORTED | Canonical conclusion from the three-context result. |

## Audit decision

- Narration sentences audited: **51/51**
- Unsupported positive claims: **0**
- Required limitations present: **PASS**
- Future work explicitly labeled: **PASS**
- Predictive/therapeutic overclaim: **NONE**
- **Claim audit: PASS**
