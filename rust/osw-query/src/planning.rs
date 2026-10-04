//! Editorial route decisions stay bound to their source worklist and owner.
use serde_json::Value;
use std::collections::BTreeMap;

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
            || source["published_length_rank_eligible"] != false
            || !owner["published_length_km"].is_null()
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
        if record["status"] != "editorial_planning_crosswalk_not_scientific_classification_approval"
            || record["source_catalog_file"]
                != "research/ocean-current-reference-path-candidates.json"
            || record["source_catalog_sha256"]
                != manifest["input_sha256"]["research/ocean-current-reference-path-candidates.json"]
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
