#!/usr/bin/env python3
"""Build the F2 three-context response atlas from frozen C4 registries.

This script performs no differential expression or enrichment. It transforms
the verified F1/EXP003-C4 metadata into a stable component universe, long and
wide response representations, axis summaries, a manifest, report, and two
competition figures.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "skinexo_f2_mpl"))
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle


ROOT = Path(__file__).resolve().parents[2]
META = ROOT / "data/metadata"
OUT = ROOT / "outputs/framework"
SUBFIG = ROOT / "submission/figures"
ATLAS_VERSION = "F2-2026-10-01"
AXES = "PMEAI"
AXIS_NAMES = {
    "P": "Proliferation / Cell Cycle",
    "M": "Migration / Motility",
    "E": "ECM Organization / Remodeling",
    "A": "Vascular / Endothelial Interaction",
    "I": "Inflammation / Immune Signaling",
}
ACTIVITY_STATES = {"ACTIVE_POSITIVE", "ACTIVE_NEGATIVE", "OBSERVED_NULL", "NOT_TESTED", "UNKNOWN"}
INTERPRETATIONS = {
    "P": "TWO_CONTEXT_SHARED_COMPONENT",
    "M": "CONTEXT_DEPENDENT_DISCORDANT",
    "E": "NULL_NOT_TESTABLE",
    "A": "CONTEXT_DEPENDENT_DISCORDANT",
    "I": "CONSERVED_AXIS_CONTEXT_VARIANT",
}


def read_csv(path: Path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def split(value):
    return [item for item in str(value).split(";") if item]


def sha256(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def representative(component):
    evidence = json.loads(component["term_evidence_json"])
    tested = [
        item for item in evidence
        if item.get("eligible", True) and item.get("NES") is not None and item.get("FDR") is not None
    ]
    if not tested:
        return None
    qualified = [item for item in tested if item.get("qualified")]
    candidates = qualified or tested
    return sorted(candidates, key=lambda item: (float(item["FDR"]), -abs(float(item["NES"])), item["term_id"]))[0]


def activity_state(component, rep):
    if rep is None:
        return "NOT_TESTED"
    if component["evidence_status"] == "OBSERVED_NULL":
        return "OBSERVED_NULL"
    if component["evidence_status"] != "QUALIFIED":
        return "UNKNOWN"
    if component["direction"] == "POSITIVE":
        return "ACTIVE_POSITIVE"
    if component["direction"] == "NEGATIVE":
        return "ACTIVE_NEGATIVE"
    raise RuntimeError(f"Unsupported qualified direction: {component['component_entry_id']}")


def source_checkpoint_provenance(checkpoint):
    return {
        "EXP001-C4": "reports/EXP001_C4_pathway_analysis.md",
        "EXP002-C4": "reports/EXP002_C4_cross_study_pathway_validation.md",
        "EXP003-C4": "reports/EXP003_C4_third_context_pathway_test.md",
    }[checkpoint]


def build_atlas():
    contexts = read_csv(META / "skinexo_contexts.csv")
    components = read_csv(META / "skinexo_response_components.csv")
    responses = read_csv(META / "skinexo_responses.csv")
    anchors = read_csv(META / "skinexo_phenotype_anchors.csv")
    reliability = read_csv(META / "skinexo_reliability.csv")
    term_map = read_csv(META / "skinexo_c4_term_map.csv")
    correlations = read_csv(ROOT / "outputs/exp003/c4_pairwise_nes_correlations.csv")
    if len(contexts) != 3 or any(row["study_status"] != "VERIFIED" for row in contexts):
        raise RuntimeError("F2 requires exactly three verified contexts")
    if len(components) != 1017:
        raise RuntimeError("Frozen three-context component grid is incomplete")

    term_lookup = {row["term_id"]: row for row in term_map}
    templates = sorted(
        (row for row in components if row["context_id"] == "CTX001"),
        key=lambda row: (AXES.index(row["axis"]), row["component_id"]),
    )
    if len(templates) != 339:
        raise RuntimeError("Expected 339 frozen components")

    universe = []
    for row in templates:
        term_ids = split(row["mapped_term_ids"])
        missing = [term for term in term_ids if term not in term_lookup]
        if missing:
            raise RuntimeError(f"Component {row['component_id']} has unmapped terms: {missing}")
        term_names = [term_lookup[term]["term_name"] for term in term_ids]
        databases = []
        for term in term_ids:
            database = term_lookup[term]["database"]
            if database not in databases:
                databases.append(database)
        component_name = term_names[0] if len(term_names) == 1 else f"{term_names[0]} component cluster ({len(term_names)} mapped terms)"
        universe.append({
            "component_id": row["component_id"], "axis": row["axis"],
            "component_name": component_name,
            "source_database": ";".join(databases),
            "source_term_id": ";".join(term_ids),
            "source_term_name": ";".join(term_names),
            "definition": "Frozen source-membership component; mapped terms remain distinct evidence and are not independent confirmations",
            "status": "FROZEN_F2",
        })
    write_csv(META / "skinexo_component_universe.csv", universe, list(universe[0]))

    reliability_by_context = defaultdict(list)
    for row in reliability:
        reliability_by_context[row["context_id"]].append(row["reliability_id"])
    anchors_by_context_axis = defaultdict(list)
    for row in anchors:
        anchors_by_context_axis[(row["context_id"], row["axis"])].append(row["anchor_id"])

    long_rows = []
    long_by_key = {}
    for component in sorted(components, key=lambda row: (row["context_id"], row["component_id"])):
        rep = representative(component)
        state = activity_state(component, rep)
        direction = {
            "ACTIVE_POSITIVE": "POSITIVE", "ACTIVE_NEGATIVE": "NEGATIVE",
            "OBSERVED_NULL": "INACTIVE", "NOT_TESTED": "NOT_TESTED", "UNKNOWN": "UNKNOWN",
        }[state]
        phenotype_ids = sorted(anchors_by_context_axis[(component["context_id"], component["axis"])])
        row = {
            "context_id": component["context_id"], "axis": component["axis"],
            "component_id": component["component_id"], "direction": direction,
            "NES": "" if rep is None else repr(float(rep["NES"])),
            "FDR": "" if rep is None else repr(float(rep["FDR"])),
            "representative_term_id": "" if rep is None else rep["term_id"],
            "activity_state": state,
            "tested_mask": "0" if rep is None else "1",
            "active_mask": "1" if state.startswith("ACTIVE_") else "0",
            "evidence_layer": component["evidence_layer"],
            "phenotype_anchor": ";".join(phenotype_ids),
            "sensitivity_status": component["sensitivity_direction"],
            "reliability_reference": ";".join(sorted(reliability_by_context[component["context_id"]])),
            "source_checkpoint": component["source_checkpoint"],
            "provenance": f"data/metadata/skinexo_response_components.csv;{source_checkpoint_provenance(component['source_checkpoint'])}",
        }
        long_rows.append(row)
        long_by_key[(row["context_id"], row["component_id"])] = row
    long_fields = [
        "context_id", "axis", "component_id", "direction", "NES", "FDR",
        "representative_term_id", "activity_state", "tested_mask", "active_mask",
        "evidence_layer", "phenotype_anchor", "sensitivity_status",
        "reliability_reference", "source_checkpoint", "provenance",
    ]
    write_csv(META / "skinexo_response_atlas_long.csv", long_rows, long_fields)

    matrix_rows = []
    component_ids = [row["component_id"] for row in universe]
    for context in sorted(row["context_id"] for row in contexts):
        matrix_row = {"context_id": context}
        for component_id in component_ids:
            row = long_by_key[(context, component_id)]
            matrix_row[component_id] = json.dumps({
                "activity_state": row["activity_state"], "direction": row["direction"],
                "NES": None if row["NES"] == "" else float(row["NES"]),
                "FDR": None if row["FDR"] == "" else float(row["FDR"]),
                "tested_mask": int(row["tested_mask"]), "active_mask": int(row["active_mask"]),
            }, separators=(",", ":"))
        matrix_rows.append(matrix_row)
    write_csv(META / "skinexo_response_matrix.csv", matrix_rows, ["context_id"] + component_ids)

    reliability_lookup = {(row["context_id"], row["dimension"]): row for row in reliability}
    category = {
        "CTX001": ("endothelial-cell-derived EV", "ENDOTHELIAL_CELL"),
        "CTX002": ("human bone-marrow MSC small EV", "BONE_MARROW_MSC"),
        "CTX003": ("human dermal fibroblast-derived EV", "DERMAL_FIBROBLAST"),
    }
    batch = {"CTX001": "UNKNOWN", "CTX002": "DOCUMENTED_2_BATCHES_ADJUSTED", "CTX003": "NOT_DOCUMENTED"}
    pairing = {"CTX001": "UNKNOWN", "CTX002": "UNKNOWN", "CTX003": "NO_EVIDENCE"}
    feature_rows = []
    for row in sorted(contexts, key=lambda item: item["context_id"]):
        context = row["context_id"]
        donor = reliability_lookup[(context, "recipient_donor_independence")]
        preparation = reliability_lookup[(context, "ev_preparation_independence")]
        feature_rows.append({
            "context_id": context, "dataset_id": row["dataset_id"],
            "ev_source": category[context][0], "ev_source_category": category[context][1],
            "recipient": row["recipient_cell"], "recipient_category": "HUMAN_DERMAL_FIBROBLAST",
            "species": row["species"], "dose": row["dose"], "duration_h": row["duration_h"],
            "experimental_system": row["experimental_system"], "sample_count": row["sample_count"],
            "treatment_n": row["treatment_n"], "control_n": row["control_n"],
            "donor_status": f"{donor['status']}: {donor['detail']}",
            "ev_preparation_status": f"{preparation['status']}: {preparation['detail']}",
            "batch_status": batch[context], "pairing_status": pairing[context],
            "omics_type": row["omics_type"], "phenotype_available": row["phenotype_available"],
            "cargo_available": row["cargo_data_available"],
            "study_independence": reliability_lookup[(context, "study_independence")]["status"],
            "data_status": row["data_status"], "major_limitations": row["major_limitations"],
        })
    write_csv(META / "skinexo_context_features.csv", feature_rows, list(feature_rows[0]))

    response_by_key = {(row["context_id"], row["axis"]): row for row in responses}
    axis_rows = []
    for context in sorted(row["context_id"] for row in contexts):
        for axis in AXES:
            records = [row for row in long_rows if row["context_id"] == context and row["axis"] == axis]
            positive = [row for row in records if row["activity_state"] == "ACTIVE_POSITIVE"]
            negative = [row for row in records if row["activity_state"] == "ACTIVE_NEGATIVE"]
            strongest_positive = max(positive, key=lambda row: float(row["NES"]))["component_id"] if positive else "NONE"
            strongest_negative = min(negative, key=lambda row: float(row["NES"]))["component_id"] if negative else "NONE"
            response = response_by_key[(context, axis)]
            axis_rows.append({
                "context_id": context, "axis": axis, "axis_status": response["direction"],
                "active_component_count": len(positive) + len(negative),
                "positive_component_count": len(positive), "negative_component_count": len(negative),
                "strongest_positive_component": strongest_positive,
                "strongest_negative_component": strongest_negative,
                "phenotype_anchor_count": len(anchors_by_context_axis[(context, axis)]),
                "reliability_notes": next(item["major_limitations"] for item in contexts if item["context_id"] == context),
                "source_checkpoint": response["source_checkpoint"],
            })
    write_csv(META / "skinexo_axis_summary.csv", axis_rows, list(axis_rows[0]))

    counts = Counter(row["activity_state"] for row in long_rows)
    correlation_json = {
        f"{row['context_a']}_vs_{row['context_b']}": {
            "shared_gene_sets": int(row["shared_gene_sets"]),
            "pearson": float(row["pearson"]), "spearman": float(row["spearman"]),
            "role": "SECONDARY_DESCRIPTIVE",
        } for row in correlations
    }
    manifest = {
        "framework_version": "F2", "atlas_version": ATLAS_VERSION,
        "component_universe_version": ATLAS_VERSION,
        "contexts": 3, "verified_contexts": 3, "axes": 5,
        "component_count": len(universe), "response_records": len(long_rows),
        "tested_response_records": sum(row["tested_mask"] == "1" for row in long_rows),
        "active_response_records": counts["ACTIVE_POSITIVE"] + counts["ACTIVE_NEGATIVE"],
        "observed_null_records": counts["OBSERVED_NULL"],
        "not_tested_records": counts["NOT_TESTED"], "unknown_records": counts["UNKNOWN"],
        "activity_states": sorted(ACTIVITY_STATES),
        "phenotype_anchor_count": len(anchors), "reliability_record_count": len(reliability),
        "global_NES_correlations": correlation_json,
        "broad_universal_EV_response": "NOT_SUPPORTED",
        "P_interpretation": INTERPRETATIONS["P"], "M_interpretation": INTERPRETATIONS["M"],
        "E_interpretation": INTERPRETATIONS["E"], "A_interpretation": INTERPRETATIONS["A"],
        "I_interpretation": INTERPRETATIONS["I"],
        "response_representation": "READY", "retrieval_ready": True,
        "retrieval_status": "NOT_IMPLEMENTED", "explorer_status": "NOT_IMPLEMENTED",
        "predictive_AI_status": "NOT_IMPLEMENTED",
        "source_hashes": {
            "contexts": sha256(META / "skinexo_contexts.csv"),
            "components": sha256(META / "skinexo_response_components.csv"),
            "responses": sha256(META / "skinexo_responses.csv"),
            "reliability": sha256(META / "skinexo_reliability.csv"),
        },
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "framework_f2_atlas.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return contexts, universe, long_rows, axis_rows, anchors, reliability, manifest


def atlas_figure(contexts, long_rows, axis_rows, anchors):
    SUBFIG.mkdir(parents=True, exist_ok=True)
    context_ids = ["CTX001", "CTX002", "CTX003"]
    context_subtitles = {
        "CTX001": "Endothelial EV · 72 h",
        "CTX002": "Bone-marrow MSC sEV · 48 h",
        "CTX003": "Dermal fibroblast EV · 72 h",
    }
    colors = {"POSITIVE": "#F1A58F", "NEGATIVE": "#94BDE0", "NULL": "#D9DDE2", "MIXED": "#E7C878"}
    axis_lookup = {(row["context_id"], row["axis"]): row for row in axis_rows}
    anchors_lookup = defaultdict(list)
    for row in anchors:
        anchors_lookup[(row["context_id"], row["axis"])].append(row)
    fig, ax = plt.subplots(figsize=(16, 10.5), constrained_layout=True)
    ax.set_xlim(0, 3.6); ax.set_ylim(0, 6.2); ax.axis("off")
    fig.suptitle("SkinExo-AI Three-Context Response Atlas", fontsize=23, fontweight="bold")
    ax.text(1.8, 6.05, "Same recipient: human dermal fibroblast · different EV sources and exposure contexts",
            ha="center", fontsize=13, color="#384554")
    for j, context in enumerate(context_ids):
        x = 0.55 + j
        ax.text(x + .45, 5.74, context, ha="center", fontsize=16, fontweight="bold")
        ax.text(x + .45, 5.52, context_subtitles[context], ha="center", fontsize=10.5)
        ax.text(x + .45, 5.25, "study independent · donor/preparation limits", ha="center", fontsize=8.8, color="#9A6500")
    for i, axis in enumerate(AXES):
        y = 4.43 - i * .84
        ax.text(.08, y + .34, axis, fontsize=17, fontweight="bold", va="center")
        ax.text(.08, y + .13, AXIS_NAMES[axis], fontsize=8.4, va="center", color="#455465")
        for j, context in enumerate(context_ids):
            x = .55 + j
            summary = axis_lookup[(context, axis)]
            status = summary["axis_status"]
            if status == "NO_QUALIFIED_COMPONENT": color, label = colors["NULL"], "OBSERVED NULL"
            elif status.startswith("POSITIVE"): color, label = colors["POSITIVE"], "POSITIVE DOMINANT\n+ OPPOSING" if "OPPOSING" in status else "POSITIVE"
            elif status.startswith("NEGATIVE"): color, label = colors["NEGATIVE"], "NEGATIVE DOMINANT\n+ OPPOSING" if "OPPOSING" in status else "NEGATIVE"
            else: color, label = colors["MIXED"], "MIXED"
            ax.add_patch(Rectangle((x, y), .9, .72, facecolor=color, edgecolor="white", linewidth=2))
            active = [row["component_id"] for row in long_rows if row["context_id"] == context and row["axis"] == axis and row["active_mask"] == "1"]
            component_text = "none" if not active else ", ".join(active[:4]) + (f" +{len(active)-4}" if len(active) > 4 else "")
            ax.text(x + .45, y + .49, label, ha="center", va="center", fontsize=11, fontweight="bold")
            ax.text(x + .45, y + .28, f"{len(active)} active component(s)", ha="center", fontsize=9)
            ax.text(x + .45, y + .11, component_text, ha="center", fontsize=8.2)
            linked = anchors_lookup[(context, axis)]
            if linked:
                kinds = sorted({"24 h assay" if item["evidence_level"] == "FUNCTIONAL_ASSAY" else "in vivo" for item in linked})
                ax.scatter([x + .08], [y + .63], s=60, color="#7E57A0", edgecolor="white", zorder=5)
                ax.text(x + .16, y + .62, "/".join(kinds), fontsize=7.4, color="#5D3A78", va="center")
    ax.text(.55, .12, "Cell fill = transcriptomic axis status", fontsize=9)
    ax.scatter([1.42], [.15], s=60, color="#7E57A0", edgecolor="white")
    ax.text(1.5, .12, "separate phenotype anchor", fontsize=9)
    ax.text(2.35, .12, "Reliability retained separately: donor, EV preparation, batch, pairing, control, QC, diagnostics", fontsize=8.6, color="#9A6500")
    fig.savefig(SUBFIG / "fig08_context_aware_response_atlas.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def architecture_figure():
    SUBFIG.mkdir(parents=True, exist_ok=True)
    stages = [
        ("Public EV studies", "GEO/SRA + study metadata", "IMPLEMENTED"),
        ("Context normalization", "source · recipient · dose · time", "IMPLEMENTED"),
        ("Reproducible analysis", "QC · DE · ranked enrichment", "IMPLEMENTED"),
        ("Response Atlas", "339 frozen components × 3 contexts", "IMPLEMENTED"),
        ("Component-aware evidence", "direction · NES · FDR · null/missingness", "IMPLEMENTED"),
        ("Reliability", "separate design and evidence dimensions", "IMPLEMENTED"),
        ("Retrieval", "interpretable context similarity", "NEXT"),
        ("Explorer", "interactive evidence inspection", "NEXT"),
    ]
    fig, ax = plt.subplots(figsize=(11, 14), constrained_layout=True)
    ax.set_xlim(0, 10); ax.set_ylim(0, 15); ax.axis("off")
    fig.suptitle("SkinExo-AI Platform Architecture", fontsize=24, fontweight="bold")
    ax.text(5, 14.55, "Context-aware evidence representation; predictive AI is not implemented", ha="center", fontsize=12, color="#455465")
    ys = [13.3, 11.65, 10.0, 8.35, 6.7, 5.05, 3.4, 1.75]
    for index, ((title, subtitle, status), y) in enumerate(zip(stages, ys)):
        implemented = status == "IMPLEMENTED"
        box = FancyBboxPatch((1.35, y - .55), 7.3, 1.05, boxstyle="round,pad=0.02,rounding_size=0.08",
                             facecolor="#D7EAF5" if implemented else "#F1F2F4",
                             edgecolor="#2878A5" if implemented else "#78828D",
                             linewidth=2, linestyle="-" if implemented else "--")
        ax.add_patch(box)
        ax.text(5, y + .13, title, ha="center", fontsize=15, fontweight="bold")
        ax.text(5, y - .2, subtitle, ha="center", fontsize=10.5, color="#425466")
        ax.text(8.95, y, status, ha="left", va="center", fontsize=10, fontweight="bold",
                color="#2878A5" if implemented else "#6C7077")
        if index < len(stages) - 1:
            ax.add_patch(FancyArrowPatch((5, y - .57), (5, ys[index + 1] + .57), arrowstyle="-|>", mutation_scale=18,
                                         color="#65717E", linewidth=1.7))
    ax.text(5, .62, "F2 boundary: Atlas, evidence, and reliability are implemented. Retrieval and Explorer are the next stages.",
            ha="center", fontsize=10.5, color="#384554")
    fig.savefig(SUBFIG / "fig09_skinexo_platform_architecture.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def write_report(manifest):
    correlations = manifest["global_NES_correlations"]
    report = f"""# SkinExo-AI FRAMEWORK-F2

