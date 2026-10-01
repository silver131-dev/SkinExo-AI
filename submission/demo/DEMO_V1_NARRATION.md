# SkinExo-AI DEMO-V1 final narration

**Target runtime:** 4:55
**Delivery:** calm, precise, intelligent, restrained

## Scene 1 — The Problem · 0:00–0:35

Extracellular vesicles carry biological signals between cells, but their effects are usually studied one experiment at a time. EV source, recipient cell, dose, duration, and study design can all differ. That makes response evidence difficult to compare without losing the context that produced it. SkinExo-AI asks a focused question: when the recipient is a human dermal fibroblast, which response programs repeat across EV contexts, which depend on context, and where is the evidence absent or discordant?

## Scene 2 — Three EV Contexts · 0:35–1:05

We structured three public, study-level independent contexts. CTX001 uses endothelial-cell-derived EVs with primary human dermal fibroblasts at seventy-two hours. CTX002 uses bone-marrow mesenchymal-stromal-cell small EVs with primary human dermal fibroblasts at forty-eight hours. CTX003 uses human dermal-fibroblast-derived EVs with human dermal fibroblasts at seventy-two hours. These studies share a recipient biological class, but they are not experimentally identical. Study independence does not establish donor-level or EV-preparation-level replication.

## Scene 3 — The Scientific Turn · 1:05–1:45

We first tested whether a broadly reproducible EV-associated response existed. The result was not broad concordance. It was something more informative: context dependence. Proliferation retained one shared component in CTX001 and CTX002, but that component did not extend to CTX003. Migration and vascular or endothelial interaction were context-dependent and discordant. ECM organization remained null or not testable in the three-context interpretation. Inflammation showed a conserved broad axis with context-varying components. CTX002 and CTX003 shared exact inflammatory components, while CTX001 reached the same broad axis through a different component structure. Same axis does not mean same component.

## Scene 4 — The Response Atlas · 1:45–2:20

That result motivated the Response Atlas. The Atlas contains three verified contexts, three hundred thirty-nine stable response components, and one thousand seventeen context-component records. Each record links context, axis, component, direction, statistical evidence, phenotype support, reliability, and provenance. It also preserves missingness. Observed null means a component was tested but did not qualify as active. Not tested means comparable evidence is unavailable. Those states are not interchangeable, and neither is silently converted to biological zero.

## Scene 5 — Live Explorer · 2:20–3:55

Now we open the offline Explorer at its default query, CTX003. The context card keeps EV source, recipient, dose, duration, dataset, and unresolved limitations visible. Its response profile preserves observed-null proliferation and ECM evidence alongside active migration, vascular-interaction, and inflammatory components.

Retrieval compares components tested in both contexts using mask-aware NES cosine. For CTX003, CTX002 ranks first with response similarity plus zero point six zero five three. CTX001 ranks second at minus zero point two seven five five. These are descriptive response similarities, not probabilities or prediction accuracy.

The WHY panel explains the ranking. CTX002 and CTX003 share nine active components in the same direction, with directional concordance of one point zero zero zero. Active-union cosine is plus zero point eight five six three. The Explorer also exposes discordant, query-only, target-only, and observed-null differences instead of hiding them behind one number.

Phenotype evidence remains separate. CTX003 includes CCK-8 and scratch-assay anchors at twenty-four hours, while its transcriptome is measured at seventy-two hours. Reliability is shown dimension by dimension, including unknown donor and EV-preparation independence. Neither layer changes the similarity score.

## Scene 6 — Evidence, Reliability & Vision · 3:55–4:55

Every displayed interpretation traces to a public dataset, frozen checkpoint, analysis method, and gene-set release. The Explorer runs from tracked derived artifacts without raw sequencing data, licensed publications, or internet access at runtime. Seventeen of seventeen retrieval and Explorer tests pass. This validates deterministic behavior and artifact closure; it is not predictive validation.

SkinExo-AI version zero point three is a research-support platform, not a trained predictive model or therapeutic predictor. Future work may add versioned EV contexts, analyze the deferred cargo dataset, and test cargo-to-response-to-phenotype hypotheses without presuming causality. Prospective experiments and future Organ-on-Chip integration could then evaluate context-specific hypotheses.

SkinExo-AI does not assume a universal EV response. It retrieves and explains context-dependent response patterns while keeping evidence, phenotype anchors, reliability, missingness, and provenance visible. Context matters.
