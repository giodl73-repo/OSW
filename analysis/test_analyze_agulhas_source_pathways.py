import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("analyze_agulhas_source_pathways.py")
SPEC = importlib.util.spec_from_file_location("analyze_agulhas_source_pathways", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class AgulhasSourcePathwayTests(unittest.TestCase):
    def test_thresholds_are_geographic_and_can_overlap(self):
        track = {"status": "completed", "points": [
            {"latitude": -36, "longitude": 14},
            {"latitude": -38, "longitude": 36},
        ]}
        self.assertEqual("both_thresholds", module.classify(track, 15, 35))

    def test_termination_does_not_override_observed_crossing(self):
        track = {"status": "terminated_invalid_wet_stencil_or_domain", "points": [{"latitude": -35, "longitude": 14}]}
        self.assertEqual("cape_basin", module.classify(track, 15, 35))

    def test_shipped_field_preserves_baseline_census(self):
        root = pathlib.Path(__file__).parents[1]
        result = module.run(root / "atlas/data/oscar-timeseries-agulhas-native-2018.js")
        self.assertEqual(108, result["release_contract"]["count"])
        self.assertEqual({
            "cape_basin": 14,
            "return_corridor": 24,
            "both_thresholds": 0,
            "unresolved": 62,
            "terminated": 8,
        }, result["baseline_fates"])
        self.assertEqual(9, len(result["gate_sensitivity"]))


if __name__ == "__main__":
    unittest.main()
