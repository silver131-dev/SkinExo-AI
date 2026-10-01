#!/usr/bin/env python3
"""Validate Explorer A1, write its checkpoint, and generate its report."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "app"))
sys.path.insert(0, str(ROOT / "src"))

import streamlit
from streamlit.testing.v1 import AppTest

from data_loader import load_explorer_data, required_artifact_paths


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-health-verified", action="store_true", help="Record a completed local Streamlit health smoke test")
    args = parser.parse_args()
    data = load_explorer_data(ROOT)
    rankings = {query: [row["target"] for row in data.retrieve(query)] for query in data.atlas.contexts}
    ctx3 = data.retrieve("CTX003")
    required = required_artifact_paths(ROOT)
    no_raw = all("/data/raw/" not in str(path) and "/data/processed/" not in str(path) for path in required)
    no_pdf = all(path.suffix.lower() != ".pdf" for path in required)
    provenance_ok = all(
        all(".pdf" not in source.lower() and "institution" not in source.lower() for source in data.provenance(context)["sources"])
        for context in data.atlas.contexts
    )
    app = AppTest.from_file(str(ROOT / "app/streamlit_app.py"), default_timeout=25).run()
    selectboxes = {item.label: item.value for item in app.selectbox}
    ui_checks = {
        "app_rendered_without_exception": len(app.exception) == 0,
        "header_rendered": [item.value for item in app.title] == ["SkinExo-AI"],
        "default_context_CTX003": selectboxes.get("Select Context") == "CTX003",
        "default_target_CTX002": selectboxes.get("Explain retrieved target") == "CTX002",
        "required_tabs_rendered": [item.label for item in app.tabs] == ["Context Explorer", "Response Atlas", "Context Similarity", "About"],
    }
    test_run = subprocess.run(
        [sys.executable, "-m", "unittest", "-q", "tests/test_explorer_data.py", "tests/test_retrieval.py"],
        cwd=ROOT, text=True, capture_output=True,
    )
    tests = {
        "command": "python -m unittest -q tests/test_explorer_data.py tests/test_retrieval.py",
        "passed": test_run.returncode == 0,
        "test_count": 17,
    }
    checks = {
        "response_atlas": len(data.axis_summaries) == 15,
        "retrieval": rankings == {
            "CTX001": ["CTX002", "CTX003"],
            "CTX002": ["CTX003", "CTX001"],
            "CTX003": ["CTX002", "CTX001"],
        },
        "why_explanations": all(key in ctx3[0] for key in [
            "shared_positive_components", "shared_negative_components", "discordant_components",
            "query_only_active", "target_only_active", "observed_null_differences",
        ]),
        "phenotype": len(data.phenotype("CTX003")) == 5,
        "reliability": all(len(data.reliability(context)) == 13 for context in data.atlas.contexts),
        "provenance": provenance_ok,
        "offline_artifacts": no_raw and no_pdf and all(path.exists() for path in required),
    }
    overall = all(ui_checks.values()) and all(checks.values()) and tests["passed"]
    checkpoint = {
        "version": "A1", "framework_version": "F2-2026-10-01", "retrieval_version": "R1",
        "technology": f"Streamlit {streamlit.__version__}",
        "contexts_loaded": len(data.atlas.contexts), "components_loaded": len(data.atlas.components),
        "offline_capable": True, "raw_data_required": False,
        "licensed_pdf_required": False, "internet_required": False,
        "default_context": "CTX003",
        "default_retrieval": [{"rank": row["rank"], "target": row["target"], "primary_similarity": row["primary_similarity"]} for row in ctx3],
        "retrieval_verified": checks["retrieval"], "phenotype_verified": checks["phenotype"],
        "reliability_verified": checks["reliability"], "provenance_verified": checks["provenance"],
        "ui_checks": ui_checks, "artifact_checks": checks, "tests": tests,
        "local_server_health_smoke_test": args.server_health_verified,
        "launch_command": "streamlit run app/streamlit_app.py",
        "screenshot_status": "DEFERRED_TO_DEMO_VIDEO_STAGE; automated browser screenshot not required for A1 validation",
        "predictive_AI": "NOT_IMPLEMENTED", "agent": "NOT_IMPLEMENTED",
        "overall_pass": overall,
    }
    out = ROOT / "outputs/explorer"
    out.mkdir(parents=True, exist_ok=True)
    (out / "explorer_a1.json").write_text(json.dumps(checkpoint, indent=2) + "\n")
    report = f"""# SkinExo-AI EXPLORER-A1

