"""EXP001-C4: frozen-plan ORA/GSEA and evidence integration.

Run `prepare` first to record mapping and predefined term families, then `analyze`.
Official MSigDB GMT files belong in ignored data/raw/c4_gene_sets/.
No C3 or C3.5 input is changed by this script.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/skinexo_c4_matplotlib")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import hypergeom


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs/exp001"
META = ROOT / "data/metadata"
RAW = ROOT / "data/raw/c4_gene_sets"
PLAN_PATH = ROOT / "configs/exp001_c4_frozen_plan.json"
DBS = ("GO_BP", "Reactome", "Hallmark")
AXES = {"Q1": "P_proliferation", "Q2": "M_migration", "Q3": "E_ecm",
        "Q4": "A_angiogenesis", "Q5": "I_inflammation"}
LABELS = {"Q1": "Proliferation / cell cycle", "Q2": "Migration / motility",
          "Q3": "ECM organization / remodeling", "Q4": "Angiogenesis / endothelial interaction",
          "Q5": "Inflammation / immune response", "Q6": "Regenerative vs fibrotic"}


def read_json(path: Path):
    return json.loads(path.read_text())


def display_fdr(value):
    return "<0.001 (permutation estimate)" if float(value) == 0 else f"{float(value):.3g}"


def checks():
    c3 = read_json(OUT / "exp001_c3_de.json")
    c35 = read_json(OUT / "exp001_c3_5_evidence.json")
    plan = read_json(PLAN_PATH)
    if not c3.get("overall_pass") or not c35.get("overall_pass"):
        raise RuntimeError("C3 and C3.5 must pass before C4")
    if not plan.get("frozen_before_enrichment") or plan["questions"] != [f"Q{i}" for i in range(1, 7)]:
        raise RuntimeError("Frozen C4 plan missing or changed")
    if [q["id"] for q in c35["C4_questions"]] != plan["questions"]:
        raise RuntimeError("C4 questions differ from C3.5")
    de = pd.read_csv(OUT / "differential_expression_all.csv")
    sig = pd.read_csv(OUT / "differential_expression_significant.csv")
    evidence = pd.read_csv(META / "skinexo_evidence_matrix.csv", keep_default_na=False)
    catalog = pd.read_csv(META / "skinexo_dataset_catalog.csv", keep_default_na=False)
    if len(de) != c3["genes_tested"] or len(sig) != c3["threshold_b_total"]:
        raise RuntimeError("C3 result table size disagrees with checkpoint")
    if len(evidence) != c35["papers_screened"] or len(catalog) != c35["public_datasets_found"]:
        raise RuntimeError("C3.5 evidence inputs disagree with checkpoint")
    if not de.gene_id.is_unique or de[["stat", "log2FoldChange"]].isna().any().any():
        raise RuntimeError("C3 identifier/statistics invalid")
    if not np.isfinite(de["stat"].to_numpy(dtype=float)).all():
        raise RuntimeError("Nonfinite C3 Wald statistic")
    if de.gene_symbol.isna().any() or de.gene_symbol.astype(str).str.strip().eq("").any():
        raise RuntimeError("Missing C3 gene symbol for GMT mapping")
    if set(sig.gene_id) - set(de.gene_id):
        raise RuntimeError("Significant gene IDs absent from C3 universe")
    up = set(sig.loc[(sig.padj < 0.05) & (sig.log2FoldChange >= 1), "gene_id"])
    down = set(sig.loc[(sig.padj < 0.05) & (sig.log2FoldChange <= -1), "gene_id"])
    if len(up) != c3["threshold_b_up"] or len(down) != c3["threshold_b_down"]:
        raise RuntimeError("C3 threshold-B groups differ from checkpoint")
    return c3, c35, plan, de, evidence, up, down


def load_sets(plan, de):
    symbol_to_ids = defaultdict(set)
    id_to_symbol = {}
    for row in de.itertuples(index=False):
        symbol = str(row.gene_symbol).strip().upper()
        symbol_to_ids[symbol].add(row.gene_id)
        id_to_symbol[row.gene_id] = str(row.gene_symbol)
    terms = {}
    counts = {}
    membership = set()
    for db in DBS:
        filename = plan["gene_set_collections"][db]
        path = RAW / filename
        if not path.is_file():
            raise FileNotFoundError(path)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != plan["gene_set_sha256"][db]:
            raise RuntimeError(f"Gene-set SHA-256 mismatch: {filename}")
        total = eligible = 0
        for line in path.read_text().splitlines():
            parts = line.split("\t")
            if len(parts) < 3:
                raise RuntimeError(f"Bad GMT row: {filename}")
            term_id, source_url, *symbols = parts
            if term_id in terms:
                raise RuntimeError(f"Duplicate term ID across collections: {term_id}")
            source_symbols = {s.strip().upper() for s in symbols if s.strip()}
            ids = set().union(*(symbol_to_ids[s] for s in source_symbols)) if source_symbols else set()
            membership.update(ids)
            is_eligible = plan["gene_set_size_min"] <= len(ids) <= plan["gene_set_size_max"]
            total += 1
            eligible += int(is_eligible)
            terms[term_id] = dict(database=db, term_id=term_id,
                                  term_name=term_id.removeprefix("GOBP_").removeprefix("REACTOME_").removeprefix("HALLMARK_").replace("_", " ").title(),
                                  source_url=source_url, source_gene_symbol_count=len(source_symbols),
                                  ids=ids, gene_set_size=len(ids), eligible=is_eligible)
        counts[db] = {"source_terms": total, "eligible_terms": eligible,
                      "filename": filename, "sha256": digest,
                      "source_url": plan["gene_set_source_base"] + filename}
    return terms, counts, membership, id_to_symbol


def term_map(plan, terms):
    rows = []
    for term in terms.values():
        db = term["database"]
        for question, rule in plan["term_mapping"][db].items():
            if isinstance(rule, list):
                match = term["term_id"] in rule
                basis = "EXACT_ID:" + term["term_id"]
            else:
                match = bool(re.search(rule, term["term_id"], re.IGNORECASE))
                basis = "TERM_ID_REGEX:" + rule
            if match:
                rows.append(dict(question=question, database=db,
                                 term_id=term["term_id"], term_name=term["term_name"],
                                 mapping_basis=basis, predefined_or_posthoc="PREDEFINED",
                                 effective_gene_set_size=term["gene_set_size"],
                                 eligible_for_testing=term["eligible"]))
    return pd.DataFrame(rows).sort_values(["question", "database", "term_id"])


def prepare():
    c3, c35, plan, de, evidence, up, down = checks()
    terms, counts, membership, id_to_symbol = load_sets(plan, de)
    ranked = de[["gene_id", "gene_symbol", "stat", "log2FoldChange", "padj"]].copy()
    ranked = ranked.sort_values(["stat", "gene_id"], ascending=[False, True], kind="stable")
    ranked.insert(0, "rank", np.arange(1, len(ranked) + 1))
    ranked.to_csv(OUT / "c4_ranked_genes.csv", index=False)
    mapped = term_map(plan, terms)
    mapped.to_csv(META / "skinexo_c4_term_map.csv", index=False)
    unmapped = de.loc[~de.gene_id.isin(membership), ["gene_id", "gene_symbol"]].copy()
    unmapped.to_csv(OUT / "c4_unmapped_gene_ids.csv", index=False)
    symbol_counts = de.gene_symbol.str.upper().value_counts()
    manifest = dict(database_release=plan["gene_set_release"],
                    frozen_plan_sha256=hashlib.sha256(PLAN_PATH.read_bytes()).hexdigest(),
                    release_note_url="https://docs.gsea-msigdb.org/MSigDB/Release_Notes/MSigDB_2026.1.Hs/",
                    collection_page_url="https://www.gsea-msigdb.org/gsea/msigdb/collections.jsp",
                    license_url="https://www.gsea-msigdb.org/gsea/msigdb_license_terms.jsp",
                    license_summary="CC BY 4.0 base terms; additional terms apply to some collections. Only GO BP, Reactome, Hallmark used; GMT cached under ignored data/raw.",
                    source_release_details={"GO_BP": "GO-basic 2025-10-10; NCBI gene2go 2025-12-14 per MSigDB 2026.1 notes",
                                            "Reactome": "Reactome architecture release 95 per MSigDB 2026.1 notes",
                                            "Hallmark": "MSigDB Hallmark 2026.1.Hs"},
                    collections=counts, source_term_count=len(terms),
                    eligible_term_count=sum(t["eligible"] for t in terms.values()),
                    tested_gene_universe_size=len(de), ranked_gene_count=len(ranked),
                    c3_gene_ids_with_symbol=len(de), c3_duplicate_symbol_groups=int((symbol_counts > 1).sum()),
                    c3_gene_ids_in_duplicate_symbol_groups=int(symbol_counts[symbol_counts > 1].sum()),
                    gene_ids_in_at_least_one_source_set=len(membership),
                    gene_ids_absent_all_source_sets=len(unmapped),
                    predefined_mapped_term_rows=len(mapped),
                    predefined_eligible_term_rows=int(mapped.eligible_for_testing.sum()),
                    ranking_method="DESeq2 Wald stat descending; positive=ECEV higher; all C3-tested gene IDs; no ties in observed C3 stats",
                    symbol_mapping="Uppercase exact C3 gene_symbol to MSigDB HGNC symbols; each source symbol maps to every corresponding tested gene_id, preserving duplicate-symbol IDs; source terms restricted to tested IDs",
                    q6_signature_status="NOT_YET_TESTABLE",
                    q6_reason="C3.5 verified GSE141814 as two pooled mouse scRNA-seq libraries without replicate libraries, and did not verify independently defined signed regenerative-like and fibrotic-like gene lists. No signature derived from EXP001 or review narrative.")
    (OUT / "c4_gene_set_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({k: manifest[k] for k in ("tested_gene_universe_size", "ranked_gene_count", "source_term_count", "eligible_term_count", "gene_ids_in_at_least_one_source_set", "gene_ids_absent_all_source_sets", "predefined_mapped_term_rows", "predefined_eligible_term_rows", "c3_duplicate_symbol_groups")}, indent=2))


def bh(pvalues):
    p = np.asarray(pvalues, dtype=float)
    order = np.argsort(p, kind="stable")
    out = np.empty(len(p), dtype=float)
    raw = p[order] * len(p) / np.arange(1, len(p) + 1)
    out[order] = np.minimum.accumulate(raw[::-1])[::-1].clip(0, 1)
    return out


def run_ora(terms, genes, direction, id_to_symbol, universe_size):
    rows = []
    eligible = sorted((t for t in terms.values() if t["eligible"]), key=lambda t: t["term_id"])
    for term in eligible:
        overlap = sorted(term["ids"] & genes)
        k = len(overlap)
        pval = float(hypergeom.sf(k - 1, universe_size, term["gene_set_size"], len(genes))) if k else 1.0
        rows.append(dict(database=term["database"], term_id=term["term_id"],
                         term_name=term["term_name"], direction=direction,
                         gene_set_size=term["gene_set_size"], overlap_size=k,
                         background_size=universe_size, query_size=len(genes),
                         pvalue=pval, overlap_genes=";".join(overlap),
                         overlap_symbols=";".join(id_to_symbol[x] for x in overlap)))
    result = pd.DataFrame(rows)
    result["padj"] = bh(result.pvalue)
    result = result.sort_values(["padj", "pvalue", "term_id"], kind="stable")
    return result[["database", "term_id", "term_name", "direction", "gene_set_size",
                   "overlap_size", "background_size", "query_size", "pvalue", "padj",
                   "overlap_genes", "overlap_symbols"]]


def run_gsea(plan, ranked, terms, id_to_symbol):
    import gseapy as gp

    if gp.__version__ != "1.3.1":
        raise RuntimeError(f"Expected GSEApy 1.3.1, found {gp.__version__}")
    eligible = {term_id: sorted(t["ids"]) for term_id, t in terms.items() if t["eligible"]}
    res = gp.prerank(rnk=ranked[["gene_id", "stat"]], gene_sets=eligible,
                     min_size=plan["gene_set_size_min"], max_size=plan["gene_set_size_max"],
                     permutation_num=1000, weight=1.0, ascending=False, threads=4,
                     seed=42, method="permutation", outdir=None, no_plot=True, verbose=False)
    raw = res.res2d.copy()
    if len(raw) != len(eligible):
        missing = set(eligible) - set(raw["Term"])
        raise RuntimeError(f"GSEApy returned {len(raw)} of {len(eligible)} eligible terms; missing examples: {sorted(missing)[:10]}")
    stat = dict(zip(ranked.gene_id, ranked.stat))
    rows = []
    for _, d in raw.iterrows():
        term_id = str(d["Term"])
        t = terms[term_id]
        nes = float(d["NES"])
        lead = [x for x in str(d["Lead_genes"]).split(";") if x and x != "nan"]
        matching = sum((stat[x] > 0) == (nes > 0) for x in lead if x in stat)
        frac = matching / len(lead) if lead else 0.0
        rows.append(dict(database=t["database"], term_id=term_id, term_name=t["term_name"],
                         direction="UP" if nes > 0 else "DOWN", gene_set_size=t["gene_set_size"],
                         background_size=len(ranked), ES=float(d["ES"]), NES=nes,
                         nominal_pvalue=float(d["NOM p-val"]), padj=float(d["FDR q-val"]),
                         leading_edge_genes=";".join(lead),
                         leading_edge_symbols=";".join(id_to_symbol.get(x, "NA") for x in lead),
                         leading_edge_n=len(lead),
                         leading_edge_same_sign_fraction=frac,
                         leading_edge_coherent=(len(lead) >= 5 and frac >= 0.8)))
    result = pd.DataFrame(rows).sort_values(["padj", "nominal_pvalue", "term_id"], kind="stable")
    return result


def top_sig(df, ids, n=3):
    sub = df[df.term_id.isin(ids) & (df.padj < 0.05)].copy()
    if "NES" in sub:
        sub["absNES"] = sub.NES.abs()
        sub = sub.sort_values(["padj", "absNES", "term_id"], ascending=[True, False, True])
        cols = ["database", "term_id", "direction", "NES", "padj", "leading_edge_n", "leading_edge_same_sign_fraction"]
    else:
        sub = sub.sort_values(["padj", "pvalue", "term_id"])
        cols = ["database", "term_id", "direction", "overlap_size", "padj"]
    return sub.head(n)[cols].to_dict("records")


def integrate(plan, mapped, ora_up, ora_down, gsea, evidence):
    rows = []
    top = {}
    for q, axis in AXES.items():
        ids = set(mapped.loc[(mapped.question == q) & mapped.eligible_for_testing, "term_id"])
        up = ora_up[ora_up.term_id.isin(ids) & (ora_up.padj < 0.05)]
        down = ora_down[ora_down.term_id.isin(ids) & (ora_down.padj < 0.05)]
        gs = gsea[gsea.term_id.isin(ids) & (gsea.padj < 0.05)]
        coherent = gs[gs.leading_edge_coherent]
        same_dir_ora = any((r.direction == "UP" and r.term_id in set(up.term_id)) or
                           (r.direction == "DOWN" and r.term_id in set(down.term_id))
                           for r in coherent.itertuples())
        if len(coherent) and same_dir_ora:
            status = "SUPPORTED"
        elif len(gs) or len(up) or len(down):
            status = "PARTIALLY_SUPPORTED"
        else:
            status = "NOT_SUPPORTED"
        direct = int((evidence[axis] == "DIRECT").sum())
        indirect = int((evidence[axis] == "INDIRECT").sum())
        ext_direct = int(((evidence[axis] == "DIRECT") & (evidence.evidence_class != "SAME_DATASET")).sum())
        if len(gs):
            interpretation = f"Mapped {LABELS[q]} gene sets show ranked transcriptomic association; this does not demonstrate the corresponding cellular phenotype."
        elif len(up) or len(down):
            interpretation = f"ORA-only mapped signal for {LABELS[q]}; primary ranked GSEA does not meet the prespecified FDR threshold."
        else:
            interpretation = f"No mapped {LABELS[q]} set met the prespecified FDR threshold in GSEA or ORA; this is not evidence of biological absence."
        limits = "n=3/condition; competitive gene-set association; overlapping terms; no direct phenotype measurement by C4."
        if q == "Q1":
            limits += " Cell-cycle transcription is distinct from experimentally measured proliferation."
        if q == "Q4":
            limits += " C3.5 direct angiogenesis study count is zero; pathway association cannot establish angiogenesis."
        rows.append(dict(question=q, ORA_up_support=f"{len(up)} significant mapped terms",
                         ORA_down_support=f"{len(down)} significant mapped terms",
                         GSEA_support=f"{len(gs)} significant mapped terms; {len(coherent)} coherent leading edges",
                         literature_direct_evidence_count=direct,
                         literature_indirect_evidence_count=indirect,
                         literature_independent_direct_evidence_count=ext_direct,
                         external_signature_support="NOT_ASSESSED",
                         overall_evidence_status=status, interpretation=interpretation,
                         limitations=limits))
        top[q] = dict(GSEA=top_sig(gsea, ids), ORA_up=top_sig(ora_up, ids, 2),
                      ORA_down=top_sig(ora_down, ids, 2),
                      mapped_eligible_terms=len(ids), coherent_significant_gsea_terms=len(coherent))
    rows.append(dict(question="Q6", ORA_up_support="NOT_TESTED", ORA_down_support="NOT_TESTED",
                     GSEA_support="NOT_TESTED", literature_direct_evidence_count=int((evidence.regenerative_evidence == "DIRECT").sum()),
                     literature_indirect_evidence_count=int((evidence.regenerative_evidence == "INDIRECT").sum()),
                     literature_independent_direct_evidence_count=int(((evidence.regenerative_evidence == "DIRECT") & (evidence.evidence_class != "SAME_DATASET")).sum()),
                     external_signature_support="NOT_YET_TESTABLE: separate signed regenerative-like and fibrotic-like signatures unavailable",
                     overall_evidence_status="NOT_TESTABLE",
                     interpretation="Regenerative-like and fibrotic-like are separate hypotheses; no external directional signature test was performed.",
                     limitations="GSE141814 has one pooled mouse scRNA-seq library per fate and no validated signed signature in the C3.5 catalog; deriving one requires new external analysis and ortholog handling."))
    top["Q6"] = {"status": "NOT_YET_TESTABLE", "reason": rows[-1]["limitations"]}
    return pd.DataFrame(rows), top


def choose_figure_terms(mapped, gsea):
    chosen = []
    for q in AXES:
        ids = set(mapped.loc[(mapped.question == q) & mapped.eligible_for_testing, "term_id"])
        sub = gsea[gsea.term_id.isin(ids) & (gsea.padj < 0.05)].copy()
        sub["absNES"] = sub.NES.abs()
        sub = sub.sort_values(["padj", "absNES", "term_id"], ascending=[True, False, True])
        retained = []
        for r in sub.itertuples():
            lead = set(r.leading_edge_genes.split(";"))
            if any(len(lead & old) / len(lead | old) > 0.5 for old in retained):
                continue
            chosen.append(dict(question=q, database=r.database, term_id=r.term_id,
                               term_name=r.term_name, NES=float(r.NES), padj=float(r.padj),
                               leading_edge_n=int(r.leading_edge_n)))
            retained.append(lead)
            if len(retained) == 2:
                break
    return chosen


def figure_pathways(chosen):
    fig = plt.figure(figsize=(17, 11.5))
    grid = fig.add_gridspec(5, 3, width_ratios=[4.9, 3.5, 2.9], hspace=0.66, wspace=0.04)
    max_abs = max([abs(x["NES"]) for x in chosen] + [2.0]) + 0.5
    for row_index, q in enumerate(AXES):
        name_ax = fig.add_subplot(grid[row_index, 0])
        plot_ax = fig.add_subplot(grid[row_index, 1])
        value_ax = fig.add_subplot(grid[row_index, 2])
        name_ax.axis("off")
        value_ax.axis("off")
        name_ax.set_xlim(0, 1)
        name_ax.set_ylim(-0.55, 1.55)
        value_ax.set_xlim(0, 1)
        value_ax.set_ylim(-0.55, 1.55)
        terms = [x for x in chosen if x["question"] == q]
        plot_ax.axvline(0, color="#777777", linewidth=0.8)
        plot_ax.set_xlim(-max_abs, max_abs)
        plot_ax.set_ylim(-0.55, 1.55)
        plot_ax.set_yticks([])
        plot_ax.set_xticks([-3, -2, -1, 0, 1, 2, 3])
        plot_ax.grid(axis="x", alpha=0.14)
        name_ax.text(0, 1.26, f"{q} — {LABELS[q]}", fontsize=11, fontweight="bold",
                     va="center", transform=name_ax.transData)
        if not terms:
            name_ax.text(0, 0.50, "No predefined mapped GSEA term at FDR < 0.05", color="#555555", va="center")
            continue
        for i, x in enumerate(terms):
            y = 0.76 - i * 0.72
            color = "#c45a3c" if x["NES"] > 0 else "#3978a8"
            label = f"{x['database']}: {x['term_name']}"
            if len(label) > 64:
                label = label[:61] + "…"
            name_ax.text(0, y, label, va="center", fontsize=8.5)
            plot_ax.plot([0, x["NES"]], [y, y], color=color, lw=2.5)
            size = min(160, 34 + 24 * max(0, -np.log10(max(x["padj"], 1e-3))))
            plot_ax.scatter([x["NES"]], [y], s=size, color=color, edgecolor="white", linewidth=0.6, zorder=3)
            value_ax.text(0, y, f"NES {x['NES']:+.2f}  |  FDR {display_fdr(x['padj'])}\nleading edge: {x['leading_edge_n']} IDs",
                          va="center", fontsize=8.3)
        if q == "Q4":
            value_ax.text(0, -0.42, "Angiogenesis-specific terms: none at FDR < 0.05", fontsize=8, color="#555555")
    fig.text(0.59, 0.063, "NES: positive = ECEV-higher genes; negative = ECEV-lower genes", ha="center", fontsize=9)
    fig.suptitle("EXP001-C4: prespecified program families — GSEA primary evidence", fontsize=14)
    fig.text(0.5, 0.022, "At most 2 terms/question; FDR then |NES|; leading-edge Jaccard >0.5 removed within question. Related terms are not independent findings.",
             ha="center", fontsize=8)
    fig.savefig(OUT / "figures/fig08_pathway_enrichment.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def figure_evidence_map(integration, top):
    fig, ax = plt.subplots(figsize=(14, 8.8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis("off")
    for y, text in ((8.3, "ECEV exposure"), (7.35, "Primary human dermal fibroblast"),
                    (6.4, "C3 transcriptomic state difference (n=3 per condition)")):
        ax.text(7, y, text, ha="center", va="center", fontsize=13,
                bbox=dict(boxstyle="round,pad=0.5", fc="#e9eff5", ec="#66809b"))
    for y1, y2 in ((8.06, 7.68), (7.11, 6.73)):
        ax.annotate("", xy=(7, y2), xytext=(7, y1), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.annotate("", xy=(7, 5.60), xytext=(7, 6.12), arrowprops=dict(arrowstyle="->", lw=1.5))
    xs = [1.55, 4.25, 7, 9.75, 12.45]
    df = integration.set_index("question")
    for x, (q, axis) in zip(xs, AXES.items()):
        row = df.loc[q]
        gs = top[q]["GSEA"]
        if gs:
            directions = sorted({v["direction"] for v in gs})
            gsea_text = ", ".join(directions) + f"; {len(gs)} top shown"
        else:
            gsea_text = "no mapped FDR<0.05"
        direct = int(row.literature_direct_evidence_count)
        indirect = int(row.literature_indirect_evidence_count)
        face = "#fff4ec" if row.overall_evidence_status == "SUPPORTED" else "#edf2f5"
        if q == "Q4":
            face = "#f0f0f0"
        content = (f"{q}  {['P','M','E','A','I'][int(q[1])-1]}\n"
                   f"{LABELS[q].split('/')[0].strip()}\n\n"
                   f"GSEA: {gsea_text}\n"
                   f"Literature DIRECT: {direct}\n"
                   f"Literature INDIRECT: {indirect}\n"
                   f"Status: {row.overall_evidence_status}")
        if q == "Q4":
            content = ("Q4  A\nVascular/endothelial\nGSEA: related DOWN terms\n"
                       "Angiogenesis-specific: no FDR<0.05\n"
                       f"Literature DIRECT: {direct}\nLiterature INDIRECT: {indirect}\n"
                       "Broad program status: SUPPORTED\nNo direct angiogenesis study")
        ax.text(x, 4.5, content, ha="center", va="center", fontsize=8.4,
                bbox=dict(boxstyle="round,pad=0.55", fc=face, ec="#666666", lw=1.1))
    ax.text(7, 1.7, "Evidence layers: ranked transcriptomic association ≠ direct cellular phenotype ≠ independent validation",
            ha="center", va="center", fontsize=11,
            bbox=dict(boxstyle="round,pad=0.6", fc="#e9eff5", ec="#66809b"))
    ax.text(7, 0.6, "Q6 requires separate external regenerative-like and fibrotic-like signatures: NOT YET TESTABLE", ha="center", fontsize=10)
    ax.text(7, 1.22, "Literature DIRECT counts include same-study and other-model evidence; they do not independently validate EXP001.", ha="center", fontsize=8)
    fig.suptitle("SkinExo evidence map — EXP001-C4", fontsize=15)
    fig.savefig(OUT / "figures/fig09_skinexo_evidence_map.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def write_report(manifest, checkpoint, integration, top, chosen, gsea):
    qs = {r.question: r for r in integration.itertuples()}
    lines = ["# SkinExo-AI EXP001-C4", "", "## Objective", "",
             "Identify transcriptomic program associations with the ECEV-versus-CTRL response in primary human dermal fibroblasts. Enrichment is association, not a directly measured repair phenotype.", "",
             "## Pre-Specified Questions", "",
             "C3.5 froze Q1 cell cycle/proliferation, Q2 migration/motility, Q3 ECM organization/remodeling, Q4 angiogenic/endothelial interaction, Q5 inflammatory/immune response, and Q6 external regenerative-like versus fibrotic-like programs. The exact source releases, keyword rules, thresholds, status logic, and figure-selection rule were frozen in [`exp001_c4_frozen_plan.json`](../configs/exp001_c4_frozen_plan.json) before enrichment. GSEA is the **primary** pathway-level evidence; ORA is secondary.", "",
             "## Input Data", "",
             "C3 and C3.5 checkpoints passed. The unchanged C3 DESeq2 all-gene and threshold-B tables were read. C3/C3.5 outputs were not modified. The ECEV-versus-CTRL contrast uses CTRL as reference; positive Wald statistic and log2FC mean higher expression in ECEV.", "",
             "## Gene Universe", "",
             f"ORA background: **{manifest['tested_gene_universe_size']:,} C3-tested gene IDs**. All had a nonblank gene symbol; {manifest['c3_duplicate_symbol_groups']} symbols represented {manifest['c3_gene_ids_in_duplicate_symbol_groups']} gene IDs. Symbol-to-gene-set mapping retained every gene ID, including duplicates. {manifest['gene_ids_in_at_least_one_source_set']:,} IDs occur in at least one of the three source collections; {manifest['gene_ids_absent_all_source_sets']:,} occur in none and are listed in [`c4_unmapped_gene_ids.csv`](../outputs/exp001/c4_unmapped_gene_ids.csv). Sets were restricted to tested IDs; eligible effective sizes were 15–500. The tested universe, rather than the whole genome, was used for ORA.", "",
             "## Gene Ranking", "",
             f"All **{manifest['ranked_gene_count']:,}** tested gene IDs were ranked by the DESeq2 Wald `stat` descending, with gene_id as a deterministic tie rule (no ties occurred). No significance filter or adjusted-p ranking was used. [`c4_ranked_genes.csv`](../outputs/exp001/c4_ranked_genes.csv) preserves the ranking and C3 values.", "",
             "## Gene-Set Sources", "",
             f"[MSigDB human {manifest['database_release']}](https://www.gsea-msigdb.org/gsea/msigdb/collections.jsp) supplied all three collections. The [release notes]({manifest['release_note_url']}) record the underlying GO and Reactome versions. Exact GMT URLs and SHA-256 hashes are preserved in [`c4_gene_set_manifest.json`](../outputs/exp001/c4_gene_set_manifest.json); the small GMT files are cached under Git-ignored `data/raw/c4_gene_sets/`. Source gene sets are not checked into the repository. Of {manifest['source_term_count']:,} source sets, {manifest['eligible_term_count']:,} had 15–500 C3-tested gene IDs and were analyzed. The source release details are: GO BP — {manifest['source_release_details']['GO_BP']}; Reactome — {manifest['source_release_details']['Reactome']}; Hallmark — {manifest['source_release_details']['Hallmark']}. Consult the [MSigDB license]({manifest['license_url']}) before redistribution.", "",
             "The initial predefined Q5 lexical pattern accidentally matched `CYTOKINESIS` through the prefix `CYTOKINE`. The documented QA correction required `CYTOKINE` to end or be followed by an underscore; it removed cell-division false positives from Q5 irrespective of significance. No question, threshold, or additional term family changed; the complete analysis was rerun. The correction is recorded in the frozen-plan JSON and checkpoint.", "",
             "## ORA", "",
             f"Hypergeometric upper-tail tests used the 16,271 tested IDs, separately for **995 UP** and **1,037 DOWN** threshold-B genes. Benjamini–Hochberg correction was applied across all {manifest['eligible_term_count']:,} eligible terms from all three collections separately per direction. Complete eligible-term tables, including nonsignificant terms and zero overlaps: [`UP`](../outputs/exp001/c4_ora_up_all.csv) and [`DOWN`](../outputs/exp001/c4_ora_down_all.csv). Significant terms at FDR < 0.05: **{checkpoint['ora_up_significant_count']:,} UP**, **{checkpoint['ora_down_significant_count']:,} DOWN**. ORA is secondary to the ranked analysis; overlapping gene sets are not independent findings.", "",
             "## GSEA", "",
             f"GSEApy **1.3.1** preranked GSEA used all {manifest['ranked_gene_count']:,} Wald statistics, weighted running score (weight 1), 1,000 gene-set permutations, seed 42, and a single combined three-collection run so reported FDR is estimated across the combined tested sets. Complete results: [`c4_gsea_all.csv`](../outputs/exp001/c4_gsea_all.csv), with NES, nominal p, FDR, and leading-edge IDs/symbols. **{checkpoint['gsea_significant_count']:,}** sets have FDR < 0.05. Positive NES associates a set with ECEV-higher genes; negative NES with ECEV-lower genes. It does **not** indicate beneficial or harmful repair. Permutation p-values have finite resolution; numeric zeros in estimated nominal p or FDR are displayed as <0.001 in figures/text, not exact zero probability. Gene-set permutations do not capture all uncertainty from n=3/group. Leading-edge coherence was prespecified as ≥5 genes and ≥80% Wald-stat sign agreement with NES.", ""]
    for q, heading in (("Q1", "Proliferation / Cell Cycle"), ("Q2", "Migration / Motility"),
                       ("Q3", "ECM Organization / Remodeling"), ("Q4", "Angiogenesis / Endothelial Interaction"),
                       ("Q5", "Inflammation / Immune Response")):
        r = qs[q]
        lines += [f"## {q} — {heading}", "", f"**PRE-SPECIFIED. Status: {r.overall_evidence_status}.** {r.interpretation}", "",
                  f"GSEA primary: {r.GSEA_support}. ORA secondary: UP {r.ORA_up_support}; DOWN {r.ORA_down_support}.", ""]
        for x in top[q]["GSEA"]:
            lines.append(f"- GSEA {x['database']} `{x['term_id']}`: NES {x['NES']:+.3f}, FDR {display_fdr(x['padj'])}, leading edge n={x['leading_edge_n']}, same-sign fraction {x['leading_edge_same_sign_fraction']:.2f}.")
        if not top[q]["GSEA"]:
            lines.append("- No predefined mapped set reached GSEA FDR < 0.05.")
        lines += ["", f"Literature coding: DIRECT {r.literature_direct_evidence_count}, INDIRECT {r.literature_indirect_evidence_count}; independent external DIRECT {r.literature_independent_direct_evidence_count}. {r.limitations}", ""]
        if q == "Q1":
            lines += ["E2F/G2M and related leading edges support a **cell-cycle transcriptional program** among ECEV-higher genes. C4 did not measure cell division or proliferation. These overlapping sets are related annotations, not independent confirmations.", ""]
        elif q == "Q2":
            lines += ["The strongest mapped terms concern **chemotaxis regulation**, including negative chemotaxis, among ECEV-lower genes. This is not a direct fibroblast migration assay and does not establish increased or decreased cell motility.", ""]
        elif q == "Q3":
            lines += ["Collagen-fibril and ECM-organization terms show negative NES, associating them with ECEV-lower genes. This does not measure collagen deposition, matrix architecture, or scar outcome in C4.", ""]
        elif q == "Q4":
            q4ids = set(pd.read_csv(META / "skinexo_c4_term_map.csv").query("question == 'Q4' and eligible_for_testing").term_id)
            angiogenesis = gsea[gsea.term_id.isin(q4ids) & gsea.term_id.str.contains("ANGIOGENESIS", regex=False)]
            lines += [f"The significant predefined Q4 terms concern vascular-associated smooth-muscle proliferation and endothelial-cell apoptosis; **no term containing `ANGIOGENESIS` reached GSEA FDR < 0.05** ({len(angiogenesis)} eligible angiogenesis-named terms checked). Q4's rule-based `SUPPORTED` status applies only to the broad vascular/endothelial transcriptomic family. Angiogenesis itself and an angiogenic phenotype remain unsupported by this analysis; C3.5 direct angiogenesis evidence is zero.", ""]
        elif q == "Q5":
            lines += ["The strongest remaining Q5 terms include IL-12/JAK–STAT and immune-receptor annotations. Such gene-set labels in bulk fibroblast RNA-seq do not demonstrate immune-cell behavior or a beneficial inflammatory state. The cell-division `CYTOKINESIS` false matches were removed by the documented mapping QA correction.", ""]
    lines += ["## Q6 — Regenerative vs Fibrotic Programs", "",
              "**PRE-SPECIFIED; NOT YET TESTABLE.** Regenerative-like and fibrotic-like require **separate externally defined directional signatures**. C3.5 verified GSE141814, but it has one pooled mouse scRNA-seq library per fate and no validated signed signatures were cataloged. Deriving a signature would require additional external analysis and species/ortholog handling, so neither GSEA nor ORA was run for Q6. The two contexts were not treated as opposite ends of a single score.", "",
              "## Evidence Integration", "",
              "[`c4_evidence_integration.csv`](../outputs/exp001/c4_evidence_integration.csv) combines mapped GSEA (primary), ORA (secondary), and C3.5 direct/indirect literature counts. A `SUPPORTED` label refers only to a transcriptomic program association with coherent GSEA plus same-direction ORA; it never denotes experimentally verified proliferation, migration, ECM change, angiogenesis, inflammation, or wound healing. P00 is the same source study as GSE293186 and is not independent validation. Literature counts span different models and may include non-EV experiments. The pathway and evidence-map figures encode the differences: [Figure 8](../outputs/exp001/figures/fig08_pathway_enrichment.png), [Figure 9](../outputs/exp001/figures/fig09_skinexo_evidence_map.png). Figure 8 uses the frozen FDR/|NES| and leading-edge Jaccard >0.5 redundancy rule within each question; all terms remain in the result tables.", "",
              "## Post-Hoc Exploratory Findings", "",
              "**None promoted to a biological claim.** Unmapped significant terms remain in the complete ORA/GSEA tables. Any later narrative about them must be labeled `POSTHOC_EXPLORATORY` and cannot change the frozen Q1–Q6 interpretation.", "",
              "## Limitations", "",
              "n=3 biological replicates per condition; one bulk RNA-seq experiment; overlapping and annotation-dependent gene sets; gene-set permutation uncertainty; symbol mapping from C3 annotations; no new phenotype assay. Q4's C3.5 literature direct angiogenesis count remains zero even if vascular terms enrich. Cell-cycle transcription is not proof of increased proliferation. The GSE293186 primary paper and author DEG archive are same-dataset evidence, not independent validation. Q6 is untested. No SkinExo numerical score or machine-learning model was produced.", "",
              "## C4 Decision", "",
              f"**{'PASS' if checkpoint['overall_pass'] else 'REVIEW REQUIRED'}** for the prespecified pathway-analysis checkpoint, with Q6 explicitly `NOT_YET_TESTABLE`. This decision assesses execution and documentation, not therapeutic efficacy or validation of any phenotype.", ""]
    (ROOT / "reports/EXP001_C4_pathway_analysis.md").write_text("\n".join(lines))


def analyze():
    c3, c35, plan, de, evidence, up, down = checks()
    manifest = read_json(OUT / "c4_gene_set_manifest.json")
    if manifest.get("frozen_plan_sha256") != hashlib.sha256(PLAN_PATH.read_bytes()).hexdigest():
        raise RuntimeError("Prepared C4 inputs were generated with a different frozen plan; run prepare again")
    terms, counts, membership, id_to_symbol = load_sets(plan, de)
    ranked = pd.read_csv(OUT / "c4_ranked_genes.csv")
    mapped = pd.read_csv(META / "skinexo_c4_term_map.csv")
    if len(ranked) != len(de) or set(ranked.gene_id) != set(de.gene_id):
        raise RuntimeError("Prepared ranking differs from C3 tested universe")
    if not mapped.predefined_or_posthoc.eq("PREDEFINED").all():
        raise RuntimeError("Primary term map contains posthoc rows")
    ora_up = run_ora(terms, up, "UP", id_to_symbol, len(de))
    ora_down = run_ora(terms, down, "DOWN", id_to_symbol, len(de))
    ora_up.to_csv(OUT / "c4_ora_up_all.csv", index=False)
    ora_down.to_csv(OUT / "c4_ora_down_all.csv", index=False)
    gsea = run_gsea(plan, ranked, terms, id_to_symbol)
    gsea.to_csv(OUT / "c4_gsea_all.csv", index=False)
    integration, top = integrate(plan, mapped, ora_up, ora_down, gsea, evidence)
    integration.to_csv(OUT / "c4_evidence_integration.csv", index=False)
    chosen = choose_figure_terms(mapped, gsea)
    (OUT / "c4_figure_selection.json").write_text(json.dumps(chosen, indent=2) + "\n")
    figure_pathways(chosen)
    figure_evidence_map(integration, top)
    limitations = ["n=3 biological replicates per condition; one bulk RNA-seq dataset.",
                   "GSEA gene-set permutations do not represent sample-label uncertainty and finite permutations limit nominal p resolution.",
                   "Overlapping GO/Reactome terms and HGNC symbol mapping limit independence and annotation coverage.",
                   "Enrichment is transcriptomic association, not direct phenotype measurement or therapeutic benefit.",
                   "The GSE293186 paper and author DEG table are same-dataset evidence, not independent validation.",
                   "C3.5 has zero direct angiogenesis studies in the verified set; Q4 cannot establish angiogenesis.",
                   "Q6 has no verified separate external signed regenerative-like and fibrotic-like signatures; not tested."]
    checkpoint = dict(dataset="GSE293186", experiment="EXP001", checkpoint="EXP001-C4 Pre-Specified Biological Pathway Analysis",
                      c3_overall_pass=True, c3_5_overall_pass=True,
                      tested_gene_universe_size=len(de), ranked_gene_count=len(ranked),
                      gene_identifier_mapping=manifest["symbol_mapping"],
                      unmapped_gene_id_count=manifest["gene_ids_absent_all_source_sets"],
                      gene_set_sources=manifest["collections"],
                      ora_up_significant_count=int((ora_up.padj < 0.05).sum()),
                      ora_down_significant_count=int((ora_down.padj < 0.05).sum()),
                      gsea_significant_count=int((gsea.padj < 0.05).sum()),
                      gsea_primary=True, ora_secondary=True,
                      mapping_qa_correction=plan.get("mapping_qa_correction"),
                      **{f"{q}_status": integration.set_index("question").loc[q, "overall_evidence_status"] for q in AXES},
                      Q6_status="NOT_YET_TESTABLE",
                      **{f"{q}_top_evidence": top[q] for q in [*AXES, "Q6"]},
                      posthoc_findings=[], limitations=limitations,
                      overall_pass=(len(gsea) == manifest["eligible_term_count"] and
                                    len(ora_up) == manifest["eligible_term_count"] and
                                    len(ora_down) == manifest["eligible_term_count"]))
    (OUT / "exp001_c4_pathways.json").write_text(json.dumps(checkpoint, indent=2) + "\n")
    write_report(manifest, checkpoint, integration, top, chosen, gsea)
    print(json.dumps({k: checkpoint[k] for k in ("tested_gene_universe_size", "ranked_gene_count", "ora_up_significant_count", "ora_down_significant_count", "gsea_significant_count", "Q1_status", "Q2_status", "Q3_status", "Q4_status", "Q5_status", "Q6_status", "overall_pass")}, indent=2))
    if not checkpoint["overall_pass"]:
        raise RuntimeError("Incomplete ORA/GSEA result table")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"prepare", "analyze"}:
        raise SystemExit("Usage: python experiments/exp001/04_pathway_analysis.py prepare|analyze")
    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    if sys.argv[1] == "prepare":
        prepare()
    else:
        analyze()
