import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("analyze_oras5_drake_control_box_sensitivity.py")
SPEC = importlib.util.spec_from_file_location("analyze_oras5_drake_control_box_sensitivity", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class DrakeControlBoxSensitivityTests(unittest.TestCase):
    def test_variants_change_one_dimension_at_a_time(self):
        variants = module.variants()
        self.assertEqual(8, len(variants))
        east = [bounds for _, family, bounds in variants if family == "eastward_extent"]
        north = [bounds for _, family, bounds in variants if family == "northward_extent"]
        self.assertEqual(1, len({item["north_v_y"] for item in east}))
        self.assertEqual(1, len({item["east_u_x"] for item in north}))
        self.assertEqual([61, 65, 69, 73], [item["t_x_stop_exclusive"] for item in east])
        self.assertEqual([75, 97, 119, 140], [item["t_y_stop_exclusive"] for item in north])


if __name__ == "__main__":
    unittest.main()
