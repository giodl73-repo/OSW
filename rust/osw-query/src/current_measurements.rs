//! Qualified prose reports are distinct from current envelopes and annual ranges.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
pub const PATH: &str = "research/southern-east-madagascar-prose-dimension-admissions.json";
pub const EXPORT: &str = "research/ocean-current-working-measurements.json";
pub const RAW: &str =
    include_str!("../../../research/southern-east-madagascar-prose-dimension-admissions.json");
const EXPORT_RAW: &str = include_str!("../../../research/ocean-current-working-measurements.json");
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
pub fn document() -> Value {
    serde_json::from_str(RAW).unwrap()
}
pub fn active_manifest(manifest: &Value) -> bool {
    manifest["input_sha256"][PATH].is_string()
        || manifest["current_measurement_admission_version"] == "0.2.0-draft-prose-1"
}
pub fn active(bundle: &Bundle) -> bool {
    active_manifest(&bundle.manifest)
        || bundle
            .collections
            .contains_key("current_measurement_admissions")
}
pub fn widths(bundle: &Bundle) -> Vec<Value> {
    if active(bundle) {
        vec![document()["width_record"].clone()]
    } else {
        vec![]
    }
}
fn records() -> Vec<(&'static str, Value)> {
    let doc = document();
    let mut admission = doc.clone();
    admission["id"] = json!("current_measurement_admission:southern-east-madagascar");
    vec![
        ("measurements", doc["measurement"].clone()),
        ("claims", doc["claim"].clone()),
        ("sources", doc["source_record"].clone()),
        ("widths", doc["width_record"].clone()),
        ("length_assessments", doc["length_assessment"].clone()),
        ("current_measurement_admissions", admission),
    ]
}
pub fn validate(bundle: &Bundle) -> Result<(), String> {
    if !active(bundle) {
        return Ok(());
    }
    let doc = document();
    let export: Value = serde_json::from_str(EXPORT_RAW).unwrap();
    if bundle.manifest["current_measurement_admission_version"] != doc["version"]
        || bundle.manifest["input_sha256"][PATH] != pin(RAW)
        || bundle.manifest["input_sha256"][EXPORT] != pin(EXPORT_RAW)
    {
        return Err("Changed prose dimension admission receipt or edition".into());
    }
    for inputs in [&doc["input_sha256"], &export["input_sha256"]] {
        for (path, digest) in inputs.as_object().unwrap() {
            if bundle.manifest["input_sha256"][path] != *digest {
                return Err("Changed prose dimension dependency".into());
            }
        }
    }
    for (collection, mut expected) in records() {
        if collection == "sources" && crate::madagascar_coastal_curve::active(bundle) {
            expected =
                crate::madagascar_coastal_curve::catalogue()["primary_source_record"].clone();
        }
        if collection == "length_assessments" {
            expected = crate::nwasc_admission::rank_override(expected, bundle);
        }
        let rows: Vec<_> = bundle
            .collections
            .get(collection)
            .into_iter()
            .flatten()
            .filter(|r| r["id"] == expected["id"])
            .collect();
        if rows != vec![&expected] {
            return Err(format!("Changed source-reported dimension in {collection}"));
        }
    }
    Ok(())
}
#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> Bundle {
        let doc = document();
        let export: Value = serde_json::from_str(EXPORT_RAW).unwrap();
        let mut inputs = doc["input_sha256"].clone();
        for (k, v) in export["input_sha256"].as_object().unwrap() {
            inputs[k] = v.clone();
        }
        inputs[PATH] = json!(pin(RAW));
        inputs[EXPORT] = json!(pin(EXPORT_RAW));
        let mut collections = std::collections::BTreeMap::new();
        for (name, row) in records() {
            collections
                .entry(name.into())
                .or_insert_with(Vec::new)
                .push(row);
        }
        Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest: json!({"input_sha256":inputs,"current_measurement_admission_version":doc["version"]}),
            collections,
        }
    }
    #[test]
    fn source_reports_reject_changed_values_and_physical_promotions() {
        assert!(validate(&fixture()).is_ok());
        for (key, value) in [
            ("approximate_width_km", json!(140)),
            ("annual_width_range_km", json!([100, 140])),
            ("whole_current_representative", json!(true)),
            ("seasonal_playback_eligible", json!(true)),
            ("fixed_layer_bounds_m", json!([0, 100])),
        ] {
            let mut b = fixture();
            b.collections.get_mut("widths").unwrap()[0][key] = value;
            assert!(validate(&b).is_err(), "{key}");
        }
        let mut b = fixture();
        b.collections.get_mut("measurements").unwrap()[0]["value"] = json!(120);
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections.get_mut("length_assessments").unwrap()[0]["published_rank"] = json!(11);
        assert!(validate(&b).is_err());
    }
    #[test]
    fn duplicates_and_coherent_erasure_reject() {
        let mut b = fixture();
        let row = b.collections["widths"][0].clone();
        b.collections.get_mut("widths").unwrap().push(row);
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections.get_mut("widths").unwrap().clear();
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections.clear();
        b.manifest["input_sha256"]
            .as_object_mut()
            .unwrap()
            .remove(PATH);
        assert!(validate(&b).is_err());
    }
}
