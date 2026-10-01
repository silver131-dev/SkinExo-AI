#!/usr/bin/env python3
"""Freeze EXP003-C4 interpretation and update three-context framework objects.

The component vocabulary comes unchanged from FRAMEWORK-F1. This script never
creates a new primary component and never alters frozen EXP001/EXP002 numerical
outputs or the original CTX001-vs-CTX002 comparison rows.
"""

from __future__ import annotations

import csv
import json
import os
import tempfile
from collections import defaultdict
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "skinexo_exp003_c4_finalize_mpl"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs/exp003"
META = ROOT / "data/metadata"
FIGURES = OUT / "figures"
REPORT = ROOT / "reports/EXP003_C4_third_context_pathway_test.md"
AXES = "PMEAI"
QUESTION = {"P": "Q1", "M": "Q2", "E": "Q3", "A": "Q4", "I": "Q5"}
AXIS_NAMES = {
    "P": "Proliferation / Cell Cycle", "M": "Migration / Motility",
    "E": "ECM Organization / Remodeling", "A": "Vascular / Endothelial Interaction",
    "I": "Inflammation / Immune Signaling",
}
THREE_INTERPRETATION = {
    "P": "NULL_NOT_TESTABLE", "M": "DISCORDANT", "E": "NULL_NOT_TESTABLE",
    "A": "DISCORDANT", "I": "CONSERVED_AXIS_CONTEXT_VARIANT",
}
PHENOTYPE = {
    "P": "FUNCTIONAL_ASSAY_24H_DIFFERENT_TIME",
    "M": "FUNCTIONAL_ASSAY_24H_DIFFERENT_TIME;IN_VIVO_DIFFERENT_MODEL",
    "E": "IN_VIVO_DIFFERENT_MODEL_ONLY",
    "A": "NONE_REGISTERED",
    "I": "NONE_REGISTERED",
}


def csv_rows(path: Path):
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_rows(path: Path, rows, fields):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def split_ids(value: str) -> list[str]:
    return [item for item in str(value).split(";") if item]


