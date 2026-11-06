//! Frozen model-normal geometry, separately typed from physical width evidence.
use crate::Bundle;
use geo::{GeodesicIntermediate, Point};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::sync::OnceLock;
pub const FILE: &str = "research/kuroshio-wang-2024-axis-normal-spans.json";
pub const CONTRACT: &str = "research/kuroshio-wang-2024-axis-normal-query-contract.json";
pub const COLLECTION: &str = "current_axis_normal_samples";
pub const ID: &str = "diagnostic:kuroshio-wang-2024-axis-normal-spans";
pub static RAW: &str = include_str!("../../../research/kuroshio-wang-2024-axis-normal-spans.json");
const CONTRACT_RAW: &str =
    include_str!("../../../research/kuroshio-wang-2024-axis-normal-query-contract.json");
const SOURCE: &str = "source:kuroshio-wang-2026-v1";
fn document() -> &'static Value {
    static DOC: OnceLock<Value> = OnceLock::new();
    DOC.get_or_init(|| serde_json::from_str(RAW).unwrap())
}
fn contract() -> Value {
    serde_json::from_str(CONTRACT_RAW).unwrap()
}
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
pub fn active(b: &Bundle) -> bool {
    b.manifest["kuroshio_axis_normal_version"].is_string()
        || b.manifest["input_sha256"][FILE].is_string()
        || b.manifest["input_sha256"][CONTRACT].is_string()
        || b.collections.contains_key(COLLECTION)
        || b.collections
            .get("diagnostics")
            .into_iter()
            .flatten()
            .any(|r| r["id"] == ID)
}
fn samples() -> Vec<Value> {
    document()["cases"].as_array().unwrap().iter().enumerate().map(|(i,r)|json!({
        "id":r["id"],"entity_id":"current:kuroshio","current_id":"kuroshio",
        "sample_date":r["sample_date"],"source_level":r["source_level"],"nominal_depth_m":r["nominal_depth_m"],
        "section_latitude":r["latitude"],"tangent_half_window_km":r["tangent_half_window_km"],
        "is_primary_convention":r["tangent_half_window_km"]==14,"quantity":"axis_normal_model_boundary_span",
        "status":r["status"],"value_km":r["span_km"],"report_case_index":i,
        "source_id":SOURCE,"diagnostic_id":ID,"evidence_class":"model_derived",
        "rank_eligible":false,"physical_width_inventory_admitted":false,"velocity_normal_verified":false,
        "ocean_connectivity_verified":false,"uncertainty_km":null,"boundary_fallback_occurred":null,
        "threshold_attained":null,"exceeds_source_nominal_140km_transect":r["exceeds_source_nominal_140km_transect"]})).collect()
}
fn diagnostic() -> Value {
    let doc = document();
    let mut summary = json!({});
    for key in [
        "counts",
        "status_counts",
        "primary_status_counts",
        "metric",
        "numerical_readback",
    ] {
        summary[key] = doc[key].clone();
    }
    json!({"id":ID,"label":"Kuroshio2024 axis-normal model spans and sample ranges",
        "entity_id":"current:kuroshio","current_id":"kuroshio","rank_eligible":false,
        "source_file":FILE,"source_file_sha256":pin(RAW),"source_json":RAW,"summary":summary})
}
pub fn validate(b: &Bundle) -> Result<(), String> {
    if !active(b) {
        return Ok(());
    }
    if b.manifest["kuroshio_axis_normal_version"] != "1"
        || b.manifest["kuroshio_daily_dimensions_version"] != "1"
    {
        return Err("Missing Kuroshio normal/base edition".into());
    }
    let c = contract();
    for (p, sha) in [(FILE, pin(RAW)), (CONTRACT, pin(CONTRACT_RAW))] {
        if b.manifest["input_sha256"][p] != sha {
            return Err("Changed Kuroshio normal source/contract pin".into());
        }
    }
    for (p, sha) in c["input_sha256"].as_object().unwrap() {
        if b.manifest["input_sha256"][p] != *sha {
            return Err(format!("Changed Kuroshio normal dependency: {p}"));
        }
    }
    if b.collections.get(COLLECTION) != Some(&samples()) {
        return Err("Changed Kuroshio normal projection".into());
    }
    let ds: Vec<_> = b
        .collections
        .get("diagnostics")
        .into_iter()
        .flatten()
        .filter(|r| r["id"] == ID)
        .collect();
    if ds != vec![&diagnostic()] {
        return Err("Changed Kuroshio normal diagnostic".into());
    }
    let sources: Vec<_> = b
        .collections
        .get("sources")
        .into_iter()
        .flatten()
        .filter(|r| r["id"] == SOURCE)
        .collect();
    if sources != vec![&c["source_record"]] {
        return Err("Changed Kuroshio normal source link".into());
    }
    let owners: Vec<_> = b
        .collections
        .get("objects")
        .into_iter()
        .flatten()
        .filter(|r| r["id"] == "current:kuroshio")
        .collect();
    if owners.len() != 1
        || owners[0]["capabilities"]["axis_normal_samples"] != 16470
        || !owners[0]["diagnostic_ids"]
            .as_array()
            .is_some_and(|a| a.contains(&json!(ID)))
        || !owners[0]["source_ids"]
            .as_array()
            .is_some_and(|a| a.contains(&json!(SOURCE)))
    {
        return Err("Changed Kuroshio normal owner".into());
    }
    Ok(())
}
fn normal_path(r: &Value) -> String {
    if r["status"] != "resolved" {
        return String::new();
    }
    let a = &r["edges"]["left"]["point"];
    let b = &r["edges"]["right"]["point"];
    let start = Point::new(a[0].as_f64().unwrap(), a[1].as_f64().unwrap());
    let end = Point::new(b[0].as_f64().unwrap(), b[1].as_f64().unwrap());
    start
        .geodesic_intermediate_fill(&end, 5000., true)
        .iter()
        .enumerate()
        .map(|(i, p)| {
            let (x, y) = crate::map::point(&json!([p.x(), p.y()])).unwrap();
            format!("{} {x:.7} {y:.7} ", if i == 0 { 'M' } else { 'L' })
        })
        .collect()
}
pub fn attach(scene: &mut Value, b: &Bundle) {
    if !active(b) {
        return;
    }
    let doc = document();
    for frame in scene["frames"].as_array_mut().unwrap() {
        let selected: Vec<_> = doc["cases"]
            .as_array()
            .unwrap()
            .iter()
            .filter(|r| {
                r["sample_date"] == frame["date"] && r["source_level"] == frame["source_level"]
            })
            .collect();
        frame["normal_sections"]=json!(selected.iter().map(|r|json!({"sample_id":r["id"],"latitude":r["latitude"],
            "tangent_half_window_km":r["tangent_half_window_km"],"status":r["status"],"span_km":r["span_km"],
            "gate":r["gate"],"edges":r["edges"],"d":normal_path(r),
            "exceeds_source_nominal_140km_transect":r["exceeds_source_nominal_140km_transect"]})).collect::<Vec<_>>());
        frame["normal_sensitivity"]=json!(doc["latitude_gates"].as_array().unwrap().iter().map(|lat|{
            let values:Vec<_>=selected.iter().filter(|r|r["latitude"]==*lat).filter_map(|r|r["span_km"].as_f64()).collect();
            let complete=values.len()==3;
            json!({"latitude":lat,"complete":complete,"resolved_windows":values.len(),"expected_windows":3,
                "minimum_km":if complete{values.iter().copied().reduce(f64::min)}else{None},
                "maximum_km":if complete{values.iter().copied().reduce(f64::max)}else{None}})
        }).collect::<Vec<_>>());
    }
    scene["normal"] = json!({"collection":COLLECTION,"diagnostic_id":ID,"source_file":FILE,
        "scope":contract()["scope"],"counts":doc["counts"],"status_counts":doc["status_counts"],
        "primary_status_counts":doc["primary_status_counts"],"summaries":doc["summaries"],
        "paired_tangent_sensitivity":doc["paired_tangent_sensitivity"],"tangent_half_windows_km":doc["tangent_half_windows_km"],
        "primary_tangent_half_window_km":14,"figure_file":doc["figure"],"numerical_readback":doc["numerical_readback"]});
}
#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> Bundle {
        let c = contract();
        let mut pins = c["input_sha256"].clone();
        pins[FILE] = json!(pin(RAW));
        pins[CONTRACT] = json!(pin(CONTRACT_RAW));
        serde_json::from_value(json!({"schema":"osw.query-bundle.v1", "manifest":{"kuroshio_axis_normal_version":"1","kuroshio_daily_dimensions_version":"1","input_sha256":pins},
            "collections":{COLLECTION:samples(),"diagnostics":[diagnostic()],"sources":[c["source_record"]],
                "objects":[{"id":"current:kuroshio","capabilities":{"axis_normal_samples":16470},"diagnostic_ids":[ID],"source_ids":[SOURCE]}]}})).unwrap()
    }
    #[test]
    fn all_attempts_and_nulls_bound() {
        let mut b = fixture();
        validate(&b).unwrap();
        assert_eq!(b.collections[COLLECTION].len(), 16470);
        b.collections.get_mut(COLLECTION).unwrap()[0]["uncertainty_km"] = json!(0);
        assert!(validate(&b).is_err());
    }
    #[test]
    fn native_normal_paths_respect_source_edges_and_missingness() {
        let doc = document();
        let resolved = doc["cases"]
            .as_array()
            .unwrap()
            .iter()
            .find(|r| r["status"] == "resolved")
            .unwrap();
        let missing = doc["cases"]
            .as_array()
            .unwrap()
            .iter()
            .find(|r| r["status"] != "resolved")
            .unwrap();
        let path = normal_path(resolved);
        assert!(path.starts_with('M'));
        assert!(path.contains('L'));
        assert!(!path.contains("NaN"));
        assert_eq!(normal_path(missing), "");
        let mut scene = json!({"frames":[{"date":resolved["sample_date"],"source_level":resolved["source_level"]}]});
        attach(&mut scene, &fixture());
        assert_eq!(
            scene["frames"][0]["normal_sections"]
                .as_array()
                .unwrap()
                .len(),
            15
        );
        assert_eq!(scene["normal"]["summaries"].as_array().unwrap().len(), 585);
        assert_eq!(
            scene["frames"][0]["normal_sensitivity"]
                .as_array()
                .unwrap()
                .len(),
            5
        );
    }
    #[test]
    fn missing_source_or_owner_and_rebound_diagnostic_reject() {
        let mut b = fixture();
        b.collections.get_mut("objects").unwrap()[0]["diagnostic_ids"] = json!([]);
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections.get_mut(COLLECTION).unwrap().pop();
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections.get_mut("diagnostics").unwrap()[0]["source_json"] = json!("{}");
        assert!(validate(&b).is_err());
    }
    #[test]
    fn old_snapshot_is_optional_but_partial_edition_rejects() {
        let b: Bundle = serde_json::from_value(
            json!({"schema":"osw.query-bundle.v1","manifest":{},"collections":{}}),
        )
        .unwrap();
        validate(&b).unwrap();
        let mut b = fixture();
        b.manifest
            .as_object_mut()
            .unwrap()
            .remove("kuroshio_axis_normal_version");
        assert!(validate(&b).is_err());
    }
}