## Objective

Convert the frozen CTX001, CTX002, and CTX003 evidence into Atlas version `{ATLAS_VERSION}` without rerunning or changing any biological analysis.

## Why Three Contexts Are Sufficient for the Submission Atlas

Three study-independent contexts are sufficient to demonstrate the representation problem: a two-context shared component can fail to extend to a third context, the same axis can be driven by different components, direct component discordance can occur, and null evidence must remain visible. Three contexts do not support universal generalization, donor-level replication, or EV-preparation-level replication.

## Atlas Data Model

The Atlas links context features, a frozen component universe, 1,017 context-component records, 15 axis summaries, five phenotype anchors, and 39 separate reliability records. The wide matrix stores structured JSON cells; the long table is the normalized source for retrieval.

## Component Universe

The F2 universe contains **{manifest['component_count']}** components frozen from the existing C4 mapping. Distinct components remain distinct even when they share an axis. Versioning is `{ATLAS_VERSION}`; later additions require a new version.

## Activity States

`ACTIVE_POSITIVE`, `ACTIVE_NEGATIVE`, `OBSERVED_NULL`, `NOT_TESTED`, and `UNKNOWN` are distinct. F2 contains {manifest['active_response_records']} active, {manifest['observed_null_records']} observed-null, {manifest['not_tested_records']} not-tested, and {manifest['unknown_records']} unknown records. A null is tested nonqualification; it is not missing evidence.

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

