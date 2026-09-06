import importlib.util
import pathlib
import unittest

import numpy as np


PATH = pathlib.Path(__file__).with_name("fetch_oras5_drake_t_metrics.py")
SPEC = importlib.util.spec_from_file_location("fetch_oras5_drake_t_metrics", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class DrakeTMetricsTests(unittest.TestCase):
    def test_validates_positive_native_area(self):
        result = module.validate_arrays({"e1t": np.array([[2, 3]]), "e2t": np.array([[4, 5]])}, (1, 2))
        self.assertEqual(8, result["minimum_m2"])
        self.assertEqual(15, result["maximum_m2"])

    def test_rejects_shape_or_nonpositive_metric(self):
        with self.assertRaisesRegex(ValueError, "shape"):
            module.validate_arrays({"e1t": np.ones((1, 1)), "e2t": np.ones((1, 1))}, (2, 1))
        with self.assertRaisesRegex(ValueError, "positive"):
            module.validate_arrays({"e1t": np.array([[0]]), "e2t": np.ones((1, 1))}, (1, 1))


if __name__ == "__main__":
    unittest.main()
