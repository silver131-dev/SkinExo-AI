#!/usr/bin/env python3
"""EXP003-C2: condition-blind sample QC and frozen design artifacts.

This script reuses the EXP003-C1 structural-padding predicate and verifies all
source invariants against the C1 checkpoint before calculating QC. It does not
fit a differential-expression model or perform pathway analysis.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/skinexo-matplotlib-exp003-c2")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/raw/exp003/GSE293956_hDF_total_count.txt.gz"
CONFIG_PATH = ROOT / "configs/exp003_c2_qc_plan.json"
C1_PATH = ROOT / "outputs/exp003/exp003_c1_integrity.json"
MAPPING_PATH = ROOT / "outputs/exp003/c1_sample_mapping.csv"
OUT = ROOT / "outputs/exp003"
FIGURES = OUT / "figures"
OUT.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

PADDING_TOKENS = {"", "NA", "N/A", "#N/A", "NULL"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_c1_valid_matrix(path: Path):
    """Apply the exact C1 padding rule and reject any non-padding trailing row."""
    genes = []
    count_rows = []
    physical_rows = 0
    padding_rows = 0
    padding_started = False
    first_padding_row = None
    last_padding_row = None
    padding_patterns = set()

    with gzip.open(path, "rt", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader)
        if len(header) != 7:
            raise ValueError(f"Expected seven columns, found {len(header)}")
        for row in reader:
            physical_rows += 1
            if len(row) != len(header):
                raise ValueError(f"Malformed physical data row {physical_rows}")
            identifier = row[0].strip()
            cells = [cell.strip() for cell in row[1:]]
            is_structural_padding = (
                not identifier
                and all(cell.upper() in PADDING_TOKENS for cell in cells)
            )
            if is_structural_padding:
                padding_started = True
                padding_rows += 1
                first_padding_row = first_padding_row or physical_rows
                last_padding_row = physical_rows
                padding_patterns.add(tuple(cells))
                continue
            if padding_started:
                raise ValueError(
                    f"Non-padding row follows structural padding at physical row {physical_rows}"
                )
            if not identifier or identifier.upper() in PADDING_TOKENS:
                raise ValueError(f"Invalid biological identifier at physical row {physical_rows}")
            values = []
            for cell in cells:
                if not cell or cell.upper() in PADDING_TOKENS:
                    raise ValueError(f"Missing count at physical row {physical_rows}")
                value = int(cell)
                if value < 0 or str(value) != cell:
                    raise ValueError(f"Invalid raw integer count at physical row {physical_rows}")
                values.append(value)
            genes.append(identifier)
            count_rows.append(values)

    return (
        header,
        genes,
        np.asarray(count_rows, dtype=np.int64),
        {
            "physical_rows": physical_rows,
            "padding_rows": padding_rows,
            "first_padding_row": first_padding_row,
            "last_padding_row": last_padding_row,
            "padding_pattern_count": len(padding_patterns),
        },
    )


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def clean_float(value: float) -> float:
    return float(value)


with CONFIG_PATH.open() as handle:
    config = json.load(handle)
with C1_PATH.open() as handle:
    c1 = json.load(handle)
with MAPPING_PATH.open(newline="") as handle:
    mapping = list(csv.DictReader(handle))

if not config.get("frozen_before_qc_computation"):
    raise SystemExit("C2 QC plan was not frozen before computation")
if sha256(SOURCE) != config["input"]["expected_sha256"] or sha256(SOURCE) != c1["sha256"]:
    raise SystemExit("Raw source checksum differs from frozen C1 input")

header, genes, counts, structure = load_c1_valid_matrix(SOURCE)
expected_structure = {
    "physical_rows": config["input"]["expected_physical_data_rows"],
    "padding_rows": config["input"]["expected_structural_padding_rows"],
    "first_padding_row": config["input"]["expected_valid_gene_rows"] + 1,
    "last_padding_row": config["input"]["expected_physical_data_rows"],
    "padding_pattern_count": c1["structural_padding_pattern_count"],
}
if structure != expected_structure or counts.shape != (config["input"]["expected_valid_gene_rows"], 6):
    raise SystemExit(f"C1 structural invariants failed: {structure}; shape={counts.shape}")
if header != c1["header"] or genes != list(dict.fromkeys(genes)):
    raise SystemExit("Header mismatch or duplicate gene identifiers")

mapping_by_column = {row["matrix_column"]: row for row in mapping}
if set(header[1:]) != set(mapping_by_column) or any(
    mapping_by_column[column]["mapping_status"] != "VERIFIED" for column in header[1:]
):
    raise SystemExit("C1 sample mapping is incomplete")

sample_rows = [mapping_by_column[column] for column in header[1:]]
samples = [row["sample_name"] for row in sample_rows]
conditions = [row["condition"] for row in sample_rows]
matrix_columns = header[1:]
library_sizes = counts.sum(axis=0)
if library_sizes.tolist() != [entry["library_size"] for entry in c1["library_sizes"]]:
    raise SystemExit("Raw library sizes no longer match C1")

# The denominators include all valid biological rows. No gene is removed before
# the candidate filters are evaluated.
cpm = counts.astype(np.float64) / library_sizes[np.newaxis, :] * 1_000_000.0
filter_rows = []
primary_mask = None
for candidate in config["filter_candidates"]:
    mask = (cpm >= candidate["cpm_threshold"]).sum(axis=1) >= candidate["minimum_samples"]
    retained = int(mask.sum())
    filter_rows.append(
        {
            "filter_id": candidate["filter_id"],
            "rule": candidate["rule"],
            "primary": str(candidate["primary"]).upper(),
            "genes_before_filtering": counts.shape[0],
            "zero_count_genes": int((counts.sum(axis=1) == 0).sum()),
            "genes_retained": retained,
            "genes_removed": int(counts.shape[0] - retained),
        }
    )
    if candidate["primary"]:
        if primary_mask is not None:
            raise SystemExit("More than one primary filter was frozen")
        primary_mask = mask
if primary_mask is None:
    raise SystemExit("No primary filter was frozen")
write_csv(
    OUT / "filtering_summary.csv",
    filter_rows,
    ["filter_id", "rule", "primary", "genes_before_filtering", "zero_count_genes", "genes_retained", "genes_removed"],
)

detected = (counts > 0).sum(axis=0)
sample_qc_rows = []
for index, sample in enumerate(samples):
    values = counts[:, index]
    nonzero = values[values > 0]
    sample_qc_rows.append(
        {
            "matrix_column": matrix_columns[index],
            "sample": sample,
            "gsm_id": sample_rows[index]["gsm_id"],
            "condition": conditions[index],
            "raw_library_size": int(library_sizes[index]),
            "genes_detected": int(detected[index]),
            "zero_fraction": clean_float((values == 0).mean()),
            "median_nonzero_count": clean_float(np.median(nonzero)),
            "count_q75": clean_float(np.quantile(values, 0.75)),
            "count_q90": clean_float(np.quantile(values, 0.90)),
            "count_q95": clean_float(np.quantile(values, 0.95)),
            "count_q99": clean_float(np.quantile(values, 0.99)),
            "maximum_count": int(values.max()),
        }
    )
write_csv(
    OUT / "sample_qc_metrics.csv",
    sample_qc_rows,
    list(sample_qc_rows[0]),
)

plt.figure(figsize=(8.4, 4.8))
colors = ["#4063D8" if condition == "CONTROL" else "#D1495B" for condition in conditions]
positions = np.arange(len(samples))
plt.bar(positions, library_sizes / 1_000_000.0, color=colors, edgecolor="black", linewidth=0.5)
plt.xticks(positions, samples, rotation=35, ha="right")
plt.ylabel("Raw library size (millions)")
plt.title("CTX003 hDF raw library sizes")
plt.tight_layout()
plt.savefig(FIGURES / "fig01_library_size.png", dpi=180)
plt.close()

# This transformed representation is used only for QC. The frozen future DE
# model receives raw integer counts after the independently frozen filter.
qc = np.log2(cpm[primary_mask, :] + 1.0)
correlation = np.corrcoef(qc.T)
with (OUT / "sample_correlation.csv").open("w", newline="") as handle:
    writer = csv.writer(handle)
    writer.writerow(["sample"] + samples)
    for sample, values in zip(samples, correlation):
        writer.writerow([sample] + [f"{value:.12f}" for value in values])

fig, ax = plt.subplots(figsize=(7.2, 6.2))
image = ax.imshow(correlation, vmin=0.90, vmax=1.0, cmap="viridis")
ax.set_xticks(np.arange(len(samples)), labels=samples, rotation=45, ha="right")
ax.set_yticks(np.arange(len(samples)), labels=samples)
for i in range(len(samples)):
    for j in range(len(samples)):
        ax.text(j, i, f"{correlation[i, j]:.3f}", ha="center", va="center", fontsize=7,
                color="white" if correlation[i, j] < 0.95 else "black")
fig.colorbar(image, ax=ax, label="Pearson correlation")
ax.set_title("Filtered log2(CPM + 1) sample correlation")
fig.tight_layout()
fig.savefig(FIGURES / "fig02_sample_correlation.png", dpi=180)
plt.close(fig)

def pair_values(kind: str) -> list[float]:
    values = []
    for left in range(len(samples)):
        for right in range(left + 1, len(samples)):
            if kind == "WITHIN_EV" and conditions[left] == conditions[right] == "HDF_EV":
                values.append(clean_float(correlation[left, right]))
            elif kind == "WITHIN_CONTROL" and conditions[left] == conditions[right] == "CONTROL":
                values.append(clean_float(correlation[left, right]))
            elif kind == "BETWEEN" and conditions[left] != conditions[right]:
                values.append(clean_float(correlation[left, right]))
    return values


def summary(values: list[float]) -> dict:
    return {
        "pair_count": len(values),
        "mean": clean_float(np.mean(values)),
        "minimum": clean_float(np.min(values)),
        "maximum": clean_float(np.max(values)),
    }


correlation_summary = {
    "within_ev": summary(pair_values("WITHIN_EV")),
    "within_control": summary(pair_values("WITHIN_CONTROL")),
    "between_conditions": summary(pair_values("BETWEEN")),
    "significance_testing": "NOT_PERFORMED",
}


def fit_pca(feature_matrix: np.ndarray):
    model = PCA(n_components=2, svd_solver="full")
    coordinates = model.fit_transform(feature_matrix.T)
    return model, coordinates


primary_model, primary_coordinates = fit_pca(qc)
pca_rows = []
for index, sample in enumerate(samples):
    pca_rows.append(
        {
            "sample": sample,
            "matrix_column": matrix_columns[index],
            "gsm_id": sample_rows[index]["gsm_id"],
            "condition": conditions[index],
            "PC1": clean_float(primary_coordinates[index, 0]),
            "PC2": clean_float(primary_coordinates[index, 1]),
            "PC1_variance_fraction": clean_float(primary_model.explained_variance_ratio_[0]),
            "PC2_variance_fraction": clean_float(primary_model.explained_variance_ratio_[1]),
        }
    )
write_csv(
    OUT / "pca_coordinates.csv",
    pca_rows,
    list(pca_rows[0]),
)

fig, ax = plt.subplots(figsize=(7.2, 5.8))
for condition, color, marker in [("CONTROL", "#4063D8", "o"), ("HDF_EV", "#D1495B", "s")]:
    indexes = [i for i, value in enumerate(conditions) if value == condition]
    ax.scatter(primary_coordinates[indexes, 0], primary_coordinates[indexes, 1],
               c=color, marker=marker, s=75, edgecolor="black", linewidth=0.5, label=condition)
for index, sample in enumerate(samples):
    ax.annotate(sample, primary_coordinates[index], xytext=(5, 4), textcoords="offset points", fontsize=8)
ax.axhline(0, color="#bbbbbb", linewidth=0.7)
ax.axvline(0, color="#bbbbbb", linewidth=0.7)
ax.set_xlabel(f"PC1 ({primary_model.explained_variance_ratio_[0] * 100:.2f}%)")
ax.set_ylabel(f"PC2 ({primary_model.explained_variance_ratio_[1] * 100:.2f}%)")
ax.set_title("Unsupervised PCA: primary-filtered QC representation")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(FIGURES / "fig03_pca.png", dpi=180)
plt.close(fig)

variances = np.var(qc, axis=1, ddof=1)
feature_sets = [
    ("ALL_FILTERED", qc),
    ("TOP_5000_VARIABLE", qc[np.argsort(variances)[-min(5000, qc.shape[0]):], :]),
    ("TOP_2000_VARIABLE", qc[np.argsort(variances)[-min(2000, qc.shape[0]):], :]),
]
robustness_rows = []
robustness_results = {}
for label, feature_matrix in feature_sets:
    model, coordinates = fit_pca(feature_matrix)
    distances = np.sqrt(((coordinates[:, None, :] - coordinates[None, :, :]) ** 2).sum(axis=2))
    np.fill_diagonal(distances, np.inf)
    nearest = distances.min(axis=1)
    nearest_ratio = nearest / np.median(nearest)
    robustness_results[label] = {
        "coordinates": coordinates,
        "pc1_variance": clean_float(model.explained_variance_ratio_[0]),
        "pc2_variance": clean_float(model.explained_variance_ratio_[1]),
        "nearest_neighbor_distance": nearest,
        "nearest_neighbor_distance_ratio": nearest_ratio,
    }
    for index, sample in enumerate(samples):
        robustness_rows.append(
            {
                "feature_set": label,
                "gene_count": feature_matrix.shape[0],
                "sample": sample,
                "condition": conditions[index],
                "PC1": clean_float(coordinates[index, 0]),
                "PC2": clean_float(coordinates[index, 1]),
                "PC1_variance_fraction": clean_float(model.explained_variance_ratio_[0]),
                "PC2_variance_fraction": clean_float(model.explained_variance_ratio_[1]),
                "nearest_neighbor_distance": clean_float(nearest[index]),
                "nearest_neighbor_distance_ratio": clean_float(nearest_ratio[index]),
            }
        )
write_csv(
    OUT / "pca_robustness.csv",
    robustness_rows,
    list(robustness_rows[0]),
)

fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.8))
for ax, (label, _) in zip(axes, feature_sets):
    result = robustness_results[label]
    coordinates = result["coordinates"]
    for condition, color, marker in [("CONTROL", "#4063D8", "o"), ("HDF_EV", "#D1495B", "s")]:
        indexes = [i for i, value in enumerate(conditions) if value == condition]
        ax.scatter(coordinates[indexes, 0], coordinates[indexes, 1], c=color, marker=marker,
                   s=60, edgecolor="black", linewidth=0.5, label=condition)
    for index, sample in enumerate(samples):
        ax.annotate(sample, coordinates[index], xytext=(4, 3), textcoords="offset points", fontsize=7)
    ax.set_title(label.replace("_", " ").title())
    ax.set_xlabel(f"PC1 ({result['pc1_variance'] * 100:.1f}%)")
    ax.set_ylabel(f"PC2 ({result['pc2_variance'] * 100:.1f}%)")
axes[0].legend(frameon=False, fontsize=8)
fig.suptitle("Unsupervised PCA robustness across condition-blind feature sets")
fig.tight_layout()
fig.savefig(FIGURES / "fig04_pca_robustness.png", dpi=180)
plt.close(fig)

# Symmetric technical review using criteria frozen in the configuration.
median_library = float(np.median(library_sizes))
median_detected = float(np.median(detected))
mean_off_diagonal = (correlation.sum(axis=1) - 1.0) / (len(samples) - 1)
median_mean_correlation = float(np.median(mean_off_diagonal))
sample_statuses = []
for index, sample in enumerate(samples):
    flags = []
    if library_sizes[index] < 0.67 * median_library or library_sizes[index] > 1.50 * median_library:
        flags.append("LIBRARY_SIZE_REVIEW")
    if detected[index] < 0.80 * median_detected:
        flags.append("DETECTED_GENES_REVIEW")
    if mean_off_diagonal[index] < median_mean_correlation - 0.05:
        flags.append("MEAN_CORRELATION_REVIEW")
    pca_flag_count = sum(
        robustness_results[label]["nearest_neighbor_distance_ratio"][index] > 3.0
        for label, _ in feature_sets
    )
    if pca_flag_count >= 2:
        flags.append("PCA_POSITION_REVIEW")
    sample_statuses.append(
        {
            "sample": sample,
            "condition": conditions[index],
            "status": "QC_REVIEW_NEEDED" if flags else "NO_OBVIOUS_ISSUE",
            "review_flags": flags,
            "mean_off_diagonal_correlation": clean_float(mean_off_diagonal[index]),
            "pca_feature_sets_flagged": int(pca_flag_count),
        }
    )

# Coordinate-distance concordance avoids arbitrary PC sign choices. Spearman
# rank correlation is calculated directly without importing inferential tests.
def condensed_distances(coordinates: np.ndarray) -> np.ndarray:
    values = []
    for left in range(len(samples)):
        for right in range(left + 1, len(samples)):
            values.append(float(np.linalg.norm(coordinates[left] - coordinates[right])))
    return np.asarray(values)


def rankdata(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    ranks[order] = np.arange(len(values), dtype=float)
    unique, inverse, counts_unique = np.unique(values, return_inverse=True, return_counts=True)
    if np.any(counts_unique > 1):
        for group in range(len(unique)):
            positions = np.where(inverse == group)[0]
            if len(positions) > 1:
                ranks[positions] = ranks[positions].mean()
    return ranks


all_distances = condensed_distances(robustness_results["ALL_FILTERED"]["coordinates"])
distance_correlations = {}
for label in ["TOP_5000_VARIABLE", "TOP_2000_VARIABLE"]:
    other = condensed_distances(robustness_results[label]["coordinates"])
    distance_correlations[label] = clean_float(np.corrcoef(rankdata(all_distances), rankdata(other))[0, 1])

any_review = any(entry["status"] != "NO_OBVIOUS_ISSUE" for entry in sample_statuses)
critical_failure = any(entry["status"] == "TECHNICAL_PROBLEM_CONFIRMED" for entry in sample_statuses)
pca_dominated = any(
    entry["pca_feature_sets_flagged"] >= 2 for entry in sample_statuses
)
pca_robustness_summary = {
    "feature_sets": [
        {
            "feature_set": label,
            "gene_count": int(matrix.shape[0]),
            "pc1_variance_fraction": robustness_results[label]["pc1_variance"],
            "pc2_variance_fraction": robustness_results[label]["pc2_variance"],
        }
        for label, matrix in feature_sets
    ],
    "distance_rank_correlation_vs_all_filtered": distance_correlations,
    "sample_dominates_two_or_more_feature_sets": pca_dominated,
    "interpretation": (
        "ONE_OR_MORE_SAMPLES_REQUIRE_QC_REVIEW"
        if any_review
        else "STABLE_WITH_NO_SINGLE_SAMPLE_DOMINANCE_BY_FROZEN_CRITERIA"
    ),
}

limitations = [
    "n = 3 libraries per condition",
    "Recipient donor count and donor-to-library mapping are UNKNOWN",
    "Independent EV preparation count and preparation-to-library mapping are UNKNOWN",
    "Pairing is UNKNOWN and unsupported by authoritative metadata",
    "Exact RNA-seq control medium and vehicle are UNKNOWN",
    "Batch is not documented; no batch covariate can be justified",
    "PC1 captures a stable two-cluster structure aligned with replicate-1 versus replicate-2/3 labels, but no authoritative factor explains it; it is not assigned as batch or pairing",
    "The six libraries do not support donor-level or EV-preparation-level generalization",
    "QC transformations and PCA are descriptive and do not validate phenotype or treatment biology",
]

checkpoint = {
    "dataset": "GSE293956",
    "context_id": "CTX003",
    "sample_count": 6,
    "ev_count": conditions.count("HDF_EV"),
    "control_count": conditions.count("CONTROL"),
    "source_file": str(SOURCE.relative_to(ROOT)),
    "source_sha256": c1["sha256"],
    "c1_parser_rule_reused": True,
    "original_physical_data_rows": structure["physical_rows"],
    "valid_gene_rows": counts.shape[0],
    "structural_padding_rows": structure["padding_rows"],
    "genes_before_filtering": counts.shape[0],
    "zero_count_genes": int((counts.sum(axis=1) == 0).sum()),
    "filter_candidates": filter_rows,
    "primary_filter": config["primary_filter"]["rule"],
    "filtered_gene_count": int(primary_mask.sum()),
    "qc_transformation": config["qc_representation"],
    "library_qc": sample_qc_rows,
    "sample_statuses": sample_statuses,
    "correlation_summary": correlation_summary,
    "pca_pc1_variance": clean_float(primary_model.explained_variance_ratio_[0]),
    "pca_pc2_variance": clean_float(primary_model.explained_variance_ratio_[1]),
    "pca_coordinates": pca_rows,
    "pca_robustness_summary": pca_robustness_summary,
    "batch_status": "NOT_DOCUMENTED",
    "pairing_status": "NO_EVIDENCE / UNKNOWN",
    "recommended_de_design": "~ condition",
    "de_framework": "DESeq2",
    "de_filter_rule": config["frozen_de_plan"]["testing_filter"],
    "contrast": config["frozen_de_plan"]["contrast"],
    "positive_log2fc_definition": config["frozen_de_plan"]["positive_log2fc"],
    "de_reporting_thresholds": {
        "A": config["frozen_de_plan"]["threshold_a"],
        "B": config["frozen_de_plan"]["threshold_b"],
    },
    "gsea_release": config["frozen_pathway_plan"]["release"],
    "gsea_databases": config["frozen_pathway_plan"]["databases"],
    "gsea_ranking": config["frozen_pathway_plan"]["ranking"],
    "validation_questions": {
        "P": "Does candidate conserved-component evidence persist in CTX003?",
        "M": "Does CTX003 support either prior direction, another context-dependent response, or remain not testable?",
        "E": "Does CTX003 provide evidence where the prior comparison was NULL_NOT_TESTABLE?",
        "A": "Does CTX003 support either prior context or reinforce discordance/context dependence?",
        "I": "Does CTX003 share an active component with either context, show axis-only overlap, discordance, or no evidence?",
    },
    "phenotype_anchor_rules": {
        "P": "hDF CCK-8 at 24 h is a separate functional-assay layer from the 72 h transcriptome",
        "M": "hDF scratch assay at 24 h is a separate functional-assay layer from the 72 h transcriptome",
        "in_vivo": "Mouse wound, scar, and collagen outcomes are a different-model IN_VIVO layer and are not direct hDF transcriptomic validation",
    },
    "limitations": limitations,
    "technical_qc_failure": critical_failure,
    "decision": "REVIEW_REQUIRED" if critical_failure else "PASS_WITH_LIMITATIONS",
    "overall_pass": not critical_failure,
}
with (OUT / "exp003_c2_qc.json").open("w") as handle:
    json.dump(checkpoint, handle, indent=2)
    handle.write("\n")

print(json.dumps({
    "filtered_gene_count": checkpoint["filtered_gene_count"],
    "correlation_summary": correlation_summary,
    "pc1": checkpoint["pca_pc1_variance"],
    "pc2": checkpoint["pca_pc2_variance"],
    "sample_statuses": sample_statuses,
    "pca_robustness": pca_robustness_summary,
    "decision": checkpoint["decision"],
}, indent=2))
