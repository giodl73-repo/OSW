//! Compiled scope for the original Atlantic EUC campaign core properties.
use crate::Bundle;
use serde_json::Value;
pub const PATH: &str = "research/atlantic-euc-layer-island-scope-audit.json";
pub fn validate(bundle: &Bundle) -> Result<(), String> {
    let has_owner = bundle
        .collections
        .get("route_decisions")
        .is_some_and(|rows| {
            rows.iter()
                .any(|r| r["current_id"] == "atlantic-equatorial-undercurrent")
        });
    let receipt = &bundle.manifest["atlas_receipts"][PATH];
    if !has_owner && receipt.is_null() {
        return Ok(());
    }
    let actual: Value = serde_json::from_str(
        receipt["source_json"]
            .as_str()
            .ok_or("Missing Atlantic section source")?,
    )
    .map_err(|e| e.to_string())?;
    let expected: Value = serde_json::from_str(include_str!(
        "../../../research/atlantic-euc-layer-island-scope-audit.json"
    ))
    .map_err(|e| e.to_string())?;
    if actual != expected {
        return Err(
            "Atlantic section extraction or scope differs from compiled original review".into(),
        );
    }
    let section = &expected["section_properties"];
    for key in ["protocol", "acquisition"] {
        let path = section[format!("{key}_file")]
            .as_str()
            .ok_or("Missing Atlantic section provenance")?;
        if bundle.manifest["input_sha256"][path] != section[format!("{key}_sha256")] {
            return Err("Stale Atlantic section provenance".into());
        }
    }
    for row in bundle
        .collections
        .get("route_decisions")
        .into_iter()
        .flatten()
        .filter(|r| r["current_id"] == "atlantic-equatorial-undercurrent")
    {
        if !row["scope_reviews"]
            .as_array()
            .is_some_and(|reviews| reviews.iter().any(|r| r["document"] == expected))
        {
            return Err("Atlantic planning source differs from compiled section review".into());
        }
    }
    Ok(())
}
