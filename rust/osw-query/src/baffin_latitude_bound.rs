//! Frozen source-stage results require a complete, unranked working admission.
use crate::Bundle;
use serde_json::Value;
use sha2::{Digest, Sha256};

const FILE: &str = "research/baffin-latitude-bound-admission-v1.json";
const RAW: &str = include_str!("../../../research/baffin-latitude-bound-admission-v1.json");
const VERSION: &str = "baffin_latitude_gate_bound_version";
const OWNER_FILE: &str = "research/baffin-bound-owner-transition-v1.json";
const OWNER_RAW: &str = include_str!("../../../research/baffin-bound-owner-transition-v1.json");
const PARENT_FILE: &str = "research/baffin-bound-parent-owner-v1.json";

fn document() -> Value {
    serde_json::from_str(RAW).unwrap()
}
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
fn records(doc: &Value) -> Vec<(&'static str, Value)> {
    let mut result = vec![
        (
            "objects",
            serde_json::from_str::<Value>(OWNER_RAW).unwrap()["owner"].clone(),
        ),
        ("length_assessments", doc["length_assessment"].clone()),
        ("measurements", doc["measurement"].clone()),
        ("claims", doc["claim"].clone()),
        ("current_length_bound_admissions", doc["admission"].clone()),
    ];
    for row in doc["source_records"].as_array().unwrap() {
        result.push(("sources", row.clone()));
    }
    for row in doc["scenario_records"].as_array().unwrap() {
        result.push(("current_length_bound_scenarios", row.clone()));
    }
    result
}
fn present(bundle: &Bundle, doc: &Value) -> bool {
    // Indexing a pending source contract alone must not activate this edition.
    bundle.manifest.get(VERSION).is_some()
        || bundle.collections.values().flatten().any(|row| {
            row["id"] == doc["measurement"]["id"]
                || row["id"] == doc["admission"]["id"]
                || doc["source_records"]
                    .as_array()
                    .unwrap()
                    .iter()
                    .any(|source| row["id"] == source["id"])
                || row["length_bound_admission_id"] == doc["admission"]["id"]
                || row["admission_id"] == doc["admission"]["id"]
                || row["method_source_id"] == doc["measurement"]["method_source_id"]
                || row["gate_distance_method_source_id"] == doc["measurement"]["method_source_id"]
                || row["measurement_admission_file"] == FILE
                || row["regional_length_bound"]["admission_id"] == doc["admission"]["id"]
        })
}
pub(crate) fn verified_assessment_overlay(bundle: &Bundle) -> Result<Option<Value>, String> {
    let doc = document();
    if !present(bundle, &doc) {
        return Ok(None);
    }
    validate(bundle)?;
    Ok(Some(doc["length_assessment"].clone()))
}
pub fn validate(bundle: &Bundle) -> Result<(), String> {
    let doc = document();
    if !present(bundle, &doc) {
        return Ok(());
    }
    if bundle.manifest[VERSION] != "1" || bundle.manifest["input_sha256"][FILE] != pin(RAW) {
        return Err("Changed Baffin geographic-bound edition or contract".into());
    }
    for (path, hash) in doc["input_sha256"].as_object().unwrap() {
        if bundle.manifest["input_sha256"][path] != *hash {
            return Err(format!(
                "Changed Baffin geographic-bound dependency: {path}"
            ));
        }
    }
    let owner: Value = serde_json::from_str(OWNER_RAW).unwrap();
    if bundle.manifest["input_sha256"][OWNER_FILE] != pin(OWNER_RAW)
        || bundle.manifest["input_sha256"][PARENT_FILE] != owner["parent_owner_sha256"]
        || owner["admission_contract_sha256"] != pin(RAW)
    {
        return Err("Changed Baffin owner transition or parent projection".into());
    }
    for (name, expected) in records(&doc) {
        let rows: Vec<_> = bundle
            .collections
            .get(name)
            .into_iter()
            .flatten()
            .filter(|row| row["id"] == expected["id"])
            .collect();
        if rows != vec![&expected] {
            return Err(format!("Changed Baffin geographic-bound {name}"));
        }
    }
    let assessments = bundle.collections["length_assessments"]
        .iter()
        .filter(|row| row["entity_id"] == "current:baffin")
        .count();
    let scenarios = bundle.collections["current_length_bound_scenarios"]
        .iter()
        .filter(|row| {
            row["entity_id"] == "current:baffin"
                || row["admission_id"] == doc["admission"]["id"]
                || row["measurement_id"] == doc["measurement"]["id"]
        })
        .count();
    if assessments != 1 || scenarios != 9 {
        return Err("Duplicate or transferred Baffin assessment/scenarios".into());
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn fixture() -> Bundle {
        let doc = document();
        let mut inputs = doc["input_sha256"].clone();
        inputs[FILE] = json!(pin(RAW));
        inputs[OWNER_FILE] = json!(pin(OWNER_RAW));
        inputs[PARENT_FILE] =
            serde_json::from_str::<Value>(OWNER_RAW).unwrap()["parent_owner_sha256"].clone();
        let mut collections = std::collections::BTreeMap::new();
        for (name, row) in records(&doc) {
            collections
                .entry(name.into())
                .or_insert_with(Vec::new)
                .push(row);
        }
        Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest: json!({"input_sha256":inputs,"baffin_latitude_gate_bound_version":"1"}),
            collections,
        }
    }
    #[test]
    fn exact_records_and_editorial_scenarios_pass() {
        let bundle = fixture();
        validate(&bundle).unwrap();
        assert_eq!(
            verified_assessment_overlay(&bundle).unwrap(),
            Some(document()["length_assessment"].clone())
        );
    }
    #[test]
    fn pending_source_index_does_not_activate_measurement() {
        let bundle = Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest: json!({"input_sha256":{(FILE):pin(RAW)}}),
            collections: std::collections::BTreeMap::new(),
        };
        validate(&bundle).unwrap();
        assert!(verified_assessment_overlay(&bundle).unwrap().is_none());
    }
    #[test]
    fn absent_or_corrupted_complete_record_rejects() {
        for (name, row) in records(&document()) {
            let mut bundle = fixture();
            let rows = bundle.collections.get_mut(name).unwrap();
            rows.retain(|r| r["id"] != row["id"]);
            assert!(validate(&bundle).is_err(), "{name}");
        }
        for (name, field, value) in [
            ("measurements", "value", json!(1100)),
            ("measurements", "rank_eligible", json!(true)),
            ("measurements", "entity_id", json!("current:other")),
            ("measurements", "annual_length_range_km", json!([893, 1116])),
            (
                "current_length_bound_scenarios",
                "is_observation",
                json!(true),
            ),
            (
                "current_length_bound_admissions",
                "study_season",
                json!("winter"),
            ),
        ] {
            let mut bundle = fixture();
            bundle.collections.get_mut(name).unwrap()[0][field] = value;
            assert!(validate(&bundle).is_err(), "{name}.{field}");
        }
    }
    #[test]
    fn duplicate_transferred_scenario_and_changed_pin_reject() {
        let mut bundle = fixture();
        let mut row = bundle.collections["current_length_bound_scenarios"][0].clone();
        row["id"] = json!("extra");
        row["entity_id"] = json!("current:other");
        bundle
            .collections
            .get_mut("current_length_bound_scenarios")
            .unwrap()
            .push(row);
        assert!(validate(&bundle).is_err());
        let mut bundle = fixture();
        bundle.manifest["input_sha256"][FILE] = json!("changed");
        assert!(validate(&bundle).is_err());
        let mut bundle = fixture();
        bundle.manifest.as_object_mut().unwrap().remove(VERSION);
        assert!(validate(&bundle).is_err());
    }
    #[test]
    fn changed_physical_owner_fields_and_missing_transition_pin_reject() {
        for (field, value) in [
            ("width_ids", json!([])),
            ("map_features", json!([])),
            ("latest_observation_date", json!("2026-10-24")),
            ("capabilities", json!({"reported_length":1})),
        ] {
            let mut bundle = fixture();
            bundle.collections.get_mut("objects").unwrap()[0][field] = value;
            assert!(validate(&bundle).is_err(), "{field}");
        }
        let mut bundle = fixture();
        bundle.manifest["input_sha256"]
            .as_object_mut()
            .unwrap()
            .remove(OWNER_FILE);
        assert!(validate(&bundle).is_err());
    }
}
