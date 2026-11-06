//! Experimental surface-product paths remain separate from physical dimensions.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
use std::sync::OnceLock;

pub(crate) const FILE: &str = "research/pacific-nec-product-axis-query-contract-v1.json";
const RAW: &str = include_str!("../../../research/pacific-nec-product-axis-query-contract-v1.json");
const KEY: &str = "pacific_nec_surface_product_axes_v1";
pub(crate) const OWNER: &str = "current:pacific-north-equatorial";
const COLLECTIONS: [&str; 4] = ["current_axis_series", "current_axis_readings", "current_axis_scenarios", "current_axis_section_spans"];
const PREFIXES: [&str; 4] = ["product_axis_series:pacific-nec:", "product_axis_reading:pacific-nec:", "product_axis_scenario:pacific-nec:", "product_axis_span:pacific-nec:"];

fn pin() -> String { format!("{:x}", Sha256::digest(RAW.as_bytes())) }
fn document() -> &'static Value {
    static DOC: OnceLock<Value> = OnceLock::new();
    DOC.get_or_init(|| serde_json::from_str(RAW).expect("compiled Pacific NEC product-axis contract"))
}
fn marker() -> Value {
    json!({"schema":"osw.pacific-nec-product-axis-runtime.v1","contract_file":FILE,"contract_sha256":pin(),
        "parent_logical_sha256":document()["parent_logical_sha256"],"collections_added":document()["counts_added"],
        "sources_added":3,"admission":"experimental_product_operator_only","reported_lengths_added":0,
        "reference_routes_added":0,"physical_widths_added":0,"physical_state_joins_added":0,
        "annual_physical_ranges_added":0,"independent_observations_added":0})
}
fn rows<'a>(collections: &'a BTreeMap<String, Vec<Value>>, name: &str) -> &'a [Value] {
    collections.get(name).map(Vec::as_slice).unwrap_or(&[])
}
fn owns(row: &Value, owner: &str) -> bool {
    row["entity_id"] == owner || row["family_entity_id"] == owner
        || owner.strip_prefix("current:").is_some_and(|short| row["current_id"] == short)
}
fn locations() -> &'static BTreeMap<String, (String, usize)> {
    static POS: OnceLock<BTreeMap<String, (String, usize)>> = OnceLock::new();
    POS.get_or_init(|| {
        let mut result = BTreeMap::new();
        for name in COLLECTIONS {
            for (index, row) in document()["collections_added"][name].as_array().unwrap().iter().enumerate() {
                assert!(result.insert(row["id"].as_str().unwrap().into(), (name.into(), index)).is_none());
            }
        }
        result
    })
}
fn checked(collections: &BTreeMap<String, Vec<Value>>, manifest: &Value) -> Result<bool, String> {
    let fail = || "Invalid Pacific NEC experimental surface-product diagnostic extension".to_owned();
    let doc = document();
    let sources = doc["new_sources"].as_array().ok_or_else(fail)?;
    let prefix = |row: &Value| row["id"].as_str().is_some_and(|id| PREFIXES.iter().any(|p| id.starts_with(p)));
    let present = !manifest[KEY].is_null() || !manifest["input_sha256"][FILE].is_null()
        || COLLECTIONS.iter().any(|name| collections.contains_key(*name))
        || rows(collections, "sources").iter().any(|r| sources.iter().any(|s| r["id"] == s["id"]))
        || collections.values().flatten().any(prefix);
    if !present { return Ok(false); }
    if manifest[KEY] != marker() || manifest["input_sha256"][FILE] != pin() { return Err(fail()); }
    for (path, digest) in doc["input_sha256"].as_object().ok_or_else(fail)? {
        if manifest["input_sha256"][path] != *digest { return Err(fail()); }
    }
    for name in COLLECTIONS {
        let expected = doc["collections_added"][name].as_array().ok_or_else(fail)?;
        if rows(collections, name) != expected.as_slice() { return Err(fail()); }
    }
    for (name, records) in collections {
        for row in records {
            if prefix(row) {
                let id = row["id"].as_str().ok_or_else(fail)?;
                if locations().get(id).map(|(n, _)| n.as_str()) != Some(name.as_str()) { return Err(fail()); }
            }
        }
    }
    let mut source_ids = BTreeSet::new();
    for row in rows(collections, "sources") {
        let id = row["id"].as_str().filter(|s| !s.is_empty()).ok_or_else(fail)?;
        if !source_ids.insert(id) { return Err(fail()); }
    }
    for expected in doc["prior_source_inventory"].as_array().ok_or_else(fail)?.iter().chain(sources) {
        if rows(collections, "sources").iter().filter(|r| r["id"] == expected["id"]).collect::<Vec<_>>() != vec![expected] { return Err(fail()); }
    }
    for (owner, prior) in doc["prior_identity_rows"].as_object().ok_or_else(fail)? {
        for name in ["objects", "entities"] {
            let expected = prior[name].as_array().ok_or_else(fail)?;
            if rows(collections, name).iter().filter(|r| r["id"] == *owner).collect::<Vec<_>>() != expected.iter().collect::<Vec<_>>() { return Err(fail()); }
        }
        for (name, expected) in prior["linked_records"].as_object().ok_or_else(fail)? {
            if rows(collections, name).iter().filter(|r| owns(r, owner)).collect::<Vec<_>>() != expected.as_array().ok_or_else(fail)?.iter().collect::<Vec<_>>() { return Err(fail()); }
        }
    }
    Ok(true)
}
pub(crate) fn validate(bundle: &Bundle) -> Result<(), String> { checked(&bundle.collections, &bundle.manifest).map(|_| ()) }
pub(crate) fn identity_overlay(bundle: &Bundle) -> Result<bool, String> { checked(&bundle.collections, &bundle.manifest) }
pub(crate) fn additional_source_count(collections: &BTreeMap<String, Vec<Value>>, manifest: &Value) -> Result<usize, String> {
    Ok(if checked(collections, manifest)? { 3 } else { 0 })
}
// Only after identity_overlay validated the complete extension. Unknown or changed
// rows are retained for the preceding validator to reject, never silently hidden.
pub(crate) fn identity_parent_row<'a>(collection: &str, row: &'a Value, enabled: bool) -> Option<&'a Value> {
    if enabled {
        if let Some((name, index)) = row["id"].as_str().and_then(|id| locations().get(id)) {
            if name.as_str() == collection && row == &document()["collections_added"][name.as_str()][*index] { return None; }
        }
    }
    Some(row)
}
fn full_scene() -> Value {
    json!({"kind":"surface_product_axis_diagnostics","entity_id":OWNER,"title":"Pacific NEC:2013 surface-product diagnostics",
        "scope":"Experimental window-constrained OSCAR product-operator paths between130E and120W. They do not establish whole-current dimensions, physical axes, annual physical ranges or independent observations.",
        "series":document()["collections_added"]["current_axis_series"],
        "readings":document()["collections_added"]["current_axis_readings"],
        "section_spans":document()["collections_added"]["current_axis_section_spans"],
        "scenario_count":1332,"sources":document()["new_sources"],
        "nominal_window_deg_north":[8,18],"default_month":1,"year":2013,
        "playback_scope":"Dated monthly source-product frames only; no temporal interpolation or seasonal climatology.",
        "method_span_scope":"Threshold, direction, search/window and representation choices are separate operators; their spread is not physical uncertainty."})
}
pub(crate) fn query_scene(collection: &str, selected: &[&Value], bundle: &Bundle) -> Result<Value, String> {
    if !COLLECTIONS.contains(&collection) { return Ok(Value::Null); }
    if !identity_overlay(bundle)? { return Err("Product-axis scene lacks complete validated evidence".into()); }
    let mut scene = full_scene();
    let ids: BTreeSet<&str> = selected.iter().filter_map(|r| {
        if collection == "current_axis_series" { r["id"].as_str() } else { r["series_id"].as_str() }
    }).collect();
    scene["series"] = json!(document()["collections_added"]["current_axis_series"].as_array().unwrap().iter().filter(|r| r["id"].as_str().is_some_and(|id| ids.contains(id))).collect::<Vec<_>>());
    scene["readings"] = if collection == "current_axis_readings" { json!(selected) }
        else if collection == "current_axis_series" { json!(document()["collections_added"]["current_axis_readings"].as_array().unwrap().iter().filter(|r| r["series_id"].as_str().is_some_and(|id| ids.contains(id))).collect::<Vec<_>>()) }
        else { json!([]) };
    scene["section_spans"] = if collection == "current_axis_section_spans" { json!(selected) } else { json!([]) };
    scene["selected_collection"] = json!(collection); scene["selected_records"] = json!(selected); scene["selected_count"] = json!(selected.len());
    Ok(scene)
}
pub(crate) fn object_projection(bundle: &Bundle, id: &str, mut value: Value) -> Result<Value, String> {
    if id == OWNER && identity_overlay(bundle)? { value["surface_product_axis_scene"] = full_scene(); }
    Ok(value)
}
pub(crate) fn atlas_projection(bundle: &Bundle, mut value: Value) -> Result<Value, String> {
    if identity_overlay(bundle)? { value["surface_product_axis_scenes"] = json!({"pacific-north-equatorial":full_scene()}); }
    Ok(value)
}
pub(crate) fn dashboard_projection(bundle: &Bundle, mut value: Value) -> Result<Value, String> {
    if identity_overlay(bundle)? {
        value["surface_product_axis_diagnostics"] = json!({"entity_id":OWNER,"series_count":3,"monthly_path_count":36,
            "method_scenario_count":1332,"section_span_count":36,"withheld_scenario_count":85,"withheld_section_span_count":1,
            "physical_dimensions_added":0,"label":"Pacific NEC: experimental2013 product diagnostics",
            "object_url":"object.html?id=current%3Apacific-north-equatorial","collection":"current_axis_series"});
    }
    Ok(value)
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> Bundle {
        let doc = document();
        let mut collections: BTreeMap<String, Vec<Value>> = BTreeMap::new();
        for (name, records) in doc["collections_added"].as_object().unwrap() { collections.insert(name.clone(), records.as_array().unwrap().clone()); }
        let mut sources = doc["prior_source_inventory"].as_array().unwrap().clone();
        sources.extend(doc["new_sources"].as_array().unwrap().clone()); collections.insert("sources".into(), sources);
        for prior in doc["prior_identity_rows"].as_object().unwrap().values() {
            for name in ["objects", "entities"] { collections.entry(name.into()).or_default().extend(prior[name].as_array().unwrap().clone()); }
            for (name, records) in prior["linked_records"].as_object().unwrap() {
                for row in records.as_array().unwrap() {
                    let target = collections.entry(name.clone()).or_default();
                    if !target.contains(row) { target.push(row.clone()); }
                }
            }
        }
        let mut manifest = json!({"input_sha256":doc["input_sha256"]});
        manifest["input_sha256"][FILE] = json!(pin()); manifest[KEY] = marker();
        Bundle { schema:"osw.query-bundle.v1".into(), manifest, collections }
    }
    #[test] fn validates_all_records_and_sources_without_physical_admission() {
        let b = fixture(); assert!(identity_overlay(&b).unwrap());
        assert_eq!(additional_source_count(&b.collections, &b.manifest).unwrap(), 3);
        for name in COLLECTIONS { for row in &b.collections[name] { assert_eq!(row["rank_eligible"], false); assert_eq!(row["physical_current_axis_qualified"], false); } }
    }
    #[test] fn partial_rows_modified_flags_sources_and_prior_identity_are_refused() {
        for case in 0..5 {
            let mut b = fixture();
            match case {
                0 => { b.collections.get_mut("current_axis_readings").unwrap().pop(); },
                1 => b.collections.get_mut("current_axis_readings").unwrap()[0]["rank_eligible"] = json!(true),
                2 => b.collections.get_mut("sources").unwrap().last_mut().unwrap()["title"] = json!("changed"),
                3 => b.collections.get_mut("objects").unwrap()[0]["published_length_km"] = json!(13000),
                _ => b.manifest[KEY] = json!({}),
            }
            assert!(identity_overlay(&b).is_err(), "case{case}");
        }
    }
    #[test] fn older_parent_has_no_overlay_and_no_extra_sources() {
        let b = Bundle { schema:"osw.query-bundle.v1".into(), manifest:json!({}), collections:BTreeMap::new() };
        assert!(!identity_overlay(&b).unwrap()); assert_eq!(additional_source_count(&b.collections, &b.manifest).unwrap(), 0);
    }
    #[test] fn only_exact_verified_diagnostic_rows_are_hidden_from_prior_identity_checks() {
        let b = fixture(); let enabled = identity_overlay(&b).unwrap(); let row = &b.collections[COLLECTIONS[1]][0];
        assert!(identity_parent_row(COLLECTIONS[1], row, enabled).is_none());
        let mut changed = row.clone(); changed["rank_eligible"] = json!(true);
        assert_eq!(identity_parent_row(COLLECTIONS[1], &changed, enabled), Some(&changed));
        assert_eq!(identity_parent_row("objects", row, enabled), Some(row));
        assert_eq!(identity_parent_row(COLLECTIONS[1], row, false), Some(row));
    }
    #[test] fn query_scenes_use_exact_matches_and_never_map_method_shortcuts() {
        let b = fixture(); let reading = &b.collections[COLLECTIONS[1]][0];
        let scene = query_scene(COLLECTIONS[1], &[reading], &b).unwrap();
        assert_eq!(scene["selected_count"], 1); assert_eq!(scene["readings"], json!([reading]));
        let scenario = &b.collections[COLLECTIONS[2]][0];
        let scene = query_scene(COLLECTIONS[2], &[scenario], &b).unwrap();
        assert_eq!(scene["readings"], json!([])); assert_eq!(scene["selected_records"], json!([scenario]));
        assert_eq!(query_scene(COLLECTIONS[1], &[], &b).unwrap()["readings"], json!([]));
    }
    #[test] fn owner_card_and_atlas_have_scenes_but_family_does_not() {
        let b = fixture(); assert!(!object_projection(&b, OWNER, json!({})).unwrap()["surface_product_axis_scene"].is_null());
        assert!(object_projection(&b, "current:north-equatorial", json!({"keep":true})).unwrap()["surface_product_axis_scene"].is_null());
        assert_eq!(atlas_projection(&b, json!({"keep":true})).unwrap()["keep"], true);
        assert_eq!(dashboard_projection(&b, json!({})).unwrap()["surface_product_axis_diagnostics"]["physical_dimensions_added"], 0);
    }
}
