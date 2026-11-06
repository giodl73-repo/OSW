//! Editorial route decisions stay bound to their source worklist and owner.
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;

const EICC_SOURCE: &str = "research/eicc-regional-reference-admission-candidate-v1.json";
const EICC_SOURCE_SHA: &str = "6c02b4c09e214b5080ce5017849ad9ade9f034c579da7d5c3d1b5a056ad5db9d";
const EICC_BASE: &str = "research/ocean-current-reference-path-candidates.json";

// A source-qualified editorial revision must carry its exact new source bytes and
// exact prior decision. All other currents retain the original planning contract.
fn revised_eicc_source(
    record: &Value,
    manifest: &Value,
    collections: &BTreeMap<String, Vec<Value>>,
) -> Result<Option<&'static str>, String> {
    let revision = &manifest["eicc_reference_spectral_delivery_v1"]["planning_revision"];
    if record["entity_id"] != "current:east-india-coastal" || revision.is_null() {
        return Ok(None);
    }
    let refuse = || "Invalid EICC source-qualified planning revision".to_owned();
    let raw = revision["source_json"].as_str().ok_or_else(refuse)?;
    let source: Value = serde_json::from_str(raw).map_err(|_| refuse())?;
    if revision["schema"] != "osw.eicc-source-reference-planning-revision.v1"
        || revision["owner_id"] != record["entity_id"]
        || revision["source_file"] != EICC_SOURCE
        || revision["source_sha256"] != EICC_SOURCE_SHA
        || format!("{:x}", Sha256::digest(raw.as_bytes())) != EICC_SOURCE_SHA
        || manifest["input_sha256"][EICC_SOURCE] != EICC_SOURCE_SHA
        || source["schema"] != "osw.eicc-regional-reference-admission-candidate.v1"
        || source["new_whole_current_lengths"] != 0
        || source["new_physical_dimensions_admitted"] != 0
    {
        return Err(refuse());
    }
    let prior_raw = revision["prior_decision_json"].as_str().ok_or_else(refuse)?;
    let prior: Value = serde_json::from_str(prior_raw).map_err(|_| refuse())?;
    if prior != record["prior_route_decision"]
        || prior["id"] != record["id"]
        || prior["entity_id"] != record["entity_id"]
        || prior["source_catalog_file"] != EICC_BASE
        || prior["source_catalog_sha256"] != manifest["input_sha256"][EICC_BASE]
        || prior["source_catalog_sha256"].as_str().is_none_or(|s| s.len() != 64)
        || prior["candidate_count"] != 0
        || prior["route_ids"] != serde_json::json!([])
        || prior["source_decision"]["candidate_ids"] != serde_json::json!([])
        || prior["rank_eligible"] != false
    {
        return Err(refuse());
    }
    let changed = ["construction_status", "candidate_count", "route_ids", "next_action",
        "source_catalog_file", "source_catalog_sha256", "source_url", "source_decision"];
    let prior_fields = prior.as_object().ok_or_else(refuse)?;
    if prior_fields.iter().any(|(key, value)| !changed.contains(&key.as_str()) && record.get(key) != Some(value))
        || record.as_object().ok_or_else(refuse)?.keys().any(|key| !prior_fields.contains_key(key) && key != "prior_route_decision")
    {
        return Err(refuse());
    }
    let changed_source = ["candidate_ids", "reference_path_decision", "next_action", "name_source_url"];
    let prior_source = prior["source_decision"].as_object().ok_or_else(refuse)?;
    let new_source = record["source_decision"].as_object().ok_or_else(refuse)?;
    if prior_source.iter().any(|(key, value)| !changed_source.contains(&key.as_str()) && new_source.get(key) != Some(value))
        || new_source.keys().any(|key| !prior_source.contains_key(key))
    {
        return Err(refuse());
    }
    let rows = source["rows"].as_array().ok_or_else(refuse)?;
    let ids = rows.iter().map(|row| row["id"].clone()).collect::<Vec<_>>();
    if rows.len() != 2 || record["route_ids"] != serde_json::json!(ids)
        || record["construction_status"] != "regional_source_anchor_connections_constructed"
        || record["source_url"] != rows[0]["source_url"]
    {
        return Err(refuse());
    }
    for (i, candidate) in rows.iter().enumerate() {
        let row = collections.get("reference_routes").into_iter().flatten()
            .find(|row| row["id"] == candidate["id"]).ok_or_else(refuse)?;
        if candidate["entity_id"] != record["entity_id"]
            || row["source_file"] != EICC_SOURCE
            || row["source_file_sha256"] != EICC_SOURCE_SHA
            || row["source_pointer"] != format!("/rows/{i}")
            || row["coordinates_lon_lat"] != candidate["coordinates_lon_lat"]
            || row["source_url"] != candidate["source_url"]
            || row["approximate_reference_path_km"] != candidate["approximate_reference_path_km"]
            || row["rank_eligible"] != false
            || row["physical_current_axis_admitted"] != false
            || row["physical_state_join_eligible"] != false
            || row["seasonal_playback_eligible"] != false
            || !row["whole_current_length_km"].is_null()
            || !row["annual_length_range_km"].is_null()
        {
            return Err(refuse());
        }
    }
    Ok(Some(EICC_SOURCE))
}

