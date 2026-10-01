# SkinExo-AI FRAMEWORK-F1

## Motivation

SkinExo-AI is positioned as a Context-Aware Extracellular-Vesicle Response Platform. F1 converts frozen EXP001/EXP002 results into auditable context, response, component, evidence, and reliability records. It makes uncertainty and negative evidence first-class data without changing numerical outputs.

## Empirical Trigger

The prespecified EXP001-vs-EXP002 broad five-axis concordance hypothesis was **not supported**. P and I were `PARTIALLY_CONCORDANT`, M and A `DISCORDANT`, and E `NOT_TESTABLE` because EXP002 had an observed null GSEA result. The [frozen C4 report](EXP002_C4_cross_study_pathway_validation.md) and [DEV-C1 manifest](../docs/checkpoints/DEV_C1_MANIFEST.md) are the source of these labels.

## Core Scientific Question

Given an EV source and biological context, which recipient-cell response programs are shared at a mapped component, shared only at a broad axis, context dependent, discordant, null/not testable, sensitivity dependent, or unknown?

## Context Schema

[Three contexts](../data/metadata/skinexo_contexts.csv) retain species, recipient, EV source, dose, time, omics system, arm counts, design, data status, uncertainty, and provenance. [Schema](../docs/framework/CONTEXT_SCHEMA.md). `PLANNED` for CTX003 is SkinExo analysis status; it does not deny the publication of the Liu study.

## Response Schema

[Fifteen response rows](../data/metadata/skinexo_responses.csv) cover P/M/E/A/I in three contexts. CTX001/CTX002 rows derive only from frozen C4; CTX003 rows are blank transcriptomic placeholders with `UNKNOWN`. NES/FDR, when present, refer to a named representative qualified term. [Schema](../docs/framework/RESPONSE_SCHEMA.md).

## Component Layer

[Component rows](../data/metadata/skinexo_response_components.csv) retain every C4 common eligible cluster per analyzed context, its exact mapped terms, qualified terms, direction, per-term evidence, and EXP002 sensitivity direction. Inactive rows preserve negative evidence. Components in the same axis are not interchangeable, and overlapping terms are not independent confirmations.

## Evidence States

The [controlled vocabulary](../docs/framework/EVIDENCE_STATE_SCHEMA.md) is `CONSERVED_COMPONENT`, `CONSERVED_AXIS`, `CONTEXT_DEPENDENT`, `DISCORDANT`, `NULL_NOT_TESTABLE`, `SENSITIVITY_DEPENDENT`, and `UNKNOWN`. F1 state is an additional interpretation; it does not revise C4 status.

## Evidence Layers

`TRANSCRIPTOME`, `FUNCTIONAL_ASSAY`, `IN_VIVO`, `CARGO`, `LITERATURE`, and `SENSITIVITY` retain measurement provenance. A GSEA pathway is an expression association, not a measured phenotype. A predicted miRNA target is not causal regulation. Evidence layers are complementary, not automatically equivalent.

## Phenotype Anchors

