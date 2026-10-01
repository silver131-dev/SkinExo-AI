#!/usr/bin/env python3
"""Build EXP003-C3 figures, diagnostics checkpoint, and report.

Inputs are only the saved SkinExo DESeq2 result, frozen checkpoints, prepared
raw-count representation, and display annotation manifest. No author DEG table,
gene-set collection, or earlier-context result is read.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "skinexo_exp003_c3_mpl"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs/exp003"
FIGURES = OUT / "figures"
REPORT = ROOT / "reports/EXP003_C3_differential_expression.md"
FIGURES.mkdir(parents=True, exist_ok=True)


def number(value: float) -> str:
    if value == 0:
        return "0"
    return f"{value:.3g}"


def markdown_top(rows: pd.DataFrame, limit: int = 10) -> str:
    if rows.empty:
        return "No genes met threshold B in this direction."
    lines = [
        "| Rank | Gene ID | Symbol | baseMean | log2FC | padj |",
        "| ---: | --- | --- | ---: | ---: | ---: |",
    ]
    for rank, row in enumerate(rows.head(limit).itertuples(index=False), start=1):
        symbol = row.gene_symbol if pd.notna(row.gene_symbol) and row.gene_symbol else "UNMAPPED"
        lines.append(
            f"| {rank} | {row.gene_id} | {symbol} | {row.baseMean:.2f} | "
            f"{row.log2FoldChange:+.3f} | {number(row.padj)} |"
        )
    return "\n".join(lines)


def main() -> None:
    c1 = json.loads((OUT / "exp003_c1_integrity.json").read_text())
    c2 = json.loads((OUT / "exp003_c2_qc.json").read_text())
    model = json.loads((OUT / "exp003_c3_model_summary.json").read_text())
    annotation = json.loads((ROOT / "configs/exp003_c3_annotation_source.json").read_text())
    if not (
        c1.get("overall_pass") is True
        and c2.get("overall_pass") is True
        and c2.get("decision") == "PASS_WITH_LIMITATIONS"
        and model.get("genes_tested") == c2.get("filtered_gene_count") == 13_874
        and model.get("design") == "~ condition"
        and model.get("filter_rule") == "CPM >= 1 in at least 3 of 6 samples"
    ):
        raise RuntimeError("Saved DE model does not match the frozen C1/C2 authorization")

    results = pd.read_csv(OUT / "differential_expression_all.csv")
    required = ["gene_id", "gene_symbol", "baseMean", "log2FoldChange", "lfcSE", "stat", "pvalue", "padj"]
    if list(results.columns) != required or len(results) != 13_874 or results["gene_id"].duplicated().any():
        raise RuntimeError("Complete DE table is incomplete, duplicated, or reordered in schema")
    sig_a = results["padj"].lt(0.05).fillna(False)
    sig_b = sig_a & results["log2FoldChange"].abs().ge(1).fillna(False)
    up = results.loc[sig_b & results["log2FoldChange"].ge(1)].sort_values(["padj", "gene_id"])
    down = results.loc[sig_b & results["log2FoldChange"].le(-1)].sort_values(["padj", "gene_id"])
    observed = (int(sig_a.sum()), int(sig_b.sum()), len(up), len(down))
    expected = (model["padj005"], model["thresholdB"], model["up"], model["down"])
    if observed != expected:
        raise RuntimeError(f"DE threshold counts differ from R model summary: {observed} != {expected}")
    if int(results["pvalue"].isna().sum()) != model["NA_pvalue"] or int(results["padj"].isna().sum()) != model["NA_padj"]:
        raise RuntimeError("NA counts differ from the R diagnostic summary")

    top_rows = []
    for direction, frame in [("UP", up), ("DOWN", down)]:
        for rank, row in enumerate(frame.head(10).itertuples(index=False), start=1):
            top_rows.append({
                "direction": direction,
                "direction_rank": rank,
                "gene_id": row.gene_id,
                "gene_symbol": row.gene_symbol if pd.notna(row.gene_symbol) else "",
                "baseMean": row.baseMean,
                "log2FoldChange": row.log2FoldChange,
                "lfcSE": row.lfcSE,
                "stat": row.stat,
                "pvalue": row.pvalue,
                "padj": row.padj,
            })
    top_columns = ["direction", "direction_rank"] + required
    pd.DataFrame(top_rows, columns=top_columns).to_csv(OUT / "c3_top_genes.csv", index=False)

    positive_padj = results.loc[results["padj"] > 0, "padj"]
    if positive_padj.empty:
        raise RuntimeError("No positive adjusted p-values available for volcano display")
    floor = float(positive_padj.min() / 10.0)
    plot_padj = results["padj"].fillna(1.0).clip(lower=floor)
    y = -np.log10(plot_padj)
    status = np.where(
        sig_b & results["log2FoldChange"].ge(1),
        "Threshold-B up",
        np.where(sig_b & results["log2FoldChange"].le(-1), "Threshold-B down", "Other tested genes"),
    )
    fig, ax = plt.subplots(figsize=(10, 7), constrained_layout=True)
    for label, color, size, alpha in [
        ("Other tested genes", "#a3aab0", 9, 0.42),
        ("Threshold-B down", "#2776ae", 14, 0.75),
        ("Threshold-B up", "#c2573c", 14, 0.75),
    ]:
        mask = status == label
        ax.scatter(
            results.loc[mask, "log2FoldChange"], y.loc[mask], c=color, s=size,
            alpha=alpha, linewidths=0, label=f"{label} ({int(mask.sum()):,})",
        )
    ax.axvline(-1, color="#555555", linestyle="--", linewidth=0.8)
    ax.axvline(1, color="#555555", linestyle="--", linewidth=0.8)
    ax.axhline(-np.log10(0.05), color="#555555", linestyle="--", linewidth=0.8)
    # Automatic, story-blind labeling: ten smallest padj values among threshold-B
    # genes, ties by stable gene ID.
    labels = results.loc[sig_b].sort_values(["padj", "gene_id"]).head(10)
    for index, row in enumerate(labels.itertuples(index=False)):
        position = results.index[results["gene_id"] == row.gene_id][0]
        text = row.gene_symbol if pd.notna(row.gene_symbol) and row.gene_symbol else row.gene_id
        x_offset = 8 if row.log2FoldChange >= 0 else -8
        y_offset = 7 if index % 2 == 0 else -9
        ax.annotate(
            text, (row.log2FoldChange, y.loc[position]), xytext=(x_offset, y_offset),
            textcoords="offset points", fontsize=8,
            ha="left" if x_offset > 0 else "right",
            arrowprops={"arrowstyle": "-", "lw": 0.4, "color": "#555555"},
        )
    ax.set_xlabel("log2 fold change (hDF-EV vs control)")
    ax.set_ylabel("−log10(BH-adjusted p-value)")
    ax.set_title("GSE293956 · hDF-EV vs control · DESeq2 · n = 3 vs 3")
    ax.legend(frameon=False, markerscale=2)
    ax.margins(x=0.10, y=0.08)
    fig.savefig(FIGURES / "fig06_volcano.png", dpi=180)
    plt.close(fig)

    # Descriptive influence check. It is not a paired model: suffix-matched labels
    # are never used in fitting or inference.
    counts = pd.read_csv(ROOT / "data/processed/exp003/c3_filtered_counts.csv.gz").set_index("gene_id")
    sample_diagnostics = model["DESeq2_outlier_summary"]["sample_diagnostics"]
    size_factors = pd.Series({row["sample"]: row["size_factor"] for row in sample_diagnostics})
    normalized = counts.div(size_factors, axis=1)
    threshold_ids = results.loc[sig_b, "gene_id"]
    threshold_norm = normalized.loc[threshold_ids]
    ev_names = ["hDF_EVs_1", "hDF_EVs_2", "hDF_EVs_3"]
    control_names = ["hDF_con_1", "hDF_con_2", "hDF_con_3"]
    threshold_all_ev_above_all_control = int(
        (threshold_norm[ev_names].min(axis=1) > threshold_norm[control_names].max(axis=1)).sum()
    )
    max_attr_total = sum(row["maximum_cook_attribution_count"] for row in sample_diagnostics)
    max_attr_sample = max(sample_diagnostics, key=lambda row: row["maximum_cook_attribution_count"])
    max_attr_fraction = max_attr_sample["maximum_cook_attribution_count"] / max_attr_total
    cook_exceedances = model["DESeq2_outlier_summary"]["cook_exceedance_observation_count"]
    no_single_sample_failure = (
        cook_exceedances == 0
        and model["NA_pvalue"] == 0
        and threshold_all_ev_above_all_control == model["thresholdB"]
    )
    replicate_note = (
        "C2 PC1 replicate-label-associated structure remains unexplained. "
        f"{max_attr_sample['sample']} had the largest Cook-maximum attribution "
        f"({max_attr_sample['maximum_cook_attribution_count']:,}/{max_attr_total:,} genes; "
        f"{max_attr_fraction:.1%}), but no Cook's distance exceeded the DESeq2 diagnostic cutoff "
        f"({model['DESeq2_outlier_summary']['cook_cutoff']:.3g}), no p-value was suppressed, and "
        f"all {model['thresholdB']} threshold-B genes had every EV normalized count above every control normalized count. "
        "The suffix labels were not modeled as batch or pairing."
    )

    serious_failure = bool(
        model["dispersion_summary"]["beta_nonconverged"]
        or model["dispersion_summary"]["gene_estimate_nonfinite"]
        or model["dispersion_summary"]["fitted_trend_nonfinite"]
        or not no_single_sample_failure
    )
    decision = "REVIEW_REQUIRED" if serious_failure else "PASS_WITH_LIMITATIONS"
    limitations = [
        "n = 3 libraries per condition",
        "Recipient donor count and donor-to-library mapping are UNKNOWN",
        "Independent EV preparation count and preparation-to-library mapping are UNKNOWN",
        "Pairing is NO_EVIDENCE / UNKNOWN and suffix labels were not used as pairs",
        "Batch is NOT_DOCUMENTED and no batch covariate was fitted",
        "Exact RNA-seq control medium and vehicle are UNKNOWN",
        "C2 PC1 replicate-label-associated structure remains unexplained",
        "GENCODE v44 supplies display annotation for 13,771 of 13,874 tested stable IDs; the original count-generation annotation release is unknown",
        "No donor-level or EV-preparation-level generalization is supported",
        "No pathway analysis, phenotype validation, or cross-context validation has been performed",
    ]
    warnings = [
        "The unexplained PC1 structure materially limits biological interpretation despite acceptable model diagnostics.",
        "The largest Cook-maximum attribution share occurs in hDF_EVs_1, consistent with the latent replicate-label structure, but no observation exceeds the diagnostic cutoff.",
        "No threshold-B downregulated genes were observed; thresholds were not relaxed.",
        "Author-reported DEG findings were not accessed or compared in C3.",
    ]

    checkpoint = {
        "dataset": "GSE293956",
        "context_id": "CTX003",
        "framework": model["framework"],
        "R_version": model["R_version"],
        "Bioconductor_version": model["Bioconductor_version"],
        "DESeq2_version": model["DESeq2_version"],
        "samples": model["samples"],
        "ev_samples": model["ev_samples"],
        "control_samples": model["control_samples"],
        "design": model["design"],
        "contrast": "hDF-EV vs control",
        "positive_log2fc_definition": model["positive_log2fc_definition"],
        "genes_before_filtering": model["genes_before_filtering"],
        "filter_rule": model["filter_rule"],
        "genes_tested": model["genes_tested"],
        "padj005": model["padj005"],
        "thresholdB": model["thresholdB"],
        "up": model["up"],
        "down": model["down"],
        "NA_pvalue": model["NA_pvalue"],
        "NA_padj": model["NA_padj"],
        "annotation": annotation,
        "DESeq2_outlier_summary": model["DESeq2_outlier_summary"],
        "dispersion_summary": model["dispersion_summary"],
        "pvalue_distribution_summary": model["pvalue_distribution_summary"],
        "independent_filtering_summary": model["independent_filtering_summary"],
        "replicate_label_structure_note": replicate_note,
        "thresholdB_all_ev_above_all_control_normalized_counts": threshold_all_ev_above_all_control,
        "recipient_donor_count": "UNKNOWN",
        "ev_preparation_count": "UNKNOWN",
        "batch_status": "NOT_DOCUMENTED",
        "pairing_status": "NO_EVIDENCE / UNKNOWN",
        "control_definition": "control-labeled hDF without recorded EV; exact RNA-seq medium and vehicle UNKNOWN",
        "limitations": limitations,
        "warnings": warnings,
        "author_result_firewall": "PASS — no author DEG table or reported DEG result was read, compared, or used",
        "pathway_analysis_status": "NOT_RUN",
        "cross_context_comparison_status": "NOT_RUN",
        "decision": decision,
        "overall_pass": not serious_failure,
    }
    (OUT / "exp003_c3_de.json").write_text(json.dumps(checkpoint, indent=2) + "\n")

    pcounts = model["pvalue_distribution_summary"]["decile_counts"]
    independent = model["independent_filtering_summary"]
    dispersion = model["dispersion_summary"]
    cooks = model["DESeq2_outlier_summary"]
    report = f"""# SkinExo-AI EXP003-C3

