#!/usr/bin/env python3
"""EXP002-C3 robustness, figures, and report from two frozen DESeq2 fits.

This code does not open EXP001 files or run GSEA.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs/exp002"
FIG = OUT / "figures"
REPORT = ROOT / "reports/EXP002_C3_differential_expression.md"
REQUIRED = ["gene_id", "gene_symbol", "baseMean", "log2FoldChange", "lfcSE", "stat", "pvalue", "padj"]


def read_results(label: str) -> pd.DataFrame:
    frame = pd.read_csv(OUT / f"differential_expression_{label}_all.csv")
    if not set(REQUIRED).issubset(frame.columns) or frame.gene_id.isna().any() or frame.gene_id.duplicated().any():
        raise ValueError(f"Invalid {label} DE result table")
    padj = frame.padj.to_numpy(dtype=float)
    finite_padj = padj[np.isfinite(padj)]
    if np.any(np.diff(finite_padj) < 0) or (np.isnan(padj).any() and not np.isnan(padj[len(finite_padj):]).all()):
        raise ValueError(f"{label} result table is not sorted by padj")
    significant = frame.loc[frame.padj.lt(0.05) & frame.log2FoldChange.abs().ge(1)]
    saved = pd.read_csv(OUT / f"differential_expression_{label}_significant.csv")
    if list(saved.gene_id) != list(significant.gene_id):
        raise ValueError(f"{label} threshold-B table does not match complete result")
    return frame


def overlap(a: set[str], b: set[str]) -> dict[str, int | float | None]:
    union = len(a | b)
    return {"intersection": len(a & b), "union": union,
            "jaccard": len(a & b) / union if union else None}


def render_figure(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()


def main() -> None:
    model = json.loads((OUT / "exp002_c3_model_summary.json").read_text())
    c2r = json.loads((OUT / "exp002_c2r_ev8_review.json").read_text())
    plan = json.loads((ROOT / "configs/exp002_c3_robustness_plan.json").read_text())
    if not plan["declared_before_model_fit"] or c2r["EV8_decision"] != "RETAIN":
        raise ValueError("Frozen EV_8 or robustness plan mismatch")
    if model["design"] != "~ batch + condition" or model["contrast"] != "MSC_sEV vs CTRL_DMEM":
        raise ValueError("R model differs from frozen design")
    primary = read_results("primary")
    sensitivity = read_results("sensitivity")
    if len(primary) != model["primary"]["genes_tested"] or len(sensitivity) != model["sensitivity"]["genes_tested"]:
        raise ValueError("Model summary disagrees with DE result table dimensions")
    paired = primary[["gene_id", "log2FoldChange", "padj"]].merge(
        sensitivity[["gene_id", "log2FoldChange", "padj"]], on="gene_id",
        suffixes=("_primary", "_sensitivity"), validate="one_to_one")
    finite = np.isfinite(paired.log2FoldChange_primary) & np.isfinite(paired.log2FoldChange_sensitivity)
    common = paired.loc[finite].copy()
    if len(common) < 5000:
        raise ValueError("Too few shared finite DE estimates for sensitivity comparison")
    x = common.log2FoldChange_primary.to_numpy(dtype=float)
    y = common.log2FoldChange_sensitivity.to_numpy(dtype=float)
    delta = y - x
    nonzero = (x != 0) & (y != 0)
    reversals = nonzero & (np.sign(x) != np.sign(y))
    large = nonzero & (np.maximum(np.abs(x), np.abs(y)) >= 1)
    pearson = float(pearsonr(x, y).statistic)
    spearman = float(spearmanr(x, y).statistic)
    direction = float(np.mean(np.sign(x[nonzero]) == np.sign(y[nonzero]))) if nonzero.any() else None
    large_direction = float(np.mean(np.sign(x[large]) == np.sign(y[large]))) if large.any() else None
    abs_delta = np.abs(delta)
    a_primary = set(primary.loc[primary.padj.lt(0.05), "gene_id"])
    a_sensitivity = set(sensitivity.loc[sensitivity.padj.lt(0.05), "gene_id"])
    b_primary = set(primary.loc[primary.padj.lt(0.05) & primary.log2FoldChange.abs().ge(1), "gene_id"])
    b_sensitivity = set(sensitivity.loc[sensitivity.padj.lt(0.05) & sensitivity.log2FoldChange.abs().ge(1), "gene_id"])
    a_overlap = overlap(a_primary, a_sensitivity)
    b_overlap = overlap(b_primary, b_sensitivity)
    ge05 = int(np.sum(abs_delta >= 0.5))
    ge1 = int(np.sum(abs_delta >= 1.0))
    guide = plan["material_sensitivity_warning_guide"]
    warning_triggers = {
        "fraction_abs_delta_ge_0_5": ge05 / len(common) >= guide["fraction_shared_genes_abs_delta_log2fc_ge_0_5"],
        "fraction_abs_delta_ge_1": ge1 / len(common) >= guide["fraction_shared_genes_abs_delta_log2fc_ge_1"],
        "log2fc_pearson": pearson < guide["log2fc_pearson_below"],
        "effect_size_direction_concordance": large_direction is not None and large_direction < guide["effect_size_subset_direction_concordance_below"],
    }
    diagnostics = {label: model[label]["diagnostics"] for label in ("primary", "sensitivity")}
    critical = any(d["finite_pvalue_count"] < 0.5 * model[label]["genes_tested"] for label, d in diagnostics.items())
    if critical:
        decision = "REVIEW REQUIRED"
    elif any(warning_triggers.values()):
        decision = "PASS WITH SENSITIVITY WARNING"
    else:
        decision = "PASS"

    FIG.mkdir(parents=True, exist_ok=True)
    # All finite effects and adjusted p-values are shown; zero padj is placed at
    # a stated plotting floor to avoid infinite coordinates.
    valid = primary.loc[np.isfinite(primary.log2FoldChange) & primary.padj.notna()].copy()
    positive = valid.loc[valid.padj.gt(0), "padj"]
    padj_floor = float(positive.min() / 10) if len(positive) else 1e-300
    plot_padj = valid.padj.clip(lower=padj_floor)
    yy = -np.log10(plot_padj.to_numpy(dtype=float))
    up = valid.padj.lt(0.05) & valid.log2FoldChange.ge(1)
    down = valid.padj.lt(0.05) & valid.log2FoldChange.le(-1)
    fig, ax = plt.subplots(figsize=(9.5, 6.5))
    for mask, color, label in ((~(up | down), "#888888", "Below threshold B"),
                               (up, "#c35332", "Higher in MSC-sEV"),
                               (down, "#2364a0", "Lower in MSC-sEV")):
        ax.scatter(valid.loc[mask, "log2FoldChange"], yy[mask.to_numpy()],
                   s=7, alpha=0.48, color=color, linewidths=0, label=label)
    ax.axvline(-1, color="#555555", linestyle="--", linewidth=0.7)
    ax.axvline(1, color="#555555", linestyle="--", linewidth=0.7)
    ax.axhline(-np.log10(0.05), color="#555555", linestyle="--", linewidth=0.7)
    strongest = valid.loc[up | down].sort_values(["padj", "gene_id"], kind="stable").head(8)
    previous_y = {"positive": float("inf"), "negative": float("inf")}
    for idx, row in strongest.iterrows():
        label = row.gene_symbol if pd.notna(row.gene_symbol) and str(row.gene_symbol) else row.gene_id
        observed_y = yy[valid.index.get_loc(idx)]
        side = "positive" if row.log2FoldChange > 0 else "negative"
        label_y = min(observed_y, previous_y[side] - 2.0)
        previous_y[side] = label_y
        label_x = row.log2FoldChange + (0.25 if side == "positive" else -0.25)
        ax.annotate(str(label), (row.log2FoldChange, observed_y),
                    xytext=(label_x, label_y), textcoords="data", fontsize=7,
                    ha="left" if side == "positive" else "right",
                    arrowprops={"arrowstyle": "-", "color": "#777777", "lw": 0.5})
    ax.set_xlabel("DESeq2 log2 fold change (MSC-sEV vs DMEM)")
    ax.set_ylabel("−log10(BH adjusted p-value)")
    ax.set_title("GSE251807 primary DESeq2 analysis — batch adjusted")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(alpha=0.12)
    render_figure(FIG / "fig06_primary_volcano.png")

    lim = float(max(np.max(np.abs(x)), np.max(np.abs(y)))) * 1.04
    fig, axes = plt.subplots(1, 2, figsize=(13.6, 6.2))
    for ax, view_limit, title in ((axes[0], lim, "Full effect range"),
                                  (axes[1], 2.0, "Central range (±2 log2FC)")):
        ax.scatter(x, y, s=6, color="#386f95", alpha=0.23, linewidths=0, rasterized=True)
        ax.plot([-view_limit, view_limit], [-view_limit, view_limit],
                color="#b13f31", linewidth=1, linestyle="--", label="Identity")
        ax.set_xlim(-view_limit, view_limit)
        ax.set_ylim(-view_limit, view_limit)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel("Primary log2FC (16 samples)")
        ax.set_title(title)
        ax.grid(alpha=0.12)
    axes[0].set_ylabel("Sensitivity log2FC (15 samples; EV_8 omitted)")
    axes[0].legend(frameon=False)
    fig.suptitle(f"GSE251807 — EV_8 influence | Pearson r={pearson:.3f}; Spearman ρ={spearman:.3f}; n={len(common):,}")
    render_figure(FIG / "fig07_primary_vs_sensitivity_log2fc.png")

    limitations = [
        "One documented recipient NHDF donor lot; no donor-level generalization",
        "Independent EV-preparation count and assignment unknown",
        "The original Salmon index release is unverified; GENCODE v44 is compatible, not proven original",
        "Gene counts are estimated from Salmon transcript quantification, not original integer gene counts",
        "The two batches had different transcript universes; Strategy A retains only 189,509 exact-shared transcripts",
        "EV_8 remains a PCA outlier, but no technical defect was demonstrated; primary includes it",
        "No EXP001-versus-EXP002 biological validation or pathway comparison was performed in C3",
    ]
    checkpoint = {
        "dataset": "GSE251807", "experiment": "EXP002", "checkpoint": "EXP002-C3",
        "framework": model["framework"], "R_version": model["R_version"],
        "Bioconductor_version": model["Bioconductor_version"],
        "DESeq2_version": model["DESeq2_version"], "tximport_version": model["tximport_version"],
        "count_representation": "estimated gene-level counts derived from Salmon transcript quantification",
        "annotation_source": model["annotation_source"],
        "gene_symbol_available": model["gene_symbol_available"],
        "primary_samples": model["primary"]["sample_count"],
        "sensitivity_samples": model["sensitivity"]["sample_count"],
        "design": model["design"], "contrast": model["contrast"],
        "positive_log2fc_definition": model["positive_log2fc_definition"],
        "genes_before_filtering": model["primary"]["genes_before_filtering"],
        "filter_rule": model["filter_rule"],
        "primary_genes_tested": model["primary"]["genes_tested"],
        "sensitivity_genes_tested": model["sensitivity"]["genes_tested"],
        "shared_genes_tested": len(paired),
        "shared_genes_finite_log2fc": len(common),
        "primary_padj005": model["primary"]["padj005"],
        "primary_thresholdB": model["primary"]["thresholdB"],
        "primary_up": model["primary"]["up"], "primary_down": model["primary"]["down"],
        "sensitivity_padj005": model["sensitivity"]["padj005"],
        "sensitivity_thresholdB": model["sensitivity"]["thresholdB"],
        "sensitivity_up": model["sensitivity"]["up"],
        "sensitivity_down": model["sensitivity"]["down"],
        "log2fc_pearson": pearson, "log2fc_spearman": spearman,
        "direction_concordance": direction,
        "direction_concordance_nonzero_gene_count": int(nonzero.sum()),
        "direction_concordance_zero_exclusions": int((~nonzero).sum()),
        "effect_size_subset_rule": plan["effect_size_direction_subset"],
        "effect_size_subset_gene_count": int(large.sum()),
        "effect_size_subset_direction_concordance": large_direction,
        "padj005_intersection": a_overlap["intersection"],
        "padj005_union": a_overlap["union"],
        "padj005_jaccard": a_overlap["jaccard"],
        "thresholdB_intersection": b_overlap["intersection"],
        "thresholdB_union": b_overlap["union"],
        "thresholdB_jaccard": b_overlap["jaccard"],
        "median_abs_delta_log2fc": float(np.median(abs_delta)),
        "p95_abs_delta_log2fc": float(np.quantile(abs_delta, 0.95)),
        "sign_reversal_count": int(reversals.sum()),
        "delta_log2fc_ge_05": ge05, "delta_log2fc_ge_1": ge1,
        "DESeq2_outlier_summary": diagnostics,
        "EV8_robustness_interpretation": decision,
        "material_warning_guide": guide,
        "material_warning_triggers": warning_triggers,
        "P_M_E_A_I_GSEA_stability": "PENDING_C4",
        "GSEA_NES_correlation": "PENDING_C4",
        "volcano_padj_plot_floor": padj_floor,
        "volcano_zero_padj_points": int((valid.padj == 0).sum()),
        "volcano_label_count": len(strongest),
        "limitations": limitations,
        "decision": decision,
        "overall_pass": decision != "REVIEW REQUIRED",
    }
    (OUT / "exp002_c3_de.json").write_text(json.dumps(checkpoint, indent=2, allow_nan=False) + "\n")

    def fmt(value: float | None, digits: int = 3) -> str:
        return "NA" if value is None else f"{value:.{digits}f}"

    histogram = diagnostics["primary"]["pvalue_histogram_deciles"]
    histogram_text = ", ".join(str(v) for v in histogram)
    top_primary = primary.loc[primary.padj.lt(0.05) & primary.log2FoldChange.abs().ge(1)].head(10)
    top_lines = "\n".join(
        f"| {row.gene_id} | {row.gene_symbol if pd.notna(row.gene_symbol) else 'NA'} | {row.log2FoldChange:.3f} | {row.padj:.3g} |"
        for row in top_primary.itertuples(index=False)) or "| None | NA | NA | NA |"
    warnings = []
    if decision == "PASS WITH SENSITIVITY WARNING":
        warnings.append("At least one effect-sensitivity guide threshold was crossed; keep the 16-sample fit primary.")
    if diagnostics["primary"]["pvalue_na"] or diagnostics["sensitivity"]["pvalue_na"]:
        warnings.append("DESeq2 returned NA nominal p-values for some genes; Cook's distances and NA counts are reported below.")
    report = f"""# SkinExo-AI EXP002-C3

