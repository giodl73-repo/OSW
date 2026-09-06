import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("analyze_geomar_agulhas_transport.py")
SPEC = importlib.util.spec_from_file_location("analyze_geomar_agulhas_transport", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)
ROOT = pathlib.Path(__file__).parents[1]


class GeomarAgulhasTransportTests(unittest.TestCase):
    def test_published_compact_artifacts_reproduce_reported_mean(self):
        data = ROOT / "atlas/data/geomar-agulhas"
        result = module.run(
            data / "Parcels_sections_32S.nc",
            data / "Parcels_trajectories_32S_postprocessing_transport_per_section.nc",
            data / "Parcels_trajectories_32S_examples.nc",
        )
        self.assertEqual(57, result["release_years"]["count"])
        self.assertAlmostEqual(9.8939648056, result["leakage"]["mean_sv"], places=9)
        self.assertAlmostEqual(0.4638587858, result["leakage"]["linear_trend_sv_per_decade"], places=9)
        self.assertEqual(1972, result["leakage"]["minimum_release_year"])
        self.assertEqual(1984, result["leakage"]["maximum_release_year"])
        self.assertAlmostEqual(40.0154760849, result["return_current_east_exit"]["mean_sv"], places=9)
        self.assertEqual(63, len(result["section_geometry"]))
        self.assertEqual(4, len(result["example_trajectories"]))
        self.assertEqual("CC BY 4.0", result["archive"]["license"])

    def test_section_geometry_contains_both_leakage_exits(self):
        data = ROOT / "atlas/data/geomar-agulhas"
        result = module.run(data / "Parcels_sections_32S.nc", data / "Parcels_trajectories_32S_postprocessing_transport_per_section.nc", data / "Parcels_trajectories_32S_examples.nc")
        names = {point["section"] for point in result["section_geometry"]}
        self.assertIn("west", names)
        self.assertIn("northwest", names)


if __name__ == "__main__":
    unittest.main()
