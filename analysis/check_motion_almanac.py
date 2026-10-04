"""Check that the motion atlas covers its complete named source ledgers."""

import csv
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path

from build_ocean_current_length_evidence import build as build_length_evidence
from build_loop_eddy_name_date_conflict_audit import build as build_loop_eddy_name_date_conflict_audit
from build_ocean_current_gate_distances import build as build_gate_distances
from build_ocean_current_nasa_crosswalk import build as build_current_nasa_crosswalk
from build_ocean_current_state_relation_matrix import build as build_current_state_matrix
from build_nasa_current_cartographic_crop_join import build as build_nasa_current_cartographic_crop_join
from build_nasa_object_movie_variant_join import build as build_nasa_object_movie_variant_join
from build_noaa_eddy_seasonal_manifest import build as build_noaa_eddy_seasonal_manifest
from build_noaa_nasa_eddy_crop_join import build as build_noaa_nasa_eddy_crop_join
from build_nasa_perpetual_ocean_atlas_catalog import build as build_nasa_perpetual_ocean_atlas_catalog


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"


def read(name: str) -> dict:
    return json.loads((RESEARCH / name).read_text(encoding="utf-8"))


def main() -> None:
    name_date_conflict = read("loop-eddy-cameron-darwin-name-date-conflict.json")
    assert name_date_conflict == build_loop_eddy_name_date_conflict_audit(), "Cameron/Darwin name-date audit is stale"
    assert name_date_conflict["assessment"]["type"] == "within_paper_name_date_inconsistency"
    assert name_date_conflict["assessment"]["section_3_4_matches_horizon_by_name"] == {
        "Cameron": True, "Darwin": False}
    observed = name_date_conflict["independent_observation"]
    assert observed["name_origin"] == "horizon_attributed_not_independently_named"
    assert [(row["name"], row["date"]) for row in observed["observations"]] == [
        ("Cameron", "2009-01-20"), ("Darwin", "2009-07-25"), ("Darwin", "2009-08-05")]
    assert observed["observations"][0]["reported_position_lon_lat"] == [-95.0, 22.5]
    assert all(row["reported_position_lon_lat"] is None for row in observed["observations"][1:])
    currents = read("ocean-current-almanac.json")
    length_evidence = read("ocean-current-length-evidence.json")
    assert length_evidence == build_length_evidence(), "Length evidence ledger is stale"
    assert len(length_evidence["entries"]) == len(currents["entries"])
    acc_length = next(item for item in length_evidence["entries"] if item["current_id"] == "acc")
    assert acc_length["length_km"] == 25000
    assert acc_length["source_reported_length_variants"][0]["length_km_approx"] == 21000
    assert acc_length["source_reported_length_variants"][0]["rank_eligible"] is False
    humboldt_length = next(item for item in length_evidence["entries"] if item["current_id"] == "peru-humboldt")
    assert humboldt_length["length_km"] == 6000
    assert humboldt_length["rank_eligible"] and humboldt_length["status"] == "published_estimate"
    assert length_evidence["counts"]["published_estimate"] == 11
    alaska_coastal = next(item for item in length_evidence["entries"] if item["current_id"] == "alaska-coastal-gulf")
    assert alaska_coastal["length_km"] == 1700 and alaska_coastal["rank_eligible"]
    assert "Seward" in alaska_coastal["scope"] and "Samalga" in alaska_coastal["scope"]
    assert next(item for item in length_evidence["entries"] if item["current_id"] == "alaska")["length_km"] is None
    pacific_euc_length = next(item for item in length_evidence["entries"] if item["current_id"] == "pacific-equatorial-undercurrent")
    assert pacific_euc_length["length_km"] == 14000 and pacific_euc_length["rank_eligible"]
    assert pacific_euc_length["source_reported_length_variants"][0]["length_km_approx"] == 13000
    gate_distances = read("ocean-current-gate-distances.json")
    assert gate_distances == build_gate_distances(), "Current gate-distance audit is stale"
    assert gate_distances["count"] == 7
    scenario_rows = {row["current_id"]: row["gate_distance_sensitivity"]
                     for row in gate_distances["entries"]}
    assert {key: (row["geographic_span_rank_best"], row["geographic_span_rank_worst"])
            for key, row in scenario_rows.items()} == {
        "agulhas-return": (1, 1), "deep-western-boundary": (2, 2),
        "east-greenland": (3, 3), "east-australian": (4, 4),
        "agulhas": (5, 5), "benguela": (6, 7), "brazil": (6, 7)}
    for row in gate_distances["entries"]:
        scenario = row["gate_distance_sensitivity"]
        assert scenario["scenario_min_km"] <= row["direct_gate_distance_km"] <= scenario["scenario_max_km"]
        assert scenario["scenario_count"] == (9 if row["gate_type"] == "source_latitude_span" else 81)
        assert scenario["perturbation_degrees"] == 0.5
        assert "not source-reported" in scenario["perturbation_basis"]
    assert {item["current_id"] for item in gate_distances["entries"]} == {
        item["current_id"] for item in length_evidence["entries"] if item["status"] == "derived_lower_bound"
    }
    new_floors = {item["current_id"]: item for item in gate_distances["entries"]
                  if item["current_id"] in {"benguela", "brazil", "deep-western-boundary"}}
    assert {key: (row["direct_gate_distance_km"], row["admitted_rounded_geographic_floor_km"])
            for key, row in new_floors.items()} == {
                "benguela": (1218.4, 1200),
                "brazil": (1218.4, 1200),
                "deep-western-boundary": (2496.6, 2400),
            }
    assert next(item for item in gate_distances["entries"] if item["current_id"] == "east-greenland")["start"]["latitude"] == 78.5
    illustrated_spans = read("ocean-current-illustrated-spans.json")
    assert illustrated_spans["counts"] == {
        "named_currents": 100,
        "mapped_currents": 27,
        "ranked_illustrated_spans": 24,
        "excluded_multi_basin_families": 3,
        "without_arrow": 73,
    }
    assert illustrated_spans["source_geojson_sha256"] == read("cartographic-ocean-current-state-join.json")["source_geojson_sha256"]
    assert {item["current_id"] for item in illustrated_spans["entries"]} == {item["id"] for item in currents["entries"]}
    ranked_spans = [item for item in illustrated_spans["entries"] if item["illustrated_span_rank"] is not None]
    assert [item["illustrated_span_rank"] for item in ranked_spans] == list(range(1, 25))
    assert all(item["identity_level"] != "family" and item["arrows"] for item in ranked_spans)
    assert all(item["longest_arrow_span_km"] == max(arrow["illustrated_span_km"] for arrow in item["arrows"]) for item in ranked_spans)
    assert all(item["illustrated_span_rank"] is None for item in illustrated_spans["entries"] if item["identity_level"] == "family")
    current_nasa_crosswalk = read("ocean-current-nasa-crosswalk.json")
    assert current_nasa_crosswalk == build_current_nasa_crosswalk(), "Current/NASA crosswalk is stale"
    assert current_nasa_crosswalk["counts"] == {
        "nasa_named_or_described": 7,
        "independent_context": 3,
        "regional_movie_only": len(currents["entries"]) - 10,
    }
    current_crop_join = read("nasa-current-cartographic-crop-join.json")
    assert current_crop_join == build_nasa_current_cartographic_crop_join(), "NASA current/crop join is stale"
    crop_records = {item["current_id"]: item for item in current_crop_join["records"]}
    assert len(crop_records) == 7
    assert len(crop_records["gulf-stream"]["cartographic_crop_contacts"]) == 8
    assert len(crop_records["agulhas"]["cartographic_crop_contacts"]) == 4
    assert len(crop_records["east-australian"]["cartographic_crop_contacts"]) == 6
    assert all(crop_records[key]["coverage_status"] == "no_mapped_source_arrow" for key in (
        "kuroshio", "indonesian-throughflow", "red-sea-saline-overflow", "persian-gulf-saline-overflow"
    ))
    movie_variant_join = read("nasa-object-movie-variant-join.json")
    assert movie_variant_join == build_nasa_object_movie_variant_join(), "NASA object/movie variant join is stale"
    assert movie_variant_join["movie_listing_count"] == 55
    assert movie_variant_join["status_counts"]["source_group_or_cue_join"] == 14
    seasonal_eddies = read("noaa-munster-eddy-seasonal-manifest-2021-2023.json")
    assert seasonal_eddies == build_noaa_eddy_seasonal_manifest(), "NOAA seasonal manifest is stale"
    assert seasonal_eddies["snapshot_count"] == 12
    assert seasonal_eddies["detection_count_sum"] == 92891
    eddy_crop_join = read("noaa-nasa-eddy-crop-join.json")
    assert eddy_crop_join == build_noaa_nasa_eddy_crop_join(), "NOAA/NASA eddy crop join is stale"
    assert eddy_crop_join["date_count"] == 5
    assert eddy_crop_join["detection_count"] == 38675
    assert set(eddy_crop_join["dates"]) == {"2022-12-01", "2023-03-01", "2023-06-01", "2023-09-01", "2023-12-01"}
    integrated_catalog = read("nasa-perpetual-ocean-atlas-catalog.json")
    assert integrated_catalog == build_nasa_perpetual_ocean_atlas_catalog(), "NASA integrated catalog is stale"
    assert integrated_catalog["object_count"] == 22 and integrated_catalog["state_pair_count"] == 1232
    assert integrated_catalog["release_count"] == 7
    assert sum(row["object_count"] for row in integrated_catalog["releases"]) == 39
    assert {row["id"]: row["object_ids"] for row in integrated_catalog["releases"]} == {
        release["id"]: [item["id"] for item in read("nasa-perpetual-ocean-objects.json")["objects"] if release["id"] in item["nasa_sources"]]
        for release in integrated_catalog["releases"]
    }
    catalog_by_id = {item["id"]: item for item in integrated_catalog["records"]}
    assert len(catalog_by_id["ocean-eddies"]["named_eddy_context"]) == 136
    assert len(catalog_by_id["gulf-of-mexico-loop-eddies"]["named_eddy_context"]) == 97
    assert sum("specific_class_context" in item["relations"] for item in catalog_by_id["gulf-of-mexico-loop-eddies"]["named_eddy_context"]) == 96
    assert len(catalog_by_id["agulhas-rings"]["named_eddy_context"]) == 8
    berek_catalog = next(item for item in catalog_by_id["gulf-of-mexico-loop-eddies"]["named_eddy_context"] if item["named_eddy_id"] == "horizon:loop-77-primary")
    assert berek_catalog["published_observed_position"]["coordinate"] == [-89, 26]
    assert berek_catalog["published_dated_map_presence"]["date"] == "2023-12-21"
    assert all(not context["individual_nasa_identity_claim"] for item in integrated_catalog["records"] for context in item["named_eddy_context"])
    eddies = read("named-loop-current-eddies.json")
    eddy_names = read("named-loop-current-eddy-identities.json")
    loop_context = read("named-loop-eddy-nasa-context.json")
    eddy_geography = read("named-eddy-geography.json")
    eddy_geography_join = read("named-eddy-geography-join.json")
    eddy_inventory = read("ocean-eddy-name-inventory.json")
    index = read("ocean-current-atlas-index.json")
    named_editorial_paths = read("ocean-current-editorial-paths.json")
    taxonomy = read("ocean-motion-taxonomy.json")
    nasa = read("nasa-perpetual-ocean-objects.json")
    nasa_audit = read("nasa-perpetual-ocean-source-audit.json")
    nasa_coverage = read("nasa-perpetual-ocean-object-coverage-audit.json")
    tiles = read("nasa-perpetual-ocean-tile-join.json")
    state_tiles = read("nasa-perpetual-ocean-state-tile-join.json")
    nasa_crosswalk = read("nasa-ocean-object-state-crosswalk.json")
    nasa_matrix = read("nasa-object-state-relation-matrix.json")
    nasa_media = read("nasa-perpetual-ocean-object-media.json")
    nasa_evidence = read("nasa-perpetual-ocean-object-evidence.json")
    nasa_properties = read("nasa-perpetual-ocean-object-properties.json")
    nasa_release_media = read("nasa-perpetual-ocean-release-media.json")
    nasa_crop_timeline = read("nasa-perpetual-ocean-crop-timeline.json")
    nasa_forms = read("nasa-perpetual-ocean-motion-forms.json")
    marine_regions = read("marine-regions-current-crosswalk.json")
    states = read("ocean-motion-state-join.json")
    cartographic = read("cartographic-ocean-current-state-join.json")
    current_state_matrix = read("ocean-current-state-relation-matrix.json")
    assert current_state_matrix == build_current_state_matrix(), "Current/state matrix is stale"
    assert current_state_matrix["current_count"] == len(currents["entries"]) == 100
    assert current_state_matrix["state_count"] == len(states["states"]) == 56
    assert current_state_matrix["pair_count"] == 5600
    assert current_state_matrix["atlas_linked_pair_count"] == 213
    assert current_state_matrix["currents"]["alaska-coastal-gulf"]["states_by_relation"]["editorial_locator_candidate"] == ["ALSK", "BERS"]
    assert all(current_state_matrix["states"][code]["currents"]["alaska-coastal-gulf"]["physical_relation"] ==
               "unknown_no_observed_current_core_footprint" for code in current_state_matrix["states"])
    assert current_state_matrix["states"]["MEDI"]["currents"]["northern-mediterranean"]["atlas_relation"] == "editorial_locator_candidate"
    assert current_state_matrix["states"]["NECS"]["currents"]["northern-mediterranean"]["atlas_relation"] == "unresolved"
    assert current_state_matrix["states"]["GFST"]["currents"]["gulf-stream"]["atlas_relation"] == "cartographic_arrow_crossing"
    assert current_state_matrix["states"]["GFST"]["currents"]["gulf-stream"]["cartographic_source_arrow_ids"]["stable"] == [57, 58]
    assert current_state_matrix["states"]["NAST W"]["currents"]["gulf-stream"]["cartographic_source_arrow_ids"]["width_sensitive"] == [58]
    assert current_state_matrix["states"]["NEWZ"]["currents"]["antarctic-coastal"]["cartographic_source_arrow_ids"] == {"stable": [29], "width_sensitive": [98]}
    assert current_state_matrix["states"]["SUND"]["currents"]["indonesian-throughflow"]["atlas_relation"] == "editorial_locator_candidate"
    for current_id, row in current_state_matrix["currents"].items():
        assigned = set(row["unresolved_states"])
        for status, codes in row["states_by_relation"].items():
            assert status in current_state_matrix["status_by_evidence_kind"].values()
            assert not assigned.intersection(codes)
            assigned.update(codes)
            assert all(current_state_matrix["states"][code]["currents"][current_id]["atlas_relation"] == status for code in codes)
        assert assigned == set(states["states"])
    detected = read("noaa-munster-eddy-state-20230601.json")
    historical_detections = [
        read("noaa-munster-eddy-state-20210601.json"),
        read("noaa-munster-eddy-state-20220601.json"),
    ]
    weekly = read("noaa-munster-eddy-weekly-join-20230601-20230607.json")
    weekly_states = read("noaa-munster-eddy-weekly-state-join-20230601-20230607.json")
    weekly_contours = read("noaa-munster-eddy-weekly-contour-state-join-20230601-20230607.json")
    ids = [item["id"] for item in currents["entries"]]
    assert len(ids) == len(set(ids)), "Duplicate current ID"
    assert marine_regions["source_record_count"] == len(marine_regions["records"]) == 52
    assert len({item["mrgid"] for item in marine_regions["records"]}) == 52
    assert sum(item["join_status"].startswith("matched") for item in marine_regions["records"]) == 41
    assert sum(item["join_status"] == "candidate_needs_review" for item in marine_regions["records"]) == 7
    assert sum(item["join_status"] in {"different_object_type", "generic_class", "sea_ice_drift", "circulation_system"} for item in marine_regions["records"]) == 4
    assert all(item["source_place_type"] == "Current" and item["record_url"].endswith(str(item["mrgid"])) for item in marine_regions["records"])
    assert all(item["osw_current_id"] in ids for item in marine_regions["records"] if item["osw_current_id"])
    assert set(ids) == set(index["entries"]), "Current ledger and map index differ"
    assert set(named_editorial_paths["paths"]) == {"agulhas-return", "kuroshio-extension", "tasman-front"}
    for current_id, path in named_editorial_paths["paths"].items():
        assert path["source"] in currents["sources"].values() and path["source_scope"]
        assert len(path["coordinates_lon_lat"]) >= 2
        assert all(-180 <= longitude <= 180 and -90 <= latitude <= 90 for longitude, latitude in path["coordinates_lon_lat"])
    assert "black-sea-rim" not in states["states"]["MEDI"]["current_locator_candidates"]
    assert set(index["nasa_current_scene_urls"]) == {item["almanac_current_id"] for item in nasa["objects"] if item.get("almanac_current_id")}
    current_by_id = {item["id"]: item for item in currents["entries"]}
    nasa_by_id = {item["id"]: item for item in nasa["objects"]}
    agulhas_return = current_by_id["agulhas-return"]
    assert agulhas_return["length_km"] is None
    assert agulhas_return["length_lower_bound_km"] == 3000
    assert current_by_id["agulhas"]["length_km"] is None
    assert current_by_id["agulhas"]["length_lower_bound_km"] == 1400
    agulhas_scope_variant = current_by_id["agulhas"]["source_reported_length_variants"][0]
    assert agulhas_scope_variant["length_km_approx"] == 1000
    assert agulhas_scope_variant["rank_eligible"] is False
    assert next(item for item in length_evidence["entries"] if item["current_id"] == "agulhas")["source_reported_length_variants"][0]["length_km_approx"] == 1000
    assert current_by_id["east-greenland"]["length_lower_bound_km"] == 2100
    assert current_by_id["east-greenland"]["length_km"] is None
    assert current_by_id["east-greenland"]["length_source"] == "east_greenland_extent"
    assert len(index["entries"]["agulhas-return"]["locators"]) == 3
    assert "agulhas-return" in states["states"]["SSTC"]["current_locator_candidates"]
    gulf_stream = current_by_id["gulf-stream"]
    gulf_system = current_by_id["gulf-stream-system"]
    assert gulf_system["component_current_ids"] == ["florida", "gulf-stream", "north-atlantic"]
    assert all(current_by_id[component]["part_of_system"] == "gulf-stream-system" for component in gulf_system["component_current_ids"])
    assert gulf_stream["length_km"] == 2500 and gulf_stream.get("length_lower_bound_km") is None
    assert gulf_stream["length_source"] == "regional_oceanography_atlantic"
    assert current_by_id["florida"]["length_km"] == 1200
    assert current_by_id["florida"]["length_source"] == "regional_oceanography_atlantic"
    assert {variant["source"] for variant in gulf_stream["source_extent_variants"]} == {"noaa_glossary", "noaa_gulf_stream_coast_pilot", "nasa_po2_western_boundary"}
    assert len(index["entries"]["gulf-stream-system"]["locators"]) == 3
    assert nasa_by_id["gulf-stream"]["related_current_system_id"] == "gulf-stream-system"
    assert "Florida Straits" in nasa_by_id["gulf-stream"]["name_scope_note"]
    assert gulf_stream["sampled_reach"]["alongflow_km_approx"] == 2000
    tasman_front = current_by_id["tasman-front"]
    assert tasman_front["length_km"] is None and tasman_front["length_source"] is None
    assert tasman_front["identity_scope_source"] == "east_australian_system_review"
    assert tasman_front["related_current_ids"] == ["east-australian"]
    assert len(index["entries"]["tasman-front"]["locators"]) == 2
    assert "tasman-front" in states["states"]["TASM"]["current_locator_candidates"]
    assert {code for code, state in states["states"].items() if "tasman-front" in state["editorial_named_current_line_crossings"]} == {"AUSE", "TASM"}
    assert {code for code, state in states["states"].items() if "agulhas-return" in state["editorial_named_current_line_crossings"]} == {"EAFR", "ISSG", "SSTC"}
    western_pacific_locators = {
        "mindanao-current": "SUND",
        "new-guinea-coastal-undercurrent": "ARCH",
        "new-ireland-coastal-undercurrent": "WARM",
        "solomon-island-coastal-undercurrent": "AUSE",
    }
    for current_id, code in western_pacific_locators.items():
        assert current_by_id[current_id]["name_source"] == "western_pacific_euc_pathways"
        assert current_by_id[current_id]["length_km"] is None
        assert current_id in states["states"][code]["current_locator_candidates"]
        assert current_state_matrix["currents"][current_id]["states_by_relation"]["editorial_locator_candidate"] == [code]
        assert tiles["current_joins"][current_id][0]["tile_id"] in {"level2_F_4", "level2_G_4"}
    assert current_by_id["mindanao-current"]["related_nasa_object_ids"] == ["indonesian-throughflow"]
    assert next(item for item in current_nasa_crosswalk["entries"] if item["current_id"] == "mindanao-current")["status"] == "independent_context"
    additional_currents = {
        "new-guinea-coastal-current": ("ARCH", "level2_G_4", "new_guinea_coastal_moorings"),
        "pacific-north-subsurface-countercurrent": ("PNEC", "level2_H_4", "pacific_subsurface_countercurrent_sections"),
        "pacific-south-subsurface-countercurrent": ("PNEC", "level2_H_4", "pacific_subsurface_countercurrent_sections"),
        "hiri-current": ("ARCH", "level2_G_5", "hiri_current_scope"),
    }
    for current_id, (code, tile_id, source) in additional_currents.items():
        assert current_by_id[current_id]["name_source"] == source and current_by_id[current_id]["length_km"] is None
        assert current_state_matrix["currents"][current_id]["states_by_relation"]["editorial_locator_candidate"] == [code]
        assert tiles["current_joins"][current_id][0]["tile_id"] == tile_id
    assert index["entries"]["new-guinea-coastal-current"]["time_behavior"] == "seasonally_reversing"
    assert all(index["entries"][current_id]["vertical_setting"] == "subsurface_core" for current_id in (
        "pacific-north-subsurface-countercurrent", "pacific-south-subsurface-countercurrent"
    ))
    marine_regions_by_id = {item["mrgid"]: item for item in marine_regions["records"]}
    assert marine_regions_by_id[30052]["join_status"] == "matched_alias_review"
    assert marine_regions_by_id[30052]["osw_current_id"] == "gaspe"
    assert marine_regions_by_id[30077]["join_status"] == "matched_alias_review"
    assert marine_regions_by_id[30077]["osw_current_id"] == "atlantic-equatorial-undercurrent"
    antilles_guiana = marine_regions_by_id[5398]
    assert antilles_guiana["join_status"] == "candidate_needs_review"
    assert antilles_guiana["review_status"] == "historical_continuity_disputed"
    assert antilles_guiana["source_point"] is None and antilles_guiana["osw_current_id"] is None
    assert antilles_guiana["review_source_url"].endswith("ingham.pdf")
    north_sea_bottom = marine_regions_by_id[30232]
    assert north_sea_bottom["join_status"] == "candidate_needs_review"
    assert north_sea_bottom["review_status"] == "gazetteer_geography_conflicts_with_cited_study"
    assert north_sea_bottom["source_point"] is None and north_sea_bottom["osw_current_id"] is None
    assert north_sea_bottom["review_source_url"].endswith("GSL.MEM.2002.022.01.10")
    for item in currents["entries"]:
        if source_id := item.get("source_mrgid"):
            source = marine_regions_by_id[source_id]
            assert source["osw_current_id"] == item["id"]
            assert source["record_url"] == item["name_source_url"]
            assert index["entries"][item["id"]]["locators"] == [source["source_point"]]
            assert item["length_km"] is None, item["id"]
        estimate = item["length_km"]
        lower_bound = item.get("length_lower_bound_km")
        hypothesis = item.get("hypothesized_length_km")
        assert sum(value is not None for value in (estimate, lower_bound, hypothesis)) <= 1, item["id"]
        assert estimate is None or estimate > 0, item["id"]
        assert lower_bound is None or lower_bound > 0, item["id"]
        assert hypothesis is None or hypothesis > 0, item["id"]
        assert (estimate is None and lower_bound is None) or item["length_source"] in currents["sources"], item["id"]
        if hypothesis is not None:
            assert item["hypothesis_source"] in currents["sources"]
            assert "hypothes" in item["length_scope"].lower()
        if item.get("length_bound_basis"):
            assert lower_bound is not None and item["length_source"] in currents["sources"]
        for variant in item.get("source_extent_variants", []):
            assert variant["source"] in currents["sources"] and variant["definition"] and variant["upstream"] and variant["downstream"]
        if item["id"] == "east-australian":
            assert lower_bound == 1800 and lower_bound < 17 * 111.2
        if reach := item.get("sampled_reach"):
            assert reach["source"] in currents["sources"]
            assert reach["alongflow_km_approx"] > 0 and reach["region"] and reach["scope"]
        if item.get("related_current_ids"):
            assert all(related_id in current_by_id and related_id != item["id"] for related_id in item["related_current_ids"])
        for object_id in item.get("related_nasa_object_ids", []):
            assert object_id in nasa_by_id
            assert item["id"] in {context["current_id"] for context in nasa_by_id[object_id].get("external_current_context", [])}
        if item.get("component_current_ids"):
            assert len(item["component_current_ids"]) == len(set(item["component_current_ids"]))
            assert all(current_by_id[component]["part_of_system"] == item["id"] for component in item["component_current_ids"])
        if item.get("part_of_system"):
            assert item["id"] in current_by_id[item["part_of_system"]]["component_current_ids"]
        if review := item.get("identity_review"):
            related = current_by_id[review["related_current_id"]]
            assert related["identity_review"]["related_current_id"] == item["id"]
            assert review["note"]
        if survey := item.get("survey_section"):
            assert item["length_km"] is None and survey["source"] in currents["sources"]
            south, north = survey["latitude_range"]
            assert -90 <= south < north <= 90
            assert survey["transport_sv_approx"] > 0 and survey["period"]
            assert survey["direction"] in {"eastward", "westward", "northward", "southward"}
            assert index["entries"][item["id"]]["locators"] == [[survey["longitude"], (south + north) / 2]]
        if section := item.get("section_observation"):
            assert item["length_km"] is None and item.get("length_lower_bound_km") is None
            assert section["source"] in currents["sources"]
            assert section.get("method_note", "Source-reported section measurement.")
            if "reference_place" in section:
                assert section["reference_point_source"] in currents["sources"]
                assert len(section["reference_point"]) == 2
                assert section["distance_from_coast_nautical_miles"] == [1, 5]
                longitude, latitude = index["entries"][item["id"]]["locators"][0]
                reference_longitude, reference_latitude = section["reference_point"]
                assert abs(longitude - reference_longitude) < 0.3 and abs(latitude - reference_latitude) < 0.2
                continue
            assert ("transport_sv" in section) != ("transport_layers_sv" in section)
            if "transport_sv" in section:
                assert section["transport_sv"] > 0
            else:
                assert section["transport_layers_sv"] and all(layer["value"] > 0 and layer["uncertainty"] >= 0 and layer["layer"] for layer in section["transport_layers_sv"])
            assert section["direction"] in {"eastward", "westward", "southward", "northward"}
            if "latitude_range" in section:
                assert "longitude_range" not in section and section["latitude_range"][0] < section["latitude_range"][1]
                assert section["meridional_width_km"] > 0
                point = [section["longitude"], sum(section["latitude_range"]) / 2]
            else:
                assert "longitude_range" in section and section["longitude_range"][0] < section["longitude_range"][1]
                assert section.get("transport_uncertainty_sv", 0) >= 0
                point = [sum(section["longitude_range"]) / 2, section["latitude"]]
            assert index["entries"][item["id"]]["locators"] == [point]
    for key, item in index["entries"].items():
        for axis in ("identity_level", "setting", "time_behavior"):
            assert item[axis] in taxonomy["axes"][axis], (key, axis, item[axis])
        if "vertical_setting" in item:
            assert item["vertical_setting"] in taxonomy["axes"]["vertical_setting"], key
        assert item["locators"], f"No map locator for {key}"
        for longitude, latitude in item["locators"]:
            assert -180 <= longitude <= 180 and -90 <= latitude <= 90, key
    numbers = [item["source_number"] for item in eddies["entries"]]
    assert len(numbers) == len(set(numbers)), "Duplicate source eddy number"
    assert eddy_names["numbered_event_count"] == len(numbers)
    assert eddy_names["secondary_name_count"] == sum(bool(item["secondary_name"]) for item in eddies["entries"])
    assert len(eddy_names["entries"]) == len(numbers) + eddy_names["secondary_name_count"]
    assert len({item["id"] for item in eddy_names["entries"]}) == len(eddy_names["entries"])
    assert len({item["name"].casefold() for item in eddy_names["entries"]}) == len(eddy_names["entries"])
    by_event = {item["source_number"]: item for item in eddies["entries"]}
    for item in eddy_names["entries"]:
        source = by_event[item["source_number"]]
        if item["role"] == "primary":
            assert item["name"] == source["name"] and item["initial_separation"] == source["initial_separation"]
            assert item["related_primary_id"] is None
        else:
            assert item["role"] == "secondary" and item["name"] == source["secondary_name"]
            assert item["initial_separation"] is None
            assert item["related_primary_id"] == f"loop-{item['source_number']:02d}-primary"
    assert loop_context["name_count"] == len(loop_context["entries"]) == len(eddy_names["entries"])
    assert {item["id"] for item in loop_context["entries"]} == {item["id"] for item in eddy_names["entries"]}
    assert loop_context["state_locator_candidates"] == ["CAMR"]
    assert loop_context["states"] == {"CAMR": [item["id"] for item in loop_context["entries"]]}
    assert loop_context["primary_separations_in_model_years"] == 8
    assert loop_context["secondary_names_linked_to_model_year_events"] == 4
    assert loop_context["supplemental_position_count"] == 1
    assert loop_context["dated_map_presence_count"] == 1
    assert loop_context["states_with_published_positions"] == {"CAMR": ["loop-77-primary"]}
    assert loop_context["crop_date_alignment_status"] == nasa_crop_timeline["alignment_status"] == "cross_release_inference"
    assert loop_context["crop_date_window_inferred"] == [nasa_crop_timeline["date_start"], nasa_crop_timeline["date_end"]]
    for item in loop_context["entries"]:
        source = next(name for name in eddy_names["entries"] if name["id"] == item["id"])
        assert item["name"] == source["name"] and item["role"] == source["role"]
        assert item["independent_separation_date"] == source["initial_separation"]
        assert item["nasa_object_relation"] == "related_described_class_only"
        assert item["nasa_object_id"] == "gulf-of-mexico-loop-eddies"
        assert item["state_relation"] == "shared_source_region_gateway_only"
        assert item["nasa_region_movie"]["relation"] == "regional_context_only"
        assert item["nasa_region_movie"]["url"] == tiles["named_loop_current_eddies_region_join"]["url"]
        assert item["state_locator_candidates"] == ["CAMR"]
        if item["role"] == "secondary":
            assert item["independent_separation_date"] is None
    berek_position = next(item for item in loop_context["entries"] if item["id"] == "loop-77-primary")["published_observed_position"]
    assert berek_position["coordinate"] == [-89, 26]
    assert berek_position["state_point_candidates"] == ["CAMR"]
    assert berek_position["nasa_region_movie"]["tile_id"] == "level2_B_3"
    assert "exact center date not stated" in berek_position["period"]
    berek_presence = next(item for item in loop_context["entries"] if item["id"] == "loop-77-primary")["published_dated_map_presence"]
    assert berek_presence["date"] == "2023-12-21"
    assert berek_presence["nasa_crop_seek"]["estimated_seconds"] == nasa_crop_timeline["dates"]["2023-12-21"]["estimated_crop_seconds"]
    assert berek_presence["nasa_crop_seek"]["relation"] == "same_date_geographic_context_only"
    assert berek_presence["nasa_model_date_relation"] == "sos_date_list_overlap_identity_unverified"
    assert index["named_loop_current_eddies"]["location_evidence"] == "source_region_only"
    franklin = next(item for item in eddy_names["entries"] if item["id"] == "loop-55-primary")
    assert franklin["name"] == "Franklin" and franklin["initial_separation"] == "2010-06-09"
    assert franklin["external_evidence"]["relation"] == "independent_named_2010_ring_account"
    assert franklin["external_evidence"]["source_url"] == "https://repository.library.noaa.gov/view/noaa/28993"
    geography_by_id = {item["id"]: item for item in eddy_geography["entries"]}
    assert len(geography_by_id) == len(eddy_geography["entries"]) == 35
    for eddy_id, polarity in (("mindanao-eddy-region", "cyclonic"), ("halmahera-eddy-region", "anticyclonic")):
        eddy = geography_by_id[eddy_id]
        assert eddy["identity_level"] == "recurrent_eddy_region" and eddy["polarity"] == polarity
        assert eddy["related_current_id"] == "pacific-north-equatorial-countercurrent"
        assert eddy["activity_region"]["source"] == "western_pacific_eddy_activity_regions"
        assert eddy["activity_region"]["role"] == "study_defined_primary_activity_box_not_eddy_footprint"
        assert eddy_geography_join["entries"][eddy_id]["state_locator_candidates"] == ["SUND"]
        assert eddy_geography_join["entries"][eddy_id]["nasa_region_movie"]["tile_id"] == "level2_F_4"
    new_guinea_eddy = geography_by_id["new-guinea-eddy-region"]
    assert new_guinea_eddy["related_current_id"] == "new-guinea-coastal-undercurrent"
    assert new_guinea_eddy["locator"] == [138, 2] and new_guinea_eddy["polarity"] == "anticyclonic"
    assert new_guinea_eddy["supporting_sources"] == ["new_guinea_eddy_intermediate_observations", "new_guinea_eddy_name_variant"]
    assert eddy_geography_join["entries"]["new-guinea-eddy-region"]["state_locator_candidates"] == ["WARM"]
    assert eddy_geography_join["entries"]["new-guinea-eddy-region"]["nasa_region_movie"]["depth_relation"] == "subsurface_visibility_unverified"
    assert geography_by_id["meddies-family"]["related_current_id"] == "mediterranean-undercurrent"
    assert geography_by_id["meddy-ulla-1997"]["observed_center"]["coordinate"] == [-11.5, 45]
    for eddy_id in ("cyprus-eddy-region", "shikmona-eddy-region", "latakia-eddy-region"):
        assert eddy_geography_join["entries"][eddy_id]["state_locator_candidates"] == ["MEDI"]
        assert eddy_geography_join["entries"][eddy_id]["explicit_state_exclusions"] == ["REDS"]
    assert geography_by_id["latakia-eddy-region"]["polarity"] == "unresolved"
    assert "reversals" in geography_by_id["latakia-eddy-region"]["identity_note"]
    assert {"ana-2004", "eliza-2007", "jeannette-2012"} <= set(geography_by_id)
    assert "AS2" in geography_by_id["jeannette-2012"]["identity_note"]
    cubans = geography_by_id["cuba-anticyclones-family"]
    assert cubans["identity_level"] == "eddy_family" and cubans["source_activity_periods"] == 5
    assert cubans["related_nasa_object_id"] == "gulf-of-mexico-loop-eddies"
    assert set(geography_by_id) == set(eddy_geography_join["entries"])
    assert set(eddy_geography_join["states"]) == set(states["states"])
    nasa_tile_ids = {item["id"] for item in tiles["tiles"]}
    for eddy_id, item in geography_by_id.items():
        assert item["identity_level"] in taxonomy["axes"]["identity_level"]
        assert item["time_behavior"] in taxonomy["axes"]["time_behavior"]
        assert item["object_type"] in {"eddy", "ring"} and item["polarity"] in taxonomy["axes"]["polarity"]
        assert item["source"] in eddy_geography["sources"] and item["locator_basis"]
        if item["nasa_identified"]:
            assert item["identity_level"] == "eddy_family"
            assert item["nasa_object_id"] in {object_["id"] for object_ in nasa["objects"]}
        else:
            assert not item.get("nasa_object_id")
        if related_nasa := item.get("related_nasa_object_id"):
            assert related_nasa in {object_["id"] for object_ in nasa["objects"]}
            assert not item["nasa_identified"]
        longitude, latitude = item["locator"]
        assert -180 <= longitude <= 180 and -90 <= latitude <= 90
        if sample := item.get("sample_site"):
            assert sample["source_classification"] == "core" and sample["depth_db"] > 0
            assert sample["longitude_east_0_360"] - 360 == longitude and sample["latitude"] == latitude
            assert int(sample["date"][:4]) == item["event_year"]
            assert item["identity_level"] == "individual_eddy"
        if observed := item.get("observed_center"):
            assert item["identity_level"] == "individual_eddy"
            assert observed["coordinate"] == item["locator"] and observed["period"] and observed["method"]
        if formation := item.get("formation"):
            assert formation["coordinate"] and formation["period"]
        if track_period := item.get("reported_track_period"):
            assert item["identity_level"] == "individual_eddy"
            assert track_period["start"] < track_period["end"]
        if item.get("identity_note"):
            assert len(item["identity_note"]) > 30
        assert all(key in eddy_geography["sources"] for key in item.get("supporting_sources", []))
        if box := item.get("activity_region"):
            assert box["west"] < box["east"] and box["south"] < box["north"]
            assert box["west"] <= longitude <= box["east"] and box["south"] <= latitude <= box["north"]
            assert box["source"] in eddy_geography["sources"]
            assert box["role"] == "study_defined_primary_activity_box_not_eddy_footprint"
        if fate := item.get("reported_fate"):
            assert fate["type"] in {"last_confirmed_alive", "dissipation_period"} and fate["note"]
            assert ("date" in fate) != ("period" in fate)
        relation = eddy_geography_join["entries"][eddy_id]
        class_context = relation["nasa_class_context"]
        agulhas_member = eddy_id == "agulhas-rings-family" or item.get("member_of") == "agulhas-rings-family"
        assert class_context["generic_class_id"] == "ocean-eddies"
        assert class_context["generic_relation"] == "osw_taxonomic_class_context_only"
        assert class_context["specific_class_id"] == ("agulhas-rings" if agulhas_member else None)
        assert class_context["specific_relation"] == ("same_named_family_class" if eddy_id == "agulhas-rings-family" else "external_member_of_nasa_named_family" if agulhas_member else None)
        assert class_context["individual_nasa_identity_claim"] is False
        assert relation["nasa_region_movie"]["tile_id"] in nasa_tile_ids
        assert relation["nasa_region_movie"]["relation"] == "regional_context_only"
        assert relation["nasa_region_movie"]["depth_relation"] == ("subsurface_visibility_unverified" if item.get("vertical_evidence") else "not_assessed")
        assert relation["nasa_region_movie"]["model_period"] == tiles["model_period"]
        assert relation["nasa_region_movie"]["crop_date_start"] == nasa_crop_timeline["date_start"]
        assert relation["nasa_region_movie"]["crop_date_end"] == nasa_crop_timeline["date_end"]
        assert relation["nasa_region_movie"]["crop_date_alignment_status"] == "cross_release_inference"
        assert relation["explicit_state_exclusions"] == sorted(item.get("state_exclusions", []))
        assert all(eddy_id in eddy_geography_join["states"][code] for code in relation["state_locator_candidates"])
        if item["basin"] == "Black Sea":
            assert not relation["state_locator_candidates"] and {"MEDI", "REDS"} <= set(relation["explicit_state_exclusions"])
        if item["identity_level"] == "individual_eddy":
            assert item["member_of"] in geography_by_id and item["event_year"] > 0
            assert relation["nasa_region_movie"]["temporal_relation"] == "outside_model_period"
        elif item.get("source_observed_months"):
            assert all(len(month) == 7 and month[:4].isdigit() for month in item["source_observed_months"])
            assert relation["nasa_region_movie"]["temporal_relation"] == "source_observations_before_inferred_crop_window"
        else:
            assert relation["nasa_region_movie"]["temporal_relation"] == "recurring_name_no_generation_match"
    for code, eddy_ids in eddy_geography_join["states"].items():
        assert all(code in eddy_geography_join["entries"][eddy_id]["state_locator_candidates"] for eddy_id in eddy_ids)
    assert sum(bool(row["nasa_class_context"]["specific_class_id"]) for row in eddy_geography_join["entries"].values()) == 8
    published_loop = read("named-loop-eddy-published-observations.json")["entries"]
    assert eddy_inventory["record_count"] == len(eddy_inventory["entries"]) == len(eddy_names["entries"]) + len(eddy_geography["entries"]) + len(published_loop) == 136
    assert eddy_inventory["published_loop_record_count"] == len(published_loop) == 5
    assert eddy_inventory["horizon_name_count"] == len(eddy_names["entries"])
    assert eddy_inventory["horizon_numbered_event_count"] == eddy_names["numbered_event_count"]
    assert eddy_inventory["other_named_record_count"] == len(eddy_geography["entries"])
    assert eddy_inventory["source_dated_other_individual_count"] == sum(item["identity_level"] == "individual_eddy" for item in eddy_geography["entries"])
    inventory_by_id = {item["id"]: item for item in eddy_inventory["entries"]}
    assert len(inventory_by_id) == eddy_inventory["record_count"]
    for eddy_id in ("mindanao-eddy-region", "halmahera-eddy-region"):
        inventory_row = inventory_by_id[f"geography:{eddy_id}"]
        assert inventory_row["related_current_id"] == "pacific-north-equatorial-countercurrent"
        assert inventory_row["activity_region"]["source_url"] == eddy_geography["sources"]["western_pacific_eddy_activity_regions"]
    assert inventory_by_id["geography:new-guinea-eddy-region"]["supporting_source_urls"] == [eddy_geography["sources"][key] for key in new_guinea_eddy["supporting_sources"]]
    assert set(inventory_by_id) == ({f"horizon:{item['id']}" for item in eddy_names["entries"]} |
                                    {f"geography:{item['id']}" for item in eddy_geography["entries"]} |
                                    {item["eddy_id"] for item in published_loop})
    for item in published_loop:
        row = inventory_by_id[item["eddy_id"]]
        assert row["source_collection"] == "published_loop_current"
        assert row["source_url"] == item["source_url"] and row["name"] == item["name"]
        assert row["date_evidence"] == {"observation_start": item["observation_start"],
                                        "observation_end": item["observation_end"]}
        assert row["independent_event_observations"] == item.get("independent_event_observations", [])
        assert row["source_event_number"] is None and row["source_event_date"] is None
        assert row["state_locator_candidates"] == (["CAMR"] if item["eddy_id"] in {"published:kraken-2013", "published:cameron-2009-observed"} else [])
        assert row["nasa_individual_identity_claim"] is False
        if item["eddy_id"] == "published:kraken-2013":
            assert row["state_relation"] == "figure_derived_red_curve_candidate_only"
            assert row["figure_state_audit"]["physical_relation"].endswith("whole_ring_containment_unresolved")
        assert "possible_same_ring_as_horizon_id" not in row
        assert "horizon:loop-" not in json.dumps(row, ensure_ascii=False).lower()
        if item["eddy_id"] == "published:cameron-2009-observed":
            assert row["published_observed_position"]["state_center_candidates"] == ["CAMR"]
            assert row["state_relation"] == "published_dated_center_point_candidate_only"
        if item["eddy_id"] == "published:darwin-2009-observed":
            assert row["published_observed_position"] is None
            assert row["near_center_mooring"]["relation"] == "mooring_near_eddy_center_not_exact_center"
    for item in eddy_names["entries"]:
        row = inventory_by_id[f"horizon:{item['id']}"]
        context = next(entry for entry in loop_context["entries"] if entry["id"] == item["id"])
        assert row["name"] == item["name"] and row["source_event_date"] == item["initial_separation"]
        assert row["date_evidence"]["initial_separation"] == item["initial_separation"]
        assert row["date_evidence"]["independent_secondary_date"] == (item["initial_separation"] if item["role"] == "primary" else None)
        assert row["locator_evidence_type"] == "shared_source_region_gateway"
        assert row["specific_nasa_class_id"] == context["nasa_object_id"] == "gulf-of-mexico-loop-eddies"
        assert row["state_locator_candidates"] == context["state_locator_candidates"]
        assert row["atlas_anchor"] == f"#eddy-{item['id']}"
        assert row["nasa_individual_identity_claim"] is False
    for item in eddy_geography["entries"]:
        row = inventory_by_id[f"geography:{item['id']}"]
        context = eddy_geography_join["entries"][item["id"]]
        assert row["name"] == item["name"] and row["identity_level"] == item["identity_level"]
        assert row["date_evidence"]["formation_period"] == item.get("formation", {}).get("period")
        assert row["date_evidence"]["observed_center_period"] == item.get("observed_center", {}).get("period")
        assert row["date_evidence"]["sample_date"] == item.get("sample_site", {}).get("date")
        assert row["date_evidence"]["reported_track_period"] == item.get("reported_track_period")
        assert row["date_evidence"]["reported_encounter"] == item.get("reported_encounter")
        assert row["external_track_identifier"] == item.get("external_track_identifier")
        assert row["locator_evidence_type"] == ("sample_site" if item.get("sample_site") else "observed_center" if item.get("observed_center") else "reported_event_point" if item.get("formation") else "editorial_region")
        assert row["source_url"] == eddy_geography["sources"][item["source"]]
        assert row["specific_nasa_class_id"] == context["nasa_class_context"]["specific_class_id"]
        assert row["state_locator_candidates"] == context["state_locator_candidates"]
        assert row["additional_observed_position_joins"] == context["additional_observed_position_joins"]
        assert row["atlas_anchor"] == f"#eddy-geography-{item['id']}"
        assert row["nasa_individual_identity_claim"] is False
    lilian = inventory_by_id["geography:lilian-2006"]
    assert lilian["external_track_identifier"]["track_label"] == 147078
    assert lilian["reported_travel_km_lower_bound"] == 5500
    assert lilian["state_locator_candidates"] == ["BRAZ"]
    assert lilian["specific_nasa_class_id"] == "agulhas-rings"
    eddy_w = inventory_by_id["geography:agulhas-eddy-w-2000"]
    assert eddy_w["state_locator_candidates"] == ["BENG"]
    assert eddy_w["specific_nasa_class_id"] == "agulhas-rings"
    assert eddy_geography_join["entries"]["agulhas-eddy-w-2000"]["nasa_region_movie"]["temporal_relation"] == "outside_model_period"
    lilian_first_detection = eddy_geography_join["entries"]["lilian-2006"]["additional_observed_position_joins"]
    assert len(lilian_first_detection) == 1
    assert lilian_first_detection[0]["date"] is None
    assert lilian_first_detection[0]["coordinate"] == [14.6, -39.5]
    assert lilian_first_detection[0]["state_center_candidates"] == ["SSTC"]
    agulhas_census = inventory_by_id["geography:agulhas-rings-family"]["independent_source_census"]
    assert agulhas_census["initial_shed_rings"] == 140
    assert agulhas_census["long_lived_walvis_crossing_tracks"] == 74
    assert agulhas_census["source_url"].endswith("Guerra_et_al_18.pdf")
    jeannette_endpoint = eddy_geography_join["entries"]["jeannette-2012"]["additional_observed_position_joins"]
    assert len(jeannette_endpoint) == 1
    assert jeannette_endpoint[0]["coordinate"] == [-35, -21]
    assert jeannette_endpoint[0]["date"] == "2015-12-27"
    assert jeannette_endpoint[0]["state_center_candidates"] == ["BRAZ"]
    assert eddy_geography_join["states_with_additional_observed_positions"]["BRAZ"] == [
        {"eddy_id": "jeannette-2012", "date": "2015-12-27", "period": None, "evidence_type": "reported_track_endpoint"}
    ]
    release_ids = {item["id"] for item in nasa["releases"]}
    assert nasa_release_media["release_count"] == len(release_ids)
    assert {item["release_id"] for item in nasa_release_media["releases"]} == release_ids
    assert nasa_release_media["movie_listing_count"] == sum(len(item["movies"]) for item in nasa_release_media["releases"])
    for media_release in nasa_release_media["releases"]:
        source = next(item for item in nasa["releases"] if item["id"] == media_release["release_id"])
        assert media_release["source_page"] == source["url"]
        assert media_release["api_url"].endswith(f"/{media_release['page_id']}")
        assert len({movie["url"] for movie in media_release["movies"]}) == len(media_release["movies"])
        assert all(movie["url"].startswith("https://svs.gsfc.nasa.gov/vis/") for movie in media_release["movies"])
    object_ids = [item["id"] for item in nasa["objects"]]
    media_ids = [item["id"] for item in nasa_media["assets"]]
    assert len(media_ids) == len(set(media_ids))
    for asset in nasa_media["assets"]:
        assert asset["source_release_id"] in release_ids
        assert asset["source_page"] == next(release["url"] for release in nasa["releases"] if release["id"] == asset["source_release_id"])
        assert asset["relation"] in {"feature_specific", "class_example"}
        assert asset["object_ids"] and set(asset["object_ids"]) <= set(object_ids)
        assert asset["movie_url"].startswith("https://svs.gsfc.nasa.gov/vis/")
        assert all(asset["source_release_id"] in next(item["nasa_sources"] for item in nasa["objects"] if item["id"] == object_id) for object_id in asset["object_ids"])
    assert set(nasa_crosswalk["objects"]) == set(object_ids)
    assert set(nasa_crosswalk["states"]) == set(states["states"])
    assert nasa_matrix["object_count"] == len(object_ids)
    assert nasa_matrix["state_count"] == len(states["states"])
    assert nasa_matrix["pair_count"] == len(object_ids) * len(states["states"])
    assert set(nasa_matrix["states"]) == set(states["states"])
    matrix_linked = 0
    matrix_contextual = 0
    for code, state_row in nasa_matrix["states"].items():
        assert state_row["name"] == states["states"][code]["name"]
        assert set(state_row["objects"]) == set(object_ids)
        for object_id, relation in state_row["objects"].items():
            expected = [kind for kind in nasa_matrix["status_precedence"] if code in nasa_crosswalk["objects"][object_id]["state_evidence"][kind]]
            assert relation["evidence_kinds"] == expected
            assert relation["atlas_relation"] == (nasa_matrix["status_by_evidence_kind"][expected[0]] if expected else "unresolved")
            assert relation["physical_relation"] == "unknown_no_nasa_feature_footprint"
            current_id = nasa_crosswalk["objects"][object_id]["almanac_current_id"]
            source_arrows = (current_state_matrix["states"][code]["currents"][current_id]["cartographic_source_arrow_ids"]
                             if current_id else {"stable": [], "width_sensitive": []})
            assert relation["cartographic_source_arrow_ids"] == source_arrows
            for member in relation["contextual_members"]:
                assert member["object_id"] in object_ids
                assert member["relation"] in {"nasa_named_example", "nasa_narrated_part_of_system", "osw_taxonomic_child"}
                assert member["evidence_kinds"] == [kind for kind in nasa_matrix["status_precedence"] if code in nasa_crosswalk["objects"][member["object_id"]]["state_evidence"][kind]]
                assert member["evidence_kinds"]
            matrix_linked += bool(expected)
            matrix_contextual += bool(relation["contextual_members"])
        assert state_row["atlas_linked_object_count"] == sum(bool(relation["evidence_kinds"]) for relation in state_row["objects"].values())
    assert nasa_matrix["atlas_linked_pair_count"] == matrix_linked
    assert nasa_matrix["contextual_pair_count"] == matrix_contextual == 26
    assert nasa_matrix["states"]["GFST"]["objects"]["gulf-stream"]["cartographic_source_arrow_ids"]["stable"] == [57, 58]
    assert nasa_matrix["states"]["NAST W"]["objects"]["gulf-stream"]["cartographic_source_arrow_ids"]["width_sensitive"] == [58]
    assert {member["object_id"] for member in nasa_matrix["states"]["GFST"]["objects"]["global-overturning"]["contextual_members"]} == {"gulf-stream", "gulf-stream-deep-return"}
    assert [member["object_id"] for member in nasa_matrix["states"]["SSTC"]["objects"]["ocean-eddies"]["contextual_members"]] == ["agulhas-rings"]
    assert nasa_matrix["states"]["SANT"]["objects"]["ocean-eddies"]["contextual_members"] == []
    with (RESEARCH / "ocean-object-classification.csv").open(encoding="utf-8", newline="") as source:
        registry_ids = {item["object_id"] for item in csv.DictReader(source)}
    assert len(object_ids) == len(set(object_ids)), "Duplicate NASA object"
    assert set(nasa_evidence["objects"]) == set(object_ids)
    assert nasa_evidence["relationship_count"] == sum(len(item["nasa_sources"]) for item in nasa["objects"])
    assert nasa_evidence["relationship_count"] == 39
    assert nasa_crosswalk["objects"]["red-sea-saline-overflow"]["state_evidence"]["object_locator_candidates"] == ["REDS"]
    assert nasa_crosswalk["objects"]["persian-gulf-saline-overflow"]["state_evidence"]["object_locator_candidates"] == ["ARAB"]
    assert len(nasa_properties["properties"]) == 15
    cold_core_polarity = next(item for item in nasa_properties["properties"] if item["object_id"] == "gulf-stream-cold-cores" and item["quantity"] == "polarity_description")
    assert cold_core_polarity["relation"] == "source_specific_majority_claim"
    assert cold_core_polarity["value"] == "anticyclonic"
    assert cold_core_polarity["review_status"] == "scope_discrepancy_requires_object_definition"
    assert cold_core_polarity["review_source_url"].startswith("https://doi.org/")
    assert "no individual eddy is classified" in cold_core_polarity["scope_note"]
    for property in nasa_properties["properties"]:
        assert property["object_id"] in object_ids and property["quantity"] != "current_length"
        assert property["scope_note"] and property["source_release_id"] in release_ids
        evidence = nasa_evidence["objects"][property["object_id"]][property["source_release_id"]]
        assert property["source_url"].split("#")[0].rstrip("/") == evidence["source_url"].split("#")[0].rstrip("/")
        if property.get("source_location") == "page_introduction":
            assert property["source_url"] == next(release["url"] for release in nasa["releases"] if release["id"] == property["source_release_id"])
        elif property["source_release_id"] == "po2-narrated":
            assert property["cue_numbers"] and set(property["cue_numbers"]) <= set(evidence["cue_numbers"])
        else:
            assert property["source_url"].split("#")[-1] == evidence["source_url"].split("#")[-1]
    audit_rows = {item["id"]: item for item in nasa_audit["releases"]}
    assert set(audit_rows) == release_ids, "NASA source audit does not cover every release"
    discovery = nasa_audit["series_discovery"]
    shared_post = nasa_audit["user_shared_post_provenance"]
    canonical_release = next(item for item in nasa["releases"] if item["id"] == shared_post["canonical_nasa_release_id"])
    assert shared_post["canonical_nasa_url"] == canonical_release["url"]
    assert shared_post["source_relation"].startswith("likely_cropped_excerpt")
    assert shared_post["attribution_rule"] and shared_post["comparison_basis"]
    assert discovery["tagged_count"] == len(discovery["tagged_release_ids"]) == 4
    release_page_numbers = {int(item["url"].rstrip("/").rsplit("/", 1)[-1]) for item in nasa["releases"]}
    assert set(discovery["tagged_release_ids"] + discovery["additional_related_release_ids"]) == release_page_numbers
    assert all(exclusion["page_id"] not in release_page_numbers and exclusion["url"].startswith("https://svs.gsfc.nasa.gov/") and exclusion["reason"]
               for exclusion in discovery["reviewed_related_exclusions"])
    for release in nasa["releases"]:
        row = audit_rows[release["id"]]
        assert row["url"] in {release["url"], release.get("transcript")}, release["id"]
        expected = {item["id"] for item in nasa["objects"] if release["id"] in item["nasa_sources"]}
        assert set(row["object_ids"]) == expected, release["id"]
    coverage_rows = {item["object_id"]: item for item in nasa_coverage["objects"]}
    assert len(coverage_rows) == len(nasa["objects"]) and set(coverage_rows) == {item["id"] for item in nasa["objects"]}
    assert nasa_coverage["summary"]["audited_releases"] == len(nasa["releases"])
    assert nasa_coverage["summary"]["source_evidence_edges"] == sum(len(item) for item in nasa_evidence["objects"].values()) == 39
    assert nasa_coverage["summary"]["source_phrase_checks"] == nasa_evidence["relationship_count"]
    assert nasa_coverage["summary"]["individual_media_group_phrase_checks"] == sum(
        len(edge.get("media_group_ids", [])) for edges in nasa_evidence["objects"].values() for edge in edges.values()
    )
    assert nasa_coverage["summary"]["narration_passage_checks"] == sum(
        edge["evidence_kind"] == "narration_cues" for edges in nasa_evidence["objects"].values() for edge in edges.values()
    )
    assert nasa_coverage["summary"]["objects_with_editorial_locators"] == sum(item["locator"] is not None for item in nasa["objects"]) == 16
    assert nasa_coverage["summary"]["unlocated_classes_or_processes"] == 6
    assert nasa_coverage["summary"]["objects_with_media_navigation"] == len(nasa["objects"])
    assert nasa_coverage["summary"]["coverage_issue_count"] == 0
    assert nasa_coverage["summary"]["motion_forms_classified"] == len(nasa["objects"])
    assert nasa_coverage["summary"]["nasa_regional_crop_movies"] == len(tiles["tiles"])
    assert set(nasa_forms["objects"]) == {item["id"] for item in nasa["objects"]}
    assert set(nasa_forms["objects"].values()) <= set(nasa_forms["forms"])
    class_edges = nasa_forms["class_relations"]
    assert len(class_edges) == len({edge["child_id"] for edge in class_edges}) == 5
    assert {edge["parent_id"] for edge in class_edges} == {"ocean-eddies"}
    assert {edge["child_id"] for edge in class_edges} == {"kuroshio-eddies", "agulhas-rings", "western-boundary-rings", "gulf-stream-cold-cores", "gulf-of-mexico-loop-eddies"}
    assert all(nasa_forms["objects"][edge["child_id"]] in {"eddy_class", "ring_class"} and nasa_forms["objects"][edge["parent_id"]] == "eddy_class" for edge in class_edges)
    assert taxonomy["axes"]["motion_form"]["vocabulary"] == "research/nasa-perpetual-ocean-motion-forms.json"
    assert nasa_forms["objects"]["agulhas-rings"] == "ring_class"
    assert nasa_forms["objects"]["global-overturning"] == "circulation_system"
    assert nasa_forms["objects"]["upwelling"] == nasa_forms["objects"]["downwelling"] == "vertical_process"
    for item in nasa["objects"]:
        row = coverage_rows[item["id"]]
        assert row["source_release_ids"] == item["nasa_sources"]
        assert row["motion_form"] == nasa_forms["objects"][item["id"]]
        assert row["source_evidence_count"] == len(nasa_evidence["objects"][item["id"]])
        assert row["source_phrase_check_count"] == row["source_evidence_count"]
        assert row["state_locator_candidates"] == nasa_crosswalk["objects"][item["id"]]["state_evidence"]["object_locator_candidates"]
        assert row["has_editorial_locator"] == (item["locator"] is not None)
        assert row["primary_media_route"] != "missing" and row["primary_media_url"] and row["coverage_issue"] is None
    for item in nasa["objects"]:
        assert item["support"] in nasa["support_levels"]
        assert item["nasa_sources"] and set(item["nasa_sources"]) <= release_ids
        assert item["osw_object_id"] in registry_ids
        relation = nasa_crosswalk["objects"][item["id"]]
        assert relation["release_ids"] == item["nasa_sources"]
        assert relation["release_urls"] == [next(release["url"] for release in nasa["releases"] if release["id"] == release_id) for release_id in item["nasa_sources"]]
        assert set(nasa_evidence["objects"][item["id"]]) == set(item["nasa_sources"])
        assert relation["release_evidence"] == nasa_evidence["objects"][item["id"]]
        assert relation["reported_properties"] == [property for property in nasa_properties["properties"] if property["object_id"] == item["id"]]
        for release_id, source in relation["release_evidence"].items():
            assert source["support_pattern"] and len(source["support_pattern"]) >= 3
            if release_id == "po2-narrated":
                assert source["evidence_kind"] == "narration_cues"
                assert source["source_url"] == next(release["transcript"] for release in nasa["releases"] if release["id"] == release_id)
                assert source["cue_numbers"] == sorted(set(source["cue_numbers"]))
                assert [cue["number"] for cue in source["cue_times"]] == source["cue_numbers"]
                assert all(0 < cue["start_seconds"] < cue["end_seconds"] <= 317 for cue in source["cue_times"])
                assert any(cue["start_seconds"] < item["narrated_end_s"] and cue["end_seconds"] > item["narrated_start_s"] for cue in source["cue_times"])
            else:
                assert source["evidence_kind"] == "nasa_media_group"
                assert source["media_group_ids"]
                assert source["source_url"] == source["media_group_urls"][0]
                assert all(url.startswith(next(release["url"] for release in nasa["releases"] if release["id"] == release_id) + "#media_group_") for url in source["media_group_urls"])
        assert relation["almanac_current_id"] == item.get("almanac_current_id")
        assert relation["parent_current_id"] == (next(parent.get("almanac_current_id") for parent in nasa["objects"] if parent["id"] == item["parent_id"]) if item.get("parent_id") else None)
        assert relation["external_current_context"] == item.get("external_current_context", [])
        for context in relation["external_current_context"]:
            current = current_by_id[context["current_id"]]
            assert item["id"] in current["related_nasa_object_ids"]
            assert context["relation"] in {"independently_named_downstream_flow", "independently_named_upstream_feeder"}
            assert context["source_url"] == currents["sources"][current["name_source"]]
            assert context["note"] and "NASA" in context["note"]
        assert relation["example_object_ids"] == item.get("example_object_ids", [])
        assert relation["example_relation"] == item.get("example_relation")
        if relation["example_object_ids"]:
            assert item["support"] == "generic_process" and relation["example_relation"]
            assert len(relation["example_object_ids"]) == len(set(relation["example_object_ids"]))
            for example_id in relation["example_object_ids"]:
                example = nasa_by_id[example_id]
                assert example["support"] == "explicit_name" and example["almanac_current_id"] in ids
                assert set(example["nasa_sources"]) & set(item["nasa_sources"])
        assert relation["system_context"] == item.get("system_context", [])
        assert relation["class_parent"] == next((edge for edge in class_edges if edge["child_id"] == item["id"]), None)
        assert relation["class_children"] == sorted((edge for edge in class_edges if edge["parent_id"] == item["id"]), key=lambda edge: edge["child_id"])
        for context in relation["system_context"]:
            assert context["system_id"] == "global-overturning"
            assert context["relation"] == "narrated_part_of" and context["note"]
            assert set(context["cue_numbers"]) <= set(relation["release_evidence"]["po2-narrated"]["cue_numbers"])
        assert relation["narrated_start_s"] == item.get("narrated_start_s")
        assert relation["narrated_end_s"] == item.get("narrated_end_s")
        if "po2-narrated" in item["nasa_sources"]:
            assert 0 <= item["narrated_start_s"] < item["narrated_end_s"] <= 317, item["id"]
        else:
            assert "narrated_start_s" not in item and "narrated_end_s" not in item, item["id"]
        assert relation["regional_movie"] == tiles["nasa_object_joins"].get(item["id"])
        assert relation["feature_media_ids"] == [asset["id"] for asset in nasa_media["assets"] if item["id"] in asset["object_ids"]]
        overview = relation["source_overview_movie"]
        if overview:
            assert item.get("narrated_start_s") is None
            assert relation["regional_movie"] is None and not relation["feature_media_ids"]
            assert overview["relation"] == "release_overview_only" and overview["release_id"] in item["nasa_sources"]
            source_movies = next(release["movies"] for release in nasa_release_media["releases"] if release["release_id"] == overview["release_id"])
            assert any(movie["media_id"] == overview["media_id"] and movie["url"] == overview["url"] for movie in source_movies)
        else:
            assert item.get("narrated_start_s") is not None or relation["regional_movie"] or relation["feature_media_ids"], item["id"]
        if item.get("almanac_current_id"):
            assert item["almanac_current_id"] in ids
        if item.get("parent_id"):
            assert item["parent_id"] in object_ids
        current_id = item.get("almanac_current_id")
        expected_evidence = {
            "cartographic_current_crossings": sorted(code for code, state in cartographic["states"].items() if current_id and current_id in state["stable_cartographic_current_crossings"]),
            "width_sensitive_cartographic_contacts": sorted(code for code, state in cartographic["states"].items() if current_id and current_id in state["width_sensitive_cartographic_contacts"]),
            "schematic_current_crossings": sorted(code for code, state in states["states"].items() if current_id and current_id in state["schematic_current_centerline_crossings"]),
            "schematic_object_crossings": sorted(code for code, state in states["states"].items() if item["id"] in state["schematic_nasa_object_crossings"]),
            "editorial_current_line_crossings": sorted(code for code, state in states["states"].items() if current_id and current_id in state["editorial_nasa_current_line_crossings"]),
            "object_locator_candidates": sorted(code for code, state in states["states"].items() if item["id"] in state["nasa_object_locator_candidates"]),
        }
        assert relation["state_evidence"] == expected_evidence, item["id"]
        for kind, codes in relation["state_evidence"].items():
            assert len(codes) == len(set(codes)) and set(codes) <= set(states["states"])
            for code in codes:
                assert item["id"] in nasa_crosswalk["states"][code][kind]
    assert set(nasa_by_id["western-boundary-currents"]["example_object_ids"]) == {"gulf-stream", "kuroshio", "agulhas", "east-australian"}
    assert nasa_crosswalk["objects"]["indonesian-throughflow"]["state_evidence"]["schematic_object_crossings"] == ["SUND"]
    assert {item["id"] for item in nasa["objects"] if item.get("system_context")} == {"agulhas-rings", "gulf-stream", "gulf-stream-deep-return"}
    assert nasa_by_id["agulhas-rings"]["narrated_end_s"] == 178
    for code, kinds in nasa_crosswalk["states"].items():
        for kind, linked_ids in kinds.items():
            assert linked_ids == sorted(set(linked_ids))
            assert all(code in nasa_crosswalk["objects"][object_id]["state_evidence"][kind] for object_id in linked_ids)
    assert len(tiles["tiles"]) == 70 and len({item["id"] for item in tiles["tiles"]}) == 70
    assert set(tiles["current_joins"]) == set(ids)
    assert set(tiles["nasa_object_joins"]) == {item["id"] for item in nasa["objects"] if item["locator"]}
    tile_urls = {item["url"] for item in tiles["tiles"]}
    tile_ids = {item["id"] for item in tiles["tiles"]}
    assert all(match["url"] in tile_urls for joins in tiles["current_joins"].values() for match in joins)
    assert all(match["url"] in tile_urls for match in tiles["nasa_object_joins"].values())
    province_svg = ET.parse(ROOT / "figures" / "osw-province-atlas-interactive.svg")
    province_codes = {item.get("data-code") for item in province_svg.iter() if "province " in item.get("class", "")}
    assert len(province_codes) == 56 and set(states["states"]) == province_codes
    assert state_tiles["state_count"] == 56 and state_tiles["tile_count"] == 70
    assert set(state_tiles["states"]) == province_codes
    polar_release = next(item for item in nasa_release_media["releases"] if item["release_id"] == "po2-polar")
    polar_urls = {item["url"]: item for item in polar_release["movies"] if item["filename"] in {"north_1080.mp4", "south_1080.mp4"}}
    assert len(polar_urls) == 2
    assert sum(bool(item["polar_perspective"]) for item in state_tiles["states"].values()) == 12
    assert state_tiles["states"]["BPLR"]["polar_perspective"]["hemisphere"] == "north"
    assert state_tiles["states"]["SANT"]["polar_perspective"]["hemisphere"] == "south"
    assert state_tiles["states"]["CAMR"]["polar_perspective"] is None
    for code, relation in state_tiles["states"].items():
        if polar := relation["polar_perspective"]:
            assert polar["url"] in polar_urls and polar["media_id"] == polar_urls[polar["url"]]["media_id"]
            assert polar_urls[polar["url"]]["filename"] == f"{polar['hemisphere']}_1080.mp4"
        matches = relation["matches"]
        match_ids = {item["tile_id"] for item in matches}
        assert matches and len(matches) == len(match_ids), code
        assert match_ids <= tile_ids
        assert all(item["url"] in tile_urls and 0 < item["display_coverage_fraction"] <= 1 for item in matches), code
        assert set(relation["recommended_regional_tiles"]) <= match_ids
        assert relation["overview_tile"] in match_ids
        assert all(next(item for item in matches if item["tile_id"] == tile_id)["zoom"] == relation["regional_zoom"] for tile_id in relation["recommended_regional_tiles"])
        assert next(item for item in matches if item["tile_id"] == relation["recommended_regional_tiles"][0])["display_coverage_fraction"] > 0.5, code
    assert set(cartographic["states"]) == province_codes
    assert len(cartographic["arrows"]) == cartographic["source_arrow_count"] == 73
    assert cartographic["mapped_arrow_count"] == 61 and cartographic["mapped_current_count"] == 27
    assert set(cartographic["name_crosswalk"].values()) <= set(ids)
    assert cartographic["name_crosswalk"]["East Wind Drift / Antarctic Subpolar"] == "antarctic-coastal"
    assert cartographic["name_crosswalk_notes"]["East Wind Drift / Antarctic Subpolar"]
    assert len({item["source_arrow_id"] for item in cartographic["arrows"]}) == 73
    for arrow in cartographic["arrows"]:
        assert (arrow["osw_current_id"] is None) == (arrow["unmapped_reason"] is not None)
        by_scale = arrow["state_codes_by_scale"]
        assert set(map(int, by_scale)) == set(cartographic["scales_compared"])
        scale_sets = [set(codes) for codes in by_scale.values()]
        assert set(arrow["stable_state_codes"]) == set.intersection(*scale_sets)
        assert set(arrow["width_sensitive_state_codes"]) == set.union(*scale_sets) - set.intersection(*scale_sets)
        assert set.union(*scale_sets) <= province_codes
    for code, relation in cartographic["states"].items():
        stable = {item["osw_current_id"] for item in cartographic["arrows"] if item["osw_current_id"] and code in item["stable_state_codes"]}
        sensitive = {item["osw_current_id"] for item in cartographic["arrows"] if item["osw_current_id"] and code in item["width_sensitive_state_codes"]} - stable
        assert set(relation["stable_cartographic_current_crossings"]) == stable
        assert set(relation["width_sensitive_cartographic_contacts"]) == sensitive
    drawn_ids = {"gulf-stream", "kuroshio", "agulhas", "acc"}
    assert all(set(state["schematic_current_centerline_crossings"]) <= drawn_ids for state in states["states"].values())
    assert all(set(state["editorial_nasa_current_line_crossings"]) <= {"east-australian"} for state in states["states"].values())
    assert all(set(state["current_locator_candidates"]) <= set(ids) for state in states["states"].values())
    assert all(set(state["nasa_object_locator_candidates"]) <= set(object_ids) for state in states["states"].values())
    assert all(state["individual_named_eddy_containment"] == "unknown_no_dated_footprints" for state in states["states"].values())
    assert set(detected["states"]) == province_codes
    for snapshot, date, count in zip(historical_detections, ("2021-06-01", "2022-06-01"), (7851, 7751)):
        assert snapshot["date"] == date
        assert len(snapshot["entries"]) == count
        assert set(snapshot["states"]) == province_codes
        lookup = {item["id"]: item for item in snapshot["entries"]}
        assert len(lookup) == count
        assert all(item["name"] is None and item["persistent_track_id"] is None for item in snapshot["entries"])
        for code, relation in snapshot["states"].items():
            assert all(code in lookup[eddy_id]["contained_states"] for eddy_id in relation["contained"])
            assert all(code in lookup[eddy_id]["intersected_states"] for eddy_id in relation["intersected"])
    detected_ids = [item["id"] for item in detected["entries"]]
    assert len(detected_ids) == len(set(detected_ids)) == 7699
    detected_lookup = {item["id"]: item for item in detected["entries"]}
    assert weekly["daily_source_sha256"] == detected["source_sha256"]
    assert weekly["matched_daily_eddies"] == len(detected_ids)
    assert set(weekly["tracks"]) == set(detected_ids)
    assert len({item["file_scoped_track_ref"] for item in weekly["tracks"].values()}) == len(detected_ids)
    for eddy_id, track in weekly["tracks"].items():
        assert 1 <= len(track["positions"]) <= 7
        assert track["positions"][0]["date"] == detected["date"]
        assert track["positions"][0]["center"] == detected_lookup[eddy_id]["center"]
        assert all(weekly["start_date"] <= point["date"] <= weekly["end_date"] for point in track["positions"])
    assert weekly_states["weekly_source_sha256"] == weekly["source_sha256"]
    assert weekly_states["track_count"] == len(detected_ids)
    assert set(weekly_states["tracks"]) == set(detected_ids)
    assert set(weekly_states["states"]) == province_codes
    reverse_visits = {code: {} for code in province_codes}
    for eddy_id, visits in weekly_states["tracks"].items():
        assert len(visits) == len(weekly["tracks"][eddy_id]["positions"])
        for visit, position in zip(visits, weekly["tracks"][eddy_id]["positions"]):
            assert visit["date"] == position["date"]
            assert visit["state_codes"] == sorted(set(visit["state_codes"]))
            assert set(visit["state_codes"]) <= province_codes
            for code in visit["state_codes"]:
                reverse_visits[code].setdefault(eddy_id, []).append(visit["date"])
    assert all(weekly_states["states"][code]["track_dates"] == reverse_visits[code] for code in province_codes)
    assert weekly_contours["weekly_source_sha256"] == weekly["source_sha256"]
    assert weekly_contours["track_count"] == len(detected_ids)
    assert set(weekly_contours["tracks"]) == set(detected_ids)
    assert set(weekly_contours["states"]) == province_codes
    assert nasa_crop_timeline["date_count"] == len(nasa_crop_timeline["dates"])
    assert nasa_crop_timeline["source_frame_count"] == 3601
    assert nasa_crop_timeline["sampled_crop_video_evidence"]["video_frames"] == 7201
    assert detected["date"] in nasa_crop_timeline["dates"]
    assert nasa_crop_timeline["dates"][detected["date"]]["estimated_crop_seconds"] == 118.2
    assert list(nasa_crop_timeline["dates"]) == sorted(nasa_crop_timeline["dates"])
    assert all(0 <= item["sos_first_frame"] <= item["sos_last_frame"] < 3601
               and 0 <= item["estimated_crop_frame"] < 7201
               and 0 <= item["estimated_crop_seconds"] <= 240
               for item in nasa_crop_timeline["dates"].values())
    contour_reverse = {code: {"contained": {}, "intersected": {}} for code in province_codes}
    for eddy_id, visits in weekly_contours["tracks"].items():
        assert len(visits) == len(weekly["tracks"][eddy_id]["positions"])
        first = visits[0]
        assert set(first["contained_states"]) == set(detected_lookup[eddy_id]["contained_states"])
        assert set(first["intersected_states"]) == set(detected_lookup[eddy_id]["intersected_states"])
        for visit, position in zip(visits, weekly["tracks"][eddy_id]["positions"]):
            assert visit["date"] == position["date"]
            assert not set(visit["contained_states"]) & set(visit["intersected_states"])
            assert set(visit["contained_states"] + visit["intersected_states"]) <= province_codes
            assert visit["contour_available"] or not (visit["contained_states"] or visit["intersected_states"])
            for status in ("contained", "intersected"):
                for code in visit[f"{status}_states"]:
                    contour_reverse[code][status].setdefault(eddy_id, []).append(visit["date"])
    assert weekly_contours["states"] == contour_reverse
    for snapshot in historical_detections:
        stamp = snapshot["date"].replace("-", "")
        end = (datetime.strptime(stamp, "%Y%m%d") + timedelta(days=6)).strftime("%Y%m%d")
        dated_weekly = read(f"noaa-munster-eddy-weekly-join-{stamp}-{end}.json")
        dated_centers = read(f"noaa-munster-eddy-weekly-state-join-{stamp}-{end}.json")
        dated_contours = read(f"noaa-munster-eddy-weekly-contour-state-join-{stamp}-{end}.json")
        lookup = {item["id"]: item for item in snapshot["entries"]}
        assert dated_weekly["start_date"] == snapshot["date"]
        assert dated_weekly["daily_source_sha256"] == snapshot["source_sha256"]
        assert dated_weekly["matched_daily_eddies"] == len(lookup)
        assert set(dated_weekly["tracks"]) == set(lookup)
        assert dated_centers["weekly_source_sha256"] == dated_contours["weekly_source_sha256"] == dated_weekly["source_sha256"]
        assert dated_centers["track_count"] == dated_contours["track_count"] == len(lookup)
        assert set(dated_centers["tracks"]) == set(dated_contours["tracks"]) == set(lookup)
        assert set(dated_centers["states"]) == set(dated_contours["states"]) == province_codes
        center_reverse = {code: {} for code in province_codes}
        dated_contour_reverse = {code: {"contained": {}, "intersected": {}} for code in province_codes}
        for eddy_id, track in dated_weekly["tracks"].items():
            positions = track["positions"]
            center_visits = dated_centers["tracks"][eddy_id]
            contour_visits = dated_contours["tracks"][eddy_id]
            assert 1 <= len(positions) == len(center_visits) == len(contour_visits) <= 7
            assert positions[0]["date"] == snapshot["date"]
            assert positions[0]["center"] == lookup[eddy_id]["center"]
            assert set(contour_visits[0]["contained_states"]) == set(lookup[eddy_id]["contained_states"])
            assert set(contour_visits[0]["intersected_states"]) == set(lookup[eddy_id]["intersected_states"])
            for position, center, contour in zip(positions, center_visits, contour_visits):
                assert position["date"] == center["date"] == contour["date"]
                assert dated_weekly["start_date"] <= position["date"] <= dated_weekly["end_date"]
                assert not set(contour["contained_states"]) & set(contour["intersected_states"])
                for code in center["state_codes"]:
                    center_reverse[code].setdefault(eddy_id, []).append(position["date"])
                for status in ("contained", "intersected"):
                    for code in contour[f"{status}_states"]:
                        dated_contour_reverse[code][status].setdefault(eddy_id, []).append(position["date"])
        assert all(dated_centers["states"][code]["track_dates"] == center_reverse[code] for code in province_codes)
        assert dated_contours["states"] == dated_contour_reverse
    assert all(item["name"] is None and item["persistent_track_id"] is None for item in detected["entries"])
    for item in detected["entries"]:
        assert not set(item["contained_states"]) & set(item["intersected_states"])
        assert set(item["contained_states"] + item["intersected_states"]) <= province_codes
        assert item["radius_km"] is None or item["radius_km"] > 0
    for code, relation in detected["states"].items():
        assert all(code in detected_lookup[eddy_id]["contained_states"] for eddy_id in relation["contained"])
        assert all(code in detected_lookup[eddy_id]["intersected_states"] for eddy_id in relation["intersected"])
    cartographic_relations = sum(len(state["stable_cartographic_current_crossings"]) for state in cartographic["states"].values())
    print(f"OK: {len(ids)} currents, {len(nasa['objects'])} NASA objects, {len(tiles['tiles'])} NASA crop links, {len(states['states'])} states, {cartographic_relations} stable cartographic current/state joins, {seasonal_eddies['detection_count_sum']} NOAA eddy detections across {seasonal_eddies['snapshot_count']} sampled dates, {len(eddy_names['entries'])} Loop eddy labels from {len(numbers)} events, {len(eddy_geography['entries'])} other named eddy records")


if __name__ == "__main__":
    main()
