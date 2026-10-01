# SkinExo-AI EXPLORER-A1

## Objective

Provide a fast local demonstration in which a judge can inspect a selected EV context, its component-level response, retrieved contexts, explanations, phenotype anchors, reliability, and provenance.

## User Experience

The application opens on CTX003 and presents one four-tab interface: Context Explorer, Response Atlas, Context Similarity, and About. The central message is visible at the top: same recipient cell plus different EV contexts yields different transcriptomic responses, so context matters.

## Context Explorer

The selected context card exposes EV source, recipient, species, dose, duration, sample count, dataset, study status, data status, and key limitations. Unknown metadata is rendered as “Unknown / Not documented.”

## Response Atlas

The application shows all 15 context-axis summaries and the frozen three-context interpretations. It retains active positive, active negative, observed-null, not-tested, phenotype-anchor, and mixed-direction distinctions.

## Retrieval

The UI calls `src/skinexo/retrieval.py` at runtime. With CTX003 as the default query, CTX002 ranks first (+0.6053) and CTX001 second (-0.2755). Scores are labeled response similarity, never prediction.

## Explainability

Every ordered match exposes shared positive, shared negative, discordant, query-only active, target-only active, and observed-null-difference components using the fixed R1 explanation rule. Axis-aware summaries display an explicit insufficient-evidence message when similarity is undefined.

## Phenotype Evidence

CTX003 includes five anchors. CCK-8 and scratch assays retain their 24 h timepoint against the 72 h transcriptome; mouse evidence is labeled in vivo and different model. Phenotype does not alter retrieval similarity.

## Reliability

Thirteen dimensions per context are displayed separately. No combined reliability score or percentage is computed.

## Provenance

Expandable provenance shows accession, study identifier, source checkpoint, analysis method, MSigDB release, trackable registry sources, and public study references. Licensed-PDF and institutional-access paths are excluded.

## Offline Reproducibility

The app uses only trackable metadata, F2 manifests, and the R1 checkpoint. It requires no raw GEO data, processed count matrix, PDF, internet connection, database, API server, or notebook. Tested technology: **Streamlit 1.64.0**. Launch with `streamlit run app/streamlit_app.py`.

## Demo Flow

The 60–90 second script starts at CTX003, shows the response overview, retrieves CTX002 first, opens shared inflammatory components, contrasts CTX001 discordance, then shows phenotype timing, reliability, and provenance.

## Limitations

Only three contexts exist. The Explorer demonstrates descriptive retrieval over observed studies and does not validate prediction, therapeutic efficacy, unseen-context generalization, donor replication, or EV-preparation replication. Final screenshots and video capture remain for the demo-video stage.

## Competition Role

A1 turns the evidence engine into a judge-facing narrative while keeping null evidence, missing metadata, phenotype layers, reliability limits, and claim boundaries visible.

## A1 Decision

**PASS.** AppTest rendered the complete default interface, the offline data contract passed, 17 unit/sanity tests passed, and the local server health smoke test was **PASS**. Predictive AI and an agent remain unimplemented.
