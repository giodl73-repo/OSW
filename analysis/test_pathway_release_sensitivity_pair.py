import importlib.util
import json
import pathlib
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("synthesize_pathway_release_sensitivities.py")
SPEC = importlib.util.spec_from_file_location("synthesize_pathway_release_sensitivities", MODULE_PATH)
pairing = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(pairing)


def study(kind, groups):
    key = "release_time" if kind == "position" else "central_release_time"
    return {
        "schema": kind, "velocity_source": {"field_sha256": "same"},
        "groups": [{"base_id": identity, key: "2018-01-01T00:00:00Z", "release_index": index,
                    "central_status": "completed", "completed": completed,
                    "completed_endpoint_separation_from_central_km": None}
                   for identity, index, completed in groups],
    }


class PathwayReleaseSensitivityPairTests(unittest.TestCase):
    def test_completion_classes(self):
        self.assertEqual("full", pairing.completion_class(9, 9))
        self.assertEqual("mixed", pairing.completion_class(4, 9))
        self.assertEqual("lost", pairing.completion_class(0, 9))

    def test_keeps_position_and_time_separate(self):
        position = study("position", [("a", 1, 9), ("b", 2, 3)])
        time = study("time", [("a", 1, 5), ("b", 2, 0)])
        result = pairing.synthesize(position, time)
        self.assertEqual({"full/full": 1, "mixed/lost": 1}, result["summary"]["paired_pattern_counts"])
        self.assertEqual("mixed/lost", result["releases"][1]["paired_pattern"])


class HistoricalPairArtifactTests(unittest.TestCase):
    def test_declared_pair_counts_are_preserved(self):
        path = MODULE_PATH.parents[1] / "research/osw-m2-drake-release-sensitivity-pair-2018.json"
        if not path.exists():
            self.skipTest("generated pair artifact not present")
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual((40, 32, 2, 6), (
            data["summary"]["base_releases"], data["summary"]["full_under_both"],
            data["summary"]["lost_under_both"], data["summary"]["other_or_mixed"],
        ))


if __name__ == "__main__":
    unittest.main()
