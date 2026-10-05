//! Bind the two local Loop method diagnostics to their owner, receipts and frames.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;

pub fn validate(
    collections: &BTreeMap<String, Vec<Value>>,
    manifest: &Value,
) -> Result<(), String> {
    let records: Vec<_> = collections
        .get("diagnostics")
        .into_iter()
        .flatten()
        .filter(|r| {
            r["id"]
                .as_str()
                .is_some_and(|id| id.starts_with("diagnostic:loop-"))
        })
        .collect();
    if records.is_empty() {
        return Ok(());
    }
    if records.len() != 2 {
        return Err("Incomplete Loop method comparison".into());
    }
    let owner = collections["objects"]
        .iter()
        .find(|r| r["id"] == "current:loop")
        .ok_or("Missing Loop owner")?;
    if owner["diagnostic_ids"]
        != json!([
            "diagnostic:loop-noaa-20260925",
            "diagnostic:loop-adt-20260925"
        ])
    {
        return Err("Loop diagnostic owner links mismatch".into());
    }
    for record in records {
        let noaa = record["id"] == "diagnostic:loop-noaa-20260925";
        if !noaa && record["id"] != "diagnostic:loop-adt-20260925" {
            return Err("Unknown Loop diagnostic".into());
        }
        let doc = &record["document"];
        let raw = record["source_json"]
            .as_str()
            .ok_or("Missing original Loop diagnostic JSON")?;
        let original: Value =
            serde_json::from_str(raw).map_err(|_| "Invalid original Loop diagnostic JSON")?;
        if original != *doc
            || json!(format!("{:x}", Sha256::digest(raw.as_bytes())))
                != record["source_file_sha256"]
        {
            return Err("Loop diagnostic differs from checksum-bound original JSON".into());
        }
        let source_key = if noaa { "source_subset" } else { "source_file" };
        let source_hash = if noaa {
            "source_subset_sha256"
        } else {
            "source_sha256"
        };
        let selected = &doc[if noaa { "nominal" } else { "selected" }];
        if record["entity_id"] != "current:loop"
            || record["current_id"] != "loop"
            || doc["current_id"] != "loop"
            || record["observation_date"] != doc["observation_date"]
            || record["observation_date"] != "2026-09-25"
            || record["rank_eligible"] != false
            || doc["rank_eligible"] != false
            || ![
                "whole_current_length_km",
                "width_km",
                "annual_length_range_km",
                "confidence_interval_km",
            ]
            .iter()
            .all(|key| doc.get(key).is_some_and(Value::is_null))
            || record["status"] != doc["status"]
            || record["diagnostic_page"] != "almanac/loop-current-experiment.html"
        {
            return Err("Loop diagnostic identity or admission mismatch".into());
        }
        for (file, hash) in [
            (&record["source_file"], &record["source_file_sha256"]),
            (&doc[source_key], &doc[source_hash]),
            (&doc["protocol_file"], &doc["protocol_sha256"]),
        ] {
            let path = file.as_str().ok_or("Missing Loop source path")?;
            if hash.as_str().is_none_or(|h| h.len() != 64)
                || *hash != manifest["input_sha256"][path]
            {
                return Err("Loop source receipt mismatch".into());
            }
        }
        let frame_id = format!(
            "geometry-frame:{}",
            record["id"]
                .as_str()
                .unwrap()
                .trim_start_matches("diagnostic:")
        );
        let frame = collections
            .get("geometry_frames")
            .into_iter()
            .flatten()
            .find(|r| r["id"] == frame_id);
        let connected = if noaa {
            selected["gate_connected"] == true
        } else {
            selected.is_object()
        };
        if connected {
            let frame = frame.ok_or("Missing Loop diagnostic frame")?;
            if frame["entity_id"] != "current:loop"
                || frame["diagnostic_id"] != record["id"]
                || frame["observation_date"] != doc["observation_date"]
                || frame["rank_eligible"] != false
                || frame["coordinates_lon_lat"] != selected["coordinates_lon_lat"]
            {
                return Err("Loop diagnostic frame differs from source geometry".into());
            }
        } else if frame.is_some() {
            return Err("Unresolved Loop diagnostic has invented frame".into());
        }
        if !noaa
            && doc["comparison"]["noaa_diagnostic_sha256"]
                != manifest["input_sha256"]["research/loop-current-dated-streamline-20260925.json"]
        {
            return Err("Loop comparison source mismatch".into());
        }
    }
    Ok(())
}
