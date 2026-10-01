#!/usr/bin/env python3
"""Run the prospectively frozen EXP003-C4 GSEA and secondary ORA.

This step produces complete enrichment tables only. It does not inspect author
pathway findings, alter the frozen P/M/E/A/I map, update framework metadata, or
compare biological outcomes across contexts.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from collections import defaultdict
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "skinexo_exp003_c4_mpl"))

import gseapy as gp
import numpy as np
import pandas as pd
from scipy.stats import hypergeom


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs/exp003"
RAW = ROOT / "data/raw/c4_gene_sets"
PLAN_PATH = ROOT / "configs/exp001_c4_frozen_plan.json"
EXP1_MANIFEST = ROOT / "outputs/exp001/c4_gene_set_manifest.json"
C2_PLAN = ROOT / "docs/checkpoints/EXP003_C2_ANALYSIS_PLAN.md"
ENDPOINTS = ROOT / "docs/checkpoints/EXP003_VALIDATION_ENDPOINTS.md"
DBS = ("GO_BP", "Reactome", "Hallmark")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bh(values) -> np.ndarray:
    p = np.asarray(values, dtype=float)
    order = np.argsort(p, kind="stable")
    adjusted = np.empty(len(p), dtype=float)
    ranked = p[order] * len(p) / np.arange(1, len(p) + 1)
    adjusted[order] = np.minimum.accumulate(ranked[::-1])[::-1].clip(0, 1)
    return adjusted


def checks():
    c2 = json.loads((OUT / "exp003_c2_qc.json").read_text())
    c3 = json.loads((OUT / "exp003_c3_de.json").read_text())
    plan = json.loads(PLAN_PATH.read_text())
    exp1_manifest = json.loads(EXP1_MANIFEST.read_text())
    if not (
        c2.get("overall_pass") is True
        and c2.get("decision") == "PASS_WITH_LIMITATIONS"
        and c2.get("primary_filter") == "CPM >= 1 in at least 3 of 6 samples"
        and c2.get("gsea_release") == "MSigDB 2026.1.Hs"
        and c2.get("gsea_ranking") == "DESeq2 Wald statistic"
    ):
        raise RuntimeError("Frozen C2 checkpoint does not authorize C4")
    if not (
        c3.get("overall_pass") is True
        and c3.get("decision") == "PASS_WITH_LIMITATIONS"
        and c3.get("genes_tested") == 13_874
        and c3.get("design") == "~ condition"
        and c3.get("pathway_analysis_status") == "NOT_RUN"
        and c3.get("cross_context_comparison_status") == "NOT_RUN"
    ):
        raise RuntimeError("Frozen C3 checkpoint does not authorize C4")
    if not (
        plan.get("gene_set_release") == "MSigDB v2026.1.Hs"
        and plan.get("gsea", "").startswith("GSEApy 1.3.1")
        and plan.get("questions") == ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"]
        and exp1_manifest.get("frozen_plan_sha256") == digest(PLAN_PATH)
    ):
        raise RuntimeError("Established EXP001 C4 plan/release differs from the frozen resource")
    plan_text = C2_PLAN.read_text()
    endpoint_text = ENDPOINTS.read_text()
    required_plan = ["MSigDB 2026.1.Hs", "DESeq2 Wald statistic", "GO Biological Process", "Reactome", "Hallmark"]
    required_endpoints = ["P —", "M —", "E —", "A —", "I —", "Cross-context interpretation begins only after CTX003 C3 and C4 pass"]
    if not all(value in plan_text for value in required_plan) or not all(value in endpoint_text for value in required_endpoints):
        raise RuntimeError("Frozen C4 plan or validation endpoints are incomplete")
    de = pd.read_csv(OUT / "differential_expression_all.csv")
    sig = pd.read_csv(OUT / "differential_expression_significant.csv")
    required = {"gene_id", "gene_symbol", "stat", "log2FoldChange", "padj"}
    if not required <= set(de) or len(de) != 13_874 or not de.gene_id.is_unique:
        raise RuntimeError("C3 complete result table is invalid")
    if not np.isfinite(de[["stat", "log2FoldChange"]].to_numpy(dtype=float)).all():
        raise RuntimeError("C3 rank/effect values are not finite")
    threshold = de.padj.lt(.05).fillna(False) & de.log2FoldChange.abs().ge(1)
    if set(sig.gene_id) != set(de.loc[threshold, "gene_id"]) or len(sig) != c3["thresholdB"]:
        raise RuntimeError("C3 threshold-B table differs from frozen result")
    up = set(de.loc[threshold & de.log2FoldChange.ge(1), "gene_id"])
    down = set(de.loc[threshold & de.log2FoldChange.le(-1), "gene_id"])
    if (len(up), len(down)) != (c3["up"], c3["down"]):
        raise RuntimeError("C3 threshold-B directions differ from checkpoint")
    return c2, c3, plan, de, up, down


def load_sets(plan: dict, de: pd.DataFrame):
    symbol_to_ids: dict[str, set[str]] = defaultdict(set)
    id_to_symbol = {}
    missing_symbol_ids = []
    for row in de.itertuples(index=False):
        if pd.isna(row.gene_symbol) or not str(row.gene_symbol).strip():
            missing_symbol_ids.append(row.gene_id)
            id_to_symbol[row.gene_id] = ""
            continue
        symbol = str(row.gene_symbol).strip()
        symbol_to_ids[symbol.upper()].add(row.gene_id)
        id_to_symbol[row.gene_id] = symbol
    terms = {}
    counts = {}
    membership = set()
    for database in DBS:
        filename = plan["gene_set_collections"][database]
        path = RAW / filename
        observed_hash = digest(path)
        if observed_hash != plan["gene_set_sha256"][database]:
            raise RuntimeError(f"Gene-set hash mismatch: {filename}")
        source_terms = eligible_terms = 0
        for line in path.read_text().splitlines():
            parts = line.split("\t")
            if len(parts) < 3:
                raise RuntimeError(f"Malformed GMT row in {filename}")
            term_id, source_url, *symbols = parts
            if term_id in terms:
                raise RuntimeError(f"Duplicate term ID across collections: {term_id}")
            source_symbols = {value.strip().upper() for value in symbols if value.strip()}
            ids = set().union(*(symbol_to_ids[symbol] for symbol in source_symbols)) if source_symbols else set()
            eligible = plan["gene_set_size_min"] <= len(ids) <= plan["gene_set_size_max"]
            membership.update(ids)
            source_terms += 1
            eligible_terms += int(eligible)
            terms[term_id] = {
                "database": database,
                "term_id": term_id,
                "term_name": term_id.removeprefix("GOBP_").removeprefix("REACTOME_").removeprefix("HALLMARK_").replace("_", " ").title(),
                "source_url": source_url,
                "source_gene_symbol_count": len(source_symbols),
                "ids": ids,
                "gene_set_size": len(ids),
                "eligible": eligible,
            }
        counts[database] = {
            "filename": filename,
            "sha256": observed_hash,
            "source_terms": source_terms,
            "eligible_terms": eligible_terms,
        }
    return terms, counts, membership, id_to_symbol, missing_symbol_ids, symbol_to_ids


def run_gsea(plan, ranked, terms, id_to_symbol):
    if gp.__version__ != "1.3.1":
        raise RuntimeError(f"Expected GSEApy 1.3.1, found {gp.__version__}")
    eligible = {term_id: sorted(term["ids"]) for term_id, term in terms.items() if term["eligible"]}
    result = gp.prerank(
        rnk=ranked[["gene_id", "stat"]], gene_sets=eligible,
        min_size=plan["gene_set_size_min"], max_size=plan["gene_set_size_max"],
        permutation_num=1000, weight=1.0, ascending=False, threads=4,
        seed=42, method="permutation", outdir=None, no_plot=True, verbose=False,
    ).res2d.copy()
    if len(result) != len(eligible) or set(result.Term) != set(eligible):
        missing = sorted(set(eligible) - set(result.Term))[:10]
        raise RuntimeError(f"GSEA result coverage failure; missing examples: {missing}")
    stat = dict(zip(ranked.gene_id, ranked.stat))
    rows = []
    for row in result.itertuples(index=False):
        term_id = str(row.Term)
        term = terms[term_id]
        nes = float(row.NES)
        leading = [value for value in str(row.Lead_genes).split(";") if value and value != "nan"]
        matched = sum((stat[gene] > 0) == (nes > 0) for gene in leading if gene in stat)
        fraction = matched / len(leading) if leading else 0.0
        # Column labels contain spaces/hyphens, so use the source frame by term.
        source_row = result.loc[result.Term == term_id].iloc[0]
        nominal = float(source_row["NOM p-val"])
        fdr = float(source_row["FDR q-val"])
        rows.append({
            "database": term["database"], "term_id": term_id, "term_name": term["term_name"],
            "direction": "UP" if nes > 0 else "DOWN", "gene_set_size": term["gene_set_size"],
            "background_size": len(ranked), "ES": float(source_row["ES"]), "NES": nes,
            "pvalue": nominal, "FDR": fdr,
            "leading_edge_genes": ";".join(leading),
            "leading_edge_symbols": ";".join(id_to_symbol.get(gene, "") or "UNMAPPED" for gene in leading),
            "leading_edge_n": len(leading), "leading_edge_same_sign_fraction": fraction,
            "leading_edge_coherent": len(leading) >= 5 and fraction >= .8,
        })
    return pd.DataFrame(rows).sort_values(["FDR", "pvalue", "term_id"], kind="stable")


def run_ora(terms, query, direction, id_to_symbol, universe_size):
    rows = []
    for term in sorted((value for value in terms.values() if value["eligible"]), key=lambda value: value["term_id"]):
        overlap = sorted(term["ids"] & query)
        pvalue = float(hypergeom.sf(len(overlap) - 1, universe_size, term["gene_set_size"], len(query))) if overlap else 1.0
        rows.append({
            "database": term["database"], "term_id": term["term_id"], "term_name": term["term_name"],
            "direction": direction, "gene_set_size": term["gene_set_size"], "overlap_size": len(overlap),
            "background_size": universe_size, "query_size": len(query), "pvalue": pvalue,
            "overlap_genes": ";".join(overlap),
            "overlap_symbols": ";".join(id_to_symbol.get(gene, "") or "UNMAPPED" for gene in overlap),
        })
    frame = pd.DataFrame(rows)
    frame["FDR"] = bh(frame.pvalue)
    return frame.sort_values(["FDR", "pvalue", "term_id"], kind="stable")


def main():
    c2, c3, plan, de, up, down = checks()
    terms, counts, membership, id_to_symbol, missing_symbols, symbol_to_ids = load_sets(plan, de)
    ranked = de[["gene_id", "gene_symbol", "stat", "log2FoldChange", "padj"]].copy()
    ranked["has_verified_symbol"] = ranked.gene_symbol.notna() & ranked.gene_symbol.astype(str).str.strip().ne("")
    ranked["mapped_to_any_gene_set"] = ranked.gene_id.isin(membership)
    ranked = ranked.sort_values(["stat", "gene_id"], ascending=[False, True], kind="stable")
    ranked.insert(0, "rank", np.arange(1, len(ranked) + 1))
    ranked.to_csv(OUT / "c4_ranked_genes.csv", index=False)

    gsea = run_gsea(plan, ranked, terms, id_to_symbol)
    ora_up = run_ora(terms, up, "UP", id_to_symbol, len(ranked))
    ora_down = run_ora(terms, down, "DOWN", id_to_symbol, len(ranked))
    gsea.to_csv(OUT / "c4_gsea_all.csv", index=False)
    ora_up.to_csv(OUT / "c4_ora_up_all.csv", index=False)
    ora_down.to_csv(OUT / "c4_ora_down_all.csv", index=False)

    symbol_counts = pd.Series([key for key in symbol_to_ids for _ in symbol_to_ids[key]]).value_counts()
    manifest = {
        "dataset": "GSE293956", "context_id": "CTX003",
        "gene_set_release": "MSigDB 2026.1.Hs",
        "frozen_plan_sha256": digest(PLAN_PATH),
        "collections": counts,
        "gseapy_version": gp.__version__, "permutations": 1000, "weight": 1,
        "seed": 42, "gene_set_size_min": 15, "gene_set_size_max": 500,
        "source_gene_sets": len(terms), "tested_gene_sets": len(gsea),
        "ranked_genes": len(ranked), "genes_with_verified_symbol": int(ranked.has_verified_symbol.sum()),
        "genes_without_verified_symbol": len(missing_symbols),
        "genes_mapped_to_at_least_one_gene_set": int(ranked.mapped_to_any_gene_set.sum()),
        "genes_absent_all_gene_sets": int((~ranked.mapped_to_any_gene_set).sum()),
        "duplicate_symbol_groups": int((symbol_counts > 1).sum()),
        "gene_ids_in_duplicate_symbol_groups": int(symbol_counts[symbol_counts > 1].sum()),
        "symbol_mapping": "Exact uppercase verified GENCODE v44 gene_symbol to MSigDB symbol; every stable gene ID sharing a symbol is retained; missing-symbol genes remain in the ranked universe but cannot enter symbol-defined sets",
        "ranking": "All 13,874 C3-tested stable gene IDs by DESeq2 Wald statistic descending; gene_id ascending tie rule; positive = hDF-EV higher",
        "thresholdB_up": len(up), "thresholdB_down": len(down),
        "gsea_FDR_lt_0_05": int(gsea.FDR.lt(.05).sum()),
        "gsea_qualified_FDR_coherent": int((gsea.FDR.lt(.05) & gsea.leading_edge_coherent).sum()),
        "ora_up_FDR_lt_0_05": int(ora_up.FDR.lt(.05).sum()),
        "ora_down_FDR_lt_0_05": int(ora_down.FDR.lt(.05).sum()),
        "ora_power_note": "Secondary ORA has 20 UP and 0 DOWN threshold-B genes; power is limited and ORA cannot override GSEA",
        "author_result_firewall": "No author DEG or pathway result was read or used",
    }
    (OUT / "c4_gene_set_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({key: manifest[key] for key in [
        "ranked_genes", "genes_with_verified_symbol", "genes_without_verified_symbol",
        "tested_gene_sets", "gsea_FDR_lt_0_05", "gsea_qualified_FDR_coherent",
        "ora_up_FDR_lt_0_05", "ora_down_FDR_lt_0_05",
    ]}, indent=2))


if __name__ == "__main__":
    main()
