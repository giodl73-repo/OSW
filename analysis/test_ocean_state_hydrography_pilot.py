import json
import pathlib

import numpy as np

from acquire_ocean_state_hydrography_pilot import assign_provinces, summarize


ROOT = pathlib.Path(__file__).parent.parent
ARTIFACT = ROOT / "research/ocean-state-hydrography-pilot-2018.json"


def test_distribution_summary_is_complete_and_ordered():
    result = summarize(np.array([-2.0, 0.0, 2.0, 4.0, 6.0]))
    assert result["sample_count"] == 5
    assert result["mean_degC"] == 2.0
    assert result["minimum_degC"] <= result["p10_degC"] <= result["median_degC"] <= result["p90_degC"] <= result["maximum_degC"]


def test_polygon_assignment_exposes_overlap_and_missing_support():
    from shapely.geometry import box

    lon = np.array([[0.5, 1.5, 3.0]])
    lat = np.array([[0.5, 0.5, 0.5]])
    assigned, audit = assign_provinces(lon, lat, {"A": box(0, 0, 2, 1), "B": box(1, 0, 2, 1)})
    assert assigned.tolist() == [["A", "A", ""]]
    assert audit == {"assigned_horizontal_cells": 2, "unassigned_horizontal_cells": 1, "overlap_cell_count": 1}


def test_committed_stage_3_artifact_contract():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["schema"] == "osw-ocean-state-hydrography-pilot-v1"
    assert payload["status"] == "stage_3_temperature_only_model_screen"
    assert payload["admitted_properties"] == ["sea_water_potential_temperature"]
    assert {item["property"] for item in payload["unsupported_properties"]} == {
        "sea_water_salinity", "sea_water_density", "moles_of_oxygen_per_unit_mass_in_sea_water", "heat_content"
    }
    assert payload["grid"]["overlap_cell_count"] == 0
    assert payload["grid"]["coordinate_extent_deg"] == {
        "west": -83.25,
        "east": -39.5,
        "south": -71.0233154296875,
        "north": -46.569602966308594,
    }
    assert len(payload["property_passports"]) == 96
    assert len(payload["adjacent_contrasts"]) == 128
    assert payload["source_custody"]["product_doi"] == "10.24381/cds.67e8eeb7"
    assert "CC-BY" in payload["source_custody"]["license"]
    assert payload["provinces"]
    assert payload["property_passports"]
    assert payload["adjacent_contrasts"]
    for passport in payload["property_passports"]:
        assert passport["address"]["geometry_edition"] == "longhurst-v4-54"
        assert passport["evidence_class"] == "assimilative_reanalysis_model_screen"
        assert 0 < passport["support"]["fraction"] <= 1
        assert passport["uncertainty"]["status"] == "not_estimated"
        values = passport["distribution"]
        assert values["minimum_degC"] <= values["p10_degC"] <= values["median_degC"] <= values["p90_degC"] <= values["maximum_degC"]
    assert all(item["inference"] == "descriptive_model_screen_no_independence_or_significance_claim" for item in payload["adjacent_contrasts"])
