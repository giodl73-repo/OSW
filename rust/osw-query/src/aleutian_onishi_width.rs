//! A strict author-reported width lower constraint, not a finite mean.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
pub const FILE: &str = "research/aleutian-onishi-2001-width-admission.json";
pub const EXPORT: &str = "research/ocean-current-measurements-aleutian-edition.json";
const CONTRACT: &str = "research/aleutian-onishi-2001-width-contract.json";
pub const RAW: &str = include_str!("../../../research/aleutian-onishi-2001-width-admission.json");
const CONTRACT_RAW: &str =
    include_str!("../../../research/aleutian-onishi-2001-width-contract.json");
const ID: &str = "diagnostic:aleutian-onishi-2001-width-constraint";
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
fn document() -> Value {
    serde_json::from_str(RAW).unwrap()
}
pub fn active(b: &Bundle) -> bool {
    b.manifest["aleutian_onishi_width_version"].is_string()
        || b.manifest["input_sha256"][FILE].is_string()
        || b.collections.values().flatten().any(|r| {
            r["id"] == ID
                || r["id"] == "source:aleutian-onishi-2001"
                || r["id"]
                    .as_str()
                    .is_some_and(|s| s.starts_with("aleutian-onishi-2001-"))
        })
}
pub fn widths(b: &Bundle) -> Vec<Value> {
    if active(b) {
        document()["width_records"].as_array().unwrap().clone()
    } else {
        vec![]
    }
}
fn diagnostic() -> Value {
    json!({"id":ID,"label":"Aleutian published width: strict regional lower constraint","entity_id":"current:aleutian","current_id":"aleutian","rank_eligible":false,
        "source_file":FILE,"source_file_sha256":pin(RAW),"source_json":RAW,
        "summary":{"source_constraint":">400 km","finite_width_km":null,"annual_width_range_km":null,"width_layer":null,"width_epoch":null,"source_field_reproduction":false}})
}
pub fn validate(b: &Bundle) -> Result<(), String> {
    if !active(b) {
        return Ok(());
    }
    if b.manifest["aleutian_onishi_width_version"] != "1" {
        return Err("Changed Aleutian width admission edition".into());
    }
    let d = document();
    let c: Value = serde_json::from_str(CONTRACT_RAW).unwrap();
    for (p, raw) in [(FILE, RAW), (CONTRACT, CONTRACT_RAW)] {
        if b.manifest["input_sha256"][p] != pin(raw) {
            return Err(format!("Changed Aleutian receipt:{p}"));
        }
    }
    if c["report_file"] != FILE
        || c["report_sha256"] != pin(RAW)
        || c["export_file"] != EXPORT
        || b.manifest["input_sha256"][EXPORT] != c["export_sha256"]
        || c["previous_export_file"] != crate::neuc_glider_widths::EXPORT
        || c["previous_export_sha256"] != pin(crate::neuc_glider_widths::EXPORT_RAW)
        || b.manifest["input_sha256"][crate::neuc_glider_widths::EXPORT]
            != c["previous_export_sha256"]
    {
        return Err("Changed Aleutian thin export contract".into());
    }
    for (p, sha) in d["input_sha256"].as_object().unwrap() {
        if b.manifest["input_sha256"][p] != *sha {
            return Err(format!("Changed Aleutian dependency:{p}"));
        }
    }
    let previous: Value = serde_json::from_str(crate::neuc_glider_widths::EXPORT_RAW).unwrap();
    let mut expected = previous["widths"].as_array().unwrap().clone();
    expected.extend(widths(b));
    if b.collections.get("widths") != Some(&expected)
        || b.collections.get("length_assessments") != previous["length_assessments"].as_array()
    {
        return Err("Aleutian constraint changed prior widths or length evidence".into());
    }
    for (collection, row) in [
        ("widths", d["width_records"][0].clone()),
        ("sources", d["source_record"].clone()),
        ("diagnostics", diagnostic()),
    ] {
        let actual: Vec<_> = b
            .collections
            .get(collection)
            .into_iter()
            .flatten()
            .filter(|r| r["id"] == row["id"])
            .collect();
        if actual != vec![&row] {
            return Err(format!("Changed Aleutian scoped {collection}"));
        }
    }
    if let Some(objects) = b.collections.get("objects") {
        let owners: Vec<_> = objects
            .iter()
            .filter(|r| r["id"] == "current:aleutian")
            .collect();
        if owners.len() != 1
            || owners[0]["capabilities"]["scoped_width"] != 1
            || !owners[0]["source_ids"]
                .as_array()
                .is_some_and(|a| a.contains(&d["source_record"]["id"]))
            || !owners[0]["diagnostic_ids"]
                .as_array()
                .is_some_and(|a| a.contains(&json!(ID)))
        {
            return Err("Missing Aleutian constraint owner/source/diagnostic join".into());
        }
    }
    Ok(())
}
pub fn query(rows: &[&Value], b: &Bundle) -> Value {
    if !active(b)
        || !rows
            .iter()
            .any(|r| r["id"] == ID || r["id"] == "aleutian-onishi-2001-published-width-constraint")
    {
        return Value::Null;
    }
    let d = document();
    json!({"kind":"aleutian_published_width_constraint","source_file":FILE,"source_url":d["source_url"],"archive_url":d["source_record"]["source_url"],
        "figure_file":d["figure_file"],"effective_measurements_file":EXPORT,"width_record":d["width_records"][0],
        "scope":"Onishi2001 introductory regional description of the eastward Subarctic/Aleutian Current: strict width>400km. Width epoch, layer, numeric edges and upper extent unspecified. Study180E/1990-1998/3000m reference are not width support. No finite mean, annual range, new geometry, physical state passage or seasonal playback."})
}
#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> Bundle {
        let d = document();
        let c: Value = serde_json::from_str(CONTRACT_RAW).unwrap();
        let e: Value = serde_json::from_str(crate::neuc_glider_widths::EXPORT_RAW).unwrap();
        let mut pins = d["input_sha256"].clone();
        pins[FILE] = json!(pin(RAW));
        pins[CONTRACT] = json!(pin(CONTRACT_RAW));
        pins[EXPORT] = c["export_sha256"].clone();
        pins[crate::neuc_glider_widths::EXPORT] = c["previous_export_sha256"].clone();
        let mut ws = e["widths"].as_array().unwrap().clone();
        ws.extend(d["width_records"].as_array().unwrap().clone());
        serde_json::from_value(json!({"schema":"osw.query-bundle.v1","manifest":{"aleutian_onishi_width_version":"1","input_sha256":pins},
            "collections":{"widths":ws,"length_assessments":e["length_assessments"],"sources":[d["source_record"]],"diagnostics":[diagnostic()],
                "objects":[{"id":"current:aleutian","capabilities":{"scoped_width":1},"source_ids":[d["source_record"]["id"]],"diagnostic_ids":[ID]}]}})).unwrap()
    }
    #[test]
    fn strict_lower_constraint_keeps_unspecified_support() {
        let b = fixture();
        validate(&b).unwrap();
        let s = query(&[&b.collections["diagnostics"][0]], &b);
        assert_eq!(
            s["width_record"]["reported_width_constraint"]["operator"],
            ">"
        );
        for k in [
            "approximate_width_km",
            "width_range_km",
            "reference_period",
            "fixed_layer_bounds_m",
        ] {
            assert!(s["width_record"][k].is_null());
        }
    }
    #[test]
    fn rejects_neighbor_transfer_finite_widths_and_invented_seasons() {
        for (field, value) in [
            ("current_id", json!("alaskan-stream")),
            ("approximate_width_km", json!(400)),
            ("width_range_km", json!([400, 800])),
            ("fixed_layer_bounds_m", json!([0, 3000])),
            ("reference_period", json!([1990, 1998])),
            ("seasonal_playback_eligible", json!(true)),
        ] {
            let mut b = fixture();
            b.collections.get_mut("widths").unwrap().last_mut().unwrap()[field] = value;
            assert!(validate(&b).is_err(), "{field}");
        }
        let mut b = fixture();
        b.collections.get_mut("widths").unwrap().last_mut().unwrap()["reported_width_constraint"]
            ["operator"] = json!(">=");
        assert!(validate(&b).is_err());
    }
    #[test]
    fn binds_export_and_required_owner_links() {
        for field in ["source_ids", "diagnostic_ids"] {
            let mut b = fixture();
            b.collections.get_mut("objects").unwrap()[0][field] = json!([]);
            assert!(validate(&b).is_err());
        }
        let mut b = fixture();
        b.manifest["input_sha256"][EXPORT] = json!("0".repeat(64));
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.manifest["aleutian_onishi_width_version"] = Value::Null;
        assert!(validate(&b).is_err());
    }
}
