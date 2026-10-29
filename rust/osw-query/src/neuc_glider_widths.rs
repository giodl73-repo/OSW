//! Source-reported repeat-section ranges remain separate from mean breadths.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
pub const FILE: &str = "research/neuc-glider-2015-width-admissions.json";
pub const EXPORT: &str = "research/ocean-current-measurements-neuc-edition.json";
pub const RAW: &str = include_str!("../../../research/neuc-glider-2015-width-admissions.json");
pub static EXPORT_RAW: &str =
    include_str!("../../../research/ocean-current-measurements-neuc-edition.json");
const OWNER: &str = "current:pacific-north-equatorial-undercurrent";
const ID: &str = "diagnostic:neuc-glider-2015-width-ranges";
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
fn document() -> Value {
    serde_json::from_str(RAW).unwrap()
}
pub fn active(b: &Bundle) -> bool {
    b.manifest["neuc_glider_widths_version"].is_string()
        || b.manifest["input_sha256"][FILE].is_string()
        || b.collections.values().flatten().any(|r| {
            r["id"] == ID
                || r["id"] == "source:neuc-schonau-rudnick-2015"
                || r["id"]
                    .as_str()
                    .is_some_and(|s| s.starts_with("neuc-glider-2015-"))
        })
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
fn diagnostic() -> Value {
    let d = document();
    json!({"id":ID,"label":"NEUC glider jet width ranges: two local jets","entity_id":OWNER,
        "current_id":"pacific-north-equatorial-undercurrent","rank_eligible":false,
        "source_file":FILE,"source_file_sha256":pin(RAW),"source_json":RAW,
        "summary":{"local_jet_ranges":2,"reference_period":d["reference_period"],"annual_width_range_km":null,
            "source_original_retained":false,"source_field_reproduction":false}})
}
pub fn validate(b: &Bundle) -> Result<(), String> {
    if !active(b) {
        return Ok(());
    }
    if b.manifest["neuc_glider_widths_version"] != "1" {
        return Err("Changed NEUC source range edition".into());
    }
    let d = document();
    let e: Value = serde_json::from_str(EXPORT_RAW).unwrap();
    for (p, raw) in [(FILE, RAW), (EXPORT, EXPORT_RAW)] {
        if b.manifest["input_sha256"][p] != pin(raw) {
            return Err(format!("Changed NEUC receipt:{p}"));
        }
    }
    for doc in [&d, &e] {
        for (p, sha) in doc["input_sha256"].as_object().unwrap() {
            if b.manifest["input_sha256"][p] != *sha {
                return Err(format!("Changed NEUC dependency:{p}"));
            }
        }
    }
    let mut rows: Vec<(&str, Value)> = d["width_records"]
        .as_array()
        .unwrap()
        .iter()
        .cloned()
        .map(|r| ("widths", r))
        .collect();
    rows.push(("sources", d["source_record"].clone()));
    rows.push(("diagnostics", diagnostic()));
    for (collection, expected) in rows {
        let actual: Vec<_> = b
            .collections
            .get(collection)
            .into_iter()
            .flatten()
            .filter(|r| r["id"] == expected["id"])
            .collect();
        if actual != vec![&expected] {
            return Err(format!("Changed NEUC scoped {collection}"));
        }
    }
    let mut expected_widths = e["widths"].as_array().unwrap().clone();
    expected_widths.extend(crate::aleutian_onishi_width::widths(b));
    expected_widths.extend(crate::current_gap_admissions::widths(b));
    expected_widths.extend(crate::satellite_core_widths::widths(b));
    expected_widths.extend(crate::wicc_review_width::widths(b));
    expected_widths.extend(crate::eacc_cited_width::widths(b));
    expected_widths.extend(crate::madagascar_dimensions::validated_widths(b)?);
    expected_widths.extend(crate::azcc_onken_width::validated_widths(b)?);
    expected_widths.extend(crate::pacific_nec_nominal_width::validated_widths(b)?);
    expected_widths.extend(crate::dimoune_section_widths::validated_widths(b)?);
    let expected_lengths =
        crate::length_assessment_overlays::expected(b, &e["length_assessments"])?;
    if b.collections.get("widths") != Some(&expected_widths)
        || b.collections.get("length_assessments") != expected_lengths.as_array()
    {
        return Err("NEUC ranges changed preceding width inventory or length evidence".into());
    }
    if let Some(objects) = b.collections.get("objects") {
        let owners: Vec<_> = objects.iter().filter(|r| r["id"] == OWNER).collect();
        if owners.len() != 1
            || owners[0]["capabilities"]["scoped_width"] != 4
            || !owners[0]["source_ids"]
                .as_array()
                .is_some_and(|a| a.contains(&d["source_record"]["id"]))
            || !owners[0]["diagnostic_ids"]
                .as_array()
                .is_some_and(|a| a.contains(&json!(ID)))
        {
            return Err("Missing Pacific NEUC range owner/source/diagnostic joins".into());
        }
    }
    Ok(())
}
pub fn query(rows: &[&Value], b: &Bundle) -> Value {
    if !active(b)
        || !rows.iter().any(|r| {
            r["id"] == ID
                || r["id"]
                    .as_str()
                    .is_some_and(|s| s.starts_with("neuc-glider-2015-"))
        })
    {
        return Value::Null;
    }
    let d = document();
    json!({"kind":"neuc_glider_width_ranges","source_file":FILE,"source_url":d["source_url"],"figure_file":d["figure_file"],
        "effective_measurements_file":if crate::aleutian_onishi_width::active(b){crate::aleutian_onishi_width::EXPORT}else{EXPORT},"width_records":d["width_records"],
        "mean_breadth_comparison":crate::pacific_neuc_breadths::full(b.collections.get("widths").map(Vec::as_slice).unwrap_or(&[])),
        "scope":"Two local Pacific NEUC jet ranges at134.3E across the June2009-January2014 study. Meridional eastward geostrophic-flow extents in source density context26.7-27.3kg/m3; southern broad cases may combine jets. Neither annual envelopes nor width error; no dated samples, new physical edges or source-field reproduction. Primary HTML reviewed, original file not retained."})
}
pub fn width_scene(rows: &[&Value], b: &Bundle) -> Value {
    let mut s = query(rows, b);
    if let Some(object) = s.as_object_mut() {
        object.remove("mean_breadth_comparison");
    }
    s
}
#[cfg(test)]
pub(crate) mod tests {
    use super::*;
    pub(crate) fn fixture() -> Bundle {
        let d = document();
        let e: Value = serde_json::from_str(EXPORT_RAW).unwrap();
        let mut pins = e["input_sha256"].clone();
        for (p, h) in d["input_sha256"].as_object().unwrap() {
            pins[p] = h.clone();
        }
        pins[FILE] = json!(pin(RAW));
        pins[EXPORT] = json!(pin(EXPORT_RAW));
        serde_json::from_value(json!({"schema":"osw.query-bundle.v1","manifest":{"neuc_glider_widths_version":"1","input_sha256":pins},
            "collections":{"widths":e["widths"],"length_assessments":e["length_assessments"],"sources":[d["source_record"]],"diagnostics":[diagnostic()],
                "objects":[{"id":OWNER,"capabilities":{"scoped_width":4},"source_ids":[d["source_record"]["id"]],"diagnostic_ids":[ID]}]}})).unwrap()
    }
    #[test]
    fn exact_cited_constraint_append_preserves_inventory_rejection() {
        let mut b = fixture();
        b.manifest["published_eacc_cited_width_constraint_v1"] = json!({});
        let rows = crate::eacc_cited_width::widths(&b);
        b.collections.get_mut("widths").unwrap().extend(rows);
        validate(&b).unwrap();
        let row = b.collections["widths"].last().unwrap().clone();
        b.collections.get_mut("widths").unwrap().push(row);
        assert!(validate(&b).is_err());
        b.collections.get_mut("widths").unwrap().pop();
        b.collections.get_mut("widths").unwrap().last_mut().unwrap()["reported_bound_km"] =
            json!(400);
        assert!(validate(&b).is_err());
    }
    #[test]
    fn exact_review_width_append_preserves_inventory_rejection() {
        let mut b = fixture();
        b.manifest["published_wicc_review_width_v1"] = json!({});
        let rows = crate::wicc_review_width::widths(&b);
        b.collections.get_mut("widths").unwrap().extend(rows);
        validate(&b).unwrap();
        let row = b.collections["widths"].last().unwrap().clone();
        b.collections.get_mut("widths").unwrap().push(row);
        assert!(validate(&b).is_err());
        b.collections.get_mut("widths").unwrap().pop();
        b.collections.get_mut("widths").unwrap().last_mut().unwrap()["approximate_width_km"] =
            json!(400);
        assert!(validate(&b).is_err());
    }
    #[test]
    fn exact_satellite_append_preserves_the_complete_inventory_guard() {
        let mut b = fixture();
        b.manifest["published_satellite_core_widths_v1"] = json!({});
        let appended = crate::satellite_core_widths::widths(&b);
        assert_eq!(appended.len(), 2);
        b.collections.get_mut("widths").unwrap().extend(appended);
        validate(&b).unwrap();
        let original = b.collections["widths"].clone();
        let rows = b.collections.get_mut("widths").unwrap();
        rows.last_mut().unwrap()["approximate_width_km"] = json!(81);
        assert!(validate(&b).is_err());
        b.collections.insert("widths".into(), original.clone());
        let extra = original.last().unwrap().clone();
        b.collections.get_mut("widths").unwrap().push(extra);
        assert!(validate(&b).is_err());
        b.collections.insert("widths".into(), original);
        b.collections.get_mut("widths").unwrap().swap(0, 1);
        assert!(validate(&b).is_err());
    }
    #[test]
    fn exact_local_ranges_keep_zero_and_distinct_mean_context() {
        let b = fixture();
        validate(&b).unwrap();
        let d = document();
        let w = &d["width_records"][1];
        assert_eq!(w["width_range_km"], json!([0, 200]));
        assert_eq!(w["source_zero_lower_bound"], true);
        let scene = query(&[&b.collections["diagnostics"][0]], &b);
        assert_eq!(
            scene["mean_breadth_comparison"]["records"]
                .as_array()
                .unwrap()
                .len(),
            2
        );
        assert_eq!(scene["width_records"].as_array().unwrap().len(), 2);
    }
    #[test]
    fn rejects_family_transfer_seasons_midpoints_and_false_originals() {
        for (key, value) in [
            ("current_id", json!("north-equatorial-undercurrent")),
            ("approximate_width_km", json!(225)),
            ("width_range_km", json!([1, 200])),
            ("seasonal_playback_eligible", json!(true)),
            ("calendar_months", json!([6])),
            ("fixed_layer_bounds_m", json!([267, 273])),
            ("source_zero_lower_bound", json!(false)),
        ] {
            let mut b = fixture();
            let row = b.collections.get_mut("widths").unwrap().last_mut().unwrap();
            row[key] = value;
            assert!(validate(&b).is_err(), "{key}");
        }
        let mut b = fixture();
        b.collections.get_mut("sources").unwrap()[0]["original_file_retained"] = json!(true);
        assert!(validate(&b).is_err());
    }
    #[test]
    fn original_scope_dispatch_accepts_only_exact_source_ranges() {
        let d = document();
        let row = &d["width_records"][0];
        crate::original_regional_widths::validate(row).unwrap();
        let mut bad = row.clone();
        bad["width_range_km"] = json!([0, 350]);
        assert!(!recognizes_width(&bad));
        assert!(crate::original_regional_widths::validate(&bad).is_err());
    }
    #[test]
    fn requires_edition_dependencies_and_owner_joins() {
        for field in ["source_ids", "diagnostic_ids"] {
            let mut b = fixture();
            b.collections.get_mut("objects").unwrap()[0][field] = json!([]);
            assert!(validate(&b).is_err());
        }
        for field in ["neuc_glider_widths_version", "input_sha256"] {
            let mut b = fixture();
            b.manifest[field] = Value::Null;
            assert!(validate(&b).is_err());
        }
        let mut b = fixture();
        b.collections.get_mut("widths").unwrap()[0]["width_range_km"] = json!([0, 350]);
        assert!(validate(&b).is_err());
    }
}
