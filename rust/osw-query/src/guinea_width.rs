//! Regional reference-model width is distinct from theoretical scales and seasons.
use serde_json::Value;
use sha2::{Digest, Sha256};
const PATH: &str = "research/guinea-djakoure-2017-model-width-source-review.json";
const AUDIT: &str =
    include_str!("../../../research/guinea-djakoure-2017-model-width-source-review.json");
pub(crate) fn validate(row: &Value) -> Result<(), String> {
    if row["current_id"] != "guinea"
        && row["phase_kind"] != "model_regional_width_summary"
        && row.get("model_regional_context").is_none()
    {
        return Ok(());
    }
    let doc: Value = serde_json::from_str(AUDIT).map_err(|e| e.to_string())?;
    let mut expected = doc["measurement"].clone();
    expected["model_regional_context"]["audit_file"] = Value::String(PATH.into());
    expected["model_regional_context"]["audit_sha256"] =
        Value::String(format!("{:x}", Sha256::digest(AUDIT.as_bytes())));
    if *row != expected {
        return Err("Guinea model width source or mean scope mismatch".into());
    }
    Ok(())
}
