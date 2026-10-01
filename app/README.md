# SkinExo-AI Explorer A1

The Explorer is a local Streamlit interface over the frozen F2 Response Atlas and R1 retrieval engine. It lets a user inspect an EV context, response components, retrieved contexts, deterministic explanations, phenotype anchors, reliability dimensions, and provenance.

## Launch

From the repository root:

```bash
python -m pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

The default query is CTX003. R1 computes the ranking at runtime; CTX002 should appear first and CTX001 second for the frozen F2 Atlas.

## Screens

- **Context Explorer:** context metadata, P/M/E/A/I overview, component evidence, retrieval, “Why this match?”, phenotype, reliability, and provenance.
- **Response Atlas:** all three contexts and the frozen axis interpretations.
- **Context Similarity:** primary mask-aware and active-union similarity views.
- **About:** implemented features, scientific boundaries, and version status.

## Offline data dependencies

The application reads tracked files under `data/metadata/` and `outputs/framework/` plus the R1 checkpoint under `outputs/retrieval/`. The reusable retrieval implementation lives in `src/skinexo/retrieval.py`; similarity logic is not duplicated in the UI.

Normal operation requires no raw GEO files, processed count matrices, licensed publication PDFs, institutional resources, database, API server, notebook, or internet connection.

## Tests

```bash
pytest tests/test_explorer_data.py
pytest tests/test_retrieval.py
```

## Limitations

The Explorer covers three verified contexts. Retrieval is descriptive and does not predict response for new treatments or patients. Phenotype anchors and reliability metadata are explanatory layers and do not change similarity. The interface makes no therapeutic efficacy, donor-level replication, or EV-preparation-level replication claim.