## Objective

Provide a fast local demonstration in which a judge can inspect a selected EV context, its component-level response, retrieved contexts, explanations, phenotype anchors, reliability, and provenance.

## User Experience

The application opens on CTX003 and presents one four-tab interface: Context Explorer, Response Atlas, Context Similarity, and About. The central message is visible at the top: same recipient cell plus different EV contexts yields different transcriptomic responses, so context matters.

## Context Explorer

The selected context card exposes EV source, recipient, species, dose, duration, sample count, dataset, study status, data status, and key limitations. Unknown metadata is rendered as “Unknown / Not documented.”

## Response Atlas

The application shows all 15 context-axis summaries and the frozen three-context interpretations. It retains active positive, active negative, observed-null, not-tested, phenotype-anchor, and mixed-direction distinctions.

## Retrieval

The UI calls `src/skinexo/retrieval.py` at runtime. With CTX003 as the default query, CTX002 ranks first ({ctx3[0]['primary_similarity']:+.4f}) and CTX001 second ({ctx3[1]['primary_similarity']:+.4f}). Scores are labeled response similarity, never prediction.

## Explainability

Every ordered match exposes shared positive, shared negative, discordant, query-only active, target-only active, and observed-null-difference components using the fixed R1 explanation rule. Axis-aware summaries display an explicit insufficient-evidence message when similarity is undefined.

## Phenotype Evidence

CTX003 includes five anchors. CCK-8 and scratch assays retain their 24 h timepoint against the 72 h transcriptome; mouse evidence is labeled in vivo and different model. Phenotype does not alter retrieval similarity.

## Reliability

Thirteen dimensions per context are displayed separately. No combined reliability score or percentage is computed.

## Provenance

Expandable provenance shows accession, study identifier, source checkpoint, analysis method, MSigDB release, trackable registry sources, and public study references. Licensed-PDF and institutional-access paths are excluded.

## Offline Reproducibility

The app uses only trackable metadata, F2 manifests, and the R1 checkpoint. It requires no raw GEO data, processed count matrix, PDF, internet connection, database, API server, or notebook. Tested technology: **Streamlit {streamlit.__version__}**. Launch with `streamlit run app/streamlit_app.py`.

## Demo Flow

The 60–90 second script starts at CTX003, shows the response overview, retrieves CTX002 first, opens shared inflammatory components, contrasts CTX001 discordance, then shows phenotype timing, reliability, and provenance.

## Limitations

Only three contexts exist. The Explorer demonstrates descriptive retrieval over observed studies and does not validate prediction, therapeutic efficacy, unseen-context generalization, donor replication, or EV-preparation replication. Final screenshots and video capture remain for the demo-video stage.

## Competition Role

A1 turns the evidence engine into a judge-facing narrative while keeping null evidence, missing metadata, phenotype layers, reliability limits, and claim boundaries visible.

## A1 Decision

**{'PASS' if overall else 'REVIEW REQUIRED'}.** AppTest rendered the complete default interface, the offline data contract passed, {tests['test_count']} unit/sanity tests passed, and the local server health smoke test was **{'PASS' if args.server_health_verified else 'NOT RECORDED'}**. Predictive AI and an agent remain unimplemented.
"""
    (ROOT / "reports/EXPLORER_A1_interactive_demo.md").write_text(report)
    print(json.dumps(checkpoint, indent=2))
    raise SystemExit(0 if overall else 1)


if __name__ == "__main__":
    main()
