//! Historical branching-point cycles retain their own metric and layer.
use serde_json::{Value, json};
pub const SOURCE: &str = "research/indian-sec-monthly-bifurcation-extraction.json";

pub fn view(doc: &Value, series_id: &str, month: u8) -> Result<Value, String> {
    if !(1..=12).contains(&month) || !["surface_ssh", "wod_upper400"].contains(&series_id) {
        return Err("Unknown branching series or month".into());
    }
    if doc["schema"] != "osw.monthly-bifurcation-plot-extraction.v1"
        || doc["metric"] != "regional_bifurcation_latitude"
        || doc["units"] != "degrees_north_signed"
        || doc["proposed_current_id"] != "indian-south-equatorial"
        || doc["reading_interval_kind"]
            != "editorial_graph_reading_allowance_not_measurement_uncertainty"
        || doc["reading_allowance_degrees"].as_f64() != Some(0.1)
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
    if all.len() != 2 {
        return Err("Expected two source layers".into());
    }
    let mut curves = Vec::new();
    for id in ["surface_ssh", "wod_upper400"] {
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
            let interval = row["plot_reading_interval_degrees_north"]
                .as_array()
                .ok_or("Missing reading allowance")?;
            if interval.len() != 2 {
                return Err("Invalid reading allowance".into());
            }
            let lo = interval[0].as_f64().ok_or("Missing lower reading bound")?;
            let hi = interval[1].as_f64().ok_or("Missing upper reading bound")?;
            if !(-19.0..=-15.0).contains(&lo)
                || !(-19.0..=-15.0).contains(&hi)
                || !(lo..=hi).contains(&latitude)
            {
                return Err("Latitude or reading allowance outside chart support".into());
            }
            if (lo - (latitude - 0.1)).abs() > 1e-6 || (hi - (latitude + 0.1)).abs() > 1e-6 {
                return Err("Changed graph-reading allowance".into());
            }
            points.push(json!({"month":index+1,"latitude":latitude,"reading_interval":[lo,hi],"x":56. + index as f64*48.,"y":210. - (latitude+19.)*40.,"reading_y":[210. - (hi+19.)*40.,210. - (lo+19.)*40.]}));
        }
        curves.push(json!({"id":id,"label":if id=="surface_ssh" {"Surface SSH"} else {"Upper 400 m"},"layer":series["layer"],"source_period":series["source_period"],"period_note":series["period_note"],"points":points,"rows":rows}));
    }
    let selected = curves
        .iter()
        .find(|curve| curve["id"] == series_id)
        .unwrap();
    Ok(
        json!({"ok":true,"section":"monthly_bifurcation","source":SOURCE,"source_url":doc["source_url"],"source_locator":doc["source_locator"],"series_id":series_id,"month":month,"curves":curves,"selected":selected["points"][month as usize-1],"rows":selected["rows"],"layer":selected["layer"],"source_period":selected["source_period"],"period_note":selected["period_note"],"reading_interval_kind":doc["reading_interval_kind"],"scope":doc["scope_note"],"chart":{"view_box":"0 0 640 250","latitude_ticks":([-19,-18,-17,-16,-15].iter().map(|value|json!({"latitude":value,"y":210.-(*value as f64+19.)*40.})).collect::<Vec<_>>())},"geographic_playback_eligible":false}),
    )
}

#[cfg(test)]
mod tests {
    use super::*;
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
