# SkinExo-AI S2 claim dictionary

Use this dictionary to keep the Technical Report, Kaggle Writeup, demo, figures, README, and spoken narrative aligned.

## SUPPORTED

| Topic | Canonical wording | Evidence |
|---|---|---|
| Platform | SkinExo-AI v0.3 is a Context-Aware Extracellular-Vesicle Response Platform. | F2, R1, and A2 checkpoints |
| Context-aware response | SkinExo-AI represents EV-associated responses in the experimental context defined by EV source, recipient, species, dose, duration, study, and evidence layer. | Context schema and F2 context features |
| Atlas | The F2 Atlas contains 3 verified contexts, 339 response components, and 1,017 context-component records. | `framework_f2_validation.json` |
| Activity states | The Atlas preserves active positive, active negative, observed-null, not-tested, and unknown states. | F2 schema and validation |
| Universal response | A broad universal EV transcriptomic response was not supported across the three analyzed contexts. | F2 manifest and EXP003-C4 |
| P | P081 is a two-context shared component in CTX001 and CTX002; CTX003 is observed null across the frozen P mapping. | F2 Atlas and EXP003-C4 |
| M | Migration/motility shows context-dependent, discordant response structure. | F2 Atlas |
| E | ECM organization/remodeling is null/not testable in the three-context interpretation. | F2 Atlas |
| A | Vascular/endothelial interaction shows context-dependent, discordant transcriptomic evidence. | F2 Atlas |
| I | Inflammation/immune signaling is a conserved broad axis with context-varying component structure. CTX002 and CTX003 share exact components; CTX001 does not share that exact structure. | F2 Atlas and R1 explanations |
| Retrieval | R1 retrieves observed contexts using mask-aware NES cosine over shared-tested response components and produces deterministic WHY explanations. | `retrieval_r1.json` and tests |
| Default retrieval | For query CTX003, CTX002 ranks first at +0.6053 and CTX001 second at −0.2755. | R1 and A2 artifacts |
| Reliability | Reliability is represented in separate dimensions and is not folded into response similarity. | Reliability schema and table |
| Explorer | A2 is an offline Streamlit Explorer with a judge-facing Demo Mode and detailed Research Mode; it uses tracked derived artifacts and requires no raw data, licensed PDF, or internet at runtime. | `explorer_a2.json` |

## SUPPORTED_WITH_LIMITATIONS

| Topic | Canonical wording | Required limitation |
|---|---|---|
| Study independence | The three contexts are independent at the study level. | Do not generalize to donor or EV-preparation independence. |
| CTX002–CTX003 similarity | CTX002 and CTX003 have +0.6053 mask-aware response similarity; active-union cosine is +0.8563 with 9 same-direction shared active components. | Descriptive retrieval over three contexts; not prediction performance. |
| Phenotype evidence | CTX003 has CCK-8 and scratch-assay phenotype anchors from the same EV source and recipient. | Assays are at 24 h while transcriptomics is at 72 h; scratch closure can reflect motility and proliferation. |
| In-vivo evidence | Mouse wound closure, scar length, and collagen deposition are linked as in-vivo anchors. | Different species and model; not direct validation of human fibroblast transcriptomic axes. |
| Analytical validation | EXP001 internal reproduction, EXP002 independent-study comparison and sensitivity analysis, and the prospective CTX003 third-context test support the workflow. | Small context count and design uncertainty remain. |

## NOT_SUPPORTED

| Topic | Canonical wording |
|---|---|
| Universal EV biology | A universal EV transcriptomic response is not supported by these three contexts. |
| P across three contexts | Three-context P component conservation is not supported. |
| E generalization | A conserved ECM/remodeling response is not established. |
| Angiogenesis | Vascular/endothelial transcriptomic annotations do not demonstrate angiogenesis or neovascularization. |
| Therapeutic efficacy | SkinExo-AI v0.3 does not establish therapeutic efficacy or human wound-healing benefit. |
| Donor replication | Independent-donor replication is not established across the Atlas. |
| EV-preparation replication | Independent EV-preparation replication is not established across the Atlas. |
| Cargo causality | No causal cargo-response mechanism has been established; GSE293957 remains unanalyzed. |
| Predictive performance | No accuracy, AUC, generalization estimate, or prospective prediction performance exists. |

## FUTURE

| Topic | Canonical wording |
|---|---|
| Cargo integration | Future work may analyze GSE293957 and evaluate cargo → response → phenotype hypotheses without presuming causality. |
| Context expansion | Future versioned Atlas releases may add EV contexts under the same missingness and provenance rules. |
| Prospective validation | Prospective experiments can test context-specific response hypotheses and phenotype links. |
| Organ-on-Chip | Organ-on-Chip integration is a future experimental validation direction. |
| Predictive modeling | Predictive modeling may be evaluated only after the context base and prospective validation are sufficiently expanded. |

## AI and prediction language

Use **interpretable retrieval baseline**, **response similarity**, **evidence engine**, **Response Atlas**, and **interactive Explorer**. Do not call cosine similarity a trained AI model. The integrated evidence-aware representation and workflow are the technical contribution.