Secondary descriptive NES correlations are CTX001/CTX002 Pearson {correlations['CTX001_vs_CTX002']['pearson']:+.4f}, Spearman {correlations['CTX001_vs_CTX002']['spearman']:+.4f}; CTX001/CTX003 Pearson {correlations['CTX001_vs_CTX003']['pearson']:+.4f}, Spearman {correlations['CTX001_vs_CTX003']['spearman']:+.4f}; CTX002/CTX003 Pearson {correlations['CTX002_vs_CTX003']['pearson']:+.4f}, Spearman {correlations['CTX002_vs_CTX003']['spearman']:+.4f}. These are not prediction performance.

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
"""
    (ROOT / "reports/FRAMEWORK_F2_three_context_response_atlas.md").write_text(report)


def main():
    contexts, universe, long_rows, axis_rows, anchors, reliability, manifest = build_atlas()
    atlas_figure(contexts, long_rows, axis_rows, anchors)
    architecture_figure()
    write_report(manifest)
    print(json.dumps({
        "atlas_version": ATLAS_VERSION, "components": len(universe),
        "response_records": len(long_rows), "activity_states": Counter(row["activity_state"] for row in long_rows),
        "phenotype_anchors": len(anchors), "reliability_records": len(reliability),
    }, indent=2))


if __name__ == "__main__":
    main()
