//! Source-specific radius claims retain conflicts and cannot become occupied disks.
use serde_json::Value;
pub(crate) const PATH: &str = "research/agulhas-guerra-2022-ring-radius-scope-audit.json";
const ORIGINAL: &str =
    include_str!("../../../research/agulhas-guerra-2022-ring-radius-scope-audit.json");
pub(crate) fn validate(doc: &Value) -> Result<(), String> {
    let expected: Value = serde_json::from_str(ORIGINAL).map_err(|e| e.to_string())?;
    if *doc != expected {
        return Err("Agulhas radius source or unresolved scope mismatch".into());
    }
    Ok(())
}
