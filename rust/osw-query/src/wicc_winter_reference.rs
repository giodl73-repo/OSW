//! Exact regional editorial reference; missing physical support stays missing.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
use std::sync::OnceLock;

pub(crate) const FILE: &str = "research/wicc-winter-reference-runtime-contract-v1.json";
const RAW: &str = include_str!("../../../research/wicc-winter-reference-runtime-contract-v1.json");
const KEY: &str = "wicc_winter_reference_delivery_v1";
const OWNER: &str = "current:west-india-coastal";
const CURRENT: &str = "west-india-coastal";
const ROUTE: &str = "wicc-winter-10n-22n-regional-reference-v1";
const CANDIDATE: &str = "research/wicc-winter-regional-reference-route-v4-candidate.json";
fn pin(raw: &str) -> String { format!("{:x}", Sha256::digest(raw.as_bytes())) }
fn document() -> &'static Value {
    static DOC: OnceLock<Value> = OnceLock::new();
    DOC.get_or_init(|| serde_json::from_str(RAW).expect("compiled WICC runtime contract"))
}
fn marker() -> Value {
    json!({"schema":"osw.wicc-winter-reference-runtime-receipt.v1",
        "parent_logical_sha256":document()["parent_logical_sha256"],"contract_file":FILE,"contract_sha256":pin(RAW),
        "new_editorial_routes":1,"new_publication_citations":2,"new_internal_sources":1,"new_physical_dimensions":0})
}
fn normalized_doi(v: &Value) -> String {
    let text = v.as_str().unwrap_or("").trim().to_lowercase();
    for prefix in ["https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "http://dx.doi.org/", "doi:"] {
        if let Some(tail) = text.strip_prefix(prefix) { return tail.trim().trim_end_matches('/').into(); }
    }
    text.trim_end_matches('/').into()
}
fn normalized_url(v: &Value) -> String {
    let text = v.as_str().unwrap_or("").trim().to_lowercase();
    let text = text.split(['?', '#']).next().unwrap_or("");
    text.strip_prefix("https://").or_else(|| text.strip_prefix("http://")).unwrap_or(text).trim_end_matches('/').into()
}
fn normalized_title(v: &Value) -> String {
    v.as_str().unwrap_or("").chars().filter(char::is_ascii_alphanumeric).flat_map(char::to_lowercase).collect()
}

pub(crate) fn routes(collections: &BTreeMap<String, Vec<Value>>, manifest: &Value) -> Result<Vec<Value>, String> {
    let fail = || "Invalid WICC winter regional reference projection".to_owned();
    let rows = |name: &str| collections.get(name).map(Vec::as_slice).unwrap_or(&[]);
    let actual: Vec<_> = rows("reference_routes").iter().filter(|r| r["id"] == ROUTE || r["current_id"] == CURRENT).collect();
    let doc = document();
    let query = &doc["query_contract"];
    let sources = rows("sources");
    if manifest[KEY].is_null() {
        let source_trace = query["new_sources"].as_array().ok_or_else(fail)?.iter()
            .any(|s| sources.iter().any(|r| r["id"] == s["id"]));
        let owner_trace = rows("objects").iter().any(|r| r["id"] == OWNER
            && (r["route_ids"].as_array().is_some_and(|ids| ids.iter().any(|id| id == ROUTE))
                || r["map_features"].as_array().is_some_and(|fs| fs.iter().any(|f| f["candidate_id"] == ROUTE))));
        if !actual.is_empty() || source_trace || owner_trace || !manifest["input_sha256"][FILE].is_null() { return Err(fail()); }
        return Ok(vec![]);
    }
    if manifest[KEY] != marker() || manifest["input_sha256"][FILE] != pin(RAW)
        || sources.len() as u64 != query["parent_collection_counts"]["sources"].as_u64().ok_or_else(fail)? + 3 + crate::mean_core_sections::additional_source_count(collections, manifest)? as u64 + crate::madagascar_dimensions::additional_source_count(collections, manifest)? as u64 + crate::azcc_onken_width::additional_source_count(collections, manifest)? as u64 + crate::pacific_nec_nominal_width::additional_source_count(collections, manifest)? as u64 + crate::indian_sec_model_grid_lengths::additional_source_count(collections, manifest)? as u64 + crate::pacific_nec_product_axes::additional_source_count(collections, manifest)? as u64 + crate::dimoune_section_widths::additional_source_count(collections, manifest)? as u64 + crate::atlantic_nec_band_spans::additional_source_count(collections, manifest)? as u64 + crate::characteristic_velocities::additional_source_count(collections, manifest)? as u64
        || rows("reference_routes").len() as u64 != query["parent_collection_counts"]["reference_routes"].as_u64().ok_or_else(fail)? + 1
        || actual != vec![&query["route"]] { return Err(fail()); }
    for (path, digest) in doc["input_sha256"].as_object().ok_or_else(fail)? {
        if manifest["input_sha256"][path] != *digest { return Err(fail()); }
    }
    let mut ids = BTreeSet::new();
    for row in sources {
        let id = row["id"].as_str().ok_or_else(fail)?;
        if id.is_empty() || !ids.insert(id) { return Err(fail()); }
    }
    for expected in query["new_sources"].as_array().ok_or_else(fail)? {
        let doi = normalized_doi(&expected["doi"]);
        let url = normalized_url(&expected["url"]);
        let title = normalized_title(&expected["title"]);
        let matches: Vec<_> = sources.iter().filter(|r| r["id"] == expected["id"]
            || (!doi.is_empty() && (normalized_doi(&r["doi"]) == doi || normalized_doi(&r["url"]) == doi))
            || (!url.is_empty() && normalized_url(&r["url"]) == url)
            || (!title.is_empty() && normalized_title(&r["title"]) == title)).collect();
        if matches != vec![expected] { return Err(fail()); }
    }
    let prior = &query["prior_records"];
    for expected in prior["owner_sources"].as_array().ok_or_else(fail)? {
        if sources.iter().filter(|r| r["id"] == expected["id"]).collect::<Vec<_>>() != vec![expected] { return Err(fail()); }
    }
    for (collection, field, expected) in [("objects", "id", &doc["final_owner"]),
        ("entities", "id", &prior["entity"]), ("route_decisions", "entity_id", &doc["final_decision"])] {
        if rows(collection).iter().filter(|r| r[field] == OWNER).collect::<Vec<_>>() != vec![expected] { return Err(fail()); }
    }
    if rows("widths").iter().filter(|r| r["current_id"] == CURRENT).cloned().collect::<Vec<_>>()
        != *prior["widths"].as_array().ok_or_else(fail)? { return Err(fail()); }
    let route = &query["route"];
    for key in ["scenario_range_km", "uncertainty_km", "annual_length_range_km", "annual_width_range_km", "whole_current_length_km", "physical_width_km", "sample_date"] {
        if !route[key].is_null() { return Err(fail()); }
    }
    for key in ["rank_eligible", "physical_current_axis_admitted", "physical_state_join_eligible", "seasonal_playback_eligible"] {
        if route[key] != false { return Err(fail()); }
    }
    Ok(vec![route.clone()])
}

