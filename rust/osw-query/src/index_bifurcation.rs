//! Historical branching-point cycles retain their own metric and layer.
use serde_json::{Value, json};
pub const SOURCE: &str = "research/indian-sec-monthly-bifurcation-extraction.json";

pub const PACIFIC_SOURCE: &str = "research/pacific-nec-monthly-bifurcation-extraction.json";
pub fn source(current_id: &str) -> Result<&'static str, String> {
    match current_id {
        "indian-south-equatorial" => Ok(SOURCE),
        "pacific-north-equatorial" => Ok(PACIFIC_SOURCE),
        _ => Err("Unknown branching current".into()),
    }
}

fn reading_bounds(value: &Value, center: f64, low: f64, high: f64) -> Result<[f64; 2], String> {
    let interval = value.as_array().ok_or("Missing reading allowance")?;
    if interval.len() != 2 {
        return Err("Invalid reading allowance".into());
    }
    let lo = interval[0].as_f64().ok_or("Missing lower reading bound")?;
    let hi = interval[1].as_f64().ok_or("Missing upper reading bound")?;
    if !(low..=high).contains(&lo) || !(low..=high).contains(&hi) || !(lo..=hi).contains(&center) {
        return Err("Latitude or reading allowance outside chart support".into());
    }
    if (lo - (center - 0.1)).abs() > 1e-6 || (hi - (center + 0.1)).abs() > 1e-6 {
        return Err("Changed graph-reading allowance".into());
    }
    Ok([lo, hi])
}

