//! Exact source-bound South Java editorial reach; no physical dimensions admitted.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};

pub(crate) const FILE: &str = "research/south-java-reference-runtime-contract-v1.json";
const RAW: &str = include_str!("../../../research/south-java-reference-runtime-contract-v1.json");
const KEY: &str = "south_java_reference_delivery_v1";
const OWNER: &str = "current:south-java";
const CURRENT: &str = "south-java";
const ROUTE: &str = "south-java-java-bali-reference-reach-v1";
const METHOD: &str = "source:south-java-java-bali-reference-method-v1";
const PARENT: &str = "f0e046651b75c84da488c4e81204e410b18f37256e102c26a0ab2f70b5f69184";

fn pin(raw: &str) -> String { format!("{:x}", Sha256::digest(raw.as_bytes())) }
fn contract() -> Result<Value, String> {
    serde_json::from_str(RAW).map_err(|_| "Invalid South Java runtime source".into())
}
fn doi(value: &Value) -> String {
    let text = value.as_str().unwrap_or("").trim().to_lowercase();
    for prefix in ["https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "http://dx.doi.org/", "doi:"] {
        if let Some(tail) = text.strip_prefix(prefix) { return tail.trim().trim_end_matches('/').into(); }
    }
    text.trim_end_matches('/').into()
}
fn source_url(value: &Value) -> String {
    let text = value.as_str().unwrap_or("").trim().split(['?', '#']).next().unwrap_or("");
    let text = text.strip_prefix("https://").or_else(|| text.strip_prefix("http://")).unwrap_or(text);
    let (host, path) = text.split_once('/').unwrap_or((text, ""));
    format!("{}/{}", host.to_lowercase(), path.trim_end_matches('/'))
}

