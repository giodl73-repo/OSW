//! Exact delivery contracts for the Indian identities and scoped source batch.
//! These guards admit source descriptions, never inferred physical envelopes.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};

const IDENTITY: (&str, &str) = (
    "research/indian-current-identity-query-contract-v1.json",
    include_str!("../../../research/indian-current-identity-query-contract-v1.json"),
);
const CONTEXT: (&str, &str) = (
    "research/indian-current-evidence-query-contract-v1.json",
    include_str!("../../../research/indian-current-evidence-query-contract-v1.json"),
);
const BRAZIL: (&str, &str) = (
    "research/brazil-regional-reach-query-contract-v1.json",
    include_str!("../../../research/brazil-regional-reach-query-contract-v1.json"),
);
const WIDTH: (&str, &str) = (
    "research/eicc-t24-published-width-admission-v1.json",
    include_str!("../../../research/eicc-t24-published-width-admission-v1.json"),
);
const PLANNING: (&str, &str) = (
    "research/indian-current-reference-route-planning-v1.json",
    include_str!("../../../research/indian-current-reference-route-planning-v1.json"),
);
const CONTRACTS: [(&str, &str); 5] = [IDENTITY, CONTEXT, BRAZIL, WIDTH, PLANNING];
const VERSION: &str = "indian-coastal-brazil-t24-v1";
fn doc(raw: &str) -> Value {
    serde_json::from_str(raw).expect("compiled delivery contract")
}
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
pub fn active_manifest(manifest: &Value) -> bool {
    manifest["current_gap_admission_version"] == VERSION
        || CONTRACTS
            .iter()
            .any(|(path, _)| manifest["input_sha256"][path].is_string())
}
pub fn active(bundle: &Bundle) -> bool {
    active_manifest(&bundle.manifest)
        || bundle
            .collections
            .get("entities")
            .into_iter()
            .flatten()
            .any(|row| {
                entities_from_contract()
                    .iter()
                    .any(|entity| entity["id"] == row["id"])
            })
}
fn entities_from_contract() -> Vec<Value> {
    doc(IDENTITY.1)["additions"]["entities"]
        .as_array()
        .unwrap()
        .clone()
}
pub fn entities(bundle: &Bundle) -> Vec<Value> {
    if active(bundle) {
        entities_from_contract()
    } else {
        vec![]
    }
}
pub fn widths(bundle: &Bundle) -> Vec<Value> {
    if active(bundle) {
        vec![doc(WIDTH.1)["width_record"].clone()]
    } else {
        vec![]
    }
}
pub fn planning_source(current: &str, manifest: &Value) -> Option<(Value, &'static str)> {
    if !active_manifest(manifest) {
        return None;
    }
    doc(PLANNING.1)["entries"]
        .as_array()
        .unwrap()
        .iter()
        .find(|row| row["current_id"] == current)
        .map(|row| (row.clone(), PLANNING.0))
}
pub fn decision(bundle: &Bundle, admission: &Value) -> Option<Value> {
    if !active(bundle) {
        return None;
    }
    let entity = entities_from_contract()
        .into_iter()
        .find(|row| row["id"] == admission["entity_id"])?;
    let measured = entity["id"] == "current:east-india-coastal";
    Some(
        json!({"current_id":admission["proposal_id"],"name":entity["label"],
        "measurement_ids":if measured { json!([doc(WIDTH.1)["width_record"]["id"]]) } else { json!([]) },
        "status":if measured { "scoped_published_width_admitted" } else { "identity_admitted_width_not_admitted" },
        "whole_current_width_km":null,"annual_width_range_km":null,"admission_id":admission["id"]}),
    )
}
fn expected_records() -> Vec<(String, Value)> {
    let mut records = vec![];
    for raw in [IDENTITY.1, CONTEXT.1] {
        for (name, rows) in doc(raw)["additions"].as_object().unwrap() {
            if name != "objects" {
                records.extend(
                    rows.as_array()
                        .unwrap()
                        .iter()
                        .map(|row| (name.clone(), row.clone())),
                );
            }
        }
    }
    let width = doc(WIDTH.1);
    for (name, row) in &mut records {
        if name == "current_reported_width_evidence"
            && row["id"] == width["width_record"]["source_statement_id"]
        {
            row["source_stage_canonical_width_admitted"] = row["canonical_width_admitted"].clone();
            row["canonical_width_admitted"] = json!(true);
            row["width_id"] = width["width_record"]["id"].clone();
            row["width_admission_id"] = width["admission"]["id"].clone();
        }
    }
    let brazil = doc(BRAZIL.1);
    for (name, key) in [
        ("current_regional_reaches", "record"),
        ("claims", "claim"),
        ("sources", "source_record"),
        ("sources", "method_source"),
    ] {
        records.push((name.into(), brazil[key].clone()));
    }
    for (name, key) in [
        ("widths", "width_record"),
        ("claims", "claim"),
        ("current_measurement_admissions", "admission"),
    ] {
        records.push((name.into(), width[key].clone()));
    }
    records
}
pub fn validate(bundle: &Bundle) -> Result<(), String> {
    if !active(bundle) {
        return Ok(());
    }
    if bundle.manifest["current_gap_admission_version"] != VERSION {
        return Err("Missing current-gap cohort version".into());
    }
    for (path, raw) in CONTRACTS {
        if bundle.manifest["input_sha256"][path] != pin(raw) {
            return Err(format!("Changed current-gap contract: {path}"));
        }
        if let Some(inputs) = doc(raw)["input_sha256"].as_object() {
            for (dependency, digest) in inputs {
                if bundle.manifest["input_sha256"][dependency] != *digest {
                    return Err(format!("Changed current-gap dependency: {dependency}"));
                }
            }
        }
    }
    for (name, expected) in expected_records() {
        let actual: Vec<_> = bundle
            .collections
            .get(&name)
            .into_iter()
            .flatten()
            .filter(|row| row["id"] == expected["id"])
            .collect();
        if actual != vec![&expected] {
            return Err(format!(
                "Changed current-gap {name} record: {}",
                expected["id"]
            ));
        }
    }
    let width = doc(WIDTH.1);
    for entity in entities_from_contract() {
        let owners: Vec<_> = bundle
            .collections
            .get("objects")
            .into_iter()
            .flatten()
            .filter(|row| row["id"] == entity["id"])
            .collect();
        if owners.len() != 1 {
            return Err("Missing current-gap owner".into());
        }
        let owner = owners[0];
        let measured = entity["id"] == width["width_record"]["entity_id"];
        let expected_widths = if measured {
            json!([width["width_record"]["id"]])
        } else {
            json!([])
        };
        if owner["width_ids"] != expected_widths
            || owner["capabilities"]["scoped_width"] != json!(usize::from(measured))
            || owner["capabilities"]["width_samples"] != 0
            || owner["capabilities"]["reported_length"] != 0
            || owner["capabilities"]["time_samples"] != 0
            || owner["measurement_ids"] != json!([])
            || owner["width_sample_ids"] != json!([])
            || owner["state_codes"] != json!([])
            || owner["state_evidence"] != json!([])
            || owner["route_ids"] != json!([])
            || owner["map_features"] != json!([])
            || !owner["published_length_km"].is_null()
            || !owner["latest_observation_date"].is_null()
        {
            return Err("Current-gap owner promoted unadmitted physical coverage".into());
        }
        for (collection, field, capability) in [
            (
                "current_direction_calendars",
                "direction_calendar_ids",
                "direction_calendars",
            ),
            (
                "current_direction_descriptions",
                "direction_description_ids",
                "direction_descriptions",
            ),
            (
                "current_reported_width_evidence",
                "reported_width_evidence_ids",
                "reported_width_evidence",
            ),
            (
                "current_cross_shore_context",
                "cross_shore_context_ids",
                "cross_shore_context",
            ),
            (
                "current_regime_context",
                "regime_context_ids",
                "regime_context",
            ),
        ] {
            let refs: Vec<_> = bundle
                .collections
                .get(collection)
                .into_iter()
                .flatten()
                .filter(|row| row["entity_id"] == entity["id"])
                .map(|row| row["id"].clone())
                .collect();
            // Owners without any context in this collection may omit the field.
            if (!refs.is_empty() || !owner[field].is_null()) && owner[field] != json!(refs)
                || owner["capabilities"][capability].as_u64().unwrap_or(0) != refs.len() as u64
            {
                return Err(format!("Changed current-gap context ownership: {field}"));
            }
        }
    }
    let registry: std::collections::BTreeSet<_> = bundle
        .collections
        .get("sources")
        .into_iter()
        .flatten()
        .filter_map(|row| row["id"].as_str())
        .collect();
    for owner in bundle.collections.get("objects").into_iter().flatten() {
        let refs = owner["source_ids"]
            .as_array()
            .ok_or("Missing current-gap owner provenance")?;
        let unique: std::collections::BTreeSet<_> = refs.iter().filter_map(Value::as_str).collect();
        if unique.len() != refs.len()
            || unique.iter().any(|id| !registry.contains(id))
            || owner["linked_source_count"].as_u64() != Some(refs.len() as u64)
        {
            return Err("Invalid current-gap owner provenance projection".into());
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> Bundle {
        let mut manifest = json!({"current_gap_admission_version":VERSION,"input_sha256":{}});
        for (path, raw) in CONTRACTS {
            manifest["input_sha256"][path] = json!(pin(raw));
            if let Some(inputs) = doc(raw)["input_sha256"].as_object() {
                for (key, value) in inputs {
                    manifest["input_sha256"][key] = value.clone();
                }
            }
        }
        let mut collections = std::collections::BTreeMap::<String, Vec<Value>>::new();
        for (name, row) in expected_records() {
            collections.entry(name).or_default().push(row);
        }
        let mut objects = doc(IDENTITY.1)["additions"]["objects"]
            .as_array()
            .unwrap()
            .clone();
        for owner in &mut objects {
            let mut refs = std::collections::BTreeSet::new();
            for rows in collections.values() {
                for row in rows.iter().filter(|row| row["entity_id"] == owner["id"]) {
                    for field in ["source_id", "method_source_id"] {
                        if let Some(id) = row[field].as_str() {
                            refs.insert(id.to_owned());
                        }
                    }
                    for id in row["source_ids"]
                        .as_array()
                        .into_iter()
                        .flatten()
                        .filter_map(Value::as_str)
                    {
                        refs.insert(id.to_owned());
                    }
                }
            }
            owner["source_ids"] = json!(refs);
            owner["linked_source_count"] = json!(refs.len());
            for (collection, field, capability) in [
                (
                    "current_direction_calendars",
                    "direction_calendar_ids",
                    "direction_calendars",
                ),
                (
                    "current_direction_descriptions",
                    "direction_description_ids",
                    "direction_descriptions",
                ),
                (
                    "current_reported_width_evidence",
                    "reported_width_evidence_ids",
                    "reported_width_evidence",
                ),
                (
                    "current_cross_shore_context",
                    "cross_shore_context_ids",
                    "cross_shore_context",
                ),
                (
                    "current_regime_context",
                    "regime_context_ids",
                    "regime_context",
                ),
            ] {
                let refs: Vec<_> = collections
                    .get(collection)
                    .unwrap()
                    .iter()
                    .filter(|row| row["entity_id"] == owner["id"])
                    .map(|row| row["id"].clone())
                    .collect();
                owner[field] = json!(refs);
                owner["capabilities"][capability] = json!(refs.len());
            }
            if owner["id"] == "current:east-india-coastal" {
                owner["width_ids"] = json!([doc(WIDTH.1)["width_record"]["id"]]);
                owner["capabilities"]["scoped_width"] = json!(1);
            }
        }
        collections.insert("objects".into(), objects);
        Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest,
            collections,
        }
    }
    #[test]
    fn exact_cohort_retains_scoped_source_semantics() {
        assert!(validate(&fixture()).is_ok());
        let mut b = fixture();
        b.collections.get_mut("widths").unwrap()[0]["annual_width_range_km"] = json!([100, 250]);
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections
            .get_mut("current_cross_shore_context")
            .unwrap()[0]["canonical_width_admitted"] = json!(true);
        assert!(validate(&b).is_err());
    }
    #[test]
    fn rejects_missing_receipt_rows_and_wrong_owner() {
        let mut b = fixture();
        b.manifest["input_sha256"][WIDTH.0] = json!("changed");
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections
            .get_mut("current_direction_descriptions")
            .unwrap()
            .pop();
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections.get_mut("objects").unwrap()[0]["width_ids"] =
            json!([doc(WIDTH.1)["width_record"]["id"]]);
        assert!(validate(&b).is_err());
    }
    #[test]
    fn identity_decisions_do_not_borrow_another_currents_width() {
        let b = fixture();
        for admission in &b.collections["current_identity_admissions"] {
            let row = decision(&b, admission).unwrap();
            assert_eq!(
                row["measurement_ids"].as_array().unwrap().len(),
                usize::from(admission["entity_id"] == "current:east-india-coastal")
            );
            assert!(row["annual_width_range_km"].is_null());
        }
    }
}
