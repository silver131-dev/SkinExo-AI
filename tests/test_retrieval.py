"""Synthetic sanity tests for SkinExo-AI RETRIEVAL-R1."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from skinexo.retrieval import (
    AtlasData,
    active_union_similarity,
    build_response_matrix,
    compute_shared_tested_mask,
    explain_pair,
    masked_cosine_similarity,
)


class RetrievalSanityTests(unittest.TestCase):
    def test_a_identical_vector_is_one(self):
        vector = np.array([1.0, -2.0, 3.0])
        result = masked_cosine_similarity(vector, vector.copy(), np.ones(3, dtype=bool))
        self.assertEqual(result["status"], "DEFINED")
        self.assertTrue(math.isclose(result["similarity"], 1.0, abs_tol=1e-12))

    def test_b_exact_sign_reversal_is_negative_one(self):
        vector = np.array([1.0, -2.0, 3.0])
        result = masked_cosine_similarity(vector, -vector, np.ones(3, dtype=bool))
        self.assertEqual(result["status"], "DEFINED")
        self.assertTrue(math.isclose(result["similarity"], -1.0, abs_tol=1e-12))

    def test_c_nonoverlapping_masks_are_undefined(self):
        first = np.array([True, False])
        second = np.array([False, True])
        mask = compute_shared_tested_mask(first, second)
        result = masked_cosine_similarity(np.array([1.0, np.nan]), np.array([np.nan, 1.0]), mask)
        self.assertEqual(result["status"], "INSUFFICIENT_OVERLAP")
        self.assertIsNone(result["similarity"])

    def test_d_jointly_null_does_not_create_active_similarity(self):
        vector_a = np.array([1.2, -0.7])
        vector_b = np.array([0.8, -1.1])
        tested = np.ones(2, dtype=bool)
        inactive = np.zeros(2, dtype=bool)
        result = active_union_similarity(vector_a, vector_b, tested, tested, inactive, inactive)
        self.assertEqual(result["component_count"], 0)
        self.assertEqual(result["status"], "INSUFFICIENT_OVERLAP")
        self.assertIsNone(result["similarity"])

    def test_e_not_tested_is_excluded_not_zero(self):
        vector_a = np.array([np.nan, 2.0])
        vector_b = np.array([100.0, 2.0])
        mask = compute_shared_tested_mask(np.array([False, True]), np.array([True, True]))
        result = masked_cosine_similarity(vector_a, vector_b, mask)
        self.assertEqual(result["component_count"], 1)
        self.assertTrue(math.isclose(result["similarity"], 1.0, abs_tol=1e-12))

    def test_f_unknown_is_excluded_not_zero(self):
        vector_a = np.array([np.nan, -3.0])
        vector_b = np.array([0.0, -3.0])
        mask = compute_shared_tested_mask(np.array([False, True]), np.array([True, True]))
        result = masked_cosine_similarity(vector_a, vector_b, mask)
        self.assertEqual(result["component_count"], 1)
        self.assertTrue(math.isclose(result["similarity"], 1.0, abs_tol=1e-12))

    def test_g_ordered_explanations_are_reproducible(self):
        contexts = ("Q", "T")
        components = ("P001", "M001", "I001")
        states = {
            ("Q", "P001"): ("ACTIVE_POSITIVE", "1", "1", "2.0"),
            ("Q", "M001"): ("ACTIVE_NEGATIVE", "1", "1", "-1.5"),
            ("Q", "I001"): ("OBSERVED_NULL", "1", "0", "0.4"),
            ("T", "P001"): ("ACTIVE_POSITIVE", "1", "1", "1.8"),
            ("T", "M001"): ("ACTIVE_POSITIVE", "1", "1", "1.1"),
            ("T", "I001"): ("OBSERVED_NULL", "1", "0", "0.2"),
        }
        records = {}
        for key, (state, tested, active, nes) in states.items():
            records[key] = {
                "context_id": key[0], "component_id": key[1], "axis": key[1][0],
                "activity_state": state, "tested_mask": tested, "active_mask": active,
                "NES": nes, "representative_term_id": f"TERM_{key[1]}",
            }
        atlas = AtlasData(
            root=ROOT, atlas_version="SYNTHETIC", contexts=contexts, components=components,
            component_axis={"P001": "P", "M001": "M", "I001": "I"}, records=records,
            phenotype_anchors={"Q": [], "T": []}, reliability={"Q": [], "T": []},
            context_features={"Q": {"major_limitations": "synthetic"}, "T": {"major_limitations": "synthetic"}},
        )
        matrix = build_response_matrix(atlas)
        first = explain_pair(atlas, matrix, "Q", "T")
        second = explain_pair(atlas, matrix, "Q", "T")
        self.assertEqual(first, second)
        self.assertEqual(first["discordant_components"][0]["component_id"], "M001")


if __name__ == "__main__":
    unittest.main()
