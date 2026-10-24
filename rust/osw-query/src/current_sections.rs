//! Pinned fixed-depth observational sections; never a moving current footprint.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};

pub(crate) const SOURCE: &str = "research/agulhas-asca-100m-monthly-sections.json";
const CONTRACT: &str = "research/agulhas-asca-100m-query-contract.json";
const APPROVED: &str = include_str!("../../../research/agulhas-asca-100m-query-contract.json");

pub(crate) fn validate(bundle: &Bundle) -> Result<(), String> {
    let declared = bundle.manifest["editorial_collections"]
        .as_array()
        .is_some_and(|names| names.iter().any(|name| name == "current_sections"));
    let joined = bundle.collections.get("objects").is_some_and(|objects| {
        objects
            .iter()
            .any(|object| object.get("current_section_ids").is_some())
    });
    if !bundle.collections.contains_key("current_sections")
        && bundle.manifest["input_sha256"][SOURCE].is_null()
        && bundle.manifest["input_sha256"][CONTRACT].is_null()
        && !declared
        && !joined
    {
        return Ok(());
    }
    let approved: Value = serde_json::from_str(APPROVED).map_err(|e| e.to_string())?;
    if bundle.manifest["input_sha256"][CONTRACT]
        != format!("{:x}", Sha256::digest(APPROVED.as_bytes()))
    {
        return Err("ASCA section source contract changed".into());
    }
    for (file, hash) in [
        ("raw_profile_file", "raw_profile_sha256"),
        ("monthly_section_file", "monthly_section_sha256"),
        ("source_acquisition_file", "source_acquisition_sha256"),
        ("builder_file", "builder_sha256"),
        ("protocol_file", "protocol_sha256"),
    ] {
        let path = approved[file].as_str().ok_or("Missing ASCA dependency")?;
        if bundle.manifest["input_sha256"][path] != approved[hash] {
            return Err(format!("ASCA section dependency changed: {path}"));
        }
    }
    let receipt = &bundle.manifest["current_section_receipts"][SOURCE];
    let raw = receipt["source_json"]
        .as_str()
        .ok_or("Missing ASCA monthly source")?;
    let hash = format!("{:x}", Sha256::digest(raw.as_bytes()));
    if hash != approved["monthly_section_sha256"]
        || receipt["source_sha256"] != hash
        || receipt["source_file"] != SOURCE
    {
        return Err("ASCA source bytes disagree with frozen section contract".into());
    }
    let source: Value = serde_json::from_str(raw).map_err(|e| e.to_string())?;
    let expected = source["frames"].as_array().ok_or("Missing ASCA frames")?;
    if bundle.collections.get("current_sections") != Some(expected) {
        return Err("ASCA query sections disagree with frozen source".into());
    }
    let objects = bundle
        .collections
        .get("objects")
        .ok_or("Missing section owners")?;
    if !objects.iter().any(|owner| owner["id"] == "current:agulhas") {
        return Err("Missing Agulhas section owner".into());
    }
    for owner in objects {
        let ids: Vec<Value> = expected
            .iter()
            .filter(|row| row["entity_id"] == owner["id"])
            .map(|row| row["id"].clone())
            .collect();
        let count = owner["capabilities"].get("current_sections");
        if owner["current_section_ids"] != json!(ids)
            || count.is_some_and(|value| value != ids.len())
            || (!ids.is_empty() && count.is_none())
        {
            return Err("ASCA owner section links or coverage changed".into());
        }
    }
    Ok(())
}

pub(crate) fn scene(matches: &[&Value], all: &[Value]) -> Value {
    let specs = [
        ("v", "Across-array velocity; southwest negative", "m/s"),
        ("U", "Along-array velocity; southeast positive", "m/s"),
        ("temp", "Temperature", "degrees C"),
        ("sal", "Practical salinity", "PSU"),
    ];
    let fields: Vec<Value> = specs
        .iter()
        .map(|(key, label, unit)| {
            let mut low = f64::INFINITY;
            let mut high = f64::NEG_INFINITY;
            for frame in all {
                if let Some(means) = frame["field_statistics"][key]["mean"].as_array() {
                    for (i, mean) in means.iter().enumerate() {
                        if let Some(mean) = mean.as_f64() {
                            let sd = frame["field_statistics"][key]["sample_sd"][i]
                                .as_f64()
                                .unwrap_or(0.0);
                            low = low.min(mean - sd);
                            high = high.max(mean + sd);
                        }
                    }
                }
            }
            if !low.is_finite() || !high.is_finite() {
                low = 0.0;
                high = 1.0;
            }
            if *unit == "m/s" {
                let bound = low.abs().max(high.abs());
                low = -bound;
                high = bound;
            }
            let pad = (high - low).max(0.01) * 0.05;
            json!({"key":key,"label":label,"unit":unit,"y_domain":[low-pad,high+pad]})
        })
        .collect();
    let mut frames: Vec<Value> = matches.iter().map(|frame| {
        json!({"id":frame["id"],"label":frame["label"],"year":frame["year"],"month":frame["month"],
            "depth_m":frame["depth_m"],"sample_count":frame["sample_count"],
            "first_observed_at":frame["first_observed_at"],"last_observed_at":frame["last_observed_at"],
            "complete_calendar_time_support":frame["complete_calendar_time_support"],
            "distance_m":frame["distance_m"],"field_statistics":frame["field_statistics"],
            "paired_vector_statistics":frame["paired_vector_statistics"],"source_query":frame["source_query"]})
    }).collect();
    frames.sort_by_key(|frame| (frame["year"].as_u64(), frame["month"].as_u64()));
    json!({"kind":"current_sections","title":"Agulhas / ASCA 100 m sections",
        "scope":"Processed observational fields at one fixed array, April 2016–June 2018. Monthly available-record means; spread is sample standard deviation, not measurement error or a confidence interval. 500 m output spacing is interpolation, not instrument resolution. Missing components remain gaps. No whole-current width, geographic edges, seasonal extrema or climatology.",
        "source_url":"https://doi.org/10.5281/zenodo.20515068",
        "credit":"Beal Lab / Agulhas System Climate Array / product 2.0 / CC BY 4.0",
        "fields":fields,"frames":frames,"full_source_frame_count":all.len(),
        "chronological_frame_interpolation":false,"seasonal_cycle":false})
}
