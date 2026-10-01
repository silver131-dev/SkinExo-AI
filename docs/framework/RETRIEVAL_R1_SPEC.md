# SkinExo-AI RETRIEVAL-R1 specification

## Problem

Given a query EV-response context, retrieve the most similar known contexts based on transcriptomic response components tested in both contexts. Every result must explain why contexts align, where they differ, which evidence is missing, and which phenotype and reliability information accompanies the response.

R1 is an interpretable retrieval baseline over Atlas `F2-2026-10-01`. It is not a trained model, classifier, therapeutic predictor, performance evaluation, or claim of generalization.

## Inputs

- The 339-component F2 universe.
- Representative component GSEA NES and activity state for each context.
- `tested_mask` and `active_mask` aligned to the component universe.
- Context features, phenotype anchors, reliability dimensions, checkpoint provenance, and evidence provenance.
- A required `PASS` result from `framework_f2_validation.json`.

## Missingness policy

| State | Primary cosine | Active-union cosine | Meaning |
| --- | --- | --- | --- |
| `ACTIVE_POSITIVE` | Included when both contexts tested the component | Included | Qualified positive component |
| `ACTIVE_NEGATIVE` | Included when both contexts tested the component | Included | Qualified negative component |
| `OBSERVED_NULL` | Included when both contexts tested the component | Included only when the other context is active | Tested component without qualifying activity |
| `NOT_TESTED` | Excluded | Excluded | No eligible test; never imputed as zero |
| `UNKNOWN` | Excluded | Excluded | Unresolved evidence; never imputed as zero |

## Primary metric

For query vector `q`, target vector `t`, and shared-tested component set `S`:

```text
cosine(q,t | S) = sum(q_i t_i) / (sqrt(sum(q_i^2)) sqrt(sum(t_i^2))), i in S
```

At least two shared-tested components are required. Missing components never enter the numerator or either norm. A missing overlap or zero norm returns an explicit undefined status rather than zero.

## Secondary metrics

**Active-union cosine:** restrict to components that are tested in both contexts and active in either. This reduces domination by jointly nonqualifying components.

**Directional concordance:** among components active in both contexts, report same-direction and opposite-direction counts. Concordance is `same / (same + opposite)` and is undefined when there is no shared-active component. Jointly null components are excluded.

**Axis-aware similarity:** repeat primary cosine separately within P, M, E, A, and I. At least two shared-tested axis components are required. Axis records also retain shared-active and direction counts.

## Explanation rule

Every ordered query-target pair reports:

- shared positive active components;
- shared negative active components;
- active components with opposing direction;
- query-only and target-only active components among shared-tested features;
- observed-null differences;
- axis explanations;
- attached phenotype anchors;
- separate reliability records;
- limitations and provenance.

Within each component class, records are ranked by `abs(query NES) + abs(target NES)` descending and component ID ascending as a deterministic tie break. The first ten are displayed. This rule is fixed independently of the biological narrative.

## Ranking and demonstration

Known targets are ranked by primary mask-aware cosine descending, then context ID for ties. With three contexts, each context can retrieve only two targets. The leave-one-context-out display is a behavior demonstration, not conventional train/test evaluation or predictive validation.

Phenotype anchors and reliability dimensions never alter similarity in R1. They remain adjacent explanatory evidence so a high response similarity cannot hide design uncertainty or imply phenotype equivalence.
