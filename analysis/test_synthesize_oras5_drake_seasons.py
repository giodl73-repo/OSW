import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("synthesize_oras5_drake_seasons.py")
SPEC = importlib.util.spec_from_file_location("synthesize_oras5_drake_seasons", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


def payload(month, net):
    return {
        "section": {"month": month, "local_x": 1, "local_y_start": 2, "local_y_stop_exclusive": 4, "segment_count": 2, "positive_normal": "east"},
        "geometry_contract": "same",
        "volume_transport": {"positive_Sv": net + 10, "negative_Sv": -10, "net_Sv": net},
        "transport_weighted_temperature_degC": {"positive_branch": 2, "negative_branch": 1, "net": 3},
        "reference_relative_heat_transport": [
            {"reference_temperature_degC": -1.9, "net_PW": net / 50},
            {"reference_temperature_degC": 0.0, "net_PW": net / 100},
            {"reference_temperature_degC": 5.0, "net_PW": -net / 100},
        ],
        "input_sha256": month,
    }


class DrakeSeasonalSynthesisTests(unittest.TestCase):
    def test_preserves_rows_and_calculates_ranges(self):
        payloads = [payload(month, value) for month, value in zip(module.SEASONS, (120, 122, 124, 126))]
        result = module.summarize(payloads)
        self.assertEqual(123, result["summary"]["net_volume_Sv"]["mean"])
        self.assertEqual(6, result["summary"]["net_volume_Sv"]["range"])
        self.assertEqual(4, len(result["rows"]))
        self.assertIn("0.0", result["summary"]["net_heat_PW_by_reference_degC"])

    def test_rejects_gate_change(self):
        payloads = [payload(month, 120) for month in module.SEASONS]
        payloads[-1]["section"]["local_x"] = 2
        with self.assertRaisesRegex(ValueError, "gate contract"):
            module.summarize(payloads)

    def test_requires_exact_season_order(self):
        payloads = [payload(month, 120) for month in reversed(module.SEASONS)]
        with self.assertRaisesRegex(ValueError, "ordered months"):
            module.summarize(payloads)


if __name__ == "__main__":
    unittest.main()
