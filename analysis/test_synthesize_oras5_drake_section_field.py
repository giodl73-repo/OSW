import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("synthesize_oras5_drake_section_field.py")
SPEC = importlib.util.spec_from_file_location("synthesize_oras5_drake_section_field", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


def payload(temperature, velocity):
    return {
        "shape": [1, 2], "segment_width_m": [1, 1], "layer_thickness_m": [10],
        "cell_thickness_m": [10, None], "wet_fraction": [1, 0],
        "potential_temperature_degC": [temperature, None], "normal_velocity_m_s": [velocity, None],
        "constants": {"density_kg_m3": 1000, "heat_capacity_J_kg_K": 4000},
        "section": {"latitude_deg": [-60, -59], "longitude_deg": [-67, -67]},
        "temperature_contract": "test T", "normal_velocity_contract": "test U",
    }


class DrakeSectionFieldTests(unittest.TestCase):
    def test_averages_only_wet_native_cells(self):
        result = module.synthesize([payload(t, u) for t, u in ((0, 1), (2, 3), (4, 5), (6, 7))])
        self.assertEqual([3, None], result["mean_potential_temperature_degC"])
        self.assertEqual([4, None], result["mean_normal_velocity_m_s"])
        self.assertAlmostEqual(4e-05, result["mean_cell_volume_transport_Sv"][0])
        self.assertIsNone(result["mean_cell_volume_transport_Sv"][1])
        self.assertAlmostEqual(6.8e-7, result["mean_cell_heat_transport_PW_at_0C"][0])
        self.assertEqual(10, result["maximum_nominal_model_depth_m"])

    def test_rejects_mismatched_geometry(self):
        items = [payload(1, 1) for _ in range(4)]
        items[-1]["wet_fraction"] = [0, 0]
        with self.assertRaisesRegex(ValueError, "wet_fraction"):
            module.synthesize(items)


if __name__ == "__main__":
    unittest.main()
