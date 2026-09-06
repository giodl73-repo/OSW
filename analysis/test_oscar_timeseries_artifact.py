import hashlib
import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).parents[1]


def load_assignment(path: pathlib.Path, variable: str) -> dict:
    text = path.read_text(encoding="utf-8")
    prefix = f"window.{variable}="
    payload = text[text.index(prefix) + len(prefix):].rstrip().removesuffix(";")
    return json.loads(payload)


class OscarTimeseriesArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_assignment(ROOT / "atlas/data/oscar-timeseries-2018.js", "OSW_OSCAR_TIMESERIES")
        cls.drake = load_assignment(ROOT / "atlas/data/oscar-timeseries-drake-2018.js", "OSW_OSCAR_TIMESERIES")
        cls.drake_native = load_assignment(ROOT / "atlas/data/oscar-timeseries-drake-native-2018.js", "OSW_OSCAR_TIMESERIES")
        cls.seasons = load_assignment(ROOT / "atlas/data/oscar-seasons-2018.js", "OSW_OSCAR_SEASONS")

    def test_receipt_matches_seasonal_source(self):
        self.assertEqual(self.seasons["source_sha256"], self.data["source_sha256"])
        self.assertEqual([71, 25, 54], self.data["shape"])
        self.assertEqual(71, len(self.data["frames"]))

    def test_field_hash_and_frame_shapes(self):
        encoded = json.dumps(self.data["frames"], ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.assertEqual(self.data["field_sha256"], hashlib.sha256(encoded).hexdigest())
        cells = self.data["shape"][1] * self.data["shape"][2]
        for frame in self.data["frames"]:
            self.assertEqual(cells, len(frame["u_mm_s"]))
            self.assertEqual(cells, len(frame["v_mm_s"]))
            joint = sum(u is not None and v is not None for u, v in zip(frame["u_mm_s"], frame["v_mm_s"]))
            self.assertEqual(frame["valid_cells"], joint)

    def test_frame_times_equal_the_four_season_inputs(self):
        expected = sorted(
            time
            for season in self.seasons["season_order"]
            for time in self.seasons["seasons"][season]["sample_times"]
        )
        self.assertEqual(expected, [frame["time"] for frame in self.data["frames"]])

    def test_drake_substrate_is_finer_and_receipted(self):
        self.assertEqual([71, 38, 61], self.drake["shape"])
        self.assertEqual(2, self.drake["display_stride"])
        self.assertEqual({"north": -45.0, "south": -69.66666666666667, "west": 280.0, "east": 320.0}, self.drake["sampled_extent"])
        encoded = json.dumps(self.drake["frames"], ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.assertEqual(self.drake["field_sha256"], hashlib.sha256(encoded).hexdigest())
        self.assertEqual(
            [frame["time"] for frame in self.data["frames"]],
            [frame["time"] for frame in self.drake["frames"]],
        )

    def test_native_drake_substrate_preserves_dates_and_field_hash(self):
        self.assertEqual([71, 76, 121], self.drake_native["shape"])
        self.assertEqual(1, self.drake_native["display_stride"])
        encoded = json.dumps(self.drake_native["frames"], ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.assertEqual(self.drake_native["field_sha256"], hashlib.sha256(encoded).hexdigest())
        self.assertEqual(
            [frame["time"] for frame in self.data["frames"]],
            [frame["time"] for frame in self.drake_native["frames"]],
        )


if __name__ == "__main__":
    unittest.main()