pub fn view(doc: &Value, series_id: &str, month: u8) -> Result<Value, String> {
    let current_id = doc["proposed_current_id"]
        .as_str()
        .ok_or("Missing branching current")?;
    let source_path = source(current_id)?;
    let pacific = current_id == "pacific-north-equatorial";
    let ids: &[&str] = if pacific {
        &["surface_ssh"]
    } else {
        &["surface_ssh", "wod_upper400"]
    };
    let (low, high) = if pacific { (8.0, 18.0) } else { (-19.0, -15.0) };
    let y = |latitude: f64| 210.0 - (latitude - low) * 160.0 / (high - low);
    if !(1..=12).contains(&month) || !ids.contains(&series_id) {
        return Err("Unknown branching series or month".into());
    }
    if doc["schema"] != "osw.monthly-bifurcation-plot-extraction.v1"
        || doc["metric"] != "regional_bifurcation_latitude"
        || doc["units"] != "degrees_north_signed"
        || doc["reading_interval_kind"]
            != "editorial_graph_reading_allowance_not_measurement_uncertainty"
        || doc["reading_allowance_degrees"].as_f64() != Some(0.1)
        || doc["chart_playback_eligible"] != true
        || doc["source_variability_envelope_extracted"] != pacific
        || (pacific
            && (doc["source_variability_kind"] != "caption_labelled_standard_deviation_range"
                || [
                    "statistical_denominator",
                    "standard_deviation_multiplier",
                    "confidence_probability",
                ]
                .iter()
                .any(|key| !doc[*key].is_null())))
        || [
            "geometry",
            "whole_current_length_km",
            "current_width_km",
            "annual_dimension_range_km",
        ]
        .iter()
        .any(|key| !doc[*key].is_null())
        || [
            "rank_eligible",
            "annual_extrema_eligible",
            "geographic_playback_eligible",
            "is_confidence_interval",
            "distinct_observed_years_inferred",
        ]
        .iter()
        .any(|key| doc[*key] != false)
    {
        return Err("Invalid regional branching-point scope".into());
    }
    let all = doc["series"].as_array().ok_or("Missing branching series")?;
    if all.len() != ids.len() {
        return Err("Unexpected source layers".into());
    }
    let mut curves = Vec::new();
    for &id in ids {
        let matches: Vec<_> = all.iter().filter(|row| row["id"] == id).collect();
        if matches.len() != 1 {
            return Err("Unresolved branching series".into());
        }
        let series = matches[0];
        let rows = series["months"]
            .as_array()
            .ok_or("Missing monthly values")?;
        if rows.len() != 12 || series["layer"].as_str().is_none_or(str::is_empty) {
            return Err("Missing monthly or layer support".into());
        }
        let mut points = Vec::new();
        for (index, row) in rows.iter().enumerate() {
            if row["month"].as_u64() != Some((index + 1) as u64) {
                return Err("Unordered or missing source month".into());
            }
            let latitude = row["approximate_latitude_degrees_north"]
                .as_f64()
                .ok_or("Missing branching latitude")?;
            let [lo, hi] = reading_bounds(
                &row["plot_reading_interval_degrees_north"],
                latitude,
                low,
                high,
            )?;
            let mut point = json!({"month":index+1,"latitude":latitude,"reading_interval":[lo,hi],"x":56. + index as f64*48.,"y":y(latitude),"reading_y":[y(hi),y(lo)]});
            if pacific {
                let band = row["approximate_source_standard_deviation_band_degrees_north"]
                    .as_array()
                    .ok_or("Missing source variability band")?;
                let allowances = row["band_endpoint_plot_reading_intervals_degrees_north"]
                    .as_array()
                    .ok_or("Missing band endpoint reading allowances")?;
                if band.len() != 2 || allowances.len() != 2 {
                    return Err("Invalid source variability band".into());
                }
                let lower = band[0].as_f64().ok_or("Missing lower source band")?;
                let upper = band[1].as_f64().ok_or("Missing upper source band")?;
                if !(lower..=upper).contains(&latitude) {
                    return Err("Source band does not contain mean".into());
                }
                reading_bounds(&allowances[0], lower, low, high)?;
                reading_bounds(&allowances[1], upper, low, high)?;
                point["source_band"] = json!([lower, upper]);
                point["source_band_y"] = json!([y(upper), y(lower)]);
                point["band_endpoint_reading_intervals"] = json!(allowances);
            } else if [
                "approximate_source_standard_deviation_band_degrees_north",
                "band_endpoint_plot_reading_intervals_degrees_north",
            ]
            .iter()
            .any(|key| !row[*key].is_null())
            {
                return Err("Unextracted source variability band".into());
            }
            points.push(point);
        }
        curves.push(json!({"id":id,"label":if id=="surface_ssh" {"Surface SSH"} else {"Upper 400 m"},"layer":series["layer"],"source_period":series["source_period"],"period_note":series["period_note"],"points":points,"rows":rows}));
    }
    let selected = curves
        .iter()
        .find(|curve| curve["id"] == series_id)
        .unwrap();
    Ok(
        json!({"ok":true,"section":"monthly_bifurcation","source":source_path,"current_id":current_id,"source_url":doc["source_url"],"source_locator":doc["source_locator"],"series_id":series_id,"month":month,"curves":curves,"selected":selected["points"][month as usize-1],"rows":selected["rows"],"layer":selected["layer"],"source_period":selected["source_period"],"period_note":selected["period_note"],"reading_interval_kind":doc["reading_interval_kind"],"scope":doc["scope_note"],"source_variability_kind":doc["source_variability_kind"],"source_variability_envelope_extracted":pacific,"chart":{"view_box":"0 0 640 250","latitude_ticks":((if pacific {vec![8,10,12,14,16,18]} else {vec![-19,-18,-17,-16,-15]}).iter().map(|value|json!({"latitude":value,"y":y(*value as f64)})).collect::<Vec<_>>())},"geographic_playback_eligible":false}),
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn pacific_band_keeps_reading_allowances_and_statistical_scope() {
        let doc: Value = serde_json::from_str(include_str!(
            "../../../research/pacific-nec-monthly-bifurcation-extraction.json"
        ))
        .unwrap();
        for month in 1..=12 {
            let result = view(&doc, "surface_ssh", month).unwrap();
            let row = &doc["series"][0]["months"][month as usize - 1];
            assert_eq!(result["source"], PACIFIC_SOURCE);
            assert_eq!(result["rows"], doc["series"][0]["months"]);
            assert_eq!(
                result["selected"]["source_band"],
                row["approximate_source_standard_deviation_band_degrees_north"]
            );
            assert_eq!(
                result["selected"]["band_endpoint_reading_intervals"],
                row["band_endpoint_plot_reading_intervals_degrees_north"]
            );
            assert_eq!(result["source_period"], doc["series"][0]["source_period"]);
            assert_eq!(
                result["chart"]["latitude_ticks"][0],
                json!({"latitude":8,"y":210.0})
            );
            assert_eq!(
                result["chart"]["latitude_ticks"][5],
                json!({"latitude":18,"y":50.0})
            );
        }
        assert!(source("invented").is_err());
        assert!(view(&doc, "wod_upper400", 1).is_err());
        for (pointer, value) in [
            ("/proposed_current_id", json!("invented")),
            ("/source_variability_kind", json!("confidence_interval")),
            ("/source_variability_envelope_extracted", json!(false)),
            ("/standard_deviation_multiplier", json!(1)),
            ("/statistical_denominator", json!(100)),
            ("/confidence_probability", json!(0.68)),
            ("/is_confidence_interval", json!(true)),
            ("/current_width_km", json!(100)),
            ("/annual_extrema_eligible", json!(true)),
            (
                "/series/0/months/0/approximate_source_standard_deviation_band_degrees_north",
                json!([12.4, 14.2]),
            ),
            (
                "/series/0/months/0/band_endpoint_plot_reading_intervals_degrees_north",
                json!([[10.0, 10.6], [14.1, 14.3]]),
            ),
            (
                "/series/0/months/0/band_endpoint_plot_reading_intervals_degrees_north",
                json!([[10.2, 10.4], [17.8, 18.1]]),
            ),
            ("/series/0/months/0/month", json!(2)),
        ] {
            let mut invalid = doc.clone();
            *invalid.pointer_mut(pointer).unwrap() = value;
            assert!(view(&invalid, "surface_ssh", 1).is_err(), "{pointer}");
        }
    }
    #[test]
    fn regional_cycles_reject_dimensions_gaps_and_wrong_units() {
        let doc: Value = serde_json::from_str(include_str!(
            "../../../research/indian-sec-monthly-bifurcation-extraction.json"
        ))
        .unwrap();
        let result = view(&doc, "surface_ssh", 6).unwrap();
        assert_eq!(result["selected"]["latitude"], -17.6);
        assert_eq!(result["rows"].as_array().unwrap().len(), 12);
        // Keep the original plot extraction's binary float, even beyond displayed precision.
        let upper = view(&doc, "wod_upper400", 4).unwrap();
        assert_eq!(
            upper["rows"][3]["raw_plot_latitude_degrees_north"].as_f64(),
            Some(-18.071613813501738)
        );
        assert!(view(&doc, "surface_ssh", 13).is_err());
        for (key, value) in [
            ("metric", json!("current_width")),
            ("units", json!("km")),
            ("current_width_km", json!(100)),
            ("geographic_playback_eligible", json!(true)),
        ] {
            let mut invalid = doc.clone();
            invalid[key] = value;
            assert!(view(&invalid, "surface_ssh", 1).is_err());
        }
        let mut invalid = doc.clone();
        invalid["series"][0]["months"][1]["month"] = json!(1);
        assert!(view(&invalid, "surface_ssh", 1).is_err());
    }
}