## Objective

Estimate the hDF-EV-associated transcriptomic contrast in CTX003 using the design and low-expression filter frozen before viewing differential-expression results. This checkpoint performs DE only. It does not run pathway analysis or compare CTX003 biologically with CTX001 or CTX002.

## Frozen C2 Design

- Samples: **6**, comprising **3 hDF-EV** and **3 control** libraries.
- Primary design: **`~ condition`**.
- Contrast: **hDF-EV versus control**.
- Positive log2 fold change: **higher expression in hDF-EV-treated hDF**.
- Frozen filter: **CPM ≥ 1 in at least 3 of 6 samples**.
- Threshold A: `padj < 0.05`.
- Threshold B: `padj < 0.05 AND |log2FC| >= 1`.
- Batch: `NOT_DOCUMENTED`; pairing: `NO_EVIDENCE / UNKNOWN`.

No batch, donor, pairing, or replicate-label covariate was introduced. The author DEG findings were not read or used to select any parameter.

## Input Matrix

The unchanged official `GSE293956_hDF_total_count.txt.gz` source was reconstructed with the validated C1 parser. It contains **1,048,575** physical data rows, of which **60,675** have valid nonblank biological gene identifiers and **987,900** form the confirmed contiguous trailing structural-padding block. Parsing retained all zero-count biological genes and removed only blank-identifier blank/NA padding.

