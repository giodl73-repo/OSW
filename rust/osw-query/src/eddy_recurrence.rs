//! Published recurrence summaries remain distinct from individual detections.
use crate::Bundle;
use serde_json::Value;
use sha2::{Digest, Sha256};
pub fn validate(bundle: &Bundle) -> Result<(), String> {
    let Some(rows) = bundle.collections.get("eddy_recurrence") else {
        return Ok(());
    };
    let path = "research/black-sea-eddy-recurrence.json";
    let receipt = &bundle.manifest["eddy_recurrence_receipt"];
    let raw = receipt["source_json"]
        .as_str()
        .ok_or("Missing recurrence source receipt")?;
    let hash = format!("{:x}", Sha256::digest(raw.as_bytes()));
    if receipt["source_file"] != path
        || receipt["source_sha256"] != hash
        || bundle.manifest["input_sha256"][path] != hash
    {
        return Err("Changed recurrence source receipt".into());
    }
    let doc: Value = serde_json::from_str(raw).map_err(|e| e.to_string())?;
    if doc["schema"] != "osw.eddy-recurrence-summary.v1"
        || doc["entries"].as_array() != Some(rows)
        || rows.len() != 9
    {
        return Err("Recurrence projection differs from source extraction".into());
    }
    for row in rows {
        let entity = bundle.collections["objects"]
            .iter()
            .find(|e| e["id"] == row["entity_id"])
            .ok_or("Unresolved recurrence region")?;
        let lifetime = row["reported_event_lifetime_approx"].as_f64();
        if entity["identity_level"] != "recurrent_eddy_region"
            || entity["basin"] != "Black Sea"
            || row["identity_level"] != "recurrent_eddy_region"
            || row["label"] != entity["label"]
            || !row["reported_occurrence_days_per_year_approx"]
                .as_f64()
                .is_some_and(|v| v > 0.0 && v <= 366.0)
            || lifetime.is_some_and(|v| v <= 0.0)
            || !row["reported_event_lifetime_approx"].is_null() && lifetime.is_none()
            || lifetime.is_some()
                && !matches!(
                    row["event_lifetime_statistic"].as_str(),
                    Some("mean" | "typical")
                )
            || row["source_document_sha256"] != doc["source_document_sha256"]
            || bundle.manifest["input_sha256"][doc["source_document_file"]
                .as_str()
                .ok_or("Missing recurrence primary source")?]
                != doc["source_document_sha256"]
            || lifetime.is_some()
                && !matches!(row["event_lifetime_unit"].as_str(), Some("day" | "month"))
            || lifetime.is_none()
                && (!row["event_lifetime_unit"].is_null()
                    || !row["event_lifetime_statistic"].is_null())
            || [
                "geometry",
                "individual_track_id",
                "observation_period",
                "calendar_months",
                "uncertainty_interval",
            ]
            .iter()
            .any(|k| !row[*k].is_null())
            || [
                "dated_event_identity",
                "seasonal_playback_eligible",
                "physical_state_join_eligible",
            ]
            .iter()
            .any(|k| row[*k] != false)
            || entity["eddy_recurrence_ids"] != serde_json::json!([row["id"]])
        {
            return Err("Recurrence identity, units or admission scope mismatch".into());
        }
    }
    Ok(())
}
