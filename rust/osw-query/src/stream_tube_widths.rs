//! Bind original Table 2 cells, including non-temporal threshold sensitivity.
use serde_json::Value;
use sha2::{Digest, Sha256};
const AUDIT: &str = include_str!(
    "../../../research/west-spitsbergen-kolas-2018-stream-tube-width-scope-audit.json"
);
const PATH: &str = "research/west-spitsbergen-kolas-2018-stream-tube-width-scope-audit.json";

pub(crate) fn validate(row: &Value) -> Result<(), String> {
    let id = row["id"].as_str().unwrap_or("");
    if row["current_id"] != "west-spitsbergen"
        && row["phase_kind"] != "synoptic_stream_tube_section"
        && !id.starts_with("west-spitsbergen-kolas-2018-")
        && row.get("stream_tube_context").is_none()
    {
        return Ok(());
    }
    let doc: Value = serde_json::from_str(AUDIT).map_err(|e| e.to_string())?;
    let expected = doc["measurements"]
        .as_array()
        .unwrap()
        .iter()
        .find(|r| r["id"] == id)
        .ok_or("Unknown WSC stream-tube source cell")?;
    let mut actual = row.clone();
    let context = actual["stream_tube_context"]
        .as_object_mut()
        .ok_or("Missing WSC tube context")?;
    if context.remove("audit_file") != Some(Value::String(PATH.into()))
        || context.remove("audit_sha256")
            != Some(Value::String(format!(
                "{:x}",
                Sha256::digest(AUDIT.as_bytes())
            )))
    {
        return Err("Changed WSC source audit receipt".into());
    }
    if actual != *expected {
        return Err("WSC stream-tube source cell, threshold or scope mismatch".into());
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    #[test]
    fn sensitivity_is_not_temporal_variability_or_width_error() {
        let doc: Value = serde_json::from_str(AUDIT).unwrap();
        for source in doc["measurements"].as_array().unwrap() {
            let mut row = source.clone();
            row["stream_tube_context"]["audit_file"] = json!(PATH);
            row["stream_tube_context"]["audit_sha256"] =
                json!(format!("{:x}", Sha256::digest(AUDIT.as_bytes())));
            validate(&row).unwrap();
            for (key, value) in [
                ("current_id", json!("spitsbergen-atlantic")),
                ("width_range_km", json!([11, 61])),
                ("fixed_layer_bounds_m", json!([45, 475])),
                ("seasonal_playback_eligible", json!(true)),
            ] {
                let mut bad = row.clone();
                bad[key] = value;
                assert!(validate(&bad).is_err(), "{key}");
            }
            let mut bad = row.clone();
            bad["stream_tube_context"]["transport_tolerance_is_width_error"] = json!(true);
            assert!(validate(&bad).is_err());
        }
    }
}
