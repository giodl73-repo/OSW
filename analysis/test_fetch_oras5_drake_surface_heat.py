import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("fetch_oras5_drake_surface_heat.py")
SPEC = importlib.util.spec_from_file_location("fetch_oras5_drake_surface_heat", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class DrakeSurfaceHeatFetchTests(unittest.TestCase):
    def test_native_window_matches_control_box_in_global_indices(self):
        receipt = {"native_index_box": {"y_start": 88, "x_start": 816}}
        self.assertEqual({"y_start": 142, "y_stop_exclusive": 228, "x_start": 873, "x_stop_exclusive": 889}, module.native_window(receipt))

    def test_source_is_native_orca025_t_grid(self):
        url = module.source_url("201801")
        self.assertIn("/ORCA025/sohefldo/opa0/", url)
        self.assertTrue(url.endswith("sohefldo_ORAS5_1m_201801_grid_T_02.nc"))

    def test_has_twelve_months(self):
        self.assertEqual("201801", module.MONTHS[0])
        self.assertEqual("201812", module.MONTHS[-1])
        self.assertEqual(12, len(module.MONTHS))


if __name__ == "__main__":
    unittest.main()
