"""Offline, UI-neutral data access for the SkinExo-AI Explorer."""

from __future__ import annotations

import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from skinexo.retrieval import AtlasData, ResponseMatrix, build_response_matrix, load_atlas, retrieve_contexts


CONTEXT_LABELS = {
    "CTX001": "CTX001 · Endothelial EV → Human Dermal Fibroblast",
    "CTX002": "CTX002 · Bone-Marrow MSC sEV → Human Dermal Fibroblast",
    "CTX003": "CTX003 · Human Dermal Fibroblast EV → Human Dermal Fibroblast",
}
AXIS_NAMES = {
    "P": "Proliferation / Cell Cycle",
    "M": "Migration / Motility",
    "E": "ECM Organization / Remodeling",
    "A": "Vascular / Endothelial Interaction",
    "I": "Inflammation / Immune Signaling",
}
INTERPRETATIONS = {
    "P": "Two-context shared component only",
    "M": "Context-dependent / discordant",
    "E": "Null / not testable",
    "A": "Context-dependent / discordant",
    "I": "Conserved axis / context variant",
}


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def required_artifact_paths(root: Path = ROOT) -> tuple[Path, ...]:
    """Trackable artifacts required for normal offline operation."""
    return (
        root / "data/metadata/skinexo_component_universe.csv",
        root / "data/metadata/skinexo_context_features.csv",
        root / "data/metadata/skinexo_contexts.csv",
        root / "data/metadata/skinexo_response_atlas_long.csv",
        root / "data/metadata/skinexo_axis_summary.csv",
        root / "data/metadata/skinexo_phenotype_anchors.csv",
        root / "data/metadata/skinexo_reliability.csv",
        root / "outputs/framework/framework_f2_atlas.json",
        root / "outputs/framework/framework_f2_validation.json",
        root / "outputs/retrieval/retrieval_r1.json",
    )


