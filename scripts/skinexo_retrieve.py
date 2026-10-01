#!/usr/bin/env python3
"""Command-line interface for SkinExo-AI RETRIEVAL-R1."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from skinexo.retrieval import build_response_matrix, load_atlas, retrieve_contexts


def component_ids(rows, limit=6):
    values = [row["component_id"] for row in rows]
    if not values:
        return "none"
    shown = ", ".join(values[:limit])
    return shown + (f" (+{len(values)-limit} more shown in JSON)" if len(values) > limit else "")


def main():
    parser = argparse.ArgumentParser(description="Retrieve similar observed SkinExo response contexts")
    parser.add_argument("--query", required=True, help="Atlas context ID, for example CTX003")
    parser.add_argument("--root", default=str(ROOT), help="SkinExo-AI repository root")
    args = parser.parse_args()
    atlas = load_atlas(args.root)
    matrix = build_response_matrix(atlas)
    try:
        ranked = retrieve_contexts(atlas, matrix, args.query)
    except KeyError as exc:
        parser.error(str(exc))
    print(f"Query context: {args.query}")
    feature = atlas.context_features[args.query]
    print(f"EV source: {feature['ev_source']}")
    print(f"Recipient: {feature['recipient']}")
    print("Metric: mask-aware cosine of NES on shared-tested components")
    print("Phenotype and reliability are attached explanations; they do not affect similarity.\n")
    for result in ranked:
        primary = "undefined" if result["primary_similarity"] is None else f"{result['primary_similarity']:+.4f}"
        active = "undefined" if result["active_similarity"] is None else f"{result['active_similarity']:+.4f}"
        concordance = "undefined" if result["directional_concordance"] is None else f"{result['directional_concordance']:.3f}"
        print(f"Rank {result['rank']}: {result['target']}")
        print(f"  Primary similarity: {primary} ({result['shared_tested_components']} shared-tested components)")
        print(f"  Active-response similarity: {active} ({result['active_union_components']} active-union components)")
        print(f"  Shared active: {result['shared_active_components']}; directional concordance: {concordance}")
        print(f"  Shared positive: {component_ids(result['shared_positive_components'])}")
        print(f"  Shared negative: {component_ids(result['shared_negative_components'])}")
        print(f"  Discordant: {component_ids(result['discordant_components'])}")
        anchors = result["phenotype_anchors"]["target"]
        print("  Target phenotype evidence: " + (", ".join(f"{row['anchor_id']} ({row['evidence_level']})" for row in anchors) if anchors else "none registered"))
        limited = [row for row in result["reliability_target"] if row["status"] in {"LIMITED", "UNKNOWN"}]
        print("  Target reliability notes: " + ("; ".join(f"{row['dimension']}={row['status']}" for row in limited) if limited else "no limited/unknown dimension"))
        print()
    print("R1 is descriptive retrieval over three observed contexts; no predictive model is used.")


if __name__ == "__main__":
    main()
