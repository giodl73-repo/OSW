//! Source-reference connection with fixed anchors, not an observed current axis.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
pub const FILE: &str = "research/nwasc-source-anchor-reference-route.json";
pub const INPUT: &str = "research/nwasc-source-anchor-reference-route-input.json";
pub const RAW: &str = include_str!("../../../research/nwasc-source-anchor-reference-route.json");
pub const ROUTE: &str = "norwegian-atlantic-slope-asar-regional-reference-route";
pub const OWNER: &str = "current:norwegian-atlantic-slope";
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
pub fn document() -> Value {
    serde_json::from_str(RAW).unwrap()
}
pub fn active_manifest(m: &Value) -> bool {
    m["nwasc_reference_route_version"] == "1" || m["input_sha256"][FILE].is_string()
}
pub fn active(b: &Bundle) -> bool {
    active_manifest(&b.manifest)
        || b.collections
            .get("reference_routes")
            .into_iter()
            .flatten()
            .any(|r| r["id"] == ROUTE)
}
pub fn route() -> Value {
    let mut row = document()["route_record"].clone();
    row["candidate_sha256"] = json!(pin(RAW));
    row
}
pub fn extend_routes(mut rows: Vec<Value>, b: &Bundle) -> Vec<Value> {
    if active(b) {
        let r = route();
        let length = r["approximate_reference_path_km"].as_f64().unwrap();
        let position = rows
            .iter()
            .position(|r| r["approximate_reference_path_km"].as_f64().unwrap() < length)
            .unwrap_or(rows.len());
        rows.insert(position, r);
    }
    rows
}
pub fn catalogue(b: &Bundle) -> Value {
    let mut cat = crate::madagascar_coastal_curve::catalogue();
    if !active(b) {
        return cat;
    }
    let d = document();
    cat["candidates"] = json!(extend_routes(
        cat["candidates"].as_array().unwrap().clone(),
        b
    ));
    cat["remaining_current_decisions"]
        .as_array_mut()
        .unwrap()
        .push(d["planning_decision"].clone());
    let scope = cat["working_scope"].as_str().unwrap().to_owned();
    cat["working_scope"] = json!(
        scope
            + " Includes one source-anchor NwASC regional connection; no whole-current axis inferred."
    );
    cat["working_catalogue_version"] = json!("0.4.0-draft-source-anchor-route");
    for (k, v) in [
        ("route_candidates", 78),
        ("currents_with_route_candidates", 72),
        ("accepted_current_names", 102),
        ("currents_without_any_reference_card", 30),
        ("source_anchor_connection_candidates", 1),
        ("route_decision_records", 91),
    ] {
        cat["counts"][k] = json!(v);
    }
    cat["effective_accepted_current_count"] = json!(102);
    for s in cat["planning_taxonomy"]["strategies"]
        .as_array_mut()
        .unwrap()
    {
        if s["id"] == d["planning_decision"]["route_strategy_id"] {
            s["current_count"] = json!(s["current_count"].as_u64().unwrap() + 1);
        }
    }
    cat
}
pub fn validate(b: &Bundle) -> Result<(), String> {
    if !active(b) {
        return Ok(());
    }
    let d = document();
    if b.manifest["nwasc_reference_route_version"] != "1"
        || b.manifest["input_sha256"][FILE] != pin(RAW)
        || b.manifest["input_sha256"][INPUT] != d["input_sha256"]
    {
        return Err("Missing/changed NwASC reference-route edition/receipt".into());
    }
    for (path, sha) in d["input_dependencies_sha256"].as_object().unwrap() {
        if b.manifest["input_sha256"][path] != *sha {
            return Err(format!("Changed NwASC route dependency:{path}"));
        }
    }
    let mut expected = extend_routes(
        crate::madagascar_coastal_curve::catalogue()["candidates"]
            .as_array()
            .unwrap()
            .clone(),
        b,
    );
    expected.extend(crate::planning::eicc_reference_routes(
        &b.collections,
        &b.manifest,
    )?);
    if b.collections.get("reference_routes") != Some(&expected) {
        return Err("Changed source-reference route or previous route inventory".into());
    }
    let methods: Vec<_> = b
        .collections
        .get("sources")
        .into_iter()
        .flatten()
        .filter(|r| r["id"] == d["method_source"]["id"])
        .collect();
    if methods != vec![&d["method_source"]] {
        return Err("Changed NwASC reference-route method source".into());
    }
    let owners: Vec<_> = b
        .collections
        .get("objects")
        .into_iter()
        .flatten()
        .filter(|r| r["id"] == OWNER)
        .collect();
    if owners.len() != 1 {
        return Err("Missing NwASC reference owner".into());
    }
    let o = owners[0];
    let features = o["map_features"]
        .as_array()
        .ok_or("Missing source-anchor map feature")?;
    if features.len() != 1
        || o["route_ids"] != json!([ROUTE])
        || o["capabilities"]["reference_route"] != 1
        || !o["latest_observation_date"].is_null()
    {
        return Err("Changed NwASC reference-route owner scope".into());
    }
    let f = &features[0];
    if f["candidate_id"] != ROUTE
        || f["role"] != "editorial_reference_route"
        || f["geometry"] != d["route_record"]["geometry"]
        || f["spatial_geometry"] != d["canonical_spatial_geometry"]
        || !f["observation_date"].is_null()
        || !f["frame_id"].is_null()
        || f["physical_state_join_eligible"] != false
        || f["physical_current_axis_admitted"] != false
    {
        return Err(
            "Source-reference line promoted to physical/different/dateranged current geometry"
                .into(),
        );
    }
    for id in d["route_record"]["source_ids"].as_array().unwrap() {
        if !o["source_ids"].as_array().is_some_and(|a| a.contains(id)) {
            return Err("Missing reference-route source join".into());
        }
    }
    Ok(())
}
#[cfg(test)]
pub(crate) mod tests {
    use super::*;
    fn fixture() -> Bundle {
        let d = document();
        let mut pins = d["input_dependencies_sha256"].clone();
        pins[FILE] = json!(pin(RAW));
        let mut b:Bundle=serde_json::from_value(json!({"schema":"osw.query-bundle.v1",
            "manifest":{"nwasc_reference_route_version":"1","input_sha256":pins},
            "collections":{"sources":[d["method_source"]],"objects":[{"id":OWNER,"route_ids":[ROUTE],
                "capabilities":{"reference_route":1},"source_ids":d["route_record"]["source_ids"],
                "map_features":[{"candidate_id":ROUTE,"role":"editorial_reference_route","geometry":d["route_record"]["geometry"],
                    "spatial_geometry":d["canonical_spatial_geometry"],"physical_state_join_eligible":false,"physical_current_axis_admitted":false}]}]}})).unwrap();
        let rows = extend_routes(
            crate::madagascar_coastal_curve::catalogue()["candidates"]
                .as_array()
                .unwrap()
                .clone(),
            &b,
        );
        b.collections.insert("reference_routes".into(), rows);
        b
    }
    // Combine small source-bound fixtures; never load the installed packet.
    pub(crate) fn eicc_fixture() -> Bundle {
        let mut combined = fixture();
        for addition in [
            crate::madagascar_coastal_curve::tests::fixture(),
            crate::planning::tests::revised_fixture(),
        ] {
            for (key, value) in addition.manifest.as_object().unwrap() {
                if key == "input_sha256" {
                    for (path, digest) in value.as_object().unwrap() {
                        if let Some(existing) = combined.manifest[key].get(path) {
                            assert_eq!(existing, digest, "conflicting source receipt: {path}");
                        } else {
                            combined.manifest[key][path] = digest.clone();
                        }
                    }
                } else if let Some(existing) = combined.manifest.get(key) {
                    assert_eq!(existing, value, "conflicting manifest field: {key}");
                } else {
                    combined.manifest[key] = value.clone();
                }
            }
            for (name, rows) in addition.collections {
                let target = combined.collections.entry(name.clone()).or_default();
                for row in rows {
                    if let Some(existing) = target.iter().find(|existing| existing["id"] == row["id"]) {
                        assert_eq!(existing, &row, "conflicting {name} row: {}", row["id"]);
                    } else {
                        target.push(row);
                    }
                }
            }
        }
        assert_eq!(combined.collections["reference_routes"].len(), 80);
        let previous = fixture();
        assert_eq!(&combined.collections["reference_routes"][..78], previous.collections["reference_routes"].as_slice());
        combined
    }
    #[test]
    fn eicc_extension_preserves_nwasc_and_rejects_duplicates_and_bad_receipts() {
        let b = eicc_fixture();
        validate(&b).unwrap();
        crate::planning::validate(&b.collections, &b.manifest).unwrap();
        crate::current_gap_admissions::validate(&b).unwrap();
        let mut duplicate = eicc_fixture();
        let row = duplicate.collections["reference_routes"][78].clone();
        duplicate.collections.get_mut("reference_routes").unwrap().push(row);
        assert!(validate(&duplicate).is_err());
        let mut missing = eicc_fixture();
        missing.collections.get_mut("reference_routes").unwrap().pop();
        assert!(validate(&missing).is_err());
        let mut bad_receipt = eicc_fixture();
        bad_receipt.manifest["eicc_reference_spectral_delivery_v1"]["planning_revision"]["query_contract_sha256"] = json!("0".repeat(64));
        assert!(validate(&bad_receipt).is_err());
        let mut changed = eicc_fixture();
        changed.collections.get_mut("reference_routes").unwrap()[0]["approximate_reference_path_km"] = json!(999);
        assert!(validate(&changed).is_err());
    }
    #[test]
    fn accepts_regional_reference_and_preserved_projection() {
        validate(&fixture()).unwrap();
        assert_eq!(catalogue(&fixture())["counts"]["route_candidates"], 78);
    }
    #[test]
    fn rejects_altered_anchors_role_date_and_physical_join() {
        for (key, value) in [
            ("role", json!("observed_current_axis")),
            ("observation_date", json!("2010-07-01")),
            ("frame_id", json!("season:summer")),
            ("physical_state_join_eligible", json!(true)),
            (
                "geometry",
                json!({"type":"LineString","coordinates":[[0.5,62],[3,62.666666666666664],[4.25,62.8]]}),
            ),
        ] {
            let mut b = fixture();
            b.collections.get_mut("objects").unwrap()[0]["map_features"][0][key] = value;
            assert!(validate(&b).is_err(), "{key}");
        }
    }
    #[test]
    fn rejects_previous_route_edits_and_stripped_receipts() {
        let mut b = fixture();
        b.collections.get_mut("reference_routes").unwrap()[0]["approximate_reference_path_km"] =
            json!(999);
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.manifest = json!({});
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections.get_mut("objects").unwrap()[0]["source_ids"] = json!([]);
        assert!(validate(&b).is_err());
    }
}
