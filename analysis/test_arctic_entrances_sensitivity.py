import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("analyze_arctic_entrances_sensitivity.py")
SPEC = importlib.util.spec_from_file_location("analyze_arctic_entrances_sensitivity", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class ArcticEntrancesSensitivityTests(unittest.TestCase):
    def test_declared_bakeoff_sizes(self):
        self.assertEqual(30, len(module.FRAM_LATITUDES) * len(module.FRAM_EAST_STARTS))
        self.assertEqual(18, len(module.FRAM_LATITUDES) * len(module.FRAM_WEST_ENDS))
        self.assertEqual(11, len(module.BARENTS_LONGITUDES))

    def test_direction_summary_counts_strict_sign(self):
        cases = [{"annual_mean_normal_velocity_m_s": value} for value in (-1, 0, 2)]
        self.assertEqual(1, module.summarize_cases(cases, True)["direction_support_count"])
        self.assertEqual(1, module.summarize_cases(cases, False)["direction_support_count"])


if __name__ == "__main__":
    unittest.main()
