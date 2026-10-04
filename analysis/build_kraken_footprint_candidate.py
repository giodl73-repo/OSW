"""Normalize the pinned figure audit as a dated, unverified SSH proxy."""
import hashlib
import json

def geometry_digest(geometry):
    return hashlib.sha256(json.dumps(geometry, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()

def build(audit, geometry_id, source_id, snapshot_id):
    evidence = audit["dated_ssh_footprint_candidate"]
    candidate_id = "footprint_candidate:kraken:2013-05-29"
    geometry = evidence["nominal_geometry"]
    digest = geometry_digest(geometry)
    shared = {"entity_id": "eddy:published:kraken-2013", "observation_date": "2013-05-29",
              "source_id": source_id, "source_snapshot_id": snapshot_id,
              "source_locator": evidence["source_locator"], "method": evidence["method"]}
    geometry_row = {**shared, "id": geometry_id, "role": "dated_figure_ssh_contour_proxy",
        "coordinate_reference_system": evidence["coordinate_reference_system"],
        "coordinate_reference_status": evidence["coordinate_reference_status"],
        "positional_uncertainty": "Manual axis calibration, JPEG line width and color segmentation; see three thresholds and +/-3 source-pixel cases. No survey-error bound is supplied.",
        "geometry": geometry, "geometry_sha256": digest, "candidate_id": candidate_id,
        "source_pixel_ring": evidence["source_pixel_ring"],
        "source_panel_axes_pixels": evidence["source_panel_axes_pixels"]}
    cases = evidence["segmentation_sensitivity_cases"]
    assessments = []
    for code in ("CAMR", "CARB"):
        ranges = [case[code.lower()+"_footprint_area_fraction_range"] for case in cases]
        assessments.append({"state_id": "state:" + code,
            "intersection_assessment": "robust_across_tested_calibrations" if code == "CAMR" else "calibration_sensitive_candidate",
            "containment_assessment": "unresolved",
            "nominal_display_area_fraction": cases[1]["nominal_footprint_area_fraction_by_state"][code],
            "display_area_fraction_range": [min(value[0] for value in ranges), max(value[1] for value in ranges)]})
    candidate = {**shared, "id": candidate_id, "geometry_id": geometry_id,
        "geometry_sha256": digest, "boundary_type": "figure_digitized_instantaneous_ssh_contour_proxy",
        "physical_limit": evidence["claim_limit"], "review_status": "not_individually_reviewed",
        "state_assessments": assessments,
        **{key: evidence[key] for key in ("source_pdf_sha256", "embedded_figure_sha256", "state_geometry_sha256", "source_panel_axes_pixels", "nominal_segmentation_case_index", "segmentation_sensitivity_cases", "coordinate_reference_status")}}
    return geometry_row, candidate
