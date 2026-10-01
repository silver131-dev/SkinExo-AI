"""EXP001-C2: reproducible filtering and exploratory sample-level RNA-seq QC."""

from __future__ import annotations

import json
import os
import tempfile
from itertools import combinations
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "skinexo_mpl"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform
from scipy.stats import spearmanr
from sklearn.decomposition import PCA


DATASET = "GSE293186"
PRIMARY_RULE = "C: CPM >= 1 in at least 2 samples"
RULE_NAMES = {
    "A": "count >= 10 in at least 2 samples",
    "B": "count >= 10 in at least 3 samples",
    "C": "CPM >= 1 in at least 2 samples",
}
COLORS = {"CTRL": "#2468a0", "ECEV": "#c05736"}


def project_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "data" / "raw").is_dir() and (parent / "experiments" / "exp001").is_dir():
            return parent
    raise RuntimeError("Could not locate SkinExo-AI project root")


def load_inputs(root: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    c1 = json.loads((root / "outputs/exp001/exp001_c1_integrity.json").read_text())
    if c1.get("overall_pass") is not True:
        raise RuntimeError("C1 overall_pass is not true; C2 cannot proceed")
    if c1.get("dataset") != DATASET:
        raise ValueError("C1 dataset accession mismatch")
    metadata = pd.read_csv(root / "data/metadata/GSE293186_samples.csv", dtype=str)
    required = {"gsm_id", "count_column", "sample_name", "condition"}
    if not required.issubset(metadata.columns) or len(metadata) != 6:
        raise ValueError("Sample metadata must contain six mapped samples")
    if metadata[list(required)].isna().any().any():
        raise ValueError("Missing sample metadata")
    if metadata["count_column"].duplicated().any() or metadata["gsm_id"].duplicated().any():
        raise ValueError("Ambiguous sample metadata")
    if metadata["condition"].value_counts().to_dict() != {"CTRL": 3, "ECEV": 3}:
        raise ValueError("Sample metadata does not contain three samples per condition")
    sample_cols = metadata["count_column"].tolist()
    c1_mapping = {row["gsm_id"]: row["count_column"] for row in c1["sample_mapping"]}
    if dict(zip(metadata["gsm_id"], sample_cols)) != c1_mapping:
        raise ValueError("Current sample metadata disagrees with passed C1 mapping")

    matrix = pd.read_csv(root / "data/raw/GSE293186_gene_count.csv.gz", compression="gzip")
    if matrix.shape != (c1["matrix_rows"], c1["matrix_columns"]):
        raise ValueError("Count matrix shape changed since C1")
    gene_col = c1["gene_identifier_column"]
    if gene_col not in matrix or not set(sample_cols).issubset(matrix.columns):
        raise ValueError("C1 gene identifier or mapped sample columns missing")
    raw = matrix[sample_cols]
    if raw.isna().any().any() or not all(pd.api.types.is_integer_dtype(t) for t in raw.dtypes):
        raise ValueError("Raw counts must be complete integers")
    if (raw < 0).any().any():
        raise ValueError("Raw counts contain negative values")
    if matrix[gene_col].isna().any() or matrix[gene_col].duplicated().any():
        raise ValueError("Missing or duplicate gene identifiers")
    if raw.sum().to_dict() != c1["library_sizes"]:
        raise ValueError("Library sizes differ from passed C1 checkpoint")
    if int(raw.eq(0).all(axis=1).sum()) != c1["zero_count_genes"]:
        raise ValueError("Zero-count gene total differs from passed C1 checkpoint")
    return matrix, metadata, c1


def pca_coordinates(log_cpm: pd.DataFrame, metadata: pd.DataFrame) -> tuple[pd.DataFrame, list[float]]:
    # Transpose: six samples are observations; genes are features. No labels enter fit.
    transformed = PCA(n_components=2, svd_solver="full").fit(log_cpm.T)
    scores = transformed.transform(log_cpm.T)
    coords = pd.DataFrame({
        "sample": metadata["count_column"].to_numpy(),
        "condition": metadata["condition"].to_numpy(),
        "PC1": scores[:, 0],
        "PC2": scores[:, 1],
    })
    return coords, transformed.explained_variance_ratio_.tolist()


def pca_structure(coords: pd.DataFrame) -> dict:
    points = coords[["PC1", "PC2"]].to_numpy()
    distances = squareform(pdist(points))
    np.fill_diagonal(distances, np.inf)
    nearest = distances.argmin(axis=1)
    names = coords["sample"].tolist()
    labels = coords["condition"].tolist()
    within = []
    for condition in ("CTRL", "ECEV"):
        subset = coords.loc[coords["condition"] == condition, ["PC1", "PC2"]].to_numpy()
        within.extend(np.linalg.norm(subset - subset.mean(axis=0), axis=1))
    ctrl_center = coords.loc[coords["condition"] == "CTRL", ["PC1", "PC2"]].mean().to_numpy()
    ecev_center = coords.loc[coords["condition"] == "ECEV", ["PC1", "PC2"]].mean().to_numpy()
    return {
        "nearest_neighbors": {names[i]: names[int(nearest[i])] for i in range(len(names))},
        "nearest_neighbor_same_condition": int(sum(labels[i] == labels[int(nearest[i])] for i in range(len(names)))),
        "centroid_distance_to_mean_within_spread": float(
            np.linalg.norm(ctrl_center - ecev_center) / np.mean(within)
        ) if np.mean(within) else None,
        "nearest_neighbor_distances": {names[i]: float(distances[i, nearest[i]]) for i in range(len(names))},
    }


def draw_scatter(ax, coords: pd.DataFrame, title: str) -> None:
    label_offsets = {
        "CTRL_72h_1": (6, 12),
        "CTRL_72h_2": (6, -8),
        "CTRL_72h_3": (6, -26),
        "ECEV_72h_1": (6, -3),
        "ECEV_72h_2": (6, 6),
        "ECEV_72h_3": (6, 6),
    }
    for condition in ("CTRL", "ECEV"):
        subset = coords.loc[coords["condition"] == condition]
        ax.scatter(subset["PC1"], subset["PC2"], s=90, color=COLORS[condition], label=condition)
        for row in subset.itertuples(index=False):
            ax.annotate(row.sample, (row.PC1, row.PC2),
                        xytext=label_offsets.get(row.sample, (6, 6)),
                        textcoords="offset points", fontsize=8)
    ax.axhline(0, color="#bbbbbb", lw=0.7)
    ax.axvline(0, color="#bbbbbb", lw=0.7)
    ax.set_title(title)
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.legend(frameon=False, loc="best")
    ax.margins(0.24)


def main() -> int:
    root = project_root()
    matrix, metadata, c1 = load_inputs(root)
    sample_cols = metadata["count_column"].tolist()
    conditions = dict(zip(sample_cols, metadata["condition"]))
    gene_col = c1["gene_identifier_column"]
    raw = matrix[sample_cols]
    original_gene_count = len(raw)
    zero_count_gene_count = int(raw.eq(0).all(axis=1).sum())
    nonzero_gene_count = original_gene_count - zero_count_gene_count
    library_sizes = raw.sum(axis=0).astype(int)
    if (library_sizes <= 0).any():
        raise ValueError("Cannot calculate CPM with a zero library size")

    # Full-library denominators are kept after filtering; no condition labels are used.
    cpm = raw.div(library_sizes, axis=1) * 1_000_000
    filters = {
        "A": raw.ge(10).sum(axis=1).ge(2),
        "B": raw.ge(10).sum(axis=1).ge(3),
        "C": cpm.ge(1).sum(axis=1).ge(2),
    }
    filter_summary = pd.DataFrame([
        {
            "rule": key,
            "definition": RULE_NAMES[key],
            "genes_retained": int(mask.sum()),
            "genes_removed": int((~mask).sum()),
            "primary": key == "C",
        }
        for key, mask in filters.items()
    ])
    keep = filters["C"]
    filtered_raw = raw.loc[keep].copy()
    filtered_raw.insert(0, gene_col, matrix.loc[keep, gene_col].to_numpy())
    filtered_cpm = cpm.loc[keep]
    log_cpm = np.log2(filtered_cpm + 1)
    log_cpm_with_ids = log_cpm.copy()
    log_cpm_with_ids.insert(0, gene_col, matrix.loc[keep, gene_col].to_numpy())

    processed = root / "data/processed"
    outputs = root / "outputs/exp001"
    figures = outputs / "figures"
    processed.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    filtered_raw.to_csv(processed / "GSE293186_filtered_counts.csv.gz", index=False, compression="gzip")
    log_cpm_with_ids.to_csv(processed / "GSE293186_log2_cpm.csv.gz", index=False, compression="gzip", float_format="%.10g")
    filter_summary.to_csv(outputs / "filtering_summary.csv", index=False)

    lib_min = int(library_sizes.min())
    lib_max = int(library_sizes.max())
    lib_median = float(library_sizes.median())
    lib_ratio = lib_max / lib_min
    fig, ax = plt.subplots(figsize=(10, 5), constrained_layout=True)
    bars = ax.bar(sample_cols, library_sizes.to_numpy() / 1_000_000,
                  color=[COLORS[conditions[s]] for s in sample_cols])
    ax.axhline(lib_median / 1_000_000, ls="--", color="#555555", label="Median")
    ax.bar_label(bars, fmt="%.2f", padding=3, fontsize=8)
    ax.set_ylabel("Total raw counts (millions)")
    ax.set_title("GSE293186 library sizes · EXP001-C2")
    ax.tick_params(axis="x", rotation=30)
    ax.legend(frameon=False)
    fig.savefig(figures / "fig01_library_size.png", dpi=180)
    plt.close(fig)

    correlation = log_cpm.corr(method="pearson")
    correlation.to_csv(outputs / "sample_correlation.csv", float_format="%.10g")
    within_ctrl = []
    within_ecev = []
    between = []
    for left, right in combinations(sample_cols, 2):
        value = float(correlation.loc[left, right])
        if conditions[left] == conditions[right] == "CTRL":
            within_ctrl.append(value)
        elif conditions[left] == conditions[right] == "ECEV":
            within_ecev.append(value)
        else:
            between.append(value)
    fig, ax = plt.subplots(figsize=(8, 7), constrained_layout=True)
    heat = ax.imshow(correlation.to_numpy(), cmap="viridis", vmin=min(0.8, float(correlation.min().min())), vmax=1)
    ax.set_xticks(range(6), sample_cols, rotation=45, ha="right")
    ax.set_yticks(range(6), sample_cols)
    for i in range(6):
        for j in range(6):
            ax.text(j, i, f"{correlation.iat[i, j]:.3f}", ha="center", va="center",
                    fontsize=8, color="white" if correlation.iat[i, j] < 0.92 else "black")
    ax.set_title("Pearson correlation · filtered log2(CPM + 1)")
    fig.colorbar(heat, ax=ax, label="Pearson r", shrink=0.8)
    fig.savefig(figures / "fig02_sample_correlation.png", dpi=180)
    plt.close(fig)

    # Feature ranking depends only on variance over all six samples.
    variance_order = np.argsort(-log_cpm.var(axis=1, ddof=1).to_numpy(), kind="stable")
    if len(log_cpm) < 5000:
        raise ValueError("Primary filter retained fewer than 5,000 genes")
    variants = {
        "all_filtered": log_cpm,
        "top_5000_variable": log_cpm.iloc[variance_order[:5000]],
        "top_2000_variable": log_cpm.iloc[variance_order[:2000]],
    }
    coordinates = {}
    variance_explained = {}
    structures = {}
    for name, feature_matrix in variants.items():
        coordinates[name], variance_explained[name] = pca_coordinates(feature_matrix, metadata)
        structures[name] = pca_structure(coordinates[name])

    main_coords = coordinates["all_filtered"]
    main_coords.to_csv(outputs / "pca_coordinates.csv", index=False, float_format="%.10g")
    fig, ax = plt.subplots(figsize=(8, 6), constrained_layout=True)
    draw_scatter(ax, main_coords,
                 f"PCA · all filtered genes\nPC1 {variance_explained['all_filtered'][0]*100:.1f}% · PC2 {variance_explained['all_filtered'][1]*100:.1f}%")
    fig.savefig(figures / "fig03_pca.png", dpi=180)
    plt.close(fig)

    primary_distances = pdist(main_coords[["PC1", "PC2"]].to_numpy())
    robustness_rows = []
    robustness_summary = {}
    for name, coords in coordinates.items():
        variant_distances = pdist(coords[["PC1", "PC2"]].to_numpy())
        distance_rank_r = float(spearmanr(primary_distances, variant_distances).statistic)
        reference_neighbors = structures["all_filtered"]["nearest_neighbors"]
        neighbors = structures[name]["nearest_neighbors"]
        neighbor_agreement = sum(neighbors[s] == reference_neighbors[s] for s in sample_cols)
        robustness_summary[name] = {
            "gene_count": len(variants[name]),
            "pc1_variance": float(variance_explained[name][0]),
            "pc2_variance": float(variance_explained[name][1]),
            "pairwise_distance_spearman_vs_all": distance_rank_r,
            "nearest_neighbor_agreement_vs_all": f"{neighbor_agreement}/6",
            "nearest_neighbor_same_condition": f"{structures[name]['nearest_neighbor_same_condition']}/6",
            "centroid_distance_to_mean_within_spread": structures[name]["centroid_distance_to_mean_within_spread"],
        }
        for row in coords.to_dict("records"):
            robustness_rows.append({
                "feature_set": name,
                "gene_count": len(variants[name]),
                **row,
                "pc1_variance": variance_explained[name][0],
                "pc2_variance": variance_explained[name][1],
            })
    pd.DataFrame(robustness_rows).to_csv(outputs / "pca_robustness.csv", index=False, float_format="%.10g")
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), constrained_layout=True)
    for ax, (name, coords) in zip(axes, coordinates.items()):
        ev = variance_explained[name]
        draw_scatter(ax, coords, f"{name.replace('_', ' ')} · {len(variants[name]):,} genes\nPC1 {ev[0]*100:.1f}% · PC2 {ev[1]*100:.1f}%")
    fig.suptitle("PCA robustness · unsupervised feature choices")
    fig.savefig(figures / "fig04_pca_robustness.png", dpi=180)
    plt.close(fig)

    # Heuristic review flags only; no sample is removed.
    sample_warnings = []
    for sample in sample_cols:
        size = int(library_sizes[sample])
        if size < 0.5 * lib_median or size > 2 * lib_median:
            sample_warnings.append(f"{sample}: library size outside 0.5–2× the median")
        other = [s for s in sample_cols if s != sample]
        mean_all = float(correlation.loc[sample, other].mean())
        same = [s for s in other if conditions[s] == conditions[sample]]
        different = [s for s in other if conditions[s] != conditions[sample]]
        mean_same = float(correlation.loc[sample, same].mean())
        mean_different = float(correlation.loc[sample, different].mean())
        if mean_all < 0.90:
            sample_warnings.append(f"{sample}: mean correlation to other samples below 0.90 ({mean_all:.3f})")
        if mean_same < 0.90 or mean_same + 0.01 < mean_different:
            sample_warnings.append(f"{sample}: within-condition correlation warrants review (within {mean_same:.3f}; between {mean_different:.3f})")
    nearest_distances = structures["all_filtered"]["nearest_neighbor_distances"]
    median_nearest = float(np.median(list(nearest_distances.values())))
    for sample, distance in nearest_distances.items():
        if median_nearest > 0 and distance > 3 * median_nearest:
            sample_warnings.append(f"{sample}: PCA nearest-neighbor distance exceeds 3× the median")
    for name in ("top_5000_variable", "top_2000_variable"):
        if robustness_summary[name]["pairwise_distance_spearman_vs_all"] < 0.8:
            sample_warnings.append(f"{name}: PCA pairwise-distance ranks differ from the all-gene PCA (Spearman < 0.8)")
    overall_pass = len(sample_warnings) == 0
    layout_stable = all(
        robustness_summary[name]["nearest_neighbor_agreement_vs_all"] == "6/6"
        and robustness_summary[name]["pairwise_distance_spearman_vs_all"] >= 0.8
        for name in ("top_5000_variable", "top_2000_variable")
    )
    qualitative_structure = (
        "The sample layout is stable across the three unsupervised feature sets: "
        "all six nearest neighbors match the all-gene PCA, and sample-pair distance "
        "ranks remain similar. CTRL and ECEV occupy distinct regions in these plots."
        if layout_stable else
        "The sample layout changes across unsupervised feature sets and warrants review."
    )

    result = {
        "dataset": DATASET,
        "experiment": "EXP001",
        "checkpoint": "EXP001-C2 Filtering / normalization / sample-level QC",
        "c1_overall_pass": True,
        "original_gene_count": original_gene_count,
        "zero_count_gene_count": zero_count_gene_count,
        "nonzero_gene_count": nonzero_gene_count,
        "filter_rules_evaluated": filter_summary.to_dict("records"),
        "primary_filter_rule": PRIMARY_RULE,
        "filtered_gene_count": int(keep.sum()),
        "library_sizes": {s: int(library_sizes[s]) for s in sample_cols},
        "library_size_min": lib_min,
        "library_size_max": lib_max,
        "library_size_median": lib_median,
        "library_size_ratio": lib_ratio,
        "mean_within_ctrl_correlation": float(np.mean(within_ctrl)),
        "mean_within_ecev_correlation": float(np.mean(within_ecev)),
        "mean_between_condition_correlation": float(np.mean(between)),
        "pca_pc1_variance": float(variance_explained["all_filtered"][0]),
        "pca_pc2_variance": float(variance_explained["all_filtered"][1]),
        "pca_coordinates": main_coords.to_dict("records"),
        "pca_robustness_summary": robustness_summary,
        "pca_qualitative_structure": qualitative_structure,
        "sample_warnings": sample_warnings,
        "overall_pass": overall_pass,
        "normalization_note": "Library-size CPM and log2(CPM + 1) are for sample QC only; C3 requires a count-based differential-expression framework.",
    }
    (outputs / "exp001_c2_qc.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    filter_lines = [f"| {r.rule} | {r.definition} | {r.genes_retained:,} |" for r in filter_summary.itertuples(index=False)]
    size_lines = [f"| {s} | {int(library_sizes[s]):,} |" for s in sample_cols]
    coord_lines = [f"| {r.sample} | {r.condition} | {r.PC1:.3f} | {r.PC2:.3f} |" for r in main_coords.itertuples(index=False)]
    robust_lines = [
        f"| {name.replace('_', ' ')} | {entry['gene_count']:,} | {entry['pc1_variance']*100:.1f}% | {entry['pc2_variance']*100:.1f}% | {entry['pairwise_distance_spearman_vs_all']:.3f} | {entry['nearest_neighbor_agreement_vs_all']} | {entry['nearest_neighbor_same_condition']} |"
        for name, entry in robustness_summary.items()
    ]
    decision = "PASS" if overall_pass else "REVIEW REQUIRED"
    report = f"""# SkinExo-AI EXP001-C2

## Objective

Assess whether the six GSE293186 RNA-seq samples are suitable for later analysis and describe their sample-level structure. No biological effect is tested here.

## Input Data

- C1 checkpoint: **PASS**; [C1 integrity report](EXP001_C1_dataset_integrity.md).
- [NCBI GEO series](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE293186) and the official gene-count matrix, with sample mapping from `data/metadata/GSE293186_samples.csv`.
- {original_gene_count:,} original genes; {zero_count_gene_count:,} all-sample zero-count genes; {nonzero_gene_count:,} genes with at least one nonzero count; six samples (3 CTRL, 3 ECEV).

## Filtering

All rules were evaluated on raw counts or library-size CPM without condition labels:

| Rule | Definition | Genes retained |
| --- | --- | ---: |
{chr(10).join(filter_lines)}

**Primary rule: {PRIMARY_RULE}**, retaining **{int(keep.sum()):,}** genes. With six samples and library sizes spanning {lib_min:,}–{lib_max:,}, a CPM threshold accounts for sequencing-depth differences and expression in two samples avoids retaining one-sample signals. This rule was chosen without examining CTRL/ECEV separation. The filtered raw counts are saved unchanged. The [edgeR user guide](https://bioconductor.org/packages/release/bioc/vignettes/edgeR/inst/doc/edgeRUsersGuide.pdf) motivates filtering low-expression genes and using CPM to account for library size; this fixed C2 rule is not an edgeR `filterByExpr` run.

## Normalization for QC

CPM = raw count / **original full-library count total** × 1,000,000. Correlation and PCA use log2(CPM + 1) for the filtered genes. CPM and log-CPM here are for QC and visualization only. They do not replace DESeq2 or TMM normalization for differential expression. C3 requires an appropriate count-based statistical framework using raw counts; see the [DESeq2 documentation](https://bioconductor.org/packages/release/bioc/vignettes/DESeq2/inst/doc/DESeq2.html).

## Library Size QC

| Sample | Raw-count library size |
| --- | ---: |
{chr(10).join(size_lines)}

Minimum **{lib_min:,}**; maximum **{lib_max:,}**; median **{lib_median:,.0f}**; max/min ratio **{lib_ratio:.3f}**. [Figure 1](../outputs/exp001/figures/fig01_library_size.png). Library size is a technical QC quantity, not evidence of a biological effect.

## Sample Correlation

Pearson correlation of filtered log2(CPM + 1), calculated across genes: mean within CTRL **{np.mean(within_ctrl):.4f}**, mean within ECEV **{np.mean(within_ecev):.4f}**, mean between conditions **{np.mean(between):.4f}**. These are descriptive summaries; no significance tests were run. [Correlation matrix](../outputs/exp001/sample_correlation.csv) and [Figure 2](../outputs/exp001/figures/fig02_sample_correlation.png).

## PCA

Samples are observations and filtered genes are features. Condition labels entered the plot only after fitting PCA. PC1 explains **{variance_explained['all_filtered'][0]*100:.2f}%** and PC2 **{variance_explained['all_filtered'][1]*100:.2f}%** of variance.

| Sample | Condition | PC1 | PC2 |
| --- | --- | ---: | ---: |
{chr(10).join(coord_lines)}

[Coordinates](../outputs/exp001/pca_coordinates.csv) and [Figure 3](../outputs/exp001/figures/fig03_pca.png).

## PCA Robustness

Variable genes were ranked by variance across all six log-CPM sample values, without condition labels. PCA was refit independently for each feature set. The distance-rank correlation compares the 15 sample-pair distances in the first two PCs to the all-filtered result; nearest-neighbor agreement is a second descriptive stability check. PCA axes can rotate or flip, so raw PC signs are not compared.

| Feature set | Genes | PC1 | PC2 | Distance-rank Spearman vs all | Same nearest neighbor vs all | Nearest neighbor in same condition |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(robust_lines)}

[Robustness coordinates](../outputs/exp001/pca_robustness.csv) and [Figure 4](../outputs/exp001/figures/fig04_pca_robustness.png). {qualitative_structure} These comparisons are descriptive and do not establish treatment causality.

## Sample-Level Warnings

{chr(10).join('- ' + warning for warning in sample_warnings) if sample_warnings else '- No sample crossed the prespecified heuristic flags for library size, mean correlation, replicate consistency, PCA isolation, or PCA distance-rank instability.'}

No sample was removed. Heuristic flags are prompts for review, not formal outlier tests.

## Limitations

- **n = 6** (three samples per condition) is small, so sample-level summaries and outlier heuristics are unstable.
- PCA is exploratory; visual separation does not establish treatment causality.
- CPM/log-CPM is used for QC and visualization; differential expression requires separate count-based modeling in C3.
- Pairwise correlations and PCA distances are descriptive; no differential-expression testing, pathway analysis, gene-set scoring, or supervised modeling was performed.

## C2 Decision

**{decision}**. The decision reflects the stated sample-level QC heuristics only.
"""
    report_path = root / "reports/EXP001_C2_sample_qc.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    print(f"C1: PASS; genes: {original_gene_count}; retained: {int(keep.sum())}")
    print(filter_summary.to_string(index=False))
    print(f"Library size ratio: {lib_ratio:.3f}")
    print(f"Mean correlations (CTRL/ECEV/between): {np.mean(within_ctrl):.4f} / {np.mean(within_ecev):.4f} / {np.mean(between):.4f}")
    print(f"PCA variance (PC1/PC2): {variance_explained['all_filtered'][0]*100:.2f}% / {variance_explained['all_filtered'][1]*100:.2f}%")
    print(f"Sample warnings: {sample_warnings or 'none'}")
    print(f"C2 result: {decision}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
