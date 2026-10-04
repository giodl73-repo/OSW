//! Scoped width samples retain their exact parent diagnostic and reading support.
use serde_json::{Value, json};
use std::collections::BTreeMap;

pub fn validate(collections: &BTreeMap<String, Vec<Value>>) -> Result<(), String> {
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
        if family == "kuroshio_seasonal_profile_plot" {
            if parts.len() != 5
                || parts[1] != "seasons"
                || parts[3] != "samples"
                || row["phase_path"] != format!("/seasons/{}", parts[2])
            {
                return Err("Width sample phase/path mismatch".into());
            }
        } else if parts.len() != 3 || parts[1] != "months" || !row["phase_path"].is_null() {
            return Err("Monthly sample path mismatch".into());
        }
        let mut context = document.clone();
        let object = context.as_object_mut().ok_or("Invalid width diagnostic")?;
        object.remove("months");
        object.remove("seasons");
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
        let expected_value = if row["sample_family"] == "necc_monthly_connected_component" {
            &sample["zero_crossing"]["span_km"]
        } else {
            &sample["approximate_width_km"]
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
            || row["month"] != sample["month"]
            || row["year"] != document["year"]
        {
            return Err("Width sample differs from its source diagnostic".into());
        }
        let metric = document
            .get("width_metric")
            .unwrap_or(&document["width_equation"]);
        let longitude = sample
            .get("longitude_degrees_east")
            .unwrap_or(&document["section_longitude_degrees_east"]);
        let label = if phase.is_null() {
            &sample["label"]
        } else {
            &phase["label"]
        };
        if row["metric"] != *metric
            || row["longitude_degrees_east"] != *longitude
            || row["phase_label"] != *label
            || row["source_url"] != document["source_url"]
        {
            return Err("Width sample support differs from source".into());
        }
        let status = sample
            .get("status")
            .or_else(|| sample["zero_crossing"].get("status"))
            .unwrap_or(&document["status"]);
        if row["status"] != *status {
            return Err("Width sample status differs from source".into());
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
