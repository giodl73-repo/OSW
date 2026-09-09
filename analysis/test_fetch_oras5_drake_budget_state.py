import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("fetch_oras5_drake_budget_state.py")
SPEC = importlib.util.spec_from_file_location("fetch_oras5_drake_budget_state", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class DrakeBudgetStateTests(unittest.TestCase):
    def test_windows_cover_adjacent_temperature_and_four_boundaries(self):
        t = module.WINDOWS["votemper"]
        u = module.WINDOWS["vozocrtx"]
        v = module.WINDOWS["vomecrty"]
        self.assertEqual((88, 18), (t["y_stop_exclusive"] - t["y_start"], t["x_stop_exclusive"] - t["x_start"]))
        self.assertEqual((86, 17), (u["y_stop_exclusive"] - u["y_start"], u["x_stop_exclusive"] - u["x_start"]))
        self.assertEqual((87, 16), (v["y_stop_exclusive"] - v["y_start"], v["x_stop_exclusive"] - v["x_start"]))

    def test_global_window_adds_mesh_origin(self):
        result = module.global_window({"y_start": 2, "y_stop_exclusive": 4, "x_start": 3, "x_stop_exclusive": 8}, {"y_start": 100, "x_start": 200})
        self.assertEqual({"y_start": 102, "y_stop_exclusive": 104, "x_start": 203, "x_stop_exclusive": 208}, result)


if __name__ == "__main__":
    unittest.main()
