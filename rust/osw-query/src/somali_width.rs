//! Seasonal regional prose must not become monthly width observations.
use serde_json::Value;
use sha2::{Digest, Sha256};
const PATH: &str = "research/somali-schott-2001-premonsoon-width-scope-audit.json";
const AUDIT: &str =
    include_str!("../../../research/somali-schott-2001-premonsoon-width-scope-audit.json");
pub(crate) fn validate(row: &Value) -> Result<(), String> {
    if row["phase_kind"] != "seasonal_regional_width_range"
        && row.get("seasonal_regional_context").is_none()
        && !row["id"]
            .as_str()
            .unwrap_or("")
            .starts_with("somali-schott-2001-")
    {
        return Ok(());
    }
    let doc: Value = serde_json::from_str(AUDIT).map_err(|e| e.to_string())?;
    let mut expected = doc["measurement"].clone();
    expected["seasonal_regional_context"]["audit_file"] = Value::String(PATH.into());
    expected["seasonal_regional_context"]["audit_sha256"] =
        Value::String(format!("{:x}", Sha256::digest(AUDIT.as_bytes())));
    if *row != expected {
        return Err("Somali seasonal width source or calendar scope mismatch".into());
    }
    Ok(())
}
