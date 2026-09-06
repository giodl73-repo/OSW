import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("fetch_oras5_drake_surface_water.py")
SPEC = importlib.util.spec_from_file_location("fetch_oras5_drake_surface_water", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class DrakeSurfaceWaterFetchTests(unittest.TestCase):
    def test_native_window_matches_control_box(self):
        receipt = {"native_index_box": {"y_start": 88, "x_start": 816}}
        self.assertEqual({"y_start": 142, "y_stop_exclusive": 228, "x_start": 873, "x_stop_exclusive": 889}, module.native_window(receipt))

    def test_source_is_native_orca025_t_grid(self):
        url = module.source_url("201812")
        self.assertIn("/ORCA025/sowaflup/opa0/", url)
        self.assertTrue(url.endswith("sowaflup_ORAS5_1m_201812_grid_T_02.nc"))


if __name__ == "__main__":
    unittest.main()
