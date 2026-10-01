"""EXP001-C3 figures, independent author-table QA, and final checkpoint report."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "skinexo_mpl"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import leaves_list, linkage


AUTHOR_URL = (
    "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE293nnn/GSE293186/suppl/"
    "GSE293186_ECEV_72hvsCTRL_72h_deg_all.csv.gz"
)
DESEQ2_URL = "https://bioconductor.org/packages/release/bioc/vignettes/DESeq2/inst/doc/DESeq2.html"


def root_from_script() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "data" / "raw").is_dir() and (parent / "experiments" / "exp001").is_dir():
            return parent
    raise RuntimeError("Could not find SkinExo-AI project root")


def nfmt(value: float) -> str:
    return "0 (underflow)" if value == 0 else f"{value:.3g}"


def top_table(rows: pd.DataFrame) -> str:
    lines = ["| Gene ID | Symbol | log2FC | padj |", "| --- | --- | ---: | ---: |"]
    for row in rows.head(10).itertuples(index=False):
        symbol = row.gene_symbol if pd.notna(row.gene_symbol) else "NA"
        lines.append(f"| {row.gene_id} | {symbol} | {row.log2FoldChange:+.3f} | {nfmt(row.padj)} |")
    return "\n".join(lines)


def main() -> None:
    root = root_from_script()
    outputs = root / "outputs/exp001"
    figures = outputs / "figures"
    c1 = json.loads((outputs / "exp001_c1_integrity.json").read_text())
    c2 = json.loads((outputs / "exp001_c2_qc.json").read_text())
    if c1.get("overall_pass") is not True or c2.get("overall_pass") is not True:
        raise RuntimeError("C1 and C2 must both pass")
    summary = json.loads((outputs / "deg_summary.json").read_text())
    results = pd.read_csv(outputs / "differential_expression_all.csv")
    required = {"gene_id", "gene_symbol", "baseMean", "log2FoldChange", "lfcSE", "stat", "pvalue", "padj"}
    if not required.issubset(results.columns) or results["gene_id"].duplicated().any():
        raise ValueError("Invalid independent DESeq2 result table")
    if len(results) != summary["genes_tested"]:
        raise ValueError("DESeq2 result count differs from summary")
    sig_a = results["padj"].lt(0.05).fillna(False)
    sig_b = (sig_a & results["log2FoldChange"].abs().ge(1).fillna(False))
    up = results.loc[sig_b & results["log2FoldChange"].ge(1)].sort_values("padj")
    down = results.loc[sig_b & results["log2FoldChange"].le(-1)].sort_values("padj")
    if (int(sig_a.sum()), int(sig_b.sum()), len(up), len(down)) != (
        summary["padj_lt_0_05"], summary["threshold_b_total"],
        summary["threshold_b_up"], summary["threshold_b_down"]
    ):
        raise ValueError("DESeq2 threshold summary disagrees with result table")

    # Volcano: all tested genes remain visible. A single padj=0 from floating-point
    # underflow is displayed just above the smallest representable positive padj.
    positive_padj = results.loc[results["padj"] > 0, "padj"]
    if positive_padj.empty:
        raise ValueError("No positive adjusted p-values for volcano plot")
    padj_floor = float(positive_padj.min() / 10)
    plot_padj = results["padj"].fillna(1).clip(lower=padj_floor)
    volcano_y = -np.log10(plot_padj)
    status = np.where(sig_b & results["log2FoldChange"].ge(1), "Significant up",
                      np.where(sig_b & results["log2FoldChange"].le(-1),
                               "Significant down", "Other tested genes"))
    fig, ax = plt.subplots(figsize=(10, 7), constrained_layout=True)
    for label, color, size, alpha in (
        ("Other tested genes", "#a3aab0", 8, 0.4),
        ("Significant down", "#2776ae", 11, 0.7),
        ("Significant up", "#c2573c", 11, 0.7),
    ):
        mask = status == label
        ax.scatter(results.loc[mask, "log2FoldChange"], volcano_y.loc[mask],
                   c=color, s=size, alpha=alpha, linewidths=0, label=f"{label} ({int(mask.sum()):,})")
    ax.axvline(-1, color="#555555", ls="--", lw=0.8)
    ax.axvline(1, color="#555555", ls="--", lw=0.8)
    ax.axhline(-np.log10(0.05), color="#555555", ls="--", lw=0.8)
    top_labels = results.loc[sig_b].sort_values(["padj", "gene_id"]).head(10)
    for rank, row in enumerate(top_labels.itertuples(index=False)):
        point_y = float(volcano_y.loc[results["gene_id"] == row.gene_id].iloc[0])
        x_offset = 10 if row.log2FoldChange >= 0 else -10
        y_offset = 7 if rank % 2 == 0 else -9
        ax.annotate(row.gene_symbol if pd.notna(row.gene_symbol) else row.gene_id,
                    (row.log2FoldChange, point_y), xytext=(x_offset, y_offset),
                    textcoords="offset points", ha="left" if x_offset > 0 else "right",
                    fontsize=8, arrowprops={"arrowstyle": "-", "lw": 0.4, "color": "#555555"})
    ax.set_xlabel("log2 fold change (ECEV vs CTRL)")
    ax.set_ylabel("−log10(BH-adjusted p-value)")
    ax.set_title("GSE293186 volcano plot · DESeq2 Wald test")
    ax.legend(frameon=False, markerscale=2, loc="upper right")
    ax.margins(x=0.12, y=0.08)
    fig.savefig(figures / "fig06_volcano.png", dpi=180)
    plt.close(fig)

    heatmap = pd.read_csv(outputs / "de_heatmap_expression.csv")
    samples = pd.read_csv(root / "data/metadata/GSE293186_samples.csv")["count_column"].tolist()
    expected_top_ids = results.loc[sig_b, "gene_id"].head(30).tolist()
    if heatmap["gene_id"].tolist() != expected_top_ids or not set(samples).issubset(heatmap.columns):
        raise ValueError("Heatmap expression does not match the top 30 threshold-B genes")
    expression = heatmap[samples].to_numpy(dtype=float)
    if not np.isfinite(expression).all():
        raise ValueError("Non-finite transformed heatmap expression")
    row_means = expression.mean(axis=1, keepdims=True)
    row_sds = expression.std(axis=1, ddof=1, keepdims=True)
    if (row_sds == 0).any():
        raise ValueError("A selected heatmap gene has zero transformed variance")
    z = (expression - row_means) / row_sds
    gene_order = leaves_list(linkage(z, method="average", metric="euclidean"))
    selected = results.set_index("gene_id").loc[heatmap["gene_id"]]
    symbols = []
    selected_symbols = selected["gene_symbol"].fillna("")
    for gene_id, symbol in zip(heatmap["gene_id"], selected_symbols):
        if not symbol:
            symbols.append(gene_id)
        elif int((selected_symbols == symbol).sum()) > 1:
            symbols.append(f"{symbol} ({gene_id})")
        else:
            symbols.append(symbol)
    fig, ax = plt.subplots(figsize=(9, 10), constrained_layout=True)
    heat = ax.imshow(z[gene_order], aspect="auto", cmap="RdBu_r", vmin=-2, vmax=2)
    ax.set_xticks(range(6), samples, rotation=45, ha="right")
    ax.set_yticks(range(len(gene_order)), [symbols[i] for i in gene_order], fontsize=8)
    ax.set_title("Top 30 threshold-B genes · blind VST, row z-scores")
    fig.colorbar(heat, ax=ax, label="Row z-score", shrink=0.75)
    fig.savefig(figures / "fig07_de_heatmap.png", dpi=180)
    plt.close(fig)

    author_path = root / "data/raw/GSE293186_ECEV_72hvsCTRL_72h_deg_all.csv.gz"
    if not author_path.is_file():
        raise FileNotFoundError(f"Official author DEG archive missing: {author_path}")
    author = pd.read_csv(author_path)
    author_required = {"gene_id", "gene_name", "log2FoldChange", "padj"}
    if not author_required.issubset(author.columns) or author["gene_id"].duplicated().any():
        raise ValueError("Cannot unambiguously map author DEG rows by gene_id")
    raw = pd.read_csv(root / "data/raw/GSE293186_gene_count.csv.gz",
                      usecols=["gene_id"] + samples)
    author_raw = author.merge(raw, on="gene_id", how="left", validate="one_to_one",
                              suffixes=("_author", "_raw"))
    if author_raw["gene_id"].isna().any() or len(author_raw) != len(author):
        raise ValueError("Author gene IDs do not map uniquely to raw matrix")
    count_mismatch = 0
    for sample in samples:
        author_col = f"{sample}_count"
        if author_col not in author_raw:
            raise ValueError(f"Author sample count column missing: {author_col}")
        count_mismatch += int((author_raw[author_col] != author_raw[f"{sample}_raw"]).sum())

    ours = results[["gene_id", "gene_symbol", "log2FoldChange", "padj"]].rename(
        columns={"log2FoldChange": "ours_log2FoldChange", "padj": "ours_padj"})
    author_subset = author[["gene_id", "gene_name", "log2FoldChange", "padj"]].rename(
        columns={"gene_name": "author_gene_symbol", "log2FoldChange": "author_log2FoldChange",
                 "padj": "author_padj"})
    concordance = ours.merge(author_subset, on="gene_id", how="outer", indicator=True,
                             validate="one_to_one")
    concordance["comparison_status"] = concordance["_merge"].map({
        "both": "both", "left_only": "ours_tested_not_author_reported",
        "right_only": "author_reported_not_tested_by_ours",
    })
    concordance = concordance.drop(columns="_merge")
    matched = concordance["comparison_status"] == "both"
    comparable = matched & concordance["ours_log2FoldChange"].notna() & concordance["author_log2FoldChange"].notna()
    concordance["direction_agreement"] = pd.Series(pd.NA, index=concordance.index, dtype="boolean")
    concordance.loc[comparable, "direction_agreement"] = (
        np.sign(concordance.loc[comparable, "ours_log2FoldChange"])
        == np.sign(concordance.loc[comparable, "author_log2FoldChange"])
    ).to_numpy()
    concordance["ours_threshold_b"] = (
        concordance["ours_padj"].lt(0.05) & concordance["ours_log2FoldChange"].abs().ge(1)
    ).fillna(False)
    concordance["author_threshold_b"] = (
        concordance["author_padj"].lt(0.05) & concordance["author_log2FoldChange"].abs().ge(1)
    ).fillna(False)
    concordance = concordance.sort_values(["comparison_status", "author_padj", "ours_padj", "gene_id"],
                                          na_position="last")
    concordance.to_csv(outputs / "author_deg_concordance.csv", index=False, float_format="%.10g")

    paired = concordance.loc[comparable]
    direction_fraction = float(paired["direction_agreement"].mean())
    pearson = float(paired["ours_log2FoldChange"].corr(paired["author_log2FoldChange"], method="pearson"))
    spearman = float(paired["ours_log2FoldChange"].corr(paired["author_log2FoldChange"], method="spearman"))
    author_sig_a = author["padj"].lt(0.05)
    author_sig_b = author_sig_a & author["log2FoldChange"].abs().ge(1)
    overlap_a = int((matched & concordance["ours_padj"].lt(0.05) & concordance["author_padj"].lt(0.05)).sum())
    overlap_b = int((concordance["ours_threshold_b"] & concordance["author_threshold_b"]).sum())
    ours_b_total = int(sig_b.sum())
    author_b_total = int(author_sig_b.sum())
    union_b = ours_b_total + author_b_total - overlap_b
    author_not_tested = int((concordance["comparison_status"] == "author_reported_not_tested_by_ours").sum())
    ours_b_not_author = ours_b_total - overlap_b
    author_b_not_ours = author_b_total - overlap_b
    author_matched_not_ours_b = int((matched & concordance["author_threshold_b"] & ~concordance["ours_threshold_b"]).sum())
    lfc_abs_diff = (paired["ours_log2FoldChange"] - paired["author_log2FoldChange"]).abs()
    author_metrics = {
        "author_source_url": AUTHOR_URL,
        "author_file_rows": len(author),
        "author_all_padj_lt_0_05": bool(author_sig_a.all()),
        "author_all_abs_log2fc_ge_1": bool(author["log2FoldChange"].abs().ge(1).all()),
        "author_raw_count_mismatches": count_mismatch,
        "our_tested_genes": len(results),
        "genes_compared": int(comparable.sum()),
        "author_rows_not_tested_after_our_filter": author_not_tested,
        "log2fc_pearson": pearson,
        "log2fc_spearman": spearman,
        "direction_concordance": direction_fraction,
        "median_absolute_log2fc_difference": float(lfc_abs_diff.median()),
        "max_absolute_log2fc_difference": float(lfc_abs_diff.max()),
        "author_padj_lt_0_05": int(author_sig_a.sum()),
        "author_threshold_b_total": author_b_total,
        "our_threshold_a_overlap_with_author": overlap_a,
        "threshold_b_overlap": overlap_b,
        "threshold_b_jaccard": overlap_b / union_b,
        "our_threshold_b_not_in_author_file": ours_b_not_author,
        "author_threshold_b_not_in_our_significant_table": author_b_not_ours,
        "author_tested_but_not_our_threshold_b": author_matched_not_ours_b,
    }
    warnings = [
        "n=3 biological replicates per condition; DE estimates and outlier handling are sensitive to individual samples.",
        "The author archive is a thresholded subset, so it cannot establish agreement over all tested genes.",
    ]
    if author_not_tested:
        warnings.append(f"{author_not_tested} author-reported genes did not pass our prespecified count filter.")
    if ours_b_not_author:
        warnings.append(f"{ours_b_not_author} of our threshold-B genes are absent from the author archive.")
    if author_matched_not_ours_b:
        warnings.append(f"{author_matched_not_ours_b} author genes were tested by us but did not meet our threshold B.")
    if count_mismatch:
        warnings.append(f"Author per-sample raw counts differ from the GEO count matrix in {count_mismatch} cells.")
    if (results["padj"] == 0).any():
        warnings.append("One adjusted p-value underflowed to zero; its volcano y-value uses a documented plotting floor.")

    overall_pass = bool(
        summary["genes_tested"] > 0 and count_mismatch == 0
        and len(paired) > 0 and direction_fraction >= 0.95 and pearson >= 0.9
    )
    checkpoint = {**summary,
        "c1_overall_pass": True,
        "c2_overall_pass": True,
        "author_deg_concordance": author_metrics,
        "warnings": warnings,
        "overall_pass": overall_pass,
        "volcano_padj_zero_plot_floor": padj_floor,
        "heatmap_transform": "DESeq2 vst(dds, blind=TRUE); row z-score across six samples",
        "heatmap_gene_selection": "top 30 threshold-B genes by padj, ties by gene_id",
    }
    (outputs / "exp001_c3_de.json").write_text(json.dumps(checkpoint, indent=2) + "\n")

    report = f"""# SkinExo-AI EXP001-C3

