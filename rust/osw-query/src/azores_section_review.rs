//! Verified provenance enriches existing dated widths without adding a dimension.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};

const KEY: &str = "azores_2009_section_review_v1";
const REVIEW: &str = "research/azores-2009-section-original-review-v1.json";
const BINDINGS: &str = "research/azores-2009-section-record-bindings-v1.json";
const VISUAL: &str = "research/azores-2009-section-card-visual-review-v1.json";
const FIGURE: &str = "figures/azores-2009-section-card-v1.svg";
const RAW: &str = include_str!("../../../research/azores-2009-section-original-review-v1.json");
const BOUND: &str = include_str!("../../../research/azores-2009-section-record-bindings-v1.json");
const CHECK: &str =
    include_str!("../../../research/azores-2009-section-card-visual-review-v1.json");
const SVG: &str = include_str!("../../../figures/azores-2009-section-card-v1.svg");

fn hash(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}

fn bindings() -> Value {
    serde_json::from_str(BOUND).expect("frozen Azores section bindings")
}

fn marker() -> Value {
    let mut pins = json!({});
    for (path, raw) in [
        (REVIEW, RAW),
        (BINDINGS, BOUND),
        (VISUAL, CHECK),
        (FIGURE, SVG),
    ] {
        pins[path] = json!(hash(raw));
    }
    json!({"logical_parent_sha256":bindings()["logical_parent_sha256"],"input_sha256":pins,
           "measurement_records_added":0,"measurement_records_changed":0})
}

fn active(bundle: &crate::Bundle) -> bool {
    bundle.manifest.get(KEY).is_some()
}

pub(crate) fn validate(bundle: &crate::Bundle) -> Result<(), String> {
    let expected = marker();
    let source_present = expected["input_sha256"]
        .as_object()
        .unwrap()
        .keys()
        .any(|p| bundle.manifest["input_sha256"].get(p).is_some());
    if !active(bundle) && !source_present {
        return Ok(());
    }
    if bundle.manifest[KEY] != expected {
        return Err("Azores section review activation or source identity differs".into());
    }
    for (path, hash) in expected["input_sha256"].as_object().unwrap() {
        if &bundle.manifest["input_sha256"][path] != hash {
            return Err("Azores original section source binding differs".into());
        }
    }
    let bound = bindings();
    for row in bound["records"].as_array().unwrap() {
        let actual: Vec<_> = bundle
            .collections
            .get("widths")
            .into_iter()
            .flatten()
            .filter(|r| r["id"] == row["id"])
            .collect();
        if actual != vec![row] {
            return Err("Azores existing width identity, period or method differs".into());
        }
    }
    Ok(())
}

pub(crate) fn full(bundle: &crate::Bundle) -> Value {
    if !active(bundle) {
        return Value::Null;
    }
    let doc: Value = serde_json::from_str(RAW).unwrap();
    json!({"kind":"azores_2009_section_review","title":"Azores / surveyed width sections",
        "source_file":REVIEW,"bindings_file":BINDINGS,"source_url":doc["source"]["publisher_url"],
        "figure_file":FIGURE,"figure_sha256":hash(SVG),"section_context":doc["shared_section_context"],
        "records":bindings()["records"],"enrichments":doc["existing_measurement_enrichments"],
        "remaining_gates":doc["remaining_gates"],"matching_ids":[],
        "scope":"Two existing approximately 110 km dated meridional section spans. Not along-current lengths, uniform width layers, seasonal ranges or current footprints."})
}

pub(crate) fn query(matches: &[&Value], bundle: &crate::Bundle) -> Value {
    let mut scene = full(bundle);
    if scene.is_null() {
        return scene;
    }
    let rows = scene["records"].as_array().unwrap();
    let mut ids: Vec<_> = matches
        .iter()
        .filter(|r| rows.iter().any(|s| s["id"] == r["id"]))
        .map(|r| r["id"].clone())
        .collect();
    ids.sort_by(|a, b| a.as_str().cmp(&b.as_str()));
    ids.dedup();
    if ids.is_empty() {
        return Value::Null;
    }
    scene["matching_ids"] = json!(ids);
    scene
}

#[cfg(test)]
mod tests {
    use super::*;

    fn bundle() -> crate::Bundle {
        let mut data: crate::Bundle = serde_json::from_value(json!({
            "schema":"osw.query-bundle.v1","manifest":{},"collections":{"widths":bindings()["records"]}
        })).unwrap();
        let expected = marker();
        data.manifest["input_sha256"] = expected["input_sha256"].clone();
        data.manifest[KEY] = expected;
        data
    }

    #[test]
    fn exact_existing_sections_are_required() {
        let mut data = bundle();
        assert!(validate(&data).is_ok());
        data.collections.get_mut("widths").unwrap()[0]["approximate_width_km"] = json!(111);
        assert!(validate(&data).is_err());
    }

    #[test]
    fn original_source_cannot_be_rebound_or_partially_activated() {
        let mut data = bundle();
        data.manifest["input_sha256"][REVIEW] = json!("wrong");
        assert!(validate(&data).is_err());
        let mut data = bundle();
        data.manifest.as_object_mut().unwrap().remove(KEY);
        assert!(validate(&data).is_err());
    }

    #[test]
    fn a_query_keeps_both_sections_but_marks_only_its_matches() {
        let data = bundle();
        let row = &data.collections["widths"][0];
        let scene = query(&[row], &data);
        assert_eq!(scene["records"].as_array().unwrap().len(), 2);
        assert_eq!(scene["matching_ids"], json!([row["id"]]));
        assert!(query(&[], &data).is_null());
    }
}
