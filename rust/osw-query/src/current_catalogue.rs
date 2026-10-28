//! Identity admissions extend a pinned base without admitting measurements.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
pub const PATH: &str = "research/ocean-current-identity-admissions.json";
pub const CATALOGUE: &str = "research/ocean-current-working-catalogue.json";
pub const RAW: &str = include_str!("../../../research/ocean-current-identity-admissions.json");
pub const CATALOGUE_RAW: &str =
    include_str!("../../../research/ocean-current-working-catalogue.json");
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
fn document() -> Value {
    serde_json::from_str(RAW).unwrap()
}
fn records() -> Vec<(&'static str, Value)> {
    let doc = document();
    let mut result = vec![];
    for entry in doc["entries"].as_array().unwrap() {
        let id = entry["proposal_id"].as_str().unwrap();
        let entity = &entry["entity"]["id"];
        let source = &entry["source"]["id"];
        result.push(("entities", entry["entity"].clone()));
        result.push(("sources", entry["source"].clone()));
        result.push(("names",json!({"id":format!("name:current:{id}"),"entity_id":entity,"label":entry["entity"]["label"],"preferred":true,"source_id":source})));
        result.push(("length_assessments",json!({"id":format!("length_assessment:{id}"),"entity_id":entity,
            "evidence_status":"reported_contextual_extent_pending_measurement_admission","rank_eligible":false,
            "published_length_km":null,"published_rank":null,"lower_bound_km":null,"proposed_system_length_km":null,
            "source_id":source,"length_source_id":source,"length_source_locator":"Introduction paragraph2",
            "scope":"Name identity admitted. The separately retained contextual650km report has not been admitted to the canonical ranked measurements.",
            "source_dimension_file":"research/ocean-current-inventory-expansion-candidates.json","source_dimension_proposal_id":id})));
        result.push(("current_identity_admissions", entry.clone()));
    }
    result
}
pub fn validate(bundle: &Bundle) -> Result<(), String> {
    let required = bundle.manifest["input_sha256"][PATH].is_string()
        || bundle
            .collections
            .contains_key("current_identity_admissions")
        || bundle.manifest["current_catalogue_version"] == "0.2.0-draft";
    if !required {
        return Ok(());
    }
    if bundle.manifest["input_sha256"][PATH] != pin(RAW)
        || bundle.manifest["input_sha256"][CATALOGUE] != pin(CATALOGUE_RAW)
    {
        return Err("Changed effective current catalogue receipt".into());
    }
    let doc = document();
    if bundle.manifest["current_catalogue_version"] != doc["version"] {
        return Err("Current catalogue edition mismatch".into());
    }
    let catalogue: Value = serde_json::from_str(CATALOGUE_RAW).unwrap();
    for inputs in [&doc["input_sha256"], &catalogue["input_sha256"]] {
        for (path, digest) in inputs.as_object().unwrap() {
            if bundle.manifest["input_sha256"][path] != *digest {
                return Err("Changed current identity admission dependency".into());
            }
        }
    }
    for (collection, mut expected) in records() {
        if collection == "length_assessments" && crate::current_measurements::active(bundle) {
            expected = crate::current_measurements::document()["length_assessment"].clone();
        }
        if collection == "sources" && crate::current_measurements::active(bundle) {
            expected = crate::current_measurements::document()["source_record"].clone();
        }
        if collection == "sources"
            && crate::madagascar_coastal_curve::active(bundle)
            && expected["id"]
                == crate::madagascar_coastal_curve::catalogue()["primary_source_record"]["id"]
        {
            expected =
                crate::madagascar_coastal_curve::catalogue()["primary_source_record"].clone();
        }
        if collection == "length_assessments" {
            expected = crate::nwasc_admission::rank_override(expected, bundle);
        }
        let actual: Vec<_> = bundle
            .collections
            .get(collection)
            .into_iter()
            .flatten()
            .filter(|r| r["id"] == expected["id"])
            .collect();
        if actual != vec![&expected] {
            return Err(format!("Changed admitted current {collection} record"));
        }
    }
    let currents: Vec<_> = bundle
        .collections
        .get("entities")
        .into_iter()
        .flatten()
        .filter(|r| r["type"] == "named_current")
        .collect();
    let mut expected = catalogue["entries"].as_array().unwrap().clone();
    if crate::nwasc_admission::active(bundle) {
        expected.push(crate::nwasc_admission::document()["entity"].clone());
    }
    expected.extend(crate::current_gap_admissions::entities(bundle));
    if currents.len() != expected.len() || expected.iter().any(|r| !currents.contains(&r)) {
        return Err("Incomplete effective current identity inventory".into());
    }
    for row in doc["entries"].as_array().unwrap() {
        let entity = &row["entity_id"];
        if let Some(object) = bundle
            .collections
            .get("objects")
            .into_iter()
            .flatten()
            .find(|r| r["id"] == *entity)
        {
            let object = crate::madagascar_dimensions::legacy_owner_projection(bundle, object)?;
            let count = if crate::current_measurements::active(bundle) {
                1
            } else {
                0
            };
            if object["capabilities"]["reported_length"] != count
                || object["capabilities"]["scoped_width"] != count
                || !object["latest_observation_date"].is_null()
                || (!(crate::madagascar_coastal_curve::active(bundle)
                    && object["id"] == "current:southern-east-madagascar")
                    && object["map_features"] != json!([]))
            {
                return Err(
                    "Identity admission promoted unadmitted measurements or geometry".into(),
                );
            }
        }
    }
    Ok(())
}
pub fn planning_source(current: &str, manifest: &Value) -> Option<(Value, &'static str)> {
    if let Some(source) = crate::current_gap_admissions::planning_source(current, manifest) {
        return Some(source);
    }
    if current == "norwegian-atlantic-slope"
        && crate::nwasc_reference_route::active_manifest(manifest)
    {
        return Some((
            crate::nwasc_reference_route::document()["planning_decision"].clone(),
            crate::nwasc_reference_route::FILE,
        ));
    }
    if current == "norwegian-atlantic-slope" && manifest["nwasc_working_admission_version"] == "1" {
        return Some((
            crate::nwasc_admission::document()["identity_entry"]["route_planning_decision"].clone(),
            crate::nwasc_admission::FILE,
        ));
    }
    if current == "southern-east-madagascar"
        && crate::madagascar_coastal_curve::active_manifest(manifest)
    {
        return Some((
            crate::madagascar_coastal_curve::planning_source(),
            crate::madagascar_coastal_curve::CATALOGUE,
        ));
    }
    if current == "southern-east-madagascar"
        && crate::current_measurements::active_manifest(manifest)
    {
        return Some((
            crate::current_measurements::document()["route_planning_decision"].clone(),
            crate::current_measurements::PATH,
        ));
    }
    document()["entries"]
        .as_array()
        .unwrap()
        .iter()
        .find(|r| r["proposal_id"] == current)
        .map(|r| (r["route_planning_decision"].clone(), PATH))
}
pub fn decisions(bundle: &Bundle) -> Vec<Value> {
    bundle.collections.get("current_identity_admissions").into_iter().flatten().map(|r|{
        if r["proposal_id"] == "norwegian-atlantic-slope" && crate::nwasc_admission::active(bundle) { return crate::nwasc_admission::identity_decision(bundle); }
        if let Some(decision) = crate::current_gap_admissions::decision(bundle, r) { return decision; }
        let measured=r["proposal_id"] == "southern-east-madagascar" && crate::current_measurements::active(bundle);
        json!({"current_id":r["proposal_id"],"name":r["entity"]["label"],
        "measurement_ids":if measured{json!([crate::current_measurements::document()["width_record"]["id"]])}else{json!([])},
        "status":if measured{"scoped_survey_width_admitted"}else{"identity_admitted_width_not_admitted"},
        "whole_current_width_km":null,"annual_width_range_km":null,"admission_id":r["id"]})}).collect()
}
pub fn add_plans(bundle: &Bundle, plans: &mut Value) {
    for row in decisions(bundle) {
        let id = row["current_id"].as_str().unwrap();
        if !plans[id].is_null() {
            if id == "norwegian-atlantic-slope" {
                plans[id]["range_note"] = json!(
                    "Separately scoped source descriptions, not a seasonal sequence. Mean-field widths and an undated mean-flow width do not establish annual extrema or comparable dated boundaries."
                );
                plans[id]["playback_scope"] = json!(
                    "No animation: these source descriptions are not comparable dated states."
                );
            }
            continue;
        }
        plans[id] = json!({"current_id":id,"phases":[],"can_play":false,"eligible_indices":[],
            "range_note":if id=="norwegian-atlantic-slope" {"Separately scoped reported widths; no comparable dated sequence, whole-current width or annual range. Static mean fields cannot show monthly states."}else if id=="east-india-coastal" {"About100km reported at21m for T24 on23-24December2013 south of Sri Lanka. No paired edges, annual width range or comparable seasonal geometry admitted."}else{"Current identity admitted. Whole-current width, annual ranges and seasonal geometry remain unmeasured; separately admitted scoped widths do not establish annual extrema."},
            "playback_scope":"No seasonal animation without comparable recorded states."});
    }
}
#[cfg(test)]
pub(crate) mod tests {
    use super::*;
    pub(crate) fn fixture() -> Bundle {
        let doc = document();
        let cat: Value = serde_json::from_str(CATALOGUE_RAW).unwrap();
        let mut inputs = doc["input_sha256"].clone();
        for (k, v) in cat["input_sha256"].as_object().unwrap() {
            inputs[k] = v.clone();
        }
        inputs[PATH] = json!(pin(RAW));
        inputs[CATALOGUE] = json!(pin(CATALOGUE_RAW));
        let mut collections = std::collections::BTreeMap::new();
        for (name, row) in records() {
            collections
                .entry(name.to_owned())
                .or_insert_with(Vec::new)
                .push(row);
        }
        collections.insert(
            "entities".into(),
            cat["entries"].as_array().unwrap().clone(),
        );
        Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest: json!({"input_sha256":inputs,"current_catalogue_version":"0.2.0-draft"}),
            collections,
        }
    }
    #[test]
    fn identity_admission_preserves_scope_and_inventory() {
        assert!(validate(&fixture()).is_ok());
        for (key, value) in [
            ("rank_eligible", json!(true)),
            ("canonical_measurements_admitted", json!(true)),
            ("annual_width_range_km", json!([100, 140])),
        ] {
            let mut b = fixture();
            b.collections
                .get_mut("current_identity_admissions")
                .unwrap()[0][key] = value;
            assert!(validate(&b).is_err());
        }
        let mut b = fixture();
        b.collections.get_mut("entities").unwrap().pop();
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections
            .get_mut("current_identity_admissions")
            .unwrap()
            .clear();
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections.remove("current_identity_admissions");
        b.manifest["input_sha256"]
            .as_object_mut()
            .unwrap()
            .remove(PATH);
        b.manifest["input_sha256"]
            .as_object_mut()
            .unwrap()
            .remove(CATALOGUE);
        assert!(validate(&b).is_err());
    }
    #[test]
    fn new_current_has_empty_non_playable_seasonal_plan() {
        let b = fixture();
        let mut plans = json!({});
        add_plans(&b, &mut plans);
        assert_eq!(decisions(&b).len(), 1);
        let p = &plans["southern-east-madagascar"];
        assert_eq!(p["phases"], json!([]));
        assert_eq!(p["can_play"], false);
    }
    #[test]
    fn madagascar_admission_cannot_supply_an_unrelated_identity_width() {
        let mut b = fixture();
        b.manifest["current_measurement_admission_version"] = json!("0.2.0-draft-prose-1");
        b.collections
            .get_mut("current_identity_admissions")
            .unwrap()
            .push(json!({
            "id":"current_admission:unrelated", "proposal_id":"unrelated",
            "entity_id":"current:unrelated", "entity":{"label":"Unrelated Current"}}));
        let rows = decisions(&b);
        let unrelated = rows
            .iter()
            .find(|row| row["current_id"] == "unrelated")
            .unwrap();
        assert_eq!(unrelated["measurement_ids"], json!([]));
        assert_eq!(unrelated["status"], "identity_admitted_width_not_admitted");
        let madagascar = rows
            .iter()
            .find(|row| row["current_id"] == "southern-east-madagascar")
            .unwrap();
        assert_eq!(madagascar["measurement_ids"].as_array().unwrap().len(), 1);
    }
}
