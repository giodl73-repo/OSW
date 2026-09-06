import importlib.util
import pathlib
import unittest

import numpy as np


PATH = pathlib.Path(__file__).with_name("analyze_oras5_drake_surface_budget.py")
SPEC = importlib.util.spec_from_file_location("analyze_oras5_drake_surface_budget", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class DrakeSurfaceBudgetTests(unittest.TestCase):
    def test_positive_downward_flux_is_positive_ocean_input(self):
        flux = np.array([[[10.0, 20.0]]])
        area = np.array([[2e12, 1e12]])
        result = module.integrate_surface_flux(flux, area)
        self.assertAlmostEqual(0.04, result[0])

    def test_shapes_must_align(self):
        with self.assertRaises(ValueError):
            module.integrate_surface_flux(np.ones((12, 2, 2)), np.ones((3, 2)))


if __name__ == "__main__":
    unittest.main()
