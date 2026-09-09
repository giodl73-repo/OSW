import json
from pathlib import Path

import numpy as np

from acquire_longhurst_2007_gebco_depths import water_volume_by_depth_band


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research" / "longhurst-2007-gebco-2026-depths.json"
RECEIPT = ROOT / "research" / "longhurst-2007-gebco-2026-source-receipt.json"
BROWSER = ROOT / "column" / "province-footprints.js"


def load():
    return json.loads(DATA.read_text(encoding="utf-8"))


def test_water_volume_integrator_truncates_each_reference_band():
    volumes = water_volume_by_depth_band(
        np.array([90, 500, 7_000]),
        np.array([1.0, 2.0, 3.0]),
    )
    assert volumes == {
        "epipelagic": 1_090.0,
        "mesopelagic": 3_000.0,
        "bathypelagic": 9_000.0,
        "abyssopelagic": 6_000.0,
        "hadalpelagic": 3_000.0,
    }


def test_source_receipt_identifies_exact_queries_without_vendoring_payloads():
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["schema"] == "osw-longhurst-2007-gebco-2026-source-receipt-v1"
    assert "provider bytes omitted" in receipt["source_payload_posture"]
    assert receipt["sources"]["geometry"]["feature_count"] == 54
    assert receipt["sources"]["geometry"]["crs"] == "EPSG:4326"
    assert receipt["sources"]["geometry"]["license"].startswith("CC BY 4.0")
    assert "typeName=MarineRegions:longhurst" in receipt["sources"]["geometry"]["url"]
    assert "elevation[30:60:43170][30:60:86370]" in receipt["sources"]["elevation"]["url"]
    assert "tid[30:60:43170][30:60:86370]" in receipt["sources"]["tid"]["url"]
    for source in receipt["sources"].values():
        assert source["response_bytes"] > 0
        assert len(source["response_sha256"]) == 64


def test_crosswalk_exposes_the_56_to_54_edition_mismatch():
    payload = load()
    assert len(payload["crosswalk"]) == 56
    assert len(payload["provinces"]) == 54
    unavailable = {item["osw_code"] for item in payload["crosswalk"] if item["source_code"] is None}
    assert unavailable == {"NPSE", "OCAL"}
    aliases = {item["osw_code"]: item["source_code"] for item in payload["crosswalk"] if item["note"].startswith("code alias")}
    assert aliases == {"HUMB": "CHIL", "IND E": "INDE", "IND W": "INDW", "NAST E": "NASE", "NAST W": "NASW"}


def test_global_mask_and_area_weighted_summaries_close():
    payload = load()
    coverage = payload["coverage"]
    assert coverage == {
        "source_feature_count": 54,
        "osw_directory_count": 56,
        "source_aligned_osw_count": 54,
        "older_only_osw_count": 2,
        "geometry_grid_cell_count": 687150,
        "wet_geometry_grid_cell_count": 681631,
        "non_wet_geometry_grid_cell_count": 5519,
        "global_wet_grid_cell_count": 684403,
        "wet_cells_outside_geometry_count": 2772,
        "overlapping_geometry_grid_cell_count": 0,
        "source_geometry_repair_count": 3,
    }
    assert {item["source_code"] for item in payload["source_geometry_repairs"]} == {"ALSK", "NECS", "SUND"}
    assert all(abs(item["relative_planar_area_change"]) < 1e-9 for item in payload["source_geometry_repairs"])
    assert sum(item[2] - item[1] + 1 for item in payload["footprint_runs"]) == coverage["geometry_grid_cell_count"]
    assert all(0 <= item[0] < 720 and 0 <= item[1] <= item[2] < 1440 for item in payload["footprint_runs"])
    for province in payload["provinces"].values():
        assert province["wet_sample_count"] > 0
        assert province["sampled_wet_area_km2"] > 0
        assert abs(sum(province["wet_area_fraction_by_seafloor_band"].values()) - 1) < 5e-6
        assert abs(sum(province["wet_area_fraction_by_tid_class"].values()) - 1) < 5e-6
        assert province["sampled_water_volume_km3"] > 0
        assert province["area_weighted_mean_water_depth_m"] > 0
        assert abs(sum(province["water_volume_fraction_by_depth_band"].values()) - 1) < 5e-6
        assert abs(sum(province["water_volume_km3_by_depth_band"].values()) - province["sampled_water_volume_km3"]) < 0.1
    volume = payload["volume_summary"]
    assert volume["sampled_source_aligned_water_volume_km3"] == 1_337_654_389.66
    assert volume["water_volume_fraction_by_depth_band"] == {
        "epipelagic": 0.051439,
        "mesopelagic": 0.194953,
        "bathypelagic": 0.628426,
        "abyssopelagic": 0.124062,
        "hadalpelagic": 0.001121,
    }
    assert abs(sum(volume["water_volume_fraction_by_depth_band"].values()) - 1) < 5e-6
    assert abs(sum(volume["water_volume_km3_by_depth_band"].values()) - volume["sampled_source_aligned_water_volume_km3"]) < 0.1
    assert volume["independent_context"]["published_ocean_volume_km3"] == 1_338_000_000
    assert abs(volume["independent_context"]["difference_from_published_percent"]) < 0.1
    assert "did not calibrate" in volume["independent_context"]["interpretation"]


def test_browser_payload_is_exactly_the_research_payload():
    prefix = "window.OSW_PROVINCE_FOOTPRINTS = "
    text = BROWSER.read_text(encoding="utf-8")
    assert text.startswith(prefix) and text.endswith(";\n")
    assert json.loads(text[len(prefix):-2]) == load()


def test_comparative_fields_have_complete_values_and_expected_leaders():
    provinces = load()["provinces"]
    assert len(provinces) == 54
    metrics = {
        "sampled_wet_area_km2": "SPSG",
        "sampled_water_volume_km3": "SPSG",
        "area_weighted_mean_water_depth_m": "NPPF",
    }
    for field, expected_leader in metrics.items():
        assert all(province[field] > 0 for province in provinces.values())
        assert len({province[field] for province in provinces.values()}) == 54
        ordered = sorted(provinces.values(), key=lambda province: province[field], reverse=True)
        assert ordered[0]["osw_code"] == expected_leader
        assert len({province["osw_code"] for province in ordered}) == 54
