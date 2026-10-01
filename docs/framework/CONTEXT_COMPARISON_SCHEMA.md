# F1 context comparison schema

One row in `data/metadata/skinexo_context_comparisons.csv` compares two analyzed contexts on one axis. The comparator must retain both contexts' EV source, recipient identity, species, dose, exposure time, study, statistical design, and evidence layer by reference to their context rows. It must not compare a human in-vitro RNA-seq response with a mouse wound endpoint as if they were equivalent.

| Priority | Comparison level | F1 interpretation |
| --- | --- | --- |
| 1 | Same mapped component, same direction | `CONSERVED_COMPONENT` candidate within the observed independent contexts; inspect exact qualified terms and sensitivity |
| 2 | Same axis, different active components | `CONSERVED_AXIS` thematic overlap; no component replication claim |
| 3 | Meaningful context differences | `CONTEXT_DEPENDENT`, with the differing sources, doses, times, recipients or study systems named |
| 4 | Comparable opposing evidence | `DISCORDANT`; record whether same component or only axis-dominant directions oppose |
| 5 | Missing/null evidence | `NULL_NOT_TESTABLE` and an explicit missing-coverage, observed-null, or metadata reason |
| 6 | Material sensitivity change | `SENSITIVITY_DEPENDENT` flag alongside both primary and preregistered sensitivity conclusions |

The hierarchy is an interpretation guide, not a numeric ranking of biological importance. Direct opposing evidence can supersede thematic overlap; observed null prevents an activity claim. If a planned context has no SkinExo omics result, its state is `UNKNOWN` and no biological comparison row is created.

F1 records five CTX001-vs-CTX002 rows. `prior_c4_status` is copied unchanged from `outputs/exp002/c4_axes_exp001_vs_primary.csv`; `framework_state` is the added component-aware interpretation. `shared_component`, `same_direction`, and `limitations` keep the rationale visible. The EXP002 sensitivity fit does not change any of the five C4 axis outcomes.

After EXP003-C4 froze the CTX003 interpretation, ten rows were added for CTX001-vs-CTX003 and CTX002-vs-CTX003. These rows use `EXP003-C4` as their source checkpoint and preserve the original five rows. Pairwise component states remain separate from the three-context endpoint in `outputs/exp003/c4_three_context_comparison.csv`. Different EV sources, exposure durations, unresolved donor and preparation independence, and CTX003 design uncertainty block universal-response inference even when components match.
