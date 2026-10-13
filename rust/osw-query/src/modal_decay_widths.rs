//! Campaign modal decay estimates retain source arithmetic and separate time supports.
use serde_json::Value;
use sha2::{Digest, Sha256};

pub(crate) fn validate(row: &Value) -> Result<(), String> {
    if row["current_id"] != "tsushima" {
        return if row.get("modal_decay_context").is_none() {
            Ok(())
        } else {
            Err("Unknown modal decay width owner".into())
        };
    }
    let path = "research/tsushima-matsuyama-1990-modal-width-scope-audit.json";
    let raw =
        include_str!("../../../research/tsushima-matsuyama-1990-modal-width-scope-audit.json");
    let doc: Value = serde_json::from_str(raw).map_err(|e| e.to_string())?;
    let mut expected = doc["measurement"].clone();
    expected["modal_decay_context"]["audit_file"] = Value::String(path.into());
    expected["modal_decay_context"]["audit_sha256"] =
        Value::String(format!("{:x}", Sha256::digest(raw.as_bytes())));
    if *row != expected {
        return Err("Tsushima modal width or operator support mismatch".into());
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    #[test]
    fn erased_context_and_promoted_report_are_rejected() {
        for row in [
            json!({"current_id":"tsushima"}),
            json!({"current_id":"tsushima","approximate_width_km":23.076923,"seasonal_playback_eligible":true}),
            json!({"current_id":"other","modal_decay_context":{}}),
        ] {
            assert!(validate(&row).is_err());
        }
    }
}
