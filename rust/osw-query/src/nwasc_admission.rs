//! A source-defined slope branch and separately scoped reports extend the base.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};

pub const FILE: &str = "research/norwegian-atlantic-slope-working-admission.json";
pub const RAW: &str =
    include_str!("../../../research/norwegian-atlantic-slope-working-admission.json");
pub const CATALOGUE: &str = "research/ocean-current-effective-catalogue.json";
pub const CATALOGUE_RAW: &str =
    include_str!("../../../research/ocean-current-effective-catalogue.json");
pub const EXPORT: &str = "research/ocean-current-live-measurements.json";
pub const EXPORT_RAW: &str = include_str!("../../../research/ocean-current-live-measurements.json");
pub const ENTITY: &str = "current:norwegian-atlantic-slope";
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
pub fn document() -> Value {
    serde_json::from_str(RAW).unwrap()
}
pub fn active(b: &Bundle) -> bool {
    b.manifest["nwasc_working_admission_version"].is_string()
        || b.manifest["input_sha256"][FILE].is_string()
        || b.collections
            .get("entities")
            .into_iter()
            .flatten()
            .any(|r| r["id"] == ENTITY)
        || b.collections
            .get("widths")
            .into_iter()
            .flatten()
            .any(|r| r["current_id"] == "norwegian-atlantic-slope")
}
pub fn rank_override(mut row: Value, b: &Bundle) -> Value {
    if active(b) {
        for update in document()["rank_updates"].as_array().unwrap() {
            if row["id"] == update["id"] {
                row["published_rank"] = update["working_rank"].clone();
            }
        }
    }
    row
}
pub fn recognizes_width(row: &Value) -> bool {
    document()["width_records"]
        .as_array()
        .unwrap()
        .contains(row)
}
pub fn widths(b: &Bundle) -> Vec<Value> {
    if active(b) {
        document()["width_records"].as_array().unwrap().clone()
    } else {
        vec![]
    }
}
pub fn identity_decision() -> Value {
    let doc = document();
    json!({"current_id":"norwegian-atlantic-slope","name":doc["entity"]["label"],
        "measurement_ids":doc["width_records"].as_array().unwrap().iter().map(|r|r["id"].clone()).collect::<Vec<_>>(),
        "status":"six_scoped_source_reports_admitted","whole_current_width_km":null,"annual_width_range_km":null,
        "admission_id":doc["identity_entry"]["id"]})
}
fn records() -> Vec<(&'static str, Value)> {
    let d = document();
    let mut rows = vec![
        ("entities", d["entity"].clone()),
        (
            "names",
            json!({"id":"name:current:norwegian-atlantic-slope","entity_id":ENTITY,
                       "label":d["entity"]["label"],"preferred":true,"source_id":"source:nwasc-baumann-2026"}),
        ),
        ("current_identity_admissions", d["identity_entry"].clone()),
        ("current_measurement_admissions", d.clone()),
        ("measurements", d["measurement"].clone()),
        ("claims", d["claim"].clone()),
    ];
    for (collection, key) in [("widths", "width_records"), ("sources", "source_records")] {
        rows.extend(
            d[key]
                .as_array()
                .unwrap()
                .iter()
                .map(|r| (collection, r.clone())),
        );
    }
    rows
}
pub fn validate(b: &Bundle) -> Result<(), String> {
    if !active(b) {
        return Ok(());
    }
    let doc = document();
    if b.manifest["nwasc_working_admission_version"] != "1" {
        return Err("Changed slope admission edition".into());
    }
    for (path, raw) in [
        (FILE, RAW),
        (CATALOGUE, CATALOGUE_RAW),
        (EXPORT, EXPORT_RAW),
    ] {
        if b.manifest["input_sha256"][path] != pin(raw) {
            return Err(format!("Changed slope admission receipt: {path}"));
        }
    }
    for raw in [RAW, CATALOGUE_RAW, EXPORT_RAW] {
        let d: Value = serde_json::from_str(raw).unwrap();
        for (p, h) in d["input_sha256"].as_object().unwrap() {
            if b.manifest["input_sha256"][p] != *h {
                return Err(format!("Changed slope admission dependency: {p}"));
            }
        }
    }
    for (collection, expected) in records() {
        let actual: Vec<_> = b
            .collections
            .get(collection)
            .into_iter()
            .flatten()
            .filter(|r| r["id"] == expected["id"])
            .collect();
        if actual != vec![&expected] {
            return Err(format!("Changed admitted slope-current {collection}"));
        }
    }
    if b.collections.get("length_assessments").map(|r| json!(r))
        != Some(doc["working_length_assessments"].clone())
    {
        return Err("Changed working length assessment or reported-length ranks".into());
    }
    if let Some(objects) = b.collections.get("objects") {
        let rows: Vec<_> = objects.iter().filter(|r| r["id"] == ENTITY).collect();
        if rows.len() != 1
            || rows[0]["capabilities"]["reported_length"] != 1
            || rows[0]["capabilities"]["scoped_width"] != 6
            || rows[0]["map_features"] != json!([])
            || rows[0]["published_length_km"] != 3500
            || !rows[0]["latest_observation_date"].is_null()
        {
            return Err("Changed slope-current object dimensions or unlocated geometry".into());
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> Bundle {
        let mut inputs = json!({});
        for raw in [RAW, CATALOGUE_RAW, EXPORT_RAW] {
            let d: Value = serde_json::from_str(raw).unwrap();
            for (p, h) in d["input_sha256"].as_object().unwrap() {
                inputs[p] = h.clone();
            }
        }
        for (p, raw) in [
            (FILE, RAW),
            (CATALOGUE, CATALOGUE_RAW),
            (EXPORT, EXPORT_RAW),
        ] {
            inputs[p] = json!(pin(raw));
        }
        let mut collections = std::collections::BTreeMap::new();
        for (name, row) in records() {
            collections
                .entry(name.into())
                .or_insert_with(Vec::new)
                .push(row);
        }
        collections.insert(
            "length_assessments".into(),
            document()["working_length_assessments"]
                .as_array()
                .unwrap()
                .clone(),
        );
        Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest: json!({"input_sha256":inputs,"nwasc_working_admission_version":"1"}),
            collections,
        }
    }
    #[test]
    fn migrated_regional_context_requires_an_exact_admitted_row() {
        let d = document();
        let row = d["width_records"]
            .as_array()
            .unwrap()
            .iter()
            .find(|r| !r["original_regional_context"].is_null())
            .unwrap();
        crate::original_regional_widths::validate(row).unwrap();
        for (key, value) in [
            ("current_id", json!("norwegian")),
            ("width_range_km", json!([20, 40])),
        ] {
            let mut bad = row.clone();
            bad[key] = value;
            assert!(!recognizes_width(&bad));
            assert!(crate::original_regional_widths::validate(&bad).is_err());
        }
    }
    #[test]
    fn accepts_scoped_reports() {
        validate(&fixture()).unwrap();
    }
    #[test]
    fn rejects_owner_layer_range_and_value_transfers() {
        for (collection, key, value) in [
            ("entities", "label", json!("Norwegian Current")),
            ("widths", "current_id", json!("norwegian")),
            ("widths", "approximate_width_km", json!(3500)),
            ("widths", "annual_width_range_km", json!([25, 50])),
            ("widths", "fixed_layer_bounds_m", json!([0, 900])),
            ("measurements", "value", json!(4000)),
            ("measurements", "source_id", json!("source:other")),
            (
                "measurements",
                "endpoint_coordinates_lon_lat",
                json!([[0, 60], [10, 80]]),
            ),
        ] {
            let mut b = fixture();
            b.collections.get_mut(collection).unwrap()[0][key] = value;
            assert!(validate(&b).is_err(), "{collection}/{key}");
        }
    }
    #[test]
    fn rejects_stripped_receipts_and_stale_ranks() {
        let mut b = fixture();
        b.manifest = json!({});
        assert!(validate(&b).is_err());
        let mut b = fixture();
        let rows = b.collections.get_mut("length_assessments").unwrap();
        let r = rows
            .iter_mut()
            .find(|r| r["entity_id"] == "current:southern-east-madagascar")
            .unwrap();
        r["published_rank"] = json!(12);
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections.get_mut("widths").unwrap().pop();
        assert!(validate(&b).is_err());
    }
}
