import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("synthesize_oras5_drake_temperature_classes.py")
SPEC = importlib.util.spec_from_file_location("synthesize_oras5_drake_temperature_classes", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class DrakeTemperatureClassTests(unittest.TestCase):
    def test_edges_are_half_open_and_exhaustive(self):
        expected = [0, 1, 2, 3, 4, 5]
        actual = [module.classify(value) for value in (-1, 0, 1, 2, 3, 5)]
        self.assertEqual(expected, actual)

    def test_partition_conserves_a_small_section(self):
        section = {
            "shape": [1, 3], "segment_width_m": [1, 1, 1], "layer_thickness_m": [1],
            "wet_fraction": [1, 1, 1], "normal_velocity_m_s": [1e6, -1e6, 2e6],
            "potential_temperature_degC": [-1, 1.5, 6], "constants": {"density_kg_m3": 1000, "heat_capacity_J_kg_K": 4000},
            "temperature_contract": "test",
        }
        transport = {"volume_transport": {"net_Sv": 2}, "reference_relative_heat_transport": [{"reference_temperature_degC": 0, "net_PW": .038}]}
        result = module.synthesize([section] * 4, [transport] * 4)
        self.assertTrue(all(abs(item["volume_residual_Sv"]) < 1e-12 for item in result["conservation_audit"]))
        self.assertTrue(all(abs(item["heat_0C_residual_PW"]) < 1e-12 for item in result["conservation_audit"]))


if __name__ == "__main__":
    unittest.main()
