import importlib.util
import pathlib
import unittest

import numpy as np


PATH = pathlib.Path(__file__).with_name("analyze_oras5_drake_control_box.py")
SPEC = importlib.util.spec_from_file_location("analyze_oras5_drake_control_box", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class DrakeControlBoxTests(unittest.TestCase):
    def test_boundary_transport_obeys_outward_sign_and_reference_identity(self):
        velocity = np.array([[2.0, -1.0]])
        temperature = np.array([[3.0, 1.0]])
        thickness = np.array([[5.0, 5.0]])
        width = np.array([10.0, 10.0])
        result = module.boundary_transport(velocity, temperature, thickness, width, np.ones((1, 2)), -1, rho=1000, cp=4000)
        self.assertAlmostEqual(-5e-5, result["volume_Sv"])
        heat0 = next(item["net_PW"] for item in result["heat_transport_PW"] if item["reference_temperature_degC"] == 0)
        heat5 = next(item["net_PW"] for item in result["heat_transport_PW"] if item["reference_temperature_degC"] == 5)
        expected_change = -1000 * 4000 * (-50) * 5 / 1e15
        self.assertAlmostEqual(expected_change, heat5 - heat0)

    def test_rejects_wrong_width_shape(self):
        with self.assertRaisesRegex(ValueError, "width"):
            module.boundary_transport(np.ones((1, 2)), np.ones((1, 2)), np.ones((1, 2)), np.ones(1), np.ones((1, 2)), 1)

    def test_summary_keeps_boundary_and_reference_dimensions(self):
        months = []
        for month in module.MONTHS:
            boundaries = []
            for name, volume in (("west", -10), ("east", 6), ("south", 1), ("north", 3)):
                boundaries.append({"name": name, "volume_Sv": volume, "heat_transport_PW": [{"reference_temperature_degC": ref, "net_PW": volume * .01} for ref in module.REFERENCES]})
            months.append({"boundaries": boundaries, "net_outward_volume_Sv": 0, "net_outward_heat_PW": [{"reference_temperature_degC": ref, "net_boundary_PW": 0} for ref in module.REFERENCES]})
        result = module.summarize(months)
        self.assertEqual(4, len(result["boundaries"]))
        self.assertEqual(3, len(result["net_outward_heat_PW"]))
        self.assertEqual(0, result["net_outward_volume_Sv"]["mean"])


if __name__ == "__main__":
    unittest.main()
