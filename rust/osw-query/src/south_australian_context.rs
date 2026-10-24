//! Exact source/model-context contract. No physical-width promotion.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
pub const ID: &str = "diagnostic:south-australian-hycom-2d-flow-context";
const FILE: &str = "research/south-australian-hycom-2d-flow-context-scene.json";
const RAW: &str =
    include_str!("../../../research/south-australian-hycom-2d-flow-context-scene.json");
const HELPER: &str = include_str!("../../../analysis/south_australian_flow_context.py");
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
fn document() -> Value {
    serde_json::from_str(RAW).unwrap()
}
fn record(doc: &Value) -> Value {
    json!({"id":ID,"label":"South Australian monthly model-grid context; width unresolved",
        "entity_id":"current:south-australian","current_id":"south-australian","status":doc["status"],
        "rank_eligible":false,"source_file":FILE,"source_file_sha256":pin(RAW),"source_json":RAW,"document":doc})
}
pub fn validate(bundle: &crate::Bundle) -> Result<(), String> {
    let empty = Vec::new();
    let doc = document();
    let diagnostics = bundle.collections.get("diagnostics").unwrap_or(&empty);
    let widths = bundle.collections.get("widths").unwrap_or(&empty);
    let promoted = widths.iter().any(|w| {
        w.to_string().contains(FILE)
            || w.to_string()
                .contains(doc["raw_context_file"].as_str().unwrap())
            || w["diagnostic_id"] == ID
    });
    let present = promoted
        || bundle.manifest["input_sha256"].get(FILE).is_some()
        || diagnostics
            .iter()
            .any(|d| d["id"] == ID || d["document"]["schema"] == doc["schema"]);
    if !present {
        return Ok(());
    }
    let pins = &bundle.manifest["input_sha256"];
    if pins[FILE] != pin(RAW) || pins["analysis/south_australian_flow_context.py"] != pin(HELPER) {
        return Err("South Australian exact scene/operator binding changed".into());
    }
    for (path, expected) in doc["input_sha256"].as_object().unwrap() {
        if pins[path] != *expected {
            return Err("South Australian source/figure/protocol binding changed".into());
        }
    }
    let found = diagnostics
        .iter()
        .filter(|d| d["id"] == ID)
        .collect::<Vec<_>>();
    if found.len() != 1 || *found[0] != record(&doc) {
        return Err("South Australian exact scene projection changed".into());
    }
    let owner = bundle
        .collections
        .get("objects")
        .unwrap_or(&empty)
        .iter()
        .find(|o| o["id"] == "current:south-australian")
        .ok_or("Missing South Australian context owner")?;
    if !owner["diagnostic_ids"]
        .as_array()
        .is_some_and(|ids| ids.contains(&json!(ID)))
    {
        return Err("Missing South Australian diagnostic join".into());
    }
    if promoted {
        return Err("Model-grid context cannot become an inventory width".into());
    }
    Ok(())
}
pub fn scene(bundle: &crate::Bundle) -> Value {
    if !bundle
        .collections
        .get("diagnostics")
        .into_iter()
        .flatten()
        .any(|d| d["id"] == ID)
    {
        return Value::Null;
    }
    let mut doc = document();
    doc["kind"] = json!("south_australian_flow_context");
    doc["diagnostic_id"] = json!(ID);
    doc["source_file"] = json!(FILE);
    doc["source_sha256"] = json!(pin(RAW));
    doc
}
pub fn query(matches: &[&Value], bundle: &crate::Bundle) -> Value {
    if matches.iter().any(|d| d["id"] == ID) {
        scene(bundle)
    } else {
        Value::Null
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> crate::Bundle {
        let doc = document();
        let mut pins = doc["input_sha256"].clone();
        pins[FILE] = json!(pin(RAW));
        crate::Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest: json!({"input_sha256":pins}),
            collections: std::collections::BTreeMap::from([
                ("diagnostics".into(), vec![record(&doc)]),
                (
                    "objects".into(),
                    vec![json!({"id":"current:south-australian","diagnostic_ids":[ID]})],
                ),
                ("widths".into(), vec![]),
            ]),
        }
    }
    #[test]
    fn source_scope_and_all_cases_survive() {
        let b = fixture();
        assert!(validate(&b).is_ok());
        let s = scene(&b);
        assert_eq!(s["months"].as_array().unwrap().len(), 12);
        assert_eq!(s["original_scalar_overlap"], 55632);
        assert_eq!(s["width_measurement_admitted"], false);
        assert_eq!(s["annual_range_admitted"], false);
        for m in s["months"].as_array().unwrap() {
            assert_eq!(m["threshold_cases"].as_array().unwrap().len(), 3)
        }
    }
    #[test]
    fn altered_scope_source_membership_or_join_rejects() {
        for mode in [
            "scope",
            "source",
            "membership",
            "join",
            "duplicate",
            "resealed",
        ] {
            let mut b = fixture();
            match mode {
                "scope" => {
                    b.collections.get_mut("diagnostics").unwrap()[0]["document"]["width_measurement_admitted"] =
                        json!(true)
                }
                "source" => {
                    b.manifest["input_sha256"][document()["raw_context_file"].as_str().unwrap()] =
                        json!("0".repeat(64))
                }
                "membership" => {
                    b.collections.get_mut("diagnostics").unwrap()[0]["document"]["months"][0]["threshold_cases"]
                        [1]["cells"] = json!([])
                }
                "join" => {
                    b.collections.get_mut("objects").unwrap()[0]["diagnostic_ids"] = json!([])
                }
                "duplicate" => {
                    let row = b.collections["diagnostics"][0].clone();
                    b.collections.get_mut("diagnostics").unwrap().push(row);
                }
                _ => {
                    let d = &mut b.collections.get_mut("diagnostics").unwrap()[0];
                    d["document"]["source_dates"] = json!(1);
                    let raw = d["document"].to_string();
                    d["source_json"] = json!(raw);
                    d["source_file_sha256"] = json!(pin(&raw));
                    b.manifest["input_sha256"][FILE] = json!(pin(&raw));
                }
            }
            assert!(validate(&b).is_err(), "{mode}")
        }
    }
    #[test]
    fn width_promotion_rejects_after_erased_diagnostic() {
        let mut b = fixture();
        b.collections.get_mut("diagnostics").unwrap().clear();
        b.collections.get_mut("objects").unwrap().clear();
        b.collections
            .get_mut("widths")
            .unwrap()
            .push(json!({"source_file":document()["raw_context_file"],"approximate_width_km":50}));
        assert!(validate(&b).is_err());
    }
}
