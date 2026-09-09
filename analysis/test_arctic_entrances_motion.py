import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("analyze_arctic_entrances_motion.py")
SPEC = importlib.util.spec_from_file_location("analyze_arctic_entrances_motion", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class ArcticEntrancesMotionTests(unittest.TestCase):
    def test_gate_indices_select_correct_orientation(self):
        payload = {"shape": [1, 3, 4], "latitude_values": [80, 79, 78], "longitude_values": [20, 21, 22, 23]}
        zonal = {"orientation": "zonal", "target": 79.2, "along_min": 21, "along_max": 23}
        indices, fixed = module.gate_indices(payload, zonal)
        self.assertEqual([5, 6, 7], indices)
        self.assertEqual(79, fixed)
        meridional = {"orientation": "meridional", "target": 21.2, "along_min": 78, "along_max": 80}
        indices, fixed = module.gate_indices(payload, meridional)
        self.assertEqual([1, 5, 9], indices)
        self.assertEqual(21, fixed)

    def test_seasons_cover_all_months_once(self):
        months = [month for values in module.SEASON_MONTHS.values() for month in values]
        self.assertEqual(list(range(1, 13)), sorted(months))


if __name__ == "__main__":
    unittest.main()
