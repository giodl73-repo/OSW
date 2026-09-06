import hashlib
import json
import pathlib
import unittest

import netCDF4


ROOT = pathlib.Path(__file__).parent.parent
RESEARCH = ROOT / "research"
DATA = ROOT / "atlas" / "data"


def load(name):
    return json.loads((RESEARCH / name).read_text(encoding="utf-8"))


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class Oras5M3ArtifactTests(unittest.TestCase):
    def test_m2_arctic_entrances_are_pinned_and_keep_fram_lanes_separate(self):
        motion = load("osw-m2-arctic-entrances-motion-2018.json")
        for source in motion["sources"]:
            self.assertEqual(source["sha256"], sha256_file(ROOT / source["path"]))
            self.assertEqual(71, source["shape"][0])
        fram, barents = motion["entrances"]
        lanes = {lane["name"]: lane for lane in fram["lanes"]}
        self.assertLess(lanes["western export lane"]["annual_frame_weighted_mean_normal_velocity_m_s"], 0)
        self.assertGreater(lanes["eastern inflow lane"]["annual_frame_weighted_mean_normal_velocity_m_s"], 0)
        self.assertGreater(barents["annual_frame_weighted_mean_normal_velocity_m_s"], 0)

    def test_arctic_m3_request_is_deterministic_and_requires_salinity(self):
        manifest = load("osw-m3-oras5-arctic-entrances-request-2018.json")
        encoded = json.dumps(manifest["request"], sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(manifest["request_sha256"], hashlib.sha256(encoded).hexdigest())
        self.assertIn("vosaline", manifest["request"]["fields"])
        self.assertEqual(16, len(manifest["sources"]))
        self.assertEqual("native_mesh_acquired_four_snapshot_transport_synthesis_executed", manifest["status"])
        self.assertEqual("research/osw-m3-oras5-arctic-gate-readiness.json", manifest["geometry_receipt"])

    def test_arctic_state_and_transport_pilot_are_pinned(self):
        state = load("osw-m3-oras5-arctic-entrances-state-201802.json")
        self.assertEqual(state["output"]["sha256"], sha256_file(ROOT / state["output"]["path"]))
        self.assertEqual([75, 200, 240], state["shape"])
        self.assertEqual({"votemper", "vosaline", "vozocrtx", "vomecrty"}, set(state["fields"]))
        pilot = load("osw-m3-oras5-arctic-transport-pilot-201802.json")
        for source in pilot["sources"].values():
            self.assertEqual(source["sha256"], sha256_file(ROOT / source["path"]))
        self.assertAlmostEqual(-0.4492724105349816, pilot["sections"]["fram"]["volume_transport_Sv"]["net_Sv"])
        self.assertAlmostEqual(3.2308784062818474, pilot["sections"]["barents-proxy"]["volume_transport_Sv"]["net_Sv"])
        self.assertAlmostEqual(3.637633170542391, pilot["sections"]["barents-closure"]["volume_transport_Sv"]["net_Sv"])
        self.assertTrue(pilot["checks"]["volume_invariant_to_tracer_collocation"])

    def test_arctic_four_snapshot_synthesis_is_pinned(self):
        seasons = load("osw-m3-oras5-arctic-seasons-2018.json")
        self.assertEqual(24, len(seasons["receipts"]))
        for receipt in seasons["receipts"]:
            self.assertEqual(receipt["sha256"], sha256_file(ROOT / receipt["path"]))
        for state in seasons["state_files"]:
            self.assertEqual(state["sha256"], sha256_file(ROOT / state["path"]))
            self.assertEqual(state["receipt_sha256"], sha256_file(ROOT / state["receipt_path"]))
        self.assertAlmostEqual(-1.4233559609776303, seasons["sections"]["fram"]["sample_summary"]["net_volume_Sv"]["sample_mean"])
        self.assertAlmostEqual(3.2443910066619295, seasons["sections"]["barents-proxy"]["sample_summary"]["net_volume_Sv"]["sample_mean"])
        self.assertAlmostEqual(3.609848415978025, seasons["sections"]["barents-closure"]["sample_summary"]["net_volume_Sv"]["sample_mean"])
        self.assertTrue(seasons["checks"]["all_three_0C_heat_signs_persist"])

    def test_arctic_screen_sensitivity_is_pinned_and_directionally_separated(self):
        sensitivity = load("osw-m2-arctic-entrances-sensitivity-2018.json")
        for source in sensitivity["sources"]:
            self.assertEqual(source["sha256"], sha256_file(ROOT / source["path"]))
        self.assertEqual(20, sensitivity["fram_eastern_inflow"]["summary"]["direction_support_count"])
        self.assertEqual(18, sensitivity["fram_western_export"]["summary"]["direction_support_count"])
        self.assertEqual(11, sensitivity["barents_eastward_inflow"]["summary"]["direction_support_count"])

    def test_arctic_pathways_are_pinned_and_keep_track_fates_explicit(self):
        pathways = load("osw-m2-arctic-entrance-pathways-2018.json")
        for source in pathways["sources"]:
            self.assertEqual(source["sha256"], sha256_file(ROOT / source["path"]))
        summaries = {item["group"]: item for item in pathways["summaries"]}
        self.assertEqual(112, len(pathways["tracks"]))
        self.assertEqual({"southward": 26, "other": 0, "terminated": 6}, summaries["fram_west_export"]["fates"])
        self.assertEqual({"northward": 14, "other": 13, "terminated": 13}, summaries["fram_east_inflow"]["fates"])
        self.assertEqual({"eastward": 27, "other": 3, "terminated": 10}, summaries["barents_inflow"]["fates"])

    def test_mesh_payload_matches_receipt_and_native_shape(self):
        receipt = load("osw-m3-oras5-drake-mesh.json")
        path = DATA / "oras5-drake-mesh.nc"
        self.assertEqual(receipt["output"]["sha256"], sha256_file(path))
        with netCDF4.Dataset(path) as dataset:
            self.assertEqual((75, 200, 176), dataset.variables["umask"].shape)

    def test_state_payload_matches_receipt_and_mesh_hash(self):
        mesh = load("osw-m3-oras5-drake-mesh.json")
        for month in ("201802", "201805", "201808", "201811"):
            with self.subTest(month=month):
                state = load(f"osw-m3-oras5-drake-state-{month}.json")
                path = DATA / f"oras5-drake-state-{month}.nc"
                self.assertEqual(state["output"]["sha256"], sha256_file(path))
                self.assertEqual(mesh["output"]["sha256"], state["mesh_sha256"])

    def test_native_geometry_audit_is_pinned_to_mesh(self):
        mesh = load("osw-m3-oras5-drake-mesh.json")
        audit = load("osw-m3-oras5-face-thickness-audit.json")
        self.assertEqual(mesh["output"]["sha256"], audit["source"]["sha256"])
        self.assertEqual({"u": 0, "v": 0}, audit["mask_mismatch_count"])
        self.assertEqual("candidate_passes_native_geometry_consistency", audit["status"])

    def test_transport_is_pinned_to_canonical_section_input(self):
        section = load("osw-m3-oras5-drake-section-input-201802.json")
        transport = load("osw-m3-oras5-drake-transport-201802.json")
        encoded = json.dumps(section, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(hashlib.sha256(encoded).hexdigest(), transport["input_sha256"])
        self.assertAlmostEqual(124.29048534937463, transport["volume_transport"]["net_Sv"])
        self.assertEqual("not_evaluable_from_one_open_section", transport["mass_closure"]["status"])

    def test_reference_change_identity_is_exact_in_receipt(self):
        for month in ("201802", "201805", "201808", "201811"):
            transport = load(f"osw-m3-oras5-drake-transport-{month}.json")
            self.assertTrue(all(abs(item["identity_residual_W"]) <= 1 for item in transport["reference_change_audit"]))

    def test_seasonal_synthesis_is_pinned_to_all_transport_receipts(self):
        synthesis = load("osw-m3-oras5-drake-seasons-2018.json")
        self.assertEqual(4, len(synthesis["sources"]))
        for source in synthesis["sources"]:
            self.assertEqual(source["sha256"], sha256_file(ROOT / source["path"]))
        self.assertAlmostEqual(124.18487732845439, synthesis["summary"]["net_volume_Sv"]["mean"])
        self.assertAlmostEqual(5.642427547392003, synthesis["summary"]["net_volume_Sv"]["range"])

    def test_method_sensitivity_is_pinned_to_native_sources(self):
        sensitivity = load("osw-m3-oras5-drake-method-sensitivity-2018.json")
        sources = sensitivity["sources"]
        self.assertEqual(sources["mesh"]["sha256"], sha256_file(ROOT / sources["mesh"]["path"]))
        self.assertEqual(sources["primary_gate"]["sha256"], sha256_file(ROOT / sources["primary_gate"]["path"]))
        for source in sources["states"]:
            self.assertEqual(source["sha256"], sha256_file(ROOT / source["path"]))
        self.assertAlmostEqual(0.11139706124680515, sensitivity["across_gate_four_sample_mean_volume_Sv"]["range"])
        volume_means = {item["net_volume_Sv"]["mean"] for item in sensitivity["collocation_summary"]}
        self.assertEqual(1, len(volume_means))

    def test_vertical_synthesis_is_pinned_and_conservative(self):
        vertical = load("osw-m3-oras5-drake-vertical-2018.json")
        for source in vertical["sources"]:
            self.assertEqual(source["sha256"], sha256_file(ROOT / source["path"]))
        self.assertTrue(all(abs(item["volume_residual_Sv"]) < 1e-12 for item in vertical["conservation_audit"]))
        self.assertTrue(all(abs(item["heat_0C_residual_PW"]) < 1e-12 for item in vertical["conservation_audit"]))

    def test_temperature_classes_are_pinned_and_conservative(self):
        classes = load("osw-m3-oras5-drake-temperature-classes-2018.json")
        for group in classes["sources"].values():
            for source in group:
                self.assertEqual(source["sha256"], sha256_file(ROOT / source["path"]))
        self.assertTrue(all(abs(item["volume_residual_Sv"]) < 1e-12 for item in classes["conservation_audit"]))
        self.assertTrue(all(abs(item["heat_0C_residual_PW"]) < 1e-12 for item in classes["conservation_audit"]))

    def test_section_field_is_pinned_to_four_native_sections(self):
        field = load("osw-m3-oras5-drake-section-field-2018.json")
        self.assertEqual([75, 87], field["shape"])
        self.assertEqual(4662, sum(value is not None for value in field["mean_potential_temperature_degC"]))
        for source in field["sources"]:
            self.assertEqual(source["sha256"], sha256_file(ROOT / source["path"]))
        self.assertAlmostEqual(124.18487732845439, field["transport_sum_audit"]["volume_Sv"])
        self.assertAlmostEqual(1.3004260575272404, field["transport_sum_audit"]["heat_transport_PW_at_0C"])

    def test_m4_control_box_is_pinned_and_nearly_volume_closed(self):
        box = load("osw-m4-oras5-drake-control-box-2018.json")
        self.assertEqual(box["sources"]["mesh"]["sha256"], sha256_file(ROOT / box["sources"]["mesh"]["path"]))
        for source in box["sources"]["states"]:
            self.assertEqual(source["sha256"], sha256_file(ROOT / source["path"]))
        self.assertLess(box["summary"]["net_outward_volume_Sv"]["maximum"], .01)
        self.assertLess(box["summary"]["across_reference_mean_heat_range_PW"], .001)
        for month in box["months"]:
            self.assertTrue(all(abs(item["identity_residual_W"]) < 2 for item in month["reference_change_audit"]))

    def test_m4_box_sensitivity_is_pinned_and_separates_geometry(self):
        sensitivity = load("osw-m4-oras5-drake-control-box-sensitivity-2018.json")
        self.assertEqual(sensitivity["sources"]["mesh"]["sha256"], sha256_file(ROOT / sensitivity["sources"]["mesh"]["path"]))
        for source in sensitivity["sources"]["states"]:
            self.assertEqual(source["sha256"], sha256_file(ROOT / source["path"]))
        self.assertEqual(8, len(sensitivity["variants"]))
        for family in sensitivity["family_summary"]:
            self.assertLess(family["maximum_absolute_monthly_volume_imbalance_Sv"], .01)
        ranges = {item["family"]: item["heat_0C_mean_PW_across_boxes"]["range"] for item in sensitivity["family_summary"]}
        self.assertGreater(ranges["eastward_extent"], .03)
        self.assertGreater(ranges["northward_extent"], .05)

    def test_m4_t_metrics_companion_is_pinned(self):
        receipt = load("osw-m4-oras5-drake-t-metrics.json")
        output = ROOT / receipt["output"]["path"]
        self.assertEqual(receipt["output"]["sha256"], sha256_file(output))
        self.assertEqual(receipt["mesh_receipt"]["sha256"], sha256_file(ROOT / receipt["mesh_receipt"]["path"]))
        self.assertTrue(receipt["t_cell_area_m2"]["all_finite_positive"])

    def test_m4_storage_probe_is_pinned_and_reference_invariant(self):
        probe = load("osw-m4-oras5-drake-storage-probe-2018.json")
        for key in ("mesh", "t_metrics", "control_box"):
            source = probe["sources"][key]
            self.assertEqual(source["sha256"], sha256_file(ROOT / source["path"]))
        for source in probe["sources"]["states"]:
            self.assertEqual(source["sha256"], sha256_file(ROOT / source["path"]))
        for interval in probe["intervals"]:
            values = [item["storage_tendency_PW"] for item in interval["reference_tendency_audit"]]
            self.assertLess(max(values) - min(values), 1e-12)

    def test_compact_budget_states_are_pinned_to_mesh(self):
        mesh = load("osw-m3-oras5-drake-mesh.json")
        for month in range(1, 13):
            receipt = load(f"osw-m4-oras5-drake-budget-state-2018{month:02d}.json")
            path = ROOT / receipt["output"]["path"]
            self.assertEqual(receipt["output"]["sha256"], sha256_file(path))
            self.assertEqual(mesh["output"]["sha256"], receipt["mesh_receipt"]["mesh_output_sha256"])

    def test_monthly_budget_is_pinned_and_exact_at_anchors(self):
        budget = load("osw-m4-oras5-drake-monthly-budget-2018.json")
        for key in ("mesh", "t_metrics", "control_box", "storage_probe"):
            source = budget["sources"][key]
            self.assertEqual(source["sha256"], sha256_file(ROOT / source["path"]))
        for source in budget["sources"]["budget_states"]:
            self.assertEqual(source["sha256"], sha256_file(ROOT / source["path"]))
        self.assertEqual(12, len(budget["monthly"]))
        self.assertEqual(11, len(budget["intervals"]))
        for anchor in budget["four_month_anchor_audit"]:
            self.assertEqual(0, anchor["volume_residual_Sv"])
            self.assertEqual(0, anchor["heat_0C_residual_PW"])
            self.assertEqual(0, anchor["temperature_residual_degC"])
        self.assertAlmostEqual(0.06215130344203181, budget["sampled_span"]["mean_unclosed_PW"])

    def test_m4_native_surface_budget_is_pinned_and_partial(self):
        receipt = load("osw-m4-oras5-drake-surface-heat-2018.json")
        surface_path = ROOT / receipt["output"]["path"]
        self.assertEqual(receipt["output"]["sha256"], sha256_file(surface_path))
        self.assertEqual([12, 86, 16], receipt["shape"])
        budget = load("osw-m4-oras5-drake-surface-budget-2018.json")
        for key in ("monthly_budget", "surface_heat", "surface_receipt", "t_metrics"):
            source = budget["sources"][key]
            self.assertEqual(source["sha256"], sha256_file(ROOT / source["path"]))
        span = budget["sampled_span"]
        self.assertAlmostEqual(0.019466496642464314, span["time_weighted_mean_net_downward_surface_heat_PW"])
        self.assertAlmostEqual(0.0426848067995675, span["mean_remaining_after_surface_heat_PW"])
        self.assertTrue(all(item["remaining_after_surface_heat_PW"] > 0 for item in budget["intervals"]))


if __name__ == "__main__":
    unittest.main()
