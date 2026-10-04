"""Validate the frozen ocean motion package without network access."""

import csv
import gzip
import hashlib
import json
import itertools
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit

from jsonschema import Draft202012Validator, FormatChecker
from shapely.geometry import LineString, Polygon, Point, shape, box
from build_cartographic_current_state_join import load_states, project
from build_gulf_stream_navo_state_snapshot import build as build_front_state_snapshot
from build_gulf_stream_geostrophic_path import build as build_geostrophic_path
from build_navo_freddies_eddy_state_join import build as build_operational_eddy_join
from build_ocean_motion_claims import review_fingerprint
from build_kraken_footprint_candidate import geometry_digest


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "almanac" / "release" / "v0.1.0"
COLLECTIONS = ("entities", "names", "measurements", "length_assessments", "relations", "claims", "media", "geometries", "tiles", "tile_state_relations", "named_eddy_state_assessments", "named_eddy_source_observations", "named_current_source_observations", "operational_eddy_state_observations", "diagnosed_current_path_observations", "classification_vocabularies", "named_eddy_footprint_candidates", "footprint_movie_context", "observation_sets", "sources")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def check():
    if not __debug__:
        raise RuntimeError("Release validation requires Python assertions; do not run with -O")
    # Full provider polygon rings exceed the csv module's default 128 KiB cell.
    csv.field_size_limit(16 * 1024 * 1024)
    manifest = load(PACKAGE / "manifest.json")
    for entry in manifest["inputs"]:
        path = ROOT / entry["path"]
        assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"], entry
    for entry in manifest["code_files"]:
        path = ROOT / entry["path"]
        assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"], entry
    for entry in manifest["files"]:
        path = PACKAGE / entry["path"]
        assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"], entry
    for filename in ("METHODS.md", "CHANGELOG.md", "CLAIM-REVIEW-WORKFLOW.md",
                     "DATASET-CITATION-DRAFT.json"):
        assert (PACKAGE / filename).read_bytes() == (ROOT / "almanac" / "release" / filename).read_bytes()
    citation = load(PACKAGE / "DATASET-CITATION-DRAFT.json")
    assert citation["status"] == "candidate_not_registered_or_published"
    assert citation["version"] == manifest["version"]
    assert citation["doi"] is None and citation["publication_year"] is None
    assert citation["publisher"] is None and citation["rights_statement"] is None
    assert citation["resource_type_general"] == "Dataset"
    rows = {key: load(PACKAGE / (key + ".json")) for key in COLLECTIONS}
    schema = load(PACKAGE / "schema.json")["definitions"]
    validators = {}
    for key in COLLECTIONS:
        Draft202012Validator.check_schema(schema[key])
        validators[key] = Draft202012Validator(schema[key], format_checker=FormatChecker())
    coverage = load(PACKAGE / "coverage.json")
    ids = {key: {row["id"] for row in value} for key, value in rows.items()}
    for key, value in rows.items():
        assert len(value) == len(ids[key]) == coverage["counts"][key], key
        with (PACKAGE / (key + ".csv")).open(encoding="utf-8", newline="") as stream:
            flat_rows = list(csv.DictReader(stream))
        assert len(flat_rows) == len(value), key
        for source_row, flat_row in zip(value, flat_rows):
            for field, cell in flat_row.items():
                original = source_row.get(field)
                expected = (json.dumps(original, ensure_ascii=False, sort_keys=True)
                            if isinstance(original, (list, dict)) else "" if original is None else str(original))
                assert cell == expected, (key, source_row["id"], field)
        for row in value:
            assert set(schema[key]["required"]) <= set(row), (key, row)
            validators[key].validate(row)
            if "entity_id" in row:
                assert row["entity_id"] in ids["entities"], row
            if "operational_eddy_id" in row:
                assert row["operational_eddy_id"] in ids["entities"], row
            if "geometry_id" in row:
                assert row["geometry_id"] in ids["geometries"], row
            if "subject_id" in row and key != "claims":
                assert row["subject_id"] in ids["entities"] and row["object_id"] in ids["entities"], row
            if "source_id" in row:
                assert row["source_id"] in ids["sources"], row
            if "source_snapshot_id" in row:
                assert row["source_snapshot_id"] is None or row["source_snapshot_id"] in ids["sources"], row
    claims_by_id = {row["id"]: row for row in rows["claims"]}
    assert all(row["subject_id"] in ids["entities"] | ids["tiles"] and
               (row["object_id"] is None or row["object_id"] in ids["entities"])
               for row in rows["claims"])
    editorial = load(PACKAGE / "ranked-length-editorial-reviews.json")
    assert editorial == load(PACKAGE / "source-ledgers" / "ocean-motion-ranked-length-editorial-reviews.json")
    assert editorial["schema"] == "osw.ocean-motion-ranked-length-editorial-reviews.v1"
    assert editorial["status"] == "source_passage_audit_only_not_scientific_claim_approval"
    ranked = {row["claim_id"]: row for row in rows["measurements"] if row["rank_eligible"]}
    assert len(ranked) == len(editorial["entries"]) == 11
    assert {entry["claim_id"] for entry in editorial["entries"]} == set(ranked)
    for entry in editorial["entries"]:
        claim = claims_by_id[entry["claim_id"]]
        measurement = ranked[entry["claim_id"]]
        assert entry["review_fingerprint"] == claim["review_fingerprint"]
        assert entry["subject_id"] == claim["subject_id"] == measurement["entity_id"]
        assert entry["reported_length_km"] == claim["value"] == measurement["value"]
        assert entry["scientific_review_status"] == claim["review_status"]
        assert entry["source_passage_assessment"] in {
            "quoted_number_supported_with_scope_limit", "quoted_number_supported_with_source_warning"}
        assert entry["editorial_note"].strip()
    assert len(claims_by_id) == sum(len(rows[key]) for key in
                                    ("relations", "measurements", "tile_state_relations",
                                     "named_eddy_state_assessments", "named_eddy_source_observations",
                                     "named_current_source_observations", "operational_eddy_state_observations",
                                     "diagnosed_current_path_observations", "classification_vocabularies", "named_eddy_footprint_candidates", "footprint_movie_context"))
    for collection_name in ("relations", "measurements", "tile_state_relations",
                            "named_eddy_state_assessments", "named_eddy_source_observations",
                            "named_current_source_observations", "operational_eddy_state_observations",
                            "diagnosed_current_path_observations", "classification_vocabularies", "named_eddy_footprint_candidates", "footprint_movie_context"):
        for record in rows[collection_name]:
            claim = claims_by_id[record["claim_id"]]
            assert claim["target_collection"] == collection_name and claim["target_id"] == record["id"]
            assert claim["source_id"] == record["source_id"]
            expected_predicate = (record.get("predicate") or record.get("quantity") or record.get("relation") or
                                  {"named_eddy_state_assessments": "named_eddy_state_assessment",
                                   "named_eddy_source_observations": "published_named_eddy_observation",
                                   "named_current_source_observations": "source_reported_local_current_presence",
                                   "classification_vocabularies": "source_scoped_regime_vocabulary", "footprint_movie_context": "figure_footprint_movie_geographic_context", "named_eddy_footprint_candidates": "dated_figure_ssh_footprint_candidate", "diagnosed_current_path_observations": "dated_geostrophic_streamline_reach"}.get(collection_name))
            assert claim["predicate"] == expected_predicate
            assert claim["review_fingerprint"] == review_fingerprint(claim)
            if collection_name == "measurements":
                assert claim["subject_id"] == record["entity_id"] and claim["object_id"] is None
                assert claim["value"] == record["value"] and claim["unit"] == record["unit"]
            elif collection_name == "named_eddy_state_assessments":
                assert claim["subject_id"] == record["eddy_id"] and claim["object_id"] == record["state_id"]
                assert claim["evidence_class"] == record["evidence_status"]
                assert claim["assertion_status"] == "unresolved_assessment"
            elif collection_name == "named_eddy_source_observations":
                assert claim["subject_id"] == record["entity_id"] and claim["object_id"] is None
                assert claim["assertion_status"] == "recorded_observation"
            elif collection_name == "named_current_source_observations":
                assert claim["subject_id"] == record["entity_id"] and claim["object_id"] == record["state_id"]
                assert claim["assertion_status"] == "recorded_relation"
                if record.get("reported_observation_points_lon_lat"):
                    assert claim["observation_support"] == {key: record[key] for key in
                        ("reported_observation_points_lon_lat", "observation_time_precision", "observation_depth_note", "state_boundary_limit")}
            elif collection_name == "operational_eddy_state_observations":
                assert claim["subject_id"] == record["operational_eddy_id"] and claim["object_id"] == record["state_id"]
                assert claim["assertion_status"] == "recorded_relation"
            elif collection_name == "footprint_movie_context":
                assert claim["subject_id"] == record["entity_id"] and claim["object_id"] is None
                assert claim["assertion_status"] == "navigation_only_no_event_identity"
                assert claim["navigation_support"] == {key: value for key, value in record.items() if key not in {"id", "claim_id"}}
            elif collection_name == "named_eddy_footprint_candidates":
                assert claim["subject_id"] == record["entity_id"] and claim["object_id"] is None
                assert claim["assertion_status"] == "recorded_footprint_candidate_not_verified_boundary"
                assert claim["footprint_support"] == {key: value for key, value in record.items() if key not in {"id", "claim_id", "review_status"}}
            elif collection_name == "classification_vocabularies":
                assert claim["subject_id"] == record["entity_id"] and claim["object_id"] is None
                assert claim["assertion_status"] == "recorded_vocabulary_not_observed_assignment"
                assert claim["vocabulary_definition"] == {key: record[key] for key in
                    ("terms", "density_variable_note", "assignment_requirements",
                     "not_equivalent_to", "assignment_status", "assignments")}
                assert record["assignments"] == []
                assert record["assignment_status"] == "vocabulary_only_no_osw_state_assignments"
                assert len({term["id"] for term in record["terms"]}) == len(record["terms"])
                assert claim["observation_time"] is None and claim["value"] is None
            elif collection_name == "diagnosed_current_path_observations":
                assert claim["subject_id"] == record["entity_id"] and claim["object_id"] is None
                assert claim["value"] == record["reach_length_km"] and claim["unit"] == "km"
            else:
                assert claim["subject_id"] == record.get("subject_id", "tile:" + record.get("tile_id", ""))
                assert claim["object_id"] == record.get("object_id", record.get("state_id"))
                assert (claim["assertion_status"] == "unresolved_assessment") == (
                    record["evidence_class"] == "unresolved" or
                    str(record.get("physical_relation", "")).startswith("unknown"))
    assert Counter(row["source_locator_status"] for row in rows["claims"]) == coverage["claim_locator_statuses"]
    assert Counter(row["method_status"] for row in rows["claims"]) == coverage["claim_method_statuses"]
    assert Counter(row["review_status"] for row in rows["claims"]) == coverage["claim_review_statuses"]
    review_ledger = load(PACKAGE / "source-ledgers" / "ocean-motion-claim-reviews.json")
    review_decisions = {row["claim_id"]: row for row in review_ledger["decisions"]}
    assert review_ledger["schema"] == "osw.ocean-motion-claim-reviews.v1"
    assert len(review_decisions) == len(review_ledger["decisions"])
    assert set(review_decisions) <= set(claims_by_id)
    for claim in rows["claims"]:
        decision = review_decisions.get(claim["id"])
        if decision is None:
            assert claim["review_status"] == "not_individually_reviewed"
            assert claim["reviewer"] is None and claim["review_date"] is None and claim["review_note"] is None
        else:
            assert decision["review_fingerprint"] == claim["review_fingerprint"]
            assert all(claim[key] == decision[key] for key in
                       ("review_status", "reviewer", "review_date", "review_note"))
    with (PACKAGE / "source-locator-worklist.csv").open(encoding="utf-8", newline="") as stream:
        locator_worklist = list(csv.DictReader(stream))
    missing_locator_claims = {row["id"]: row for row in rows["claims"]
                              if row["source_locator_status"] == "source_only_no_precise_locator"}
    assert not missing_locator_claims, "Every released claim needs a precise source locator"
    with (PACKAGE / "claim-science-review-first-pass.csv").open(encoding="utf-8", newline="") as stream:
        science_worklist = list(csv.DictReader(stream))
    specific_claims = {row["id"]: row for row in rows["claims"] if row["source_locator_status"] == "specific"}
    assert len(science_worklist) == len(specific_claims)
    assert {row["claim_id"] for row in science_worklist} == set(specific_claims)
    for row in science_worklist:
        claim = specific_claims[row["claim_id"]]
        assert row["review_fingerprint"] == claim["review_fingerprint"]
        assert row["source_locator"] == claim["source_locator"]
        assert row["review_status"] == claim["review_status"]
    assert {row["claim_id"] for row in locator_worklist} == set(missing_locator_claims)
    assert len(locator_worklist) == len(missing_locator_claims)
    for row in locator_worklist:
        claim = missing_locator_claims[row["claim_id"]]
        assert row["target_id"] == claim["target_id"] and row["source_id"] == claim["source_id"]
        assert row["source_url"] == next(source["url"] for source in rows["sources"]
                                         if source["id"] == claim["source_id"])
        assert row["resolution_status"] == "pending" and not row["reviewer"] and not row["review_date"]
    for collection_name in ("operational_eddy_state_observations", "diagnosed_current_path_observations", "classification_vocabularies", "named_eddy_footprint_candidates", "footprint_movie_context"):
        assert all(row["source_locator_status"] == "specific" for row in rows["claims"]
                   if row["target_collection"] == collection_name)
    assert all(row["source_locator_status"] == "specific" for row in rows["claims"]
               if row["predicate"] in {"dated_surface_front_intersection",
                                       "dated_geostrophic_streamline_segment_intersection",
                                       "dated_geostrophic_streamline_reach"})
    for claim in rows["claims"]:
        if claim["support_claim_id"] is not None:
            supported = claims_by_id[claim["support_claim_id"]]
            if claim["target_collection"] == "footprint_movie_context":
                assert supported["target_collection"] == "named_eddy_footprint_candidates"
                assert supported["subject_id"] == claim["subject_id"]
                target = next(row for row in rows["footprint_movie_context"] if row["id"] == claim["target_id"])
                assert supported["target_id"] == target["footprint_candidate_id"]
                continue
            target = next(row for row in rows["relations"] if row["id"] == claim["target_id"])
            assert supported["target_collection"] == "named_current_source_observations"
            assert supported["target_id"] == target["observation_id"]
    # Independently verify nominal geographic navigation against every crop.
    context_tiles = {row["tile_id"]: row for row in rows["tiles"]}
    context_geometries = {row["id"]: row for row in rows["geometries"]}
    for candidate in rows["named_eddy_footprint_candidates"]:
        polygon = shape(context_geometries[candidate["geometry_id"]]["geometry"])
        expected = {}
        for tile_id, tile in context_tiles.items():
            west, east = tile["longitude_range_unwrapped"]
            south, north = tile["latitude_range"]
            # Valid crops span at most one revolution; disjoint periodic interiors.
            area = sum(polygon.intersection(box(west + offset, south, east + offset, north)).area
                       for offset in (-720, -360, 0, 360, 720))
            fraction = area / polygon.area
            if fraction > 1e-10: expected[tile_id] = min(1.0, fraction)
        contexts = [row for row in rows["footprint_movie_context"] if row["footprint_candidate_id"] == candidate["id"]]
        assert len(contexts) == len(expected)
        assert {row["tile_id"] for row in contexts} == set(expected)
        for row in contexts:
            tile = context_tiles[row["tile_id"]]
            assert abs(row["nominal_angular_overlap_fraction"] - expected[row["tile_id"]]) < 5.1e-10
            assert row["nominal_complete_view"] == (expected[row["tile_id"]] >= 1 - 1e-9)
            for field in ("zoom", "url", "latitude_range", "longitude_range_unwrapped", "source_id"):
                assert row[field] == tile[field]
            assert row["geometry_id"] == candidate["geometry_id"]
            assert row["geometry_sha256"] == candidate["geometry_sha256"]
            assert row["figure_source_id"] == candidate["source_id"]
            assert row["figure_snapshot_source_id"] == candidate["source_snapshot_id"]
            assert row["observation_date"] == candidate["observation_date"]
            assert row["movie_model_period"] == "2021–2023"
            assert row["temporal_alignment_status"] == "outside_declared_model_years"
            assert row["event_identity_status"] == "not_established"
        complete = [row for row in contexts if row["nominal_complete_view"]]
        best = min(complete, key=lambda row: (-row["zoom"], row["crop_center_distance_score"], row["tile_id"]))
        assert [row["id"] for row in contexts if row["recommended"]] == [best["id"]]
        assert best["tile_id"] == "level2_B_3"
    assert coverage["claim_locator_statuses"]["internal_ledger_row"] == 5600 + 877
    assert coverage["claim_locator_statuses"]["internal_ledger_record"] == 136 * 56 + 128
    internal_documents = {}
    sources_by_claim_id = {row["id"]: row for row in rows["sources"]}
    targets_by_collection = {name: {row["id"]: row for row in rows[name]}
                             for name in ("relations", "measurements", "tile_state_relations",
                                          "named_eddy_state_assessments", "named_eddy_source_observations",
                                          "named_current_source_observations", "operational_eddy_state_observations",
                                          "diagnosed_current_path_observations", "classification_vocabularies", "named_eddy_footprint_candidates", "footprint_movie_context")}
    for claim in rows["claims"]:
        if claim["method_source_id"] is not None:
            assert claim["method_source_id"] in ids["sources"]
        if claim["source_locator_status"] not in {"internal_ledger_row", "internal_ledger_record"}:
            continue
        location, pointer = claim["source_locator"].split("#", 1)
        assert location == sources_by_claim_id[claim["source_id"]]["path"]
        assert location.startswith("source-ledgers/") and pointer.startswith("/")
        if location not in internal_documents:
            internal_documents[location] = load(PACKAGE / location)
        selected = internal_documents[location]
        for token in pointer.lstrip("/").split("/"):
            selected = selected[int(token)] if isinstance(selected, list) else selected[token]
        target = targets_by_collection[claim["target_collection"]][claim["target_id"]]
        if claim["source_locator_status"] == "internal_ledger_record":
            assert selected["id"] == claim["subject_id"].split(":", 1)[1]
        elif claim["target_collection"] == "tile_state_relations":
            assert selected["tile_id"] == target["tile_id"]
        else:
            assert selected["atlas_relation"] == target["predicate"]
    entity_types = Counter(row["type"] for row in rows["entities"])
    taxonomy = load(PACKAGE / "taxonomy.json")
    assert set(taxonomy["source_scoped_regime_vocabulary_ids"]) == ids["classification_vocabularies"]
    assert taxonomy["status"].startswith("OSW editorial")
    assert set(taxonomy["source_ids"]) <= ids["sources"]
    for entity in rows["entities"]:
        if entity["type"] in {"named_current", "named_eddy"}:
            assert entity["identity_level"] in taxonomy["axes"]["identity_level"]
            assert entity["setting"] in taxonomy["axes"]["setting"]
            assert entity["time_behavior"] in taxonomy["axes"]["time_behavior"]
        if entity["type"] == "nasa_described_motion":
            assert entity["motion_form"] in taxonomy["nasa_motion_forms"]
    assert entity_types == coverage["entity_types"]
    assert Counter(row["identity_level"] for row in rows["entities"]
                   if row["type"] in {"named_current", "named_eddy"}) == coverage["identity_levels"]
    assert Counter(row["setting"] for row in rows["entities"]
                   if row["type"] in {"named_current", "named_eddy"}) == coverage["settings"]
    assert Counter(row["motion_form"] for row in rows["entities"]
                   if row["type"] == "nasa_described_motion") == coverage["nasa_motion_forms"]
    assert entity_types == {"named_current": 100, "named_eddy": 136,
                            "nasa_described_motion": 22, "osw_state": 56,
                            "operational_eddy_detection": 4}
    northern = next(row for row in rows["entities"] if row["id"] == "current:northern-mediterranean")
    assert northern["label"] == "Northern Current" and northern["identity_level"] == "current"
    assert any(row["entity_id"] == northern["id"] and
               row["label"] == "Liguro-Provençal-Catalan Current" and not row["preferred"]
               for row in rows["names"])
    assert any(row["subject_id"] == "current:ligurian" and
               row["object_id"] == northern["id"] and
               row["predicate"] == "named_regional_segment_of" and
               row["evidence_class"] == "source_associated"
               for row in rows["relations"])
    current_observation_source = load(PACKAGE / "source-ledgers" / "named-current-published-observations.json")
    current_observations = rows["named_current_source_observations"]
    assert len(current_observations) == len(current_observation_source["entries"]) == 8
    assert coverage["named_currents_with_published_local_observations"] == 7
    alaska_observation = next(row for row in current_observations if row["entity_id"] == "current:alaska-coastal-gulf")
    assert alaska_observation["id"] == "current_source_observation:0007"
    assert alaska_observation["state_id"] == "state:ALSK"
    assert (alaska_observation["observation_start"], alaska_observation["observation_end"]) == ("1989-05-10", "1989-07-15")
    assert alaska_observation["reported_section_endpoints_lon_lat"] is None
    assert "Sea Valley" in alaska_observation["reported_locality"]
    assert "whole_current_passage_unresolved" in alaska_observation["physical_relation"]
    section_events = {}
    for row, original in zip(current_observations, current_observation_source["entries"]):
        assert row["entity_id"] == "current:" + original["current_id"]
        assert row["state_id"] == "state:" + original["state_code"]
        assert row["state_id"] in ids["entities"]
        assert row["observation_start"] == original["observation_start"]
        assert row["observation_end"] == original["observation_end"]
        assert row["source_url"] == original["source_url"]
        assert row["state_assignment_method"] == original["state_assignment_method"]
        assert row["physical_relation"] == original["physical_relation"]
        assert row["observation_event_id"] == original["observation_event_id"]
        assert row["geometry_status"] == original["geometry_status"]
        assert row["reported_section_endpoints_lon_lat"] == original.get("reported_section_endpoints_lon_lat")
        if row["reported_section_endpoints_lon_lat"]:
            assert row["state_assignment_method"] == "source_reported_section_intersects_approximate_osw_state_polygon"
            assert row["geometry_status"] == "source_reported_section_bounds_not_current_axis"
            event = section_events.setdefault(row["observation_event_id"], {"bounds": row["reported_section_endpoints_lon_lat"], "states": set()})
            assert event["bounds"] == row["reported_section_endpoints_lon_lat"]
            event["states"].add(row["state_id"].removeprefix("state:"))
        elif row.get("reported_observation_points_lon_lat"):
            assert row["geometry_status"] == "source_reported_instrument_points_not_current_axis_or_footprint"
            assert row["reported_observation_points_lon_lat"] == original["reported_observation_points_lon_lat"]
            assert row["observation_time_precision"] == "month"
            assert len(row["observation_start"]) == len(row["observation_end"]) == 7
            assert row["state_assignment_method"] == "source_reported_instrument_points_projected_into_approximate_osw_state_polygon"
            assert row["observation_depth_note"] == original["observation_depth_note"]
            state_shapes = load_states()
            for point in row["reported_observation_points_lon_lat"]:
                assert {code for code, shape in state_shapes.items() if shape.covers(Point(project(*point)))} == {original["state_code"]}
        else:
            if row["observation_event_id"] == "toulon-2011-northern":
                assert row["geometry_status"] == "source_figures_not_digitized"
            else:
                assert row["observation_event_id"] == "shelikof-sea-valley-1989-alaska-coastal"
                assert row["geometry_status"] == "source_reported_locality_no_digitized_section_geometry"
        assert any(relation["observation_id"] == row["id"] and
                   relation["predicate"] == "source_reported_local_current_presence" and
                   relation["subject_id"] == row["entity_id"] and
                   relation["object_id"] == row["state_id"] and
                   relation["evidence_class"] == "source_associated"
                   for relation in rows["relations"] if relation.get("observation_id"))
    state_shapes = load_states()
    for event in section_events.values():
        section = LineString([project(*point) for point in event["bounds"]])
        intersects = {code for code, shape in state_shapes.items() if section.intersection(shape).length > 1e-8}
        assert event["states"] == intersects, (event["states"], intersects)
    operational_source = load(PACKAGE / "source-ledgers" / "navo-freddies-eddy-snapshot-20260925.json")
    operational_join = load(PACKAGE / "source-ledgers" / "navo-freddies-eddy-state-join-20260925.json")
    assert operational_join == build_operational_eddy_join()
    assert operational_source["source_zip_sha256"] == operational_join["source_zip_sha256"]
    assert "Approved for Public Release" in operational_source["source_release_text"]
    operational_rows = rows["operational_eddy_state_observations"]
    expected_relations = {(feature["id"], "state:" + relation["state_code"], relation["relation"])
                          for feature in operational_join["features"] for relation in feature["state_relations"]}
    assert len(operational_rows) == len(expected_relations) == 4
    assert coverage["dated_operational_eddies_with_source_polygons"] == 4
    assert {(row["operational_eddy_id"], row["state_id"], row["relation"]) for row in operational_rows} == expected_relations
    operational_entities = {row["id"]: row for row in rows["entities"]
                            if row["type"] == "operational_eddy_detection"}
    operational_geometries = {row["entity_id"]: row for row in rows["geometries"]
                              if row["role"] == "dated_operational_eddy_polygon"}
    assert set(operational_entities) == set(operational_geometries) == {feature["id"] for feature in operational_join["features"]}
    receipt_by_code = {row["provider_code"]: row for row in operational_source["eddies"]}
    for feature in operational_join["features"]:
        entity = operational_entities[feature["id"]]
        geometry = operational_geometries[feature["id"]]
        ring = receipt_by_code[feature["provider_code"]]["source_polygon_lon_lat"]
        assert entity["identity_level"] == "dated_detection" and entity["observation_date"] == "2026-09-25"
        assert geometry["geometry"] == {"type": "Polygon", "coordinates": [ring]}
        assert ring[0] == ring[-1] and Polygon(ring).is_valid and Polygon(ring).area > 0
        assert geometry["coordinate_reference_system"] == "unspecified_datum_lon_lat_degrees"
        assert geometry["source_zip_sha256"] == operational_source["source_zip_sha256"]
        assert all(row["geometry_id"] == geometry["id"] for row in operational_rows
                   if row["operational_eddy_id"] == entity["id"])
        assert next(row for row in rows["sources"] if row["id"] == entity["source_id"])["rights_status"].startswith("pending")
    assert all(row["relation"] == "contained_in_approximate_state" and
               row["display_projection_polygon_area_fraction"] == 1.0 and
               row["source_zip_sha256"] == operational_source["source_zip_sha256"]
               for row in operational_rows)
    eddy_state_rows = rows["named_eddy_state_assessments"]
    assert len(eddy_state_rows) == coverage["named_eddy_state_pairs"] == 136 * 56
    assert Counter(row["evidence_status"] for row in eddy_state_rows) == coverage["named_eddy_state_evidence_statuses"]
    assert {(row["eddy_id"], row["state_id"]) for row in eddy_state_rows} == {
        (eddy["id"], state["id"]) for eddy in rows["entities"] if eddy["type"] == "named_eddy"
        for state in rows["entities"] if state["type"] == "osw_state"}
    eddy_inventory = load(PACKAGE / "source-ledgers" / "ocean-eddy-name-inventory.json")
    eddies_by_id = {"eddy:" + item["id"]: item for item in eddy_inventory["entries"]}
    for row in eddy_state_rows:
        item = eddies_by_id[row["eddy_id"]]
        code = row["state_id"].removeprefix("state:")
        primary = code in item["state_locator_candidates"]
        points = [point["evidence_type"] for point in item.get("additional_observed_position_joins", [])
                  if code in point.get("state_center_candidates", [])]
        expected = ([item["locator_evidence_type"]] if primary else []) + points
        status = ("figure_derived_red_curve_candidate" if item["id"] == "published:kraken-2013" and code == "CAMR" else
                  "figure_derived_dated_ssh_contour_candidate" if item["id"] == "published:kraken-2013" and code == "CARB" else
                  "published_observed_center_point_candidate" if primary and item["source_collection"] == "published_loop_current" and item.get("published_observed_position") else
                  "shared_source_region_gateway" if primary and item["state_relation"] == "shared_source_region_gateway_only"
                  else "point_or_region_locator" if primary else
                  "additional_observed_point" if points else "unresolved")
        assert row["evidence_status"] == status and row["point_evidence_types"] == expected
        assert row["physical_relation"] == (
            "observed_center_point_not_whole_eddy_containment"
            if status == "published_observed_center_point_candidate" else
            "dated_ssh_proxy_intersection_candidate_whole_eddy_relation_unresolved"
            if item["id"] == "published:kraken-2013" and code in {"CAMR", "CARB"}
            else "unknown_no_dated_eddy_footprint")
        if item["id"] == "published:kraken-2013" and code in {"CAMR", "CARB"}:
            assert row["dated_ssh_contour_observation_date"] == "2013-05-29"
            assert next(source for source in rows["sources"] if source["id"] == row["source_id"])["path"] == "source-ledgers/kraken-2013-figure2-state-audit.json"
            lower, upper = row["dated_ssh_contour_area_fraction_range"]
            nominal = row["dated_ssh_contour_nominal_area_fraction"]
            assert lower <= nominal <= upper
            if code == "CAMR":
                assert lower > 0.9 and row["dated_ssh_contour_assessment"] == "robust_figure_intersection_candidate"
            else:
                assert lower == 0 < nominal < upper and row["dated_ssh_contour_assessment"] == "axis_sensitive_figure_intersection_candidate"
        assert row["source_record_id"] == item["source_record_id"]
    published_eddy_evidence = load(PACKAGE / "source-ledgers" / "named-loop-eddy-published-observations.json")
    observed_eddies = rows["named_eddy_source_observations"]
    assert len(observed_eddies) == 9 and len(published_eddy_evidence["entries"]) == 5
    assert len({row["entity_id"] for row in observed_eddies}) == coverage["named_eddies_with_published_observations"] == 5
    source_urls = {row["id"]: row["url"] for row in rows["sources"]}
    primary_observations = [row for row in observed_eddies if row.get("event_stage") is None]
    for row, original in zip(primary_observations, published_eddy_evidence["entries"]):
        assert row["entity_id"] == "eddy:" + original["eddy_id"]
        assert original["eddy_id"].startswith("published:")
        assert original["possible_same_ring_as_horizon_id"].startswith("horizon:")
        assert row["observation_start"] == original["observation_start"]
        assert row["observation_end"] == original["observation_end"]
        assert row["evidence_type"] == original["evidence_type"]
        assert row["name_origin"] == original.get("name_origin")
        assert row["observed_center"] == original.get("observed_center")
        assert row["near_center_mooring"] == original.get("near_center_mooring")
        assert row["source_locator"] == original["source_locator"]
        assert row["reported_measure"] == original["reported_measure"]
        assert row["interpretation"] == original["interpretation"]
        assert source_urls[row["source_id"]] == original["source_url"]
        assert row["geometry_status"] == ("figure_red_pixels_georeferenced_no_closed_boundary"
                                           if original["eddy_id"] == "published:kraken-2013" else
                                           "published_figure_not_digitized")
    expected_events = {(original["eddy_id"], event["observation_date"], event["event_stage"]): event
                       for original in published_eddy_evidence["entries"]
                       for event in original.get("independent_event_observations", [])}
    event_rows = [row for row in observed_eddies if row.get("event_stage")]
    assert len(event_rows) == len(expected_events) == 4
    for row in event_rows:
        key = (row["entity_id"].removeprefix("eddy:"), row["observation_start"], row["event_stage"])
        event = expected_events[key]
        assert row["observation_end"] == event["observation_date"]
        assert row["source_locator"] == event["source_locator"]
        assert row["interpretation"] == event["interpretation"]
        assert source_urls[row["source_id"]] == event["source_url"]
        assert row["geometry_status"] == "source_reported_event_no_named_eddy_footprint"
        assert row["physical_state_relation"] == "unresolved_without_reusable_dated_geometry"
    assert sum(row["subject_id"].startswith("current:") and row["object_id"].startswith("state:")
               and row["predicate"] not in {"dated_surface_front_intersection", "source_reported_local_current_presence", "dated_geostrophic_streamline_segment_intersection"}
               for row in rows["relations"]) == coverage["current_state_pairs"] == 5600
    assert all(row["physical_relation"].startswith("unknown") for row in rows["relations"]
               if row["subject_id"].startswith("current:") and row["object_id"].startswith("state:")
               and row["predicate"] not in {"dated_surface_front_intersection", "source_reported_local_current_presence", "dated_geostrophic_streamline_segment_intersection"})
    assert all((row["role"], row["geometry"]["type"]) in
               {("editorial_locator", "Point"), ("dated_analyzed_surface_front", "LineString"),
                ("dated_partial_geostrophic_streamline", "LineString"),
                ("dated_operational_eddy_polygon", "Polygon"), ("dated_figure_ssh_contour_proxy", "Polygon")}
               for row in rows["geometries"])
    assert all(row["coordinate_reference_system"] == "OGC:CRS84" for row in rows["geometries"]
               if row["role"] not in {"dated_operational_eddy_polygon", "dated_figure_ssh_contour_proxy"})
    assert sum(row["role"] == "editorial_locator" and row["entity_id"].startswith("current:")
               for row in rows["geometries"]) == 134
    candidates = rows["named_eddy_footprint_candidates"]
    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate["entity_id"] == "eddy:published:kraken-2013" and candidate["observation_date"] == "2013-05-29"
    assert candidate["boundary_type"] == "figure_digitized_instantaneous_ssh_contour_proxy"
    proxy = next(row for row in rows["geometries"] if row["id"] == candidate["geometry_id"])
    assert proxy["candidate_id"] == candidate["id"] and proxy["role"] == "dated_figure_ssh_contour_proxy"
    assert proxy["source_id"] == candidate["source_id"] and proxy["source_snapshot_id"] == candidate["source_snapshot_id"]
    assert candidate["geometry_sha256"] == proxy["geometry_sha256"] == geometry_digest(proxy["geometry"])
    audit = load(PACKAGE / "source-ledgers" / "kraken-2013-figure2-state-audit.json")
    receipt = audit["dated_ssh_footprint_candidate"]
    assert proxy["geometry"] == receipt["nominal_geometry"]
    assert proxy["coordinate_reference_system"] == "figure_axis_lon_lat_degrees_unspecified_datum"
    assert candidate["segmentation_sensitivity_cases"] == receipt["segmentation_sensitivity_cases"]
    ring = proxy["geometry"]["coordinates"][0]
    pixels = proxy["source_pixel_ring"]
    axes = proxy["source_panel_axes_pixels"]
    assert len(ring) == len(pixels) == 457 and ring[0] == ring[-1] and pixels[0] == pixels[-1]
    assert Polygon(ring).is_valid and Polygon(ring).area > 0
    assert axes == receipt["source_panel_axes_pixels"] == [108, 313, 57, 661]
    # Independently reconstruct the nominal digitization from source pixels.
    def calibrated_ring(ticks):
        x98, x936, y31, y18 = ticks
        return [[-98 + (x - x98) * 4.4 / (x936 - x98), 31 - (y - y31) * 13 / (y18 - y31)] for x, y in pixels]
    assert all(abs(actual - expected) <= 5.1e-8 for point, expected_point in zip(ring, calibrated_ring(axes)) for actual, expected in zip(point, expected_point))
    state_shapes = load_states()
    nominal = Polygon([project(*point) for point in ring])
    assessments = {row["state_id"].removeprefix("state:"): row for row in candidate["state_assessments"]}
    assert set(assessments) == {"CAMR", "CARB"}
    for code, assessment in assessments.items():
        assert assessment["containment_assessment"] == "unresolved"
        assert abs(nominal.intersection(state_shapes[code]).area / nominal.area - assessment["nominal_display_area_fraction"]) < 1e-6
    assert assessments["CAMR"]["intersection_assessment"] == "robust_across_tested_calibrations"
    assert assessments["CARB"]["intersection_assessment"] == "calibration_sensitive_candidate"
    fractions = {"CAMR": [], "CARB": []}
    for shifts in itertools.product((-3, 3), repeat=4):
        polygon = Polygon([project(*point) for point in calibrated_ring([a+b for a,b in zip(axes, shifts)])])
        for code in fractions:
            fractions[code].append(polygon.intersection(state_shapes[code]).area / polygon.area)
    for code, values in fractions.items():
        expected = receipt["segmentation_sensitivity_cases"][1][code.lower()+"_footprint_area_fraction_range"]
        assert abs(min(values)-expected[0]) < 1e-6 and abs(max(values)-expected[1]) < 1e-6
    assert min(fractions["CAMR"]) > 0.9 and min(fractions["CARB"]) == 0 < max(fractions["CARB"])
    front_receipt = load(PACKAGE / "source-ledgers" / "gulf-stream-navo-front-20260928.json")
    front_states = load(PACKAGE / "source-ledgers" / "gulf-stream-navo-state-snapshot-20260928.json")
    assert front_states == build_front_state_snapshot(), "Dated front/state length join is stale"
    front_source = next(row for row in rows["sources"] if row.get("url") == front_receipt["source_url"])
    assert front_source["source_file_sha256"] == front_receipt["source_response_sha256"]
    assert front_source["product_date"] == front_receipt["date"]
    front_geometries = {row["front_side"]: row for row in rows["geometries"]
                        if row["role"] == "dated_analyzed_surface_front"}
    assert set(front_geometries) == set(front_receipt["fronts"]) == {"north_wall", "south_wall"}
    for side, row in front_geometries.items():
        assert row["entity_id"] == "current:gulf-stream-system"
        assert row["observation_date"] == front_receipt["date"] == front_states["date"]
        assert row["geometry"] == front_receipt["fronts"][side]["geometry"]
        assert row["observed_front_length_km"] == front_states["front_lengths_km"][side] > 0
        assert row["length_interpretation"] == front_states["length_limit"]
    front_relations = [row for row in rows["relations"]
                       if row["predicate"] == "dated_surface_front_intersection"]
    expected_front_pairs = {(code, side, kind)
                            for code, state in front_states["states"].items()
                            for side, kind in state["front_observations"].items()}
    assert len(front_relations) == coverage["dated_front_state_observations"] == len(expected_front_pairs)
    assert {(row["object_id"].removeprefix("state:"), row["front_side"], row["intersection_class"])
            for row in front_relations} == expected_front_pairs
    assert all(row["subject_id"] == "current:gulf-stream-system"
               and row["geometry_id"] == front_geometries[row["front_side"]]["id"]
               and row["physical_relation"] == "observed_front_intersects_approximate_state_current_passage_unresolved"
               for row in front_relations)
    assert all(row["observed_front_segment_length_km"] == front_states["states"][
        row["object_id"].removeprefix("state:")]["front_intersection_lengths_km"][row["front_side"]]
        and row["length_interpretation"] == front_states["length_limit"]
        for row in front_relations)
    geostrophic_source = load(PACKAGE / "source-ledgers" / "noaa-lsa-geostrophic-gulf-stream-20260925.json")
    geostrophic_path = load(PACKAGE / "source-ledgers" / "gulf-stream-geostrophic-path-20260925.json")
    assert geostrophic_path == build_geostrophic_path(), "Geostrophic path or state join is stale"
    assert geostrophic_path["source_response_sha256"] == geostrophic_source["source_response_sha256"]
    diagnosed_rows = rows["diagnosed_current_path_observations"]
    assert len(diagnosed_rows) == coverage["dated_diagnosed_current_path_observations"] == 1
    diagnosed = diagnosed_rows[0]
    assert diagnosed["entity_id"] == "current:gulf-stream-system"
    assert diagnosed["source_product_status"] == geostrophic_source["source_product_status"] == "Experimental"
    assert diagnosed["reach_length_km"] == geostrophic_path["representative"]["segment_length_km"]
    assert diagnosed["rank_eligible"] is False
    assert diagnosed["adjacent_seed_sensitivity"] == geostrophic_path["adjacent_seed_sensitivity"]
    diagnosed_geometry = next(row for row in rows["geometries"] if row["id"] == diagnosed["geometry_id"])
    assert diagnosed_geometry["role"] == "dated_partial_geostrophic_streamline"
    assert diagnosed_geometry["geometry"]["coordinates"] == geostrophic_path["representative"]["coordinates_lon_lat"]
    diagnosed_relations = [row for row in rows["relations"] if row["predicate"] == "dated_geostrophic_streamline_segment_intersection"]
    assert len(diagnosed_relations) == coverage["dated_diagnosed_current_state_intersections"] == 2
    assert {(row["object_id"], row["diagnosed_segment_length_km"]) for row in diagnosed_relations} == {
        ("state:" + relation["state_code"], relation["intersection_length_km"])
        for relation in geostrophic_path["state_relations"]}
    assert all(row["evidence_class"] == "derived_field" and row["geometry_id"] == diagnosed["geometry_id"]
               for row in diagnosed_relations)
    assert any(row["quantity"] == "dated_geostrophic_streamline_reach" and
               row["value"] == diagnosed["reach_length_km"] and row["rank_eligible"] is False
               for row in rows["measurements"])
    geojson = load(PACKAGE / "geometries.geojson")
    assert geojson["type"] == "FeatureCollection"
    geojson_rows = [row for row in rows["geometries"] if row["coordinate_reference_system"] == "OGC:CRS84"]
    assert coverage["geojson_excluded_unspecified_datum_geometry_ids"] == [row["id"] for row in rows["geometries"]
        if row["coordinate_reference_system"] != "OGC:CRS84"]
    assert len(geojson["features"]) == len(geojson_rows)
    for source_row, feature in zip(geojson_rows, geojson["features"]):
        assert feature["id"] == source_row["id"]
        assert feature["geometry"] == source_row["geometry"]
        assert feature["properties"] == {key: value for key, value in source_row.items() if key != "geometry"}
    assert sum(row["rank_eligible"] for row in rows["measurements"]) == coverage["ranked_current_lengths"] == 11
    ranked_measurements = [row for row in rows["measurements"] if row["quantity"] == "reported_length"
                           and row["rank_eligible"]]
    assert len(ranked_measurements) == 11
    slope = next(row for row in ranked_measurements if row["entity_id"] == "current:antarctic-slope")
    assert slope["id"] == "measurement:0029" and slope["value"] == 21000
    assert "Antarctic Peninsula" in slope["scope"]
    assert next(row for row in rows["length_assessments"] if row["entity_id"] == "current:antarctic-slope")["published_rank"] == 2
    assert {row["object_id"] for row in rows["relations"] if row["subject_id"] == "current:antarctic-slope"
            and row["predicate"] == "source_distinguished_current"} == {"current:acc", "current:antarctic-coastal"}
    assert all(row["role"] == "editorial_locator" for row in rows["geometries"] if row["entity_id"] == "current:antarctic-slope")
    alaska_coastal = next(row for row in ranked_measurements if row["entity_id"] == "current:alaska-coastal-gulf")
    assert alaska_coastal["id"] == "measurement:0028" and alaska_coastal["value"] == 1700
    assert claims_by_id[alaska_coastal["claim_id"]]["review_status"] == "not_individually_reviewed"
    assert next(row for row in rows["length_assessments"] if row["entity_id"] == "current:alaska-coastal-gulf")["published_rank"] == 10
    malvinas = next(row for row in ranked_measurements if row["entity_id"] == "current:falkland")
    assert malvinas["id"] == "measurement:0030" and malvinas["value"] == 2000
    assert "conference abstract" in malvinas["scope"] and "No reference centerline" in malvinas["scope"]
    assert next(row for row in rows["length_assessments"] if row["entity_id"] == "current:falkland")["published_rank"] == 9
    assert claims_by_id[malvinas["claim_id"]]["review_status"] == "not_individually_reviewed"
    malvinas_source = next(row for row in rows["sources"] if row["id"] == malvinas["source_id"])
    assert malvinas_source["url"] == "https://meetingorganizer.copernicus.org/EGU2009/EGU2009-12242.pdf"
    assert "EGU2009-12242" in malvinas_source["preferred_citation"]
    assert all(row["source_locator"] for row in ranked_measurements)
    assert all(row["source_locator"] == next(
        assessment["length_source_locator"] for assessment in rows["length_assessments"]
        if assessment["entity_id"] == row["entity_id"])
        for row in ranked_measurements)
    length_source = load(PACKAGE / "source-ledgers" / "ocean-current-length-evidence.json")
    span_source = load(PACKAGE / "source-ledgers" / "ocean-current-illustrated-spans.json")
    source_lengths = {"current:" + row["current_id"]: row for row in length_source["entries"]}
    source_spans = {"current:" + row["current_id"]: row for row in span_source["entries"]}
    assert len(rows["length_assessments"]) == len(source_lengths) == len(source_spans) == 100
    assert {row["entity_id"] for row in rows["length_assessments"]} == set(source_lengths)
    ranked_values = sorted((row["length_km"] for row in source_lengths.values() if row["rank_eligible"]), reverse=True)
    source_gates = {"current:" + row["current_id"]: row for row in
                    load(PACKAGE / "source-ledgers" / "ocean-current-gate-distances.json")["entries"]}
    for assessment in rows["length_assessments"]:
        original = source_lengths[assessment["entity_id"]]
        illustration = source_spans[assessment["entity_id"]]
        assert assessment["evidence_status"] == original["status"]
        assert assessment["rank_eligible"] == original["rank_eligible"]
        assert assessment["published_rank"] == (ranked_values.index(original["length_km"]) + 1
                                                if original["rank_eligible"] else None)
        assert assessment["published_length_km"] == original["length_km"]
        assert assessment["lower_bound_km"] == original["lower_bound_km"]
        gate = source_gates.get(assessment["entity_id"])
        assert assessment["gate_distance_sensitivity"] == (gate["gate_distance_sensitivity"] if gate else None)
        if gate:
            assert assessment["gate_distance_method_source_id"] in ids["sources"]
            assert assessment["evidence_status"] == "derived_lower_bound" and not assessment["rank_eligible"]
            scenario = assessment["gate_distance_sensitivity"]
            assert scenario["scenario_min_km"] <= gate["direct_gate_distance_km"] <= scenario["scenario_max_km"]
            assert 1 <= scenario["geographic_span_rank_best"] <= scenario["geographic_span_rank_worst"] <= 7
        else:
            assert assessment["gate_distance_method_source_id"] is None
        assert assessment["proposed_system_length_km"] == original["hypothesized_length_km"]
        assert assessment.get("length_source_locator") == original.get("length_source_locator")
        assert assessment["illustrated_span_km"] == illustration["longest_arrow_span_km"]
        assert assessment["illustrated_span_rank"] == illustration["illustrated_span_rank"]
        assert not assessment["rank_eligible"] or assessment["published_rank"] is not None
        assert assessment["rank_eligible"] or assessment["published_rank"] is None
        if assessment["length_source_id"]:
            assert assessment["length_source_id"] in ids["sources"]
        if assessment["illustration_source_id"]:
            assert assessment["illustration_source_id"] in ids["sources"]
        assert assessment["illustration_ledger_source_id"] in ids["sources"]
    derived_bounds = [row for row in rows["measurements"] if row["quantity"] == "length_lower_bound"
                      and row["evidence_status"] == "derived_lower_bound"]
    assert len(derived_bounds) == 7
    assert all(row["method_source_id"] in ids["sources"] and row["direct_gate_distance_km"] > row["value"]
               for row in derived_bounds)
    tile_ids = {row["tile_id"] for row in rows["tiles"]}
    assert len(tile_ids) == 70
    assert all(row["tile_id"] in tile_ids for row in rows["media"] if row.get("tile_id"))
    state_tile_source = load(ROOT / "research" / "nasa-perpetual-ocean-state-tile-join.json")
    expected_tile_pairs = {(code, match["tile_id"]): match["display_coverage_fraction"]
                           for code, state in state_tile_source["states"].items()
                           for match in state["matches"]}
    assert len(rows["tile_state_relations"]) == len(expected_tile_pairs) == 877
    for row in rows["tile_state_relations"]:
        code = row["state_id"].removeprefix("state:")
        assert row["state_id"] in ids["entities"] and row["tile_id"] in tile_ids
        assert row["predicate"] == "display_overlap" and row["physical_relation"] == "unresolved"
        assert 0 < row["display_coverage_fraction"] <= 1
        assert row["display_coverage_fraction"] == expected_tile_pairs[(code, row["tile_id"])]
    assert len(rows["observation_sets"]) == 12
    assert sum(row["detection_count"] for row in rows["observation_sets"]) == coverage["dated_noaa_detections"] == 92891
    state_ids = {row["source_record_id"] for row in rows["entities"] if row["type"] == "osw_state"}
    sources_by_id = {row["id"]: row for row in rows["sources"]}
    crossref = load(PACKAGE / "source-ledgers" / "ocean-motion-crossref-metadata.json")
    citation_by_doi = {row["doi"].casefold(): row for row in crossref["records"]}
    used_dois = {row["doi"].casefold() for row in rows["sources"]
                 if row["kind"] == "external" and row["record_count"] > 0 and row.get("doi")}
    assert crossref["requested_count"] == crossref["matched_count"] == len(citation_by_doi) == len(used_dois) == 66
    assert set(citation_by_doi) == used_dois
    assert all(row["status"] == "matched" for row in citation_by_doi.values())
    nasa_svs = load(PACKAGE / "source-ledgers" / "ocean-motion-nasa-svs-metadata.json")
    assert nasa_svs["requested_count"] == nasa_svs["matched_count"] == len(nasa_svs["records"]) == 7
    overrides = load(PACKAGE / "source-ledgers" / "ocean-motion-source-metadata-overrides.json")
    assert len(overrides["entries"]) == 70
    external_by_url = {row["url"]: row for row in rows["sources"] if row["kind"] == "external"}
    for record in nasa_svs["records"]:
        source = external_by_url[record["source_url"]]
        assert source["title"] == record["title"]
        assert source["publication_date"] == record["release_date"][:10]
        assert source["source_update_date"] == record["update_date"]
        assert source["metadata_response_sha256"] == record["response_sha256"]
    for override in overrides["entries"]:
        source = external_by_url[override["url"]]
        assert source["title"] == override["title"]
        if override.get("publisher"):
            assert source.get("publisher") == override["publisher"]
        assert source["metadata_evidence_url"] == override["metadata_evidence_url"]
        for field in ("metadata_note", "source_file_sha256", "source_file_url", "source_file_retrieved_date", "metadata_response_sha256", "credit_text", "doi", "source_update_date", "product_date"):
            if field in override:
                assert source[field] == override[field]
        if override.get("doi"):
            receipt_sha = source.get("citation_metadata_response_sha256") or source.get("metadata_response_sha256")
            assert receipt_sha == citation_by_doi[override["doi"].casefold()]["response_sha256"]
    for observation_set in rows["observation_sets"]:
        product_source = sources_by_id[observation_set["source_id"]]
        assert product_source["title"] == f"MUNSTER v1 daily eddy identification, {observation_set['date']}"
        assert product_source["product_date"] == observation_set["date"]
        assert product_source["product_version"] == "MUNSTER v1.0"
        assert product_source["metadata_evidence_url"] == "https://coastwatch.noaa.gov/cwn/products/experimental-eddy-products.html"
        path = PACKAGE / observation_set["observation_file"]
        snapshot = load(PACKAGE / sources_by_id[observation_set["source_snapshot_id"]]["path"])
        assert len(snapshot["entries"]) == observation_set["detection_count"]
        assert set(observation_set["state_counts"]) == state_ids
        assert all(observation_set["state_counts"][code] ==
                   {"contained": len(groups["contained"]), "intersected": len(groups["intersected"])}
                   for code, groups in snapshot["states"].items())
        with gzip.open(path, "rt", encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            count = 0
            for row, source_entry in zip(reader, snapshot["entries"]):
                count += 1
                assert row["id"] == "observation:" + source_entry["id"]
                assert row["observation_set_id"] == observation_set["id"]
                assert row["date"] == observation_set["date"]
                assert row["source_id"] == observation_set["source_id"]
                assert row["polarity"] in {"cyclonic", "anticyclonic"}
                assert -180 <= float(row["center_lon"]) <= 180 and -90 <= float(row["center_lat"]) <= 90
                assert float(row["radius_km"]) > 0 and float(row["area_km2"]) > 0
                assert [float(row["center_lon"]), float(row["center_lat"])] == source_entry["center"]
                assert float(row["radius_km"]) == source_entry["radius_km"]
                contained = json.loads(row["contained_states"])
                intersected = json.loads(row["intersected_states"])
                assert contained == source_entry["contained_states"] and intersected == source_entry["intersected_states"]
                assert set(contained + intersected) <= state_ids
                assert not set(contained) & set(intersected)
            assert count == observation_set["detection_count"]
            assert next(reader, None) is None
    for row in rows["sources"]:
        if row["kind"] == "OSW source ledger":
            assert (PACKAGE / row["path"]).is_file(), row
            assert (ROOT / row["repository_path"]).is_file(), row
    used_sources = {row["id"] for row in rows["sources"]
                    if row["kind"] == "external" and row["record_count"] > 0}
    pending_sources = {row["id"] for row in rows["sources"]
                       if row["id"] in used_sources and row["rights_status"].startswith("pending")}
    reviewed_sources = {row["id"] for row in rows["sources"]
                        if row["id"] in used_sources and row["rights_status"].startswith("reviewed")}
    assert len(pending_sources) == coverage["external_sources_pending_terms"]
    assert len(reviewed_sources) == coverage["external_sources_reviewed_for_current_use"]
    assert pending_sources.isdisjoint(reviewed_sources) and pending_sources | reviewed_sources == used_sources
    redistributed = {row["url"] for row in rows["sources"]
                     if row["id"] in used_sources and row["provider_asset_redistributed"]}
    munster_urls = {row["url"] for row in rows["sources"] if row["id"] in used_sources
                    and "MUNSTER_v1_eddyident_" in (row["url"] or "")}
    assert len(munster_urls) == 12
    assert redistributed == munster_urls | {
        "https://www.horizonmarine.com/loop-current-eddies",
        "https://ocean.weather.gov/gulf_stream_text.php",
        "https://www.ncei.noaa.gov/jag/navy/data/satellite_analysis/nafreddy.zip",
        "https://coastwatch.noaa.gov/data/pub0015/coastwatch/rads/sla/2026/rads_global_nrt_sla_20260925_20260926_001.nc"}
    assert Counter(row["material_use_class"] for row in rows["sources"]
                   if row["id"] in used_sources) == coverage["used_external_material_use_classes"]
    assert sum(bool(row.get("title")) for row in rows["sources"] if row["id"] in used_sources) == coverage["used_external_sources_with_titles"]
    assert coverage["used_external_sources_with_titles"] == len(used_sources)
    queue = load(PACKAGE / "source-review-queue.json")
    assert {row["source_id"] for row in queue} == used_sources
    assert len(queue) == len(used_sources)
    pending_rights = [row for row in queue if row["rights_review_status"] == "pending source terms audit"]
    assert len(pending_rights) == coverage["external_sources_pending_terms"] == 17
    assert {row["source_id"] for row in queue
            if not row["citation_review_status"].startswith("reviewed;")} == {
                row["source_id"] for row in pending_rights}
    assert coverage["external_sources_reviewed_for_current_use"] == 95
    assert sum(row["provider_asset_redistributed"] for row in pending_rights) == 16
    assert sum(row["material_use_class"] == "derived_cartographic_measurements"
               for row in pending_rights) == 1
    cartographic_review = next(row for row in pending_rights
                              if row["material_use_class"] == "derived_cartographic_measurements")
    assert cartographic_review["record_count"] == sum(
        row.get("illustration_source_id") == cartographic_review["source_id"]
        for row in rows["length_assessments"]) == 27
    assert sum(row["citation_review_status"] ==
               "reviewed; Crossref DOI, authors, title and year recorded" for row in queue) == 57
    linked_factual = [row for row in queue if row["material_use_class"] in {
                      "source_scoped_factual_claim", "figure_derived_measurement_and_factual_claim"}]
    assert len(linked_factual) == 84
    assert sum(row["material_use_class"] == "figure_derived_measurement_and_factual_claim"
               for row in linked_factual) == 1
    assert sum(row["citation_review_status"] ==
               "reviewed; source-page or institutional citation recorded"
               and bool(row["preferred_citation"]) for row in linked_factual) == 11
    assert all(row["citation_review_status"].startswith("reviewed;") for row in linked_factual)
    nasa_rows = [row for row in queue if "svs.gsfc.nasa.gov" in row["url"]]
    assert len(nasa_rows) == 10
    assert all(row["citation_review_status"] ==
               "reviewed; NASA item credit and page citation recorded"
               and row["preferred_citation"] and row["credit_text"] for row in nasa_rows)
    assert not any("uskess.whoi.edu" in row["url"] for row in queue)
    sources_by_id = {row["id"]: row for row in rows["sources"]}
    assert all(row["record_count"] == sources_by_id[row["source_id"]]["record_count"] and
               row["derived_detection_count"] == sources_by_id[row["source_id"]]["derived_detection_count"] and
               row["total_packaged_row_count"] == row["record_count"] + row["derived_detection_count"] and
               row["material_use_class"] == sources_by_id[row["source_id"]]["material_use_class"] and
               row["provider_asset_redistributed"] == sources_by_id[row["source_id"]]["provider_asset_redistributed"] and
               set(row["affected_entity_ids"]) <= ids["entities"] and
               row["affected_entity_count"] == len(row["affected_entity_ids"])
               for row in queue)
    assert sum(row["derived_detection_count"] for row in queue) == coverage["dated_noaa_detections"]
    assert all(row["total_packaged_row_count"] >= row["record_count"] for row in queue)
    assert queue == sorted(queue, key=lambda row: (-row["total_packaged_row_count"],
                                                    -row["affected_entity_count"], row["source_id"]))
    assert all(row["rights_review_status"] == sources_by_id[row["source_id"]]["rights_status"] for row in queue)
    reviews = load(ROOT / "research" / "ocean-motion-source-use-reviews.json")
    assert {row["url"] for row in reviews["entries"]} == {row["url"] for row in queue
        if row["source_id"] in reviewed_sources}
    for review in reviews["entries"]:
        item = next(row for row in queue if row["url"] == review["url"])
        assert item["material_use_class"] == review["material_use_class"]
        assert item["rights_review_status"] == review["rights_review_status"]
        assert item["citation_review_status"] == review["citation_review_status"]
        assert item["policy_reference_url"] == review["policy_reference_url"]
        assert item["rights_review_note"] == review["review_note"]
        assert item["rights_review_date"] == review.get("review_date", reviews["review_date"])
        assert not item["provider_asset_redistributed"]
    assert next(row for row in queue if row["url"] == "https://www.horizonmarine.com/loop-current-eddies")["material_use_class"] == "compiled_name_and_date_records"
    assert next(row for row in queue if row["url"] == "https://www.nasa.gov/centers-and-facilities/jpl/seal-takes-ocean-heat-transport-data-to-new-depths/")["material_use_class"] == "source_scoped_factual_claim"
    for row in queue:
        parsed = urlsplit(row["url"])
        if parsed.netloc.lower() not in {"doi.org", "www.doi.org", "dx.doi.org"}:
            continue
        doi = unquote(parsed.path.lstrip("/"))
        citation = citation_by_doi[doi.casefold()]
        assert citation["status"] == "matched"
        assert row["title"] == citation["title"] and row["publisher"] == citation["publisher"]
        assert sources_by_id[row["source_id"]]["metadata_response_sha256"] == citation["response_sha256"]
    assert [row["total_packaged_row_count"] for row in queue] == sorted(
        (row["total_packaged_row_count"] for row in queue), reverse=True)
    with (PACKAGE / "source-review-queue.csv").open(encoding="utf-8", newline="") as stream:
        assert sum(1 for _ in csv.DictReader(stream)) == len(queue)
    print("Ocean motion release candidate valid:", len(rows["entities"]), "entities,",
          len(rows["relations"]), "relations")


if __name__ == "__main__":
    check()
