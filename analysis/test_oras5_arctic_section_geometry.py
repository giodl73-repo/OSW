import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("audit_oras5_arctic_section_geometry.py")
SPEC = importlib.util.spec_from_file_location("audit_oras5_arctic_section_geometry", PATH)
module = importlib.util.module_from_spec(SPEC); assert SPEC.loader; SPEC.loader.exec_module(module)
ROOT = pathlib.Path(__file__).parents[1]


class ArcticSectionGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = module.run(
            ROOT / "atlas/data/oras5-arctic-entrances-mesh.nc",
            ROOT / "research/osw-m3-oras5-arctic-gate-readiness.json",
            ROOT / "research/osw-m3-oras5-barents-section-bakeoff.json",
        )

    def test_all_three_sections_pass_full_depth_internal_geometry(self):
        self.assertTrue(self.result["all_sections_pass"])
        self.assertEqual(3, len(self.result["sections"]))
        for section in self.result["sections"]:
            self.assertEqual(0, section["checks"]["mask_mismatch_count"])
            self.assertTrue(section["checks"]["depth_bins_reproduce_total"])

    def test_surface_face_contracts_are_preserved(self):
        by_name = {section["name"]: section for section in self.result["sections"]}
        self.assertEqual(60, by_name["Fram Strait"]["horizontal_face_count"])
        self.assertEqual(43, by_name["Fugloya-Bear observational proxy"]["horizontal_face_count"])
        self.assertEqual(73, by_name["Norway-Svalbard model closure"]["horizontal_face_count"])
        self.assertFalse(by_name["Fugloya-Bear observational proxy"]["land_bounded_at_surface"])

    def test_no_partial_cell_fallback_was_needed(self):
        self.assertEqual(0, self.result["reconstruction"]["fallback_bottom_cell_count"])


if __name__ == "__main__":
    unittest.main()
