//! Abstract-only regional widths cannot acquire stronger scope via bundle rewrites.
use serde_json::Value;
use sha2::{Digest, Sha256};
pub(crate) fn validate(row: &Value) -> Result<(), String> {
    let owner = row["current_id"].as_str().unwrap_or("");
    let (path, raw) = match owner {
        "california" => (
            "research/california-2011-abstract-width-scope-audit.json",
            include_str!("../../../research/california-2011-abstract-width-scope-audit.json"),
        ),
        "oyashio" => (
            "research/oyashio-2005-abstract-width-scope-audit.json",
            include_str!("../../../research/oyashio-2005-abstract-width-scope-audit.json"),
        ),
        _ if row.get("source_scope_context").is_none()
            && !row["id"]
                .as_str()
                .unwrap_or("")
                .contains("abstract-regional-width") =>
        {
            return Ok(());
        }
        _ => return Err("Unknown abstract regional width owner".into()),
    };
    let doc: Value = serde_json::from_str(raw).map_err(|e| e.to_string())?;
    let mut expected = doc["measurement"].clone();
    for key in if owner == "oyashio" {
        vec!["source_scope_context", "regional_scalar_context"]
    } else {
        vec!["source_scope_context"]
    } {
        expected[key]["audit_file"] = Value::String(path.into());
        expected[key]["audit_sha256"] =
            Value::String(format!("{:x}", Sha256::digest(raw.as_bytes())));
    }
    if *row != expected {
        return Err("Abstract regional width source value or scope mismatch".into());
    }
    Ok(())
}