pub fn validate(
    collections: &BTreeMap<String, Vec<Value>>,
    manifest: &Value,
) -> Result<(), String> {
    for record in collections.get("route_decisions").into_iter().flatten() {
        let source = &record["source_decision"];
        let current = source["current_id"]
            .as_str()
            .ok_or("Missing planning source identity")?;
        let owner = collections["objects"]
            .iter()
            .find(|r| r["id"] == format!("current:{current}"))
            .ok_or("Unresolved planning current")?;
        if record["id"] != format!("route-decision:{current}")
            || record["entity_id"] != owner["id"]
            || record["candidate_count"].as_u64()
                != source["candidate_ids"].as_array().map(|r| r.len() as u64)
            || record["rank_eligible"] != false
            || source["published_length_rank_eligible"] != !owner["published_length_km"].is_null()
            || owner["route_decision_ids"] != serde_json::json!([record["id"]])
        {
            return Err("Planning identity, coverage or admission mismatch".into());
        }
        for (key, source_key) in [
            ("current_id", "current_id"),
            ("label", "name"),
            ("strategy_id", "route_strategy_id"),
            ("strategy_label", "route_strategy_label"),
            ("construction_status", "reference_path_decision"),
            ("route_ids", "candidate_ids"),
            ("next_action", "next_action"),
            ("scope", "existing_scope"),
            ("status", "planning_status"),
            ("source_url", "name_source_url"),
        ] {
            if source.get(source_key).is_none() || record[key] != source[source_key] {
                return Err(format!("Planning projection differs in {key}"));
            }
        }
        let source_path = if let Some(path) = revised_eicc_source(record, manifest, collections)? {
            path
        } else if let Some((expected, path)) =
            crate::current_catalogue::planning_source(current, manifest)
        {
            if source != &expected {
                return Err("Changed admitted-current route planning source".into());
            }
            path
        } else {
            "research/ocean-current-reference-path-candidates.json"
        };
        if record["status"] != "editorial_planning_crosswalk_not_scientific_classification_approval"
            || record["source_catalog_file"] != source_path
            || record["source_catalog_sha256"] != manifest["input_sha256"][source_path]
            || record["source_catalog_sha256"]
                .as_str()
                .is_none_or(|h| h.len() != 64)
        {
            return Err("Planning source receipt mismatch".into());
        }
        let mut linked = record["route_ids"]
            .as_array()
            .ok_or("Invalid planning routes")?
            .clone();
        linked.sort_by(|a, b| a.as_str().cmp(&b.as_str()));
        let mut actual = collections
            .get("reference_routes")
            .into_iter()
            .flatten()
            .filter(|r| r["current_id"] == current)
            .map(|r| r["id"].clone())
            .collect::<Vec<_>>();
        actual.sort_by(|a, b| a.as_str().cmp(&b.as_str()));
        let mut owner_routes = owner["route_ids"]
            .as_array()
            .ok_or("Missing owner routes")?
            .clone();
        owner_routes.sort_by(|a, b| a.as_str().cmp(&b.as_str()));
        if linked != actual || linked != owner_routes {
            return Err("Planning route inventory mismatch".into());
        }
        for review in record["scope_reviews"]
            .as_array()
            .ok_or("Missing planning scope reviews")?
        {
            let note = &review["note"];
            let file = note["audit_file"].as_str().ok_or("Missing audit file")?;
            if note["current_id"] != current
                || review["document"]["current_id"] != current
                || review["source_sha256"]
                    .as_str()
                    .is_none_or(|h| h.len() != 64)
                || review["source_sha256"] != manifest["input_sha256"][file]
                || !owner["scope_notes"]
                    .as_array()
                    .is_some_and(|rs| rs.contains(note))
            {
                return Err("Planning scope review binding mismatch".into());
            }
        }
        let notes = record["scope_reviews"]
            .as_array()
            .unwrap()
            .iter()
            .map(|r| r["note"].clone())
            .collect::<Vec<_>>();
        if owner["scope_notes"].as_array() != Some(&notes) {
            return Err("Incomplete planning scope reviews".into());
        }
    }
    if collections.contains_key("route_decisions") {
        for owner in &collections["objects"] {
            if owner["type"] == "named_current"
                && owner["published_length_km"].is_null()
                && !collections["route_decisions"]
                    .iter()
                    .any(|r| r["entity_id"] == owner["id"])
            {
                return Err("Missing remaining-current planning decision".into());
            }
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn revised_fixture() -> (BTreeMap<String, Vec<Value>>, Value) {
        let raw = std::fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"),
            "/../../research/eicc-regional-reference-admission-candidate-v1.json")).unwrap();
        let source: Value = serde_json::from_str(&raw).unwrap();
        let prior_source = json!({"current_id":"east-india-coastal","name":"EICC",
            "route_strategy_id":"source-review","route_strategy_label":"Review sources",
            "reference_path_decision":"pending","candidate_ids":[],"next_action":"Review source",
            "existing_scope":"Regional source review","planning_status":"editorial_planning_crosswalk_not_scientific_classification_approval",
            "name_source_url":"https://example.org/original","published_length_rank_eligible":false});
        let prior = json!({"id":"route-decision:east-india-coastal","entity_id":"current:east-india-coastal",
            "current_id":"east-india-coastal","label":"EICC","strategy_id":"source-review",
            "strategy_label":"Review sources","construction_status":"pending","route_ids":[],
            "candidate_count":0,"next_action":"Review source","scope":"Regional source review",
            "status":"editorial_planning_crosswalk_not_scientific_classification_approval",
            "source_url":"https://example.org/original","source_catalog_file":EICC_BASE,
            "source_catalog_sha256":"1".repeat(64),"rank_eligible":false,"scope_reviews":[],"source_decision":prior_source});
        let ids = source["rows"].as_array().unwrap().iter().map(|r| r["id"].clone()).collect::<Vec<_>>();
        let mut record = prior.clone();
        record["prior_route_decision"] = prior.clone();
        record["route_ids"] = json!(ids.clone());
        record["candidate_count"] = json!(2);
        record["construction_status"] = json!("regional_source_anchor_connections_constructed");
        record["next_action"] = json!("Recover whole-current axes");
        record["source_url"] = source["rows"][0]["source_url"].clone();
        record["source_catalog_file"] = json!(EICC_SOURCE);
        record["source_catalog_sha256"] = json!(EICC_SOURCE_SHA);
        for (target, origin) in [("candidate_ids","route_ids"),("reference_path_decision","construction_status"),
            ("next_action","next_action"),("name_source_url","source_url")] {
            record["source_decision"][target] = record[origin].clone();
        }
        let routes = source["rows"].as_array().unwrap().iter().enumerate().map(|(i, row)| {
            let mut result = row.clone();
            result["source_file"] = json!(EICC_SOURCE);
            result["source_file_sha256"] = json!(EICC_SOURCE_SHA);
            result["source_pointer"] = json!(format!("/rows/{i}"));
            result
        }).collect();
        let objects = vec![json!({"id":"current:east-india-coastal","type":"named_current",
            "published_length_km":null,"route_ids":ids,"route_decision_ids":[record["id"]],"scope_notes":[]})];
        let manifest = json!({"input_sha256":{(EICC_SOURCE):EICC_SOURCE_SHA,(EICC_BASE):"1".repeat(64)},
            "eicc_reference_spectral_delivery_v1":{"planning_revision":{
                "schema":"osw.eicc-source-reference-planning-revision.v1","owner_id":"current:east-india-coastal",
                "source_file":EICC_SOURCE,"source_sha256":EICC_SOURCE_SHA,"source_json":raw,
                "prior_decision_json":serde_json::to_string(&prior).unwrap()}}});
        (BTreeMap::from([("objects".into(), objects), ("reference_routes".into(), routes),
                        ("route_decisions".into(), vec![record])]), manifest)
    }

    #[test]
    fn source_qualified_revision_retains_original_and_resolves_two_routes() {
        let (collections, manifest) = revised_fixture();
        validate(&collections, &manifest).unwrap();
    }

    #[test]
    fn revised_source_bytes_and_prior_decision_cannot_change() {
        for field in ["source_json", "prior_decision_json"] {
            let (collections, mut manifest) = revised_fixture();
            manifest["eicc_reference_spectral_delivery_v1"]["planning_revision"][field] = json!("{}");
            assert!(validate(&collections, &manifest).is_err());
        }
    }

    #[test]
    fn revised_routes_cannot_gain_physical_admission_or_different_source() {
        for field in ["rank_eligible", "physical_current_axis_admitted", "source_file_sha256"] {
            let (mut collections, manifest) = revised_fixture();
            collections.get_mut("reference_routes").unwrap()[0][field] = json!(true);
            assert!(validate(&collections, &manifest).is_err());
        }
    }

    #[test]
    fn absent_revision_uses_original_planning_source_rules() {
        let (collections, mut manifest) = revised_fixture();
        manifest["eicc_reference_spectral_delivery_v1"] = Value::Null;
        assert_eq!(revised_eicc_source(&collections["route_decisions"][0], &manifest, &collections).unwrap(), None);
        assert!(validate(&collections, &manifest).is_err());
    }
}
