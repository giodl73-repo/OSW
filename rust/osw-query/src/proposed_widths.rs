//! Source-specific widths remain on proposed branches, outside canonical owners.
use serde_json::{Value, json};
use std::collections::BTreeSet;

fn rows_scope(rows: &[Value]) -> Result<(), String> {
    let mut ids = BTreeSet::new();
    for r in rows {
        let id = r["id"].as_str().ok_or("Missing proposed width id")?;
        let (owner, value, range) = match id {
            "norwegian-atlantic-slope-orvik-2001-regional-width" => {
                ("norwegian-atlantic-slope", Value::Null, json!([30, 50]))
            }
            "norwegian-atlantic-front-orvik-2001-regional-width" => {
                ("norwegian-atlantic-front", Value::Null, json!([30, 50]))
            }
            "norwegian-atlantic-slope-mork-2010-surface-scale" => {
                ("norwegian-atlantic-slope", json!(50), Value::Null)
            }
            _ => return Err("Unknown Norwegian branch width identity".into()),
        };
        if !ids.insert(id)
            || r["proposed_current_id"] != owner
            || r.get("current_id").is_some()
            || r["approximate_width_km"] != value
            || r["width_range_km"] != range
            || r["status"] != "editorial_width_evidence_for_proposed_identity_not_canonical"
            || [
                "observed_period",
                "calendar_months",
                "fixed_layer_bounds_m",
                "section_geometry",
            ]
            .iter()
            .any(|k| r.get(k) != Some(&Value::Null))
            || [
                "whole_current_representative",
                "full_width_inference_eligible",
                "rank_eligible",
                "annual_extrema_eligible",
                "seasonal_playback_eligible",
                "is_confidence_interval",
            ]
            .iter()
            .any(|k| r.get(k) != Some(&json!(false)))
        {
            return Err("Norwegian proposed branch width scope mismatch".into());
        }
        if r["unit"] != "km"
            || r["source_publication_year"] != if value.is_null() { 2001 } else { 2010 }
        {
            return Err("Norwegian branch units or publication year mismatch".into());
        }
        let context = if value.is_null() {
            json!({"mooring_context_months":{"start":"1995-04","end":"1999-02"},"mooring_context_is_width_sampling_interval":false,"mooring_bathymetry_m":[490,990],"bathymetry_is_width_layer":false,"reported_jet_depth_m":if owner.ends_with("front"){json!(400)}else{Value::Null},"jet_depth_is_width_layer":false})
        } else {
            json!({"ADT_context_months":{"start":"1992-10","end":"2009-07"},"ADT_context_is_exact_width_observation_interval":false,"surface_grid_resolution_km_at_section_approx":17,"figure_2_moving_average_months":3,"width_is_temporal_mean_or_mean_of_widths":false,"core_bathymetry_m_approx":500,"bathymetry_is_width_layer":false,"validation_instrument_depth_m":100,"validation_depth_is_width_layer":false})
        };
        let (method, metric, kind, url) = if value.is_null() {
            (
                "published_regional_branch_width_summary",
                "author_reported_branch_width",
                json!("reported_regional_branch_width_span"),
                "https://www.sciencedirect.com/science/article/pii/S0967063700000388",
            )
        } else {
            (
                "published_ADT_surface_branch_scale",
                "author_reported_surface_branch_scale",
                Value::Null,
                "https://os.copernicus.org/articles/6/901/2010/",
            )
        };
        if r["sampling_context"] != context
            || r["measurement_type"] != method
            || r["width_metric"] != metric
            || r["range_kind"] != kind
            || r["source_url"] != url
        {
            return Err("Norwegian proposed branch averaging or source mismatch".into());
        }
    }
    if ids.len() != 3 {
        return Err("Incomplete Norwegian proposed branch widths".into());
    }
    Ok(())
}

pub(crate) fn validate_proposals(doc: &Value) -> Result<(), String> {
    let Some(entries) = doc["entries"].as_array() else {
        return Ok(());
    };
    let owners = [
        "norwegian-atlantic",
        "norwegian-atlantic-slope",
        "norwegian-atlantic-front",
    ];
    if !entries
        .iter()
        .any(|r| owners.iter().any(|id| r["proposed_id"] == *id))
    {
        return Ok(());
    }
    let mut rows = Vec::new();
    for owner in owners {
        let matches: Vec<_> = entries
            .iter()
            .filter(|r| r["proposed_id"] == owner)
            .collect();
        if matches.len() != 1 {
            return Err("Missing or duplicated Norwegian branch proposal".into());
        }
        let p = matches[0];
        let widths = p["width_evidence"]
            .as_array()
            .ok_or("Missing proposed width records")?;
        let count = match owner {
            "norwegian-atlantic" => 0,
            "norwegian-atlantic-slope" => 2,
            _ => 1,
        };
        if widths.len() != count
            || widths.iter().any(|r| r["proposed_current_id"] != owner)
            || p.get("whole_current_width_km") != Some(&Value::Null)
            || p.get("annual_width_range_km") != Some(&Value::Null)
            || p["rank_eligible"] != false
            || (owner == "norwegian-atlantic"
                && p["component_proposed_ids"]
                    != json!(["norwegian-atlantic-slope", "norwegian-atlantic-front"]))
            || (owner != "norwegian-atlantic" && p["parent_proposed_id"] != "norwegian-atlantic")
        {
            return Err("Norwegian proposed branch or system scope mismatch".into());
        }
        rows.extend(widths.iter().cloned());
    }
    rows_scope(&rows)
}
pub(crate) fn validate_audit(doc: &Value) -> Result<(), String> {
    if doc["source_document_sha256"]
        != "cc0c4a94ba785c8bcd0e7b6bbc8e46f86583615909a265e3e5a3d4566e9f2fc3"
        || doc["source_document_file"]
            != "research/source-data/mork-norwegian-2010/journal-article.pdf"
        || doc["source_document_bytes"] != 2577439
        || doc.get("mean_front_width_km") != Some(&Value::Null)
        || doc.get("mean_front_width_range_km") != Some(&Value::Null)
    {
        return Err("Norwegian original receipt or unquantified front mean mismatch".into());
    }
    rows_scope(
        doc["measurements"]
            .as_array()
            .ok_or("Missing proposed audit widths")?,
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn proposed_branches_reject_alias_transfer_and_temporal_promotion() {
        let doc: Value = serde_json::from_str(include_str!(
            "../../../research/ocean-current-inventory-expansion-candidates.json"
        ))
        .unwrap();
        validate_proposals(&doc).unwrap();
        for (key, value) in [
            ("current_id", json!("norwegian")),
            ("approximate_width_km", json!(40)),
            ("width_range_km", json!([30, 70])),
            ("seasonal_playback_eligible", json!(true)),
            ("fixed_layer_bounds_m", json!([0, 400])),
        ] {
            let mut bad = doc.clone();
            let p = bad["entries"]
                .as_array_mut()
                .unwrap()
                .iter_mut()
                .find(|p| p["proposed_id"] == "norwegian-atlantic-slope")
                .unwrap();
            p["width_evidence"][0][key] = value;
            assert!(validate_proposals(&bad).is_err(), "{key}");
        }
        let audit: Value = serde_json::from_str(include_str!(
            "../../../research/norwegian-atlantic-branch-width-scope-audit.json"
        ))
        .unwrap();
        validate_audit(&audit).unwrap();
        let mut bad = audit;
        bad["mean_front_width_km"] = json!(60);
        assert!(validate_audit(&bad).is_err());
    }
}
