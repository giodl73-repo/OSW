//! Versioned qualitative source interpretation; never monthly measurements.
use crate::Bundle;
use serde_json::Value;
pub const PATH: &str = "research/zeehan-ridgway-2007-seasonal-scope-audit.json";
pub fn validate(bundle: &Bundle) -> Result<(), String> {
    let owners: Vec<_> = bundle
        .collections
        .get("route_decisions")
        .into_iter()
        .flatten()
        .filter(|r| r["current_id"] == "zeehan")
        .collect();
    let receipt = &bundle.manifest["atlas_receipts"][PATH];
    if owners.is_empty() && receipt.is_null() {
        return Ok(());
    }
    let actual: Value = serde_json::from_str(
        receipt["source_json"]
            .as_str()
            .ok_or("Missing Zeehan calendar source")?,
    )
    .map_err(|e| e.to_string())?;
    let expected: Value = serde_json::from_str(include_str!(
        "../../../research/zeehan-ridgway-2007-seasonal-scope-audit.json"
    ))
    .map_err(|e| e.to_string())?;
    if actual != expected {
        return Err("Zeehan calendar differs from compiled source review".into());
    }
    let protocol = expected["protocol_file"]
        .as_str()
        .ok_or("Missing calendar protocol")?;
    if bundle.manifest["input_sha256"][protocol] != expected["protocol_sha256"] {
        return Err("Stale Zeehan calendar protocol".into());
    }
    for row in owners {
        if !row["scope_reviews"]
            .as_array()
            .is_some_and(|reviews| reviews.iter().any(|r| r["document"] == expected))
        {
            return Err("Zeehan planning source disagrees with calendar".into());
        }
    }
    Ok(())
}
