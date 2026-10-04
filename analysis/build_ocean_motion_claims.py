"""Normalize release relation and measurement assertions into claim records.

Claims preserve the existing source link and explicitly expose missing
source locators, method descriptions, and individual review. They do not
upgrade atlas or unresolved relations into physical observations.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date


def review_fingerprint(claim: dict) -> str:
    """Bind a review to the exact source, assertion, locator, and method."""
    reviewed_fields = {key: value for key, value in claim.items()
                       if key not in {"reviewer", "review_date", "review_status", "review_note",
                                      "review_fingerprint"}}
    canonical = json.dumps(reviewed_fields, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def apply_claim_reviews(claims: list[dict], review_ledger: dict) -> None:
    if review_ledger.get("schema") != "osw.ocean-motion-claim-reviews.v1":
        raise ValueError("Unknown claim review ledger schema")
    by_id = {claim["id"]: claim for claim in claims}
    seen = set()
    for decision in review_ledger["decisions"]:
        claim_id = decision["claim_id"]
        if claim_id in seen or claim_id not in by_id:
            raise ValueError(f"Duplicate or unknown claim review: {claim_id}")
        seen.add(claim_id)
        claim = by_id[claim_id]
        if decision["review_fingerprint"] != claim["review_fingerprint"]:
            raise ValueError(f"Stale claim review: {claim_id}")
        if decision["review_status"] not in {"verified", "needs_revision", "rejected"}:
            raise ValueError(f"Invalid claim review decision: {claim_id}")
        if not all(isinstance(decision.get(key), str) and decision[key].strip()
                   for key in ("reviewer", "review_date", "review_note")):
            raise ValueError(f"Incomplete claim review: {claim_id}")
        if date.fromisoformat(decision["review_date"]).isoformat() != decision["review_date"]:
            raise ValueError(f"Non-ISO claim review date: {claim_id}")
        claim.update({key: decision[key] for key in ("reviewer", "review_date", "review_status", "review_note")})


def build_claims(relations: list[dict], measurements: list[dict],
                 tile_state_relations: list[dict], named_eddy_state_assessments: list[dict],
                 named_eddy_source_observations: list[dict],
                 named_current_source_observations: list[dict],
                 operational_eddy_state_observations: list[dict],
                 diagnosed_current_path_observations: list[dict],
                 sources: dict[str, dict],
                 method_by_source_id: dict[str, str],
                 internal_locators: dict[str, str],
                 classification_vocabularies: list[dict] | None = None,
                 footprint_candidates: list[dict] | None = None,
                 footprint_movie_context: list[dict] | None = None) -> list[dict]:
    claims = []
    groups = (("relations", relations), ("measurements", measurements),
              ("tile_state_relations", tile_state_relations),
              ("named_eddy_state_assessments", named_eddy_state_assessments),
              ("named_eddy_source_observations", named_eddy_source_observations),
              ("named_current_source_observations", named_current_source_observations),
              ("operational_eddy_state_observations", operational_eddy_state_observations),
              ("diagnosed_current_path_observations", diagnosed_current_path_observations),
              ("classification_vocabularies", classification_vocabularies or []),
              ("named_eddy_footprint_candidates", footprint_candidates or []),
              ("footprint_movie_context", footprint_movie_context or []))
    for collection_name, records in groups:
        for record in records:
            claim_id = "claim:" + record["id"]
            record["claim_id"] = claim_id
            source = sources[record["source_id"]]
            locator = record.get("source_locator") or internal_locators.get(record["id"])
            if not locator and source.get("url") and "#" in source["url"]:
                locator = source["url"]
            internal_record = (record["id"] in internal_locators and
                               source.get("path") in {
                                   "source-ledgers/ocean-eddy-name-inventory.json",
                                   "source-ledgers/nasa-perpetual-ocean-objects.json",
                                   "source-ledgers/kraken-2013-figure2-state-audit.json"})
            locator_status = ("internal_ledger_record" if internal_record else
                              "internal_ledger_row" if record["id"] in internal_locators and source.get("path") else
                              "specific" if locator else "source_only_no_precise_locator")
            method = (record.get("state_assignment_method") or record.get("method") or
                      method_by_source_id.get(record["source_id"]))
            if collection_name == "named_eddy_state_assessments":
                method = ("OSW georeferencing of dated Figure 2 red pixels and the 29 May closed SSH contour against approximate state geometry; "
                          "CAMR has a robust dated contour intersection, but CARB intersection varies with axis calibration and whole-ring containment is unresolved"
                          if record["evidence_status"] == "figure_derived_red_curve_candidate" else
                          "OSW georeferencing of the 29 May closed SSH contour; CARB intersection is sensitive to figure axis calibration and is a candidate only"
                          if record["evidence_status"] == "figure_derived_dated_ssh_contour_candidate" else
                          "OSW projection of a paper-reported approximate dated eddy-center point into a coast-masked display state; no whole-eddy footprint or containment is inferred"
                          if record["evidence_status"] == "published_observed_center_point_candidate" else
                          "OSW source-set eddy/state assessment from regional gateway or point evidence; "
                          "without a dated footprint, physical containment and intersection remain unknown")
            elif collection_name == "operational_eddy_state_observations":
                method = "Dated NAVO polygon containment in an approximate coast-masked OSW display state"
            elif collection_name == "diagnosed_current_path_observations":
                method = "Frozen-time geodesic midpoint integration of NOAA LSA surface geostrophic velocity; see source snapshot"
            method_source_id = record.get("method_source_id") or record.get("source_snapshot_id")
            if collection_name == "operational_eddy_state_observations":
                method_source_id = record["state_join_id"]
            observation_time = (record.get("observation_date") or
                                ({"start": record["observation_start"], "end": record["observation_end"]}
                                 if record.get("observation_start") and record.get("observation_end") else None))
            date_parts = source.get("publication_date_parts") or []
            source_date = (source.get("publication_date") or source.get("product_date") or
                           "-".join(str(part).zfill(2) if index else str(part)
                                    for index, part in enumerate(date_parts)) or None)
            if collection_name == "measurements":
                claim = {
                    "id": claim_id, "target_collection": collection_name, "target_id": record["id"],
                    "subject_id": record["entity_id"], "predicate": record["quantity"],
                    "object_id": None, "value": record["value"], "unit": record["unit"],
                    "scope": record.get("scope"), "evidence_class": record["evidence_status"],
                    "assertion_status": "reported_or_derived_measurement",
                }
            elif collection_name == "named_eddy_state_assessments":
                claim = {
                    "id": claim_id, "target_collection": collection_name, "target_id": record["id"],
                    "subject_id": record["eddy_id"], "predicate": "named_eddy_state_assessment",
                    "object_id": record["state_id"], "value": None, "unit": None,
                    "scope": record["physical_relation"],
                    "evidence_class": record["evidence_status"],
                    "assertion_status": "unresolved_assessment",
                }
            elif collection_name == "named_eddy_source_observations":
                claim = {
                    "id": claim_id, "target_collection": collection_name, "target_id": record["id"],
                    "subject_id": record["entity_id"], "predicate": "published_named_eddy_observation",
                    "object_id": None, "value": None, "unit": None,
                    "scope": record["physical_state_relation"], "evidence_class": "source_identified",
                    "assertion_status": "recorded_observation",
                }
            elif collection_name == "named_current_source_observations":
                claim = {
                    "id": claim_id, "target_collection": collection_name, "target_id": record["id"],
                    "subject_id": record["entity_id"], "predicate": "source_reported_local_current_presence",
                    "object_id": record["state_id"], "value": None, "unit": None,
                    "scope": record["physical_relation"], "evidence_class": "source_associated",
                    "assertion_status": "recorded_relation",
                }
            elif collection_name == "operational_eddy_state_observations":
                claim = {
                    "id": claim_id, "target_collection": collection_name, "target_id": record["id"],
                    "subject_id": record["operational_eddy_id"], "predicate": record["relation"],
                    "object_id": record["state_id"], "value": None, "unit": None,
                    "scope": record["relation_limit"], "evidence_class": "observed_geometry",
                    "assertion_status": "recorded_relation",
                }
            elif collection_name == "diagnosed_current_path_observations":
                claim = {
                    "id": claim_id, "target_collection": collection_name, "target_id": record["id"],
                    "subject_id": record["entity_id"], "predicate": "dated_geostrophic_streamline_reach",
                    "object_id": None, "value": record["reach_length_km"], "unit": "km",
                    "scope": record["physical_limit"], "evidence_class": "derived_field",
                    "assertion_status": "recorded_observation",
                }
            elif collection_name == "footprint_movie_context":
                claim = {
                    "id": claim_id, "target_collection": collection_name, "target_id": record["id"],
                    "subject_id": record["entity_id"], "predicate": "figure_footprint_movie_geographic_context",
                    "object_id": None, "value": None, "unit": None,
                    "scope": record["physical_limit"], "evidence_class": "atlas_geometry",
                    "assertion_status": "navigation_only_no_event_identity",
                    "navigation_support": {key: value for key, value in record.items() if key not in {"id", "claim_id"}},
                }
            elif collection_name == "named_eddy_footprint_candidates":
                claim = {
                    "id": claim_id, "target_collection": collection_name, "target_id": record["id"],
                    "subject_id": record["entity_id"], "predicate": "dated_figure_ssh_footprint_candidate",
                    "object_id": None, "value": None, "unit": None,
                    "scope": record["physical_limit"], "evidence_class": "figure_digitized",
                    "assertion_status": "recorded_footprint_candidate_not_verified_boundary",
                    "footprint_support": {key: value for key, value in record.items() if key not in {"id", "claim_id", "review_status"}},
                }
            elif collection_name == "classification_vocabularies":
                claim = {
                    "id": claim_id, "target_collection": collection_name, "target_id": record["id"],
                    "subject_id": record["entity_id"], "predicate": "source_scoped_regime_vocabulary",
                    "object_id": None, "value": None, "unit": None,
                    "scope": record["scope"], "evidence_class": "source_identified",
                    "assertion_status": "recorded_vocabulary_not_observed_assignment",
                    "vocabulary_definition": {key: record[key] for key in
                        ("terms", "density_variable_note", "assignment_requirements",
                         "not_equivalent_to", "assignment_status", "assignments")},
                }
            else:
                physical = record.get("physical_relation")
                unresolved = record["evidence_class"] == "unresolved" or (
                    isinstance(physical, str) and physical.startswith("unknown"))
                claim = {
                    "id": claim_id, "target_collection": collection_name, "target_id": record["id"],
                    "subject_id": record.get("subject_id") or "tile:" + record["tile_id"],
                    "predicate": record["predicate"],
                    "object_id": record.get("object_id") or record["state_id"],
                    "value": None, "unit": None,
                    "scope": record.get("length_interpretation") or physical,
                    "evidence_class": record["evidence_class"],
                    "assertion_status": "unresolved_assessment" if unresolved else "recorded_relation",
                }
            claim.update({
                "source_id": record["source_id"],
                "source_snapshot_id": record.get("source_snapshot_id"),
                "source_locator": locator,
                "source_locator_status": locator_status,
                "method": method,
                "method_source_id": method_source_id,
                "method_status": "described" if method else "method_reference_only" if method_source_id else "method_not_recorded",
                "observation_time": observation_time,
                "source_date": source_date,
                "reviewer": None,
                "review_date": None,
                "review_status": "not_individually_reviewed",
                "review_note": None,
                "support_claim_id": record.get("support_claim_id") or ("claim:" + record["observation_id"] if record.get("observation_id") else None),
            })
            if collection_name == "named_current_source_observations" and record.get("reported_observation_points_lon_lat"):
                claim["observation_support"] = {key: record[key] for key in
                    ("reported_observation_points_lon_lat", "observation_time_precision", "observation_depth_note", "state_boundary_limit")}
            claim["review_fingerprint"] = review_fingerprint(claim)
            claims.append(claim)
    assert len({row["id"] for row in claims}) == len(claims)
    return claims
