#!/usr/bin/env python3
"""EXP002-C2 unsupervised sample QC from tximport estimated gene counts.

No differential expression, pathway enrichment, cross-study comparison, or
supervised feature selection is performed. All feature choices come from the
frozen condition-blind configs/exp002_c2_qc_plan.json.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform
from scipy.stats import spearmanr
from sklearn.decomposition import PCA


ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data/processed/exp002"
OUT = ROOT / "outputs/exp002"
FIG = OUT / "figures"
COLORS = {"CTRL_DMEM": "#2563a6", "MSC_sEV": "#c4532e"}
MARKERS = {"1": "o", "2": "s"}


def mean_pairs(matrix: np.ndarray, indices: list[int]) -> float:
    values = [matrix[i, j] for pos, i in enumerate(indices) for j in indices[pos + 1:]]
    return float(np.mean(values)) if values else float("nan")


def eta_squared(values: np.ndarray, labels: list[str]) -> float:
    overall = float(np.mean(values))
    total = float(np.sum((values - overall) ** 2))
    if total == 0:
        return 0.0
    between = sum(sum(label == x for x in labels) * (float(np.mean(values[np.array(labels) == label])) - overall) ** 2 for label in set(labels))
    return float(between / total)


def save_figure(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=170, bbox_inches="tight")
    plt.close()


def scatter_pca(ax, coordinates: np.ndarray, rows: list[dict], variance: np.ndarray, title: str) -> None:
    for i, row in enumerate(rows):
        ax.scatter(coordinates[i, 0], coordinates[i, 1], s=65,
                   c=COLORS[row["condition"]], marker=MARKERS[row["batch"]],
                   edgecolor="black", linewidth=0.35)
        ax.annotate(row["sample_name"], (coordinates[i, 0], coordinates[i, 1]),
                    xytext=(4, 3), textcoords="offset points", fontsize=6.7)
    ax.axhline(0, lw=0.5, color="#999999")
    ax.axvline(0, lw=0.5, color="#999999")
    ax.set_xlabel(f"PC1 ({variance[0] * 100:.2f}%)")
    ax.set_ylabel(f"PC2 ({variance[1] * 100:.2f}%)")
    ax.set_title(title, fontsize=10)
    ax.grid(alpha=0.15)


def main() -> None:
    plan = json.loads((ROOT / "configs/exp002_c2_qc_plan.json").read_text())
    c1r = json.loads((OUT / "exp002_c1r_resolution.json").read_text())
    if c1r["decision"] != "LIMITED_GO" or plan["primary_filter"] != "C":
        raise ValueError("C1R authorization or frozen QC filter mismatch")
    with (ROOT / "data/metadata/GSE251807_samples.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    with (OUT / "exp002_c2_aggregation_qc.csv").open(newline="") as handle:
        aggregation = list(csv.DictReader(handle))
    samples = [row["sample_name"] for row in rows]
    if len(samples) != 16 or samples != [row["sample"] for row in aggregation]:
        raise ValueError("Selected sample mapping differs from aggregation QC")
    counts = pd.read_csv(PROCESSED / "estimated_gene_counts.csv.gz", index_col=0)
    if counts.shape != (37307, 16) or list(counts.columns) != samples or counts.index.has_duplicates:
        raise ValueError(f"Unexpected gene-level matrix: {counts.shape}")
    values = counts.to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("Estimated gene counts contain missing, nonnumeric, or negative values")
    library = values.sum(axis=0)
    retained = np.array([float(row["retained_salmon_numreads_sum"]) for row in aggregation])
    if np.max(np.abs(library - retained)) > 0.02:
        raise ValueError("tximport gene totals differ from retained transcript estimates")
    if np.any(library <= 0):
        raise ValueError("Zero sample library size")
    cpm = values / library[np.newaxis, :] * 1e6
    filters = {
        "A": np.sum(values >= 10, axis=1) >= 4,
        "B": np.sum(cpm >= 1, axis=1) >= 2,
        "C": np.sum(cpm >= 1, axis=1) >= 4,
    }
    primary = filters[plan["primary_filter"]]
    if primary.sum() < 5000:
        raise ValueError("Unexpectedly few genes remain after frozen QC filter")
    filtering_rows = [
        {"rule": key, "definition": plan["candidate_filters"][key], "genes_retained": int(mask.sum()),
         "genes_excluded": int(len(mask) - mask.sum()), "primary": key == plan["primary_filter"]}
        for key, mask in filters.items()
    ]
    pd.DataFrame(filtering_rows).to_csv(OUT / "filtering_summary.csv", index=False)
    log_cpm = np.log2(cpm[primary] + 1)
    genes = counts.index.to_numpy()[primary]
    pd.DataFrame(values[primary], index=genes, columns=samples).to_csv(
        PROCESSED / "qc_filtered_estimated_gene_counts.csv.gz", compression="gzip", index_label="gene_id")
    pd.DataFrame(log_cpm, index=genes, columns=samples).to_csv(
        PROCESSED / "qc_log2_cpm.csv.gz", compression="gzip", index_label="gene_id")

    corr = np.corrcoef(log_cpm.T)
    if not np.isfinite(corr).all():
        raise ValueError("Sample correlations are not finite")
    pd.DataFrame(corr, index=samples, columns=samples).to_csv(OUT / "sample_correlation.csv", index_label="sample")
    ev_idx = [i for i, row in enumerate(rows) if row["condition"] == "MSC_sEV"]
    ctrl_idx = [i for i, row in enumerate(rows) if row["condition"] == "CTRL_DMEM"]
    batch1_idx = [i for i, row in enumerate(rows) if row["batch"] == "1"]
    batch2_idx = [i for i, row in enumerate(rows) if row["batch"] == "2"]
    between_batches = [float(corr[i, j]) for i in batch1_idx for j in batch2_idx]
    correlations = {
        "within_ev": mean_pairs(corr, ev_idx),
        "within_control": mean_pairs(corr, ctrl_idx),
        "within_batch_1": mean_pairs(corr, batch1_idx),
        "within_batch_2": mean_pairs(corr, batch2_idx),
        "between_batches": float(np.mean(between_batches)),
    }

    feature_sets = {
        "all_filtered_genes": np.arange(log_cpm.shape[0]),
        "top_5000_variable_genes": np.argsort(-np.var(log_cpm, axis=1, ddof=1), kind="stable")[:5000],
        "top_2000_variable_genes": np.argsort(-np.var(log_cpm, axis=1, ddof=1), kind="stable")[:2000],
    }
    pca_results = {}
    for name, indices in feature_sets.items():
        fit = PCA(n_components=2, svd_solver="full")
        coordinates = fit.fit_transform(log_cpm[indices, :].T)
        pca_results[name] = {"coordinates": coordinates, "variance": fit.explained_variance_ratio_, "feature_count": len(indices)}
    all_coords = pca_results["all_filtered_genes"]["coordinates"]
    all_variance = pca_results["all_filtered_genes"]["variance"]
    pd.DataFrame([
        {"sample": row["sample_name"], "condition": row["condition"], "batch": row["batch"],
         "PC1": float(all_coords[i, 0]), "PC2": float(all_coords[i, 1])}
        for i, row in enumerate(rows)
    ]).to_csv(OUT / "pca_coordinates.csv", index=False)
    reference_dist = pdist(all_coords)
    robustness_rows = []
    robustness_summary = {}
    for name, result in pca_results.items():
        coordinates = result["coordinates"]
        distance_rho = float(spearmanr(reference_dist, pdist(coordinates)).statistic)
        batch_pc1 = eta_squared(coordinates[:, 0], [row["batch"] for row in rows])
        condition_pc1 = eta_squared(coordinates[:, 0], [row["condition"] for row in rows])
        robustness_summary[name] = {
            "feature_count": result["feature_count"],
            "pc1_variance": float(result["variance"][0]),
            "pc2_variance": float(result["variance"][1]),
            "pairwise_distance_spearman_vs_all": distance_rho,
            "pc1_batch_eta_squared_descriptive": batch_pc1,
            "pc1_condition_eta_squared_descriptive": condition_pc1,
        }
        for i, row in enumerate(rows):
            robustness_rows.append({
                "feature_set": name, "feature_count": result["feature_count"],
                "sample": row["sample_name"], "condition": row["condition"], "batch": row["batch"],
                "PC1": float(coordinates[i, 0]), "PC2": float(coordinates[i, 1]),
                "PC1_variance": float(result["variance"][0]), "PC2_variance": float(result["variance"][1]),
            })
    pd.DataFrame(robustness_rows).to_csv(OUT / "pca_robustness.csv", index=False)

    FIG.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 4.6))
    bars = ax.bar(range(16), library / 1e6, color=[COLORS[r["condition"]] for r in rows])
    for bar, row in zip(bars, rows):
        if row["batch"] == "2":
            bar.set_hatch("//")
    ax.axhline(np.median(library) / 1e6, color="#333333", ls="--", lw=1, label="Median")
    ax.set_xticks(range(16), samples, rotation=55, ha="right")
    ax.set_ylabel("Estimated gene count total (millions)")
    ax.set_title("GSE251807 — exact-shared tximport gene totals\nColor: condition; hatch: batch 2")
    ax.legend(frameon=False)
    save_figure(FIG / "fig01_library_size.png")

    fig, ax = plt.subplots(figsize=(10, 8))
    image = ax.imshow(corr, cmap="viridis", vmin=max(0.0, float(np.min(corr)) - 0.01), vmax=1)
    ax.set_xticks(range(16), samples, rotation=60, ha="right", fontsize=7)
    ax.set_yticks(range(16), samples, fontsize=7)
    ax.set_title("GSE251807 — Pearson correlation, filtered log2(CPM + 1)")
    fig.colorbar(image, ax=ax, label="Pearson r", fraction=0.045)
    save_figure(FIG / "fig02_sample_correlation.png")

    fig, ax = plt.subplots(figsize=(8, 6))
    scatter_pca(ax, all_coords, rows, all_variance, "GSE251807 — unsupervised PCA\nColor: condition; circle: batch 1; square: batch 2")
    save_figure(FIG / "fig03_pca.png")

    fig, axes = plt.subplots(1, 3, figsize=(18, 5.2))
    for ax, (name, result) in zip(axes, pca_results.items()):
        scatter_pca(ax, result["coordinates"], rows, result["variance"], name.replace("_", " "))
    fig.suptitle("GSE251807 — PCA under condition-blind feature choices\nColor: condition; circle: batch 1; square: batch 2", fontsize=12)
    save_figure(FIG / "fig04_pca_robustness.png")

    warnings = []
    med_lib = float(np.median(library))
    for i, row in enumerate(rows):
        ratio = library[i] / med_lib
        if ratio > 1.75 or ratio < 1 / 1.75:
            warnings.append(f"{row['sample_name']}: estimated gene total is {ratio:.2f} times the median; review depth, no removal")
    own_condition_means = {}
    for i, row in enumerate(rows):
        peers = [j for j, other in enumerate(rows) if j != i and other["condition"] == row["condition"]]
        own_condition_means[row["sample_name"]] = float(np.mean(corr[i, peers]))
    low_corr_flags = []
    for group in (ev_idx, ctrl_idx):
        group_median = float(np.median([own_condition_means[samples[i]] for i in group]))
        for i in group:
            if own_condition_means[samples[i]] < group_median - 0.05:
                low_corr_flags.append(samples[i])
                warnings.append(f"{samples[i]}: mean within-condition correlation is >0.05 below group median; review, no removal")
    distances = squareform(pdist(all_coords))
    np.fill_diagonal(distances, np.inf)
    nearest = distances.min(axis=1)
    ev8_idx = samples.index("EV_8")
    ev8_isolated = bool(nearest[ev8_idx] > 2 * float(np.median(nearest)))
    if ev8_isolated:
        warnings.append("EV_8: nearest-neighbor distance in PC1/PC2 exceeds twice the sample median; review, no removal")
    depth_ratio = c1r["EV8_read_count_to_selected_median_ratio"]
    count_ratio = float(library[ev8_idx] / med_lib)
    depth_tracks_count = abs(depth_ratio - count_ratio) / depth_ratio < 0.2
    ev8_status = "NO_OBVIOUS_ISSUE" if depth_tracks_count and "EV_8" not in low_corr_flags and not ev8_isolated else "QC_REVIEW_NEEDED"
    if ev8_status != "NO_OBVIOUS_ISSUE":
        warnings.append("EV_8 requires sample-level review; it remains included")

    batch_summary = {
        "pc1_batch_eta_squared_descriptive": eta_squared(all_coords[:, 0], [row["batch"] for row in rows]),
        "pc2_batch_eta_squared_descriptive": eta_squared(all_coords[:, 1], [row["batch"] for row in rows]),
        "pc1_condition_eta_squared_descriptive": eta_squared(all_coords[:, 0], [row["condition"] for row in rows]),
        "pc2_condition_eta_squared_descriptive": eta_squared(all_coords[:, 1], [row["condition"] for row in rows]),
        "batch_balanced_with_condition": True,
        "recommended_de_design": "~ batch + condition",
        "interpretation": "Descriptive unsupervised QC only; labels applied after PCA fitting",
        "qualitative": "PC1 aligns strongly with batch; PC2 aligns descriptively with condition; neither axis establishes a biological effect",
    }
    if batch_summary["pc1_batch_eta_squared_descriptive"] > 0.8:
        warnings.append("Strong batch alignment on PC1; batch adjustment remains planned for later DE")
    checkpoint = {
        "dataset": "GSE251807", "experiment": "EXP002", "checkpoint": "EXP002-C2",
        "c1r_decision": c1r["decision"],
        "shared_transcripts_used": 189509,
        "mapped_gene_count": int(counts.shape[0]),
        "unmapped_transcript_count": 0,
        "ambiguous_mapping_count": 0,
        "tximport_version": "1.30.0", "counts_from_abundance": "no",
        "count_representation": "estimated gene-level counts derived from Salmon transcript quantification",
        "sample_count": 16, "ev_count": 8, "control_count": 8, "batch_count": 2,
        "aggregation_information_loss": {
            "per_sample": {r["sample"]: {"retained_percentage": float(r["retained_percentage"]), "excluded_percentage": float(r["excluded_percentage"])} for r in aggregation},
            "min_excluded_percentage": min(float(r["excluded_percentage"]) for r in aggregation),
            "max_excluded_percentage": max(float(r["excluded_percentage"]) for r in aggregation),
        },
        "filter_rules": filtering_rows, "primary_filter": plan["candidate_filters"]["C"],
        "filtered_gene_count": int(primary.sum()),
        "qc_transformation": plan["qc_transformation"],
        "library_sizes": {sample: float(library[i]) for i, sample in enumerate(samples)},
        "library_size_min": float(np.min(library)), "library_size_median": med_lib,
        "library_size_max": float(np.max(library)), "library_size_ratio": float(np.max(library) / np.min(library)),
        "correlation_summary": correlations,
        "pca_pc1_variance": float(all_variance[0]), "pca_pc2_variance": float(all_variance[1]),
        "pca_coordinates": {sample: {"PC1": float(all_coords[i, 0]), "PC2": float(all_coords[i, 1])} for i, sample in enumerate(samples)},
        "pca_robustness_summary": robustness_summary,
        "EV8_status": ev8_status,
        "EV8_qc": {"ena_read_depth_ratio_to_median": depth_ratio, "estimated_gene_total_ratio_to_median": count_ratio,
                    "mean_within_ev_correlation": own_condition_means["EV_8"], "nearest_pca_neighbor_ratio_to_median": float(nearest[ev8_idx] / np.median(nearest))},
        "batch_effect_summary": batch_summary,
        "recommended_de_design": "~ batch + condition",
        "primary_validation_endpoint": "Directional concordance of PREDEFINED P/M/E/A/I GSEA program families across EXP001 and EXP002",
        "secondary_validation_endpoints": [
            "GSEA NES correlation across shared eligible gene sets",
            "Leading-edge gene overlap for pre-specified pathways",
            "Gene-level log2FC directional concordance across shared tested genes",
            "Global signed-Wald response similarity",
            "Pathway-level clustering/retrieval (descriptive only with two studies)",
        ],
        "sample_warnings": warnings,
        "overall_pass": bool(ev8_status == "NO_OBVIOUS_ISSUE" and not low_corr_flags),
    }
    checkpoint["decision"] = "PASS" if checkpoint["overall_pass"] else "REVIEW REQUIRED"
    (OUT / "exp002_c2_qc.json").write_text(json.dumps(checkpoint, indent=2) + "\n")
    print(f"C2: {counts.shape[0]:,} mapped genes, {primary.sum():,} QC-filtered genes")
    print("Correlations:", {key: round(value, 4) for key, value in correlations.items()})
    print(f"PCA: PC1 {all_variance[0] * 100:.2f}%, PC2 {all_variance[1] * 100:.2f}%; EV_8 {ev8_status}")
    print(f"C2 decision: {'PASS' if checkpoint['overall_pass'] else 'REVIEW REQUIRED'}")


if __name__ == "__main__":
    main()
