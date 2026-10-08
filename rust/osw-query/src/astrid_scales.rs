//! Bind diagnostic radial definitions, never an occupied geographic disk.
use serde_json::Value;
pub(crate) const PATH: &str = "research/astrid-2000-radial-scale-scope-audit.json";
const ORIGINAL: &str = include_str!("../../../research/astrid-2000-radial-scale-scope-audit.json");
pub(crate) fn validate(doc: &Value) -> Result<(), String> {
    let expected: Value = serde_json::from_str(ORIGINAL).map_err(|e| e.to_string())?;
    if *doc != expected {
        return Err("Astrid diagnostic radius source or scope mismatch".into());
    }
    Ok(())
}
