# SkinExo-AI FRAMEWORK-F2

## Objective

Convert the frozen CTX001, CTX002, and CTX003 evidence into Atlas version `F2-2026-10-01` without rerunning or changing any biological analysis.

## Why Three Contexts Are Sufficient for the Submission Atlas

Three study-independent contexts are sufficient to demonstrate the representation problem: a two-context shared component can fail to extend to a third context, the same axis can be driven by different components, direct component discordance can occur, and null evidence must remain visible. Three contexts do not support universal generalization, donor-level replication, or EV-preparation-level replication.

## Atlas Data Model

The Atlas links context features, a frozen component universe, 1,017 context-component records, 15 axis summaries, five phenotype anchors, and 39 separate reliability records. The wide matrix stores structured JSON cells; the long table is the normalized source for retrieval.

## Component Universe

The F2 universe contains **339** components frozen from the existing C4 mapping. Distinct components remain distinct even when they share an axis. Versioning is `F2-2026-10-01`; later additions require a new version.

## Activity States

`ACTIVE_POSITIVE`, `ACTIVE_NEGATIVE`, `OBSERVED_NULL`, `NOT_TESTED`, and `UNKNOWN` are distinct. F2 contains 158 active, 852 observed-null, 7 not-tested, and 0 unknown records. A null is tested nonqualification; it is not missing evidence.

## Context Feature Representation

Each context retains study, source, recipient, species, dose, duration, experimental system, sample allocation, donor/preparation status, batch, pairing, assay availability, and limitations. Unknown biological metadata remains textual missingness and is not numerically encoded.

## Response Representation

Each component record contains a deterministic representative tested term, NES, FDR, direction, activity state, tested/active masks, phenotype links, sensitivity status, reliability references, checkpoint, and provenance. For multi-term components, the representative is the qualified term with lowest FDR, then greatest absolute NES; observed-null components use the tested term selected by the same rule. No numeric value is produced for untested components.

## P

P081 is active in CTX001 and CTX002. CTX003 has an observed-null P axis and P081 does not qualify. F2 therefore records `TWO_CONTEXT_SHARED_COMPONENT`, not three-context conservation or a universal EV response.

## M

CTX003 is positive through M003, M010, M011, and M025. Direct opposition to CTX001 and different positive components in CTX002 support `CONTEXT_DEPENDENT_DISCORDANT`.

## E

CTX002 and CTX003 are observed null under the frozen mapping; CTX001 is negative. The cross-context conclusion remains `NULL_NOT_TESTABLE`.

## A

CTX003 A008 is positive while CTX001 A008 is negative. This is `CONTEXT_DEPENDENT_DISCORDANT` and does not establish angiogenesis or vascular benefit.

## I

CTX002 and CTX003 share exact positive inflammatory components, while CTX001 shares broad positive axis direction without the same active component structure. F2 records `CONSERVED_AXIS_CONTEXT_VARIANT`, never component conservation across all three.

## Phenotype Anchors

CTX003 CCK-8 and scratch assays are 24 h functional evidence linked by anchor IDs to P and M; transcriptomics is 72 h. Mouse wound, scar, and collagen anchors are different-model in-vivo evidence. Phenotypes are not merged into NES or used to change pathway significance.

## Reliability

Reliability remains a 13-dimension vector per context. No opaque confidence score is computed. All studies are independent, but donor and EV-preparation independence are not established across the Atlas; CTX003 retains its unexplained dominant PC1 structure and unresolved batch, pairing, and control details.

## Global Response Similarity

Secondary descriptive NES correlations are CTX001/CTX002 Pearson -0.0773, Spearman -0.1318; CTX001/CTX003 Pearson -0.1692, Spearman -0.1767; CTX002/CTX003 Pearson +0.1878, Spearman +0.1945. These are not prediction performance.

## Why a Universal EV Signature Is Not Supported

P does not extend its shared component to CTX003, M and A include discordance, E remains incompletely testable, and I conserves a broad axis with context-varying component structure. Global NES correlations are weak.

## Why Context-Aware Representation Is Needed

The same fibroblast recipient responds differently across EV source and exposure settings. Retaining component identity, nulls, missingness, phenotype layers, and reliability prevents broad axis labels from obscuring those differences.

## Retrieval-Ready Contract

The long Atlas provides component NES values plus `tested_mask` and `active_mask`. RETRIEVAL-R1 may consume these fields while keeping reliability outside similarity. F2 computes no cosine similarity, nearest neighbors, or PCA retrieval.

## Current Platform Capabilities

Implemented: three verified normalized contexts, reproducible source analyses, frozen component vocabulary, response Atlas, phenotype linkage, cross-context evidence, and reliability representation.

## Claim Boundaries

F2 does not establish prediction, therapeutic efficacy, universal EV biology, independent-donor replication, EV-preparation-level replication, causal cargo mechanisms, angiogenic activity, or human wound-healing efficacy. GSE293957 remains unanalysed.

## F2 Decision

**PASS.** The Atlas representation is complete and independently checked by `framework_f2_validation.json`. It is ready for an interpretable retrieval implementation; retrieval and the Explorer remain unimplemented.
