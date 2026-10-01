# Public artifact provenance

This document maps the artifacts used by the offline Explorer to their dataset basis, producing checkpoint, method, and source script.

| Public artifact | Dataset/context basis | Checkpoint and method | Source script |
|---|---|---|---|
| `data/metadata/skinexo_context_features.csv` | CTX001–CTX003 / GSE293186, GSE251807, GSE293956 | F2 context normalization | `experiments/framework/02_build_atlas.py` |
| `data/metadata/skinexo_component_universe.csv` | Frozen GO BP, Reactome, and Hallmark component mapping | F2 component universe, version `F2-2026-10-01` | `experiments/framework/02_build_atlas.py` |
| `data/metadata/skinexo_response_atlas_long.csv` | CTX001–CTX003 frozen C4 pathway results | F2 component-level Atlas; NES, FDR, direction, activity and missingness | `experiments/framework/02_build_atlas.py` |
| `data/metadata/skinexo_axis_summary.csv` | CTX001–CTX003 | F2 P/M/E/A/I summaries | `experiments/framework/02_build_atlas.py` |
| `data/metadata/skinexo_phenotype_anchors.csv` | CTX003 study metadata and literature evidence | F1/F2 separate phenotype layer | `experiments/framework/00_build_framework_metadata.py` |
| `data/metadata/skinexo_reliability.csv` | CTX001–CTX003 design and analysis records | F1/F2 separate reliability dimensions | F1/F2 framework builders |
| `outputs/framework/framework_f2_atlas.json` | Three verified contexts | F2 Atlas manifest | `experiments/framework/02_build_atlas.py` |
| `outputs/framework/framework_f2_validation.json` | F2 public representation | Atlas schema validation | `experiments/framework/02_validate_atlas.py` |
| `outputs/retrieval/retrieval_r1.json` | F2 Atlas | R1 mask-aware NES cosine and secondary metrics | `experiments/retrieval/01_build_retrieval.py` |
| `outputs/retrieval/r1_explanations.json` | All six ordered context pairs | R1 deterministic component explanations | `experiments/retrieval/01_build_retrieval.py` |
| `outputs/explorer/explorer_a1.json` | F2 + R1 tracked artifacts | A1 offline UI and data-contract validation | `experiments/explorer/01_validate_explorer.py` |

## Biological analysis chain

- CTX001 results originate from EXP001 C1–C4.
- CTX002 results originate from EXP002 D0/C1/C1R/C2/C2R/C3/C4.
- CTX003 results originate from EXP003 D0–C4.
- F2 changes representation only; it does not rerun DE or enrichment.
- R1 computes similarity over the frozen F2 component values.
- A1 calls the R1 implementation at runtime and does not duplicate the algorithm.

## Gene-set provenance

Pathway results use the frozen MSigDB `2026.1.Hs` GO Biological Process, Reactome, and Hallmark collections recorded in each C4 gene-set manifest. GMT files are not redistributed. MSigDB and all source datasets retain their own terms and citation requirements.

## Integrity

The public-readiness audit validates that every artifact required by `app/data_loader.py` is tracked. Explorer tests additionally verify the three contexts, 339 components, frozen R1 rankings, phenotype and reliability loading, and absence of raw-data or PDF dependencies.