## Objective

Identify genes with evidence of differential expression between ECEV-treated and control primary human dermal fibroblasts after 72 hours.

## Dataset

- [NCBI GEO GSE293186](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE293186): six samples, three CTRL and three ECEV.
- C1 and C2 checkpoints: **PASS**. C3 reads the official raw integer count matrix and verified sample metadata, not log-CPM or the author DEG table.
- Gene ID (`gene_id`) is the stable row key. `gene_name` in the source matrix is preserved as `gene_symbol`; description, biotype, location, length and TF family are also preserved when available. Symbols may repeat across gene IDs.

## Statistical Framework

[DESeq2]({DESEQ2_URL}) negative-binomial count model, standard dispersion estimation, Wald test, and Benjamini–Hochberg adjusted p-values. R **{summary['r_version']}**, Bioconductor **{summary['bioconductor_version']}**, DESeq2 **{summary['deseq2_version']}**. Package manifest and local setup are documented in `configs/exp001_c3_r_environment.md`.

## Filtering

- Genes before filtering: **{summary['genes_before_filtering']:,}**.
- Fixed label-blind rule: **{summary['filter_rule']}**.
- Genes after filtering and tested: **{summary['genes_tested']:,}**.
- Filtering was selected before examining differential-expression results. DESeq2's result-level independent filtering remains at its standard setting.