[CTX003 anchors](../data/metadata/skinexo_phenotype_anchors.csv) register author-reported 24 h human hDF CCK-8 and scratch readouts separately from planned 72 h RNA-seq. At graded hDF-EV doses, 10 ug/mL had the strongest reported CCK-8 effect; scratch treatment was 10 ug/mL. Mouse wound closure, scar length, and collagen deposition are explicit `Mus musculus` in-vivo rows and do not validate human fibroblast transcriptomics. Exact unpublished-at-F1 replicate and statistical details are `UNKNOWN`. [Anchor schema](../docs/framework/PHENOTYPE_ANCHOR_SCHEMA.md); [Liu primary record](https://pubmed.ncbi.nlm.nih.gov/40728022/).

## Reliability

The [reliability model](../docs/framework/RELIABILITY_SCHEMA.md) and [27 dimension records](../data/metadata/skinexo_reliability.csv) keep study independence, recipient-donor independence, EV-preparation independence, batch adjustment, sample QC, sensitivity stability, annotation certainty, phenotype support, and cross-context replication separate. No arbitrary aggregate score exists.

## CTX001

GSE293186: endothelial-cell-derived EV versus exosome-depleted-media control in primary human dermal fibroblasts, 72 h, 3+3 samples. Its frozen C4 transcriptomic directions are P positive dominant with an opposing component, M negative, E negative, A negative, and I positive dominant with an opposing component. These describe gene-set association, not direct cell behavior. Donor and EV-preparation independence remain unknown. [EXP001-C4](EXP001_C4_pathway_analysis.md).

## CTX002

GSE251807: human bone-marrow MSC small-EV fraction versus DMEM in primary normal human dermal fibroblasts, 30 ug/mL fraction protein, 48 h, 8+8 samples in two batches. Primary DESeq2 design was `~ batch + condition` with EV_8 retained; the EV_8-excluded run is a sensitivity fit. One recipient donor lot is documented; EV-preparation independence is unknown. It is an independent-study, same-cell-type comparison, **not independent-donor validation**. Primary C4 directions are P positive, M positive, E observed null, A positive, and I positive dominant with an opposing component. [EXP002-C4](EXP002_C4_cross_study_pathway_validation.md).

## CTX003 — Planned

GSE293956: human dermal fibroblast-derived EV, human dermal fibroblast recipient, 10 ug/mL, 72 h bulk RNA-seq design metadata. The series spans hDF and HaCaT samples; hDF arm counts and statistical design await EXP003-D0. No transcriptomic result or P/M/E/A/I state is assigned. Companion [GSE293957](../data/metadata/skinexo_cargo_datasets.csv) is available, unanalyzed hDF-EV miRNA array cargo and a future EXP006 candidate; no cargo-response causal link exists. [Liu provenance](../docs/literature/EXP003_D0_SOURCE_LOG.md), [primary study](https://pubmed.ncbi.nlm.nih.gov/40728022/).

## CTX001 vs CTX002

| Axis | Frozen C4 status | F1 state | Basis |
| --- | --- | --- | --- |
| P | `PARTIALLY_CONCORDANT` | `CONSERVED_COMPONENT` candidate | P081 positive in both, with different qualified terms; whole axis has opposing evidence |
| M | `DISCORDANT` | `DISCORDANT` | Opposite dominant directions; shared M026 opposite |
| E | `NOT_TESTABLE` | `NULL_NOT_TESTABLE` | Common eligible terms but no qualified EXP002 component |
| A | `DISCORDANT` | `DISCORDANT` | Opposite dominant vascular/endothelial directions; no direct angiogenesis assay |
| I | `PARTIALLY_CONCORDANT` | `CONSERVED_AXIS` | Positive dominant directions, different active components, no shared active I component |

All five C4 classifications persist under the frozen EXP002 sensitivity fit. [Machine-readable comparison](../data/metadata/skinexo_context_comparisons.csv) retains the prior labels and the new states separately. The source, time, donor, and EV-preparation differences limit any generalization.

## Platform Architecture

Data sources → context normalization → reproducible analysis → response objects → component-aware comparison → evidence/reliability → response representation → retrieval → Explorer/demo. Through evidence/reliability, F1 records implemented work, with reproducible analysis limited to frozen EXP001/EXP002. Representation, retrieval, and Explorer are **planned**. [Architecture detail](../docs/framework/SKINEXO_CONTEXT_AWARE_FRAMEWORK.md).

## Retrieval Contract

Future input: EV source, recipient, species, dose, time, and response vector. Future output: nearest contexts, similarity, shared and discordant components, evidence layers, and reliability dimensions. A standardized representation plus cosine similarity is the planned baseline; PCA may be a descriptive visualization. No retrieval is implemented and two analyzed contexts cannot establish retrieval performance. [Contract](../docs/framework/RETRIEVAL_CONTRACT.md).

## Current Capabilities

Frozen two-study transcriptomic analysis; three context registrations; ten analyzed and five placeholder response objects; full common-eligible component mapping; five cross-context comparisons; five author-reported CTX003 phenotype anchors; one unanalyzed cargo registration; 27 dimensional reliability records; schema validation.

## Planned Capabilities

EXP003-D0 context onboarding, later GSE293956 recipient analysis, possible EXP006 cargo analysis, response representation, retrieval, and Explorer. These are future work, not F1 outputs.

## Claim Boundaries

F1 does not implement predictive AI, a therapeutic predictor, a foundation model, or a digital twin. It does not show universal EV biology, independent-donor or EV-preparation replication, direct angiogenesis, scarless regeneration, or causal miRNA regulation. No author transcriptomic conclusions are imported into CTX003. Mouse wound endpoints are not human fibroblast assay results.

## F1 Decision

Framework metadata and schemas are complete when `outputs/framework/framework_f1_validation.json` reports `PASS`. The next checkpoint is EXP003-D0, not begun here.
