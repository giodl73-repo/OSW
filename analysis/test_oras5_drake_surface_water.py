import importlib.util
import pathlib
import unittest

import numpy as np


PATH = pathlib.Path(__file__).with_name("analyze_oras5_drake_surface_water.py")
SPEC = importlib.util.spec_from_file_location("analyze_oras5_drake_surface_water", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class DrakeSurfaceWaterTests(unittest.TestCase):
    def test_positive_upward_mass_flux_is_positive_outward_volume(self):
        flux = np.array([[[1026.0, -513.0]]])
        area = np.array([[1e6, 2e6]])
        result = module.integrate_water_flux_sv(flux, area)
        self.assertAlmostEqual(0.0, result[0])

    def test_negative_surface_flux_can_cancel_outward_lateral_volume(self):
        flux = np.array([[[-1026.0]]])
        area = np.array([[1e6]])
        self.assertAlmostEqual(-1.0, module.integrate_water_flux_sv(flux, area)[0])

    def test_rejects_invalid_density_and_shapes(self):
        with self.assertRaises(ValueError):
            module.integrate_water_flux_sv(np.ones((1, 1, 1)), np.ones((1, 1)), 0)
        with self.assertRaises(ValueError):
            module.integrate_water_flux_sv(np.ones((1, 2, 2)), np.ones((3, 2)))


if __name__ == "__main__":
    unittest.main()
