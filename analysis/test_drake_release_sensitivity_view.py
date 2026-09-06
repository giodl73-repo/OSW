import importlib.util
import pathlib
import sys
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("build_drake_release_sensitivity_view.py")
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("build_drake_release_sensitivity_view", MODULE_PATH)
view = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(view)


class DrakeReleaseSensitivityViewTests(unittest.TestCase):
    def test_matrix_keeps_all_four_dates_and_ten_positions(self):
        groups = [
            {"release_time": f"2018-0{row + 1}-01T00:00:00Z", "release_index": column, "completed": 9}
            for row in range(4) for column in range(1, 11)
        ]
        svg = view.matrix(groups)
        self.assertEqual(40, svg.count("<rect"))
        self.assertIn("2018-04-01", svg)
        self.assertIn(">10</text>", svg)


if __name__ == "__main__":
    unittest.main()
