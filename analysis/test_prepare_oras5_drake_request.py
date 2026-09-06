import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("prepare_oras5_drake_request.py")
SPEC = importlib.util.spec_from_file_location("prepare_oras5_drake_request", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class Oras5RequestTests(unittest.TestCase):
    def test_default_is_operational_all_level_four_season_manifest(self):
        result = module.build_manifest()
        self.assertEqual("download_not_executed", result["status"])
        self.assertEqual(["operational"], result["request"]["product_type"])
        self.assertEqual(["all_levels"], result["request"]["vertical_resolution"])
        self.assertEqual(["02", "05", "08", "11"], result["request"]["month"])
        self.assertIn("potential_temperature", result["request"]["variable"])
        self.assertIn("section_geometry", result["pilot"])

    def test_rejects_consolidated_year_under_operational_contract(self):
        with self.assertRaisesRegex(ValueError, "year >= 2015"):
            module.build_manifest(2014)

    def test_rejects_duplicate_month(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            module.build_manifest(2018, ("02", "2"))


if __name__ == "__main__":
    unittest.main()
