import importlib.util
import pathlib
import sys
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("analyze_pathway_grid_sensitivity.py")
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("analyze_pathway_grid_sensitivity", MODULE_PATH)
sensitivity = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(sensitivity)


def run(status_a="completed", status_b="completed", longitude=0):
    tracks = [
        {"id": "a", "status": status_a, "points": [{"latitude": 0, "longitude": longitude}]},
        {"id": "b", "status": status_b, "points": [{"latitude": 0, "longitude": longitude}]},
    ]
    return {"tracks": tracks, "velocity_source": {}, "summary": {"released": 2}}


class PathwayGridSensitivityTests(unittest.TestCase):
    def test_preserves_status_disagreement_and_endpoint_scale(self):
        reference = run()
        comparison = run(status_b="lost", longitude=.01)
        result = sensitivity.analyze(reference, comparison, "native", "coarse")
        self.assertEqual(1, result["status_disagreement_count"])
        self.assertEqual(1, result["common_completed_tracks"])
        self.assertGreater(result["common_completed_endpoint_separation_km"]["maximum"], 1)

    def test_rejects_different_releases(self):
        reference = run(); comparison = run(); comparison["tracks"].pop()
        with self.assertRaisesRegex(ValueError, "identical release identities"):
            sensitivity.analyze(reference, comparison, "native", "coarse")


if __name__ == "__main__":
    unittest.main()
