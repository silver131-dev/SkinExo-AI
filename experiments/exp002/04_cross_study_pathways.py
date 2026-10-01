#!/usr/bin/env python3
"""EXP002-C4: frozen EXP001/EXP002 GSEA validation; never refit C3."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs/exp002"
PLAN_PATH = ROOT / "configs/exp001_c4_frozen_plan.json"
MAP_PATH = ROOT / "data/metadata/skinexo_c4_term_map.csv"
ENDPOINT_PATH = ROOT / "docs/checkpoints/EXP002_VALIDATION_ENDPOINTS.md"
EXP001 = ROOT / "outputs/exp001"
AXES = {"Q1": "P", "Q2": "M", "Q3": "E", "Q4": "A", "Q5": "I"}

spec = importlib.util.spec_from_file_location("exp001_c4", ROOT / "experiments/exp001/04_pathway_analysis.py")
exp001_c4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exp001_c4)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable(gene_id: str) -> str:
    return str(gene_id).split(".", 1)[0]


def load_de(label: str) -> pd.DataFrame:
    path = OUT / f"differential_expression_{label}_all.csv"
    de = pd.read_csv(path)
    required = {"gene_id", "gene_symbol", "stat", "log2FoldChange"}
    if not required <= set(de) or de.gene_id.isna().any() or de.gene_symbol.isna().any():
        raise ValueError(f"Invalid C3 table: {path}")
    de.insert(1, "original_gene_id", de.gene_id)
    de.gene_id = de.gene_id.map(stable)
    if de.gene_id.duplicated().any() or not np.isfinite(de[["stat", "log2FoldChange"]]).all().all():
        raise ValueError(f"Duplicate stable ID or nonfinite Wald/effect: {path}")
    return de


def load_inputs():
    plan = json.loads(PLAN_PATH.read_text())
    c3 = json.loads((OUT / "exp002_c3_de.json").read_text())
    c2r = json.loads((OUT / "exp002_c2r_ev8_review.json").read_text())
    manifest = json.loads((EXP001 / "c4_gene_set_manifest.json").read_text())
    if not c3["overall_pass"] or c3["design"] != "~ batch + condition" or c2r["EV8_decision"] != "RETAIN":
        raise ValueError("Frozen C3/C2R checkpoint failed")
    if plan["gene_set_release"] != "MSigDB v2026.1.Hs" or digest(PLAN_PATH) != manifest["frozen_plan_sha256"]:
        raise ValueError("EXP001 plan or release differs from manifest")
    mapped = pd.read_csv(MAP_PATH)
    if set(mapped.question) != set(AXES) or set(mapped.predefined_or_posthoc) != {"PREDEFINED"}:
        raise ValueError("Frozen term map has unexpected questions or posthoc terms")
    if len(mapped) != manifest["predefined_mapped_term_rows"] or int(mapped.eligible_for_testing.sum()) != manifest["predefined_eligible_term_rows"]:
        raise ValueError("Term map differs from EXP001 manifest")
    primary, sensitivity = load_de("primary"), load_de("sensitivity")
    if len(primary) != c3["primary_genes_tested"] or len(sensitivity) != c3["sensitivity_genes_tested"]:
        raise ValueError("C3 gene count mismatch")
    if not set(sensitivity.gene_id) <= set(primary.gene_id):
        raise ValueError("Sensitivity tested universe not subset of primary")
    exp1 = pd.read_csv(EXP001 / "differential_expression_all.csv")
    if len(exp1) != manifest["tested_gene_universe_size"] or exp1.gene_id.duplicated().any():
        raise ValueError("EXP001 C3 universe differs from manifest")
    return plan, c3, manifest, mapped, exp1, primary, sensitivity


def source_memberships(plan):
    memberships = {}
    for db, filename in plan["gene_set_collections"].items():
        path = ROOT / "data/raw/c4_gene_sets" / filename
        if digest(path) != plan["gene_set_sha256"][db]:
            raise ValueError(f"GMT hash mismatch: {filename}")
        for line in path.read_text().splitlines():
            term_id, _, *symbols = line.split("\t")
            if term_id in memberships:
                raise ValueError(f"Duplicate term ID: {term_id}")
            memberships[term_id] = frozenset(s.strip().upper() for s in symbols if s.strip())
    return memberships


def gsea(label: str):
    plan, c3, manifest, mapped, exp1, primary, sensitivity = load_inputs()
    de = primary if label == "primary" else sensitivity
    terms, counts, membership, id_to_symbol = exp001_c4.load_sets(plan, de)
    ranked = de[["gene_id", "stat"]].sort_values(["stat", "gene_id"], ascending=[False, True], kind="stable")
    eligible = {term_id for term_id, term in terms.items() if term["eligible"]}
    result = exp001_c4.run_gsea(plan, ranked, terms, id_to_symbol)
    if set(result.term_id) != eligible or len(result) != len(eligible):
        raise ValueError("GSEA omitted eligible terms")
    result.to_csv(OUT / f"c4_gsea_{label}_all.csv", index=False)
    rows = [{"database": t["database"], "term_id": k, "effective_gene_set_size": t["gene_set_size"],
             "eligible_for_testing": t["eligible"]} for k, t in sorted(terms.items())]
    pd.DataFrame(rows).to_csv(OUT / f"c4_term_coverage_{label}.csv", index=False)
    return {"fit": label, "tested_genes": len(de), "eligible_terms": len(result),
            "qualified_terms": int((result.padj.lt(.05) & result.leading_edge_coherent).sum()),
            "mapped_ids": len(membership), "duplicate_symbol_groups": int((de.gene_symbol.str.upper().value_counts() > 1).sum()),
            "gmt_hashes": {db: counts[db]["sha256"] for db in counts}}


def components(term_ids, membership):
    ids = sorted(term_ids)
    parent = {x: x for x in ids}

    def root(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    # Candidate pairs only: source-symbol overlap is required for a Jaccard edge.
    inverted = defaultdict(list)
    for term_id in ids:
        for symbol in membership[term_id]:
            inverted[symbol].append(term_id)
    pairs = set()
    for terms in inverted.values():
        for i, left in enumerate(terms):
            for right in terms[i + 1:]:
                pairs.add((left, right))
    for left, right in sorted(pairs):
        a, b = membership[left], membership[right]
        overlap = len(a & b)
        if overlap / (len(a) + len(b) - overlap) >= .5:
            parent[root(right)] = root(left)
    groups = defaultdict(list)
    for term_id in ids:
        groups[root(term_id)].append(term_id)
    return [sorted(group) for group in sorted(groups.values(), key=lambda group: min(group))]


def component_direction(values):
    if not values:
        return "INACTIVE"
    signs = np.sign(values)
    median = float(np.median(values))
    if median == 0 or (len(values) % 2 == 0 and np.sign(sorted(values)[len(values)//2 - 1]) != np.sign(sorted(values)[len(values)//2])):
        return "MIXED"
    return "POSITIVE" if median > 0 else "NEGATIVE"


def dominant(directions):
    nonmixed = [d for d in directions if d in ("POSITIVE", "NEGATIVE")]
    if not nonmixed:
        return "MIXED"
    for sign in ("POSITIVE", "NEGATIVE"):
        if nonmixed.count(sign) / len(nonmixed) >= 2 / 3:
            return sign
    return "MIXED"


def outcome(a, b, da, db, eligible_count):
    if eligible_count == 0 or not a or not b:
        return "NOT_TESTABLE"
    shared = {i for i in a if i in b and a[i] == b[i] and a[i] in ("POSITIVE", "NEGATIVE")}
    all_directions = list(a.values()) + list(b.values())
    if da == db and da != "MIXED" and all(d == da for d in all_directions):
        return "CONCORDANT"
    if da != "MIXED" and db != "MIXED" and da != db:
        return "DISCORDANT"
    if da == db and da != "MIXED":
        return "PARTIALLY_CONCORDANT"
    if shared:
        return "PARTIALLY_CONCORDANT"
    return "DISCORDANT"


def corr(x, y):
    if len(x) < 2:
        return {"n": len(x), "pearson": None, "spearman": None}
    return {"n": len(x), "pearson": float(pearsonr(x, y).statistic),
            "spearman": float(spearmanr(x, y).statistic)}


def pair_analysis(name, first, second, map_rows, source, reference="EXP001"):
    first_gsea = pd.read_csv(EXP001 / "c4_gsea_all.csv") if reference == "EXP001" else pd.read_csv(OUT / "c4_gsea_primary_all.csv")
    second_gsea = pd.read_csv(OUT / f"c4_gsea_{name}_all.csv")
    first_cov = pd.read_csv(OUT / "c4_term_coverage_primary.csv") if reference != "EXP001" else pd.read_csv(EXP001 / "c4_gsea_all.csv")[["term_id"]]
    second_cov = pd.read_csv(OUT / f"c4_term_coverage_{name}.csv")
    eligible = set(first_cov.loc[first_cov.get("eligible_for_testing", pd.Series(True, index=first_cov.index)).astype(bool), "term_id"]) & set(second_cov.loc[second_cov.eligible_for_testing, "term_id"])
    if reference == "EXP001":
        eligible &= set(map_rows.loc[map_rows.eligible_for_testing, "term_id"]) | (set(eligible) - set(map_rows.term_id))
    g1 = first_gsea.set_index("term_id")
    g2 = second_gsea.set_index("term_id")
    if not eligible <= set(g1.index) & set(g2.index):
        raise ValueError("Common eligible term missing GSEA result")
    joined = g1.loc[sorted(eligible), ["NES", "padj", "leading_edge_genes", "leading_edge_n", "leading_edge_coherent"]].join(
        g2.loc[sorted(eligible), ["NES", "padj", "leading_edge_genes", "leading_edge_n", "leading_edge_coherent"]],
        lsuffix="_first", rsuffix="_second")
    joined.insert(0, "term_id", joined.index)
    joined.insert(1, "database", g1.loc[joined.index, "database"].to_numpy())
    joined.to_csv(OUT / f"c4_common_terms_{reference.lower()}_vs_{name}.csv", index=False)
    component_rows, axis_rows = [], []
    for question, axis in AXES.items():
        ids = set(map_rows.loc[(map_rows.question == question) & map_rows.eligible_for_testing, "term_id"]) & eligible
        groups = components(ids, source)
        active = [{}, {}]
        for component_no, group in enumerate(groups, 1):
            component_id = f"{axis}{component_no:03d}"
            for index, g in enumerate((g1, g2)):
                sub = g.loc[group]
                qualified = sub.loc[sub.padj.lt(.05) & sub.leading_edge_coherent.astype(bool)]
                direction = component_direction(qualified.NES.tolist())
                if direction != "INACTIVE":
                    active[index][component_id] = direction
                component_rows.append({"comparison": f"{reference}_vs_{name}", "axis": axis,
                    "component_id": component_id, "fit": reference if index == 0 else name,
                    "source_overlap_jaccard_threshold": .5, "term_count": len(group), "term_ids": ";".join(group),
                    "qualified_term_count": len(qualified), "direction": direction,
                    "term_evidence_json": json.dumps([{"term_id": term_id, "NES": float(row.NES),
                        "FDR": float(row.padj), "leading_edge_n": int(row.leading_edge_n),
                        "qualified": bool(row.padj < .05 and row.leading_edge_coherent)}
                        for term_id, row in sub.iterrows()], separators=(",", ":"))})
        da, db = dominant(list(active[0].values())), dominant(list(active[1].values()))
        verdict = outcome(*active, da, db, len(ids))
        axis_rows.append({"comparison": f"{reference}_vs_{name}", "axis": axis,
            "common_eligible_terms": len(ids), "eligible_components": len(groups),
            "active_components_first": len(active[0]), "active_components_second": len(active[1]),
            "dominant_first": da, "dominant_second": db, "outcome": verdict,
            "not_testable_reason": ("NO_COMMON_ELIGIBLE_TERMS" if not ids else "NULL_GSEA_BOTH" if not active[0] and not active[1] else "NULL_GSEA_FIRST" if not active[0] else "NULL_GSEA_SECOND" if not active[1] else "") if verdict == "NOT_TESTABLE" else ""})
    pd.DataFrame(component_rows).to_csv(OUT / f"c4_components_{reference.lower()}_vs_{name}.csv", index=False)
    pd.DataFrame(axis_rows).to_csv(OUT / f"c4_axes_{reference.lower()}_vs_{name}.csv", index=False)
    qualified_first = joined.padj_first.lt(.05) & joined.leading_edge_coherent_first
    qualified_second = joined.padj_second.lt(.05) & joined.leading_edge_coherent_second
    qualified_both = joined.loc[qualified_first & qualified_second].copy()
    overlap_rows = []
    for row in joined.itertuples():
        both = bool(row.padj_first < .05 and row.leading_edge_coherent_first and row.padj_second < .05 and row.leading_edge_coherent_second)
        a = {stable(x) for x in str(row.leading_edge_genes_first).split(";") if x and x != "nan"} if both else set()
        b = {stable(x) for x in str(row.leading_edge_genes_second).split(";") if x and x != "nan"} if both else set()
        overlap_rows.append({"term_id": row.term_id, "status": "QUALIFIED_BOTH" if both else
                             "QUALIFIED_FIRST_ONLY" if row.padj_first < .05 and row.leading_edge_coherent_first else
                             "QUALIFIED_SECOND_ONLY" if row.padj_second < .05 and row.leading_edge_coherent_second else "NOT_QUALIFIED_EITHER",
                             "first_n": len(a) if both else None, "second_n": len(b) if both else None,
                             "intersection": len(a & b) if both else None, "union": len(a | b) if both else None,
                             "jaccard": len(a & b) / len(a | b) if both else None})
    pd.DataFrame(overlap_rows).to_csv(
        OUT / f"c4_leading_edge_overlap_{reference.lower()}_vs_{name}.csv", index=False)
    db_corr = {db: corr(group.NES_first, group.NES_second) for db, group in joined.groupby("database")}
    axis_corr = {axis: corr(sub.NES_first, sub.NES_second) for question, axis in AXES.items()
                 if not (sub := joined.loc[joined.term_id.isin(set(map_rows.loc[map_rows.question == question, "term_id"]))]).empty}
    jaccards = [x["jaccard"] for x in overlap_rows if x["status"] == "QUALIFIED_BOTH"]
    return axis_rows, {"common_eligible_terms": len(eligible), "nes": corr(joined.NES_first, joined.NES_second),
                       "nes_by_database": db_corr, "nes_by_axis": axis_corr,
                       "qualified_leading_edges_first": int(qualified_first.sum()),
                       "qualified_leading_edges_second": int(qualified_second.sum()),
                       "qualified_leading_edges_both": len(qualified_both),
                       "leading_edge_jaccard_median": float(np.median(jaccards)) if jaccards else None,
                       "retrieval_performance": "NOT_ESTIMABLE_TWO_INDEPENDENT_STUDIES",
                       "nes_correlation_distance": float(1 - pearsonr(joined.NES_first, joined.NES_second).statistic)}


def gene_comparison(first, second):
    x = first.copy()
    x.gene_id = x.gene_id.map(stable)
    joined = x[["gene_id", "log2FoldChange", "stat"]].merge(second[["gene_id", "log2FoldChange", "stat"]], on="gene_id", suffixes=("_first", "_second"), validate="one_to_one")
    a, b = joined.log2FoldChange_first.to_numpy(), joined.log2FoldChange_second.to_numpy()
    nonzero = (a != 0) & (b != 0)
    return {"first_tested_ids": len(first), "second_tested_ids": len(second),
            "shared_tested_stable_ids": len(joined), "first_only_ids": len(first) - len(joined),
            "second_only_ids": len(second) - len(joined), "zero_effect_exclusions": int((~nonzero).sum()),
            "direction_concordance": float(np.mean(np.sign(a[nonzero]) == np.sign(b[nonzero]))) if nonzero.any() else None,
            "log2fc": corr(a, b), "wald_spearman": float(spearmanr(joined.stat_first, joined.stat_second).statistic)}


def summarize():
    plan, c3, manifest, mapped, exp1, primary, sensitivity = load_inputs()
    source = source_memberships(plan)
    axes_primary, primary_metrics = pair_analysis("primary", exp1, primary, mapped, source)
    axes_sensitivity, sensitivity_metrics = pair_analysis("sensitivity", exp1, sensitivity, mapped, source)
    axes_robustness, robustness_metrics = pair_analysis("sensitivity", primary, sensitivity, mapped, source, reference="primary")
    comparisons = {"EXP001_vs_primary": primary_metrics, "EXP001_vs_sensitivity": sensitivity_metrics,
                   "primary_vs_sensitivity": robustness_metrics}
    comparisons["EXP001_vs_primary"]["genes"] = gene_comparison(exp1, primary)
    comparisons["EXP001_vs_sensitivity"]["genes"] = gene_comparison(exp1, sensitivity)
    comparisons["primary_vs_sensitivity"]["genes"] = gene_comparison(primary, sensitivity)
    checkpoint = {"checkpoint": "EXP002-C4", "primary_fit": "all 16, including EV_8", "sensitivity_fit": "15, excluding EV_8",
                  "design_unchanged": c3["design"], "endpoint": "pre-specified P/M/E/A/I GSEA directional concordance",
                  "gsea_primary_evidence": True, "source_release": plan["gene_set_release"],
                  "input_sha256": {str(path.relative_to(ROOT)): digest(path) for path in [PLAN_PATH, MAP_PATH, ENDPOINT_PATH,
                     OUT / "differential_expression_primary_all.csv", OUT / "differential_expression_sensitivity_all.csv",
                     EXP001 / "c4_gsea_all.csv"]},
                  "comparisons": comparisons, "axes_primary": axes_primary, "axes_sensitivity": axes_sensitivity,
                  "axes_robustness": axes_robustness,
                  "decision": "ANALYSIS_COMPLETE",
                  "interpretation": "Report five frozen axis outcomes; broad five-axis directional concordance is not supported. No composite score was pre-specified."}
    (OUT / "exp002_c4_pathways.json").write_text(json.dumps(checkpoint, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"primary_axes": {x["axis"]: x["outcome"] for x in axes_primary},
                      "sensitivity_axes": {x["axis"]: x["outcome"] for x in axes_sensitivity},
                      "common_terms": primary_metrics["common_eligible_terms"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("step", choices=("gsea", "summarize"))
    parser.add_argument("--fit", choices=("primary", "sensitivity"))
    args = parser.parse_args()
    if args.step == "gsea":
        if not args.fit:
            parser.error("gsea requires --fit")
        print(json.dumps(gsea(args.fit), indent=2))
    else:
        summarize()
