import importlib.util
import json
import pathlib
import sys
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("analyze_pathway_release_time_sensitivity.py")
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("analyze_pathway_release_time_sensitivity", MODULE_PATH)
sensitivity = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(sensitivity)


class PathwayReleaseTimeSensitivityTests(unittest.TestCase):
    def test_iso_time_preserves_utc_z(self):
        value = sensitivity.parse_time("2018-01-01T00:00:00Z")
        self.assertEqual("2018-01-01T00:00:00Z", sensitivity.iso_time(value))

    def test_default_offsets_are_symmetric_and_include_reference(self):
        self.assertEqual(0, sum(sensitivity.DEFAULT_OFFSETS_DAYS))
        self.assertIn(0, sensitivity.DEFAULT_OFFSETS_DAYS)
        self.assertEqual(10, max(sensitivity.DEFAULT_OFFSETS_DAYS) - min(sensitivity.DEFAULT_OFFSETS_DAYS))


class HistoricalReleaseTimeSensitivityArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((MODULE_PATH.parents[1] / "research/osw-m2-drake-release-time-sensitivity-2018.json").read_text(encoding="utf-8"))

    def test_declared_time_window_counts_are_preserved(self):
        summary = self.data["summary"]
        self.assertEqual((40, 200, 176), (
            summary["base_releases"], summary["shifted_trials"], summary["completed_trials"],
        ))
        self.assertEqual((34, 2, 4), (
            summary["fully_completed_windows"], summary["mixed_windows"], summary["fully_terminated_windows"],
        ))

    def test_every_window_has_five_deterministic_trials(self):
        counts = {}
        for trial in self.data["trials"]:
            counts[trial["base_id"]] = counts.get(trial["base_id"], 0) + 1
        self.assertEqual({5}, set(counts.values()))
        self.assertEqual("none", self.data["experiment"]["diffusion"])


if __name__ == "__main__":
    unittest.main()
