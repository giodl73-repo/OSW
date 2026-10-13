//! Dated figure proxy; no physical boundary or recurring season is admitted.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
pub(crate) const PATH: &str = "research/ursa-2021-0307-figure-contour-audit.json";
const SHA: &str = "465f2a15cad95a782617ce9981fc0846514bbc0aa1c217472f788132fb59fd09";
const ID: &str = "footprint_candidate:ursa:2021-03-07";
const OWNER: &str = "eddy:published:ursa-2021";
pub(crate) fn validate_raw(raw: &str) -> Result<(), String> {
    if format!("{:x}", Sha256::digest(raw.as_bytes())) != SHA {
        return Err("Ursa contour: changed source, calibration, failed cases or scope".into());
    }
    Ok(())
}
fn document(bundle: &Bundle) -> Result<Value, String> {
    let r = &bundle.manifest["atlas_receipts"][PATH];
    let raw = r["source_json"]
        .as_str()
        .ok_or("Ursa contour: missing source audit")?;
    validate_raw(raw)?;
    if r["source_sha256"] != SHA || bundle.manifest["input_sha256"][PATH] != SHA {
        return Err("Ursa contour: stale audit receipt".into());
    }
    serde_json::from_str(raw).map_err(|e| e.to_string())
}
pub(crate) fn validate(bundle: &Bundle) -> Result<(), String> {
    let needed = !bundle.manifest["atlas_receipts"][PATH].is_null()
        || !bundle.manifest["input_sha256"][PATH].is_null()
        || bundle.collections.values().flatten().any(|r| {
            r["id"] == ID
                || r["candidate_id"] == ID
                || r["footprint_candidate_id"] == ID
                || (r["entity_id"] == OWNER && r["role"] == "dated_figure_ssh_contour_proxy")
        });
    if !needed {
        return Ok(());
    }
    let doc = document(bundle)?;
    for stem in [
        "source_document",
        "source_image",
        "source_panel_audit",
        "acquisition",
        "state_geometry",
        "protocol",
    ] {
        let file = doc[format!("{stem}_file")]
            .as_str()
            .ok_or("Ursa contour: missing dependency")?;
        if bundle.manifest["input_sha256"][file] != doc[format!("{stem}_sha256")] {
            return Err("Ursa contour: changed original, protocol or state geometry".into());
        }
    }
    let rows = bundle
        .collections
        .get("named_eddy_footprint_candidates")
        .ok_or("Ursa contour: missing candidates")?;
    let matched: Vec<_> = rows
        .iter()
        .filter(|r| r["id"] == ID || r["entity_id"] == OWNER)
        .collect();
    if matched.len() != 1 {
        return Err("Ursa contour: missing or duplicate candidate".into());
    }
    let candidate = matched[0];
    let mut expected = json!({"entity_id":OWNER,"observation_date":doc["observation_date"],"source_id":"source:905e5cc303aaceab",
        "source_snapshot_id":"source:814dda03fd8926bd","source_locator":doc["source_locator"],"method":doc["method"],
        "id":ID,"geometry_id":"geometry:0159","geometry_sha256":doc["geometry_sha256"],
        "boundary_type":"figure_digitized_instantaneous_ssh_contour_proxy","review_status":"not_individually_reviewed",
        "physical_limit":doc["physical_limit"],"source_audit_file":PATH,"claim_id":"claim:footprint_candidate:ursa:2021-03-07"});
    for key in [
        "identity_status",
        "state_assessments",
        "source_document_sha256",
        "source_image_sha256",
        "source_image_file",
        "state_geometry_sha256",
        "source_panel_axes_pixels",
        "coordinate_reference_status",
        "segmentation_sensitivity_cases",
        "rejected_segmentation_cases",
        "scenario_polygon_count",
        "scenario_attempt_count",
        "physical_boundary_admitted",
        "annual_extrema_eligible",
        "seasonal_playback_eligible",
        "source_credit",
        "source_license_url",
    ] {
        expected[key] = doc[key].clone();
    }
    if *candidate != expected {
        return Err("Ursa contour: candidate projection or scientific scope changed".into());
    }
    let geometry = bundle
        .collections
        .get("geometries")
        .and_then(|rs| rs.iter().find(|r| r["id"] == candidate["geometry_id"]))
        .ok_or("Ursa contour: missing geometry")?;
    let expected_geometry = json!({"entity_id":OWNER,"observation_date":doc["observation_date"],"source_id":candidate["source_id"],
        "source_snapshot_id":candidate["source_snapshot_id"],"source_locator":doc["source_locator"],"method":doc["method"],
        "id":"geometry:0159","role":"dated_figure_ssh_contour_proxy","geometry":doc["nominal_geometry"],
        "geometry_sha256":doc["geometry_sha256"],"candidate_id":ID,"coordinate_reference_system":doc["coordinate_reference_system"],
        "coordinate_reference_status":doc["coordinate_reference_status"],
        "positional_uncertainty":"Source-image threshold/stroke/axis scenarios; no physical uncertainty bound or survey accuracy established.",
        "source_pixel_ring":doc["source_pixel_ring"],"source_panel_axes_pixels":doc["source_panel_axes_pixels"]});
    if *geometry != expected_geometry {
        return Err("Ursa contour: geometry projection changed".into());
    }
    for assessment in doc["state_assessments"]
        .as_array()
        .ok_or("Ursa contour: missing states")?
    {
        let state = &assessment["state_id"];
        let row = bundle
            .collections
            .get("named_eddy_state_assessments")
            .and_then(|rs| {
                rs.iter()
                    .find(|r| r["eddy_id"] == OWNER && r["state_id"] == *state)
            })
            .ok_or("Ursa contour: missing dated state assessment")?;
        if row["footprint_candidate_id"] != ID
            || row["dated_ssh_contour_observation_date"] != doc["observation_date"]
            || row["dated_ssh_contour_area_fraction_range"]
                != assessment["display_area_fraction_range"]
            || row["dated_ssh_contour_nominal_area_fraction"]
                != assessment["nominal_display_area_fraction"]
            || row["dated_ssh_contour_assessment"] != assessment["intersection_assessment"]
            || row["evidence_status"] != "figure_derived_dated_ssh_contour_candidate"
            || row["physical_relation"]
                != "dated_ssh_proxy_intersection_candidate_whole_eddy_relation_unresolved"
            || !row["reported_center_lon_lat"].is_null()
            || !row["observed_center_date"].is_null()
            || row["point_evidence_types"] != json!([])
            || row["source_id"] != candidate["source_snapshot_id"]
        {
            return Err(
                "Ursa contour: state projection or unresolved physical relation changed".into(),
            );
        }
    }
    if bundle
        .collections
        .get("named_eddy_state_assessments")
        .into_iter()
        .flatten()
        .any(|r| {
            r["eddy_id"] == OWNER
                && r["state_id"] != "state:CAMR"
                && r["state_id"] != "state:CARB"
                && r["physical_relation"] != "unknown_no_dated_eddy_footprint"
        })
    {
        return Err(
            "Ursa contour: unsupported physical state relation outside the candidate".into(),
        );
    }
    Ok(())
}
pub(crate) fn overlay(bundle: &Bundle, candidate: &Value) -> Result<Value, String> {
    if candidate["id"] != ID {
        return Ok(Value::Null);
    }
    validate(bundle)?;
    let doc = document(bundle)?;
    let points = doc["source_pixel_ring"]
        .as_array()
        .ok_or("Ursa contour: missing pixel ring")?;
    let mut path = String::new();
    for (i, p) in points.iter().enumerate() {
        path.push_str(&format!(
            "{}{} {} ",
            if i == 0 { "M" } else { "L" },
            p[0],
            p[1]
        ));
    }
    path.push('Z');
    Ok(
        json!({"engine":"rust-osw-query-v1","view_box":[1120,642,264,288],"image_size_pixels":[2008,1651],
        "image_href":format!("../{}",doc["source_image_file"].as_str().unwrap()),"polygon_d":path,
        "aria_label":"Ursa event, 7 March 2021: original Figure 3 with OSW digitized contour overlay",
        "source_document":PATH,"source_pointer":"/source_pixel_ring",
        "caption":"Original source panel with OSW threshold-70 outer-stroke trace. 68 valid calibration polygons; two non-simple threshold-100 paths rejected and retained. Figure-axis datum and projection unspecified. Ring attribution and physical boundary remain unverified."}),
    )
}
pub(crate) fn atlas_views(bundle: &Bundle) -> Result<Value, String> {
    let mut views = json!({});
    if let Some(rows) = bundle.collections.get("named_eddy_footprint_candidates") {
        for candidate in rows {
            let owner = candidate["entity_id"]
                .as_str()
                .ok_or("Missing footprint owner")?;
            let geometry = bundle
                .collections
                .get("geometries")
                .and_then(|rs| rs.iter().find(|g| g["id"] == candidate["geometry_id"]))
                .ok_or("Missing footprint geometry")?;
            let mut plot = crate::object_plot::named_scene(geometry);
            plot["source_panel_overlay"] = overlay(bundle, candidate)?;
            let contexts: Vec<_> = bundle
                .collections
                .get("footprint_movie_context")
                .into_iter()
                .flatten()
                .filter(|r| r["footprint_candidate_id"] == candidate["id"])
                .collect();
            views[owner] =
                json!({"candidate":candidate,"plot_scene":plot,"movie_contexts":contexts});
        }
    }
    Ok(views)
}
