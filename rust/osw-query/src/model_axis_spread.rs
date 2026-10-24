//! An author-reported model mean axis distance is not a full current width.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
const PATH: &str = "research/pacific-necc-chen-2016-axis-spread-scale-scope-audit.json";
const RAW: &str =
    include_str!("../../../research/pacific-necc-chen-2016-axis-spread-scale-scope-audit.json");
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
fn document() -> Value {
    serde_json::from_str(RAW).unwrap()
}
fn expected() -> Vec<Value> {
    document()["measurements"]
        .as_array()
        .unwrap()
        .iter()
        .enumerate()
        .map(|(i, r)| {
            let mut row = r.clone();
            row["model_axis_spread_context"]["audit_file"] = json!(PATH);
            row["model_axis_spread_context"]["audit_sha256"] = json!(pin(RAW));
            row["source_file"] = json!(PATH);
            row["source_pointer"] = json!(format!("/measurements/{i}"));
            row
        })
        .collect()
}
pub(crate) fn validate(bundle: &crate::Bundle) -> Result<(), String> {
    let widths = bundle
        .collections
        .get("widths")
        .map(Vec::as_slice)
        .unwrap_or(&[]);
    let active = bundle.manifest["input_sha256"].get(PATH).is_some()
        || widths
            .iter()
            .any(|r| r.get("model_axis_spread_context").is_some())
        || bundle
            .collections
            .get("objects")
            .into_iter()
            .flatten()
            .any(|r| r["id"] == "current:pacific-north-equatorial-countercurrent");
    if !active {
        return Ok(());
    }
    if bundle.manifest["input_sha256"][PATH] != pin(RAW) {
        return Err("Published model scale source changed".into());
    }
    let doc = document();
    for (path, sha) in doc["input_sha256"].as_object().unwrap() {
        if bundle.manifest["input_sha256"][path] != *sha {
            return Err(format!("Published model scale dependency changed: {path}"));
        }
    }
    if bundle.manifest["input_sha256"][doc["generator_file"].as_str().unwrap()]
        != doc["generator_sha256"]
    {
        return Err("Published model scale extraction code changed".into());
    }
    for wanted in expected() {
        let rows: Vec<_> = widths.iter().filter(|r| r["id"] == wanted["id"]).collect();
        if rows.len() != 1 || rows[0] != &wanted {
            return Err(
                "Published model axis-distance value, metric, support or source changed".into(),
            );
        }
    }
    if widths
        .iter()
        .any(|r| r.get("model_axis_spread_context").is_some() && !expected().iter().any(|e| e == r))
    {
        return Err("Unexpected model axis-distance record or alias".into());
    }
    Ok(())
}
pub(crate) fn scene(matches: &[&Value]) -> Value {
    let rows = expected();
    let ids: Vec<_> = matches
        .iter()
        .filter(|r| rows.iter().any(|e| e["id"] == r["id"]))
        .map(|r| r["id"].clone())
        .collect();
    if ids.is_empty() {
        Value::Null
    } else {
        json!({"kind":"published_model_axis_spread","records":rows,"matching_ids":ids,
  "scope":"Author-reported model mean axis-distance scales. Both source states are shown for context; they are not a full width, an annual range or exact dated extrema."})
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    fn bundle() -> crate::Bundle {
        let doc = document();
        let mut inputs = doc["input_sha256"].clone();
        inputs[PATH] = json!(pin(RAW));
        inputs[doc["generator_file"].as_str().unwrap()] = doc["generator_sha256"].clone();
        serde_json::from_value(json!({"schema":"osw.query-bundle.v1","manifest":{"input_sha256":inputs},"collections":{"widths":expected()}})).unwrap()
    }
    #[test]
    fn rejects_doubling_rms_extrema_and_observation_claims() {
        validate(&bundle()).unwrap();
        for (key, value) in [
            ("approximate_width_km", json!(200)),
            ("width_metric", json!("full_width_at_half_maximum")),
            ("width_range_km", json!([100, 130])),
            ("annual_extrema_eligible", json!(true)),
            (
                "observed_period",
                json!({"start":"1960-01-01","end":"1960-01-01"}),
            ),
        ] {
            let mut bad = bundle();
            bad.collections.get_mut("widths").unwrap()[0][key] = value;
            assert!(validate(&bad).is_err());
        }
        let mut bad = bundle();
        bad.collections.get_mut("widths").unwrap()[0]["model_axis_spread_context"]["operator"]["scale_is_rms_or_standard_deviation"] =
            json!(true);
        assert!(validate(&bad).is_err());
    }
    #[test]
    fn rejects_missing_duplicate_and_original_rebinding() {
        let mut bad = bundle();
        bad.collections.get_mut("widths").unwrap().pop();
        assert!(validate(&bad).is_err());
        let mut bad = bundle();
        let r = bad.collections["widths"][0].clone();
        bad.collections.get_mut("widths").unwrap().push(r);
        assert!(validate(&bad).is_err());
        let mut bad = bundle();
        bad.manifest["input_sha256"]["research/source-data/chen-necc-2016/journal-article.pdf"] =
            json!("changed");
        assert!(validate(&bad).is_err());
    }
    #[test]
    fn filtered_scene_keeps_both_source_states_and_marks_match() {
        let rows = expected();
        let s = scene(&[&rows[1]]);
        assert_eq!(s["records"].as_array().unwrap().len(), 2);
        assert_eq!(s["matching_ids"], json!([rows[1]["id"]]));
        assert!(s["records"][0]["width_range_km"].is_null());
        assert!(scene(&[]).is_null());
    }
}
