//! A published local core statistic; reported SD is not an annual width range.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
pub const PATH: &str = "research/west-spitsbergen-dundas-2026-selected-core-width-scope-audit.json";
const RAW: &str = include_str!(
    "../../../research/west-spitsbergen-dundas-2026-selected-core-width-scope-audit.json"
);
const FIG_PATH: &str = "research/source-data/dundas-fer-wsc-2026/figure.json";
const FIG_RAW: &str = include_str!("../../../research/source-data/dundas-fer-wsc-2026/figure.json");
const ID: &str = "west-spitsbergen-dundas-2026-selected-core-width-statistic";
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
fn audit() -> Value {
    serde_json::from_str(RAW).unwrap()
}
pub(crate) fn expected() -> Value {
    let doc = audit();
    let figure: Value = serde_json::from_str(FIG_RAW).unwrap();
    let image = "figures/west-spitsbergen-selected-core-width.svg";
    let mut r = doc["measurement"].clone();
    let c = r["selected_core_context"].as_object_mut().unwrap();
    c.insert("audit_file".into(), json!(PATH));
    c.insert("audit_sha256".into(), json!(pin(RAW)));
    c.insert("section_windows".into(), doc["section_windows"].clone());
    c.insert("figure_file".into(), json!(image));
    c.insert("figure_sha256".into(), figure["files"][image].clone());
    r["source_file"] = json!(PATH);
    r["source_pointer"] = json!("/measurement");
    r
}
pub(crate) fn validate_row(row: &Value) -> Result<(), String> {
    if row != &expected() {
        return Err("Selected-core width statistic, SD, operator or source binding changed".into());
    }
    Ok(())
}
pub(crate) fn validate(bundle: &crate::Bundle) -> Result<(), String> {
    let widths = bundle
        .collections
        .get("widths")
        .map(Vec::as_slice)
        .unwrap_or(&[]);
    let present = bundle.manifest["input_sha256"].get(PATH).is_some()
        || widths.iter().any(|r| {
            r["current_id"] == "west-spitsbergen"
                || r["id"] == ID
                || r.get("selected_core_context").is_some()
        })
        || bundle
            .collections
            .get("objects")
            .into_iter()
            .flatten()
            .any(|r| r["id"] == "current:west-spitsbergen");
    if !present {
        return Ok(());
    }
    if bundle.manifest["input_sha256"][PATH] != pin(RAW)
        || bundle.manifest["input_sha256"][FIG_PATH] != pin(FIG_RAW)
    {
        return Err("Selected-core source or figure registry changed".into());
    }
    let doc = audit();
    let figure: Value = serde_json::from_str(FIG_RAW).unwrap();
    for (path, sha) in doc["input_sha256"]
        .as_object()
        .unwrap()
        .iter()
        .chain(figure["files"].as_object().unwrap().iter())
    {
        if bundle.manifest["input_sha256"][path] != *sha {
            return Err(format!("Selected-core dependency changed: {path}"));
        }
    }
    if bundle.manifest["input_sha256"][doc["protocol_file"].as_str().unwrap()]
        != doc["protocol_sha256"]
        || figure["audit_sha256"] != pin(RAW)
    {
        return Err("Selected-core calculation rules or figure audit changed".into());
    }
    let rows: Vec<_> = widths.iter().filter(|r| r["id"] == ID).collect();
    if rows.len() != 1 {
        return Err("Missing or duplicate published selected-core width".into());
    }
    validate_row(rows[0])?;
    if widths
        .iter()
        .any(|r| r.get("selected_core_context").is_some() && r["id"] != ID)
    {
        return Err("Unexpected selected-core duplicate".into());
    }
    Ok(())
}
pub(crate) fn scene(matches: &[&Value]) -> Value {
    match matches.iter().find(|r| r["id"] == ID) {
        Some(row) => {
            json!({"kind":"selected_core_width_statistic","record":row,"scope":"Local zonal core statistic from selected sections; SD is western-boundary variability, not annual extrema, confidence limits or physical edge error."})
        }
        None => Value::Null,
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn reported_sd_cannot_become_annual_range_or_another_identity() {
        let row = expected();
        validate_row(&row).unwrap();
        for (key, value) in [
            ("width_range_km", json!([21, 35])),
            ("width_standard_deviation_km", json!(14)),
            ("current_id", json!("spitsbergen-atlantic")),
            ("seasonal_playback_eligible", json!(true)),
        ] {
            let mut bad = row.clone();
            bad[key] = value;
            assert!(validate_row(&bad).is_err());
        }
        let mut bad = row;
        bad["selected_core_context"]["section_selection_percentile"] = json!(50);
        assert!(validate_row(&bad).is_err());
    }
    fn fixture() -> crate::Bundle {
        let doc = audit();
        let figure: Value = serde_json::from_str(FIG_RAW).unwrap();
        let mut inputs = doc["input_sha256"].as_object().unwrap().clone();
        inputs.extend(figure["files"].as_object().unwrap().clone());
        inputs.insert(PATH.into(), json!(pin(RAW)));
        inputs.insert(FIG_PATH.into(), json!(pin(FIG_RAW)));
        inputs.insert(
            doc["protocol_file"].as_str().unwrap().into(),
            doc["protocol_sha256"].clone(),
        );
        crate::Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest: json!({"input_sha256":inputs}),
            collections: std::collections::BTreeMap::from([
                ("widths".into(), vec![expected()]),
                (
                    "objects".into(),
                    vec![json!({"id":"current:west-spitsbergen"})],
                ),
            ]),
        }
    }
    #[test]
    fn owner_and_original_dependencies_require_the_published_record() {
        validate(&fixture()).unwrap();
        let mut missing = fixture();
        missing.collections.get_mut("widths").unwrap().clear();
        missing.manifest["input_sha256"]
            .as_object_mut()
            .unwrap()
            .remove(PATH);
        assert!(validate(&missing).is_err());
        let mut bad = fixture();
        bad.manifest["input_sha256"]["research/source-data/dundas-fer-wsc-2026/journal-article.pdf"] =
            json!("0".repeat(64));
        assert!(validate(&bad).is_err());
        let mut duplicate = fixture();
        let mut extra = expected();
        extra["id"] = json!("width:invented-copy");
        duplicate.collections.get_mut("widths").unwrap().push(extra);
        assert!(validate(&duplicate).is_err());
    }
    #[test]
    fn the_core_comparison_keeps_reported_variability_and_sampling_windows() {
        let row = expected();
        let result = scene(&[&row]);
        assert_eq!(result["kind"], "selected_core_width_statistic");
        assert_eq!(result["record"]["width_standard_deviation_km"], 7);
        assert!(result["record"]["width_range_km"].is_null());
        assert_eq!(
            result["record"]["selected_core_context"]["section_windows"]
                .as_array()
                .unwrap()
                .len(),
            3
        );
    }
}
