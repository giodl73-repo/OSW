//! Separate source descriptions; no geographic envelope or length ranking.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
pub const FILE: &str = "research/agulhas-vinayachandran-2021-reported-dimensions.json";
pub const EXPORT: &str = "research/ocean-current-effective-measurements.json";
pub const ID: &str = "diagnostic:agulhas-vinayachandran-2021-reported-dimensions";
pub static RAW: &str =
    include_str!("../../../research/agulhas-vinayachandran-2021-reported-dimensions.json");
static EXPORT_RAW: &str =
    include_str!("../../../research/ocean-current-effective-measurements.json");
fn document() -> Value {
    serde_json::from_str(RAW).unwrap()
}
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
pub fn active(b: &Bundle) -> bool {
    b.manifest["agulhas_reported_dimensions_version"].is_string()
        || b.manifest["input_sha256"][FILE].is_string()
        || b.manifest["input_sha256"][EXPORT].is_string()
        || b.collections
            .get("widths")
            .into_iter()
            .flatten()
            .any(|r| r["id"] == "agulhas-vinayachandran-2021-typical-core-description")
        || b.collections
            .get("diagnostics")
            .into_iter()
            .flatten()
            .any(|r| r["id"] == ID)
}
pub fn widths(b: &Bundle) -> Vec<Value> {
    if active(b) {
        vec![document()["width_record"].clone()]
    } else {
        vec![]
    }
}
fn diagnostic() -> Value {
    json!({"id":ID,"label":"Agulhas source-reported coastal extent and typical core description",
        "entity_id":"current:agulhas","current_id":"agulhas","rank_eligible":false,"source_file":FILE,
        "source_file_sha256":pin(RAW),"source_json":RAW,"summary":{"reported_coastal_extent_km":1000,
        "reported_typical_core_width_km":200,"independent_observation":false,"annual_range_km":null,
        "geographic_edges":null,"whole_current_length_rank_admitted":false}})
}
pub fn validate(b: &Bundle) -> Result<(), String> {
    if !active(b) {
        return Ok(());
    }
    let doc = document();
    if b.manifest["agulhas_reported_dimensions_version"] != "1"
        || b.manifest["input_sha256"][FILE] != pin(RAW)
        || b.manifest["input_sha256"][EXPORT] != pin(EXPORT_RAW)
    {
        return Err("Changed Agulhas reported edition/pins".into());
    }
    for (p, sha) in doc["input_sha256"].as_object().unwrap() {
        if b.manifest["input_sha256"][p] != *sha {
            return Err(format!("Changed Agulhas reported dependency:{p}"));
        }
    }
    for (collection, expected) in [
        ("widths", doc["width_record"].clone()),
        ("sources", doc["source_record"].clone()),
        ("diagnostics", diagnostic()),
    ] {
        let rows: Vec<_> = b
            .collections
            .get(collection)
            .into_iter()
            .flatten()
            .filter(|r| r["id"] == expected["id"])
            .collect();
        if rows != vec![&expected] {
            return Err(format!("Changed Agulhas reported {collection}"));
        }
    }
    let owners: Vec<_> = b
        .collections
        .get("objects")
        .into_iter()
        .flatten()
        .filter(|r| r["id"] == "current:agulhas")
        .collect();
    if owners.len() != 1
        || owners[0]["capabilities"]["scoped_width"] != 2
        || !owners[0]["diagnostic_ids"]
            .as_array()
            .is_some_and(|a| a.contains(&json!(ID)))
        || !owners[0]["source_ids"]
            .as_array()
            .is_some_and(|a| a.contains(&doc["source_record"]["id"]))
        || !owners[0]["published_length_km"].is_null()
    {
        return Err("Changed Agulhas reported owner/scope".into());
    }
    let assessments: Vec<_> = b
        .collections
        .get("length_assessments")
        .into_iter()
        .flatten()
        .filter(|r| r["entity_id"] == "current:agulhas")
        .collect();
    if assessments.len() != 1
        || assessments[0]["rank_eligible"] != false
        || !assessments[0]["published_length_km"].is_null()
    {
        return Err("Agulhas variant promoted into whole-length rank".into());
    }
    Ok(())
}
pub fn scene(b: &Bundle) -> Value {
    if !active(b) {
        return Value::Null;
    }
    let doc = document();
    json!({"kind":"agulhas_reported_dimensions","current_id":"agulhas","diagnostic_id":ID,
        "source_file":FILE,"source_url":doc["source_url"],"figure_file":doc["figure_file"],
        "length_variant":doc["length_variant"],"width_record":doc["width_record"],
        "original_pdf":"research/source-data/vinayachandran-indian-upwelling-2021/article.pdf",
        "source_license":"CC BY 4.0","effective_measurements_file":EXPORT})
}
pub fn query(rows: &[&Value], b: &Bundle) -> Value {
    if rows.len() == 1 && rows[0]["id"] == ID {
        scene(b)
    } else {
        Value::Null
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> Bundle {
        let d = document();
        let mut pins = d["input_sha256"].clone();
        pins[FILE] = json!(pin(RAW));
        pins[EXPORT] = json!(pin(EXPORT_RAW));
        serde_json::from_value(json!({"schema":"osw.query-bundle.v1","manifest":{"agulhas_reported_dimensions_version":"1","input_sha256":pins},
            "collections":{"widths":[d["width_record"]],"sources":[d["source_record"]],"diagnostics":[diagnostic()],
            "objects":[{"id":"current:agulhas","capabilities":{"scoped_width":2},"diagnostic_ids":[ID],"source_ids":[d["source_record"]["id"]],"published_length_km":null}],
            "length_assessments":[{"entity_id":"current:agulhas","rank_eligible":false,"published_length_km":null}]}})).unwrap()
    }
    #[test]
    fn source_description_and_unknowns_are_bound() {
        validate(&fixture()).unwrap();
        for (k, v) in [
            ("approximate_width_km", json!(219)),
            ("width_range_km", json!([200, 219])),
            ("observed_period", json!("2021-11")),
            ("fixed_layer_bounds_m", json!([0, 2000])),
            ("seasonal_playback_eligible", json!(true)),
        ] {
            let mut b = fixture();
            b.collections.get_mut("widths").unwrap()[0][k] = v;
            assert!(validate(&b).is_err(), "{k}");
        }
    }
    #[test]
    fn source_owner_and_variant_cannot_be_promoted_or_erased() {
        let mut b = fixture();
        b.collections.get_mut("length_assessments").unwrap()[0]["rank_eligible"] = json!(true);
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections.get_mut("objects").unwrap()[0]["diagnostic_ids"] = json!([]);
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections.get_mut("sources").unwrap()[0]["provider_asset_redistributed"] = json!(false);
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections.get_mut("widths").unwrap().clear();
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections.get_mut("diagnostics").unwrap()[0]["source_json"] = json!("{}");
        assert!(validate(&b).is_err());
    }
    #[test]
    fn old_snapshots_are_optional_partial_editions_are_rejected() {
        let old: Bundle = serde_json::from_value(
            json!({"schema":"osw.query-bundle.v1","manifest":{},"collections":{}}),
        )
        .unwrap();
        assert!(validate(&old).is_ok());
        let mut b = fixture();
        b.manifest
            .as_object_mut()
            .unwrap()
            .remove("agulhas_reported_dimensions_version");
        assert!(validate(&b).is_err());
    }
}