## Design

`design = ~ condition` with CTRL as the reference. All six biological samples are included; no sample was removed.

## Contrast Definition

`results(dds, contrast = c("condition", "ECEV", "CTRL"))`. **Positive log2FoldChange means higher expression in ECEV; negative means lower expression in ECEV.** Fold changes are unshrunken DESeq2 estimates.

## Differential Expression Results

- [Complete DE result table](../outputs/exp001/differential_expression_all.csv): **{summary['genes_tested']:,}** tested genes, sorted by padj with NA last.
- Threshold A (`padj < 0.05`): **{summary['padj_lt_0_05']:,}** genes.
- Threshold B (`padj < 0.05` and `|log2FC| >= 1`): **{summary['threshold_b_total']:,}** genes. [Threshold-B table](../outputs/exp001/differential_expression_significant.csv).
- Threshold B up/down: **{summary['threshold_b_up']:,}** / **{summary['threshold_b_down']:,}**.
- NA p-values / padj values: **{summary['pvalue_na']} / {summary['padj_na']}**.

## Upregulated Genes

Top 10 ECEV-higher genes by adjusted p-value among threshold-B genes (not manually selected):

{top_table(up)}

## Downregulated Genes

Top 10 ECEV-lower genes by adjusted p-value among threshold-B genes (not manually selected):