Counts are complete nonnegative integers with unique versionless Ensembl gene IDs. The source checksum remained `f30d382112d04c9e3f147fc350f8f58e6306da414a617b5cd4dd52c1fd8ec76d`.

GENCODE v44 / GRCh38.p14 official comprehensive GTF gene features were used only for display annotation through exact versionless stable-ID matching. Symbols were available for **{annotation['tested_gene_annotation_coverage']:,}/{annotation['tested_genes']:,}** tested genes. The original count-generation annotation release is unknown, and annotation did not alter the analysis universe.

## Filtering

- Genes before DE filtering: **{model['genes_before_filtering']:,}**.
- Frozen condition-blind rule: **{model['filter_rule']}**.
- Genes retained and tested: **{model['genes_tested']:,}**.

The count agrees exactly with C2. No alternate filter was selected after viewing results.

## Statistical Framework

DESeq2 negative-binomial GLM with standard size-factor and dispersion estimation, Wald testing, and Benjamini–Hochberg adjusted p-values. The fit used **{model['R_version']}**, Bioconductor **{model['Bioconductor_version']}**, and DESeq2 **{model['DESeq2_version']}**.

`results(dds, contrast = c("condition", "HDF_EV", "CONTROL"), alpha = 0.05, pAdjustMethod = "BH")` was evaluated with standard Cook's-distance handling and independent filtering. Fold changes are unshrunken DESeq2 estimates.

