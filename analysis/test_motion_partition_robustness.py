import importlib.util
import pathlib
import sys
import unittest


ANALYSIS = pathlib.Path(__file__).parent
sys.path.insert(0, str(ANALYSIS))
MODULE_PATH = ANALYSIS / "analyze_motion_partition_robustness.py"
SPEC = importlib.util.spec_from_file_location("analyze_motion_partition_robustness", MODULE_PATH)
study = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(study)


class MotionPartitionRobustnessTests(unittest.TestCase):
    def test_configuration_contract(self):
        codes = [item[0] for item in study.CONFIGURATIONS]
        self.assertEqual(6, len(codes))
        self.assertEqual(len(codes), len(set(codes)))
        self.assertIn("8N_ALL", codes)
        self.assertIn("4N_NO_DJF", codes)


if __name__ == "__main__":
    unittest.main()