{top_table(down)}

## MA Plot

[Figure 5](../outputs/exp001/figures/fig05_ma_plot.png) shows DESeq2 mean normalized counts versus log2 fold change. Blue marks padj < 0.05. The y-axis spans **{summary['ma_plot_ylim'][0]:.3f} to {summary['ma_plot_ylim'][1]:.3f}**, covering every finite fold change; no extreme gene was clipped.

## Volcano Plot

[Figure 6](../outputs/exp001/figures/fig06_volcano.png) plots log2FC against −log10(padj); up/down colors apply threshold B. Labels are the 10 most adjusted-significant threshold-B genes. One padj is numerically zero from floating-point underflow and is shown at a plotting floor of **{padj_floor:.3g}**, one order of magnitude below the smallest positive padj. This changes its display coordinate only.

## Heatmap

[Figure 7](../outputs/exp001/figures/fig07_de_heatmap.png) shows the top **{len(heatmap):,}** threshold-B genes by padj. Values use blind DESeq2 variance-stabilizing transformation, then row z-scores for display. Gene rows are clustered with average linkage and Euclidean distance; all six sample labels remain in metadata order. The heatmap is visualization, not a statistical test.

## Author DEG Concordance

Only after saving our DESeq2 result, the [official GEO author archive]({AUTHOR_URL}) was read for QA. It has **{len(author):,}** rows; empirically every row has padj < 0.05 and |log2FC| ≥ 1. It is a thresholded subset, not a complete author test table. The author per-sample raw count columns match the GEO count matrix in all compared cells (**{count_mismatch}** mismatches).