## Differential Expression

- [Complete DE table](../outputs/exp003/differential_expression_all.csv): **{model['genes_tested']:,}** genes.
- Threshold A (`padj < 0.05`): **{model['padj005']:,}** genes.
- [Threshold-B table](../outputs/exp003/differential_expression_significant.csv): **{model['thresholdB']:,}** genes.
- Threshold-B higher in hDF-EV: **{model['up']:,}**.
- Threshold-B lower in hDF-EV: **{model['down']:,}**.
- NA p-values / adjusted p-values: **{model['NA_pvalue']} / {model['NA_padj']}**.

Top hDF-EV-higher threshold-B genes by adjusted p-value, ties by stable gene ID:

{markdown_top(up)}

Top hDF-EV-lower threshold-B genes by adjusted p-value:

{markdown_top(down)}

The absence of threshold-B downregulated genes was retained; thresholds were not relaxed. The gene list is a statistical contrast and has not been converted into P/M/E/A/I evidence.

[Figure 5](../outputs/exp003/figures/fig05_ma_plot.png) shows mean normalized count versus unshrunken log2 fold change over the full finite range. [Figure 6](../outputs/exp003/figures/fig06_volcano.png) uses threshold B for classes. Volcano labels are the ten smallest adjusted p-values among threshold-B genes, ties by gene ID, without manual biological selection.

