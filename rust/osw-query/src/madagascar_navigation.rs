//! Offshore experiment remains distinct from a named-current route.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
const FILE: &str = "research/southern-east-madagascar-route-definition-diagnostic.json";
const ID: &str = "diagnostic:southern-east-madagascar-route-definition";
const RAW: &str =
    include_str!("../../../research/southern-east-madagascar-route-definition-diagnostic.json");
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
fn document() -> Value {
    serde_json::from_str(RAW).unwrap()
}
fn record() -> Value {
    let doc = document();
    json!({"id":ID,"label":"Southern East Madagascar route definition: coastal rejection and offshore alternative",
    "entity_id":doc["entity_id"],"current_id":doc["current_id"],"status":doc["status"],"rank_eligible":false,
    "source_file":FILE,"source_file_sha256":pin(RAW),"source_json":RAW,"document":doc})
}
pub fn validate(bundle: &Bundle) -> Result<(), String> {
    let rows: Vec<_> = bundle
        .collections
        .get("diagnostics")
        .into_iter()
        .flatten()
        .filter(|r| r["id"] == ID || r["source_file"] == FILE)
        .collect();
    let active = bundle.manifest["madagascar_navigation_diagnostic_version"] == "1"
        || bundle.manifest["input_sha256"][FILE].is_string()
        || !rows.is_empty();
    if !active {
        return Ok(());
    }
    if bundle.manifest["madagascar_navigation_diagnostic_version"] != "1"
        || bundle.manifest["input_sha256"][FILE] != pin(RAW)
        || rows != vec![&record()]
    {
        return Err("Changed Madagascar route diagnostic or admission limits".into());
    }
    for (path, digest) in document()["input_sha256"].as_object().unwrap() {
        if bundle.manifest["input_sha256"][path] != *digest {
            return Err("Changed Madagascar route experiment dependency".into());
        }
    }
    for name in [
        "reference_routes",
        "measurements",
        "widths",
        "state_links",
        "geometry_frames",
    ] {
        if bundle
            .collections
            .get(name)
            .into_iter()
            .flatten()
            .any(|r| r["diagnostic_id"] == ID || r["source_file"] == FILE)
        {
            return Err(
                "Unadmitted navigation experiment promoted to current geometry or dimensions"
                    .into(),
            );
        }
    }
    Ok(())
}
#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> Bundle {
        let doc = document();
        let mut pins = doc["input_sha256"].clone();
        pins[FILE] = json!(pin(RAW));
        let mut collections = std::collections::BTreeMap::new();
        collections.insert("diagnostics".into(), vec![record()]);
        Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest: json!({"input_sha256":pins,"madagascar_navigation_diagnostic_version":"1"}),
            collections,
        }
    }
    #[test]
    fn rejects_removed_failed_cases_and_physical_promotions() {
        assert!(validate(&fixture()).is_ok());
        for (field, value) in [
            ("route_admitted", json!(true)),
            ("rank_eligible", json!(true)),
            ("annual_extrema_eligible", json!(true)),
            ("physical_current_axis_verified", json!(true)),
            ("published_reported_extent_km", json!(900)),
        ] {
            let mut b = fixture();
            b.collections.get_mut("diagnostics").unwrap()[0]["document"][field] = value;
            assert!(validate(&b).is_err(), "{field}");
        }
        let mut b = fixture();
        b.collections.get_mut("diagnostics").unwrap()[0]["document"]["rejected_v1"]["attempts"]
            .as_array_mut()
            .unwrap()
            .pop();
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections
            .insert("reference_routes".into(), vec![json!({"diagnostic_id":ID})]);
        assert!(validate(&b).is_err());
    }
    #[test]
    fn rejects_duplicate_and_erased_receipts_but_reads_prior_bundles() {
        let mut b = fixture();
        b.collections.get_mut("diagnostics").unwrap().push(record());
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
}
