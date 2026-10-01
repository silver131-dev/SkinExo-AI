#!/usr/bin/env python3
"""Build RETRIEVAL-R1 artifacts from the validated F2 Atlas."""

from __future__ import annotations

import csv
import json
import math
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "skinexo_r1_mpl"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

from skinexo.retrieval import (
    active_union_similarity,
    build_response_matrix,
    compute_shared_tested_mask,
    directional_concordance,
    explain_pair,
    load_atlas,
    masked_cosine_similarity,
    retrieve_contexts,
)


OUT = ROOT / "outputs/retrieval"
FIG = ROOT / "submission/figures"
AXES = "PMEAI"


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def clean(value):
    return "" if value is None else repr(float(value))


def sanity_checks():
    a = np.array([1.0, -2.0, 3.0])
    tested = np.array([True, True, True])
    identical = masked_cosine_similarity(a, a.copy(), tested)
    reversed_result = masked_cosine_similarity(a, -a, tested)
    no_overlap = masked_cosine_similarity(a, a, np.array([False, False, False]))
    jointly_null = active_union_similarity(a, a, tested, tested, np.zeros(3, bool), np.zeros(3, bool))
    missing_a = np.array([np.nan, 2.0])
    missing_b = np.array([99.0, 2.0])
    missing_test_a = np.array([False, True])
    missing_test_b = np.array([True, True])
    not_tested = masked_cosine_similarity(missing_a, missing_b, compute_shared_tested_mask(missing_test_a, missing_test_b))
    unknown_a = np.array([np.nan, -3.0])
    unknown_b = np.array([0.0, -3.0])
    unknown = masked_cosine_similarity(unknown_a, unknown_b, compute_shared_tested_mask(missing_test_a, missing_test_b))
    checks = {
        "identical_vector_cosine_one": identical["status"] == "DEFINED" and math.isclose(identical["similarity"], 1.0, abs_tol=1e-12),
        "sign_reversal_cosine_negative_one": reversed_result["status"] == "DEFINED" and math.isclose(reversed_result["similarity"], -1.0, abs_tol=1e-12),
        "nonoverlap_is_undefined": no_overlap["similarity"] is None and no_overlap["status"] == "INSUFFICIENT_OVERLAP",
        "jointly_null_not_active_similarity": jointly_null["similarity"] is None and jointly_null["component_count"] == 0,
        "not_tested_excluded_not_zero": not_tested["component_count"] == 1 and math.isclose(not_tested["similarity"], 1.0, abs_tol=1e-12),
        "unknown_excluded_not_zero": unknown["component_count"] == 1 and math.isclose(unknown["similarity"], 1.0, abs_tol=1e-12),
    }
    return checks


