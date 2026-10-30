//! Exact source reports preserve mixed-signal and mean-field distinctions.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
pub const FILE: &str = "research/hansen-2011-asar-surface-width-admissions.json";
pub const EXPORT: &str = "research/ocean-current-measurements-asar-edition.json";
pub const RAW: &str =
    include_str!("../../../research/hansen-2011-asar-surface-width-admissions.json");
pub const EXPORT_RAW: &str =
    include_str!("../../../research/ocean-current-measurements-asar-edition.json");
const ID: &str = "diagnostic:hansen-asar-2011-surface-widths";
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
fn document() -> Value {
    serde_json::from_str(RAW).unwrap()
}
pub fn active(b: &Bundle) -> bool {
    b.manifest["hansen_asar_widths_version"].is_string()
        || b.manifest["input_sha256"][FILE].is_string()
        || b.collections.values().flatten().any(|r| {
            r["id"] == ID
                || r["id"] == format!("{ID}:coastal")
                || r["id"]
                    .as_str()
                    .is_some_and(|s| s.starts_with("hansen-asar-2011-"))
                || r["id"] == "source:hansen-asar-2011"
        })
}
pub fn widths(b: &Bundle) -> Vec<Value> {
    if active(b) {
        document()["width_records"].as_array().unwrap().clone()
    } else {
        vec![]
    }
}
pub fn recognizes_width(row: &Value) -> bool {
    document()["width_records"]
        .as_array()
        .unwrap()
        .contains(row)
}
fn diagnostic(current: &str) -> Value {
    let d = document();
    let id = if current == "norwegian-atlantic-slope" {
        ID.to_string()
    } else {
        format!("{ID}:coastal")
    };
    json!({"id":id,"label":"ASAR local surface widths: separate and mixed signals",
        "entity_id":format!("current:{current}"),"current_id":current,"rank_eligible":false,
        "source_file":FILE,"source_file_sha256":pin(RAW),"source_json":RAW,
        "summary":{"admitted_local_widths":if current=="norwegian-atlantic-slope" {2} else {1},"comparison_total_widths":3,"excluded_mixed_profiles":2,"reference_period":d["reference_period"],
            "annual_width_range_km":null,"source_field_reproduction":false}})
}
pub fn validate(b: &Bundle) -> Result<(), String> {
    if !active(b) {
        return Ok(());
    }
    if b.manifest["hansen_asar_widths_version"] != "1" {
        return Err("Changed ASAR source-report edition".into());
    }
    let d = document();
    let e: Value = serde_json::from_str(EXPORT_RAW).unwrap();
    for (p, raw) in [(FILE, RAW), (EXPORT, EXPORT_RAW)] {
        if b.manifest["input_sha256"][p] != pin(raw) {
            return Err(format!("Changed ASAR receipt:{p}"));
        }
    }
    for doc in [&d, &e] {
        for (p, hash) in doc["input_sha256"].as_object().unwrap() {
            if b.manifest["input_sha256"][p] != *hash {
                return Err(format!("Changed ASAR dependency:{p}"));
            }
        }
    }
    let mut records: Vec<(&str, Value)> = d["width_records"]
        .as_array()
        .unwrap()
        .iter()
        .cloned()
        .map(|r| ("widths", r))
        .collect();
    records.push(("sources", d["source_record"].clone()));
    records.push(("diagnostics", diagnostic("norwegian-atlantic-slope")));
    records.push(("diagnostics", diagnostic("norwegian-coastal")));
    for (collection, expected) in records {
        let rows: Vec<_> = b
            .collections
            .get(collection)
            .into_iter()
            .flatten()
            .filter(|r| r["id"] == expected["id"])
            .collect();
        if rows != vec![&expected] {
            return Err(format!("Changed ASAR scoped {collection}"));
        }
    }
    let actual = b.collections.get("widths").ok_or("Missing scoped widths")?;
    let mut expected_widths = e["widths"].as_array().unwrap().clone();
    expected_widths.extend(crate::neuc_glider_widths::widths(b));
    expected_widths.extend(crate::aleutian_onishi_width::widths(b));
    expected_widths.extend(crate::current_gap_admissions::widths(b));
    expected_widths.extend(crate::satellite_core_widths::widths(b));
    expected_widths.extend(crate::wicc_review_width::widths(b));
    expected_widths.extend(crate::eacc_cited_width::widths(b));
    expected_widths.extend(crate::madagascar_dimensions::validated_widths(b)?);
    expected_widths.extend(crate::azcc_onken_width::validated_widths(b)?);
    expected_widths.extend(crate::pacific_nec_nominal_width::validated_widths(b)?);
    expected_widths.extend(crate::dimoune_section_widths::validated_widths(b)?);
    expected_widths.extend(crate::atlantic_nec_band_spans::validated_widths(b)?);
    if actual != &expected_widths {
        return Err("Changed ASAR effective width inventory/order".into());
    }
    let expected_lengths =
        crate::length_assessment_overlays::expected(b, &e["length_assessments"])?;
    if b.collections.get("length_assessments") != expected_lengths.as_array() {
        return Err("ASAR surface width promoted into length evidence".into());
    }
    for (owner, count) in [
        ("current:norwegian-atlantic-slope", 8),
        ("current:norwegian-coastal", 2),
    ] {
        if let Some(objects) = b.collections.get("objects") {
            let rows: Vec<_> = objects.iter().filter(|r| r["id"] == owner).collect();
            if rows.len() != 1
                || rows[0]["capabilities"]["scoped_width"] != count
                || !rows[0]["source_ids"]
                    .as_array()
                    .is_some_and(|a| a.contains(&d["source_record"]["id"]))
                || !rows[0]["diagnostic_ids"].as_array().is_some_and(|a| {
                    a.contains(&diagnostic(owner.strip_prefix("current:").unwrap())["id"])
                })
            {
                return Err(format!(
                    "Changed ASAR owner dimensions/source links:{owner}"
                ));
            }
        }
    }
    Ok(())
}
pub fn query(rows: &[&Value], b: &Bundle) -> Value {
    if !active(b)
        || rows.len() != 1
        || (rows[0]["id"] != ID && rows[0]["id"] != format!("{ID}:coastal"))
    {
        return Value::Null;
    }
    let d = document();
    json!({"kind":"hansen_asar_surface_widths","source_file":FILE,"source_url":d["source_url"],
        "figure_file":d["figure_file"],"effective_measurements_file":if crate::aleutian_onishi_width::active(b){crate::aleutian_onishi_width::EXPORT}else if crate::neuc_glider_widths::active(b){crate::neuc_glider_widths::EXPORT}else{EXPORT},
        "width_records":d["width_records"],"mixed_contexts":d["mixed_contexts"],
        "scope":"August2007-July2010 weighted mean surface field. Local source reports with different operators; no annual width range, physical edges or source-field reconstruction."})
}
#[cfg(test)]
pub(crate) mod tests {
    use super::*;
    pub(crate) fn fixture() -> Bundle {
        let d = document();
        let e: Value = serde_json::from_str(EXPORT_RAW).unwrap();
        let mut inputs = e["input_sha256"].clone();
        for (p, h) in d["input_sha256"].as_object().unwrap() {
            inputs[p] = h.clone();
        }
        inputs[FILE] = json!(pin(RAW));
        inputs[EXPORT] = json!(pin(EXPORT_RAW));
        serde_json::from_value(json!({"schema":"osw.query-bundle.v1",
            "manifest":{"hansen_asar_widths_version":"1","input_sha256":inputs},
            "collections":{"widths":e["widths"],"sources":[d["source_record"]],
                "diagnostics":[diagnostic("norwegian-atlantic-slope"),diagnostic("norwegian-coastal")],"length_assessments":e["length_assessments"],
                "objects":[
                    {"id":"current:norwegian-atlantic-slope","capabilities":{"scoped_width":8},"source_ids":[d["source_record"]["id"]],"diagnostic_ids":[ID]},
                    {"id":"current:norwegian-coastal","capabilities":{"scoped_width":2},"source_ids":[d["source_record"]["id"]],"diagnostic_ids":[format!("{ID}:coastal")]}
                ]}}))
        .unwrap()
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
    fn exact_mean_field_reports_are_admitted() {
        validate(&fixture()).unwrap();
    }
    #[test]
    fn missing_owner_source_or_diagnostic_link_is_rejected() {
        for key in ["source_ids", "diagnostic_ids"] {
            let mut b = fixture();
            b.collections.get_mut("objects").unwrap()[1][key] = json!([]);
            assert!(validate(&b).is_err(), "{key}");
        }
    }
    #[test]
    fn coastal_scope_dispatch_accepts_only_the_exact_new_record() {
        let d = document();
        let row = d["width_records"].as_array().unwrap().last().unwrap();
        crate::seasons_data::norwegian_coastal_width_scope(row).unwrap();
        for (key, value) in [
            ("approximate_width_km", json!(24)),
            ("current_id", json!("norwegian")),
            ("width_range_km", json!([20, 30])),
            ("fixed_layer_bounds_m", json!([0, 200])),
        ] {
            let mut bad = row.clone();
            bad[key] = value;
            assert!(!recognizes_width(&bad));
            // Reassigned rows are rejected by the admission's full inventory
            // check even when they no longer match this owner's old guard.
            if key != "current_id" {
                assert!(crate::seasons_data::norwegian_coastal_width_scope(&bad).is_err());
            }
        }
    }
    #[test]
    fn rejects_owner_operator_period_and_range_transfers() {
        for (field, value) in [
            ("current_id", json!("norwegian")),
            ("approximate_width_km", json!(45)),
            ("conditional_on_isobath_partition", json!(true)),
            ("fixed_layer_bounds_m", json!([0, 200])),
            (
                "reference_period",
                json!({"start_month":"2007-01","end_month":"2011-12"}),
            ),
            ("seasonal_playback_eligible", json!(true)),
            ("width_range_km", json!([30, 60])),
        ] {
            let mut b = fixture();
            let w = b.collections.get_mut("widths").unwrap().last_mut().unwrap();
            w[field] = value;
            assert!(validate(&b).is_err(), "{field}");
        }
    }
    #[test]
    fn rejects_mixed_profile_promotion_and_stripped_pins() {
        let mut b = fixture();
        b.collections.get_mut("widths").unwrap().push(json!({"id":"mixed-s1","current_id":"norwegian-atlantic-slope","approximate_width_km":60}));
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.manifest = json!({});
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections.get_mut("widths").unwrap().pop();
        assert!(validate(&b).is_err());
    }
}
