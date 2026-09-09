import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("prepare_oras5_arctic_entrances_request.py")
SPEC = importlib.util.spec_from_file_location("prepare_oras5_arctic_entrances_request", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class ArcticEntrancesRequestTests(unittest.TestCase):
    def test_contract_has_both_gates_four_fields_and_four_months(self):
        payload = module.build_manifest()
        self.assertEqual("native_mesh_acquired_four_snapshot_transport_synthesis_executed", payload["status"])
        self.assertEqual({"votemper", "vosaline", "vozocrtx", "vomecrty"}, set(payload["request"]["fields"]))
        self.assertEqual(4, len(payload["request"]["months"]))
        self.assertEqual({"fram", "barents"}, set(payload["request"]["domains"]))
        self.assertEqual(16, len(payload["sources"]))
        self.assertEqual("research/osw-m3-oras5-barents-section-bakeoff.json", payload["section_bakeoff_receipt"])
        self.assertEqual("research/osw-m3-oras5-barents-section-sensitivity.json", payload["section_sensitivity_receipt"])
        self.assertEqual("research/osw-m3-oras5-arctic-section-geometry-audit.json", payload["full_depth_geometry_receipt"])
        self.assertEqual("research/osw-m3-oras5-arctic-transport-pilot-201802.json", payload["pilot_transport_receipt"])
        self.assertEqual("research/osw-m3-oras5-arctic-seasons-2018.json", payload["seasonal_transport_receipt"])

    def test_fram_and_barents_preserve_opposing_branches(self):
        gates = {gate["name"]: gate for gate in module.build_manifest()["gate_contracts"]}
        self.assertIn("western export", gates["Fram Strait"]["required_decomposition"])
        self.assertIn("eastern Atlantic inflow", gates["Fram Strait"]["required_decomposition"])
        self.assertIn("northern return flow", gates["Barents Sea Opening"]["required_decomposition"])
        self.assertIn("virtual-endpoint mixed U/V", gates["Barents Sea Opening"]["selection_rule"])
        self.assertIn("wet T cell", gates["Barents Sea Opening"]["grid_representation_warning"])

    def test_native_grid_suffixes_match_staggering(self):
        self.assertIn("_grid_T_02.nc", module.source_url("vosaline", "201802"))
        self.assertIn("_grid_U_02.nc", module.source_url("vozocrtx", "201802"))
        self.assertIn("_grid_V_02.nc", module.source_url("vomecrty", "201802"))


if __name__ == "__main__":
    unittest.main()
