//! Editorial route decisions stay bound to their source worklist and owner.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;

const EICC_SOURCE: &str = "research/eicc-regional-reference-admission-candidate-v1.json";
const EICC_SOURCE_SHA: &str = "6c02b4c09e214b5080ce5017849ad9ade9f034c579da7d5c3d1b5a056ad5db9d";
const EICC_QUERY: &str = "research/eicc-reference-query-contract-v1.json";
const EICC_QUERY_SHA: &str = "d570494537d9d9d627a17a2af47d8cc3289429b4055ac30a35a8cd3a0772d346";
const EICC: &str = "current:east-india-coastal";

pub(crate) fn eicc_reference_contract(
    collections: &BTreeMap<String, Vec<Value>>, manifest: &Value,
) -> Result<Option<Value>, String> {
    let revision = &manifest["eicc_reference_spectral_delivery_v1"]["planning_revision"];
    if revision.is_null() { return Ok(None); }
    let refuse = || "Invalid source-bound EICC reference revision".to_owned();
    let raw = revision["source_json"].as_str().ok_or_else(refuse)?;
    let query_raw = revision["query_contract_json"].as_str().ok_or_else(refuse)?;
    if revision["schema"] != "osw.eicc-source-reference-planning-revision.v2"
        || revision["owner_id"] != EICC || revision["source_file"] != EICC_SOURCE
        || revision["source_sha256"] != EICC_SOURCE_SHA
        || format!("{:x}", Sha256::digest(raw.as_bytes())) != EICC_SOURCE_SHA
        || manifest["input_sha256"][EICC_SOURCE] != EICC_SOURCE_SHA
        || revision["query_contract_file"] != EICC_QUERY
        || revision["query_contract_sha256"] != EICC_QUERY_SHA
        || format!("{:x}", Sha256::digest(query_raw.as_bytes())) != EICC_QUERY_SHA
        || manifest["input_sha256"][EICC_QUERY] != EICC_QUERY_SHA
    { return Err(refuse()); }
    let contract: Value = serde_json::from_str(query_raw).map_err(|_| refuse())?;
    let expected = crate::current_gap_admissions::original_planning_decision("east-india-coastal", manifest)?;
    let prior: Value = serde_json::from_str(revision["prior_decision_json"].as_str().ok_or_else(refuse)?)
        .map_err(|_| refuse())?;
    let records: Vec<_> = collections.get("route_decisions").into_iter().flatten()
        .filter(|row| row["entity_id"] == EICC).collect();
    if records.len() != 1 || prior != expected || records[0]["prior_route_decision"] != expected {
        return Err(refuse());
    }
    let record = records[0];
    let changed = ["construction_status", "candidate_count", "route_ids", "next_action",
        "source_catalog_file", "source_catalog_sha256", "source_url", "source_decision"];
    let prior_fields = expected.as_object().ok_or_else(refuse)?;
    if prior_fields.iter().any(|(key, value)| !changed.contains(&key.as_str()) && record.get(key) != Some(value))
        || record.as_object().ok_or_else(refuse)?.keys().any(|key| !prior_fields.contains_key(key) && key != "prior_route_decision")
    { return Err(refuse()); }
    let changed_source = ["candidate_ids", "reference_path_decision", "next_action", "name_source_url"];
    let old_source = expected["source_decision"].as_object().ok_or_else(refuse)?;
    let new_source = record["source_decision"].as_object().ok_or_else(refuse)?;
    if old_source.iter().any(|(key, value)| !changed_source.contains(&key.as_str()) && new_source.get(key) != Some(value))
        || new_source.keys().any(|key| !old_source.contains_key(key))
    { return Err(refuse()); }
    let routes = contract["collections"]["reference_routes"].as_array().ok_or_else(refuse)?;
    let ids: Vec<_> = routes.iter().map(|row| row["id"].clone()).collect();
    if routes.len() != 2 || record["route_ids"] != json!(ids)
        || record["candidate_count"] != 2 || record["source_decision"]["candidate_ids"] != record["route_ids"]
        || record["source_catalog_file"] != EICC_SOURCE || record["source_catalog_sha256"] != EICC_SOURCE_SHA
        || record["construction_status"] != "regional_source_anchor_connections_constructed"
        || record["source_decision"]["reference_path_decision"] != record["construction_status"]
        || record["source_url"] != routes[0]["source_url"]
        || record["source_decision"]["name_source_url"] != record["source_url"]
        || record["next_action"] != record["source_decision"]["next_action"]
    { return Err(refuse()); }
    for (name, field, capability) in [
        ("reference_routes", "route_ids", "reference_route"),
        ("current_sampling_reference_points", "sampling_reference_point_ids", "sampling_reference_points"),
        ("current_spectral_cross_shore_scales", "spectral_cross_shore_scale_ids", "spectral_cross_shore_scales"),
    ] {
        let rows = contract["collections"][name].as_array().ok_or_else(refuse)?;
        let actual: Vec<_> = collections.get(name).into_iter().flatten()
            .filter(|row| if name == "reference_routes" { row["current_id"] == "east-india-coastal" } else { row["entity_id"] == EICC }).collect();
        if actual.len() != rows.len() || rows.iter().any(|row| actual.iter().filter(|r| **r == row).count() != 1) {
            return Err(refuse());
        }
        let owners: Vec<_> = collections["objects"].iter().filter(|owner| owner["id"] == EICC).collect();
        if owners.len() != 1 || owners[0][field] != json!(rows.iter().map(|row| row["id"].clone()).collect::<Vec<_>>())
            || owners[0]["capabilities"][capability].as_u64() != Some(rows.len() as u64)
            || owners[0]["capabilities"]["geometry"] != 0
            || owners[0]["map_features"] != contract["owner_map_features"]
        { return Err(refuse()); }
    }
    for row in contract["collections"]["sources"].as_array().ok_or_else(refuse)? {
        if collections.get("sources").into_iter().flatten().filter(|r| r["id"] == row["id"]).collect::<Vec<_>>() != vec![row] {
            return Err(refuse());
        }
    }
    let reports = revision["atlas_reports"].as_object().ok_or_else(refuse)?;
    if reports.len() != 2 { return Err(refuse()); }
    for row in routes {
        let report = reports.get(row["id"].as_str().ok_or_else(refuse)?).ok_or_else(refuse)?;
        let feature = contract["owner_map_features"].as_array().ok_or_else(refuse)?.iter()
            .find(|feature| feature["candidate_id"] == row["id"]).ok_or_else(refuse)?;
        if row.as_object().ok_or_else(refuse)?.iter().any(|(key, value)| key != "coordinates_lon_lat" && report.get(key) != Some(value))
            || report["schema"] != "osw.current-reference-path-input.v1"
            || report["rendering_role"] != "derived_inline_source_reference_card_not_additional_observation"
            || report["coordinates_lon_lat"] != feature["geometry"]["coordinates"]
            || report["reported_approximate_reference_path_km"] != row["approximate_reference_path_km"]
            || report["scenario_range_km"] != row["public_editorial_probe_span_km"]
            || report["source_candidate_file"] != EICC_SOURCE || report["source_candidate_pointer"] != row["source_pointer"]
            || report["nasa_movie_context"] != json!([])
            || !report["recommended_nasa_tile_id"].is_null()
            || !report["remaining_gates"].as_array().is_some_and(|gates| !gates.is_empty())
        { return Err(refuse()); }
    }
    Ok(Some(contract))
}