## Objective

Estimate the MSC-sEV-associated gene-expression contrast in GSE251807 and quantify its dependence on EV_8. This checkpoint includes two frozen DESeq2 fits and gene-level sensitivity metrics only. It does not compare EXP002 with EXP001 or run GSEA.

## Dataset Constraints

GSE251807 includes 16 author-described recipient NHDF cultures/libraries: 8 MSC-sEV and 8 DMEM controls, split into two batches of 4 per arm. Recipient cells come from one documented donor lot, and EV-preparation independence is unknown. EXP002-C1R remains `LIMITED_GO`; EXP002-C2 was resolved by C2R to `PASS WITH LIMITATIONS` after retaining EV_8.

## Estimated Count Representation

Input is the C2 tximport object from **189,509 exact-shared versioned ENST transcripts**, mapped through compatible **GENCODE v44 / GRCh38.p14**. It supplies estimated gene counts, TPM, and sample-specific abundance-weighted effective gene lengths. `countsFromAbundance="no"`; `DESeqDataSetFromTximport` internally rounds fractional estimated counts and carries `avgTxLength` into gene-length-aware normalization factors. **These are estimated gene-level counts, not original integer gene counts.** The original author Salmon index release is unverified. The author-normalized matrix and EXP001 files were not DE inputs. Annotation source: {model['annotation_source']}.