- Author rows also tested by us: **{len(paired):,}**; author rows excluded by our count filter: **{author_not_tested:,}**.
- Pearson / Spearman correlation of shared log2FC: **{pearson:.6f} / {spearman:.6f}**.
- Fold-change direction concordance: **{direction_fraction:.1%}** of shared genes.
- Median / maximum absolute log2FC difference: **{lfc_abs_diff.median():.4f} / {lfc_abs_diff.max():.4f}**.
- Threshold-A overlap among shared genes: **{overlap_a:,}**. Threshold-B overlap: **{overlap_b:,}**; Jaccard index **{overlap_b / union_b:.3f}**.
- Our threshold-B genes absent from the author file: **{ours_b_not_author:,}**. Author threshold-B genes absent from our significant table: **{author_b_not_ours:,}** ({author_not_tested:,} not tested after our filter; {author_matched_not_ours_b:,} tested but below our threshold B).
- [Per-gene concordance table](../outputs/exp001/author_deg_concordance.csv) retains both result sets without overwriting our DE output.

These set differences are consistent with differing prefiltering and possibly DESeq2 processing choices; the author file does not document a complete analysis configuration, so their precise cause cannot be assigned here. Concordance checks external consistency and is **not independent biological validation**.

## Limitations

- **n=3 biological replicates per condition** limits precision and makes individual samples influential.
- Differential expression describes an association in this experimental comparison; transcriptomic differences alone do not establish wound-healing benefit.
- Large unshrunken log2FC values, especially at low expression, should be interpreted cautiously.
- The author archive is thresholded and cannot support a complete comparison of nonsignificant genes or the authors' total tested-gene universe.
- No GO, KEGG, Reactome, GSEA, SkinExo scoring, or AI modeling was performed.

## C3 Decision

**{'PASS' if overall_pass else 'REVIEW REQUIRED'}**. The independent count-based analysis completed, and author-table QA found {'no raw-count mismatch and strong directional agreement' if overall_pass else 'a discrepancy requiring review'}. This decision does not establish treatment causality or wound-healing benefit.
"""
    report_path = root / "reports/EXP001_C3_differential_expression.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"C3 {'PASS' if overall_pass else 'REVIEW REQUIRED'}: {len(results)} genes tested; {len(paired)} compared with author file")
    print(f"Author log2FC Pearson {pearson:.6f}; direction agreement {direction_fraction:.1%}; threshold-B overlap {overlap_b}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
