import importlib.util
import json
import pathlib
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("calculate_section_transport.py")
SPEC = importlib.util.spec_from_file_location("calculate_section_transport", MODULE_PATH)
transport = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(transport)
FIXTURE = json.loads((MODULE_PATH.parent / "fixtures/section-transport-balanced-synthetic.json").read_text(encoding="utf-8"))


class SectionTransportTests(unittest.TestCase):
    def test_balanced_fixture_has_zero_net_volume_and_reference_invariant_heat(self):
        result = transport.calculate(FIXTURE)
        self.assertAlmostEqual(0, result["volume_transport"]["net_Sv"])
        self.assertAlmostEqual(.02, result["volume_transport"]["positive_Sv"])
        self.assertAlmostEqual(-.02, result["volume_transport"]["negative_Sv"])
        heat = [case["net_PW"] for case in result["reference_relative_heat_transport"]]
        self.assertTrue(all(abs(value - heat[0]) < 1e-15 for value in heat))
        self.assertAlmostEqual(1027 * 3992 * 40000 / 1e15, heat[0])

    def test_reference_change_identity_for_nonzero_volume(self):
        payload = json.loads(json.dumps(FIXTURE))
        payload["normal_velocity_m_s"] = [1, 0, 0, 0]
        result = transport.calculate(payload, (0, 5))
        audit = result["reference_change_audit"][0]
        self.assertAlmostEqual(0, audit["identity_residual_W"], delta=1e-6)
        self.assertLess(audit["actual_change_W"], 0)

    def test_layer_branches_sum_to_section_branches(self):
        result = transport.calculate(FIXTURE)
        self.assertAlmostEqual(result["volume_transport"]["positive_Sv"], sum(layer["positive_volume_Sv"] for layer in result["layers"]))
        self.assertAlmostEqual(result["volume_transport"]["negative_Sv"], sum(layer["negative_volume_Sv"] for layer in result["layers"]))
        for layer in result["layers"]:
            self.assertAlmostEqual(layer["volume_Sv"], layer["positive_volume_Sv"] + layer["negative_volume_Sv"])

    def test_dry_cells_do_not_require_velocity_or_temperature(self):
        payload = json.loads(json.dumps(FIXTURE))
        payload["wet_fraction"][0] = 0
        payload["normal_velocity_m_s"][0] = None
        payload["potential_temperature_degC"][0] = None
        result = transport.calculate(payload)
        self.assertEqual(3, result["wet_cell_count"])

    def test_rejects_invalid_wet_fraction(self):
        payload = json.loads(json.dumps(FIXTURE))
        payload["wet_fraction"][0] = 1.1
        with self.assertRaisesRegex(ValueError, "wet fraction"):
            transport.calculate(payload)

    def test_one_section_does_not_claim_mass_closure(self):
        result = transport.calculate(FIXTURE)
        self.assertEqual("not_evaluable_from_one_open_section", result["mass_closure"]["status"])
        self.assertIsNone(result["mass_closure"]["residual_Sv"])

    def test_explicit_partial_cell_thickness_controls_area(self):
        payload = json.loads(json.dumps(FIXTURE))
        payload["cell_thickness_m"] = [5, 10, 10, 10]
        result = transport.calculate(payload)
        self.assertEqual(35000, result["wet_area_m2"])
        self.assertEqual("nominal layer thickness multiplied by wet fraction", result["geometry_contract"])

    def test_dry_explicit_cell_thickness_may_be_null(self):
        payload = json.loads(json.dumps(FIXTURE))
        payload["wet_fraction"][0] = 0
        payload["cell_thickness_m"] = [None, 10, 10, 10]
        result = transport.calculate(payload)
        self.assertEqual(3, result["wet_cell_count"])


if __name__ == "__main__":
    unittest.main()
