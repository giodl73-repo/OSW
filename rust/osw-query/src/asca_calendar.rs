//! Conditional source-sample distributions cannot become physical annual ranges.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
pub const ID: &str = "diagnostic:agulhas-asca100m-calendar-distributions";
const FILE: &str = "research/asca-component-calendar-distributions.json";
const RAW: &str = include_str!("../../../research/asca-component-calendar-distributions.json");
const FIGURE_FILE: &str = "research/asca-component-calendar-distributions-figure.json";
const FIGURE: &str =
    include_str!("../../../research/asca-component-calendar-distributions-figure.json");
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
fn document() -> Value {
    serde_json::from_str(RAW).unwrap()
}
fn record() -> Value {
    let doc = document();
    json!({"id":ID,"label":"Agulhas ASCA100m source-sample calendar distributions","entity_id":"current:agulhas",
        "current_id":"agulhas","status":doc["status"],"rank_eligible":false,"source_file":FILE,
        "source_file_sha256":pin(RAW),"source_json":RAW,"document":doc})
}
pub fn validate(bundle: &crate::Bundle) -> Result<(), String> {
    let present = bundle.manifest["input_sha256"][FILE].is_string()
        || bundle.manifest["input_sha256"]["research/current-measurement-object-scope-index.json"]
            .is_string()
        || bundle
            .collections
            .get("diagnostics")
            .into_iter()
            .flatten()
            .any(|r| r["id"] == ID);
    if !present {
        return Ok(());
    }
    let expected = record();
    let rows: Vec<_> = bundle
        .collections
        .get("diagnostics")
        .into_iter()
        .flatten()
        .filter(|r| r["id"] == ID || r["source_file"] == FILE)
        .collect();
    if rows != vec![&expected]
        || bundle.manifest["input_sha256"][FILE] != pin(RAW)
        || bundle.manifest["input_sha256"][FIGURE_FILE] != pin(FIGURE)
    {
        return Err("ASCA calendar source, distribution or eligibility changed".into());
    }
    let doc = document();
    let fig: Value = serde_json::from_str(FIGURE).unwrap();
    for (path, digest) in doc["input_sha256"]
        .as_object()
        .ok_or("Missing ASCA calendar inputs")?
    {
        if bundle.manifest["input_sha256"][path] != *digest {
            return Err("ASCA calendar dependency changed".into());
        }
    }
    if bundle.manifest["input_sha256"][fig["generator_file"].as_str().unwrap()]
        != fig["generator_sha256"]
    {
        return Err("ASCA calendar figure operator changed".into());
    }
    for asset in fig["figures"].as_object().unwrap().values() {
        if bundle.manifest["input_sha256"][asset["file"].as_str().unwrap()] != asset["sha256"] {
            return Err("ASCA calendar figure asset changed".into());
        }
    }
    let mut owners = 0;
    for row in bundle.collections.get("objects").into_iter().flatten() {
        let n = row["diagnostic_ids"]
            .as_array()
            .into_iter()
            .flatten()
            .filter(|id| **id == ID)
            .count();
        if n > 0 && (n != 1 || row["id"] != "current:agulhas") {
            return Err("Wrong ASCA calendar owner".into());
        }
        owners += n;
    }
    if owners != 1 {
        return Err("Missing ASCA calendar owner".into());
    }
    Ok(())
}
pub fn scene(bundle: &crate::Bundle) -> Value {
    if !bundle
        .collections
        .get("diagnostics")
        .into_iter()
        .flatten()
        .any(|r| r["id"] == ID)
    {
        return Value::Null;
    }
    let doc = document();
    let figure: Value = serde_json::from_str(FIGURE).unwrap();
    json!({"kind":"asca_component_calendar_distributions","source_file":FILE,
        "title":"Calendar sample ranges and measurement coverage","records":doc["records"],
        "figure_file":figure["figures"]["svg"]["file"],"figure_alt":figure["figure_alt"],
        "limitations":doc["limitations"],"quantile_rule":doc["quantile_rule"],
        "source_method":doc["source_method"],"source_quality_limits":doc["source_quality_limits"],
        "source_citation":doc["source_citation"],"source_url":doc["source_url"],"source_license":doc["source_license"]})
}
#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> crate::Bundle {
        let doc = document();
        let fig: Value = serde_json::from_str(FIGURE).unwrap();
        let mut inputs = doc["input_sha256"].clone();
        inputs[FILE] = json!(pin(RAW));
        inputs[FIGURE_FILE] = json!(pin(FIGURE));
        inputs[fig["generator_file"].as_str().unwrap()] = fig["generator_sha256"].clone();
        for a in fig["figures"].as_object().unwrap().values() {
            inputs[a["file"].as_str().unwrap()] = a["sha256"].clone();
        }
        crate::Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest: json!({"input_sha256":inputs}),
            collections: std::collections::BTreeMap::from([
                ("diagnostics".into(), vec![record()]),
                (
                    "objects".into(),
                    vec![json!({"id":"current:agulhas","diagnostic_ids":[ID]})],
                ),
            ]),
        }
    }
    #[test]
    fn source_sample_statistics_and_physical_promotions_reject() {
        let b = fixture();
        assert!(validate(&b).is_ok());
        for (key, value) in [
            ("physical_width_admitted", json!(true)),
            ("annual_physical_width_range_km", json!([38, 179])),
            ("time_samples_independent", json!(true)),
            ("percentiles_are_confidence_intervals", json!(true)),
        ] {
            let mut bad = fixture();
            bad.collections.get_mut("diagnostics").unwrap()[0]["document"][key] = value;
            assert!(validate(&bad).is_err(), "{key}");
        }
        let mut bad = fixture();
        bad.collections.get_mut("diagnostics").unwrap()[0]["document"]["records"][0]["resolved_samples"] =
            json!(931);
        assert!(validate(&bad).is_err());
    }
    #[test]
    fn coherent_erasure_and_wrong_owner_reject() {
        let b = fixture();
        let mut bad = fixture();
        bad.collections.get_mut("objects").unwrap()[0]["id"] = json!("current:east-australian");
        assert!(validate(&bad).is_err());
        let mut bad = fixture();
        bad.collections.get_mut("diagnostics").unwrap().clear();
        bad.collections.get_mut("objects").unwrap()[0]["diagnostic_ids"] = json!([]);
        bad.manifest["input_sha256"]
            .as_object_mut()
            .unwrap()
            .remove(FILE);
        bad.manifest["input_sha256"]["research/current-measurement-object-scope-index.json"] =
            json!("full-bundle-marker");
        assert!(validate(&bad).is_err());
    }
}
