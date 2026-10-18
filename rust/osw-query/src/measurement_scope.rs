//! Scope assessments never promote related/member dimensions to a parent.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;
const PATH: &str = "research/current-measurement-object-scope-index.json";
const RAW: &str = include_str!("../../../research/current-measurement-object-scope-index.json");

pub fn validate(
    collections: &BTreeMap<String, Vec<Value>>,
    manifest: &Value,
) -> Result<(), String> {
    let objects = collections.get("objects");
    let present = manifest["input_sha256"][PATH].is_string()
        || objects.is_some_and(|rows| {
            rows.iter().any(|r| {
                r["scope_audits"].as_array().is_some_and(|a| {
                    a.iter()
                        .any(|d| d["schema"] == "osw.current-measurement-object-scope.v1")
                })
            })
        });
    if !present {
        return Ok(());
    }
    let expected: Value =
        serde_json::from_str(RAW).map_err(|_| "Invalid compiled measurement scope")?;
    let hash = format!("{:x}", Sha256::digest(RAW.as_bytes()));
    if manifest["input_sha256"][PATH] != hash
        || manifest["input_sha256"]["research/ocean-current-scope-notes.json"]
            != expected["scope_notes_sha256"]
    {
        return Err("Measurement scope index/notes binding mismatch".into());
    }
    if manifest["input_sha256"][expected["generator_file"].as_str().unwrap()]
        != expected["generator_sha256"]
    {
        return Err("Measurement scope operator mismatch".into());
    }
    for (file, pin) in expected["input_sha256"].as_object().unwrap() {
        if manifest["input_sha256"][file] != *pin {
            return Err("Measurement scope input mismatch".into());
        }
    }
    for record in expected["records"].as_array().unwrap() {
        let owner = objects
            .into_iter()
            .flatten()
            .find(|r| r["id"] == format!("current:{}", record["current_id"].as_str().unwrap()))
            .ok_or("Missing scope owner")?;
        let file = record["source_file"].as_str().unwrap();
        let figure = record["figure_file"].as_str().unwrap();
        if manifest["input_sha256"][file] != record["source_sha256"]
            || manifest["input_sha256"][figure] != record["figure_sha256"]
        {
            return Err("Measurement scope document/figure mismatch".into());
        }
        let mut note = record["note"].clone();
        let proposed = record["document"]["members"]
            .as_array()
            .unwrap()
            .iter()
            .filter(|r| r["record_status"] == "proposed")
            .map(|r| json!({"id":r["id"],"name":r["label"]}))
            .collect::<Vec<_>>();
        if !proposed.is_empty() {
            note["related_proposed_currents"] = json!(proposed);
        }
        if !owner["scope_notes"]
            .as_array()
            .is_some_and(|rows| rows.contains(&note))
            || !owner["scope_audits"]
                .as_array()
                .is_some_and(|rows| rows.contains(&record["document"]))
            || !owner["width_ids"]
                .as_array()
                .is_some_and(|rows| rows.is_empty())
        {
            return Err("Measurement scope owner projection/admission mismatch".into());
        }
        for decision in collections
            .get("route_decisions")
            .into_iter()
            .flatten()
            .filter(|r| r["current_id"] == record["current_id"])
        {
            let reviews = decision["scope_reviews"]
                .as_array()
                .ok_or("Missing measurement scope planning reviews")?;
            let matching = reviews
                .iter()
                .filter(|r| r["note"]["audit_file"] == file)
                .collect::<Vec<_>>();
            if matching.len() != 1
                || matching[0]["note"] != note
                || matching[0]["document"] != record["document"]
                || matching[0]["source_sha256"] != record["source_sha256"]
            {
                return Err("Measurement scope planning projection mismatch".into());
            }
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn scope_source_projection_and_borrowed_widths_reject() {
        let index: Value = serde_json::from_str(RAW).unwrap();
        let mut inputs = index["input_sha256"].clone();
        inputs[PATH] = json!(format!("{:x}", Sha256::digest(RAW.as_bytes())));
        inputs["research/ocean-current-scope-notes.json"] = index["scope_notes_sha256"].clone();
        inputs[index["generator_file"].as_str().unwrap()] = index["generator_sha256"].clone();
        let mut owners = vec![];
        for r in index["records"].as_array().unwrap() {
            inputs[r["source_file"].as_str().unwrap()] = r["source_sha256"].clone();
            inputs[r["figure_file"].as_str().unwrap()] = r["figure_sha256"].clone();
            let mut note = r["note"].clone();
            let proposed = r["document"]["members"]
                .as_array()
                .unwrap()
                .iter()
                .filter(|m| m["record_status"] == "proposed")
                .map(|m| json!({"id":m["id"],"name":m["label"]}))
                .collect::<Vec<_>>();
            if !proposed.is_empty() {
                note["related_proposed_currents"] = json!(proposed);
            }
            owners.push(json!({"id":format!("current:{}",r["current_id"].as_str().unwrap()),"scope_notes":[note],"scope_audits":[r["document"]],"width_ids":[]}));
        }
        let collections = BTreeMap::from([("objects".into(), owners)]);
        let manifest = json!({"input_sha256":inputs});
        assert!(validate(&collections, &manifest).is_ok());
        for field in [
            "parent_width_km",
            "aliases_resolved",
            "member_measurements_inherited",
            "new_width_record_admitted",
        ] {
            let mut bad = collections.clone();
            bad.get_mut("objects").unwrap()[0]["scope_audits"][0][field] = json!(true);
            assert!(validate(&bad, &manifest).is_err());
        }
        let mut bad = collections.clone();
        bad.get_mut("objects").unwrap()[0]["width_ids"] = json!(["borrowed-member-width"]);
        assert!(validate(&bad, &manifest).is_err());
        let mut missing = collections.clone();
        missing.get_mut("objects").unwrap().remove(0);
        assert!(validate(&missing, &manifest).is_err());
        let mut rebound = manifest.clone();
        rebound["input_sha256"][PATH] = json!("0".repeat(64));
        assert!(validate(&collections, &rebound).is_err());
        let record = &index["records"][0];
        let owner = &collections["objects"][0];
        let review = json!({"note":owner["scope_notes"][0],
            "document":record["document"],"source_sha256":record["source_sha256"]});
        let mut planning = collections.clone();
        planning.insert(
            "route_decisions".into(),
            vec![json!({
            "current_id":record["current_id"],"scope_reviews":[review]})],
        );
        assert!(validate(&planning, &manifest).is_ok());
        for field in ["document", "note", "source_sha256"] {
            let mut bad = planning.clone();
            bad.get_mut("route_decisions").unwrap()[0]["scope_reviews"][0][field] = json!(null);
            assert!(validate(&bad, &manifest).is_err());
        }
    }
}
