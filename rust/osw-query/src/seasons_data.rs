//! Checked presentation sources for the seasonal evidence page.
use crate::{Bundle, Store};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::BTreeSet;
const SOURCES: [(&str, &str, &str); 4] = [
    (
        "widths",
        "research/ocean-current-width-inventory.json",
        "osw.current-width-inventory.v1",
    ),
    (
        "routes",
        "research/ocean-current-reference-path-candidates.json",
        "osw.current-reference-path-candidates.v1",
    ),
    (
        "frames",
        "research/ocean-current-seasonal-route-frames.json",
        "osw.current-seasonal-route-frames.v1",
    ),
    (
        "directions",
        "research/new-guinea-coastal-current-seasonal-direction-scope-audit.json",
        "osw.current-seasonal-direction-scope-audit.v1",
    ),
];
fn documents(bundle: &Bundle) -> Result<Value, String> {
    let mut docs = json!({});
    for (key, path, schema) in SOURCES {
        let receipt = &bundle.manifest["seasons_receipts"][key];
        let raw = receipt["source_json"]
            .as_str()
            .ok_or("Missing seasonal source bytes")?;
        let hash = format!("{:x}", Sha256::digest(raw.as_bytes()));
        if receipt["source_file"] != path
            || receipt["source_sha256"] != hash
            || bundle.manifest["input_sha256"][path] != hash
        {
            return Err("Changed seasonal source receipt".into());
        }
        let doc: Value = serde_json::from_str(raw).map_err(|e| e.to_string())?;
        if doc["schema"] != schema {
            return Err("Unsupported seasonal source schema".into());
        }
        docs[key] = doc;
    }
    Ok(docs)
}
fn projection(source: &Value, actual: &Value) -> bool {
    match source {
        Value::Object(fields) => fields
            .iter()
            .all(|(k, v)| actual.get(k).is_some_and(|a| projection(v, a))),
        _ => source == actual,
    }
}
fn adcp_width_scope(row: &Value) -> Result<(), String> {
    let id = row["id"].as_str().unwrap_or("");
    if row["phase_kind"] != "survey_layer_median_threshold_width"
        && row.get("adcp_threshold_context").is_none()
        && !id.starts_with("agulhas-return-boebel-2003-adcp-")
    {
        return Ok(());
    }
    let crossing = id
        .strip_prefix("agulhas-return-boebel-2003-adcp-")
        .ok_or("ADCP width identity mismatch")?;
    let (width, error, projection) = match crossing {
        "a" => (48, 14, 1),
        "b1" => (73, 18, 6),
        "b2" => (78, 18, 1),
        "c" => (48, 18, 17),
        _ => return Err("ADCP width crossing mismatch".into()),
    };
    let context = &row["adcp_threshold_context"];
    if row["current_id"] != "agulhas-return"
        || row["phase_kind"] != "survey_layer_median_threshold_width"
        || row["measurement_type"] != "published_multilayer_ADCP_threshold_width"
        || row["width_metric"]
            != "median_across_ADCP_depth_bins_of_flow_normal_half_maximum_isotach_distance"
        || row["boundary_sides"] != "paired_half_maximum_isotachs_per_bin_median"
        || row["approximate_width_km"] != width
        || row["reported_total_error_km"] != error
        || context["crossing_id"] != crossing
        || context["velocity_threshold_fraction"] != 0.5
        || context["reported_projection_uncertainty_km"] != projection
        || context["projection_error_is_included_in_total"] != true
        || context["campaign_context_year"] != 1997
        || context["deepest_reported_ADCP_bin_m"] != json!([325, 375])
        || ["confidence_level"]
            .iter()
            .any(|k| context.get(k) != Some(&Value::Null))
        || [
            "boundary_coordinates_extracted",
            "depth_bin_range_is_fixed_width_layer",
            "exact_crossing_dates_extracted",
        ]
        .iter()
        .any(|k| context.get(k) != Some(&json!(false)))
        || [
            "width_range_km",
            "observed_period",
            "calendar_months",
            "section_geometry",
            "fixed_layer_bounds_m",
        ]
        .iter()
        .any(|k| row.get(k) != Some(&Value::Null))
        || [
            "whole_current_representative",
            "width_rank_eligible",
            "annual_extrema_eligible",
            "seasonal_playback_eligible",
            "full_width_inference_eligible",
            "is_confidence_interval",
        ]
        .iter()
        .any(|k| row.get(k) != Some(&json!(false)))
    {
        return Err("ADCP layer-median width or source-error scope mismatch".into());
    }
    Ok(())
}
pub fn validate(bundle: &Bundle) -> Result<(), String> {
    if bundle.manifest.get("seasons_receipts").is_none() {
        return Ok(());
    }
    let docs = documents(bundle)?;
    for (key, field, collection) in [
        ("widths", "measurements", "widths"),
        ("routes", "candidates", "reference_routes"),
        ("frames", "frames", "seasonal_routes"),
    ] {
        let source = docs[key][field]
            .as_array()
            .ok_or("Missing seasonal source records")?;
        let actual = bundle
            .collections
            .get(collection)
            .ok_or("Missing seasonal query collection")?;
        let mut ids = BTreeSet::new();
        if source.len() != actual.len() {
            return Err("Incomplete seasonal source projection".into());
        }
        for row in source {
            if key == "widths" {
                adcp_width_scope(row)?;
            }
            let id = row["id"]
                .as_str()
                .ok_or("Missing seasonal record identity")?;
            if !ids.insert(id) || !actual.iter().any(|r| r["id"] == id && projection(row, r)) {
                return Err("Seasonal source differs from shared records".into());
            }
        }
    }
    let decisions = docs["widths"]["current_decisions"]
        .as_array()
        .ok_or("Missing seasonal current index")?;
    let actual: BTreeSet<_> = bundle.collections["objects"]
        .iter()
        .filter(|r| r["type"] == "named_current")
        .filter_map(|r| r["id"].as_str())
        .collect();
    let mut ids = BTreeSet::new();
    for row in decisions {
        if !row["name"].is_string() {
            return Err("Missing seasonal current name".into());
        }
        let id = format!(
            "current:{}",
            row["current_id"]
                .as_str()
                .ok_or("Missing seasonal current identity")?
        );
        if !ids.insert(id.clone()) || !actual.contains(id.as_str()) {
            return Err("Invalid seasonal current index".into());
        }
    }
    if ids.len() != actual.len() {
        return Err("Incomplete seasonal current index".into());
    }
    let direction = &docs["directions"];
    let phases = direction["phases"]
        .as_array()
        .ok_or("Missing local direction phases")?;
    if direction["current_id"] != "new-guinea-coastal-current" || phases.len() != 3 {
        return Err("Invalid local direction inventory".into());
    }
    for (i, p) in phases.iter().enumerate() {
        let months = [
            json!([11, 12, 1, 2, 3, 4]),
            json!([5, 6, 7, 8, 9, 10]),
            Value::Null,
        ];
        if p["current_id"] != direction["current_id"]
            || p["flow_direction"]
                != [
                    "southeastward",
                    "northwestward",
                    "southeastward NGCC absent; northwestward undercurrent shoals",
                ][i]
            || p["geometry_role"] != "local_direction_symbol_not_current_axis"
            || p["site_lon_lat"] != json!([141.4, -1.7])
            || p["calendar_months"] != months[i]
            || p["playback_eligible"] != json!(i < 2)
            || p["phase_kind"]
                != if i < 2 {
                    "seasonal_direction_composite"
                } else {
                    "event_exception"
                }
            || [
                "length_km",
                "width_km",
                "route_coordinates",
                "annual_length_range_km",
                "annual_width_range_km",
            ]
            .iter()
            .any(|k| p.get(k) != Some(&Value::Null))
        {
            return Err("Invalid local direction scope".into());
        }
    }
    Ok(())
}
fn plans(docs: &Value) -> Result<Value, String> {
    let widths = docs["widths"]["measurements"]
        .as_array()
        .ok_or("Missing widths")?;
    let frames = docs["frames"]["frames"]
        .as_array()
        .ok_or("Missing frames")?;
    let directions = &docs["directions"];
    let mut plans = json!({});
    for current in docs["widths"]["current_decisions"]
        .as_array()
        .ok_or("Missing current index")?
    {
        let id = current["current_id"].as_str().ok_or("Missing current ID")?;
        let owned: Vec<_> = frames.iter().filter(|r| r["current_id"] == id).collect();
        let linked: BTreeSet<_> = owned
            .iter()
            .flat_map(|r| r["width_measurement_ids"].as_array().into_iter().flatten())
            .filter_map(Value::as_str)
            .collect();
        let mut phases = Vec::new();
        for row in widths.iter().filter(|r| {
            r["current_id"] == id && !r["id"].as_str().is_some_and(|w| linked.contains(w))
        }) {
            let label = row["phase_label"]
                .as_str()
                .filter(|v| !v.is_empty())
                .unwrap_or_else(|| {
                    row["time_convention"]
                        .as_str()
                        .unwrap_or("Recorded evidence")
                        .split(' ')
                        .next()
                        .unwrap()
                });
            phases.push(json!({"id":row["id"],"width_id":row["id"],"frame_id":null,"direction_id":null,"label":label,"playback_step_eligible":true}));
        }
        for row in owned {
            let linked = row["width_measurement_ids"]
                .as_array()
                .ok_or("Missing linked phase widths")?;
            let width = widths.iter().find(|w| linked.contains(&w["id"]));
            phases.push(json!({"id":row["id"],"width_id":width.map(|w|&w["id"]),"frame_id":row["id"],"direction_id":null,"label":row["phase_label"],"playback_step_eligible":true}));
        }
        if directions["current_id"] == id {
            for row in directions["phases"]
                .as_array()
                .ok_or("Missing direction phases")?
            {
                phases.push(json!({"id":row["id"],"width_id":null,"frame_id":null,"direction_id":row["id"],"label":row["phase_label"],"playback_step_eligible":row["playback_eligible"]}));
            }
        }
        let summary = docs["widths"]["seasonal_summaries"]
            .as_array()
            .and_then(|rows| rows.iter().find(|r| r["current_id"] == id));
        let restriction = docs["widths"]["comparability_notes"]
            .as_array()
            .and_then(|rows| rows.iter().find(|r| r["current_id"] == id));
        let comparable = summary.is_some_and(|r| {
            r["measurement_ids"].as_array().is_some_and(|ids| {
                phases
                    .iter()
                    .all(|p| !p["width_id"].is_null() && ids.contains(&p["width_id"]))
            })
        });
        let route_only = phases.len() > 1 && phases.iter().all(|p| !p["frame_id"].is_null());
        let direction_count = phases
            .iter()
            .filter(|p| !p["direction_id"].is_null() && p["playback_step_eligible"] == true)
            .count();
        let can_play = phases.len() >= 2
            && restriction.is_none()
            && (comparable || route_only || direction_count > 1);
        let eligible: Vec<_> = if can_play {
            phases
                .iter()
                .enumerate()
                .filter(|(_, p)| p["playback_step_eligible"] == true)
                .map(|(i, _)| i)
                .collect()
        } else {
            Vec::new()
        };
        let mut note="Annual width range and measurement uncertainty: not available. A single dated section does not establish a seasonal cycle.".to_owned();
        if let Some(r) = summary {
            let span = r["reported_seasonal_value_span_km"]
                .as_array()
                .ok_or("Missing reported seasonal span")?
                .iter()
                .map(|v| {
                    v.as_f64()
                        .map(|f| f.to_string())
                        .ok_or("Invalid reported seasonal value")
                })
                .collect::<Result<Vec<_>, _>>()?
                .join("–");
            note = format!(
                "{span} km: {}",
                r["interpretation"]
                    .as_str()
                    .ok_or("Missing seasonal interpretation")?
            );
        }
        if let Some(r) = docs["frames"]["comparability"]
            .as_array()
            .and_then(|rows| rows.iter().find(|r| r["current_id"] == id))
        {
            note = r["reason"]
                .as_str()
                .ok_or("Missing route comparison scope")?
                .to_owned();
        }
        if let Some(r) = restriction {
            note = r["reason"]
                .as_str()
                .ok_or("Missing width comparison restriction")?
                .to_owned();
        }
        if directions["current_id"] == id {
            note = directions["interpretation"]
                .as_str()
                .ok_or("Missing direction interpretation")?
                .to_owned();
        }
        plans[id] = json!({"current_id":id,"phases":phases,"can_play":can_play,"eligible_indices":eligible,"range_note":note,
            "playback_scope":"Recorded comparable states only; no annual extrema or interpolated boundaries inferred."});
    }
    Ok(plans)
}

impl Store {
    pub fn seasons_snapshot(&self) -> Result<Value, String> {
        let plans = plans(&documents(&self.bundle)?)?;
        let mut sources = json!({});
        for (key, _, _) in SOURCES {
            sources[key] = self.bundle.manifest["seasons_receipts"][key]["source_json"].clone();
            if !sources[key].is_string() {
                return Err("Missing seasonal source bytes".into());
            }
        }
        Ok(
            json!({"ok":true,"engine":"rust-osw-query-v1","bundle_sha256":self.metadata()["bundle_sha256"],"sources_json":sources,"phase_plans":plans}),
        )
    }
}