pub(crate) fn additional_source_count(collections: &BTreeMap<String, Vec<Value>>, manifest: &Value) -> Result<usize, String> {
    Ok(if routes(collections, manifest)?.is_empty() { 0 } else { 3 })
}
pub(crate) fn planning_source(record: &Value, collections: &BTreeMap<String, Vec<Value>>, manifest: &Value) -> Result<Option<&'static str>, String> {
    if record["entity_id"] != OWNER || routes(collections, manifest)?.is_empty() { return Ok(None); }
    Ok(Some(CANDIDATE))
}
pub(crate) fn retained_width_owner(bundle: &Bundle, actual: &Value) -> Result<Value, String> {
    if actual["id"] != OWNER || routes(&bundle.collections, &bundle.manifest)?.is_empty() { return Ok(actual.clone()); }
    if actual != &document()["final_owner"] { return Err("Changed WICC route owner".into()); }
    Ok(document()["query_contract"]["prior_records"]["owner"].clone())
}
pub(crate) fn dashboard_row(bundle: &Bundle, original: &Value) -> Result<Value, String> {
    if original["id"] != OWNER || routes(&bundle.collections, &bundle.manifest)?.is_empty() { return Ok(original.clone()); }
    if original != &document()["dashboard_before"] { return Err("Changed preceding WICC dashboard projection".into()); }
    Ok(document()["dashboard_after"].clone())
}
pub(crate) fn dashboard_document(bundle: &Bundle, mut doc: Value) -> Result<Value, String> {
    if routes(&bundle.collections, &bundle.manifest)?.is_empty() { return Ok(doc); }
    let rows = doc["entries"].as_array().ok_or("Missing dashboard entries")?;
    let projected = rows.iter().map(|r| dashboard_row(bundle, r)).collect::<Result<Vec<_>, _>>()?;
    let prior = doc["snapshot_fingerprint"].as_str().ok_or("Missing preceding dashboard fingerprint")?;
    let fingerprint = pin(&format!("osw.wicc-winter-reference.v1\n{prior}\n{}\n", pin(RAW)));
    doc["entries"] = json!(projected);
    doc["snapshot_fingerprint"] = json!(fingerprint);
    doc["wicc_winter_reference_projection_v1"] = json!({"contract_file":FILE,"contract_sha256":pin(RAW),"scope":"One abstract-supported regional editorial path; no physical length or annual range."});
    Ok(doc)
}
pub(crate) fn catalogue_projection(bundle: &Bundle, mut catalog: Value) -> Result<Value, String> {
    let routes = routes(&bundle.collections, &bundle.manifest)?;
    if routes.is_empty() { return Ok(catalog); }
    let fail = || "Invalid WICC regional atlas projection".to_owned();
    let doc = document();
    let report = &doc["query_contract"]["atlas_report"];
    let candidates = catalog["candidates"].as_array_mut().ok_or_else(fail)?;
    if candidates.iter().any(|r| r["current_id"] == CURRENT) { return Err(fail()); }
    let mut entry = routes[0].clone();
    entry["report_inline"] = report.clone();
    entry["nominal_atlas_state_crossings"] = json!([]);
    entry["state_intersection_status"] = json!("editorial_navigation_only_no_physical_join");
    entry["remaining_gates"] = report["remaining_gates"].clone();
    candidates.push(entry);
    let plans = catalog["remaining_current_decisions"].as_array_mut().ok_or_else(fail)?;
    let indices: Vec<_> = plans.iter().enumerate().filter(|(_, r)| r["current_id"] == CURRENT).map(|(i, _)| i).collect();
    if indices.len() != 1 || plans[indices[0]] != doc["original_planning_source"] { return Err(fail()); }
    plans[indices[0]] = doc["final_decision"]["source_decision"].clone();
    for (key, delta) in [("route_candidates", 1), ("currents_with_route_candidates", 1),
        ("currents_without_route_candidates", -1), ("currents_without_any_reference_card", -1)] {
        let value = catalog["counts"][key].as_i64().ok_or_else(fail)?;
        catalog["counts"][key] = json!(value.checked_add(delta).filter(|v| *v >= 0).ok_or_else(fail)?);
    }
    let strategy = catalog["planning_taxonomy"]["strategies"].as_array_mut().ok_or_else(fail)?
        .iter_mut().find(|r| r["id"] == doc["final_decision"]["strategy_id"]).ok_or_else(fail)?;
    strategy["unbuilt_count"] = json!(strategy["unbuilt_count"].as_u64().and_then(|n| n.checked_sub(1)).ok_or_else(fail)?);
    Ok(catalog)
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> Bundle {
        serde_json::from_str(include_str!("../../../research/wicc-winter-reference-runtime-fixture-v1.json")).unwrap()
    }
    #[test]
    fn regional_route_and_full_planning_projection_accept() {
        let mut b = fixture();
        assert_eq!(routes(&b.collections, &b.manifest).unwrap().len(), 1);
        b.collections.get_mut("route_decisions").unwrap().retain(|r| r["entity_id"] == OWNER);
        crate::planning::validate(&b.collections, &b.manifest).unwrap();
        assert_eq!(additional_source_count(&b.collections, &b.manifest).unwrap(), 3);
    }
    #[test]
    fn changed_range_owner_width_citation_and_receipt_refuse() {
        for change in ["range", "owner", "width", "citation", "receipt", "missing-marker", "duplicate-title"] {
            let mut b = fixture();
            match change {
                "range" => b.collections.get_mut("reference_routes").unwrap().last_mut().unwrap()["scenario_range_km"] = json!([1500, 1600]),
                "owner" => b.collections.get_mut("objects").unwrap()[0]["capabilities"]["reported_length"] = json!(1),
                "width" => b.collections.get_mut("widths").unwrap()[0]["reported_width_km"] = json!(151),
                "citation" => b.collections.get_mut("sources").unwrap().last_mut().unwrap()["title"] = json!("changed"),
                "receipt" => b.manifest[KEY]["new_physical_dimensions"] = json!(1),
                "missing-marker" => { b.manifest.as_object_mut().unwrap().remove(KEY); },
                _ => { let paper = document()["query_contract"]["new_sources"][0].clone();
                       b.collections.get_mut("sources").unwrap()[5] = json!({"id":"fixture:duplicate-title","title":paper["title"]}); }
            }
            assert!(routes(&b.collections, &b.manifest).is_err(), "{change}");
        }
    }
    #[test]
    fn width_validator_composes_after_exact_route_validation() {
        let b = fixture();
        crate::wicc_review_width::validate(&b).unwrap();
        assert_eq!(retained_width_owner(&b, &document()["final_owner"]).unwrap(), document()["query_contract"]["prior_records"]["owner"]);
    }
    #[test]
    fn dashboard_projects_only_exact_preceding_wicc_row() {
        let b = fixture();
        assert_eq!(dashboard_row(&b, &document()["dashboard_before"]).unwrap(), document()["dashboard_after"]);
        assert!(dashboard_row(&b, &json!({"id":OWNER})).is_err());
        let unrelated = json!({"id":"current:other"});
        assert_eq!(dashboard_row(&b, &unrelated).unwrap(), unrelated);
    }
    #[test]
    fn inactive_legacy_bundle_is_unchanged() {
        let b = Bundle { schema: "osw.query-bundle.v1".into(), manifest: json!({}), collections: BTreeMap::new() };
        assert!(routes(&b.collections, &b.manifest).unwrap().is_empty());
        assert_eq!(additional_source_count(&b.collections, &b.manifest).unwrap(), 0);
    }
}