def component_direction(nes_values) -> str:
    values = sorted(float(value) for value in nes_values)
    if not values:
        return "INACTIVE"
    median = float(np.median(values))
    if median == 0 or (len(values) % 2 == 0 and np.sign(values[len(values)//2 - 1]) != np.sign(values[len(values)//2])):
        return "MIXED"
    return "POSITIVE" if median > 0 else "NEGATIVE"


def dominant(directions) -> str:
    nonmixed = [value for value in directions if value in {"POSITIVE", "NEGATIVE"}]
    if not nonmixed:
        return "MIXED"
    for direction in ("POSITIVE", "NEGATIVE"):
        if nonmixed.count(direction) / len(nonmixed) >= 2 / 3:
            return direction
    return "MIXED"


def response_direction(active_rows) -> str:
    if not active_rows:
        return "NO_QUALIFIED_COMPONENT"
    directions = [row["direction"] for row in active_rows]
    dom = dominant(directions)
    positive = "POSITIVE" in directions
    negative = "NEGATIVE" in directions
    if positive and negative:
        return f"{dom}_DOMINANT_WITH_OPPOSING_COMPONENTS" if dom != "MIXED" else "MIXED"
    return dom


def active_map(component_rows, context_id, axis):
    return {
        row["component_id"]: row["direction"]
        for row in component_rows
        if row["context_id"] == context_id and row["axis"] == axis and row["evidence_status"] == "QUALIFIED"
    }


def pair_state(first, second):
    if not first or not second:
        return {
            "prior_c4_status": "NOT_TESTABLE", "framework_state": "NULL_NOT_TESTABLE",
            "shared_component": "NONE", "same_direction": "NOT_TESTABLE",
        }
    shared = set(first) & set(second)
    shared_same = sorted(cid for cid in shared if first[cid] == second[cid] and first[cid] in {"POSITIVE", "NEGATIVE"})
    shared_opposite = sorted(cid for cid in shared if {first[cid], second[cid]} == {"POSITIVE", "NEGATIVE"})
    first_dom, second_dom = dominant(list(first.values())), dominant(list(second.values()))
    if shared_opposite or (first_dom in {"POSITIVE", "NEGATIVE"} and second_dom in {"POSITIVE", "NEGATIVE"} and first_dom != second_dom):
        return {
            "prior_c4_status": "DISCORDANT", "framework_state": "DISCORDANT",
            "shared_component": ";".join(f"{cid}_OPPOSITE_DIRECTION" for cid in shared_opposite) or "NONE",
            "same_direction": "NO",
        }
    if shared_same:
        return {
            "prior_c4_status": "PARTIALLY_CONCORDANT", "framework_state": "CONSERVED_COMPONENT",
            "shared_component": ";".join(shared_same), "same_direction": "YES_COMPONENT",
        }
    if first_dom == second_dom and first_dom in {"POSITIVE", "NEGATIVE"}:
        return {
            "prior_c4_status": "PARTIALLY_CONCORDANT", "framework_state": "CONSERVED_AXIS",
            "shared_component": "NONE", "same_direction": "YES_AXIS_ONLY",
        }
    return {
        "prior_c4_status": "CONTEXT_DEPENDENT", "framework_state": "CONTEXT_DEPENDENT",
        "shared_component": "NONE", "same_direction": "NO",
    }


def correlation(first, second):
    common = sorted(set(first.index) & set(second.index))
    x = first.loc[common, "NES"].astype(float)
    y = second.loc[common, "NES"].astype(float)
    return {
        "shared_gene_sets": len(common),
        "pearson": float(pearsonr(x, y).statistic),
        "spearman": float(spearmanr(x, y).statistic),
    }


def fmt_fdr(value):
    return "<0.001 (permutation estimate)" if float(value) == 0 else f"{float(value):.3g}"


def main():
    c2 = json.loads((OUT / "exp003_c2_qc.json").read_text())
    c3 = json.loads((OUT / "exp003_c3_de.json").read_text())
    manifest = json.loads((OUT / "c4_gene_set_manifest.json").read_text())
    if not (
        c2.get("decision") == "PASS_WITH_LIMITATIONS"
        and c3.get("decision") == "PASS_WITH_LIMITATIONS"
        and manifest.get("ranked_genes") == 13_874
        and manifest.get("tested_gene_sets") == 4_433
        and manifest.get("author_result_firewall", "").startswith("No author")
    ):
        raise RuntimeError("Frozen C2/C3 or complete enrichment output is inconsistent")

    gsea = pd.read_csv(OUT / "c4_gsea_all.csv")
    ora_up = pd.read_csv(OUT / "c4_ora_up_all.csv")
    ora_down = pd.read_csv(OUT / "c4_ora_down_all.csv")
    term_map = pd.read_csv(META / "skinexo_c4_term_map.csv")
    if len(gsea) != manifest["tested_gene_sets"] or set(gsea.database) != {"GO_BP", "Reactome", "Hallmark"}:
        raise RuntimeError("GSEA table does not cover the frozen collections")
    if len(ora_up) != len(gsea) or len(ora_down) != len(gsea):
        raise RuntimeError("ORA complete-table coverage differs from GSEA")

    old_components, component_fields = csv_rows(META / "skinexo_response_components.csv")
    base_components = [row for row in old_components if row["context_id"] in {"CTX001", "CTX002"}]
    template = [row for row in base_components if row["context_id"] == "CTX001"]
    if len(template) != 339 or {row["component_id"] for row in template} != {row["component_id"] for row in base_components if row["context_id"] == "CTX002"}:
        raise RuntimeError("F1 component vocabulary is not the frozen 339-component grid")
    gsea_by_term = gsea.set_index("term_id")
    ctx3_components = []
    component_median_nes = {}
    for row in template:
        evidence = []
        qualified = []
        qualified_nes = []
        for term_id in split_ids(row["mapped_term_ids"]):
            if term_id in gsea_by_term.index:
                result = gsea_by_term.loc[term_id]
                is_qualified = bool(result.FDR < .05 and result.leading_edge_coherent)
                evidence.append({
                    "term_id": term_id, "eligible": True,
                    "NES": float(result.NES), "FDR": float(result.FDR),
                    "leading_edge_n": int(result.leading_edge_n), "qualified": is_qualified,
                })
                if is_qualified:
                    qualified.append(term_id)
                    qualified_nes.append(float(result.NES))
            else:
                evidence.append({
                    "term_id": term_id, "eligible": False, "NES": None,
                    "FDR": None, "leading_edge_n": 0, "qualified": False,
                })
        direction = component_direction(qualified_nes)
        component_median_nes[("CTX003", row["component_id"])] = float(np.median(qualified_nes)) if qualified_nes else None
        ctx3_components.append({
            "component_entry_id": f"CTX003_{row['component_id']}",
            "component_id": row["component_id"], "context_id": "CTX003", "axis": row["axis"],
            "mapped_term_ids": row["mapped_term_ids"], "qualified_term_ids": ";".join(qualified),
            "direction": direction, "evidence_status": "QUALIFIED" if qualified else "OBSERVED_NULL",
            "term_evidence_json": json.dumps(evidence, separators=(",", ":")),
            "sensitivity_direction": "NOT_APPLICABLE", "sensitivity_qualified_term_ids": "",
            "evidence_layer": "TRANSCRIPTOME", "source_checkpoint": "EXP003-C4",
        })
    all_components = base_components + ctx3_components
    pd.DataFrame(ctx3_components).to_csv(OUT / "c4_ctx003_components.csv", index=False)

    axis_summary = {}
    for axis in AXES:
        entries = [row for row in ctx3_components if row["axis"] == axis]
        active = [row for row in entries if row["evidence_status"] == "QUALIFIED"]
        qualified_terms = sorted({term for row in active for term in split_ids(row["qualified_term_ids"])})
        mapped_ids = set(term_map.loc[term_map.question == QUESTION[axis], "term_id"])
        mapped_sig = gsea[gsea.term_id.isin(mapped_ids) & gsea.FDR.lt(.05)]
        mapped_qualified = mapped_sig[mapped_sig.leading_edge_coherent]
        ora_sig = ora_up[ora_up.term_id.isin(mapped_ids) & ora_up.FDR.lt(.05)]
        exemplar = None
        if qualified_terms:
            subset = gsea[gsea.term_id.isin(qualified_terms)].copy()
            subset["absNES"] = subset.NES.abs()
            exemplar = subset.sort_values(["FDR", "absNES", "term_id"], ascending=[True, False, True]).iloc[0]
        axis_summary[axis] = {
            "status": "QUALIFIED" if active else "OBSERVED_NULL",
            "direction": response_direction(active),
            "active_components": [row["component_id"] for row in active],
            "qualified_terms": qualified_terms,
            "representative_term_id": exemplar.term_id if exemplar is not None else "",
            "representative_NES": float(exemplar.NES) if exemplar is not None else None,
            "representative_FDR": float(exemplar.FDR) if exemplar is not None else None,
            "mapped_significant_gsea_terms": int(len(mapped_sig)),
            "mapped_qualified_gsea_terms": int(len(mapped_qualified)),
            "mapped_significant_ora_up_terms": int(len(ora_sig)),
        }

    expected_active = {
        "P": [], "M": ["M003", "M010", "M011", "M025"], "E": [],
        "A": ["A008"],
        "I": ["I004", "I008", "I009", "I012", "I015", "I025", "I041", "I043", "I044", "I076", "I080", "I093", "I102", "I108", "I111", "I112", "I114", "I115", "I116", "I117", "I118", "I123", "I131", "I136", "I142", "I144", "I145"],
    }
    if any(axis_summary[axis]["active_components"] != expected_active[axis] for axis in AXES):
        raise RuntimeError("CTX003 active components differ from the frozen-map result audit")

    # Three-context table uses the frozen EXP001/EXP002 components and new CTX003 entries.
    comparison_rows = []
    context_active = {context: {axis: active_map(all_components, context, axis) for axis in AXES}
                      for context in ("CTX001", "CTX002", "CTX003")}
    for axis in AXES:
        first, second, third = (context_active[context][axis] for context in ("CTX001", "CTX002", "CTX003"))
        shared_three = sorted(set(first) & set(second) & set(third))
        shared_three_same = [cid for cid in shared_three if first[cid] == second[cid] == third[cid] and first[cid] in {"POSITIVE", "NEGATIVE"}]
        if axis in {"P", "E"}:
            same_direction = "NOT_TESTABLE"
        elif axis in {"M", "A"}:
            same_direction = "NO"
        else:
            same_direction = "YES_AXIS_ONLY"
        comparison_rows.append({
            "axis": axis,
            "CTX001_state": response_direction([row for row in base_components if row["context_id"] == "CTX001" and row["axis"] == axis and row["evidence_status"] == "QUALIFIED"]),
            "CTX001_active_components": ";".join(first),
            "CTX002_state": response_direction([row for row in base_components if row["context_id"] == "CTX002" and row["axis"] == axis and row["evidence_status"] == "QUALIFIED"]),
            "CTX002_active_components": ";".join(second),
            "CTX003_state": axis_summary[axis]["direction"],
            "CTX003_active_components": ";".join(third),
            "shared_component_across_3": ";".join(shared_three_same) if shared_three_same else "NONE",
            "same_direction_across_3": same_direction,
            "phenotype_anchor_available": PHENOTYPE[axis],
            "three_context_interpretation": THREE_INTERPRETATION[axis],
            "reliability_notes": "Independent studies but recipient-donor and EV-preparation independence unresolved; CTX003 n=3/arm with unexplained PC1 structure; transcriptomic evidence is separate from phenotype anchors",
        })
    comparison_frame = pd.DataFrame(comparison_rows)
    comparison_frame.to_csv(OUT / "c4_three_context_comparison.csv", index=False)

    # Secondary global NES correlations and common three-way matrix.
    gsea_context = {
        "CTX001": pd.read_csv(ROOT / "outputs/exp001/c4_gsea_all.csv").set_index("term_id"),
        "CTX002": pd.read_csv(ROOT / "outputs/exp002/c4_gsea_primary_all.csv").set_index("term_id"),
        "CTX003": gsea.set_index("term_id"),
    }
    pairwise = {}
    pair_rows = []
    for first, second in (("CTX001", "CTX002"), ("CTX001", "CTX003"), ("CTX002", "CTX003")):
        metric = correlation(gsea_context[first], gsea_context[second])
        pairwise[f"{first}_vs_{second}"] = metric
        pair_rows.append({"context_a": first, "context_b": second, **metric, "evidence_role": "SECONDARY_DESCRIPTIVE"})
    pd.DataFrame(pair_rows).to_csv(OUT / "c4_pairwise_nes_correlations.csv", index=False)
    shared_all = sorted(set.intersection(*(set(frame.index) for frame in gsea_context.values())))
    shared_matrix = pd.DataFrame({
        "term_id": shared_all,
        "database": gsea_context["CTX001"].loc[shared_all, "database"].to_numpy(),
        **{context: gsea_context[context].loc[shared_all, "NES"].to_numpy() for context in gsea_context},
    })
    shared_matrix.to_csv(OUT / "c4_shared_nes_matrix.csv", index=False)

    # Pairwise framework comparison objects. Frozen CTX001-vs-CTX002 rows are retained byte-for-value.
    old_comparisons, comparison_fields = csv_rows(META / "skinexo_context_comparisons.csv")
    frozen_pair = [row for row in old_comparisons if row["context_a"] == "CTX001" and row["context_b"] == "CTX002"]
    if len(frozen_pair) != 5:
        raise RuntimeError("Frozen CTX001-vs-CTX002 comparison rows are missing")
    new_comparisons = []
    for first, second in (("CTX001", "CTX003"), ("CTX002", "CTX003")):
        for axis in AXES:
            state = pair_state(context_active[first][axis], context_active[second][axis])
            new_comparisons.append({
                "comparison_id": f"CMP_{first}_{second}_{axis}", "context_a": first, "context_b": second,
                "axis": axis, **state, "sensitivity_stable": "NOT_ASSESSED_CTX003",
                "phenotype_support": PHENOTYPE[axis] if second == "CTX003" else "NONE",
                "limitations": f"Component-aware transcriptomic comparison only; {first} and {second} differ in EV source"
                    + (" and exposure time" if first == "CTX002" else "")
                    + "; CTX003 n=3/arm, donor/EV-preparation independence UNKNOWN, unexplained PC1 structure; phenotype anchors remain separate evidence",
                "source_checkpoint": "EXP003-C4",
            })

    # Response objects for CTX003.
    response_rows, response_fields = csv_rows(META / "skinexo_responses.csv")
    gsea_lookup = gsea.set_index("term_id")
    for row in response_rows:
        if row["context_id"] != "CTX003":
            continue
        axis = row["axis"]
        summary = axis_summary[axis]
        leading = sorted({gene for term in summary["qualified_terms"] for gene in split_ids(str(gsea_lookup.loc[term, "leading_edge_genes"]))})
        row.update({
            "direction": summary["direction"], "evidence_status": summary["status"],
            "evidence_layer": "TRANSCRIPTOME", "primary_evidence_type": "GSEA_PRERANK",
            "representative_term_id": summary["representative_term_id"],
            "NES": "" if summary["representative_NES"] is None else str(summary["representative_NES"]),
            "FDR": "" if summary["representative_FDR"] is None else str(summary["representative_FDR"]),
            "key_terms": ";".join(summary["qualified_terms"]),
            "component_ids": ";".join(summary["active_components"]),
            "leading_edge_genes": ";".join(leading), "sensitivity_status": "NOT_APPLICABLE",
            "phenotype_anchor_status": PHENOTYPE[axis],
            "evidence_confidence": "QUALIFIED_WITH_DESIGN_LIMITATIONS" if summary["status"] == "QUALIFIED" else "OBSERVED_NULL_WITH_ADEQUATE_COVERAGE",
            "limitations": "Transcriptomic association only; n=3/arm; donor and EV-preparation independence UNKNOWN; batch/pairing/control medium UNKNOWN; unexplained PC1 structure; phenotype anchors are different-time or different-model evidence"
                + ("; vascular/endothelial evidence is not direct angiogenesis" if axis == "A" else "")
                + ("; secondary ORA cannot override null primary GSEA" if axis == "P" else ""),
            "source_checkpoint": "EXP003-C4",
        })

    # Promote context only after complete enrichment and interpretation.
    context_rows, context_fields = csv_rows(META / "skinexo_contexts.csv")
    for row in context_rows:
        if row["context_id"] == "CTX003":
            row.update({
                "study_status": "VERIFIED", "role": "EXP003", "data_status": "ANALYZED",
                "evidence_status": "FROZEN_C4", "batch_count": "UNKNOWN",
                "statistical_design": "DESeq2 ~ condition; CONTROL reference; no batch/pairing covariate; C2 PC1 structure unexplained",
                "major_limitations": "n=3/arm; RNA-seq control medium/vehicle UNKNOWN; recipient donor and EV-preparation independence UNKNOWN; batch and pairing UNKNOWN; unexplained replicate-label-associated PC1 structure; transcriptomic pathways do not establish phenotype; 103/13,874 tested IDs lack GENCODE v44 display symbols",
                "source_provenance": "data/metadata/GSE293956_samples.csv;reports/EXP003_D0_context_onboarding.md;reports/EXP003_C1_dataset_integrity.md;reports/EXP003_C2_sample_qc_analysis_plan.md;reports/EXP003_C3_differential_expression.md;reports/EXP003_C4_third_context_pathway_test.md;https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE293956",
            })

    # Reliability remains dimensional. Four new dimensions are added to all contexts so the grid stays rectangular.
    reliability_rows, reliability_fields = csv_rows(META / "skinexo_reliability.csv")
    reliability_rows = [row for row in reliability_rows if row["context_id"] != "CTX003"]
    source3 = "reports/EXP003_C1_dataset_integrity.md;reports/EXP003_C2_sample_qc_analysis_plan.md;reports/EXP003_C3_differential_expression.md;reports/EXP003_C4_third_context_pathway_test.md"
    ctx3_reliability = {
        "study_independence": ("VERIFIED", "Independent Liu study relative to CTX001 and CTX002; no sample reuse identified at D0"),
        "recipient_donor_independence": ("UNKNOWN", "Recipient donor count, pooling, and donor-to-library mapping unknown"),
        "ev_preparation_independence": ("UNKNOWN", "Independent EV preparation count and preparation-to-library mapping unknown"),
        "batch_adjustment": ("LIMITED", "No authoritative batch variable; primary model ~ condition; unexplained replicate-label-associated PC1 structure"),
        "sample_qc": ("LIMITED", "C1 passed and all six samples retained; C2 passed with unexplained dominant PC1 structure"),
        "sensitivity_stability": ("NOT_APPLICABLE", "No preregistered CTX003 sensitivity fit; no sample excluded"),
        "annotation_certainty": ("LIMITED", "MSigDB 2026.1.Hs hashes verified; GENCODE v44 symbols for 13,771/13,874 tested IDs; original count annotation release unknown"),
        "phenotype_support": ("LIMITED", "24 h hDF CCK-8/scratch anchors differ from 72 h RNA-seq; mouse outcomes are different-model IN_VIVO evidence"),
        "cross_context_replication": ("LIMITED", "I axis conserved with context-varying components; M/A discordant; P/E null for CTX003 primary GSEA"),
        "pairing_certainty": ("UNKNOWN", "No authoritative pairing; suffixes were not modeled as pairs"),
        "control_certainty": ("UNKNOWN", "Control-labeled hDF without recorded EV; exact medium and vehicle unknown"),
        "model_diagnostics": ("LIMITED", "DESeq2 converged with no Cook cutoff exceedance or NA p-values; unexplained PC1 remains"),
        "pathway_evidence": ("LIMITED", "4,433 sets tested; frozen component map applied; P/E observed null, M/A/I qualified with contextual limits"),
    }
    for dimension, (status, detail) in ctx3_reliability.items():
        reliability_rows.append({
            "reliability_id": f"REL_CTX003_{dimension.upper()}", "context_id": "CTX003",
            "dimension": dimension, "status": status, "detail": detail, "source_provenance": source3,
        })
    existing_keys = {(row["context_id"], row["dimension"]) for row in reliability_rows}
    additions = {
        "CTX001": {
            "pairing_certainty": ("UNKNOWN", "Pairing not documented in frozen EXP001 design"),
            "control_certainty": ("VERIFIED", "Control was exosome-depleted medium"),
            "model_diagnostics": ("LIMITED", "DESeq2 C3 passed; n=3/arm remains limiting"),
            "pathway_evidence": ("VERIFIED", "EXP001-C4 completed with frozen MSigDB release and term map"),
        },
        "CTX002": {
            "pairing_certainty": ("UNKNOWN", "No pairing term in frozen design"),
            "control_certainty": ("VERIFIED", "DMEM 1% Pen/Strep control documented"),
            "model_diagnostics": ("LIMITED", "Primary model adjusted batch; EV_8 retained with sensitivity analysis"),
            "pathway_evidence": ("LIMITED", "EXP002-C4 completed; one donor lot and transcript harmonization limits"),
        },
    }
    source_by_context = {
        "CTX001": "reports/EXP001_C3_differential_expression.md;reports/EXP001_C4_pathway_analysis.md",
        "CTX002": "reports/EXP002_C3_differential_expression.md;reports/EXP002_C4_cross_study_pathway_validation.md",
    }
    for context_id, facts in additions.items():
        for dimension, (status, detail) in facts.items():
            if (context_id, dimension) not in existing_keys:
                reliability_rows.append({
                    "reliability_id": f"REL_{context_id}_{dimension.upper()}", "context_id": context_id,
                    "dimension": dimension, "status": status, "detail": detail,
                    "source_provenance": source_by_context[context_id],
                })

    # Post-hoc results are identified mechanically and do not affect axes.
    frozen_ids = set(term_map.term_id)
    posthoc = gsea[gsea.FDR.lt(.05) & ~gsea.term_id.isin(frozen_ids)].copy()
    posthoc["absNES"] = posthoc.NES.abs()
    posthoc = posthoc.sort_values(["FDR", "absNES", "term_id"], ascending=[True, False, True])
    posthoc_records = [
        {"label": "POST_HOC_EXPLORATORY", "database": row.database, "term_id": row.term_id,
         "NES": float(row.NES), "FDR": float(row.FDR)}
        for row in posthoc.head(10).itertuples(index=False)
    ]

    # Figures are descriptive; phenotype text is visually separate from transcriptomic cells.
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(5, 1, figsize=(12, 14), sharex=True, constrained_layout=True)
    for ax, axis in zip(axes, AXES):
        active = axis_summary[axis]["active_components"]
        ax.axvline(0, color="#666666", linewidth=.8)
        if not active:
            ax.text(.5, .5, "No qualified frozen component", transform=ax.transAxes, ha="center", va="center", color="#555555")
            ax.set_yticks([])
        else:
            values = [component_median_nes[("CTX003", cid)] for cid in active]
            y = np.arange(len(active))
            colors = ["#c2573c" if value > 0 else "#2776ae" for value in values]
            ax.scatter(values, y, c=colors, s=38, edgecolor="white", linewidth=.4)
            ax.set_yticks(y, active, fontsize=7)
            ax.set_ylim(-.8, len(active)-.2)
        ax.set_ylabel(axis, rotation=0, labelpad=18, fontweight="bold")
        ax.set_title(f"{axis} — {AXIS_NAMES[axis]} · {len(active)} active component(s)", fontsize=10, loc="left")
    axes[-1].set_xlabel("Median NES of qualified terms within component (positive = hDF-EV higher)")
    fig.suptitle("CTX003 prespecified P/M/E/A/I component evidence", fontsize=14)
    fig.savefig(FIGURES / "fig07_ctx003_prespecified_axes.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(15, 8.5))
    ax.set_xlim(0, 3); ax.set_ylim(0, 5); ax.invert_yaxis(); ax.axis("off")
    contexts = ["CTX001", "CTX002", "CTX003"]
    for col, context in enumerate(contexts):
        ax.text(col + .5, -.18, context, ha="center", va="center", fontsize=12, fontweight="bold")
    for row_index, axis in enumerate(AXES):
        ax.text(-.06, row_index + .5, axis, ha="right", va="center", fontsize=12, fontweight="bold")
        for col, context in enumerate(contexts):
            active = context_active[context][axis]
            dom = dominant(list(active.values())) if active else "INACTIVE"
            face = {"POSITIVE": "#f3b4a5", "NEGATIVE": "#a8c9e5", "MIXED": "#d8c1e6", "INACTIVE": "#e5e5e5"}[dom]
            rect = plt.Rectangle((col+.03, row_index+.06), .94, .88, facecolor=face, edgecolor="white")
            ax.add_patch(rect)
            ids = sorted(active)
            if len(ids) <= 5:
                component_text = ", ".join(ids) if ids else "observed null"
            else:
                component_text = f"{len(ids)} active\n" + ", ".join(ids[:4]) + ", …"
            ax.text(col+.5, row_index+.43, f"{dom}\n{component_text}", ha="center", va="center", fontsize=7.2)
            if context == "CTX003" and PHENOTYPE[axis] != "NONE_REGISTERED":
                anchor = "24 h assay anchor" if axis in "PM" else "mouse IN_VIVO anchor"
                ax.text(col+.5, row_index+.83, anchor, ha="center", va="center", fontsize=6.5, color="#6a3d78")
    fig.suptitle("Three-context axis and component comparison\nTranscriptomic cells; phenotype anchors shown as separate text", fontsize=14)
    fig.savefig(FIGURES / "fig08_three_context_axis_comparison.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    corr_matrix = shared_matrix[["CTX001", "CTX002", "CTX003"]].corr(method="pearson")
    fig, ax = plt.subplots(figsize=(7.5, 6.4), constrained_layout=True)
    image = ax.imshow(corr_matrix, vmin=-1, vmax=1, cmap="RdBu_r")
    ax.set_xticks(range(3), corr_matrix.columns)
    ax.set_yticks(range(3), corr_matrix.index)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{corr_matrix.iloc[i,j]:+.3f}", ha="center", va="center", fontsize=11)
    fig.colorbar(image, ax=ax, label="Pearson correlation of shared GSEA NES")
    ax.set_title(f"Three-context response map · {len(shared_all):,} gene sets shared across all contexts\nSecondary descriptive evidence")
    fig.savefig(FIGURES / "fig09_three_context_response_map.png", dpi=180)
    plt.close(fig)

    reliability_limits = [
        "n=3 per condition in CTX003", "recipient donor count UNKNOWN", "EV preparation count UNKNOWN",
        "pairing UNKNOWN", "batch NOT_DOCUMENTED", "control medium/vehicle UNKNOWN",
        "unexplained dominant replicate-label-associated PC1 structure",
        "no Cook cutoff exceedances or convergence failures", "GSEA permutations do not capture sample-label uncertainty",
        "phenotype anchors differ in time or model and do not set transcriptomic significance",
    ]
    phenotype_summary = {
        "P": "hDF CCK-8 at 24 h; same source/recipient, different time from 72 h RNA-seq",
        "M": "hDF scratch assay at 24 h; same source/recipient, different time; mouse wound closure is a different-model IN_VIVO layer",
        "E": "Mouse scar length and collagen deposition are different-model IN_VIVO evidence",
        "A": "No direct angiogenesis phenotype anchor registered",
        "I": "No direct CTX003 inflammatory phenotype anchor registered",
    }
    checkpoint = {
        "dataset": "GSE293956", "context_id": "CTX003", "gene_set_release": "MSigDB 2026.1.Hs",
        "ranked_genes": manifest["ranked_genes"],
        "mapping_loss": {
            "genes_without_verified_symbol": manifest["genes_without_verified_symbol"],
            "genes_absent_all_gene_sets": manifest["genes_absent_all_gene_sets"],
            "duplicate_symbol_groups": manifest["duplicate_symbol_groups"],
            "gene_ids_in_duplicate_symbol_groups": manifest["gene_ids_in_duplicate_symbol_groups"],
        },
        "tested_gene_sets": manifest["tested_gene_sets"],
        "significant_gene_sets": manifest["gsea_FDR_lt_0_05"],
        "qualified_gene_sets": manifest["gsea_qualified_FDR_coherent"],
        "ora_up_significant_gene_sets": manifest["ora_up_FDR_lt_0_05"],
        "ora_down_significant_gene_sets": manifest["ora_down_FDR_lt_0_05"],
        **{f"{axis}_status": axis_summary[axis]["status"] for axis in AXES},
        **{f"{axis}_direction": axis_summary[axis]["direction"] for axis in AXES},
        **{f"{axis}_components": axis_summary[axis]["active_components"] for axis in AXES},
        **{f"{axis}_three_context_interpretation": THREE_INTERPRETATION[axis] for axis in AXES},
        "P_validation_endpoint": "TWO_CONTEXT_ONLY; CTX003 primary GSEA observed null; secondary ORA cannot override",
        "phenotype_anchor_summary": phenotype_summary,
        "pairwise_NES_correlations": pairwise,
        "three_way_shared_gene_sets": len(shared_all),
        "reliability_limitations": reliability_limits,
        "post_hoc_findings": {"significant_unmapped_term_count": len(posthoc), "top_10": posthoc_records},
        "broad_universal_ev_response": "NOT_SUPPORTED",
        "key_context_aware_finding": "CTX003 does not extend the two-context P conserved-component candidate; it adds positive chemotaxis/migration and endothelial-apoptosis components that preserve M/A discordance, while its inflammatory response shares exact components with CTX002 and broad axis direction with both prior contexts.",
        "framework_update_status": "UPDATED",
        "overall_pass": True,
        "decision": "PASS_WITH_LIMITATIONS",
    }

    # Report is generated before metadata writes but describes the exact frozen objects above.
    def component_text(axis):
        values = axis_summary[axis]["active_components"]
        return ", ".join(values) if values else "None"

    def qualified_term_lines(axis, maximum=12):
        terms = axis_summary[axis]["qualified_terms"]
        if not terms:
            return "- No frozen mapped term met FDR < 0.05 plus the leading-edge coherence rule."
        subset = gsea[gsea.term_id.isin(terms)].sort_values(["FDR", "term_id"]).head(maximum)
        return "\n".join(
            f"- `{row.term_id}`: NES {row.NES:+.3f}, FDR {fmt_fdr(row.FDR)}, "
            f"component {next(x['component_id'] for x in ctx3_components if x['axis'] == axis and row.term_id in split_ids(x['qualified_term_ids']))}."
            for row in subset.itertuples()
        )

    corr_lines = "\n".join(
        f"- {key.replace('_vs_', ' vs ')}: n={value['shared_gene_sets']:,}, Pearson {value['pearson']:+.4f}, Spearman {value['spearman']:+.4f}."
        for key, value in pairwise.items()
    )
    report = f"""# SkinExo-AI EXP003-C4

## Objective

Apply the prospectively frozen pathway analysis to CTX003 and determine how a third independent EV-study context changes the component-aware SkinExo interpretation. GSEA is primary, ORA is secondary, phenotype anchors remain a separate evidence layer, and the framework retains null and discordant findings.

## Why CTX003 Is a Third Context

CTX003 is GSE293956: human dermal fibroblast-derived EV at 10 ug/mL applied to primary human dermal fibroblasts for 72 h. CTX001 uses endothelial-cell EV at 72 h; CTX002 uses bone-marrow MSC small EV at 48 h. The studies, EV sources, doses, and exposure settings differ. CTX003 is independent at study level, while donor and EV-preparation independence remain unknown.

## Frozen Analysis Plan

C2 and C3 are **PASS WITH LIMITATIONS**. C4 used all 13,874 C3-tested genes ranked by signed DESeq2 Wald statistic. It did not change the C2 filter, C3 model, threshold B, P/M/E/A/I map, component vocabulary, or qualification rule. Author pathway findings were not consulted.

## GSEA Methods

The exact MSigDB **2026.1.Hs** GO Biological Process, Reactome, and Hallmark GMT files used for EXP001/EXP002 were reused with verified SHA-256 hashes. GSEApy 1.3.1 prerank used weight 1, 1,000 gene-set permutations, seed 42, and the 15–500 tested-gene effective-size rule in one combined run. A term qualifies for components when FDR < 0.05, its leading edge has at least five genes, and at least 80% of leading-edge Wald statistics agree with NES sign.

Verified symbols were available for 13,771/13,874 tested IDs. The 103 missing-symbol IDs remain in the ranked universe but cannot enter symbol-defined sets. Duplicate symbols map to every matching stable gene ID. [Ranked genes](../outputs/exp003/c4_ranked_genes.csv); [complete GSEA](../outputs/exp003/c4_gsea_all.csv).

## CTX003 Global GSEA

- Tested gene sets: **{manifest['tested_gene_sets']:,}**.
- FDR < 0.05: **{manifest['gsea_FDR_lt_0_05']:,}**.
- FDR < 0.05 with coherent leading edge: **{manifest['gsea_qualified_FDR_coherent']:,}**.
- Secondary ORA FDR < 0.05: **{manifest['ora_up_FDR_lt_0_05']} UP**, **{manifest['ora_down_FDR_lt_0_05']} DOWN**.

ORA uses only 20 threshold-B UP genes and zero DOWN genes, so it has limited power. It cannot override ranked GSEA. {len(posthoc)} significant GSEA terms fall outside the frozen P/M/E/A/I map; they are retained as `POST_HOC_EXPLORATORY` and do not determine primary endpoints.

## P — Proliferation / Cell Cycle

**CTX003: OBSERVED_NULL / NO_QUALIFIED_COMPONENT.** Active components: **None**. No frozen P term met primary GSEA FDR and coherence criteria. Secondary ORA found three epithelial-proliferation terms, but the preregistered hierarchy keeps the GSEA endpoint null.

The previously shared CTX001/CTX002 component `P081` is not active in CTX003. The candidate conserved component therefore remains **two-context only**; the three-context table records `NULL_NOT_TESTABLE`. Transcriptomics does not establish proliferation.

## M — Migration / Motility

**CTX003: QUALIFIED, POSITIVE.** Active components: **{component_text('M')}**.

{qualified_term_lines('M')}

CTX003 directly opposes CTX001 at components `M003` and `M025`. It shares a positive broad-axis direction with CTX002 but no exact active M component. The three-context interpretation remains **DISCORDANT**. The 24 h scratch assay is a separate functional anchor and does not set 72 h GSEA significance.

## E — ECM Organization / Remodeling

**CTX003: OBSERVED_NULL / NO_QUALIFIED_COMPONENT.** Active components: **None**. No frozen E term met primary GSEA or secondary ORA FDR criteria. With CTX002 also null and CTX001 carrying the only qualified E components, the three-context endpoint remains **NULL_NOT_TESTABLE**. Mouse scar and collagen outcomes remain separate `IN_VIVO` evidence and do not establish a fibroblast ECM transcriptomic phenotype.

## A — Vascular / Endothelial Interaction

**CTX003: QUALIFIED, POSITIVE.** Active component: **A008**.

{qualified_term_lines('A')}

`A008` is negative in CTX001 and positive in CTX003, a direct component-level discordance. CTX003 broadly aligns with positive CTX002 A-axis activity through different components. The three-context interpretation is **DISCORDANT**. Endothelial-apoptosis transcriptional association is not angiogenesis, neovascularization, or therapeutic vascular benefit.

## I — Inflammation / Immune Signaling

**CTX003: QUALIFIED, POSITIVE.** Active components: **{component_text('I')}**.

Top frozen qualified terms:

{qualified_term_lines('I')}

CTX003 shares nine positive components with CTX002: `I111`, `I114`, `I115`, `I116`, `I117`, `I118`, `I131`, `I136`, and `I144`. It shares no exact active I component with CTX001, although all three contexts have positive-dominant I-axis activity. The result is **CONSERVED_AXIS_CONTEXT_VARIANT**: component-level recurrence for CTX002/CTX003 and broad thematic overlap only with CTX001. It is not a universal positive inflammatory label.

## Phenotype Anchors

- P: author-reported hDF CCK-8 at 24 h; same EV source/recipient, different time from 72 h RNA-seq.
- M: author-reported hDF scratch assay at 24 h; same EV source/recipient, different time.
- Mouse wound closure, scar length, and collagen deposition: different species/model `IN_VIVO` evidence.
- No phenotype anchor changes a GSEA FDR, component direction, or null result.

## CTX001 vs CTX003

P and E are `NULL_NOT_TESTABLE` because CTX003 has no qualified component. M is `DISCORDANT` through opposite `M003`/`M025`; A is `DISCORDANT` through opposite `A008`; I is `CONSERVED_AXIS` with different active components.

## CTX002 vs CTX003

P and E are `NULL_NOT_TESTABLE`. M and A are `CONSERVED_AXIS` through positive but different components. I is `CONSERVED_COMPONENT` through nine exact positive components. These pairwise states remain bounded to their observed contexts.

## Three-Context Interpretation

| Axis | CTX003 state | Active CTX003 components | Three-context interpretation |
| --- | --- | --- | --- |
| P | Observed null | None | NULL_NOT_TESTABLE; P081 remains two-context only |
| M | Positive | {component_text('M')} | DISCORDANT |
| E | Observed null | None | NULL_NOT_TESTABLE |
| A | Positive | A008 | DISCORDANT |
| I | Positive | {component_text('I')} | CONSERVED_AXIS_CONTEXT_VARIANT |

Across three contexts, selected response components show reproducible or context-dependent patterns. A broad universal EV response is **not supported**.

## Global NES Similarity

Secondary descriptive correlations over pairwise shared eligible gene sets:

{corr_lines}

The correlations are weak, with CTX001 negatively related to both later contexts and CTX002/CTX003 weakly positive. They do not determine axis endpoints and are not machine learning or retrieval performance. [Three-context response map](../outputs/exp003/figures/fig09_three_context_response_map.png).

## Reliability

CTX003 has n=3 per condition; donor count, EV-preparation count, pairing, and exact control medium/vehicle are unknown; batch is not documented; the dominant replicate-label-associated PC1 structure remains unexplained. C3 had no convergence failure, Cook cutoff exceedance, or missing p-value, but those diagnostics do not resolve design metadata. Gene-set permutations do not represent sample-label uncertainty. Phenotype anchors differ in time or model.

## Claim Boundaries

This analysis does not establish a universal EV response, therapeutic efficacy, independent-donor replication, EV-preparation-level replication, causal cargo-response mechanisms, human wound-healing efficacy, or angiogenic activity. GSE293957 was not analyzed. No fourth transcriptomic context, retrieval system, or predictive model was added.

## C4 Decision

**PASS WITH LIMITATIONS.** The frozen ranking, gene-set release, GSEA workflow, component map, and third-context endpoints executed completely. The framework was updated only after interpretation was frozen. Reliability limits remain material, null results remain explicit, and the broad five-axis universal-response hypothesis remains unsupported.
"""
    REPORT.write_text(report)
    (OUT / "exp003_c4_pathways.json").write_text(json.dumps(checkpoint, indent=2) + "\n")

    # Metadata writes are last so a failure above leaves the F1 framework untouched.
    write_rows(META / "skinexo_response_components.csv", all_components, component_fields)
    write_rows(META / "skinexo_responses.csv", response_rows, response_fields)
    write_rows(META / "skinexo_context_comparisons.csv", frozen_pair + new_comparisons, comparison_fields)
    write_rows(META / "skinexo_contexts.csv", context_rows, context_fields)
    write_rows(META / "skinexo_reliability.csv", reliability_rows, reliability_fields)

    print(json.dumps({
        "axes": {axis: {"status": axis_summary[axis]["status"], "direction": axis_summary[axis]["direction"],
                         "components": axis_summary[axis]["active_components"],
                         "three_context": THREE_INTERPRETATION[axis]} for axis in AXES},
        "pairwise_NES": pairwise, "framework_rows": {
            "components": len(all_components), "responses": len(response_rows),
            "comparisons": len(frozen_pair + new_comparisons), "reliability": len(reliability_rows),
        }, "decision": checkpoint["decision"],
    }, indent=2))


if __name__ == "__main__":
    main()
