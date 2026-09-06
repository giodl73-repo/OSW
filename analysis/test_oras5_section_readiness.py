import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("inspect_oras5_section_readiness.py")
SPEC = importlib.util.spec_from_file_location("inspect_oras5_section_readiness", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class Oras5ReadinessTests(unittest.TestCase):
    def test_velocity_and_temperature_alone_fail_closed(self):
        result = module.assess_names({"potential_temperature", "zonal_velocity", "meridional_velocity", "time"})
        self.assertEqual("blocked_missing_native_face_evidence", result["status"])
        self.assertIn("u_face_width", result["missing"])
        self.assertIn("v_wet_mask", result["missing"])

    def test_complete_native_face_inventory_is_ready_for_extraction(self):
        names = {aliases[0] for aliases in module.ALIASES.values()}
        result = module.assess_names(names)
        self.assertEqual("ready_for_section_extraction", result["status"])
        self.assertEqual([], result["missing"])

    def test_rotated_velocity_is_reported_but_not_accepted(self):
        result = module.assess_names({"rotated_zonal_velocity", "rotated_meridional_velocity"})
        self.assertEqual(2, len(result["diagnostic_velocity_fields_not_accepted_as_face_flux"]))
        self.assertIn("u_velocity", result["missing"])


if __name__ == "__main__":
    unittest.main()
