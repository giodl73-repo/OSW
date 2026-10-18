//! Exact source-bound dated component diagnostics, never inventory widths.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
pub const ID: &str = "diagnostic:agulhas-asca100m-component-spans";
const FILE: &str = "research/agulhas-asca-100m-dated-component-spans.json";
const RAW: &str = include_str!("../../../research/agulhas-asca-100m-dated-component-spans.json");
const FIGURE_FILE: &str = "research/agulhas-asca-100m-dated-component-spans-figure.json";
const FIGURE: &str =
    include_str!("../../../research/agulhas-asca-100m-dated-component-spans-figure.json");
const HELPER: &str = include_str!("../../../analysis/asca_component_spans.py");
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
fn document() -> Value {
    serde_json::from_str(RAW).unwrap()
}
fn figure() -> Value {
    serde_json::from_str(FIGURE).unwrap()
}
fn record(doc: &Value) -> Value {
    json!({"id":ID,"label":"Agulhas ASCA100m dated component-span experiment","entity_id":"current:agulhas",
        "current_id":"agulhas","status":doc["status"],"rank_eligible":false,"source_file":FILE,
        "source_file_sha256":pin(RAW),"source_json":RAW,"document":doc})
}
pub fn validate(bundle: &crate::Bundle) -> Result<(), String> {
    let empty = Vec::new();
    let diagnostics = bundle.collections.get("diagnostics").unwrap_or(&empty);
    let widths = bundle.collections.get("widths").unwrap_or(&empty);
    let mentioned = widths.iter().any(|w| {
        w.to_string().contains(FILE)
            || w["diagnostic_id"] == ID
            || w["metric"] == "asca100m_fixed_array_component_span"
    });
    let present = bundle.manifest["input_sha256"].get(FILE).is_some()
        || diagnostics.iter().any(|d| {
            d["id"] == ID || d["document"]["schema"] == "osw.asca-dated-component-spans.v1"
        })
        || mentioned;
    if !present {
        return Ok(());
    }
    let doc = document();
    let fig = figure();
    let inputs = &bundle.manifest["input_sha256"];
    if inputs[FILE] != pin(RAW)
        || inputs[FIGURE_FILE] != pin(FIGURE)
        || inputs["analysis/asca_component_spans.py"] != pin(HELPER)
    {
        return Err("ASCA component source/figure/helper binding changed".into());
    }
    for (path, expected) in doc["input_sha256"].as_object().unwrap() {
        if inputs[path] != *expected {
            return Err("ASCA component source/operator changed".into());
        }
    }
    if inputs[fig["generator_file"].as_str().unwrap()] != fig["generator_sha256"] {
        return Err("ASCA component figure operator changed".into());
    }
    for asset in fig["figures"].as_object().unwrap().values() {
        if inputs[asset["file"].as_str().unwrap()] != asset["sha256"] {
            return Err("ASCA component figure asset changed".into());
        }
    }
    let found = diagnostics
        .iter()
        .filter(|d| d["id"] == ID)
        .collect::<Vec<_>>();
    if found.len() != 1 || *found[0] != record(&doc) {
        return Err("ASCA component exact diagnostic projection changed".into());
    }
    let owners = bundle.collections.get("objects").unwrap_or(&empty);
    let owner = owners
        .iter()
        .find(|o| o["id"] == "current:agulhas")
        .ok_or("Missing ASCA component owner")?;
    if !owner["diagnostic_ids"]
        .as_array()
        .is_some_and(|ids| ids.contains(&json!(ID)))
    {
        return Err("Missing ASCA component diagnostic join".into());
    }
    if mentioned {
        return Err("ASCA fixed-array component diagnostics cannot become inventory widths".into());
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
    let doc = document();
    let fig = figure();
    json!({"kind":"asca_dated_component_spans","diagnostic_id":ID,
        "title":"Agulhas: dated ASCA100m component spans", "source_file":FILE,"source_sha256":pin(RAW),
        "raw_source_file":"research/agulhas-asca-100m-observed-profiles.json", "source_url":doc["source_url"],
        "source_citation":doc["source_citation"],"cautions":doc["interpretation"],
        "figure_file":fig["figures"][".svg"]["file"],"figure_sha256":fig["figures"][".svg"]["sha256"],
        "figure_alt":"All931 dated ASCA100m component outcomes:330 half-peak spans resolve;601 are unresolved. Three declared threshold sensitivities and three fixed source profiles. These are section spans, not flow-normal current widths or annual physical ranges.",
        "overall_outcomes":doc["overall_outcomes"],"profiles":doc["profiles"],"months":doc["monthly_summaries"]})
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
        let fig = figure();
        let mut inputs = doc["input_sha256"].clone();
        inputs[FILE] = json!(pin(RAW));
        inputs[FIGURE_FILE] = json!(pin(FIGURE));
        inputs["analysis/asca_component_spans.py"] = json!(pin(HELPER));
        inputs[fig["generator_file"].as_str().unwrap()] = fig["generator_sha256"].clone();
        for asset in fig["figures"].as_object().unwrap().values() {
            inputs[asset["file"].as_str().unwrap()] = asset["sha256"].clone();
        }
        crate::Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest: json!({"input_sha256":inputs}),
            collections: std::collections::BTreeMap::from([
                ("diagnostics".into(), vec![record(&doc)]),
                (
                    "objects".into(),
                    vec![json!({"id":"current:agulhas","diagnostic_ids":[ID]})],
                ),
                ("widths".into(), vec![]),
            ]),
        }
    }
    #[test]
    fn all_dated_outcomes_and_failures_are_source_bound() {
        let bundle = fixture();
        assert!(validate(&bundle).is_ok());
        let s = scene(&bundle);
        assert_eq!(s["profiles"].as_array().unwrap().len(), 931);
        assert_eq!(s["months"].as_array().unwrap().len(), 27);
        assert_eq!(s["overall_outcomes"][1]["resolved_profiles"], 330);
        for kind in ["date", "case", "physical", "join", "source"] {
            let mut bad = fixture();
            match kind {
                "date" => {
                    bad.collections.get_mut("diagnostics").unwrap()[0]["document"]["profiles"][0]
                        ["observed_at"] = json!("2026-10-18T00:00:00Z")
                }
                "case" => {
                    bad.collections.get_mut("diagnostics").unwrap()[0]["document"]["profiles"]
                        .as_array_mut()
                        .unwrap()
                        .pop();
                }
                "physical" => {
                    bad.collections.get_mut("diagnostics").unwrap()[0]["document"]["width_measurement_admitted"] =
                        json!(true)
                }
                "join" => {
                    bad.collections.get_mut("objects").unwrap()[0]["diagnostic_ids"] = json!([])
                }
                _ => bad.manifest["input_sha256"][FILE] = json!("0".repeat(64)),
            }
            assert!(validate(&bad).is_err(), "{kind}");
        }
    }
    #[test]
    fn coherent_source_rebinding_and_asset_changes_reject() {
        let mut bad = fixture();
        let row = &mut bad.collections.get_mut("diagnostics").unwrap()[0];
        row["document"]["interpretation"] = json!([]);
        let raw = serde_json::to_string(&row["document"]).unwrap();
        row["source_json"] = json!(raw);
        row["source_file_sha256"] = json!(pin(&raw));
        bad.manifest["input_sha256"][FILE] = json!(pin(&raw));
        assert!(validate(&bad).is_err());
        let mut bad = fixture();
        let fig = figure();
        bad.manifest["input_sha256"][fig["figures"][".svg"]["file"].as_str().unwrap()] =
            json!("0".repeat(64));
        assert!(validate(&bad).is_err());
    }
    #[test]
    fn inventory_promotion_rejects_even_after_owner_and_diagnostic_erasure() {
        let mut bad = fixture();
        bad.collections.get_mut("diagnostics").unwrap().clear();
        bad.collections.get_mut("objects").unwrap().clear();
        bad.collections
            .get_mut("widths")
            .unwrap()
            .push(json!({"source_file":FILE,"approximate_width_km":64}));
        assert!(validate(&bad).is_err());
    }
}
