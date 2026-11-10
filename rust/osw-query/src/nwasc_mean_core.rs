//! Reported static mean-core extents remain on the proposed slope branch.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
pub const FILE: &str = "research/norwegian-baumann-2026-mean-core-widths.json";
pub static RAW: &str =
    include_str!("../../../research/norwegian-baumann-2026-mean-core-widths.json");
static SVG: &str = include_str!("../../../figures/norwegian-baumann-2026-mean-core-widths.svg");
fn document() -> Value {
    serde_json::from_str(RAW).unwrap()
}
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
pub fn owns(r: &Value) -> bool {
    r["id"]
        .as_str()
        .is_some_and(|s| s.starts_with("norwegian-atlantic-slope-baumann-2026-"))
}
fn rows() -> Vec<Value> {
    document()["measurements"]
        .as_array()
        .unwrap()
        .iter()
        .enumerate()
        .map(|(i, r)| {
            let mut r = r.clone();
            r["source_file"] = json!(FILE);
            r["source_pointer"] = json!(format!("/measurements/{i}"));
            r
        })
        .collect()
}
pub fn active(b: &Bundle) -> bool {
    !b.manifest["nwasc_mean_core_widths_version"].is_null()
        || !b.manifest["input_sha256"][FILE].is_null()
        || b.collections
            .get("proposed_widths")
            .into_iter()
            .flatten()
            .any(owns)
}
pub fn validate(b: &Bundle) -> Result<(), String> {
    if b.collections
        .get("widths")
        .into_iter()
        .flatten()
        .any(|r| owns(r) || r["source_file"] == FILE)
    {
        return Err("Proposed mean-core width transferred to canonical owner".into());
    }
    if !active(b) {
        return Ok(());
    }
    if b.manifest["nwasc_mean_core_widths_version"] != "1"
        || b.manifest["input_sha256"][FILE] != pin(RAW)
    {
        return Err("Changed mean-core width edition/source".into());
    }
    for (p, sha) in document()["input_sha256"].as_object().unwrap() {
        if b.manifest["input_sha256"][p] != *sha {
            return Err(format!("Changed mean-core width dependency:{p}"));
        }
    }
    let actual: Vec<_> = b
        .collections
        .get("proposed_widths")
        .into_iter()
        .flatten()
        .filter(|r| owns(r) || r["source_file"] == FILE)
        .cloned()
        .collect();
    if actual != rows() {
        return Err("Changed or missing mean-core width records".into());
    }
    let receipt =
        &b.manifest["atlas_receipts"]["research/ocean-current-inventory-expansion-candidates.json"];
    let proposals: Value = serde_json::from_str(
        receipt["source_json"]
            .as_str()
            .ok_or("Missing proposed branch receipt")?,
    )
    .map_err(|e| e.to_string())?;
    if !proposals["entries"].as_array().is_some_and(|a| {
        a.iter().any(|r| {
            r["proposed_id"] == "norwegian-atlantic-slope"
                && r["parent_proposed_id"] == "norwegian-atlantic"
        })
    }) {
        return Err("Missing mean-core proposed branch identity".into());
    }
    Ok(())
}
pub fn panels(matches: &[&Value], corpus: &[Value]) -> Vec<Value> {
    if !matches.iter().any(|r| owns(r)) {
        return vec![];
    }
    let source = rows();
    let present: Vec<_> = source
        .iter()
        .filter(|r| corpus.iter().any(|c| c["id"] == r["id"]))
        .enumerate()
        .map(|(i, r)| {
            json!({
        "id":r["id"],"label":r["phase_label"],"source_pointer":format!("/measurements/{i}"),
        "matching":matches.iter().any(|m|m["id"]==r["id"])})
        })
        .collect();
    vec![
        json!({"id":"nwasc-mean-core","title":"Proposed slope branch · 1993–2022 static mean-core extents",
        "svg":SVG,"source_file":FILE,"source_url":document()["source_url"],"collection":"proposed_widths","rows":present,
        "support_note":"Proposed identity only. Vertical support: Svinøy span at50m; Gimsøy horizontal projection of a variable-depth core. Isobaths constrain section scope, not measurement depth. Static mean fields, not mean widths, seasonal samples or an annual range.",
        "original_pdf":document()["original_pdf"]}),
    ]
}
#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> Bundle {
        let d = document();
        let mut pins = d["input_sha256"].clone();
        pins[FILE] = json!(pin(RAW));
        serde_json::from_value(json!({"schema":"osw.query-bundle.v1","manifest":{"nwasc_mean_core_widths_version":"1","input_sha256":pins,
            "atlas_receipts":{"research/ocean-current-inventory-expansion-candidates.json":{"source_json":"{\"entries\":[{\"proposed_id\":\"norwegian-atlantic-slope\",\"parent_proposed_id\":\"norwegian-atlantic\"}]}"}}},
            "collections":{"proposed_widths":rows(),"widths":[]}})).unwrap()
    }
    #[test]
    fn mean_core_rows_and_scope_are_exact() {
        validate(&fixture()).unwrap();
        for (k, v) in [
            ("approximate_width_km", json!(40)),
            ("width_plane_depth_m", json!(530)),
            ("observed_period", json!("2026-01")),
            ("fixed_layer_bounds_m", json!([50, 530])),
            ("proposed_current_id", json!("norwegian")),
            ("mean_transport_fraction", json!(0.7)),
            ("seasonal_playback_eligible", json!(true)),
            ("uncertainty_km", json!(5)),
            ("source_file", json!("other.json")),
        ] {
            let mut b = fixture();
            b.collections.get_mut("proposed_widths").unwrap()[1][k] = v;
            assert!(validate(&b).is_err(), "{k}");
        }
    }
    #[test]
    fn erasure_transfer_source_rebinding_and_partial_edition_fail() {
        let mut b = fixture();
        b.collections.get_mut("proposed_widths").unwrap().clear();
        assert!(validate(&b).is_err());
        let mut b = fixture();
        let mut r = rows()[0].clone();
        r["current_id"] = json!("norwegian");
        b.collections.get_mut("widths").unwrap().push(r);
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.manifest["input_sha256"][FILE] = json!("bad");
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.manifest
            .as_object_mut()
            .unwrap()
            .remove("nwasc_mean_core_widths_version");
        assert!(validate(&b).is_err());
        let mut b = fixture();
        let p = document()["input_sha256"]
            .as_object()
            .unwrap()
            .keys()
            .next()
            .unwrap()
            .clone();
        b.manifest["input_sha256"][p] = json!("bad");
        assert!(validate(&b).is_err());
    }
    #[test]
    fn legacy_packet_is_supported_and_filtered_scene_keeps_distinct_supports() {
        let mut b = fixture();
        b.manifest = json!({});
        b.collections.get_mut("proposed_widths").unwrap().clear();
        validate(&b).unwrap();
        let r = rows();
        let p = panels(&[&r[1]], &r);
        assert_eq!(p[0]["rows"].as_array().unwrap().len(), 2);
        assert_eq!(p[0]["rows"][0]["matching"], false);
        assert_eq!(p[0]["rows"][1]["matching"], true);
        assert!(
            p[0]["svg"]
                .as_str()
                .unwrap()
                .to_lowercase()
                .contains("variable-depth")
        );
    }
}
