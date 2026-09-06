import importlib.util
import pathlib
import unittest

import numpy as np


PATH = pathlib.Path(__file__).with_name("derive_oras5_arctic_gate_readiness.py")
SPEC = importlib.util.spec_from_file_location("derive_oras5_arctic_gate_readiness", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)
ROOT = pathlib.Path(__file__).parents[1]


class ArcticGateReadinessTests(unittest.TestCase):
    def test_wet_runs(self):
        self.assertEqual([(1, 3), (4, 7)], module.wet_runs([0, 1, 1, 0, 1, 1, 1, 0]))

    def test_pinned_mesh_exposes_asymmetric_readiness(self):
        result = module.derive_file(ROOT / "atlas/data/oras5-arctic-entrances-mesh.nc")
        self.assertEqual(60, result["fram"]["face_count"])
        self.assertTrue(result["fram"]["land_bounded_at_surface"])
        self.assertEqual("V", result["fram"]["native_face"])
        barents = result["barents_single_column_test"]
        self.assertFalse(barents["land_bounded_at_surface"])
        self.assertGreater(barents["longitude_drift_deg"], 10.0)
        self.assertEqual("single_native_U_column_rejected", barents["status"])
        bear = result["bear_island_representation"]
        self.assertTrue(bear["nearest_t_cell_is_wet"])
        self.assertLess(bear["nearest_wet_t_cell"]["approximate_distance_km"], 10.0)
        self.assertGreater(bear["nearest_dry_t_cell"]["approximate_distance_km"], 200.0)
        self.assertIn("observational_comparison", result["barents_contract_fork"])
        self.assertIn("model_budget_closure", result["barents_contract_fork"])


if __name__ == "__main__":
    unittest.main()
