# F1 cross-context evidence states

These values describe a comparison of two contexts for one mapped axis. They are stored in `skinexo_context_comparisons.csv` as `framework_state`; frozen `prior_c4_status` is retained separately. A state is an evidence description within observed contexts, never a universal biological law.

| State | Definition and minimum evidence |
| --- | --- |
| `CONSERVED_COMPONENT` | Same mapped biological component active in the same direction across independent contexts. Different terms within the component may qualify; preserve those term IDs and limits. |
| `CONSERVED_AXIS` | Same broad axis active with compatible dominant direction, but different active components drive the evidence. Thematic/axis overlap only. |
| `CONTEXT_DEPENDENT` | A meaningful contrast in response profile across experimental contexts without requiring directly opposite evidence for the same component. Record the context changes. |
| `DISCORDANT` | Comparable mapped evidence supports incompatible or opposing cross-context responses. Distinguish direct shared-component opposition from opposite axis-dominant directions from different components. |
| `NULL_NOT_TESTABLE` | Missing coverage, absent qualification, observed null, or insufficient evidence prevents valid cross-context activity comparison. Record which reason applies. |
| `SENSITIVITY_DEPENDENT` | The conclusion changes materially under a preregistered sensitivity analysis. Preserve both results and the perturbation. |
| `UNKNOWN` | Context not yet analyzed or metadata insufficient. |

Evidence-state assignment follows the component-first hierarchy in [Context comparison](CONTEXT_COMPARISON_SCHEMA.md). `SENSITIVITY_DEPENDENT` flags a material instability rather than silently replacing the primary result. A null is retained as a result; it is not evidence of similarity. `UNKNOWN` described CTX003 at F1. EXP003-C4 replaced those placeholders with computed CTX003 evidence and added pairwise comparisons without changing the frozen F1 CTX001-vs-CTX002 states.

The frozen EXP002-C4 labels remain `PARTIALLY_CONCORDANT` for P and I, `DISCORDANT` for M and A, and `NOT_TESTABLE` for E. F1 maps P to **candidate** `CONSERVED_COMPONENT` because one component, P081, is active positive in both studies; this does not make the whole P axis universally conserved. F1 maps I to `CONSERVED_AXIS` because positive dominant directions arise from different active components, with no shared active component. E is `NULL_NOT_TESTABLE` due to an observed EXP002 null despite adequate common term coverage. M and A retain `DISCORDANT`. These are additional interpretations and do not revise C4.
