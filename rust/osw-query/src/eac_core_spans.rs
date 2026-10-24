//! Compact contract; the large dated corpus stays in the checked source index.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
pub const ID: &str = "diagnostic:eac-csiro100m-section-core-spans";
const FILE: &str = "research/eac-csiro-100m-section-core-spans-summary.json";
const RAW: &str = include_str!("../../../research/eac-csiro-100m-section-core-spans-summary.json");
const HELPER: &str = include_str!("../../../analysis/eac_core_spans.py");
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
fn document() -> Value {
    serde_json::from_str(RAW).unwrap()
}
fn record(doc: &Value) -> Value {
    json!({"id":ID,"label":"EAC100m dated section-core spans; not physical widths",
        "entity_id":"current:east-australian","current_id":"east-australian","status":doc["status"],
        "rank_eligible":false,"source_file":FILE,"source_file_sha256":pin(RAW),"source_json":RAW,"document":doc})
}
pub fn validate(bundle: &crate::Bundle) -> Result<(), String> {
    let empty = Vec::new();
    let doc = document();
    let diagnostics = bundle.collections.get("diagnostics").unwrap_or(&empty);
    let widths = bundle.collections.get("widths").unwrap_or(&empty);
    let corpus = doc["raw_profile_file"].as_str().unwrap();
    let promoted = widths.iter().any(|w| {
        w.to_string().contains(FILE) || w.to_string().contains(corpus) || w["diagnostic_id"] == ID
    });
    let present = promoted
        || bundle.manifest["input_sha256"].get(FILE).is_some()
        || diagnostics
            .iter()
            .any(|d| d["id"] == ID || d["document"]["schema"] == "osw.eac-section-core-summary.v1");
    if !present {
        return Ok(());
    }
    let pins = &bundle.manifest["input_sha256"];
    if pins[FILE] != pin(RAW) || pins["analysis/eac_core_spans.py"] != pin(HELPER) {
        return Err("EAC core exact summary/operator binding changed".into());
    }
    for (path, expected) in doc["input_sha256"].as_object().unwrap() {
        if pins[path] != *expected {
            return Err("EAC core source/figure/protocol binding changed".into());
        }
    }
    let found = diagnostics
        .iter()
        .filter(|d| d["id"] == ID)
        .collect::<Vec<_>>();
    if found.len() != 1 || *found[0] != record(&doc) {
        return Err("EAC core summary projection changed".into());
    }
    let owner = bundle
        .collections
        .get("objects")
        .unwrap_or(&empty)
        .iter()
        .find(|o| o["id"] == "current:east-australian")
        .ok_or("Missing EAC core owner")?;
    if !owner["diagnostic_ids"]
        .as_array()
        .is_some_and(|ids| ids.contains(&json!(ID)))
    {
        return Err("Missing EAC core diagnostic join".into());
    }
    if promoted {
        return Err("Exploratory EAC section spans cannot become inventory widths".into());
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
    doc["kind"] = json!("eac_section_core_spans");
    doc["diagnostic_id"] = json!(ID);
    doc["source_file"] = json!(FILE);
    doc["source_sha256"] = json!(pin(RAW));
    doc
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
                    vec![json!({"id":"current:east-australian","diagnostic_ids":[ID]})],
                ),
                ("widths".into(), vec![]),
            ]),
        }
    }
    #[test]
    fn exact_core_scene_keeps_all_attempts_and_no_raw_profiles() {
        let b = fixture();
        assert!(validate(&b).is_ok());
        let s = scene(&b);
        assert_eq!(s["counts"]["attempts"], 33930);
        assert_eq!(s["months"].as_array().unwrap().len(), 124);
        assert!(s.get("profiles").is_none());
        assert_eq!(s["physical_width_admitted"], false);
        assert_eq!(s["overall_outcomes"][1]["resolved_dates"], 2883);
    }
    #[test]
    fn altered_core_scope_sources_and_erased_joins_reject() {
        for mode in ["scope", "source", "operator", "join", "coherent"] {
            let mut b = fixture();
            match mode {
                "scope" => {
                    b.collections.get_mut("diagnostics").unwrap()[0]["document"]["physical_width_admitted"] =
                        json!(true)
                }
                "source" => {
                    b.manifest["input_sha256"][document()["raw_profile_file"].as_str().unwrap()] =
                        json!("0".repeat(64))
                }
                "operator" => {
                    b.manifest["input_sha256"]["plans/eac-csiro-100m-section-core-span-protocol-v1.md"] =
                        json!("0".repeat(64))
                }
                "join" => {
                    b.collections.get_mut("objects").unwrap()[0]["diagnostic_ids"] = json!([])
                }
                _ => {
                    let d = &mut b.collections.get_mut("diagnostics").unwrap()[0];
                    d["document"]["counts"]["attempts"] = json!(1);
                    let raw = d["document"].to_string();
                    d["source_json"] = json!(raw);
                    d["source_file_sha256"] = json!(pin(&raw));
                    b.manifest["input_sha256"][FILE] = json!(pin(&raw));
                }
            }
            assert!(validate(&b).is_err(), "{mode}");
        }
    }
    #[test]
    fn core_width_promotion_rejects_after_diagnostic_erasure() {
        let mut b = fixture();
        b.collections.get_mut("diagnostics").unwrap().clear();
        b.collections.get_mut("objects").unwrap().clear();
        b.collections
            .get_mut("widths")
            .unwrap()
            .push(json!({"source_file":document()["raw_profile_file"],"approximate_width_km":50}));
        assert!(validate(&b).is_err());
    }
}
