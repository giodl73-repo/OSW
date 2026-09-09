import importlib.util
import pathlib
import sys
import unittest


ANALYSIS = pathlib.Path(__file__).parent
sys.path.insert(0, str(ANALYSIS))
MODULE_PATH = ANALYSIS / "analyze_motion_partition_sensitivity.py"
SPEC = importlib.util.spec_from_file_location("analyze_motion_partition_sensitivity", MODULE_PATH)
study = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(study)


class MotionPartitionSensitivityTests(unittest.TestCase):
    def test_directional_similarity(self):
        east = [(1.0, 0.0, 1.0)] * 4
        west = [(-1.0, 0.0, 1.0)] * 4
        self.assertAlmostEqual(1.0, study.directional_similarity(east, east))
        self.assertAlmostEqual(-1.0, study.directional_similarity(east, west))

    def test_partition_splits_when_threshold_tightens(self):
        vectors = {0: object(), 1: object(), 2: object()}
        edges = [(0, 1, .8), (1, 2, .4)]
        _, loose = study.partition(vectors, edges, .3)
        _, tight = study.partition(vectors, edges, .7)
        self.assertEqual([3], loose)
        self.assertEqual([2, 1], tight)


if __name__ == "__main__":
    unittest.main()
