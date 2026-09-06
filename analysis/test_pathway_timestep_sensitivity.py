import importlib.util
import pathlib
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("analyze_pathway_timestep_sensitivity.py")
SPEC = importlib.util.spec_from_file_location("analyze_pathway_timestep_sensitivity", MODULE_PATH)
sensitivity = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(sensitivity)


def track(identity, status, hours, latitude, longitude):
    return {"id": identity, "status": status, "integrated_hours": hours, "points": [{"latitude": latitude, "longitude": longitude}]}


class PathwayTimestepSensitivityTests(unittest.TestCase):
    def test_separates_endpoint_and_loss_timing_sensitivity(self):
        runs = {
            3: {"summary": {"released": 2, "completed": 1, "terminated": 1, "completion_fraction": .5}, "tracks": [track("a", "completed", 24, 0, 0), track("b", "lost", 3, 0, 0)]},
            6: {"summary": {"released": 2, "completed": 1, "terminated": 1, "completion_fraction": .5}, "tracks": [track("a", "completed", 24, 0, .01), track("b", "lost", 6, 0, 0)]},
            12: {"summary": {"released": 2, "completed": 1, "terminated": 1, "completion_fraction": .5}, "tracks": [track("a", "completed", 24, 0, .02), track("b", "lost", 12, 0, 0)]},
        }
        result = sensitivity.analyze(runs)
        self.assertEqual(1, result["common_completed_tracks"])
        self.assertEqual(9, result["maximum_loss_timing_range_hours"])
        self.assertGreater(result["cases"][-1]["common_completed_endpoint_separation_from_reference_km"]["maximum"], 2)

    def test_rejects_different_release_sets(self):
        with self.assertRaisesRegex(ValueError, "identical release identities"):
            sensitivity.analyze({3: {"tracks": [track("a", "completed", 1, 0, 0)]}, 6: {"tracks": [track("b", "completed", 1, 0, 0)]}})


if __name__ == "__main__":
    unittest.main()