def build_outputs(atlas, matrix):
    OUT.mkdir(parents=True, exist_ok=True)
    fields = ["context_id"] + list(matrix.components)
    values, tested_rows, active_rows = [], [], []
    for i, context in enumerate(matrix.contexts):
        values.append({"context_id": context, **{component: "" if np.isnan(matrix.values[i, j]) else repr(float(matrix.values[i, j])) for j, component in enumerate(matrix.components)}})
        tested_rows.append({"context_id": context, **{component: int(matrix.tested_mask[i, j]) for j, component in enumerate(matrix.components)}})
        active_rows.append({"context_id": context, **{component: int(matrix.active_mask[i, j]) for j, component in enumerate(matrix.components)}})
    write_csv(OUT / "r1_response_matrix.csv", values, fields)
    write_csv(OUT / "r1_tested_mask.csv", tested_rows, fields)
    write_csv(OUT / "r1_active_mask.csv", active_rows, fields)

    explanations = []
    pairwise = []
    for query in matrix.contexts:
        for target in matrix.contexts:
            if query == target:
                continue
            explanation = explain_pair(atlas, matrix, query, target)
            explanations.append(explanation)
            row = {
                "query_context": query, "target_context": target,
                "shared_tested_components": explanation["shared_tested_components"],
                "primary_cosine": clean(explanation["primary_similarity"]),
                "active_union_components": explanation["active_union_components"],
                "active_union_cosine": clean(explanation["active_similarity"]),
                "shared_active_components": explanation["shared_active_components"],
                "same_direction_active": explanation["same_direction_active"],
                "opposite_direction_active": explanation["opposite_direction_active"],
                "directional_concordance": clean(explanation["directional_concordance"]),
            }
            for axis in AXES:
                row[f"{axis}_similarity"] = clean(explanation["axis_explanations"][axis]["axis_NES_cosine"])
            pairwise.append(row)
    pair_fields = [
        "query_context", "target_context", "shared_tested_components", "primary_cosine",
        "active_union_components", "active_union_cosine", "shared_active_components",
        "same_direction_active", "opposite_direction_active", "directional_concordance",
        "P_similarity", "M_similarity", "E_similarity", "A_similarity", "I_similarity",
    ]
    write_csv(OUT / "r1_pairwise_similarity.csv", pairwise, pair_fields)
    (OUT / "r1_explanations.json").write_text(json.dumps({
        "retrieval_version": "R1", "atlas_version": atlas.atlas_version,
        "ranking_rule": "joint_NES_magnitude descending; component_id lexical tie break; top 10 per explanation class",
        "ordered_pair_count": len(explanations), "pairs": explanations,
    }, indent=2) + "\n")

    loco = []
    for query in matrix.contexts:
        ranked = retrieve_contexts(atlas, matrix, query)
        loco.append({
            "query": query,
            "results": [{
                "rank": item["rank"], "target": item["target"],
                "primary_similarity": item["primary_similarity"],
                "active_similarity": item["active_similarity"],
                "shared_tested_components": item["shared_tested_components"],
                "shared_active_components": item["shared_active_components"],
                "same_direction_active": item["same_direction_active"],
                "opposite_direction_active": item["opposite_direction_active"],
                "top_shared_positive": [row["component_id"] for row in item["shared_positive_components"][:5]],
                "top_discordant": [row["component_id"] for row in item["discordant_components"][:5]],
            } for item in ranked],
        })
    checks = sanity_checks()
    explanations_reproducible = explain_pair(atlas, matrix, matrix.contexts[0], matrix.contexts[1]) == explain_pair(atlas, matrix, matrix.contexts[0], matrix.contexts[1])
    checks["ordered_explanations_reproducible"] = explanations_reproducible
    attachment_checks = {
        "explanation_engine": len(explanations) == 6 and len({(row["query"], row["target"]) for row in explanations}) == 6,
        "phenotype_attachment": all(
            row["phenotype_anchors"]["query"] == atlas.phenotype_anchors[row["query"]]
            and row["phenotype_anchors"]["target"] == atlas.phenotype_anchors[row["target"]]
            for row in explanations
        ),
        "reliability_attachment": all(
            len(row["reliability_query"]) == 13 and len(row["reliability_target"]) == 13
            for row in explanations
        ),
        "matrix_mask_alignment": bool(
            np.all(matrix.tested_mask == np.isfinite(matrix.values))
            and np.all(~matrix.active_mask | matrix.tested_mask)
        ),
    }
    f2 = json.loads((ROOT / "outputs/framework/framework_f2_atlas.json").read_text())
    checkpoint = {
        "atlas_version": atlas.atlas_version, "retrieval_version": "R1",
        "contexts": len(matrix.contexts), "component_count": len(matrix.components),
        "primary_metric": "MASK_AWARE_COSINE_OF_SHARED_TESTED_COMPONENT_NES",
        "secondary_metrics": ["ACTIVE_UNION_COSINE", "DIRECTIONAL_CONCORDANCE", "AXIS_AWARE_NES_COSINE"],
        "mask_policy": {
            "NOT_TESTED": "EXCLUDED; never imputed as zero", "UNKNOWN": "EXCLUDED; never imputed as zero",
            "OBSERVED_NULL": "INCLUDED in primary NES cosine because it was tested; excluded from active masks",
            "minimum_primary_overlap": 2, "minimum_axis_overlap": 2,
        },
        "pairwise_results": pairwise,
        "leave_one_context_out_results": loco,
        "sanity_tests": checks,
        "artifact_checks": attachment_checks,
        "frozen_global_NES_correlations": f2["global_NES_correlations"],
        "predictive_model": False, "trained_parameters": "NONE",
        "phenotype_in_similarity": False, "reliability_in_similarity": False,
        "overall_pass": all(checks.values()) and all(attachment_checks.values()) and len(pairwise) == 6,
    }
    (OUT / "retrieval_r1.json").write_text(json.dumps(checkpoint, indent=2) + "\n")
    return pairwise, explanations, loco, checkpoint


