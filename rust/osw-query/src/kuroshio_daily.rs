//! Source-bound regional model dimensions, separate from inventory measurements.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
pub const FILE: &str = "research/kuroshio-wang-2024-regional-dimensions.json";
pub const CONTRACT: &str = "research/kuroshio-wang-2024-query-contract.json";
pub const COLLECTION: &str = "current_dimension_samples";
pub const ID: &str = "diagnostic:kuroshio-wang-2024-dimensions";
const SOURCE: &str = "source:kuroshio-wang-2026-v1";
pub const RAW: &str = include_str!("../../../research/kuroshio-wang-2024-regional-dimensions.json");
const CONTRACT_RAW: &str = include_str!("../../../research/kuroshio-wang-2024-query-contract.json");
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
fn document() -> Value {
    serde_json::from_str(RAW).unwrap()
}
fn contract() -> Value {
    serde_json::from_str(CONTRACT_RAW).unwrap()
}
pub fn active(b: &Bundle) -> bool {
    b.manifest["kuroshio_daily_dimensions_version"].is_string()
        || b.manifest["input_sha256"][FILE].is_string()
        || b.collections.contains_key(COLLECTION)
        || b.collections
            .get("diagnostics")
            .into_iter()
            .flatten()
            .any(|r| r["id"] == ID)
}
fn sample_id(row: &Value, latitude: Option<f64>) -> String {
    let prefix = format!(
        "dimension:kuroshio:wang-v1:{}:z{:02}:",
        row["date"].as_str().unwrap(),
        row["source_level"].as_u64().unwrap()
    );
    let metric = latitude
        .map(|v| format!("span-{}n-v1", v.to_string().replace('.', "p")))
        .unwrap_or_else(|| "axis-18n-30n-v1".into());
    prefix + &metric
}
pub fn samples(doc: &Value) -> Vec<Value> {
    let mut rows = vec![];
    for (i, r) in doc["daily"].as_array().unwrap().iter().enumerate() {
        let common = json!({"entity_id":"current:kuroshio","current_id":"kuroshio",
            "sample_date":r["date"],"nominal_depth_m":r["nominal_depth_m"],"source_level":r["source_level"],
            "report_case_index":i,"source_id":SOURCE,"diagnostic_id":ID,"evidence_class":"model_derived","rank_eligible":false,"uncertainty_km":null});
        let mut axis = common.clone();
        for (k, v) in json!({"id":sample_id(r,None),"quantity":"regional_axis_length",
                           "status":r["axis"]["status"],"value_km":r["axis"]["length_km"]})
        .as_object()
        .unwrap()
        {
            axis[k] = v.clone();
        }
        rows.push(axis);
        for s in r["sections"].as_array().unwrap() {
            let mut row = common.clone();
            for (k,v) in json!({"id":sample_id(r,s["latitude"].as_f64()),"quantity":"fixed_latitude_boundary_span",
                "section_latitude":s["latitude"],"status":s["status"],"value_km":s["span_km"],"boundary_fallback_occurred":null}).as_object().unwrap() {
                row[k]=v.clone();
            }
            rows.push(row);
        }
    }
    rows
}
fn diagnostic(doc: &Value) -> Value {
    let mut summary = json!({});
    for key in [
        "status",
        "counts",
        "axis_status_counts",
        "section_status_counts",
        "conventions",
    ] {
        summary[key] = doc[key].clone();
    }
    json!({"id":ID,"label":"Kuroshio2024 regional model dimensions and dated maps",
        "entity_id":"current:kuroshio","current_id":"kuroshio","rank_eligible":false,
        "source_file":FILE,"source_file_sha256":pin(RAW),"source_json":RAW,"summary":summary})
}
pub fn validate(b: &Bundle) -> Result<(), String> {
    if !active(b) {
        return Ok(());
    }
    if b.manifest["kuroshio_daily_dimensions_version"] != "1" {
        return Err("Missing Kuroshio daily dimension edition".into());
    }
    let c = contract();
    let doc = document();
    for (path, sha) in [(FILE, pin(RAW)), (CONTRACT, pin(CONTRACT_RAW))] {
        if b.manifest["input_sha256"][path] != sha {
            return Err("Changed Kuroshio source/contract pin".into());
        }
    }
    for (path, sha) in c["input_sha256"].as_object().unwrap() {
        if b.manifest["input_sha256"][path] != *sha {
            return Err(format!("Changed Kuroshio dependency: {path}"));
        }
    }
    let actual = b
        .collections
        .get(COLLECTION)
        .ok_or("Missing Kuroshio dimension attempts")?;
    if *actual != samples(&doc) {
        return Err("Changed Kuroshio daily dimension projection".into());
    }
    let ds: Vec<_> = b
        .collections
        .get("diagnostics")
        .into_iter()
        .flatten()
        .filter(|r| r["id"] == ID)
        .collect();
    if ds != vec![&diagnostic(&doc)] {
        return Err("Changed Kuroshio dimension diagnostic".into());
    }
    let sources: Vec<_> = b
        .collections
        .get("sources")
        .into_iter()
        .flatten()
        .filter(|r| r["id"] == SOURCE)
        .collect();
    if sources != vec![&c["source_record"]] {
        return Err("Changed Kuroshio licensed source".into());
    }
    let owners: Vec<_> = b
        .collections
        .get("objects")
        .into_iter()
        .flatten()
        .filter(|r| r["id"] == "current:kuroshio")
        .collect();
    let owner = owners.first().ok_or("Missing Kuroshio dimension owner")?;
    if owners.len() != 1
        || owner["capabilities"]["model_dimension_samples"] != 6588
        || !owner["diagnostic_ids"]
            .as_array()
            .is_some_and(|a| a.contains(&json!(ID)))
        || !owner["source_ids"]
            .as_array()
            .is_some_and(|a| a.contains(&json!(SOURCE)))
    {
        return Err("Changed Kuroshio dimension owner links".into());
    }
    Ok(())
}
fn path(coords: &Value) -> String {
    let mut d = String::new();
    let mut pen = false;
    for p in coords.as_array().unwrap() {
        if let Some((x, y)) = crate::map::point(p) {
            d.push_str(&format!("{} {x:.5} {y:.5} ", if pen { 'L' } else { 'M' }));
            pen = true;
        } else {
            pen = false;
        }
    }
    d
}
pub fn scene(b: &Bundle) -> Value {
    if !active(b) {
        return Value::Null;
    }
    let doc = document();
    let frames:Vec<_>=doc["display_frames"].as_array().unwrap().iter().map(|f| {
        let i=doc["daily"].as_array().unwrap().iter().position(|r|r["date"]==f["date"]&&r["source_level"]==f["source_level"]).unwrap();
        let paths:Vec<_>=["axis","left","right"].iter().map(|key|json!({"role":key,"d":path(&f["curves_lon_lat"][key])})).collect();
        let sections:Vec<_>=doc["daily"][i]["sections"].as_array().unwrap().iter().map(|s|{let mut item=s.clone();item["sample_id"]=json!(sample_id(&doc["daily"][i],s["latitude"].as_f64()));item}).collect();
        json!({"date":f["date"],"source_level":f["source_level"],"nominal_depth_m":f["nominal_depth_m"],
            "report_case_index":i,"paths":paths,"axis_sample_id":sample_id(&doc["daily"][i],None),"axis":doc["daily"][i]["axis"],"sections":sections})
    }).collect();
    json!({"kind":"kuroshio_daily_dimensions","source_file":FILE,"diagnostic_id":ID,
        "title":"Kuroshio2024 · dated regional model dimensions","scope":contract()["scope"],
        "counts":doc["counts"],"source":doc["source"],"frames":frames,"summaries":doc["summaries"],
        "view_box":[298,58,14,17],"extent_lon_lat":[[118,15],[132,32]],"map_projection":"equirectangular","figure_file":doc["figure"],
        "collection":COLLECTION})
}
pub fn query(records: &[&Value], b: &Bundle) -> Value {
    if records.len() == 1 && records[0]["id"] == ID {
        scene(b)
    } else {
        Value::Null
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::BTreeMap;
    fn bundle() -> Bundle {
        let c = contract();
        let doc = document();
        let mut pins = c["input_sha256"].clone();
        pins[FILE] = json!(pin(RAW));
        pins[CONTRACT] = json!(pin(CONTRACT_RAW));
        Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest: json!({"kuroshio_daily_dimensions_version":"1","input_sha256":pins}),
            collections: BTreeMap::from([
                (COLLECTION.into(), samples(&doc)),
                ("sources".into(), vec![c["source_record"].clone()]),
                ("diagnostics".into(), vec![diagnostic(&doc)]),
                (
                    "objects".into(),
                    vec![
                        json!({"id":"current:kuroshio","capabilities":{"model_dimension_samples":6588},"source_ids":[SOURCE],"diagnostic_ids":[ID]}),
                    ],
                ),
            ]),
        }
    }
    #[test]
    fn exact_projection_and_dated_scene() {
        let b = bundle();
        assert!(validate(&b).is_ok());
        assert_eq!(b.collections[COLLECTION].len(), 6588);
        let s = scene(&b);
        assert_eq!(s["frames"].as_array().unwrap().len(), 36);
        assert_eq!(s["frames"][0]["date"], "2024-01-01");
        assert!(
            s["frames"][0]["paths"][0]["d"]
                .as_str()
                .unwrap()
                .starts_with('M')
        );
    }
    #[test]
    fn source_cases_links_and_scope_cannot_drift() {
        for (field, value) in [
            ("value_km", json!(0)),
            ("sample_date", json!("2023-01-01")),
            ("rank_eligible", json!(true)),
            ("evidence_class", json!("observed")),
            ("nominal_depth_m", json!(100)),
        ] {
            let mut b = bundle();
            b.collections.get_mut(COLLECTION).unwrap()[0][field] = value;
            assert!(validate(&b).is_err(), "{field}");
        }
        let mut b = bundle();
        b.collections.get_mut(COLLECTION).unwrap().pop();
        assert!(validate(&b).is_err());
        let mut b = bundle();
        b.collections.get_mut("objects").unwrap()[0]["source_ids"] = json!([]);
        assert!(validate(&b).is_err());
        let mut b = bundle();
        b.manifest["input_sha256"][FILE] = json!("changed");
        assert!(validate(&b).is_err());
        let mut b = bundle();
        b.collections.get_mut("sources").unwrap()[0]["license"] = json!("unknown");
        assert!(validate(&b).is_err());
        let mut b = bundle();
        b.collections.get_mut("diagnostics").unwrap().clear();
        assert!(validate(&b).is_err());
        let mut b = bundle();
        b.collections.get_mut("objects").unwrap()[0]["diagnostic_ids"] = json!([]);
        assert!(validate(&b).is_err());
        let mut b = bundle();
        b.manifest["kuroshio_daily_dimensions_version"] = json!("2");
        assert!(validate(&b).is_err());
        let mut b = bundle();
        b.collections
            .get_mut(COLLECTION)
            .unwrap()
            .push(json!({"id":"unbound"}));
        assert!(validate(&b).is_err());
    }
    #[test]
    fn nulls_break_native_paths_and_older_snapshots_remain_readable() {
        let d = path(&json!([[124, 24], null, [125, 25], [126, 26]]));
        assert_eq!(d.matches('M').count(), 2);
        let b = Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest: json!({}),
            collections: BTreeMap::new(),
        };
        assert!(validate(&b).is_ok());
        assert!(scene(&b).is_null());
    }
}