## Model Diagnostics

- Dispersion fit: **{dispersion['fit_type']}**; final median **{dispersion['final_median']:.4g}**, 95th percentile **{dispersion['final_p95']:.4g}**, range **{dispersion['final_min']:.4g}–{dispersion['final_max']:.4g}**.
- Nonfinite gene estimates / fitted trends: **{dispersion['gene_estimate_nonfinite']} / {dispersion['fitted_trend_nonfinite']}**.
- Nonconverged coefficient fits: **{dispersion['beta_nonconverged']}**.
- Cook's diagnostic cutoff: **{cooks['cook_cutoff']:.3g}**; genes/observations exceeding it: **{cooks['cook_exceedance_gene_count']} / {cooks['cook_exceedance_observation_count']}**.
- Count replacements: **none**; no p-value was set to NA by outlier handling.
- P-value decile counts from `[0,0.1)` through `[0.9,1]`: **{', '.join(str(x) for x in pcounts)}**; median finite p-value **{model['pvalue_distribution_summary']['median_finite_pvalue']:.4f}**.
- Independent filtering: enabled, baseMean threshold **{independent['filter_threshold']:.6g}**, theta **{independent['filter_theta']:.3g}**; finite p-values with NA padj: **{independent['padj_NA_with_finite_pvalue']}**.

The parametric dispersion fit completed with finite estimates and full coefficient convergence. Size factors were close to one. The right-heavy p-value distribution does not show a broad anti-conservative shift; a small low-p-value tail supplies the significant calls.

## Replicate-Label Structure

{replicate_note}

The higher Cook-maximum attribution for the replicate-1-labeled samples preserves the C2 reliability concern. It does not establish a batch or pair, and no alternative model was fitted. The lack of Cook cutoff exceedances and the direction consistency across all six normalized libraries indicate that the threshold-B calls are not attributable solely to one sample. This check is descriptive and does not remove the underlying design uncertainty.

## Reliability Limitations

- n = 3 libraries per condition.
- Recipient donor count and donor-to-library mapping are unknown.
- EV-preparation independence and preparation-to-library mapping are unknown.
- Pairing is unknown; matching suffixes were not modeled as pairs.
- Batch is not documented; no batch term was fitted.
- Exact control medium and vehicle are unknown.
- The dominant C2 PC1 replicate-label-associated structure remains unexplained.
- The original count-generation annotation release is unknown.
- No donor-level or EV-preparation-level generalization is supported.
- No pathway or cross-context validation has yet been performed.

## Claim Boundaries

These results estimate a conditional six-library transcriptomic contrast at 72 h. They do not demonstrate proliferation, migration, ECM remodeling, vascular interaction, inflammation, wound healing, therapeutic efficacy, cargo causality, donor-level reproducibility, or cross-context conservation. Pathway interpretation is reserved for EXP003-C4 under the frozen endpoint plan.

The primary SkinExo result was saved without accessing or comparing author-reported DEG results. Author agreement is not part of the C3 decision.

## C3 Decision

**{decision.replace('_', ' ')}.** The frozen model fit reproducibly, all 13,874 genes produced finite p-values, dispersion estimation and coefficient fitting completed, and no Cook's-distance cutoff exceedance or critical single-sample failure occurred. Biological interpretation remains materially limited by the unexplained PC1 structure and unresolved donor, EV-preparation, pairing, batch, and control-medium metadata.

CTX003 remains `PLANNED`; its P/M/E/A/I transcriptomic response states remain `UNKNOWN`.
"""
    REPORT.write_text(report)
    print(json.dumps({
        "decision": decision,
        "padj005": model["padj005"],
        "thresholdB": model["thresholdB"],
        "up": model["up"],
        "down": model["down"],
        "top_up": [row.gene_symbol if pd.notna(row.gene_symbol) and row.gene_symbol else row.gene_id for row in up.head(10).itertuples(index=False)],
        "top_down": [row.gene_symbol if pd.notna(row.gene_symbol) and row.gene_symbol else row.gene_id for row in down.head(10).itertuples(index=False)],
        "cook_exceedances": cook_exceedances,
        "thresholdB_all_ev_above_all_control": threshold_all_ev_above_all_control,
    }, indent=2))


if __name__ == "__main__":
    main()
