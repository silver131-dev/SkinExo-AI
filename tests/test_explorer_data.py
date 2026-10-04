"""Offline data and retrieval tests for SkinExo-AI Explorer A1."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))
sys.path.insert(0, str(ROOT / "src"))

from data_loader import load_explorer_data, required_artifact_paths
from presentation import build_context_summary, build_response_signature, humanize_activity_state


class ExplorerDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_explorer_data(ROOT)

    def test_all_three_contexts_load(self):
        self.assertEqual(self.data.atlas.contexts, ("CTX001", "CTX002", "CTX003"))

    def test_339_components_available(self):
        self.assertEqual(len(self.data.atlas.components), 339)
        self.assertEqual(len(self.data.universe), 339)

    def test_retrieval_rankings_reproduce_r1(self):
        expected = {
            "CTX001": ["CTX002", "CTX003"],
            "CTX002": ["CTX003", "CTX001"],
            "CTX003": ["CTX002", "CTX001"],
        }
        for query, targets in expected.items():
            self.assertEqual([row["target"] for row in self.data.retrieve(query)], targets)

    def test_ctx003_default_ranking(self):
        ranked = self.data.retrieve("CTX003")
        self.assertEqual((ranked[0]["rank"], ranked[0]["target"]), (1, "CTX002"))
        self.assertEqual((ranked[1]["rank"], ranked[1]["target"]), (2, "CTX001"))

    def test_ctx003_a2_summary_preserves_states_and_counts(self):
        signature = {row["axis"]: row for row in build_response_signature(self.data, "CTX003")}
        self.assertEqual(
            {axis: (row["state"], row["active_count"]) for axis, row in signature.items()},
            {
                "P": ("Observed null", 0),
                "M": ("Positive", 4),
                "E": ("Observed null", 0),
                "A": ("Positive", 1),
                "I": ("Positive", 27),
            },
        )

    def test_ctx003_a2_summary_is_descriptive_and_deterministic(self):
        summary = build_context_summary("CTX003", self.data)
        self.assertIn("largest active response family (27 active components)", summary["sentence"])
        self.assertIn("Migration", summary["sentence"])
        self.assertIn("Vascular / endothelial interaction", summary["sentence"])
        self.assertIn("Proliferation and ECM remodeling are observed null", summary["sentence"])
        self.assertNotIn("predict", summary["sentence"].lower())

    def test_ctx003_a2_top_retrieval_metrics_are_frozen(self):
        top = build_context_summary("CTX003", self.data)["top_retrieval"]
        self.assertEqual(top["target"], "CTX002")
        self.assertAlmostEqual(top["primary_similarity"], 0.6053, places=4)
        self.assertAlmostEqual(top["active_similarity"], 0.8563, places=4)
        self.assertEqual(top["shared_active_components"], 9)
        self.assertEqual(top["directional_concordance"], 1.0)

    def test_observed_null_and_not_tested_have_distinct_display_labels(self):
        self.assertEqual(humanize_activity_state("OBSERVED_NULL"), "Observed null")
        self.assertEqual(humanize_activity_state("NOT_TESTED"), "Not tested")
        self.assertNotEqual(
            humanize_activity_state("OBSERVED_NULL"),
            humanize_activity_state("NOT_TESTED"),
        )

    def test_a2_does_not_generate_aggregate_confidence(self):
        summary = build_context_summary("CTX003", self.data)
        self.assertFalse(summary["aggregate_confidence_score"])
        self.assertNotIn("confidence", summary["sentence"].lower())

    def test_phenotype_anchors_load(self):
        self.assertEqual(len(self.data.phenotype("CTX003")), 5)
        self.assertEqual(len(self.data.phenotype("CTX001")), 0)
        self.assertEqual(len(self.data.phenotype("CTX002")), 0)

    def test_reliability_records_load(self):
        for context in self.data.atlas.contexts:
            self.assertEqual(len(self.data.reliability(context)), 13)

    def test_no_raw_data_dependency(self):
        required = [str(path.relative_to(ROOT)) for path in required_artifact_paths(ROOT)]
        self.assertFalse(any(path.startswith("data/raw/") or path.startswith("data/processed/") for path in required))

    def test_no_licensed_pdf_dependency(self):
        required = [str(path).lower() for path in required_artifact_paths(ROOT)]
        self.assertFalse(any(path.endswith(".pdf") for path in required))
        for context in self.data.atlas.contexts:
            provenance = self.data.provenance(context)
            self.assertFalse(any(".pdf" in source.lower() for source in provenance["sources"]))

    def test_invalid_context_is_readable_error(self):
        with self.assertRaisesRegex(ValueError, "Unknown context ID"):
            self.data.context_card("CTX999")

    def test_streamlit_app_renders_default_demo(self):
        try:
            from streamlit.testing.v1 import AppTest
        except ModuleNotFoundError:
            self.skipTest("Streamlit is not installed in this interpreter")
        app = AppTest.from_file(str(ROOT / "app/streamlit_app.py"), default_timeout=20).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual([item.value for item in app.title], ["SkinExo-AI"])
        self.assertEqual(next(item for item in app.selectbox if item.label == "Select Context").value, "CTX003")
        rendered_markdown = "\n".join(str(item.value) for item in app.markdown)
        self.assertIn('<div class="retrieval-context">CTX002</div>', rendered_markdown)
        self.assertIn('<div class="retrieval-value">+0.6053</div>', rendered_markdown)
        self.assertIn("CTX003 and CTX002 share 9 active response components", rendered_markdown)


if __name__ == "__main__":
    unittest.main()