pub(crate) fn eicc_reference_routes(
    collections: &BTreeMap<String, Vec<Value>>, manifest: &Value,
) -> Result<Vec<Value>, String> {
    Ok(eicc_reference_contract(collections, manifest)?.map(|contract|
        contract["collections"]["reference_routes"].as_array().unwrap().clone()).unwrap_or_default())
}

fn revised_eicc_source(record: &Value, manifest: &Value, collections: &BTreeMap<String, Vec<Value>>)
    -> Result<Option<&'static str>, String>
{
    if record["entity_id"] != EICC { return Ok(None); }
    Ok(eicc_reference_contract(collections, manifest)?.map(|_| EICC_SOURCE))
}

pub(crate) fn eicc_catalogue_projection(bundle: &crate::Bundle, mut catalog: Value) -> Result<Value, String> {
    let Some(contract) = eicc_reference_contract(&bundle.collections, &bundle.manifest)? else { return Ok(catalog); };
    let fail = || "Invalid EICC atlas catalog projection".to_owned();
    let routes = contract["collections"]["reference_routes"].as_array().ok_or_else(fail)?;
    let candidates = catalog["candidates"].as_array_mut().ok_or_else(fail)?;
    if candidates.iter().any(|row| row["current_id"] == "east-india-coastal") { return Err(fail()); }
    for row in routes {
        let report = &bundle.manifest["eicc_reference_spectral_delivery_v1"]["planning_revision"]["atlas_reports"][row["id"].as_str().unwrap()];
        let mut entry = row.clone();
        entry["candidate_file"] = json!(EICC_SOURCE);
        entry["candidate_sha256"] = row["source_file_sha256"].clone();
        entry["route_extent_kind"] = json!("regional source-anchor reference connection");
        entry["scenario_range_km"] = row["public_editorial_probe_span_km"].clone();
        entry["nominal_atlas_state_crossings"] = json!([]);
        entry["state_intersection_status"] = json!("unassessed_no_physical_join_admitted");
        entry["remaining_gates"] = report["remaining_gates"].clone();
        entry["report_inline"] = report.clone();
        candidates.push(entry);
    }
    let decision = bundle.collections["route_decisions"].iter().find(|row| row["entity_id"] == EICC).ok_or_else(fail)?;
    let plans = catalog["remaining_current_decisions"].as_array_mut().ok_or_else(fail)?;
    let matches: Vec<_> = plans.iter().enumerate().filter(|(_, row)| row["current_id"] == "east-india-coastal").map(|(i, _)| i).collect();
    if matches.len() != 1 || plans[matches[0]]["candidate_ids"] != json!([]) { return Err(fail()); }
    plans[matches[0]] = decision["source_decision"].clone();
    for (key, increment) in [("route_candidates", 2), ("currents_with_route_candidates", 1),
        ("currents_without_route_candidates", -1), ("currents_without_any_reference_card", -1)] {
        let old = catalog["counts"][key].as_i64().ok_or_else(fail)?;
        let value = old.checked_add(increment).filter(|n| *n >= 0).ok_or_else(fail)?;
        catalog["counts"][key] = json!(value);
    }
    let strategies = catalog["planning_taxonomy"]["strategies"].as_array_mut().ok_or_else(fail)?;
    let indices: Vec<_> = strategies.iter().enumerate().filter(|(_, row)| row["id"] == decision["strategy_id"]).map(|(i, _)| i).collect();
    if indices.len() != 1 { return Err(fail()); }
    let strategy = &mut strategies[indices[0]];
    strategy["unbuilt_count"] = json!(strategy["unbuilt_count"].as_u64().and_then(|n| n.checked_sub(1)).ok_or_else(fail)?);
    Ok(catalog)
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
        let source_path = if let Some(path) = crate::current_reference_profiles::planning_source(record, collections, manifest)? {
            path
        } else if let Some(path) = crate::atlantic_nsec_reference::planning_source(record, collections, manifest)? {
            path
        } else if let Some(path) = crate::wicc_winter_reference::planning_source(record, collections, manifest)? {
            path
        } else if let Some(path) = crate::south_java_reference::planning_source(record, collections, manifest)? {
            path
        } else if let Some(path) = crate::pacific_secc_reference::planning_source(record, collections, manifest)? {
            path
        } else if let Some(path) = revised_eicc_source(record, manifest, collections)? {
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
pub(crate) mod tests {
    use super::*;

    pub(crate) fn revised_fixture() -> crate::Bundle {
        let mut bundle = crate::current_gap_admissions::tests::fixture();
        let query_raw = std::fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"),
            "/../../research/eicc-reference-query-contract-v1.json")).unwrap();
        let source_raw = std::fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"),
            "/../../research/eicc-regional-reference-admission-candidate-v1.json")).unwrap();
        let contract: Value = serde_json::from_str(&query_raw).unwrap();
        let prior = crate::current_gap_admissions::original_planning_decision("east-india-coastal", &bundle.manifest).unwrap();
        let mut decision = prior.clone();
        decision["prior_route_decision"] = prior.clone();
        decision["route_ids"] = json!(contract["collections"]["reference_routes"].as_array().unwrap().iter()
            .map(|row| row["id"].clone()).collect::<Vec<_>>());
        decision["candidate_count"] = json!(2);
        decision["construction_status"] = json!("regional_source_anchor_connections_constructed");
        decision["source_catalog_file"] = json!(EICC_SOURCE);
        decision["source_catalog_sha256"] = json!(EICC_SOURCE_SHA);
        decision["source_url"] = contract["collections"]["reference_routes"][0]["source_url"].clone();
        decision["next_action"] = json!("Recover continuous source axes and defensible endpoints.");
        for (target, origin) in [("candidate_ids", "route_ids"), ("reference_path_decision", "construction_status"),
            ("name_source_url", "source_url"), ("next_action", "next_action")] {
            decision["source_decision"][target] = decision[origin].clone();
        }
        *bundle.collections.get_mut("route_decisions").unwrap().iter_mut().find(|row| row["entity_id"] == EICC).unwrap() = decision;
        for name in ["reference_routes", "current_sampling_reference_points", "current_spectral_cross_shore_scales", "sources"] {
            bundle.collections.entry(name.into()).or_default().extend(contract["collections"][name].as_array().unwrap().clone());
        }
        let owner = bundle.collections.get_mut("objects").unwrap().iter_mut().find(|row| row["id"] == EICC).unwrap();
        owner["map_features"] = contract["owner_map_features"].clone();
        for (name, field, capability) in [("reference_routes", "route_ids", "reference_route"),
            ("current_sampling_reference_points", "sampling_reference_point_ids", "sampling_reference_points"),
            ("current_spectral_cross_shore_scales", "spectral_cross_shore_scale_ids", "spectral_cross_shore_scales")] {
            let rows = contract["collections"][name].as_array().unwrap();
            owner[field] = json!(rows.iter().map(|row| row["id"].clone()).collect::<Vec<_>>());
            owner["capabilities"][capability] = json!(rows.len());
        }
        for row in contract["collections"]["sources"].as_array().unwrap() {
            owner["source_ids"].as_array_mut().unwrap().push(row["id"].clone());
        }
        owner["linked_source_count"] = json!(owner["source_ids"].as_array().unwrap().len());
        let mut reports = json!({});
        for row in contract["collections"]["reference_routes"].as_array().unwrap() {
            let mut report = row.clone();
            let feature = contract["owner_map_features"].as_array().unwrap().iter().find(|feature| feature["candidate_id"] == row["id"]).unwrap();
            report["schema"] = json!("osw.current-reference-path-input.v1");
            report["rendering_role"] = json!("derived_inline_source_reference_card_not_additional_observation");
            report["coordinates_lon_lat"] = feature["geometry"]["coordinates"].clone();
            report["source_candidate_file"] = json!(EICC_SOURCE);
            report["source_candidate_pointer"] = row["source_pointer"].clone();
            report["reported_approximate_reference_path_km"] = row["approximate_reference_path_km"].clone();
            report["scenario_range_km"] = row["public_editorial_probe_span_km"].clone();
            report["nasa_movie_context"] = json!([]);
            report["remaining_gates"] = json!(["Source axis and physical scope remain unresolved"]);
            reports[row["id"].as_str().unwrap()] = report;
        }
        bundle.manifest["input_sha256"][EICC_SOURCE] = json!(EICC_SOURCE_SHA);
        bundle.manifest["input_sha256"][EICC_QUERY] = json!(EICC_QUERY_SHA);
        bundle.manifest["eicc_reference_spectral_delivery_v1"] = json!({"planning_revision":{
            "schema":"osw.eicc-source-reference-planning-revision.v2", "owner_id":EICC,
            "source_file":EICC_SOURCE,"source_sha256":EICC_SOURCE_SHA,"source_json":source_raw,
            "prior_decision_json":serde_json::to_string(&prior).unwrap(),
            "query_contract_file":EICC_QUERY,"query_contract_sha256":EICC_QUERY_SHA,
            "query_contract_json":query_raw,"atlas_reports":reports}});
        bundle
    }

    #[test]
    fn actual_admitted_plan_accepts_two_editorial_references_and_source_records() {
        let bundle = revised_fixture();
        validate(&bundle.collections, &bundle.manifest).unwrap();
        crate::current_gap_admissions::validate(&bundle).unwrap();
        assert_eq!(eicc_reference_routes(&bundle.collections, &bundle.manifest).unwrap().len(), 2);
    }

    #[test]
    fn original_admission_without_revision_keeps_original_rules() {
        let bundle = crate::current_gap_admissions::tests::fixture();
        validate(&bundle.collections, &bundle.manifest).unwrap();
        crate::current_gap_admissions::validate(&bundle).unwrap();
        assert!(eicc_reference_routes(&bundle.collections, &bundle.manifest).unwrap().is_empty());
    }

    #[test]
    fn revised_prior_source_and_query_receipts_are_immutable() {
        for field in ["source_json", "prior_decision_json", "query_contract_json"] {
            let mut bundle = revised_fixture();
            bundle.manifest["eicc_reference_spectral_delivery_v1"]["planning_revision"][field] = json!("{}");
            assert!(validate(&bundle.collections, &bundle.manifest).is_err());
            assert!(crate::current_gap_admissions::validate(&bundle).is_err());
        }
    }

    #[test]
    fn diagnostics_and_reference_geometry_cannot_be_promoted_or_replaced() {
        for (collection, field, value) in [("reference_routes", "rank_eligible", json!(true)),
            ("reference_routes", "annual_length_range_km", json!([590,630])),
            ("current_sampling_reference_points", "current_thickness_m", json!(63)),
            ("current_spectral_cross_shore_scales", "paired_current_width_km", json!(23))] {
            let mut bundle = revised_fixture();
            bundle.collections.get_mut(collection).unwrap()[0][field] = value;
            assert!(validate(&bundle.collections, &bundle.manifest).is_err());
        }
        let mut bundle = revised_fixture();
        let owner = bundle.collections.get_mut("objects").unwrap().iter_mut().find(|row| row["id"] == EICC).unwrap();
        owner["map_features"][0]["role"] = json!("observed_axis");
        assert!(crate::current_gap_admissions::validate(&bundle).is_err());
    }

    #[test]
    fn physical_and_other_owner_admission_guards_remain_active() {
        for current in [EICC, "current:west-india-coastal"] {
            let mut bundle = revised_fixture();
            let owner = bundle.collections.get_mut("objects").unwrap().iter_mut().find(|row| row["id"] == current).unwrap();
            owner["published_length_km"] = json!(900);
            assert!(crate::current_gap_admissions::validate(&bundle).is_err());
        }
    }

    #[test]
    fn catalog_adds_one_owner_two_cards_without_changing_ordering() {
        let bundle = revised_fixture();
        let plan = crate::current_gap_admissions::original_planning_decision("east-india-coastal", &bundle.manifest).unwrap();
        let catalog = json!({"candidates":[{"id":"old-route","current_id":"other"}],
            "reference_route_length_order":["old-route"],"remaining_current_decisions":[plan["source_decision"]],
            "counts":{"accepted_current_names":4,"route_candidates":1,"currents_with_route_candidates":1,
                "currents_without_route_candidates":3,"currents_without_any_reference_card":3},
            "planning_taxonomy":{"strategies":[{"id":plan["strategy_id"],"unbuilt_count":1,"current_count":1}]}});
        let result = eicc_catalogue_projection(&bundle, catalog.clone()).unwrap();
        assert_eq!(result["candidates"].as_array().unwrap().len(), 3);
        assert_eq!(result["counts"]["route_candidates"], 3);
        assert_eq!(result["counts"]["currents_with_route_candidates"], 2);
        assert_eq!(result["counts"]["currents_without_any_reference_card"], 2);
        assert_eq!(result["reference_route_length_order"], catalog["reference_route_length_order"]);
        assert!(result["candidates"][1]["report_inline"].is_object());
        assert!(eicc_catalogue_projection(&bundle, result).is_err());
    }
}
