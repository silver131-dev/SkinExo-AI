# SkinExo-AI Explorer A2

The Explorer is a local Streamlit interface over the frozen F2 Response Atlas and R1 retrieval engine. A2 adds a judge-facing Demo Mode while preserving the full A1 research interface.

## Launch

From the repository root:

```bash
python -m pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

The default mode is **Demo** and the default query is **CTX003**. The mode and context controls are bound to URL query parameters for shareable views. No new runtime dependency is introduced by A2.

## Demo Mode

Demo Mode presents one continuous product story:

1. CTX003 context identity and essential conditions.
2. Deterministic Biological Summary.
3. P/M/E/A/I Response Signature and Primary Findings.
4. Most Similar Observed Context: CTX002 with response similarity `+0.6053`.
5. WHY THIS MATCH explanation from the existing R1 records.
6. Separate transcriptomic, phenotype-anchor, and reliability snapshots.
7. Advanced evidence and provenance on demand.

The summary is generated at runtime from the existing Atlas, retrieval, and reliability structures. It has no stochastic behavior, LLM, external API, predictive model, or aggregate confidence score.

## Research Mode

Research Mode retains the detailed interface:

- complete context metadata and limitations;
- five-axis response overview;
- component-level evidence and stored activity states;
- full retrieval rankings, metrics, and explanations;
- phenotype anchors with timepoint and model differences;
- all reliability dimensions;
- provenance and technical source details.

Response Atlas, Context Similarity, and About remain available as deeper views.

## Visual and accessibility system

VISUAL-V1 uses the Korean medical-aesthetic × biotech palette defined in `app/design_tokens.py` and `.streamlit/config.toml`. Positive, negative, observed-null, not-tested, unknown, and mixed states are encoded with text, symbols, counts, and border patterns in addition to color. Internal enums are translated into human-facing labels in the primary UI; stored values remain unchanged.

## Scientific boundaries

- Retrieval is descriptive among experimentally observed contexts; it is not a prediction, probability, accuracy, or confidence measure.
- `+0.6053` is displayed as response similarity, never as a percentage.
- Phenotype anchors remain separate from transcriptomic response and do not enter similarity.
- Reliability remains dimension-by-dimension; missing or unresolved evidence stays visible.
- A shared response axis does not imply identical active components.
- The interface makes no causal, therapeutic-efficacy, donor-level replication, EV-preparation-level replication, or universal EV-response claim.

## Offline behavior

The application reads tracked files under `data/metadata/`, `outputs/framework/`, and `outputs/retrieval/`. The reusable retrieval implementation remains in `src/skinexo/retrieval.py`; A2 does not duplicate or modify the retrieval algorithm.

Normal operation requires no raw GEO data, processed count matrices, licensed PDFs, database, external API, notebook, internet connection, or locally installed Streamlit development skill.

## Tests

```bash
pytest
python experiments/explorer/02_validate_explorer_a2.py --server-health-verified
```

The framework, Atlas, and retrieval validators are separate frozen-artifact checks. A2 validation does not rerun DESeq2, GSEA, or EXP001–EXP003.
