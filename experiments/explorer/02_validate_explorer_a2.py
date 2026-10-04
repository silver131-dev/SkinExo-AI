#!/usr/bin/env python3
"""Validate Explorer A2 without rerunning any biological analysis."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "app"))
sys.path.insert(0, str(ROOT / "src"))

from streamlit.testing.v1 import AppTest

from data_loader import load_explorer_data, required_artifact_paths
from presentation import build_context_summary, build_response_signature, humanize_activity_state


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-health-verified", action="store_true")
    args = parser.parse_args()

    data = load_explorer_data(ROOT)
    signature = {row["axis"]: row for row in build_response_signature(data, "CTX003")}
    summary = build_context_summary("CTX003", data)
    ranked = data.retrieve("CTX003")
    top, second = ranked

    activity_counts = Counter(
        record["activity_state"] for record in data.atlas.records.values()
    )
    numerical_checks = {
        "contexts_3": len(data.atlas.contexts) == 3,
        "components_339": len(data.atlas.components) == 339,
        "response_records_1017": len(data.atlas.records) == 1017,
        "active_positive_139": activity_counts["ACTIVE_POSITIVE"] == 139,
        "active_negative_19": activity_counts["ACTIVE_NEGATIVE"] == 19,
        "observed_null_852": activity_counts["OBSERVED_NULL"] == 852,
        "not_tested_7": activity_counts["NOT_TESTED"] == 7,
        "ctx003_signature": {
            axis: (row["state"], row["active_count"]) for axis, row in signature.items()
        }
        == {
            "P": ("Observed null", 0),
            "M": ("Positive", 4),
            "E": ("Observed null", 0),
            "A": ("Positive", 1),
            "I": ("Positive", 27),
        },
        "ctx003_rank_1": top["target"] == "CTX002" and round(top["primary_similarity"], 4) == 0.6053,
        "ctx003_rank_2": second["target"] == "CTX001" and round(second["primary_similarity"], 4) == -0.2755,
        "active_union": round(top["active_similarity"], 4) == 0.8563,
        "shared_active": top["shared_active_components"] == 9,
        "direction_concordance": top["directional_concordance"] == 1.0,
    }

    app = AppTest.from_file(str(ROOT / "app/streamlit_app.py"), default_timeout=25).run()
    markdown = "\n".join(str(item.value) for item in app.markdown)
    rendered_text = "\n".join(
        [markdown]
        + [str(item.value) for item in app.subheader]
        + [str(item.value) for item in app.caption]
    )
    selectboxes = {item.label: item.value for item in app.selectbox}
    ui_checks = {
        "app_rendered_without_exception": not app.exception,
        "product_identity": [item.value for item in app.title] == ["SkinExo-AI"],
        "default_context_CTX003": selectboxes.get("Select Context") == "CTX003",
        "biological_summary": "largest active response family (27 active components)" in markdown,
        "response_signature": "Primary findings · response signature" in markdown,
        "retrieval_hero": '<div class="retrieval-context">CTX002</div>' in markdown,
        "primary_similarity": '<div class="retrieval-value">+0.6053</div>' in markdown,
        "why_visible": "CTX003 and CTX002 share 9 active response components" in markdown,
        "phenotype_separate": "Related phenotype anchors" in rendered_text and "Different experimental timepoint" in rendered_text,
        "reliability_dimension_level": "Uncertainty stays visible" in rendered_text and "no aggregate score" in rendered_text,
        "observed_null_distinct": humanize_activity_state("OBSERVED_NULL") != humanize_activity_state("NOT_TESTED"),
        "required_tabs": [item.label for item in app.tabs]
        == ["Context Explorer", "Response Atlas", "Context Similarity", "About"],
    }

    required = required_artifact_paths(ROOT)
    artifact_checks = {
        "offline_artifacts_present": all(path.exists() for path in required),
        "raw_data_not_required": not any("/data/raw/" in str(path) or "/data/processed/" in str(path) for path in required),
        "licensed_pdf_not_required": not any(path.suffix.lower() == ".pdf" for path in required),
        "summary_uses_structured_data": summary["top_retrieval"] == top,
        "aggregate_confidence_absent": summary["aggregate_confidence_score"] is False,
        "retrieval_version_R1": data.retrieval_checkpoint.get("retrieval_version") == "R1",
        "retrieval_checkpoint_pass": data.retrieval_checkpoint.get("overall_pass") is True,
    }

    prohibited = [
        "61% similarity",
        "61% confidence",
        "high confidence",
        "moderate confidence",
        "low confidence",
        "validated treatment",
        "proven angiogenesis",
        "causal phenotype",
        "foundation model",
        "digital twin",
    ]
    claim_text = "\n".join(
        path.read_text(errors="ignore")
        for path in [
            ROOT / "app/streamlit_app.py",
            ROOT / "app/components.py",
            ROOT / "app/presentation.py",
        ]
    ).lower()
    claim_checks = {f"absent_{re.sub(r'[^a-z0-9]+', '_', phrase.lower()).strip('_')}": phrase not in claim_text for phrase in prohibited}

    test_run = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    count_match = re.search(r"(\d+) passed", test_run.stdout)
    test_count = int(count_match.group(1)) if count_match else 0
    tests_passed = test_run.returncode == 0
    overall = (
        all(numerical_checks.values())
        and all(ui_checks.values())
        and all(artifact_checks.values())
        and all(claim_checks.values())
        and tests_passed
        and args.server_health_verified
    )

    checkpoint = {
        "version": "A2",
        "mode": "PRODUCT_DEMO",
        "framework_version": "F2-2026-10-01",
        "retrieval_version": "R1",
        "default_context": "CTX003",
        "top_retrieval": "CTX002",
        "primary_similarity": 0.6053,
        "second_retrieval": "CTX001",
        "second_similarity": -0.2755,
        "active_union_similarity": 0.8563,
        "shared_active": 9,
        "direction_concordance": 1.0,
        "aggregate_confidence_score": False,
        "llm_used": False,
        "external_api_required": False,
        "offline_capable": True,
        "raw_data_required": False,
        "licensed_pdf_required": False,
        "internet_required": False,
        "scientific_values_changed": False,
        "retrieval_algorithm_changed": False,
        "numerical_checks": numerical_checks,
        "ui_checks": ui_checks,
        "artifact_checks": artifact_checks,
        "claim_checks": claim_checks,
        "tests_passed": test_count,
        "tests_ok": tests_passed,
        "server_health_verified": args.server_health_verified,
        "overall_pass": overall,
    }
    output = ROOT / "outputs/explorer/explorer_a2.json"
    output.write_text(json.dumps(checkpoint, indent=2) + "\n")
    print(json.dumps(checkpoint, indent=2))
    raise SystemExit(0 if overall else 1)


if __name__ == "__main__":
    main()
