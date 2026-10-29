//! One source-bound editorial reach; it admits no physical or seasonal dimensions.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};

pub(crate) const FILE: &str = "research/pacific-secc-reference-runtime-contract-v1.json";
const RAW: &str = include_str!("../../../research/pacific-secc-reference-runtime-contract-v1.json");
const PUBLICATION_FILE: &str = "research/pacific-secc-reference-publication-admission-v1.json";
const PUBLICATION_RAW: &str = include_str!("../../../research/pacific-secc-reference-publication-admission-v1.json");
const KEY: &str = "pacific_secc_reference_delivery_v1";
const OWNER: &str = "current:pacific-south-equatorial-countercurrent";
const CURRENT: &str = "pacific-south-equatorial-countercurrent";
const PARENT: &str = "93c7c184e547ad0c2801ff2183cc5f88f2e11f6150b69b7583fc2f0db05ab696";
const URL: &str = "https://www.soest.hawaii.edu/oceanography/bo/CQ04.pdf";
const DOI: &str = "10.1029/2003jc002243";

fn pin(raw: &str) -> String { format!("{:x}", Sha256::digest(raw.as_bytes())) }
fn contract() -> Result<Value, String> {
    serde_json::from_str(RAW).map_err(|_| "Invalid Pacific reference source contract".into())
}
fn doi(value: &Value) -> String {
    let text = value.as_str().unwrap_or("").trim().to_lowercase();
    for prefix in ["https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "doi:"] {
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
fn publication(row: &Value) -> bool {
    doi(&row["doi"]) == DOI || doi(&row["url"]) == DOI
        || source_url(&row["url"]) == source_url(&json!(URL))
}

pub(crate) fn routes(collections: &BTreeMap<String, Vec<Value>>, manifest: &Value)
    -> Result<Vec<Value>, String>
{
    let fail = || "Invalid source-bound Pacific SECC regional reference".to_owned();
    let actual: Vec<_> = collections.get("reference_routes").into_iter().flatten()
        .filter(|row| row["current_id"] == CURRENT).collect();
    let receipt = &manifest[KEY];
    if receipt.is_null() {
        if !actual.is_empty() || !manifest["input_sha256"][FILE].is_null()
            || !manifest["input_sha256"][PUBLICATION_FILE].is_null() { return Err(fail()); }
        return Ok(vec![]);
    }
    let document = contract()?;
    if receipt["schema"] != "osw.pacific-secc-reference-runtime-receipt.v1"
        || receipt["parent_logical_sha256"] != PARENT || document["parent_logical_sha256"] != PARENT
        || receipt["contract_file"] != FILE || receipt["contract_sha256"] != pin(RAW)
        || manifest["input_sha256"][FILE] != pin(RAW)
        || receipt["new_physical_dimensions"] != 0 || receipt["installed"] != false
    { return Err(fail()); }
    for (path, sha) in document["input_sha256"].as_object().ok_or_else(fail)? {
        if manifest["input_sha256"][path] != *sha { return Err(fail()); }
    }
    let query = &document["query_contract"];
    let sources = collections.get("sources").ok_or_else(fail)?;
    let publication_admission = &receipt["publication_admission"];
    if !publication_admission.is_null() {
        let expected: Value = serde_json::from_str(PUBLICATION_RAW).map_err(|_| fail())?;
        if publication_admission != &expected
            || manifest["input_sha256"][PUBLICATION_FILE] != pin(PUBLICATION_RAW)
            || receipt["prior_owner"] != expected["audited_prior_owner"]
            || receipt["prior_decision"] != expected["audited_prior_decision"]
            || receipt["publication_source"] != expected["publication_source"]
            || sources.len() != 210 + crate::south_java_reference::additional_source_count(collections, manifest)?
                + crate::wicc_winter_reference::additional_source_count(collections, manifest)?
                + crate::mean_core_sections::additional_source_count(collections, manifest)?
                + crate::madagascar_dimensions::additional_source_count(collections, manifest)?
                + crate::azcc_onken_width::additional_source_count(collections, manifest)?
                + crate::pacific_nec_nominal_width::additional_source_count(collections, manifest)?
        { return Err(fail()); }
        for (path, sha) in expected["input_sha256"].as_object().ok_or_else(fail)? {
            if manifest["input_sha256"][path] != *sha { return Err(fail()); }
        }
        for source in expected["audited_owner_sources"].as_array().ok_or_else(fail)? {
            if sources.iter().filter(|r| r["id"] == source["id"]).collect::<Vec<_>>() != vec![source] {
                return Err(fail());
            }
        }
    } else if !manifest["input_sha256"][PUBLICATION_FILE].is_null() {
        return Err(fail());
    }
    let matches: Vec<_> = sources.iter().filter(|r| publication(r)).collect();
    if matches.len() != 1 || matches[0] != &receipt["publication_source"]
        || (!matches[0]["doi"].is_null() && doi(&matches[0]["doi"]) != DOI)
    { return Err(fail()); }
    let paper = &matches[0]["id"];
    let method = &query["method_source"];
    if sources.iter().filter(|r| r["id"] == method["id"]).collect::<Vec<_>>() != vec![method] {
        return Err(fail());
    }
    let mut expected_route = query["route"].clone();
    expected_route["source_id"] = paper.clone();
    expected_route["source_ids"] = json!([paper, method["id"]]);
    if actual != vec![&expected_route] { return Err(fail()); }
    let prior = &receipt["prior_decision"];
    if prior["source_decision"] != document["original_planning_source"]
        || prior["source_catalog_file"] != document["original_planning_file"]
        || prior["source_catalog_sha256"] != document["original_planning_sha256"]
        || prior["entity_id"] != OWNER || prior["route_ids"] != json!([])
        || prior["candidate_count"] != 0 || prior["rank_eligible"] != false
    { return Err(fail()); }
    let records: Vec<_> = collections.get("route_decisions").into_iter().flatten()
        .filter(|r| r["entity_id"] == OWNER).collect();
    if records.len() != 1 { return Err(fail()); }
    let mut expected_decision = prior.clone();
    expected_decision["prior_route_decision"] = prior.clone();
    expected_decision["route_ids"] = json!([expected_route["id"]]);
    expected_decision["candidate_count"] = json!(1);
    expected_decision["construction_status"] = json!("regional_editorial_reference_constructed");
    expected_decision["source_catalog_file"] = expected_route["source_file"].clone();
    expected_decision["source_catalog_sha256"] = expected_route["source_file_sha256"].clone();
    expected_decision["source_url"] = json!(URL);
    expected_decision["next_action"] = json!("Recover compatible total-flow axes and physical endpoints; regional drawing probes do not establish seasonal dimensions or whole-current length.");
    for (target, origin) in [("candidate_ids", "route_ids"), ("reference_path_decision", "construction_status"),
        ("next_action", "next_action"), ("name_source_url", "source_url")] {
        expected_decision["source_decision"][target] = expected_decision[origin].clone();
    }
    if records != vec![&expected_decision] { return Err(fail()); }
    let old = &receipt["prior_owner"];
    let owners: Vec<_> = collections.get("objects").into_iter().flatten().filter(|r| r["id"] == OWNER).collect();
    if owners.len() != 1 || !old.is_object() || !old["capabilities"].is_object()
        || !old["section_fingerprints"].is_object() || old["id"] != OWNER || old["type"] != "named_current"
        || old["route_ids"] != json!([]) || old["capabilities"]["reference_route"] != 0
        || old["route_decision_ids"] != json!([prior["id"]])
    { return Err(fail()); }
    let mut expected_owner = old.clone();
    expected_owner["route_ids"] = json!([expected_route["id"]]);
    expected_owner["capabilities"]["reference_route"] = json!(1);
    let mut feature = query["owner_map_feature"].clone();
    feature["source_id"] = paper.clone();
    expected_owner["map_features"].as_array_mut().ok_or_else(fail)?.push(feature);
    expected_owner["evidence_links"].as_array_mut().ok_or_else(fail)?.push(json!({
        "label":"Pacific SECC western reference and measurement scope", "url":"pacific-secc-reference-support.html"}));
    let refs = old["source_ids"].as_array().ok_or_else(fail)?;
    let mut ids = BTreeSet::new();
    for id in refs {
        let id = id.as_str().ok_or_else(fail)?;
        if !ids.insert(id.to_owned()) || !sources.iter().any(|r| r["id"] == id) { return Err(fail()); }
    }
    if old["linked_source_count"].as_u64() != Some(ids.len() as u64) { return Err(fail()); }
    ids.insert(paper.as_str().ok_or_else(fail)?.into());
    ids.insert(method["id"].as_str().ok_or_else(fail)?.into());
    expected_owner["source_ids"] = json!(ids.iter().collect::<Vec<_>>());
    expected_owner["linked_source_count"] = json!(ids.len());
    if !publication_admission.is_null() {
        expected_owner["route_url"] = publication_admission["atlas_route_url"].clone();
    }
    let section_raw = receipt["section_fingerprint_json"].as_str().ok_or_else(fail)?;
    let section: Value = serde_json::from_str(section_raw).map_err(|_| fail())?;
    if section != expected_route { return Err(fail()); }
    expected_owner["section_fingerprints"]["pacific_secc_western_reference"] = json!(pin(section_raw));
    expected_owner.as_object_mut().ok_or_else(fail)?.remove("fingerprint");
    let owner_raw = receipt["owner_fingerprint_json"].as_str().ok_or_else(fail)?;
    let owner: Value = serde_json::from_str(owner_raw).map_err(|_| fail())?;
    if owner != expected_owner { return Err(fail()); }
    expected_owner["fingerprint"] = json!(pin(owner_raw));
    if owners != vec![&expected_owner] { return Err(fail()); }
    Ok(vec![expected_route])
}

pub(crate) fn planning_source(record: &Value, collections: &BTreeMap<String, Vec<Value>>, manifest: &Value)
    -> Result<Option<&'static str>, String>
{
    if record["entity_id"] != OWNER { return Ok(None); }
    if routes(collections, manifest)?.is_empty() { return Ok(None); }
    Ok(Some("research/pacific-secc-western-mean-reference-path-v2-candidate.json"))
}

pub(crate) fn catalogue_projection(bundle: &crate::Bundle, mut catalog: Value) -> Result<Value, String> {
    let rows = routes(&bundle.collections, &bundle.manifest)?;
    if rows.is_empty() { return Ok(catalog); }
    let fail = || "Invalid Pacific SECC atlas projection".to_owned();
    let doc = contract()?;
    let mut report = doc["atlas_report"].clone();
    report["rendering_role"] = json!("derived_inline_editorial_reach_card_not_additional_observation");
    let candidates = catalog["candidates"].as_array_mut().ok_or_else(fail)?;
    if candidates.iter().any(|r| r["current_id"] == CURRENT) { return Err(fail()); }
    let mut entry = rows[0].clone();
    entry["candidate_file"] = entry["source_file"].clone();
    entry["candidate_sha256"] = entry["source_file_sha256"].clone();
    entry["figure"] = entry["figure_file"].clone();
    entry["route_extent_kind"] = json!("western mean-circulation editorial reference reach");
    entry["scenario_range_km"] = entry["public_editorial_probe_span_km"].clone();
    entry["nominal_atlas_state_crossings"] = json!([]);
    entry["state_intersection_status"] = json!("unassessed_no_physical_join_admitted");
    entry["remaining_gates"] = report["remaining_gates"].clone();
    entry["report_inline"] = report;
    candidates.push(entry);
    let decision = bundle.collections.get("route_decisions").into_iter().flatten()
        .find(|r| r["entity_id"] == OWNER).ok_or_else(fail)?;
    let plans = catalog["remaining_current_decisions"].as_array_mut().ok_or_else(fail)?;
    let indices: Vec<_> = plans.iter().enumerate().filter(|(_, r)| r["current_id"] == CURRENT).map(|(i, _)| i).collect();
    if indices.len() != 1 || plans[indices[0]] != doc["original_planning_source"] { return Err(fail()); }
    plans[indices[0]] = decision["source_decision"].clone();
    for (key, delta) in [("route_candidates", 1), ("currents_with_route_candidates", 1),
        ("currents_without_route_candidates", -1), ("currents_without_any_reference_card", -1)] {
        let old = catalog["counts"][key].as_i64().ok_or_else(fail)?;
        catalog["counts"][key] = json!(old.checked_add(delta).filter(|n| *n >= 0).ok_or_else(fail)?);
    }
    let strategies = catalog["planning_taxonomy"]["strategies"].as_array_mut().ok_or_else(fail)?;
    let indices: Vec<_> = strategies.iter().enumerate().filter(|(_, r)| r["id"] == decision["strategy_id"]).map(|(i, _)| i).collect();
    if indices.len() != 1 { return Err(fail()); }
    let strategy = &mut strategies[indices[0]];
    strategy["unbuilt_count"] = json!(strategy["unbuilt_count"].as_u64().and_then(|n| n.checked_sub(1)).ok_or_else(fail)?);
    Ok(catalog)
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> crate::Bundle {
        serde_json::from_str(include_str!("../../../research/pacific-secc-reference-runtime-fixture-v1.json")).unwrap()
    }
    fn publication_fixture() -> crate::Bundle {
        serde_json::from_str(include_str!("../../../research/pacific-secc-reference-publication-fixture-v1.json")).unwrap()
    }
    #[test]
    fn audited_publication_and_direct_atlas_navigation_are_source_bound() {
        let b = publication_fixture();
        let rows = routes(&b.collections, &b.manifest).unwrap();
        assert_eq!(rows.len(), 1);
        assert_eq!(rows[0]["source_id"], "source:chen-qiu-secc-seasonal-2004");
        assert_eq!(b.collections["sources"].len(), 210);
        assert!(b.collections["objects"][0]["route_url"].as_str().unwrap().contains("atlas-route="));
        crate::planning::validate(&b.collections, &b.manifest).unwrap();
    }
    #[test]
    fn publication_supplement_refuses_changed_audited_parent_and_navigation() {
        for change in ["parent", "navigation", "publication", "pin", "partial", "registry"] {
            let mut b = publication_fixture();
            match change {
                "parent" => b.manifest[KEY]["prior_owner"]["published_length_km"] = json!(1800),
                "navigation" => b.collections.get_mut("objects").unwrap()[0]["route_url"] = json!("wrong.html"),
                "publication" => b.collections.get_mut("sources").unwrap()[208]["title"] = json!("wrong paper"),
                "pin" => b.manifest["input_sha256"][PUBLICATION_FILE] = json!("wrong"),
                "partial" => { b.manifest[KEY].as_object_mut().unwrap().remove("publication_admission"); },
                "registry" => { b.collections.get_mut("sources").unwrap().pop(); },
                _ => unreachable!(),
            }
            assert!(routes(&b.collections, &b.manifest).is_err(), "{change}");
        }
    }
    #[test]
    fn source_bound_reference_accepts_and_generic_planning_matches() {
        let b = fixture();
        let rows = routes(&b.collections, &b.manifest).unwrap();
        assert_eq!(rows.len(), 1);
        assert_eq!(rows[0]["approximate_reference_path_km"], 1800);
        assert_eq!(rows[0]["annual_length_range_km"], Value::Null);
        crate::planning::validate(&b.collections, &b.manifest).unwrap();
    }
    #[test]
    fn altered_route_owner_source_and_receipt_are_refused() {
        for change in ["route", "owner", "publication", "receipt", "missing", "prior", "duplicate", "container"] {
            let mut b = fixture();
            match change {
                "route" => b.collections.get_mut("reference_routes").unwrap().last_mut().unwrap()["annual_length_range_km"] = json!([1700,1800]),
                "owner" => b.collections.get_mut("objects").unwrap()[0]["published_length_km"] = json!(1800),
                "publication" => b.collections.get_mut("sources").unwrap()[0]["rights"] = json!("changed"),
                "receipt" => b.manifest[KEY]["contract_sha256"] = json!("wrong"),
                "missing" => { b.manifest.as_object_mut().unwrap().remove(KEY); },
                "prior" => b.manifest[KEY]["prior_decision"]["source_decision"]["candidate_ids"] = json!(["wrong"]),
                "duplicate" => b.collections.get_mut("sources").unwrap().push(json!({"id":"duplicate","doi":DOI})),
                "container" => b.manifest[KEY]["prior_owner"]["section_fingerprints"] = json!(17),
                _ => unreachable!(),
            }
            assert!(routes(&b.collections, &b.manifest).is_err(), "{change}");
        }
    }
    #[test]
    fn inactive_parent_and_atlas_projection_preserve_scope() {
        let mut b = fixture();
        let doc = contract().unwrap();
        let source = &doc["original_planning_source"];
        let catalog = json!({"candidates":[],"remaining_current_decisions":[source],
            "counts":{"route_candidates":80,"currents_with_route_candidates":73,
                "currents_without_route_candidates":22,"currents_without_any_reference_card":22},
            "planning_taxonomy":{"strategies":[{"id":source["route_strategy_id"],"unbuilt_count":9}]}});
        let result = catalogue_projection(&b, catalog).unwrap();
        assert_eq!(result["counts"]["route_candidates"], 81);
        assert_eq!(result["candidates"][0]["nominal_atlas_state_crossings"], json!([]));
        let mut expected_report = doc["atlas_report"].clone();
        expected_report["rendering_role"] = json!("derived_inline_editorial_reach_card_not_additional_observation");
        assert_eq!(result["candidates"][0]["report_inline"], expected_report);
        assert_eq!(result["candidates"][0]["figure"], result["candidates"][0]["figure_file"]);
        assert!(catalogue_projection(&b, result).is_err());
        b.manifest.as_object_mut().unwrap().remove(KEY);
        b.manifest["input_sha256"].as_object_mut().unwrap().remove(FILE);
        b.collections.get_mut("reference_routes").unwrap().retain(|r| r["current_id"] != CURRENT);
        assert!(routes(&b.collections, &b.manifest).unwrap().is_empty());
    }
}