pub(crate) fn routes(collections: &BTreeMap<String, Vec<Value>>, manifest: &Value)
    -> Result<Vec<Value>, String>
{
    let fail = || "Invalid source-bound South Java reference reach".to_owned();
    let actual: Vec<_> = collections.get("reference_routes").into_iter().flatten()
        .filter(|r| r["current_id"] == CURRENT || r["id"] == ROUTE).collect();
    let sources = collections.get("sources");
    let receipt = &manifest[KEY];
    if receipt.is_null() {
        let feature_present = collections.get("objects").into_iter().flatten()
            .filter(|r| r["id"] == OWNER).any(|r| r["map_features"].as_array()
                .is_some_and(|rows| rows.iter().any(|f| f["candidate_id"] == ROUTE)));
        if !actual.is_empty() || !manifest["input_sha256"][FILE].is_null() || feature_present
            || sources.is_some_and(|rows| rows.iter().any(|r| r["id"] == METHOD))
        { return Err(fail()); }
        return Ok(vec![]);
    }
    let doc = contract()?;
    let query = &doc["query_contract"];
    let sources = sources.ok_or_else(fail)?;
    if receipt["schema"] != "osw.south-java-reference-runtime-receipt.v1"
        || receipt["parent_logical_sha256"] != PARENT || doc["parent_logical_sha256"] != PARENT
        || receipt["contract_file"] != FILE || receipt["contract_sha256"] != pin(RAW)
        || manifest["input_sha256"][FILE] != pin(RAW)
        || sources.len() != 211 + crate::wicc_winter_reference::additional_source_count(collections, manifest)?
        || receipt["new_physical_dimensions"] != 0 || receipt["installed"] != false
        || receipt["prior_owner"] != query["prior_owner"] || receipt["prior_entity"] != query["prior_entity"]
        || receipt["prior_decision"] != query["prior_decision"]
        || receipt["publication_sources"] != query["existing_publications"]
    { return Err(fail()); }
    for (path, sha) in doc["input_sha256"].as_object().ok_or_else(fail)? {
        if manifest["input_sha256"][path] != *sha { return Err(fail()); }
    }
    let mut source_ids = BTreeSet::new();
    for source in sources {
        let id = source["id"].as_str().ok_or_else(fail)?;
        if id.is_empty() || !source_ids.insert(id) { return Err(fail()); }
    }
    for expected in query["existing_publications"].as_object().ok_or_else(fail)?.values() {
        let matches: Vec<_> = sources.iter().filter(|r| doi(&r["doi"]) == doi(&expected["doi"])
            || doi(&r["url"]) == doi(&expected["doi"])
            || source_url(&r["url"]) == source_url(&expected["url"])).collect();
        if matches != vec![expected] { return Err(fail()); }
    }
    for expected in query["prior_owner_sources"].as_array().ok_or_else(fail)? {
        if sources.iter().filter(|r| r["id"] == expected["id"]).collect::<Vec<_>>() != vec![expected] {
            return Err(fail());
        }
    }
    let method = &query["method_source"];
    if method["id"] != METHOD
        || sources.iter().filter(|r| r["id"] == METHOD).collect::<Vec<_>>() != vec![method]
    { return Err(fail()); }
    let expected_route = query["route"].clone();
    if expected_route["id"] != ROUTE || expected_route["entity_id"] != OWNER
        || expected_route["rank_eligible"] != false || expected_route["independent_observation_count"] != 0
        || expected_route["physical_current_axis_admitted"] != false
        || expected_route["physical_state_join_eligible"] != false
        || actual != vec![&expected_route]
    { return Err(fail()); }
    for key in ["whole_current_length_km", "physical_width_km", "current_thickness_m",
                "annual_length_range_km", "annual_width_range_km", "uncertainty_km", "sample_date"] {
        if !expected_route[key].is_null() { return Err(fail()); }
    }
    let entities: Vec<_> = collections.get("entities").into_iter().flatten().filter(|r| r["id"] == OWNER).collect();
    if entities != vec![&query["prior_entity"]] { return Err(fail()); }
    let prior = &query["prior_decision"];
    if prior["source_decision"] != doc["original_planning_source"]
        || prior["source_catalog_file"] != doc["original_planning_file"]
        || prior["source_catalog_sha256"] != doc["original_planning_sha256"]
        || prior["route_ids"] != json!([]) || prior["candidate_count"] != 0
    { return Err(fail()); }
    let mut decision = prior.clone();
    decision["prior_route_decision"] = prior.clone();
    decision["route_ids"] = json!([ROUTE]);
    decision["candidate_count"] = json!(1);
    decision["construction_status"] = json!("regional_editorial_reference_constructed");
    decision["source_catalog_file"] = expected_route["source_file"].clone();
    decision["source_catalog_sha256"] = expected_route["source_file_sha256"].clone();
    decision["source_url"] = expected_route["source_url"].clone();
    decision["source_id"] = expected_route["source_id"].clone();
    decision["source_ids"] = expected_route["source_ids"].clone();
    decision["next_action"] = json!("Recover compatible dated physical axes and endpoints; this partial drawing does not establish whole-current or seasonal dimensions.");
    for (target, origin) in [("candidate_ids", "route_ids"), ("name_source_url", "source_url"),
        ("reference_path_decision", "construction_status"), ("next_action", "next_action")] {
        decision["source_decision"][target] = decision[origin].clone();
    }
    let decisions: Vec<_> = collections.get("route_decisions").into_iter().flatten()
        .filter(|r| r["entity_id"] == OWNER).collect();
    if decisions != vec![&decision] { return Err(fail()); }
    let mut owner = query["prior_owner"].clone();
    if owner["route_ids"] != json!([]) || owner["capabilities"]["reference_route"] != 0 { return Err(fail()); }
    owner["route_ids"] = json!([ROUTE]);
    owner["capabilities"]["reference_route"] = json!(1);
    owner["map_features"].as_array_mut().ok_or_else(fail)?.push(query["owner_map_feature"].clone());
    let mut ids = BTreeSet::new();
    for row in [&owner["source_ids"], &expected_route["source_ids"]] {
        for id in row.as_array().ok_or_else(fail)? { ids.insert(id.as_str().ok_or_else(fail)?.to_owned()); }
    }
    owner["linked_source_count"] = json!(ids.len());
    owner["source_ids"] = json!(ids.into_iter().collect::<Vec<_>>());
    owner["route_url"] = query["atlas_url_after_installation"].clone();
    owner["evidence_links"].as_array_mut().ok_or_else(fail)?.push(
        json!({"label":"View the South Java reference reach","url":"south-java-reference-support.html"}));
    let section_raw = receipt["section_fingerprint_json"].as_str().ok_or_else(fail)?;
    let section: Value = serde_json::from_str(section_raw).map_err(|_| fail())?;
    if section != expected_route { return Err(fail()); }
    owner["section_fingerprints"]["south_java_java_bali_reference"] = json!(pin(section_raw));
    owner.as_object_mut().ok_or_else(fail)?.remove("fingerprint");
    let owner_raw = receipt["owner_fingerprint_json"].as_str().ok_or_else(fail)?;
    let fingerprint_owner: Value = serde_json::from_str(owner_raw).map_err(|_| fail())?;
    if fingerprint_owner != owner { return Err(fail()); }
    owner["fingerprint"] = json!(pin(owner_raw));
    let owners: Vec<_> = collections.get("objects").into_iter().flatten().filter(|r| r["id"] == OWNER).collect();
    if owners != vec![&owner] { return Err(fail()); }
    Ok(vec![expected_route])
}

