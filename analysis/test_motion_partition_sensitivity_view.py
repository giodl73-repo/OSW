import importlib.util
import json
import pathlib
import sys
import unittest


ANALYSIS = pathlib.Path(__file__).parent
sys.path.insert(0, str(ANALYSIS))
MODULE_PATH = ANALYSIS / "build_motion_partition_sensitivity_view.py"
SPEC = importlib.util.spec_from_file_location("build_motion_partition_sensitivity_view", MODULE_PATH)
view = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(view)


class MotionPartitionSensitivityViewTests(unittest.TestCase):
    def test_committed_sensitivity_artifacts(self):
        root = ANALYSIS.parent
        payload = json.loads((root / "research" / "osw-motion-partition-sensitivity-2018.json").read_text(encoding="utf-8"))
        svg = (root / "figures" / "osw-motion-partition-sensitivity-2018.svg").read_text(encoding="utf-8")
        self.assertEqual(759, payload["supported_cells"])
        self.assertEqual(10, len(payload["results"]))
        self.assertIn('data-motion-level="partition-sensitivity"', svg)
        self.assertIn("DOES THE WATER CHOOSE A NUMBER?", svg)
        page = (root / "projections" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-motion-view="partition"', page)


if __name__ == "__main__":
    unittest.main()