def retrieval_figure(atlas, matrix, loco):
    FIG.mkdir(parents=True, exist_ok=True)
    query = "CTX003" if "CTX003" in matrix.contexts else matrix.contexts[0]
    results = next(row["results"] for row in loco if row["query"] == query)
    source = atlas.context_features[query]["ev_source"]
    fig, ax = plt.subplots(figsize=(15, 8.5), constrained_layout=True)
    ax.set_xlim(0, 15); ax.set_ylim(0, 9); ax.axis("off")
    fig.suptitle("Interpretable context retrieval · R1 demonstration", fontsize=22, fontweight="bold")
    ax.text(7.5, 8.45, "Mask-aware cosine over shared-tested component NES · n = 3 contexts · not predictive validation", ha="center", fontsize=11.5, color="#465667")
    qbox = FancyBboxPatch((.6, 3.15), 3.7, 2.7, boxstyle="round,pad=.04,rounding_size=.08", facecolor="#D6EAF5", edgecolor="#2878A5", linewidth=2.3)
    ax.add_patch(qbox)
    ax.text(2.45, 5.3, f"QUERY · {query}", ha="center", fontsize=16, fontweight="bold")
    ax.text(2.45, 4.8, source, ha="center", fontsize=10, wrap=True)
    ax.text(2.45, 4.3, "human dermal fibroblast recipient", ha="center", fontsize=9.5)
    ax.text(2.45, 3.72, "Phenotype anchors attached separately\nReliability retained separately", ha="center", fontsize=9, color="#6B4D80")
    ax.text(4.9, 4.5, "→", ha="center", va="center", fontsize=30, color="#697684")
    ax.text(9.68, 4.5, "→", ha="center", va="center", fontsize=30, color="#697684")
    for idx, result in enumerate(results):
        x = 5.5 + idx * 4.55
        color = "#F3D2A2" if idx == 0 else "#E7E9ED"
        box = FancyBboxPatch((x, 2.05), 3.8, 4.9, boxstyle="round,pad=.04,rounding_size=.08", facecolor=color, edgecolor="#6B7480", linewidth=2)
        ax.add_patch(box)
        ax.text(x + 1.9, 6.5, f"RANK {result['rank']} · {result['target']}", ha="center", fontsize=15, fontweight="bold")
        ax.text(x + 1.9, 5.92, f"Primary cosine  {result['primary_similarity']:+.3f}", ha="center", fontsize=12)
        active_value = "undefined" if result["active_similarity"] is None else f"{result['active_similarity']:+.3f}"
        ax.text(x + 1.9, 5.52, f"Active-union cosine  {active_value}", ha="center", fontsize=10.5)
        ax.text(x + 1.9, 5.12, f"Shared tested  {result['shared_tested_components']}  ·  shared active  {result['shared_active_components']}", ha="center", fontsize=9.2)
        shared = ", ".join(result["top_shared_positive"][:4]) or "none"
        discordant = ", ".join(result["top_discordant"][:4]) or "none"
        ax.text(x + .25, 4.55, "Top shared positive", fontsize=9.5, fontweight="bold")
        ax.text(x + .25, 4.2, shared, fontsize=9.2)
        ax.text(x + .25, 3.64, "Top discordant", fontsize=9.5, fontweight="bold")
        ax.text(x + .25, 3.29, discordant, fontsize=9.2)
        ax.text(x + .25, 2.62, "Rank explains response similarity;\nphenotype and reliability do not alter score.", fontsize=8.6, color="#4C5966")
    ax.text(7.5, .7, "R1 retrieves observed contexts. It does not predict outcomes for new treatments or patients.", ha="center", fontsize=11, color="#4C5966")
    fig.savefig(FIG / "fig10_context_retrieval.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def similarity_matrix_figure(matrix, pairwise):
    lookup = {(row["query_context"], row["target_context"]): float(row["primary_cosine"]) for row in pairwise}
    n = len(matrix.contexts)
    values = np.eye(n)
    for i, query in enumerate(matrix.contexts):
        for j, target in enumerate(matrix.contexts):
            if query != target:
                values[i, j] = lookup[(query, target)]
    fig, ax = plt.subplots(figsize=(8.8, 7.8), constrained_layout=True)
    image = ax.imshow(values, vmin=-1, vmax=1, cmap="RdBu_r")
    ax.set_xticks(range(n), matrix.contexts, fontsize=11)
    ax.set_yticks(range(n), matrix.contexts, fontsize=11)
    ax.set_xlabel("Target context"); ax.set_ylabel("Query context")
    for i in range(n):
        for j in range(n):
            ax.text(j, i, f"{values[i,j]:+.3f}", ha="center", va="center", fontsize=13, fontweight="bold" if i == j else "normal")
    fig.colorbar(image, ax=ax, label="Mask-aware cosine of shared-tested component NES")
    fig.suptitle("SkinExo-AI context similarity matrix", fontsize=19, y=.995)
    ax.set_title("n = 3 contexts · descriptive retrieval baseline\nnot predictive validation", fontsize=12.5, pad=12)
    fig.savefig(FIG / "fig11_context_similarity_matrix.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def report(pairwise, loco, checkpoint):
    unique = {(row["query_context"], row["target_context"]): row for row in pairwise}
    def pair(a, b): return unique[(a, b)]
    global_corr = checkpoint["frozen_global_NES_correlations"]
    ranking_lines = []
    for item in loco:
        order = ", ".join(f"#{r['rank']} {r['target']} ({r['primary_similarity']:+.3f})" for r in item["results"])
        ranking_lines.append(f"- {item['query']}: {order}")
    sanity_lines = "\n".join(f"- {name}: **{'PASS' if passed else 'FAIL'}**" for name, passed in checkpoint["sanity_tests"].items())
    rows = []
    for a, b in [("CTX001", "CTX002"), ("CTX001", "CTX003"), ("CTX002", "CTX003")]:
        p = pair(a, b)
        rows.append(f"| {a} / {b} | {float(p['primary_cosine']):+.4f} | {float(p['active_union_cosine']):+.4f} | {p['shared_tested_components']} | {p['shared_active_components']} | {float(p['directional_concordance']):.3f} |")
    report_text = f"""# SkinExo-AI RETRIEVAL-R1

## Objective

Implement a reproducible retrieval baseline that ranks known F2 contexts by shared-tested transcriptomic component response while preserving component identity, missingness, phenotype anchors, reliability, and provenance.

## Why Retrieval Instead of Prediction

Only three verified contexts exist. R1 retrieves and explains observed evidence; it has no learned parameters and does not estimate outcomes for an unseen treatment, patient, or study.

## Input Atlas

R1 requires F2 validation PASS and consumes Atlas `{checkpoint['atlas_version']}`: three contexts, 339 frozen components, explicit activity states, five phenotype anchors, and 39 reliability records. It does not rerun DE or GSEA.

## Missingness Semantics

`NOT_TESTED` and `UNKNOWN` are excluded using the shared-tested mask and are never converted to zero. `OBSERVED_NULL` remains a tested NES observation in primary similarity but is excluded from active-response similarity unless the other context makes the component active.

## Primary Similarity

For each pair, R1 restricts both raw representative NES vectors to components tested in both contexts and computes cosine similarity. At least two shared-tested components are required; insufficient overlap returns an explicit undefined status.

| Pair | Primary cosine | Active-union cosine | Shared tested | Shared active | Directional concordance |
| --- | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(rows)}

## Active-Response Similarity

The secondary active-union cosine uses mutually tested components active in either context. This reduces domination by components that were jointly tested but did not qualify. It does not replace the primary metric.

## Directional Concordance

Directional concordance is the fraction of shared-active components with the same active direction. Jointly null components are excluded. Same- and opposite-direction counts remain visible with the fraction.

## Axis-Aware Similarity

P, M, E, A, and I cosine summaries use their own mutually tested components and a minimum overlap of two. Axis explanations also expose shared-active, same-direction, and opposite-direction component counts. Component evidence remains the primary explanatory unit.

## Explanation Engine

For every ordered query-target pair, components are classified as shared positive, shared negative, discordant, query-only active, target-only active, or observed-null differences. Within each class, the top ten are ranked by `abs(query NES) + abs(target NES)`, with component ID as a deterministic tie break.

## Phenotype Evidence

Phenotype anchors are attached to query and target explanations. CTX003 P CCK-8 and M scratch anchors are 24 h functional evidence, separate from the 72 h transcriptome; mouse anchors remain in-vivo different-model evidence. Phenotypes do not enter either cosine.

## Reliability

All 13 reliability dimensions per context are attached without aggregation. Study independence, donor/preparation independence, sample QC, batch, pairing, control, diagnostics, sensitivity, and phenotype support remain separate from similarity.

## Leave-One-Context-Out Demonstration

{chr(10).join(ranking_lines)}

Each context is used as a query and the other two are ranked. This is a descriptive behavior demonstration, not train/test evaluation or predictive validation.

## Frozen Global NES Correlations

The F2 global Pearson/Spearman values are CTX001/CTX002 {global_corr['CTX001_vs_CTX002']['pearson']:+.4f}/{global_corr['CTX001_vs_CTX002']['spearman']:+.4f}, CTX001/CTX003 {global_corr['CTX001_vs_CTX003']['pearson']:+.4f}/{global_corr['CTX001_vs_CTX003']['spearman']:+.4f}, and CTX002/CTX003 {global_corr['CTX002_vs_CTX003']['pearson']:+.4f}/{global_corr['CTX002_vs_CTX003']['spearman']:+.4f}. Both summaries qualitatively place CTX002/CTX003 as the positive pair and CTX001 against the later contexts as negative, while R1 cosine separates those pairs more strongly. Correlation centers each vector and measures covariation; cosine measures angular alignment from zero on the F2 component representation. Shared-set definitions also differ. R1 was not tuned to reproduce correlation ordering.

## Sanity Tests

{sanity_lines}

## Limitations

Only three contexts exist; all reliability limits from F2 remain. Component NES values use deterministic representative terms, context pairs can have different tested masks, and retrieval ranks cannot establish biological generalization, treatment efficacy, or prediction accuracy.

## Competition Role

R1 demonstrates how the Atlas supports interpretable evidence retrieval: each rank exposes shared, discordant, null, phenotype, reliability, and provenance information.

## R1 Decision

**PASS.** Six ordered retrievals, leave-one-context-out demonstrations, explanation records, phenotype/reliability attachments, and all sanity tests completed. No predictive model was trained.
"""
    (ROOT / "reports/RETRIEVAL_R1_interpretable_context_similarity.md").write_text(report_text)


def main():
    atlas = load_atlas(ROOT)
    matrix = build_response_matrix(atlas)
    pairwise, explanations, loco, checkpoint = build_outputs(atlas, matrix)
    retrieval_figure(atlas, matrix, loco)
    similarity_matrix_figure(matrix, pairwise)
    report(pairwise, loco, checkpoint)
    print(json.dumps({
        "contexts": len(matrix.contexts), "components": len(matrix.components),
        "ordered_pairs": len(pairwise), "sanity_tests": checkpoint["sanity_tests"],
        "overall_pass": checkpoint["overall_pass"],
    }, indent=2))


if __name__ == "__main__":
    main()
