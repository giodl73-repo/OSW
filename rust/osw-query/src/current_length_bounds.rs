//! Nominal geographic gates never become whole-current lengths or annual ranges.
use crate::Bundle;
use serde_json::Value;
use sha2::{Digest, Sha256};

const FILE: &str = "research/north-atlantic-nominal-gate-bound.json";
const RAW: &str = include_str!("../../../research/north-atlantic-nominal-gate-bound.json");
fn document() -> Value {
    serde_json::from_str(RAW).unwrap()
}
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
fn records() -> Vec<(&'static str, Value)> {
    let doc = document();
    vec![
        ("current_length_bound_admissions", doc.clone()),
        ("length_assessments", doc["length_assessment"].clone()),
        ("measurements", doc["measurement"].clone()),
        ("claims", doc["claim"].clone()),
        ("sources", doc["method_source"].clone()),
    ]
}
pub fn validate(bundle: &Bundle) -> Result<(), String> {
    let present = bundle.manifest["north_atlantic_gate_bound_version"].is_string()
        || bundle.manifest["input_sha256"][FILE].is_string()
        || bundle
            .collections
            .contains_key("current_length_bound_admissions")
        || bundle.collections.values().flatten().any(|r| {
            r["measurement_admission_file"] == FILE
                || r["method_source_id"] == "source:north-atlantic-nominal-gate-bound-v1"
                || r["id"] == "measurement:north-atlantic:nominal-section-floor"
                || r["id"] == "source:north-atlantic-nominal-gate-bound-v1"
        });
    if !present {
        return Ok(());
    }
    let doc = document();
    if bundle.manifest["north_atlantic_gate_bound_version"] != "1"
        || bundle.manifest["input_sha256"][FILE] != pin(RAW)
    {
        return Err("Changed North Atlantic gate-bound admission/edition".into());
    }
    for (path, hash) in doc["input_sha256"].as_object().unwrap() {
        if bundle.manifest["input_sha256"][path] != *hash {
            return Err(format!(
                "Changed North Atlantic gate-bound dependency: {path}"
            ));
        }
    }
    for (name, expected) in records() {
        let rows: Vec<_> = bundle
            .collections
            .get(name)
            .into_iter()
            .flatten()
            .filter(|r| r["id"] == expected["id"])
            .collect();
        if rows != vec![&expected] {
            return Err(format!("Changed North Atlantic gate-bound {name}"));
        }
        if name == "length_assessments"
            && bundle.collections[name]
                .iter()
                .filter(|r| r["entity_id"] == "current:north-atlantic")
                .count()
                != 1
        {
            return Err("Duplicate North Atlantic length assessment".into());
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    fn fixture() -> Bundle {
        let mut inputs = document()["input_sha256"].clone();
        inputs[FILE] = json!(pin(RAW));
        let mut collections = std::collections::BTreeMap::new();
        for (name, row) in records() {
            collections
                .entry(name.into())
                .or_insert_with(Vec::new)
                .push(row);
        }
        Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest: json!({"input_sha256":inputs,"north_atlantic_gate_bound_version":"1"}),
            collections,
        }
    }
    #[test]
    fn accepts_conditional_floor() {
        validate(&fixture()).unwrap();
    }
    #[test]
    fn rejects_rank_owner_source_or_value_transfer() {
        for (collection, key, value) in [
            ("length_assessments", "rank_eligible", json!(true)),
            ("length_assessments", "lower_bound_km", json!(1300)),
            ("length_assessments", "published_length_km", json!(1200)),
            ("measurements", "entity_id", json!("current:gulf-stream")),
            ("measurements", "source_id", json!("source:other")),
            ("measurements", "guaranteed_physical_minimum", json!(true)),
            (
                "measurements",
                "annual_length_range_km",
                json!([1112, 1335]),
            ),
            ("claims", "value", json!(1300)),
        ] {
            let mut b = fixture();
            b.collections.get_mut(collection).unwrap()[0][key] = value;
            assert!(validate(&b).is_err(), "{collection}/{key}");
        }
    }
    #[test]
    fn rejects_receipt_stripping_missing_rows_and_duplicates() {
        let mut b = fixture();
        b.manifest = json!({});
        assert!(validate(&b).is_err());
        for name in [
            "length_assessments",
            "measurements",
            "claims",
            "sources",
            "current_length_bound_admissions",
        ] {
            let mut missing = fixture();
            missing.collections.remove(name);
            assert!(validate(&missing).is_err(), "missing {name}");
            let mut duplicate = fixture();
            let r = duplicate.collections[name][0].clone();
            duplicate.collections.get_mut(name).unwrap().push(r);
            assert!(validate(&duplicate).is_err(), "duplicate {name}");
        }
    }
}
