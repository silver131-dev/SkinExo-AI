#!/usr/bin/env python3
"""EXP002-C2R technical-only EV_8 review; no DE or biological comparison."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
from pathlib import Path
from xml.etree import ElementTree

import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from scipy.stats import entropy


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/exp002"
OUT = ROOT / "outputs/exp002"
SAMPLE = "EV_8"


def table(path: Path, delimiter: str = ",") -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def median_ratio(value: float, values: list[float]) -> float:
    return float(value / np.median(values))


def sample_soft(gsm: str) -> tuple[dict[str, str], list[str]]:
    entries: dict[str, str] = {}
    block: list[str] = []
    active = False
    with gzip.open(RAW / "GSE251807_family.soft.gz", "rt") as handle:
        for line in handle:
            if line.startswith("^SAMPLE = "):
                active = line.strip().split(" = ", 1)[1] == gsm
            if active:
                block.append(line.rstrip("\n"))
            if active and line.startswith("!Sample_") and " = " in line:
                key, value = line.rstrip("\n").split(" = ", 1)
                entries[key] = value
    return entries, block


def main() -> None:
    criteria = json.loads((ROOT / "configs/exp002_c2r_technical_criteria.json").read_text())
    c1r = json.loads((OUT / "exp002_c1r_resolution.json").read_text())
    c2 = json.loads((OUT / "exp002_c2_qc.json").read_text())
    if not criteria["declared_before_metrics_and_decision"] or c1r["decision"] != "LIMITED_GO":
        raise ValueError("C1R or preregistered technical criteria mismatch")
    if c2["sample_count"] != 16 or c2["filtered_gene_count"] != 13724:
        raise ValueError("C2 frozen input mismatch")

    meta = table(ROOT / "data/metadata/GSE251807_samples.csv")
    if len(meta) != 16 or [r["sample_name"] for r in meta].count(SAMPLE) != 1:
        raise ValueError("Expected 16 unique sample rows and one EV_8")
    ev8 = next(r for r in meta if r["sample_name"] == SAMPLE)
    accession_fields = ("gsm_id", "srr_id", "sra_experiment_id", "biosample_id", "quantification_file")
    duplicates = {field: len({r[field] for r in meta}) != len(meta) for field in accession_fields}
    if any(duplicates.values()):
        raise ValueError(f"Duplicate sample identities: {duplicates}")
    soft, block = sample_soft(ev8["gsm_id"])
    ena_info = table(RAW / "PRJNA1055484_ena_runinfo.tsv", "\t")
    ena_depth = table(RAW / "PRJNA1055484_ena_depth.tsv", "\t")
    run_matches = [r for r in ena_info if r["run_accession"] == ev8["srr_id"]]
    depth_matches = [r for r in ena_depth if r["run_accession"] == ev8["srr_id"]]
    if len(run_matches) != 1 or len(depth_matches) != 1:
        raise ValueError("EV_8 SRA run absent or duplicated in ENA metadata")
    ena = run_matches[0]
    depth = depth_matches[0]
    xml_root = ElementTree.parse(RAW / "SAMN39054792_ena_sample.xml").getroot()
    biosample = xml_root.find("SAMPLE")
    if biosample is None:
        raise ValueError("No EV_8 BioSample XML record")
    xml_attrs = {e.findtext("TAG"): e.findtext("VALUE") for e in biosample.findall("./SAMPLE_ATTRIBUTES/SAMPLE_ATTRIBUTE")}
    xml_title = biosample.findtext("TITLE")
    relations = "\n".join(line for line in block if line.startswith("!Sample_relation"))
    geo_quant_url = soft.get("!Sample_supplementary_file_1", "")
    quant_path = RAW / ev8["quantification_file"]
    with gzip.open(quant_path, "rt") as handle:
        quant = pd.read_csv(handle, sep="\t")  # Reads to EOF and validates gzip CRC.
    quant_valid = (list(quant.columns) == ["Name", "Length", "EffectiveLength", "TPM", "NumReads"]
                   and quant["Name"].is_unique
                   and quant[["Length", "EffectiveLength", "TPM", "NumReads"]].notna().all().all()
                   and np.isfinite(quant[["Length", "EffectiveLength", "TPM", "NumReads"]].to_numpy()).all()
                   and (quant[["Length", "EffectiveLength", "TPM", "NumReads"]].to_numpy() >= 0).all())
    file_digests = {}
    for row in meta:
        digest = hashlib.sha256()
        with (RAW / row["quantification_file"]).open("rb") as handle:
            for chunk in iter(lambda: handle.read(1 << 20), b""):
                digest.update(chunk)
        file_digests[row["sample_name"]] = digest.hexdigest()
    identity = {
        "sample_name_match": soft.get("!Sample_title") == SAMPLE and xml_title == SAMPLE,
        "condition_match": ("!Sample_characteristics_ch1 = treatment: NHDFs exposed to small extracellular vesicles" in block
                            and "small extracellular vesicles" in xml_attrs.get("treatment", "").lower()
                            and ev8["condition"] == "MSC_sEV"),
        "batch_match": ("!Sample_characteristics_ch1 = batch: 2" in block
                        and xml_attrs.get("batch") == ev8["batch"] == "2"),
        "gsm_to_biosample_match": (biosample.attrib.get("accession") == ev8["biosample_id"]
                                     and biosample.attrib.get("alias") == ev8["gsm_id"]
                                     and ev8["biosample_id"] in relations),
        "gsm_to_experiment_match": ena["experiment_accession"] == ev8["sra_experiment_id"]
                                   and ena["experiment_accession"] in relations,
        "experiment_to_run_match": ena["run_accession"] == ev8["srr_id"]
                                   and depth["experiment_accession"] == ev8["sra_experiment_id"],
        "run_to_biosample_match": ena["sample_accession"] == depth["sample_accession"] == ev8["biosample_id"],
        "run_unique_in_selected_metadata": [r["srr_id"] for r in meta].count(ev8["srr_id"]) == 1,
        "run_unique_in_ena_project": sum(r["run_accession"] == ev8["srr_id"] for r in ena_info) == 1,
        "quantification_file_match": (geo_quant_url.rsplit("/", 1)[-1] == ev8["quantification_file"]
                                       and quant_path.exists() and quant_valid),
        "quantification_not_byte_duplicate": list(file_digests.values()).count(file_digests[SAMPLE]) == 1,
    }
    if not all(identity.values()):
        raise ValueError(f"EV_8 identity chain failure: {identity}")

    agg = table(OUT / "exp002_c2_aggregation_qc.csv")
    agg_by_name = {r["sample"]: r for r in agg}
    depth_by_run = {r["run_accession"]: r for r in ena_depth}
    if len(agg) != 16 or len(agg_by_name) != 16 or any(r["srr_id"] not in depth_by_run for r in meta):
        raise ValueError("Aggregation or ENA depth missing selected samples")
    identity["quantification_sum_match"] = abs(float(quant["NumReads"].sum()) - float(agg_by_name[SAMPLE]["original_salmon_numreads_sum"])) < 0.02
    if not identity["quantification_sum_match"]:
        raise ValueError("EV_8 local GEO quantification sum differs from C2 aggregation input")
    counts = pd.read_csv(ROOT / "data/processed/exp002/estimated_gene_counts.csv.gz", index_col=0)
    if list(counts.columns) != [r["sample_name"] for r in meta] or counts.shape != (37307, 16):
        raise ValueError("Gene count matrix mapping differs from C2")
    count_values = counts.to_numpy(dtype=float)
    if not np.isfinite(count_values).all() or (count_values < 0).any():
        raise ValueError("Nonfinite or negative gene estimates")
    total = count_values.sum(axis=0)
    if any(abs(float(agg_by_name[r["sample_name"]]["retained_salmon_numreads_sum"]) - total[i]) > 0.02
           for i, r in enumerate(meta)):
        raise ValueError("Gene totals do not equal retained Salmon transcript sums")
    cpm = count_values / total[np.newaxis, :] * 1e6
    qc_rows = []
    for i, r in enumerate(meta):
        name = r["sample_name"]
        rd = depth_by_run[r["srr_id"]]
        profile = count_values[:, i]
        probs = profile[profile > 0] / total[i]
        ranked = np.sort(profile)[::-1]
        detected = cpm[:, i] >= 1
        qc_rows.append({
            "sample": name, "condition": r["condition"], "batch": r["batch"],
            "read_count": int(rd["read_count"]), "base_count": int(rd["base_count"]),
            "fastq_bytes_total": sum(int(x) for x in rd["fastq_bytes"].split(";") if x),
            "salmon_numreads_sum": float(agg_by_name[name]["original_salmon_numreads_sum"]),
            "gene_count_total": float(total[i]),
            "salmon_numreads_per_ena_read_proxy": float(agg_by_name[name]["original_salmon_numreads_sum"]) / int(rd["read_count"]),
            "expressed_genes_cpm_ge_1": int(detected.sum()),
            "nonzero_genes": int(np.count_nonzero(profile)),
            "zero_gene_fraction": float(np.mean(profile == 0)),
            "median_log2_cpm_expressed": float(np.median(np.log2(cpm[detected, i] + 1))),
            "p90_log2_cpm_expressed": float(np.quantile(np.log2(cpm[detected, i] + 1), 0.9)),
            "p99_log2_cpm_expressed": float(np.quantile(np.log2(cpm[detected, i] + 1), 0.99)),
            "top10_count_fraction": float(ranked[:10].sum() / total[i]),
            "top100_count_fraction": float(ranked[:100].sum() / total[i]),
            "normalized_count_entropy": float(entropy(probs) / np.log(len(profile))),
        })
    qc = pd.DataFrame(qc_rows)
    qc.to_csv(OUT / "exp002_c2r_sample_technical_qc.csv", index=False)
    this = qc.loc[qc["sample"] == SAMPLE].iloc[0]
    ev = qc.loc[qc["condition"] == "MSC_sEV"]
    same_batch_ev = ev.loc[ev["batch"] == "2"]
    ratio_fields = ["read_count", "base_count", "fastq_bytes_total", "salmon_numreads_sum", "gene_count_total"]
    depth_ratios = {
        field: {
            "overall_median": median_ratio(float(this[field]), qc[field].to_list()),
            "ev_median": median_ratio(float(this[field]), ev[field].to_list()),
            "same_batch_ev_median": median_ratio(float(this[field]), same_batch_ev[field].to_list()),
        } for field in ratio_fields
    }
    proxy = "salmon_numreads_per_ena_read_proxy"
    proxy_summary = {
        "EV8_value": float(this[proxy]),
        "overall_median": float(qc[proxy].median()),
        "EV_median": float(ev[proxy].median()),
        "same_batch_EV_median": float(same_batch_ev[proxy].median()),
        "EV8_to_overall_median": median_ratio(float(this[proxy]), qc[proxy].to_list()),
        "EV8_to_same_batch_EV_median": median_ratio(float(this[proxy]), same_batch_ev[proxy].to_list()),
        "interpretation": criteria["quantification_proxy_note"],
    }
    fields = ["expressed_genes_cpm_ge_1", "nonzero_genes", "zero_gene_fraction", "median_log2_cpm_expressed",
              "p90_log2_cpm_expressed", "p99_log2_cpm_expressed", "top10_count_fraction",
              "top100_count_fraction", "normalized_count_entropy"]
    distribution = {
        field: {"EV8": float(this[field]), "overall_median": float(qc[field].median()),
                "same_batch_EV_median": float(same_batch_ev[field].median()),
                "EV8_to_same_batch_EV_median": median_ratio(float(this[field]), same_batch_ev[field].to_list())}
        for field in fields
    }
    corr = pd.read_csv(OUT / "sample_correlation.csv", index_col=0)
    names = [r["sample_name"] for r in meta]
    if list(corr.index) != names or list(corr.columns) != names:
        raise ValueError("Correlation matrix order differs from metadata")
    peers = [r for r in meta if r["sample_name"] != SAMPLE]
    corr_values = {r["sample_name"]: float(corr.loc[SAMPLE, r["sample_name"]]) for r in peers}
    groups = {
        "same_batch_EV": [r["sample_name"] for r in peers if r["batch"] == "2" and r["condition"] == "MSC_sEV"],
        "other_batch_EV": [r["sample_name"] for r in peers if r["batch"] == "1" and r["condition"] == "MSC_sEV"],
        "controls": [r["sample_name"] for r in peers if r["condition"] == "CTRL_DMEM"],
    }
    all_mean = {s: float(corr.loc[s].drop(s).mean()) for s in names}
    within_batch_mean = {r["sample_name"]: float(corr.loc[r["sample_name"],
                               [p["sample_name"] for p in meta if p["batch"] == r["batch"] and p["sample_name"] != r["sample_name"]]].mean()) for r in meta}
    correlation = {
        "EV8_by_group": {g: {s: corr_values[s] for s in ss} for g, ss in groups.items()},
        "EV8_group_means": {g: float(np.mean([corr_values[s] for s in ss])) for g, ss in groups.items()},
        "nearest_neighbor": max(corr_values, key=corr_values.get),
        "nearest_neighbor_r": max(corr_values.values()),
        "lowest_correlation_sample": min(corr_values, key=corr_values.get),
        "lowest_correlation_r": min(corr_values.values()),
        "EV8_mean_to_all_other_samples": all_mean[SAMPLE],
        "all_sample_mean_correlation_range": [min(all_mean.values()), max(all_mean.values())],
        "EV8_mean_within_batch": within_batch_mean[SAMPLE],
        "all_sample_within_batch_mean_range": [min(within_batch_mean.values()), max(within_batch_mean.values())],
    }
    pca = pd.read_csv(OUT / "pca_robustness.csv")
    pca_summary = {}
    for feature_set, frame in pca.groupby("feature_set", sort=False):
        frame = frame.set_index("sample").loc[names]
        xy = frame[["PC1", "PC2"]].to_numpy()
        dist = cdist(xy, xy)
        np.fill_diagonal(dist, np.inf)
        nearest = dist.min(axis=1)
        same_batch_nearest = []
        centroid_distance = []
        for i, r in enumerate(meta):
            batch_peers = [j for j, p in enumerate(meta) if j != i and p["batch"] == r["batch"]]
            same_batch_nearest.append(float(dist[i, batch_peers].min()))
            centroid_distance.append(float(np.linalg.norm(xy[i] - xy[batch_peers].mean(axis=0))))
        idx = names.index(SAMPLE)
        order = np.argsort(-nearest)
        batch_order = np.argsort(-np.array(same_batch_nearest))
        pca_summary[feature_set] = {
            "features": int(frame["feature_count"].iloc[0]),
            "EV8_nearest_distance": float(nearest[idx]),
            "all_sample_median_nearest_distance": float(np.median(nearest)),
            "EV8_nearest_to_median_ratio": float(nearest[idx] / np.median(nearest)),
            "EV8_nearest_distance_rank_descending": int(np.where(order == idx)[0][0] + 1),
            "second_highest_nearest_sample": names[order[1]],
            "second_highest_nearest_distance": float(nearest[order[1]]),
            "second_highest_nearest_to_median_ratio": float(nearest[order[1]] / np.median(nearest)),
            "EV8_same_batch_nearest_distance": same_batch_nearest[idx],
            "EV8_same_batch_rank_descending": int(np.where(batch_order == idx)[0][0] + 1),
            "EV8_distance_to_same_batch_peers_centroid": centroid_distance[idx],
            "highest_batch_peer_centroid_distance_sample": names[int(np.argmax(centroid_distance))],
            "all_sample_nearest_distance_ranking": [names[i] for i in order],
        }
    triggers = criteria["review_triggers_not_exclusion_criteria"]
    expression_trigger = (distribution["expressed_genes_cpm_ge_1"]["EV8_to_same_batch_EV_median"] <
                          triggers["same_batch_expressed_gene_count_below_median_fraction"] and
                          distribution["top10_count_fraction"]["EV8_to_same_batch_EV_median"] >
                          triggers["same_batch_top10_expression_fraction_above_median_multiple"])
    proxy_trigger = not (1 / triggers["quantification_proxy_ratio_outside_median_fold"] <=
                         proxy_summary["EV8_to_overall_median"] <=
                         triggers["quantification_proxy_ratio_outside_median_fold"])
    # Descriptive outlier flags do not constitute a technical exclusion.
    technical_defect = not all(identity.values()) or not quant_valid
    decision = "EXCLUDE_TECHNICAL" if technical_defect else "RETAIN"
    checkpoint = {
        "dataset": "GSE251807", "experiment": "EXP002", "checkpoint": "EXP002-C2R",
        "source_urls": {
            "geo_sample": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM7988524",
            "ena_biosample": "https://www.ebi.ac.uk/ena/browser/view/SAMN39054792",
            "ena_run": "https://www.ebi.ac.uk/ena/browser/view/SRR27319309",
            "geo_quantification": ev8["quantification_source"],
        },
        "EV8_identity_mapping": {"GSM": ev8["gsm_id"], "BioSample": ev8["biosample_id"],
                                 "SRA_experiment": ev8["sra_experiment_id"], "SRA_run": ev8["srr_id"],
                                 "quantification_file": ev8["quantification_file"],
                                 "checks": {k: "PASS" if v else "FAIL" for k, v in identity.items()}},
        "EV8_read_count": int(this["read_count"]), "EV8_base_count": int(this["base_count"]),
        "EV8_fastq_bytes_total": int(this["fastq_bytes_total"]),
        "EV8_salmon_total": float(this["salmon_numreads_sum"]),
        "EV8_gene_count_total": float(this["gene_count_total"]),
        "depth_ratios": depth_ratios,
        "quantification_efficiency_summary": proxy_summary,
        "expression_distribution_summary": distribution,
        "correlation_summary": correlation,
        "pca_extremeness_summary": pca_summary,
        "technical_exclusion_criteria": criteria["technical_exclusion_criteria"],
        "review_triggers_not_exclusion_criteria": triggers,
        "expression_review_trigger": bool(expression_trigger),
        "quantification_proxy_review_trigger": bool(proxy_trigger),
        "technical_defect_found": technical_defect,
        "EV8_decision": decision,
        "primary_sample_count": 16 if decision == "RETAIN" else 15,
        "sensitivity_sample_count": 15 if decision == "RETAIN" else 16,
        "primary_design": "~ batch + condition",
        "sensitivity_design": "~ batch + condition",
        "preregistered_robustness_metrics": [
            "log2FC Pearson correlation across shared tested genes",
            "log2FC Spearman correlation across shared tested genes",
            "log2FC direction concordance across shared tested genes",
            "overlap of padj < 0.05 genes",
            "overlap of padj < 0.05 and abs(log2FC) >= 1 genes",
            "P/M/E/A/I GSEA direction stability",
            "GSEA NES correlation across common eligible terms",
        ],
        "batch_interaction_decision": "No interaction in primary model; estimate average condition effect across two balanced batches with additive batch adjustment.",
        "remaining_limitations": [
            "One documented recipient NHDF donor lot; no donor-level generalization",
            "Independent EV-preparation count unknown; no EV-preparation-level generalization",
            "Original Salmon index release and mapping-rate logs unavailable; GENCODE v44 is compatible, not confirmed original",
            "ENA read_count and Salmon NumReads units may differ; their ratio is not an absolute mapping efficiency",
            "PCA extremeness persists; no FASTQ-level sequence-quality or contamination analysis was performed",
        ],
        "c2_final_status": "PASS WITH LIMITATIONS" if decision == "RETAIN" else "REVIEW REQUIRED",
        "overall_pass": decision == "RETAIN",
    }
    (OUT / "exp002_c2r_ev8_review.json").write_text(json.dumps(checkpoint, indent=2) + "\n")
    print(f"EV_8 identity: {'PASS' if all(identity.values()) else 'FAIL'}")
    print(f"EV_8 decision: {decision}; C2 final status: {checkpoint['c2_final_status']}")
    print(f"ENA read count: {checkpoint['EV8_read_count']:,}; Salmon total: {checkpoint['EV8_salmon_total']:,.0f}")
    for name, entry in pca_summary.items():
        print(f"PCA {name}: nearest-distance ratio {entry['EV8_nearest_to_median_ratio']:.2f}; rank {entry['EV8_nearest_distance_rank_descending']}/16")


if __name__ == "__main__":
    main()
