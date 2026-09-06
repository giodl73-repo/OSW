import importlib.util
import pathlib
import sys
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("build_drake_corridor_passport_view.py")
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("build_drake_corridor_passport_view", MODULE_PATH)
view = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(view)


class DrakeCorridorPassportViewTests(unittest.TestCase):
    def test_matrix_contains_two_bars_per_release(self):
        releases = []
        for row in range(4):
            for index in range(1, 11):
                releases.append({
                    "release_time": f"2018-0{row + 1}-01T00:00:00Z", "release_index": index,
                    "position": {"class": "full", "completed": 9, "total": 9},
                    "time": {"class": "full", "completed": 5, "total": 5},
                })
        svg = view.passport_matrix(releases)
        self.assertEqual(80, svg.count("<rect"))
        self.assertEqual(40, svg.count(">9/9</text>"))
        self.assertEqual(40, svg.count(">5/5</text>"))


if __name__ == "__main__":
    unittest.main()
