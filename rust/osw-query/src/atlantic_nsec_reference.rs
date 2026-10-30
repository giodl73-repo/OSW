//! Two explicitly editorial regional references; whole-current dimensions stay unknown.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
use std::sync::OnceLock;

pub(crate) const FILE: &str = "research/atlantic-nsec-reference-query-contract-v2.json";
const RAW: &str = include_str!("../../../research/atlantic-nsec-reference-query-contract-v2.json");
const KEY: &str = "atlantic_nsec_reference_routes_v1";
const OWNER: &str = "current:atlantic-south-equatorial";
const CURRENT: &str = "atlantic-south-equatorial";
const PREPARED: &str = "research/atlantic-nsec-schematic-reference-reaches-prepared-v1.json";
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
fn document() -> &'static Value {
    static DOC: OnceLock<Value> = OnceLock::new();
    DOC.get_or_init(|| {
        serde_json::from_str(RAW).expect("compiled Atlantic nSEC reference contract")
    })
}
fn rows<'a>(c: &'a BTreeMap<String, Vec<Value>>, name: &str) -> &'a [Value] {
    c.get(name).map(Vec::as_slice).unwrap_or(&[])
}
fn owns(row: &Value) -> bool {
    row["entity_id"] == OWNER || row["current_id"] == CURRENT
}
fn additions(name: &str) -> &'static [Value] {
    match name {
        "reference_routes" => document()["routes"].as_array().unwrap(),
        "sources" => document()["new_sources"].as_array().unwrap(),
        _ => &[],
    }
}
fn marker() -> Value {
    json!({"schema":"osw.atlantic-nsec-reference-runtime.v1","parent_logical_sha256":document()["parent_logical_sha256"],"contract_file":FILE,"contract_sha256":pin(RAW),"reference_routes_added":2,"sources_added":2,"reported_whole_current_lengths_added":0,"annual_ranges_added":0,"physical_geometries_added":0,"independent_observations_added":0})
}
fn checked(c: &BTreeMap<String, Vec<Value>>, manifest: &Value) -> Result<bool, String> {
    crate::validation_scope::checked(c, manifest, module_path!(), || checked_uncached(c, manifest))
}
fn checked_uncached(c: &BTreeMap<String, Vec<Value>>, manifest: &Value) -> Result<bool, String> {
    let fail = || "Invalid source-bound Atlantic SEC regional references".to_owned();
    let doc = document();
    let trace = c.values().flatten().any(|r| {
        ["reference_routes", "sources"]
            .iter()
            .any(|name| additions(name).iter().any(|e| e["id"] == r["id"]))
    });
    if manifest[KEY].is_null() && manifest["input_sha256"][FILE].is_null() && !trace {
        return Ok(false);
    }
    if manifest[KEY] != marker() || manifest["input_sha256"][FILE] != pin(RAW) {
        return Err(fail());
    }
    for (p, h) in doc["input_sha256"].as_object().ok_or_else(fail)? {
        if manifest["input_sha256"][p] != *h {
            return Err(fail());
        }
    }
    if rows(c, "objects")
        .iter()
        .filter(|r| r["id"] == OWNER)
        .collect::<Vec<_>>()
        != vec![&doc["final_owner"]]
        || rows(c, "entities")
            .iter()
            .filter(|r| r["id"] == OWNER)
            .collect::<Vec<_>>()
            != vec![&doc["prior_entity"]]
        || rows(c, "route_decisions")
            .iter()
            .filter(|r| owns(r))
            .collect::<Vec<_>>()
            != vec![&doc["final_decision"]]
        || rows(c, "reference_routes")
            .iter()
            .filter(|r| owns(r))
            .collect::<Vec<_>>()
            != additions("reference_routes").iter().collect::<Vec<_>>()
    {
        return Err(fail());
    }
    for (name, key) in [
        ("widths", "prior_widths"),
        ("length_assessments", "prior_length_assessments"),
    ] {
        if rows(c, name).iter().filter(|r| owns(r)).collect::<Vec<_>>()
            != doc[key]
                .as_array()
                .ok_or_else(fail)?
                .iter()
                .collect::<Vec<_>>()
        {
            return Err(fail());
        }
    }
    let mut ids = BTreeSet::new();
    for row in rows(c, "sources") {
        if !row["id"]
            .as_str()
            .is_some_and(|s| !s.is_empty() && ids.insert(s))
        {
            return Err(fail());
        }
    }
    for expected in doc["prior_owner_sources"]
        .as_array()
        .ok_or_else(fail)?
        .iter()
        .chain(additions("sources"))
    {
        if rows(c, "sources")
            .iter()
            .filter(|r| r["id"] == expected["id"])
            .collect::<Vec<_>>()
            != vec![expected]
        {
            return Err(fail());
        }
    }
    for name in ["reference_routes", "sources"] {
        for expected in additions(name) {
            let actual = c
                .iter()
                .flat_map(|(n, records)| {
                    records
                        .iter()
                        .filter(|r| r["id"] == expected["id"])
                        .map(move |r| (n.as_str(), r))
                })
                .collect::<Vec<_>>();
            if actual != vec![(name, expected)] {
                return Err(fail());
            }
        }
    }
    Ok(true)
}
pub(crate) fn validate(bundle: &Bundle) -> Result<(), String> {
    checked(&bundle.collections, &bundle.manifest).map(|_| ())
}
pub(crate) fn identity_overlay(bundle: &Bundle) -> Result<bool, String> {
    checked(&bundle.collections, &bundle.manifest)
}
pub(crate) fn additional_source_count(
    c: &BTreeMap<String, Vec<Value>>,
    manifest: &Value,
) -> Result<usize, String> {
    Ok((if checked(c, manifest)? { 2 } else { 0 }) + crate::current_reference_profiles::additional_source_count(c, manifest)?)
}
pub(crate) fn additional_reference_route_count(
    c: &BTreeMap<String, Vec<Value>>,
    manifest: &Value,
) -> Result<usize, String> {
    Ok(if checked(c, manifest)? {
        additions("reference_routes").len()
    } else {
        0
    } + crate::current_reference_profiles::additional_reference_route_count(c, manifest)?)
}
pub(crate) fn validated_reference_routes(bundle: &Bundle) -> Result<Vec<Value>, String> {
    let mut result = if identity_overlay(bundle)? { additions("reference_routes").to_vec() } else { vec![] };
    result.extend(crate::current_reference_profiles::validated_routes(bundle)?);
    Ok(result)
}
pub(crate) fn parent_object<'a>(row: &'a Value, manifest: &Value) -> &'a Value {
    let row = crate::current_reference_profiles::parent_object(row, manifest);
    if !manifest[KEY].is_null() && row == &document()["final_owner"] {
        &document()["prior_owner"]
    } else {
        row
    }
}
pub(crate) fn identity_parent_row<'a>(
    name: &str,
    row: &'a Value,
    enabled: bool,
) -> Option<&'a Value> {
    if enabled {
        if additions(name).contains(row) {
            return None;
        }
        if name == "objects" && row == &document()["final_owner"] {
            return Some(&document()["prior_owner"]);
        }
        if name == "route_decisions" && row == &document()["final_decision"] {
            return Some(&document()["prior_decision"]);
        }
    }
    Some(row)
}
pub(crate) fn planning_source(
    record: &Value,
    c: &BTreeMap<String, Vec<Value>>,
    manifest: &Value,
) -> Result<Option<&'static str>, String> {
    if record["entity_id"] != OWNER || !checked(c, manifest)? {
        return Ok(None);
    }
    Ok(Some(PREPARED))
}
pub(crate) fn dashboard_row(bundle: &Bundle, row: &Value) -> Result<Value, String> {
    if bundle.manifest[KEY].is_null() || row["id"] != OWNER {
        return Ok(row.clone());
    }
    let mut result = row.clone();
    let doc = document();
    for key in [
        "route_ids",
        "route_url",
        "capabilities",
        "map_features",
        "evidence_links",
        "source_ids",
        "linked_source_count",
        "section_fingerprints",
        "fingerprint",
    ] {
        if row[key] != doc["prior_owner"][key] {
            return Err(format!("Changed preceding Atlantic nSEC dashboard {key}"));
        }
        result[key] = doc["final_owner"][key].clone();
    }
    Ok(result)
}
pub(crate) fn dashboard_document(bundle: &Bundle, mut value: Value) -> Result<Value, String> {
    if bundle.manifest[KEY].is_null() {
        return Ok(value);
    }
    let old = value["entries"]
        .as_array()
        .ok_or("Missing preceding dashboard entries")?;
    let updated = old
        .iter()
        .map(|r| dashboard_row(bundle, r))
        .collect::<Result<Vec<_>, _>>()?;
    if updated.iter().filter(|r| r["id"] == OWNER).count() != 1 {
        return Err("Missing Atlantic SEC dashboard owner".into());
    }
    value["entries"] = json!(updated);
    value["snapshot_fingerprint"] = json!(pin(&format!(
        "osw.atlantic-nsec-reference.v1\n{}\n{}\n",
        value["snapshot_fingerprint"]
            .as_str()
            .ok_or("Missing prior dashboard fingerprint")?,
        pin(RAW)
    )));
    Ok(value)
}
pub(crate) fn catalogue_projection(bundle: &Bundle, mut catalog: Value) -> Result<Value, String> {
    if !identity_overlay(bundle)? {
        return Ok(catalog);
    }
    let fail = || "Invalid Atlantic nSEC atlas reference projection".to_owned();
    let doc = document();
    let candidates = catalog["candidates"].as_array_mut().ok_or_else(fail)?;
    if candidates.iter().any(owns) {
        return Err(fail());
    }
    for route in additions("reference_routes") {
        let mut entry = route.clone();
        entry["candidate_file"] = route["source_file"].clone();
        entry["candidate_sha256"] = route["source_file_sha256"].clone();
        entry["figure"] = route["figure_file"].clone();
        entry["route_extent_kind"] = json!("northern-branch regional schematic reference");
        let bounds = route["editorial_probe_length_range_km"]
            .as_array()
            .ok_or_else(fail)?;
        entry["scenario_range_km"] = json!([
            100.0 * (bounds[0].as_f64().ok_or_else(fail)? / 100.0).floor(),
            100.0 * (bounds[1].as_f64().ok_or_else(fail)? / 100.0).ceil()
        ]);
        entry["nominal_atlas_state_crossings"] = json!([]);
        entry["state_intersection_status"] = json!("unassessed_no_physical_join_admitted");
        entry["remaining_gates"] = json!([
            "Recover whole-current endpoints and the other SEC branches.",
            "Replace schematic waypoints with dated, layer-compatible total-flow axes before physical dimensions.",
            "No annual range or seasonal playback is established by these two schematics."
        ]);
        let mut report = entry.clone();
        report["figure_aspect_ratio"] = json!(690.0 / 1060.0);
        report["source_citation"] = json!(
            "Stramma and Schott (1999), The mean flow field of the tropical Atlantic Ocean, Figure 4"
        );
        report["coordinate_selection"] = json!(
            "OSW rounded waypoints follow the labelled nSEC schematic between selected interior gates. These are not calibrated digitization or measured velocity cores."
        );
        report["scenario_rule"] = route["editorial_probe_interpretation"].clone();
        report["method"] = json!(
            "WGS84 shortest-geodesic segment sums. Gate and drawing variants remain separate from physical uncertainty."
        );
        report["map_land_check"] = json!(
            "All 54 drawing/gate variants clear both retained land masks under at-most-1 km geodesic sampling; geographic screening does not establish a physical current axis."
        );
        report["nasa_movie_context"] = json!([]);
        report["rendering_role"] =
            json!("derived_inline_editorial_reach_card_not_additional_observation");
        entry["report_inline"] = report;
        candidates.push(entry);
    }
    let plans = catalog["remaining_current_decisions"]
        .as_array_mut()
        .ok_or_else(fail)?;
    let matches = plans
        .iter()
        .enumerate()
        .filter(|(_, r)| r["current_id"] == CURRENT)
        .map(|(i, _)| i)
        .collect::<Vec<_>>();
    if matches.len() != 1 || plans[matches[0]] != doc["prior_decision"]["source_decision"] {
        return Err(fail());
    }
    plans[matches[0]] = doc["final_decision"]["source_decision"].clone();
    for (key, delta) in [
        ("route_candidates", 2),
        ("studied_reach_candidates", 2),
        ("currents_with_route_candidates", 1),
        ("currents_without_route_candidates", -1),
        ("currents_without_any_reference_card", -1),
    ] {
        let old = catalog["counts"][key].as_i64().ok_or_else(fail)?;
        catalog["counts"][key] = json!(
            old.checked_add(delta)
                .filter(|n| *n >= 0)
                .ok_or_else(fail)?
        );
    }
    let strategies = catalog["planning_taxonomy"]["strategies"]
        .as_array_mut()
        .ok_or_else(fail)?;
    let indices = strategies
        .iter()
        .enumerate()
        .filter(|(_, r)| r["id"] == doc["final_decision"]["strategy_id"])
        .map(|(i, _)| i)
        .collect::<Vec<_>>();
    if indices.len() != 1 {
        return Err(fail());
    }
    let strategy = &mut strategies[indices[0]];
    strategy["unbuilt_count"] = json!(
        strategy["unbuilt_count"]
            .as_u64()
            .and_then(|n| n.checked_sub(1))
            .ok_or_else(fail)?
    );
    Ok(catalog)
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> Bundle {
        let doc = document();
        let mut c = BTreeMap::new();
        c.insert("objects".into(), vec![doc["final_owner"].clone()]);
        c.insert("entities".into(), vec![doc["prior_entity"].clone()]);
        c.insert(
            "route_decisions".into(),
            vec![doc["final_decision"].clone()],
        );
        c.insert(
            "reference_routes".into(),
            additions("reference_routes").to_vec(),
        );
        c.insert(
            "sources".into(),
            doc["prior_owner_sources"]
                .as_array()
                .unwrap()
                .iter()
                .chain(additions("sources"))
                .cloned()
                .collect(),
        );
        for (name, key) in [
            ("widths", "prior_widths"),
            ("length_assessments", "prior_length_assessments"),
        ] {
            c.insert(name.into(), doc[key].as_array().unwrap().clone());
        }
        let mut manifest = json!({"input_sha256":doc["input_sha256"].clone()});
        manifest[KEY] = marker();
        manifest["input_sha256"][FILE] = json!(pin(RAW));
        Bundle {
            schema: "osw.query-bundle.v1".into(),
            collections: c,
            manifest,
        }
    }
    #[test]
    fn exact_references_preserve_prior_physical_evidence() {
        let b = fixture();
        validate(&b).unwrap();
        assert_eq!(
            additional_source_count(&b.collections, &b.manifest).unwrap(),
            2
        );
        assert_eq!(
            additional_reference_route_count(&b.collections, &b.manifest).unwrap(),
            2
        );
        assert_eq!(
            validated_reference_routes(&b).unwrap(),
            additions("reference_routes").to_vec()
        );
        assert_eq!(
            parent_object(&document()["final_owner"], &b.manifest),
            &document()["prior_owner"]
        );
        for r in &b.collections["reference_routes"] {
            assert_eq!(r["rank_eligible"], false);
            assert_eq!(r["physical_state_join_eligible"], false);
            assert!(r["annual_length_range_km"].is_null());
        }
    }
    #[test]
    fn partial_routes_physical_promotion_and_changed_parent_evidence_refused() {
        for case in 0..6 {
            let mut b = fixture();
            match case {
                0 => {
                    b.collections.get_mut("reference_routes").unwrap().pop();
                }
                1 => {
                    b.collections.get_mut("reference_routes").unwrap()[0]["rank_eligible"] =
                        json!(true)
                }
                2 => {
                    b.collections.get_mut("objects").unwrap()[0]["published_length_km"] =
                        json!(3900)
                }
                3 => {
                    b.collections.get_mut("reference_routes").unwrap()[0]["annual_length_range_km"] =
                        json!([3800, 4000])
                }
                4 => {
                    b.collections.get_mut("route_decisions").unwrap()[0]["candidate_count"] =
                        json!(1)
                }
                _ => {
                    b.collections.get_mut("widths").unwrap().pop();
                }
            }
            assert!(validate(&b).is_err(), "case {case}");
            assert!(additional_reference_route_count(&b.collections, &b.manifest).is_err());
            assert!(validated_reference_routes(&b).is_err());
        }
    }
    #[test]
    fn absent_marker_cannot_hide_new_routes() {
        let mut b = fixture();
        b.manifest = json!({});
        assert!(validate(&b).is_err());
    }
}
