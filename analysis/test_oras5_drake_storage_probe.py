import importlib.util
import pathlib
import unittest

import numpy as np


PATH = pathlib.Path(__file__).with_name("analyze_oras5_drake_storage_probe.py")
SPEC = importlib.util.spec_from_file_location("analyze_oras5_drake_storage_probe", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class DrakeStorageProbeTests(unittest.TestCase):
    def test_heat_content_reference_change_is_volume_identity(self):
        temperature = np.array([1.0, 3.0])
        volume = np.array([2.0, 4.0])
        h0 = module.heat_content(temperature, volume, 0, rho=1000, cp=4000)
        h5 = module.heat_content(temperature, volume, 5, rho=1000, cp=4000)
        self.assertEqual(-1000 * 4000 * volume.sum() * 5, h5 - h0)

    def test_storage_tendency_is_reference_invariant_at_fixed_volume(self):
        volume = np.array([2.0, 4.0])
        start = np.array([1.0, 3.0])
        end = np.array([2.0, 2.0])
        differences = []
        for reference in module.REFERENCES:
            differences.append(module.heat_content(end, volume, reference) - module.heat_content(start, volume, reference))
        self.assertTrue(all(abs(value - differences[0]) < 1e-6 for value in differences))


if __name__ == "__main__":
    unittest.main()