The [Bioconductor tximport workflow](https://bioconductor.org/packages/3.18/bioc/vignettes/tximport/inst/doc/tximport.html) documents this counts-plus-length-offset route; [DESeq2](https://bioconductor.org/packages/3.18/bioc/html/DESeq2.html) implements the negative-binomial model.

## Statistical Framework

R **{model['R_version']}**; Bioconductor **{model['Bioconductor_version']}**; DESeq2 **{model['DESeq2_version']}**; tximport **{model['tximport_version']}**. Both fits used standard DESeq2 dispersion estimation, Wald testing, default Cook's handling and independent filtering, and Benjamini–Hochberg adjustment. No ordinary t-test or log-CPM outcome test was used.

## Frozen Design

Primary: all **16** samples, including EV_8; design `~ batch + condition`. Sensitivity: **15** samples excluding EV_8; the same additive design and framework. Reference is `CTRL_DMEM`; contrast is `MSC_sEV` versus `CTRL_DMEM`. **Positive log2FC means higher estimated expression after MSC-sEV exposure.** The scientific target is the average condition effect across batches. No batch × condition interaction was fitted. Both design matrices were full rank before fitting. The EV_8 inclusion decision was frozen before results.

## Filtering

Before each fit, apply the frozen condition-blind rule: **{model['filter_rule']}**. From **{checkpoint['genes_before_filtering']:,}** mapped genes, **{checkpoint['primary_genes_tested']:,}** entered the primary fit and **{checkpoint['sensitivity_genes_tested']:,}** the sensitivity fit. Different retained-gene counts reflect the omitted library; all comparisons below use the **{checkpoint['shared_genes_finite_log2fc']:,}** shared tested genes with finite effects. Threshold A is `padj < 0.05`; threshold B adds `|log2FC| >= 1`. Neither filter nor threshold was tuned to DEG results.

## Primary Differential Expression

The 16-sample fit yielded **{checkpoint['primary_padj005']:,}** genes at threshold A and **{checkpoint['primary_thresholdB']:,}** at threshold B (**{checkpoint['primary_up']:,}** higher; **{checkpoint['primary_down']:,}** lower in MSC-sEV). [Complete results](../outputs/exp002/differential_expression_primary_all.csv) retain all tested genes, including null and NA-adjusted-p results; [threshold-B results](../outputs/exp002/differential_expression_primary_significant.csv) are a reporting subset.

The first ten threshold-B rows by adjusted p-value, with no manual biological selection, are:

| gene_id | gene_symbol | log2FC | padj |
| --- | --- | ---: | ---: |
{top_lines}

These are statistical results, not evidence of a skin-repair phenotype.

## Sensitivity Differential Expression

The 15-sample fit yielded **{checkpoint['sensitivity_padj005']:,}** genes at threshold A and **{checkpoint['sensitivity_thresholdB']:,}** at threshold B (**{checkpoint['sensitivity_up']:,}** higher; **{checkpoint['sensitivity_down']:,}** lower). [Complete](../outputs/exp002/differential_expression_sensitivity_all.csv) and [threshold-B](../outputs/exp002/differential_expression_sensitivity_significant.csv) tables are separate. This fit does **not** replace the primary result, regardless of DEG count.

## Primary vs Sensitivity Robustness

Over **{len(common):,}** shared tested genes with finite log2FC, Pearson `r = {pearson:.4f}` and Spearman `ρ = {spearman:.4f}`. Direction concordance among **{int(nonzero.sum()):,}** genes with nonzero effects in both fits is **{fmt(direction, 4)}**; **{int((~nonzero).sum()):,}** exact-zero effects were excluded. The fixed magnitude subset, `|log2FC| >= 1` in either fit, contains **{int(large.sum()):,}** genes and has direction concordance **{fmt(large_direction, 4)}**. This cutoff comes from the previously frozen threshold-B magnitude, not from the observed sensitivity result.

| Significance-set overlap | Intersection | Union | Jaccard |
| --- | ---: | ---: | ---: |
| `padj < 0.05` | {a_overlap['intersection']:,} | {a_overlap['union']:,} | {fmt(a_overlap['jaccard'], 4)} |
| `padj < 0.05 & |log2FC| >= 1` | {b_overlap['intersection']:,} | {b_overlap['union']:,} | {fmt(b_overlap['jaccard'], 4)} |

These overlaps are descriptive and change with sample size and power. P/M/E/A/I GSEA direction stability and NES correlation remain **PENDING_C4**.

## EV_8 Influence

The median absolute primary-versus-sensitivity log2FC difference is **{np.median(abs_delta):.4f}**; the 95th percentile is **{np.quantile(abs_delta, .95):.4f}**. There are **{int(reversals.sum()):,}** sign reversals among nonzero finite effects, **{ge05:,}** genes with `|Δlog2FC| >= 0.5` (**{ge05/len(common):.2%}** of shared genes), and **{ge1:,}** with `|Δlog2FC| >= 1` (**{ge1/len(common):.2%}**). The predeclared sensitivity-warning guide crossed: {', '.join(k for k,v in warning_triggers.items() if v) or 'none'}. Pearson falls below the guide, while median and 95th-percentile changes remain small; the warning reflects an unstable effect tail rather than a broad change across most genes. Biological influence is **not** a retrospective technical reason to exclude EV_8.

## Model Diagnostics

Both fits had finite positive dispersions and gene-length-aware normalization factors. Primary median dispersion: **{diagnostics['primary']['dispersion_median']:.4g}** (95th percentile **{diagnostics['primary']['dispersion_p95']:.4g}**); sensitivity median **{diagnostics['sensitivity']['dispersion_median']:.4g}** (95th percentile **{diagnostics['sensitivity']['dispersion_p95']:.4g}**). Primary and sensitivity Cook's-distance diagnostic exceedance genes: **{diagnostics['primary']['cook_exceedance_gene_count']:,}** and **{diagnostics['sensitivity']['cook_exceedance_gene_count']:,}**. EV_8 has **{diagnostics['primary']['cook_exceedance_by_sample']['EV_8']}** of the primary fit's **{diagnostics['primary']['cook_exceedance_observation_count']}** flagged gene–sample observations; these are model diagnostics, not a retrospective technical-exclusion rule. DESeq2 nominal p-value NAs: **{diagnostics['primary']['pvalue_na']:,}** and **{diagnostics['sensitivity']['pvalue_na']:,}**; adjusted-p NAs: **{diagnostics['primary']['padj_na']:,}** and **{diagnostics['sensitivity']['padj_na']:,}**, mostly from standard independent filtering of finite p-values. Count-replacement assay detected: primary **{diagnostics['primary']['original_count_replacement_detected']}**, sensitivity **{diagnostics['sensitivity']['original_count_replacement_detected']}**. These diagnostics document standard DESeq2 behavior; no sample was manually removed and no outlier-handling default was changed.

Primary nominal p-value histogram counts in bins 0–0.1 through 0.9–1.0: **{histogram_text}**. [Primary MA plot](../outputs/exp002/figures/fig05_primary_ma_plot.png) covers the full finite log2FC range. [Primary volcano](../outputs/exp002/figures/fig06_primary_volcano.png) uses threshold B and labels the first eight threshold-B genes by padj. There were **{checkpoint['volcano_zero_padj_points']}** zero-padj points; the plotting floor is {padj_floor:.3g} and affects only such points. [Effect comparison](../outputs/exp002/figures/fig07_primary_vs_sensitivity_log2fc.png) shows all shared finite genes and the identity line in the full-range panel; the second panel explicitly zooms to ±2 log2FC for readability. No selected EXP001 genes were highlighted.

## Limitations

""" + "\n".join(f"- {item}" for item in limitations) + f"""

## C3 Decision

**{decision}.** The count-based batch-adjusted models are technically interpretable under the restricted C1R design. {'At least one preregistered effect-sensitivity guide threshold was crossed; report both fits and retain EV_8 in the primary.' if decision == 'PASS WITH SENSITIVITY WARNING' else 'No preregistered material-sensitivity guide threshold was crossed.' if decision == 'PASS' else 'A critical model diagnostic requires review.'} Independent-study DE is complete; **cross-study biological validation has not been performed**. GSEA and EXP001 comparison are reserved for EXP002-C4.
"""
    REPORT.write_text(report)
    print(f"C3 {decision}: primary {len(primary):,} genes, sensitivity {len(sensitivity):,}; Pearson {pearson:.4f}; Spearman {spearman:.4f}")


if __name__ == "__main__":
    main()
