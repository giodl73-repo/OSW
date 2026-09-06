import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("simulate_arctic_entrance_pathways.py")
SPEC = importlib.util.spec_from_file_location("simulate_arctic_entrance_pathways", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class ArcticEntrancePathwayTests(unittest.TestCase):
    def test_release_groups_preserve_opposing_fram_lanes(self):
        self.assertEqual({"fram_west_export", "fram_east_inflow", "barents_inflow"}, set(module.RELEASE_GROUPS))
        self.assertEqual("southward", module.RELEASE_GROUPS["fram_west_export"]["positive_fate"])
        self.assertEqual("northward", module.RELEASE_GROUPS["fram_east_inflow"]["positive_fate"])
        self.assertEqual(20, module.RELEASE_GROUPS["fram_east_inflow"]["duration_days"])
        self.assertEqual(30, module.RELEASE_GROUPS["barents_inflow"]["duration_days"])

    def test_fate_uses_declared_direction_only_after_completion(self):
        completed = {"status": "completed", "points": [{"latitude": 79, "longitude": 366}]}
        self.assertEqual("northward", module.fate("fram_east_inflow", 78, 365, completed))
        terminated = {"status": "terminated_invalid_wet_stencil_or_domain", "points": [{"latitude": 79, "longitude": 366}]}
        self.assertEqual("terminated", module.fate("fram_east_inflow", 78, 365, terminated))


if __name__ == "__main__":
    unittest.main()