@dataclass(frozen=True)
class ExplorerData:
    root: Path
    atlas: AtlasData
    matrix: ResponseMatrix
    universe: dict[str, dict[str, str]]
    axis_summaries: dict[tuple[str, str], dict[str, str]]
    context_registry: dict[str, dict[str, str]]
    retrieval_checkpoint: dict[str, Any]

    def validate_context(self, context_id: str) -> None:
        if context_id not in self.atlas.contexts:
            raise ValueError(f"Unknown context ID: {context_id}")

    def context_card(self, context_id: str) -> dict[str, str]:
        self.validate_context(context_id)
        feature = self.atlas.context_features[context_id]
        registry = self.context_registry[context_id]
        return {
            "EV source": display_value(feature["ev_source"]),
            "Recipient": display_value(feature["recipient"]),
            "Species": display_value(feature["species"]),
            "Dose": display_value(feature["dose"]),
            "Duration": f"{feature['duration_h']} h" if feature["duration_h"] else "Unknown / Not documented",
            "Sample count": display_value(feature["sample_count"]),
            "Dataset": display_value(feature["dataset_id"]),
            "Study status": display_value(registry["study_status"]),
            "Data status": display_value(feature["data_status"]),
            "Key limitations": display_value(feature["major_limitations"]),
        }

    def context_details(self, context_id: str) -> dict[str, str]:
        """Return presentation-ready experimental metadata without dropping unknowns."""

        self.validate_context(context_id)
        feature = self.atlas.context_features[context_id]
        registry = self.context_registry[context_id]
        return {
            "EV source": display_value(feature["ev_source"]),
            "Recipient": display_value(feature["recipient"]),
            "Species": display_value(feature["species"]),
            "Dataset": display_value(feature["dataset_id"]),
            "Dose": display_value(feature["dose"]),
            "Duration": f"{feature['duration_h']} h" if feature["duration_h"] else "Unknown",
            "Sample count": display_value(feature["sample_count"]),
            "Treatment / control": (
                f"{display_value(registry['treatment'])} / {display_value(registry['control'])}"
            ),
            "Study status": display_value(registry["study_status"]),
            "Data status": display_value(feature["data_status"]),
            "Batch": display_value(registry["batch_count"]),
            "Pairing": display_value(feature["pairing_status"]),
            "Recipient donor": display_value(feature["donor_status"]),
            "EV preparation": display_value(feature["ev_preparation_status"]),
            "Experimental system": display_value(registry["experimental_system"]),
            "Omics": display_value(registry["omics_type"]),
            "Statistical design": display_value(registry["statistical_design"]),
            "Key limitations": display_value(feature["major_limitations"]),
        }

    def axes_for_context(self, context_id: str) -> list[dict[str, Any]]:
        self.validate_context(context_id)
        results = []
        for axis in "PMEAI":
            row = dict(self.axis_summaries[(context_id, axis)])
            row["axis_name"] = AXIS_NAMES[axis]
            row["phenotype_available"] = int(row["phenotype_anchor_count"]) > 0
            results.append(row)
        return results

    def components_for_axis(self, context_id: str, axis: str) -> list[dict[str, Any]]:
        self.validate_context(context_id)
        if axis not in AXIS_NAMES:
            raise ValueError(f"Unknown axis: {axis}")
        rows = []
        for component in self.atlas.components:
            if self.atlas.component_axis[component] != axis:
                continue
            record = self.atlas.records[(context_id, component)]
            definition = self.universe[component]
            rows.append({
                "component_id": component,
                "component_name": definition["component_name"],
                "activity_state": record["activity_state"],
                "direction": record["direction"],
                "NES": None if record["NES"] == "" else float(record["NES"]),
                "FDR": None if record["FDR"] == "" else float(record["FDR"]),
                "source_database": definition["source_database"],
                "source_term": record["representative_term_id"] or definition["source_term_id"],
                "source_checkpoint": record["source_checkpoint"],
            })
        return rows

    def retrieve(self, context_id: str) -> list[dict[str, Any]]:
        self.validate_context(context_id)
        return retrieve_contexts(self.atlas, self.matrix, context_id)

    def phenotype(self, context_id: str) -> list[dict[str, str]]:
        self.validate_context(context_id)
        return self.atlas.phenotype_anchors.get(context_id, [])

    def reliability(self, context_id: str) -> list[dict[str, str]]:
        self.validate_context(context_id)
        return self.atlas.reliability.get(context_id, [])

    def provenance(self, context_id: str) -> dict[str, Any]:
        self.validate_context(context_id)
        registry = self.context_registry[context_id]
        checkpoints = sorted({self.atlas.records[(context_id, component)]["source_checkpoint"] for component in self.atlas.components})
        sources = []
        for source in registry["source_provenance"].split(";"):
            clean = source.strip()
            if clean and ".pdf" not in clean.lower() and "institution" not in clean.lower():
                sources.append(clean)
        study_references = sorted({anchor["source"] for anchor in self.phenotype(context_id) if anchor.get("source")})
        return {
            "dataset": registry["dataset_id"], "study_id": registry["study_id"],
            "source_checkpoint": "; ".join(checkpoints),
            "analysis_method": "DESeq2 Wald-ranked GSEA component representation",
            "gene_set_release": "MSigDB 2026.1.Hs (frozen C4 release)",
            "sources": sources, "study_references": study_references,
        }


def display_value(value: str | None) -> str:
    if value is None or not str(value).strip() or str(value).strip().upper() in {"UNKNOWN", "NOT_DOCUMENTED", "NO_EVIDENCE"}:
        return "Unknown / Not documented"
    return str(value)


def load_explorer_data(root: str | Path = ROOT) -> ExplorerData:
    root = Path(root).resolve()
    missing = [path for path in required_artifact_paths(root) if not path.exists()]
    if missing:
        relative = [str(path.relative_to(root)) for path in missing]
        raise FileNotFoundError("Missing Explorer artifacts: " + ", ".join(relative))
    validation = json.loads((root / "outputs/framework/framework_f2_validation.json").read_text())
    if validation.get("status") != "PASS":
        raise RuntimeError("Framework F2 validation must PASS before Explorer launch")
    retrieval_checkpoint = json.loads((root / "outputs/retrieval/retrieval_r1.json").read_text())
    if not retrieval_checkpoint.get("overall_pass"):
        raise RuntimeError("Retrieval R1 checkpoint must PASS before Explorer launch")
    atlas = load_atlas(root)
    universe_rows = _rows(root / "data/metadata/skinexo_component_universe.csv")
    axes = _rows(root / "data/metadata/skinexo_axis_summary.csv")
    context_registry_rows = _rows(root / "data/metadata/skinexo_contexts.csv")
    return ExplorerData(
        root=root, atlas=atlas, matrix=build_response_matrix(atlas),
        universe={row["component_id"]: row for row in universe_rows},
        axis_summaries={(row["context_id"], row["axis"]): row for row in axes},
        context_registry={row["context_id"]: row for row in context_registry_rows},
        retrieval_checkpoint=retrieval_checkpoint,
    )
