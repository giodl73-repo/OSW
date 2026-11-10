//! Geographic coast offsets are atlas references, not measured current axes.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
pub const FILE: &str = "research/southern-east-madagascar-coastal-reference-curve.json";
pub const CATALOGUE: &str = "research/ocean-current-working-reference-routes.json";
const COAST: &str = "research/madagascar-coastline-comparison.json";
const DIAGNOSTIC: &str = "diagnostic:madagascar-coastline-comparison";
const ROUTE: &str = "southern-east-madagascar-coastal-reference-curve";
pub const RAW: &str =
    include_str!("../../../research/southern-east-madagascar-coastal-reference-curve.json");
pub const CATALOGUE_RAW: &str =
    include_str!("../../../research/ocean-current-working-reference-routes.json");
pub const COAST_RAW: &str = include_str!("../../../research/madagascar-coastline-comparison.json");
pub const JOIN: &str = "research/ocean-current-working-reference-route-state-join.json";
pub const JOIN_RAW: &str =
    include_str!("../../../research/ocean-current-working-reference-route-state-join.json");
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
pub fn document() -> Value {
    serde_json::from_str(RAW).unwrap()
}
pub fn catalogue() -> Value {
    serde_json::from_str(CATALOGUE_RAW).unwrap()
}
pub fn active_manifest(manifest: &Value) -> bool {
    manifest["madagascar_coastal_curve_version"] == "1"
        || manifest["input_sha256"][FILE].is_string()
        || manifest["input_sha256"][CATALOGUE].is_string()
}
pub fn active(bundle: &Bundle) -> bool {
    active_manifest(&bundle.manifest)
        || bundle
            .collections
            .get("reference_routes")
            .into_iter()
            .flatten()
            .any(|r| r["id"] == ROUTE)
        || bundle
            .collections
            .get("diagnostics")
            .into_iter()
            .flatten()
            .any(|r| r["id"] == DIAGNOSTIC)
}
pub fn planning_source() -> Value {
    catalogue()["remaining_current_decisions"]
        .as_array()
        .unwrap()
        .iter()
        .find(|r| r["current_id"] == "southern-east-madagascar")
        .unwrap()
        .clone()
}
fn diagnostic() -> Value {
    let doc: Value = serde_json::from_str(COAST_RAW).unwrap();
    json!({"id":DIAGNOSTIC,"label":"Madagascar: land-mask support comparison for54 unchanged route scenarios",
        "entity_id":doc["entity_id"],"current_id":doc["current_id"],"status":doc["status"],"rank_eligible":false,
        "source_file":COAST,"source_file_sha256":pin(COAST_RAW),"source_json":COAST_RAW,"document":doc})
}
pub fn validate(bundle: &Bundle) -> Result<(), String> {
    if !active(bundle) {
        return Ok(());
    }
    if bundle.manifest["madagascar_coastal_curve_version"] != "1" {
        return Err("Missing coastal reference curve edition".into());
    }
    for (path, raw) in [
        (FILE, RAW),
        (CATALOGUE, CATALOGUE_RAW),
        (COAST, COAST_RAW),
        (JOIN, JOIN_RAW),
    ] {
        if bundle.manifest["input_sha256"][path] != pin(raw) {
            return Err("Changed coastal reference source receipt".into());
        }
    }
    let doc = document();
    let cat = catalogue();
    let coast: Value = serde_json::from_str(COAST_RAW).unwrap();
    let join: Value = serde_json::from_str(JOIN_RAW).unwrap();
    for pins in [
        &doc["input_dependencies_sha256"],
        &cat["working_input_sha256"],
        &coast["input_sha256"],
        &join["input_sha256"],
    ] {
        for (path, digest) in pins.as_object().unwrap() {
            if bundle.manifest["input_sha256"][path] != *digest {
                return Err("Changed coastal reference dependency".into());
            }
        }
    }
    let mut expected = crate::nwasc_reference_route::extend_routes(
        cat["candidates"].as_array().unwrap().clone(),
        bundle,
    );
    expected.extend(crate::planning::eicc_reference_routes(
        &bundle.collections,
        &bundle.manifest,
    )?);
    expected.extend(crate::pacific_secc_reference::routes(&bundle.collections, &bundle.manifest)?);
    expected.extend(crate::south_java_reference::routes(&bundle.collections, &bundle.manifest)?);
    expected.extend(crate::wicc_winter_reference::routes(&bundle.collections, &bundle.manifest)?);
    if bundle.collections.get("reference_routes") != Some(&expected) {
        return Err("Changed working route catalogue projection".into());
    }
    for (name, expected) in [
        ("sources", cat["land_source_record"].clone()),
        ("sources", cat["primary_source_record"].clone()),
        ("diagnostics", diagnostic()),
    ] {
        let rows: Vec<_> = bundle
            .collections
            .get(name)
            .into_iter()
            .flatten()
            .filter(|r| r["id"] == expected["id"])
            .collect();
        if rows != vec![&expected] {
            return Err(format!("Changed coast reference {name} record"));
        }
    }
    if let Some(owner) = bundle
        .collections
        .get("objects")
        .into_iter()
        .flatten()
        .find(|r| r["id"] == "current:southern-east-madagascar")
    {
        let features = owner["map_features"]
            .as_array()
            .ok_or("Missing coastal reference map feature")?;
        let route = cat["candidates"]
            .as_array()
            .unwrap()
            .iter()
            .find(|r| r["id"] == ROUTE)
            .unwrap();
        if owner["route_ids"] != json!([ROUTE])
            || features.len() != 1
            || features[0]["geometry"]["coordinates"] != doc["coordinates_lon_lat"]
            || features[0]["role"] != "editorial_reference_route"
            || !features[0]["observation_date"].is_null()
            || !features[0]["frame_id"].is_null()
            || !owner["latest_observation_date"].is_null()
            || owner["source_ids"] != route["source_ids"]
        {
            return Err("Coastal reference promoted or rebound to a dated physical axis".into());
        }
        let links: Vec<_> = bundle
            .collections
            .get("state_links")
            .into_iter()
            .flatten()
            .filter(|r| r["entity_id"] == owner["id"])
            .collect();
        if links.len()
            != doc["nominal_atlas_state_crossings"]
                .as_array()
                .unwrap()
                .len()
            || links.iter().any(|r| {
                r["source_file"] != FILE
                    || r["kind"] != "editorial_coastal_reference_curve"
                    || !r["observation_date"].is_null()
                    || !doc["nominal_atlas_state_crossings"]
                        .as_array()
                        .unwrap()
                        .contains(&r["state_code"])
            })
        {
            return Err("Changed coastal reference navigation-state relation".into());
        }
    }
    for name in ["measurements", "widths", "geometry_frames"] {
        if bundle
            .collections
            .get(name)
            .into_iter()
            .flatten()
            .any(|r| r["source_file"] == FILE || r["diagnostic_id"] == DIAGNOSTIC)
        {
            return Err(
                "Coast offsets promoted to physical dimensions or seasonal geometry".into(),
            );
        }
    }
    Ok(())
}
#[cfg(test)]
pub(crate) mod tests {
    use super::*;
    pub(crate) fn fixture() -> Bundle {
        let doc = document();
        let cat = catalogue();
        let coast: Value = serde_json::from_str(COAST_RAW).unwrap();
        let join: Value = serde_json::from_str(JOIN_RAW).unwrap();
        let mut pins = json!({});
        for group in [
            &doc["input_dependencies_sha256"],
            &cat["working_input_sha256"],
            &coast["input_sha256"],
            &join["input_sha256"],
        ] {
            for (k, v) in group.as_object().unwrap() {
                pins[k] = v.clone()
            }
        }
        for (path, raw) in [
            (FILE, RAW),
            (CATALOGUE, CATALOGUE_RAW),
            (COAST, COAST_RAW),
            (JOIN, JOIN_RAW),
        ] {
            pins[path] = json!(pin(raw))
        }
        let mut collections = std::collections::BTreeMap::new();
        collections.insert(
            "reference_routes".into(),
            cat["candidates"].as_array().unwrap().clone(),
        );
        collections.insert("diagnostics".into(), vec![diagnostic()]);
        collections.insert(
            "sources".into(),
            vec![
                cat["land_source_record"].clone(),
                cat["primary_source_record"].clone(),
            ],
        );
        Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest: json!({"madagascar_coastal_curve_version":"1","input_sha256":pins}),
            collections,
        }
    }
    #[test]
    fn eicc_extension_preserves_coastal_catalogue_and_rejects_route_changes() {
        let b = crate::nwasc_reference_route::tests::eicc_fixture();
        validate(&b).unwrap();
        for index in [0, 78, 79] {
            let mut changed = crate::nwasc_reference_route::tests::eicc_fixture();
            changed.collections.get_mut("reference_routes").unwrap()[index]["rank_eligible"] = json!(true);
            assert!(validate(&changed).is_err(), "route index {index}");
        }
        let mut missing = crate::nwasc_reference_route::tests::eicc_fixture();
        missing.collections.get_mut("reference_routes").unwrap().remove(0);
        assert!(validate(&missing).is_err());
    }
    #[test]
    fn rejects_catalogue_omission_changed_coast_and_physical_promotions() {
        assert!(validate(&fixture()).is_ok());
        let mut b = fixture();
        b.collections.get_mut("reference_routes").unwrap().pop();
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections.get_mut("diagnostics").unwrap()[0]["document"]["results"]["coastal_v1"]["natural_earth_land_contacts"] =
            json!(0);
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections.insert(
            "widths".into(),
            vec![json!({"diagnostic_id":DIAGNOSTIC,"approximate_width_km":25})],
        );
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.manifest["input_sha256"]["research/source-data/natural-earth-land-10m-5.1.1/ne_10m_land.zip"] =
            json!("0".repeat(64));
        assert!(validate(&b).is_err());
    }
    #[test]
    fn retains_legacy_bundles_but_rejects_duplicate_and_coherent_erasure() {
        let mut b = fixture();
        b.collections
            .get_mut("diagnostics")
            .unwrap()
            .push(diagnostic());
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections.clear();
        b.manifest["input_sha256"]
            .as_object_mut()
            .unwrap()
            .remove(FILE);
        assert!(validate(&b).is_err());
        b.manifest = json!({});
        assert!(validate(&b).is_ok());
    }
    #[test]
    fn new_map_and_state_placement_remain_undated_geographic_evidence() {
        let mut b = fixture();
        b.collections.insert("objects".into(),vec![json!({"id":"current:southern-east-madagascar","route_ids":[ROUTE],
            "source_ids":catalogue()["candidates"].as_array().unwrap().iter().find(|r|r["id"]==ROUTE).unwrap()["source_ids"],
            "map_features":[{"geometry":{"type":"LineString","coordinates":document()["coordinates_lon_lat"]},"role":"editorial_reference_route"}],"latest_observation_date":null})]);
        b.collections.insert("state_links".into(),vec![json!({"entity_id":"current:southern-east-madagascar","state_code":"EAFR","source_file":FILE,"kind":"editorial_coastal_reference_curve","observation_date":null})]);
        assert!(validate(&b).is_ok());
        let mut bad = Bundle {
            schema: b.schema.clone(),
            manifest: b.manifest.clone(),
            collections: b.collections.clone(),
        };
        bad.collections.get_mut("objects").unwrap()[0]["map_features"][0]["observation_date"] =
            json!("2001-04-01");
        assert!(validate(&bad).is_err());
        b.collections.get_mut("state_links").unwrap()[0]["kind"] = json!("observed_center_point");
        assert!(validate(&b).is_err());
    }
}
