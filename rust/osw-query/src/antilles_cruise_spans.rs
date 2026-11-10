//! Source-reported cruise spans; incompatible prose geography remains quarantined.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
const PATH: &str = "research/antilles-cainzos-2023-cruise-section-spans.json";
const RAW: &str = include_str!("../../../research/antilles-cainzos-2023-cruise-section-spans.json");
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
fn document() -> Value {
    serde_json::from_str(RAW).unwrap()
}
fn expected() -> Vec<Value> {
    document()["measurements"]
        .as_array()
        .unwrap()
        .iter()
        .map(|r| {
            let mut row = r.clone();
            row["extraction_file"] = json!(PATH);
            row["extraction_sha256"] = json!(pin(RAW));
            row
        })
        .collect()
}
pub(crate) fn validate(bundle: &crate::Bundle) -> Result<(), String> {
    let widths = bundle
        .collections
        .get("widths")
        .map(Vec::as_slice)
        .unwrap_or(&[]);
    let active = bundle.manifest["input_sha256"].get(PATH).is_some()
        || widths.iter().any(|r| r["extraction_file"] == PATH)
        || bundle
            .collections
            .get("objects")
            .into_iter()
            .flatten()
            .any(|r| r["id"] == "current:antilles");
    if !active {
        return Ok(());
    }
    if bundle.manifest["input_sha256"][PATH] != pin(RAW) {
        return Err("Antilles cruise source changed".into());
    }
    let doc = document();
    for (path, sha) in doc["input_sha256"].as_object().unwrap() {
        if bundle.manifest["input_sha256"][path] != *sha {
            return Err(format!("Antilles cruise dependency changed: {path}"));
        }
    }
    if bundle.manifest["input_sha256"][doc["generator_file"].as_str().unwrap()]
        != doc["generator_sha256"]
    {
        return Err("Antilles cruise extraction code changed".into());
    }
    for expected in expected() {
        let rows: Vec<_> = widths
            .iter()
            .filter(|r| r["id"] == expected["id"])
            .collect();
        if rows.len() != 1 || rows[0] != &expected {
            return Err("Antilles cruise identity, span, scope or source binding changed".into());
        }
    }
    if widths
        .iter()
        .any(|r| r["extraction_file"] == PATH && !expected().iter().any(|e| e == r))
    {
        return Err("Unexpected Antilles cruise record or duplicate alias".into());
    }
    Ok(())
}
pub(crate) fn scene(matches: &[&Value]) -> Value {
    let ids: Vec<_> = expected().iter().map(|r| r["id"].clone()).collect();
    let rows: Vec<_> = matches
        .iter()
        .filter(|r| ids.contains(&r["id"]))
        .copied()
        .collect();
    if rows.is_empty() {
        Value::Null
    } else {
        json!({"kind":"antilles_cruise_section_spans","records":rows,
        "scope":"Three transport-selected cruise-section spans. Source prose location conflict is retained. Not whole-current widths, annual extrema or geographic current edges."})
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    fn bundle() -> crate::Bundle {
        let doc = document();
        let mut inputs = doc["input_sha256"].clone();
        inputs[PATH] = json!(pin(RAW));
        inputs[doc["generator_file"].as_str().unwrap()] = doc["generator_sha256"].clone();
        serde_json::from_value(json!({"schema":"osw.query-bundle.v1","manifest":{"input_sha256":inputs},"collections":{"widths":expected()}})).unwrap()
    }
    #[test]
    fn reject_wrong_distance_and_false_physical_scope() {
        validate(&bundle()).unwrap();
        for (key, value) in [
            ("approximate_width_km", json!(38)),
            ("width_range_km", json!([38, 125])),
            ("current_id", json!("gulf-stream")),
            ("seasonal_playback_eligible", json!(true)),
            ("full_width_inference_eligible", json!(true)),
        ] {
            let mut bad = bundle();
            bad.collections.get_mut("widths").unwrap()[2][key] = value;
            assert!(validate(&bad).is_err());
        }
    }
    #[test]
    fn reject_missing_duplicate_and_rebound_source() {
        let mut bad = bundle();
        bad.collections.get_mut("widths").unwrap().pop();
        assert!(validate(&bad).is_err());
        let mut bad = bundle();
        let row = bad.collections["widths"][0].clone();
        bad.collections.get_mut("widths").unwrap().push(row);
        assert!(validate(&bad).is_err());
        let mut bad = bundle();
        bad.manifest["input_sha256"][PATH] = json!("changed");
        assert!(validate(&bad).is_err());
    }
    #[test]
    fn scene_keeps_distinct_cruise_values() {
        let rows = expected();
        let scene = scene(&rows.iter().collect::<Vec<_>>());
        assert_eq!(scene["records"][2]["approximate_width_km"], 39);
        assert!(scene["records"][0]["width_range_km"].is_null());
        assert!(super::scene(&[]).is_null());
    }
}
