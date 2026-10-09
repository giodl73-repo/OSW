//! Source-bound, signed geographic velocity observations at one fixed station.
use crate::Bundle;
use serde_json::{Value, json};

const SOURCE: &str = "research/antarctic-slope-m6-velocity-series.json";
const APPROVED: &str = include_str!("../../../research/antarctic-slope-m6-velocity-series.json");

pub(crate) fn validate(bundle: &Bundle) -> Result<(), String> {
    if !bundle.collections.contains_key("current_velocity_samples")
        && bundle.manifest["input_sha256"][SOURCE].is_null()
        && !bundle.manifest["editorial_collections"]
            .as_array()
            .is_some_and(|a| a.iter().any(|v| v == "current_velocity_samples"))
        && !bundle
            .collections
            .get("objects")
            .is_some_and(|a| a.iter().any(|v| v.get("velocity_sample_ids").is_some()))
    {
        return Ok(()); // Earlier snapshots and isolated test fixtures have no velocity projection.
    }
    let approved: Value = serde_json::from_str(APPROVED).map_err(|e| e.to_string())?;
    if bundle.collections.get("current_velocity_samples") != approved["samples"].as_array() {
        return Err("M6 velocity records differ from approved source reconstruction".into());
    }
    use sha2::{Digest, Sha256};
    let digest = format!("{:x}", Sha256::digest(APPROVED.as_bytes()));
    if bundle.manifest["input_sha256"][SOURCE] != digest {
        return Err("M6 velocity source pin changed".into());
    }
    for object in &bundle.collections["objects"] {
        let expected: Vec<Value> = approved["samples"]
            .as_array()
            .unwrap()
            .iter()
            .filter(|r| r["entity_id"] == object["id"])
            .map(|r| r["id"].clone())
            .collect();
        if object["velocity_sample_ids"] != json!(expected) {
            return Err("M6 velocity owner join changed".into());
        }
    }
    Ok(())
}

pub(crate) fn scene(matches: &[&Value], all: &[Value]) -> Value {
    let mut panels = Vec::new();
    for kind in ["monthly", "seasonal_composite"] {
        for component in ["eastward", "northward"] {
            let field = format!("{component}_mean_cm_s");
            let span = format!("{component}_interannual_span_cm_s");
            let source: Vec<_> = all.iter().filter(|r| r["series_kind"] == kind).collect();
            let mut lo = 0.0_f64;
            let mut hi = 0.0_f64;
            for row in &source {
                let v = row[&field].as_f64().unwrap();
                lo = lo.min(v);
                hi = hi.max(v);
                if let Some(bounds) = row[&span].as_array() {
                    lo = lo.min(bounds[0].as_f64().unwrap());
                    hi = hi.max(bounds[1].as_f64().unwrap());
                }
            }
            let pad = (hi - lo).max(1.0) * 0.1;
            let points: Vec<_> = matches.iter().filter(|r| r["series_kind"]==kind).map(|r| {
                let x = source.iter().position(|s| s["id"]==r["id"]).unwrap();
                json!({"sample_id":r["id"],"label":r["label"],"x_index":x,"value_cm_s":r[&field],
                    "interannual_span_cm_s":r[&span],"available_pairs":r["available_pairs"],
                    "coverage_fraction":r["hourly_coverage_fraction"],"years":r["contributing_years"],"partial_month":r["partial_month"]})
            }).collect();
            if !points.is_empty() {
                panels.push(json!({"id":format!("{kind}-{component}"),"title":format!("M6 · nominal 228 m · {component} velocity · {}",if kind=="monthly"{"monthly means"}else{"seasonal composite"}),
                    "component":component,"series_kind":kind,"y_domain_cm_s":[lo-pad,hi+pad],"source_count":source.len(),"points":points}));
            }
        }
    }
    json!({"kind":"mooring_velocity","scope":"Observed geographic components in cm/s at M6, 2017–2021. Available hourly pairs only. Seasonal composites equally weight complete year-month means; February has three years. Spans show interannual monthly-mean variation, not confidence intervals. Nominal depth differs from article bin table. Timestamp timezone unspecified. No whole-current dimensions or moving footprint.","source_url":"https://doi.pangaea.de/10.1594/PANGAEA.964717","panels":panels})
}

pub(crate) fn map_scene(matches: &[&Value]) -> Value {
    let records: Vec<Value> = matches.first().map(|r| vec![json!({"id":r["id"],"label":"M6 fixed observation station · nominal 228 m", "type":"mooring_station",
        "map_features":[{"geometry":{"type":"Point","coordinates":[-29.9162,-74.5949]},"role":"fixed_observation_station","note":"Local velocity measurement site, not a current boundary or occupied footprint."}]})]).unwrap_or_default();
    let refs: Vec<&Value> = records.iter().collect();
    let mut scene = crate::map::scene(&refs);
    scene["inspection_collection"] = json!("current_velocity_samples");
    scene["scope"] = json!(
        "One fixed M6 observation station; matching monthly records share this site. No current geometry or physical state containment inferred."
    );
    scene
}