pub(crate) fn additional_source_count(collections: &BTreeMap<String, Vec<Value>>, manifest: &Value)
    -> Result<usize, String>
{
    Ok(if routes(collections, manifest)?.is_empty() { 0 } else { 1 })
}

pub(crate) fn planning_source(record: &Value, collections: &BTreeMap<String, Vec<Value>>, manifest: &Value)
    -> Result<Option<&'static str>, String>
{
    if record["entity_id"] != OWNER || routes(collections, manifest)?.is_empty() { return Ok(None); }
    Ok(Some("research/south-java-java-bali-reference-path-v2-candidate.json"))
}

pub(crate) fn catalogue_projection(bundle: &crate::Bundle, mut catalog: Value) -> Result<Value, String> {
    let rows = routes(&bundle.collections, &bundle.manifest)?;
    if rows.is_empty() { return Ok(catalog); }
    let fail = || "Invalid South Java atlas projection".to_owned();
    let doc = contract()?;
    let report = &doc["atlas_report"];
    let candidates = catalog["candidates"].as_array_mut().ok_or_else(fail)?;
    if candidates.iter().any(|r| r["current_id"] == CURRENT) { return Err(fail()); }
    let mut entry = rows[0].clone();
    entry["candidate_file"] = entry["source_file"].clone();
    entry["candidate_sha256"] = entry["source_file_sha256"].clone();
    entry["route_extent_kind"] = json!("Java-Bali editorial study reach");
    entry["scenario_range_km"] = entry["public_editorial_probe_span_km"].clone();
    entry["nominal_atlas_state_crossings"] = json!([]);
    entry["state_intersection_status"] = json!("unassessed_no_physical_join_admitted");
    entry["remaining_gates"] = report["remaining_gates"].clone();
    entry["report_inline"] = report.clone();
    candidates.push(entry);
    let decision = bundle.collections.get("route_decisions").into_iter().flatten()
        .find(|r| r["entity_id"] == OWNER).ok_or_else(fail)?;
    let plans = catalog["remaining_current_decisions"].as_array_mut().ok_or_else(fail)?;
    let indices: Vec<_> = plans.iter().enumerate().filter(|(_, r)| r["current_id"] == CURRENT).map(|(i, _)| i).collect();
    if indices.len() != 1 || plans[indices[0]] != doc["original_planning_source"] { return Err(fail()); }
    plans[indices[0]] = decision["source_decision"].clone();
    for (key, delta) in [("route_candidates", 1), ("currents_with_route_candidates", 1),
        ("currents_without_route_candidates", -1), ("currents_without_any_reference_card", -1)] {
        let value = catalog["counts"][key].as_i64().ok_or_else(fail)?;
        catalog["counts"][key] = json!(value.checked_add(delta).filter(|v| *v >= 0).ok_or_else(fail)?);
    }
    let strategies = catalog["planning_taxonomy"]["strategies"].as_array_mut().ok_or_else(fail)?;
    let indices: Vec<_> = strategies.iter().enumerate().filter(|(_, r)| r["id"] == decision["strategy_id"]).map(|(i, _)| i).collect();
    if indices.len() != 1 { return Err(fail()); }
    let strategy = &mut strategies[indices[0]];
    strategy["unbuilt_count"] = json!(strategy["unbuilt_count"].as_u64().and_then(|v| v.checked_sub(1)).ok_or_else(fail)?);
    Ok(catalog)
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> crate::Bundle {
        serde_json::from_str(include_str!("../../../research/south-java-reference-runtime-fixture-v1.json")).unwrap()
    }
    #[test]
    fn source_bound_reference_and_generic_planning_accept() {
        let b = fixture();
        let rows = routes(&b.collections, &b.manifest).unwrap();
        assert_eq!(rows.len(), 1);
        assert_eq!(rows[0]["approximate_reference_path_km"], 1100);
        assert_eq!(rows[0]["physical_width_km"], Value::Null);
        assert_eq!(additional_source_count(&b.collections, &b.manifest).unwrap(), 1);
        crate::planning::validate(&b.collections, &b.manifest).unwrap();
    }
    #[test]
    fn altered_source_owner_scope_and_receipts_are_refused() {
        for change in ["route", "owner", "publication", "registry", "pin", "fingerprint", "prior"] {
            let mut b = fixture();
            match change {
                "route" => b.collections.get_mut("reference_routes").unwrap().last_mut().unwrap()["annual_width_range_km"] = json!([10,20]),
                "owner" => b.collections.get_mut("objects").unwrap()[0]["capabilities"]["geometry"] = json!(1),
                "publication" => {
                    let paper = b.collections.get_mut("sources").unwrap().iter_mut()
                        .find(|r| r["id"] == "source:iskandar-south-java-ofes-2006").unwrap();
                    paper["title"] = json!("changed publication");
                },
                "registry" => { b.collections.get_mut("sources").unwrap().pop(); },
                "pin" => b.manifest["input_sha256"][FILE] = json!("changed"),
                "fingerprint" => b.manifest[KEY]["owner_fingerprint_json"] = json!("{}"),
                "prior" => b.manifest[KEY]["prior_entity"]["label"] = json!("changed identity"),
                _ => unreachable!(),
            }
            assert!(routes(&b.collections, &b.manifest).is_err(), "{change}");
        }
    }
    #[test]
    fn catalogue_matches_complete_python_fixture_projection() {
        let b = fixture();
        let result = catalogue_projection(&b, b.manifest["fixture_catalogue"].clone()).unwrap();
        assert_eq!(result, b.manifest["fixture_expected_catalogue"]);
        assert_eq!(result["counts"]["route_candidates"], 82);
        assert_eq!(result["counts"]["currents_with_route_candidates"], 75);
        assert_eq!(result["candidates"].as_array().unwrap().last().unwrap()["nominal_atlas_state_crossings"], json!([]));
        assert!(catalogue_projection(&b, result).is_err());
    }
    #[test]
    fn older_bundle_without_extension_is_accepted_and_orphan_pin_is_refused() {
        let mut b = fixture();
        let doc = contract().unwrap();
        b.manifest.as_object_mut().unwrap().remove(KEY);
        b.manifest["input_sha256"].as_object_mut().unwrap().remove(FILE);
        b.collections.get_mut("reference_routes").unwrap().retain(|r| r["current_id"] != CURRENT && r["id"] != ROUTE);
        b.collections.get_mut("sources").unwrap().retain(|r| r["id"] != METHOD);
        b.collections.get_mut("objects").unwrap()[0] = doc["query_contract"]["prior_owner"].clone();
        b.collections.get_mut("route_decisions").unwrap()[0] = doc["query_contract"]["prior_decision"].clone();
        assert!(routes(&b.collections, &b.manifest).unwrap().is_empty());
        assert_eq!(additional_source_count(&b.collections, &b.manifest).unwrap(), 0);
        b.manifest["input_sha256"][FILE] = json!(pin(RAW));
        assert!(routes(&b.collections, &b.manifest).is_err());
    }
    #[test]
    fn source_count_increment_requires_the_complete_valid_extension() {
        let mut b = fixture();
        b.manifest[KEY] = json!({"installed":false});
        assert!(additional_source_count(&b.collections, &b.manifest).is_err());
        b.manifest.as_object_mut().unwrap().remove(KEY);
        assert!(additional_source_count(&b.collections, &b.manifest).is_err());
    }
}
