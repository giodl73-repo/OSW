import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("analyze_oras5_drake_gate_sensitivity.py")
SPEC = importlib.util.spec_from_file_location("analyze_oras5_drake_gate_sensitivity", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class DrakeMethodSensitivityTests(unittest.TestCase):
    def test_summarizes_gate_and_collocation_dimensions_separately(self):
        gate_records = []
        for x, lon in ((1, -68), (2, -67)):
            for month, value in zip(module.MONTHS, (120, 121, 122, 123)):
                gate_records.append({"x": x, "mean_longitude_deg": lon, "south_deg": -64, "north_deg": -56, "month": month, "net_volume_Sv": value + x, "net_heat_0C_PW": 1.2})
        collocation_records = []
        for index, scheme in enumerate(module.COLLOCATIONS):
            for month in module.MONTHS:
                collocation_records.append({"collocation": scheme, "month": month, "net_volume_Sv": 124, "net_heat_0C_PW": 1.2 + index * .01, "net_temperature_degC": 2.5})
        result = module.summarize(gate_records, collocation_records, 2)
        self.assertEqual(2, len(result["gate_summary"]))
        self.assertEqual(4, len(result["collocation_summary"]))
        self.assertAlmostEqual(.03, result["collocation_summary"][-1]["heat_difference_from_mean_collocation_PW"]["mean"])

    def test_volume_is_invariant_to_temperature_collocation(self):
        records = []
        for scheme in module.COLLOCATIONS:
            for month, volume in zip(module.MONTHS, (120, 121, 122, 123)):
                records.append({"collocation": scheme, "month": month, "net_volume_Sv": volume, "net_heat_0C_PW": 1.2, "net_temperature_degC": 2.5})
        gate_records = [
            {"x": 1, "mean_longitude_deg": -67, "south_deg": -64, "north_deg": -56, "month": month, "net_volume_Sv": volume, "net_heat_0C_PW": 1.2}
            for month, volume in zip(module.MONTHS, (120, 121, 122, 123))
        ]
        result = module.summarize(gate_records, records, 1)
        self.assertEqual(1, len({item["net_volume_Sv"]["mean"] for item in result["collocation_summary"]}))


if __name__ == "__main__":
    unittest.main()
