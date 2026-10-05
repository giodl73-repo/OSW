//! Scoped width samples retain their exact parent diagnostic and reading support.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;

pub fn validate(
    collections: &BTreeMap<String, Vec<Value>>,
    manifest: &Value,
) -> Result<(), String> {
    for row in collections.get("width_samples").into_iter().flatten() {
        let diagnostic = collections
            .get("diagnostics")
            .and_then(|rs| rs.iter().find(|r| r["id"] == row["diagnostic_id"]))
            .ok_or("Unresolved width sample diagnostic")?;
        let document = &diagnostic["document"];
        let family = match diagnostic["id"].as_str() {
            Some("diagnostic:leeuwin-monthly-width") => "leeuwin_monthly_fitted_plot",
            Some("diagnostic:kuroshio-seasonal-width") => "kuroshio_seasonal_profile_plot",
            Some("diagnostic:necc-monthly-section") => "necc_monthly_connected_component",
            Some("diagnostic:gulf-stream-widths") => "gulf_stream_dated_half_peak_section",
            Some("diagnostic:yucatan-noaa-sections" | "diagnostic:yucatan-adt-sections") => {
                "loop_dated_half_peak_section"
            }
            _ => return Err("Unsupported scoped width sample family".into()),
        };
        if row["sample_family"] != family {
            return Err("Width sample family differs from diagnostic".into());
        }
        let path = row["sample_path"]
            .as_str()
            .ok_or("Missing width sample path")?;
        let sample = document
            .pointer(path)
            .ok_or("Unresolved source width sample")?;
        if !sample.is_object() {
            return Err("Width source sample must be an object".into());
        }
        let parts: Vec<_> = path.split('/').collect();
        let dated = [
            "gulf_stream_dated_half_peak_section",
            "loop_dated_half_peak_section",
        ]
        .contains(&family);
        if family == "loop_dated_half_peak_section" {
            let owner = collections
                .get("objects")
                .into_iter()
                .flatten()
                .find(|o| o["id"] == row["entity_id"])
                .ok_or("Missing section sample owner")?;
            if !owner["width_sample_ids"]
                .as_array()
                .is_some_and(|ids| ids.contains(&row["id"]))
            {
                return Err("Missing section sample owner join".into());
            }
            let raw = diagnostic["source_json"]
                .as_str()
                .ok_or("Missing section source JSON")?;
            let original: Value =
                serde_json::from_str(raw).map_err(|_| "Invalid section source JSON")?;
            let file = diagnostic["source_file"]
                .as_str()
                .ok_or("Missing section source file")?;
            if original != *document
                || json!(format!("{:x}", Sha256::digest(raw.as_bytes())))
                    != diagnostic["source_file_sha256"]
                || diagnostic["source_file_sha256"] != manifest["input_sha256"][file]
                || row["latitude_degrees_north"] != document["section_latitude"]
            {
                return Err("Section source/latitude binding mismatch".into());
            }
        }
        if family == "kuroshio_seasonal_profile_plot" {
            if parts.len() != 5
                || parts[1] != "seasons"
                || parts[3] != "samples"
                || row["phase_path"] != format!("/seasons/{}", parts[2])
            {
                return Err("Width sample phase/path mismatch".into());
            }
        } else if parts.len() != 3
            || parts[1] != if dated { "frames" } else { "months" }
            || !row["phase_path"].is_null()
        {
            return Err("Monthly sample path mismatch".into());
        }
        let mut context = document.clone();
        let object = context.as_object_mut().ok_or("Invalid width diagnostic")?;
        object.remove("months");
        object.remove("seasons");
        object.remove("frames");
        let phase = if let Some(path) = row["phase_path"].as_str() {
            let mut phase = document
                .pointer(path)
                .ok_or("Unresolved sample phase")?
                .clone();
            phase
                .as_object_mut()
                .ok_or("Invalid sample phase")?
                .remove("samples");
            phase
        } else {
            Value::Null
        };
        let expected_value = if dated {
            &sample["approximate_section_span_km"]
        } else if row["sample_family"] == "necc_monthly_connected_component" {
            &sample["zero_crossing"]["span_km"]
        } else {
            &sample["approximate_width_km"]
        };
        let (month, year) = if dated {
            let day = sample["date"]
                .as_str()
                .filter(|d| crate::temporal::valid_day(d))
                .ok_or("Invalid dated width sample day")?;
            (
                json!(day[5..7].parse::<u8>().unwrap()),
                json!(day[..4].parse::<u16>().unwrap()),
            )
        } else {
            (sample["month"].clone(), document["year"].clone())
        };
        if row["source_sample"] != *sample
            || row["source_context"] != context
            || row["source_phase"] != phase
            || row["value_km"] != *expected_value
            || row["plot_reading_interval_km"] != sample["plot_reading_interval_km"]
            || row["current_id"] != document["current_id"]
            || row["entity_id"]
                != json!(format!(
                    "current:{}",
                    document["current_id"]
                        .as_str()
                        .ok_or("Missing sample current")?
                ))
            || row["month"] != month
            || row["year"] != year
        {
            return Err("Width sample differs from its source diagnostic".into());
        }
        let metric = if dated {
            &document["metric"]
        } else {
            document
                .get("width_metric")
                .unwrap_or(&document["width_equation"])
        };
        let longitude = if dated {
            &document["section_longitude"]
        } else {
            sample
                .get("longitude_degrees_east")
                .unwrap_or(&document["section_longitude_degrees_east"])
        };
        let label = if dated {
            &sample["date"]
        } else if phase.is_null() {
            &sample["label"]
        } else {
            &phase["label"]
        };
        if row["metric"] != *metric
            || row["longitude_degrees_east"] != *longitude
            || row["phase_label"] != *label
            || row["source_url"]
                != if dated {
                    sample["source_url"].clone()
                } else {
                    document["source_url"].clone()
                }
        {
            return Err("Width sample support differs from source".into());
        }
        let status = if dated {
            &sample["nominal"]["status"]
        } else {
            sample
                .get("status")
                .or_else(|| sample["zero_crossing"].get("status"))
                .unwrap_or(&document["status"])
        };
        if row["status"] != *status {
            return Err("Width sample status differs from source".into());
        }
        for (key, expected) in [
            (
                "observation_date",
                if dated {
                    sample["date"].clone()
                } else {
                    Value::Null
                },
            ),
            (
                "source_algorithm",
                if dated {
                    sample["source_algorithm"].clone()
                } else {
                    Value::Null
                },
            ),
            (
                "diagnostic_sensitivity_interval_km",
                if dated {
                    sample["threshold_sensitivity_span_km"].clone()
                } else {
                    Value::Null
                },
            ),
            (
                "sampling_bracket_interval_km",
                if dated {
                    sample["nominal"]["grid_bracket_span_km"].clone()
                } else {
                    Value::Null
                },
            ),
            (
                "resolution_review_required",
                if dated {
                    sample["nominal"]["resolution_review_required"].clone()
                } else {
                    Value::Null
                },
            ),
        ] {
            if row[key] != expected {
                return Err(format!("Width sample source support differs in {key}"));
            }
        }
        for key in [
            "whole_current_representative",
            "width_rank_eligible",
            "is_confidence_interval",
        ] {
            if row[key] != false || document[key] != false {
                return Err("Scoped samples cannot define ranked or whole-current widths".into());
            }
        }
        if !row["annual_width_range_km"].is_null()
            || !document["annual_width_range_km"].is_null()
            || !row["measurement_uncertainty_interval_km"].is_null()
        {
            return Err("Unsupported sample uncertainty or annual range".into());
        }
    }
    Ok(())
}
