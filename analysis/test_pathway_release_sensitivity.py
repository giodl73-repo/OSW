import importlib.util
import json
import math
import pathlib
import sys
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("analyze_pathway_release_sensitivity.py")
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("analyze_pathway_release_sensitivity", MODULE_PATH)
sensitivity = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(sensitivity)


class PathwayReleaseSensitivityTests(unittest.TestCase):
    def test_gate_basis_is_orthonormal(self):
        tangent, normal = sensitivity.gate_basis([(-56.5, 293), (-61.9, 299.3)])
        self.assertAlmostEqual(1, math.hypot(*tangent))
        self.assertAlmostEqual(1, math.hypot(*normal))
        self.assertAlmostEqual(0, tangent[0] * normal[0] + tangent[1] * normal[1])

    def test_fifteen_kilometre_across_offset_is_local(self):
        releases = [(-56.5, 293), (-61.9, 299.3)]
        tangent, normal = sensitivity.gate_basis(releases)
        shifted = sensitivity.offset_point(*releases[0], 0, 15, tangent, normal)
        distance = sensitivity.distance_km(
            {"latitude": releases[0][0], "longitude": releases[0][1]},
            {"latitude": shifted[0], "longitude": shifted[1]},
        )
        self.assertAlmostEqual(15, distance, delta=.1)


class HistoricalReleaseSensitivityArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((MODULE_PATH.parents[1] / "research/osw-m2-drake-release-sensitivity-2018.json").read_text(encoding="utf-8"))

    def test_declared_neighborhood_counts_are_preserved(self):
        summary = self.data["summary"]
        self.assertEqual(40, summary["base_releases"])
        self.assertEqual(360, summary["perturbed_trials"])
        self.assertEqual(321, summary["completed_trials"])
        self.assertEqual((33, 5, 2), (
            summary["fully_completed_neighborhoods"],
            summary["mixed_neighborhoods"],
            summary["fully_terminated_neighborhoods"],
        ))

    def test_every_neighborhood_has_nine_deterministic_trials(self):
        counts = {}
        for trial in self.data["trials"]:
            counts[trial["base_id"]] = counts.get(trial["base_id"], 0) + 1
        self.assertEqual(40, len(counts))
        self.assertEqual({9}, set(counts.values()))
        self.assertEqual("none", self.data["experiment"]["diffusion"])


if __name__ == "__main__":
    unittest.main()
