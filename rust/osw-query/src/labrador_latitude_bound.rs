//! Described latitude gates remain an unranked, conditional geographic floor.
use crate::Bundle;
use serde_json::Value;
use sha2::{Digest, Sha256};

const FILE: &str = "research/labrador-latitude-gate-bound-v1.json";
const RAW: &str = include_str!("../../../research/labrador-latitude-gate-bound-v1.json");
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
        ("sources", doc["source_record"].clone()),
        ("sources", doc["method_source"].clone()),
    ]
}
fn present(bundle: &Bundle) -> bool {
    let doc = document();
    let expected_records = records();
    bundle.manifest["labrador_latitude_gate_bound_version"].is_string()
        || bundle.manifest["input_sha256"][FILE].is_string()
        || bundle.collections.values().flatten().any(|r| {
            r["measurement_admission_file"] == FILE
                || r["method_source_id"] == doc["method_source"]["id"]
                || r["gate_distance_method_source_id"] == doc["method_source"]["id"]
                || expected_records.iter().any(|(_, expected)| {
                    r["id"] == expected["id"] && r["id"] != doc["length_assessment"]["id"]
                })
        })
}

pub(crate) fn verified_assessment_overlay(bundle: &Bundle) -> Result<Option<Value>, String> {
    if !present(bundle) {
        return Ok(None);
    }
    validate(bundle)?;
    Ok(Some(document()["length_assessment"].clone()))
}

pub fn validate(bundle: &Bundle) -> Result<(), String> {
    if !present(bundle) {
        return Ok(());
    }
    let doc = document();
    let expected_records = records();
    if bundle.manifest["labrador_latitude_gate_bound_version"] != "1"
        || bundle.manifest["input_sha256"][FILE] != pin(RAW)
    {
        return Err("Changed Labrador geographic-bound edition or source".into());
    }
    for (path, hash) in doc["input_sha256"].as_object().unwrap() {
        if bundle.manifest["input_sha256"][path] != *hash {
            return Err(format!(
                "Changed Labrador geographic-bound dependency: {path}"
            ));
        }
    }
    for (name, expected) in expected_records {
        let rows: Vec<_> = bundle
            .collections
            .get(name)
            .into_iter()
            .flatten()
            .filter(|r| r["id"] == expected["id"])
            .collect();
        if rows != vec![&expected] {
            return Err(format!("Changed Labrador geographic-bound {name}"));
        }
    }
    if bundle.collections["length_assessments"]
        .iter()
        .filter(|r| r["entity_id"] == "current:labrador")
        .count()
        != 1
    {
        return Err("Duplicate Labrador length assessment".into());
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
            manifest: json!({"input_sha256":inputs,"labrador_latitude_gate_bound_version":"1"}),
            collections,
        }
    }
    #[test]
    fn expected_table_composition_requires_complete_proof_and_keeps_other_rows() {
        let mut b = fixture();
        let previous = json!([
            {"id":"length_assessment:labrador","entity_id":"current:labrador","evidence_status":"no_numeric_length"},
            {"id":"length_assessment:other","entity_id":"current:other","rank_eligible":true,"published_length_km":1234}
        ]);
        let actual = crate::length_assessment_overlays::expected(&b, &previous).unwrap();
        assert_eq!(actual[0], document()["length_assessment"]);
        assert_eq!(actual[1], previous[1]);
        let duplicate = json!([previous[0], previous[0]]);
        assert!(crate::length_assessment_overlays::expected(&b, &duplicate).is_err());
        b.collections.remove("claims");
        assert!(crate::length_assessment_overlays::expected(&b, &previous).is_err());
        b.manifest = json!({});
        b.collections.clear();
        assert_eq!(
            crate::length_assessment_overlays::expected(&b, &previous).unwrap(),
            previous
        );
    }
    #[test]
    fn accepts_scoped_floor_and_legacy_nac_only_collection() {
        validate(&fixture()).unwrap();
        let mut legacy = fixture();
        legacy.manifest = json!({});
        legacy.collections.clear();
        legacy.collections.insert(
            "current_length_bound_admissions".into(),
            vec![json!({"id":"current_length_bound_admission:north-atlantic"})],
        );
        legacy.collections.insert("length_assessments".into(),
            vec![json!({"id":"length_assessment:labrador","entity_id":"current:labrador","evidence_status":"no_numeric_length"})]);
        validate(&legacy).unwrap();
    }
    #[test]
    fn rejects_rank_owner_source_numeric_or_seasonal_transfer() {
        for (collection, key, value) in [
            ("length_assessments", "rank_eligible", json!(true)),
            ("length_assessments", "published_length_km", json!(1800)),
            ("length_assessments", "lower_bound_km", json!(1900)),
            ("measurements", "entity_id", json!("current:north-atlantic")),
            ("measurements", "source_id", json!("source:other")),
            ("measurements", "guaranteed_physical_minimum", json!(true)),
            (
                "measurements",
                "annual_length_range_km",
                json!([1780, 2003]),
            ),
            ("claims", "value", json!(1900)),
        ] {
            let mut b = fixture();
            b.collections.get_mut(collection).unwrap()[0][key] = value;
            assert!(validate(&b).is_err(), "{collection}/{key}");
        }
    }
    #[test]
    fn rejects_missing_receipts_dependencies_rows_and_duplicates() {
        let mut b = fixture();
        b.manifest = json!({});
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.manifest["input_sha256"] = json!({});
        b.manifest["input_sha256"][FILE] = json!(pin(RAW));
        assert!(validate(&b).is_err());
        for name in [
            "current_length_bound_admissions",
            "length_assessments",
            "measurements",
            "claims",
            "sources",
        ] {
            let mut missing = fixture();
            missing.collections.remove(name);
            assert!(validate(&missing).is_err(), "missing {name}");
            let mut duplicate = fixture();
            let row = duplicate.collections[name][0].clone();
            duplicate.collections.get_mut(name).unwrap().push(row);
            assert!(validate(&duplicate).is_err(), "duplicate {name}");
        }
        let mut b = fixture();
        b.collections
            .get_mut("length_assessments")
            .unwrap()
            .push(json!({"id":"other","entity_id":"current:labrador"}));
        assert!(validate(&b).is_err());
    }
}
