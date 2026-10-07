//! Transverse instrument positions; no axis, full width or annual range inferred.
use serde_json::{Value, json};
use std::collections::BTreeSet;
pub const SOURCE: &str = "research/antilles-ab0505-400m-section-diagnostic.json";
pub fn view(doc: &Value) -> Result<Value, String> {
    if doc["schema"] != "osw.ladcp-section-diagnostic.v1"
        || doc["current_id"] != "antilles"
        || doc["status"] != "derived_local_diagnostic_requires_review"
        || doc["depth_m"] != 400
        || doc["geographic_role"] != "transverse_observation_section_not_current_axis"
        || [
            "tides_removed",
            "width_rank_eligible",
            "seasonal_playback_eligible",
        ]
        .iter()
        .any(|k| doc[*k] != false)
        || [
            "whole_current_length_km",
            "whole_current_width_km",
            "annual_length_range_km",
            "annual_width_range_km",
        ]
        .iter()
        .any(|k| doc.get(*k) != Some(&Value::Null))
    {
        return Err("Invalid observed-section identity or measurement scope".into());
    }
    let sections = doc["sections"]
        .as_array()
        .ok_or("Missing observed sections")?;
    if sections.len() != 2 {
        return Err("Incomplete observed occupation inventory".into());
    }
    let mut section_ids = BTreeSet::new();
    let mut positions = Vec::new();
    let mut result = json!({});
    for section in sections {
        let id = section["id"]
            .as_str()
            .ok_or("Missing observed occupation ID")?;
        let label = section["label"]
            .as_str()
            .ok_or("Missing observed occupation label")?;
        if !section_ids.insert(id)
            || section["half_peak_diagnostic"].get("full_width_km") != Some(&Value::Null)
        {
            return Err("Invalid observed occupation identity or full-width exclusion".into());
        }
        let samples = section["samples"]
            .as_array()
            .ok_or("Missing observed cast samples")?;
        if samples.is_empty() {
            return Err("Empty observed occupation".into());
        }
        let mut ids = BTreeSet::new();
        let mut stations = Vec::new();
        for sample in samples {
            if !sample["coordinates_lon_lat"]
                .as_array()
                .is_some_and(|xy| xy.len() == 2)
            {
                return Err("Observed cast coordinates must be a longitude/latitude pair".into());
            }
            let cast = sample["cast_id"]
                .as_str()
                .ok_or("Missing observed cast ID")?;
            let time = sample["average_cast_time_utc"]
                .as_str()
                .ok_or("Missing observed cast time")?;
            let quality = sample["quality_class"]
                .as_str()
                .ok_or("Missing observed quality")?;
            if !ids.insert(cast)
                || !crate::workspace::utc_timestamp(time)
                || !["usable", "caution"].contains(&quality)
                || ["northward_m_s", "error_velocity_m_s"].iter().any(|k| {
                    !sample
                        .get(*k)
                        .is_some_and(|v| v.is_null() || v.as_f64().is_some_and(f64::is_finite))
                })
            {
                return Err("Invalid observed cast identity, time, quality or velocity".into());
            }
            let record = json!({"id":cast,"map_features":[{"geometry":{"type":"Point","coordinates":sample["coordinates_lon_lat"]},"role":"observed_instrument_position_not_current_axis"}]});
            let scene = crate::map::scene(&[&record]);
            let primitive = scene["features"]
                .as_array()
                .and_then(|rs| rs.first())
                .map(|f| &f["primitive"])
                .ok_or("Invalid observed cast coordinates")?;
            let x = 60.
                + primitive["x"]
                    .as_f64()
                    .ok_or("Invalid observed cast projection")?
                    * 1480.
                    / 360.;
            let y = 90.
                + primitive["y"]
                    .as_f64()
                    .ok_or("Invalid observed cast projection")?
                    * 740.
                    / 180.;
            positions.push((x, y));
            let velocity = sample["northward_m_s"].as_f64();
            let value = velocity
                .map(|v| format!("{v:.3} m/s northward at 400 m"))
                .unwrap_or("no sample at 400 m".into());
            let text = format!("{cast} · {time} · {quality} · {value}");
            let error = sample["error_velocity_m_s"]
                .as_f64()
                .map(|v| format!("{v:.3} m/s"))
                .unwrap_or("no sample".into());
            stations.push(json!({"cast_id":cast,"x":x,"y":y,"label":text,"activation_text":format!("{text} · error velocity: {error}. Error velocity is not a confidence interval."),
                "color":if velocity.is_none(){"#a6aeb1"}else if quality=="caution"{"#f1b15b"}else{"#64dfce"}}));
        }
        let span = &section["half_peak_diagnostic"]["offshore_span_km"];
        let width_note = if span.is_null() {
            "Offshore half-peak boundary unresolved under quality rules.".into()
        } else {
            let value = span
                .as_f64()
                .filter(|v| v.is_finite() && *v >= 0.)
                .ok_or("Invalid observed one-sided span")?;
            format!(
                "About {} km one-sided sampled-peak-to-offshore-half-peak span; review pending.",
                value.round()
            )
        };
        result[id] = json!({"stations":stations,"status":format!("{label} · {} observed casts · 400 m instrument depth. {width_note} Full width, current length and annual ranges remain unresolved.",samples.len())});
    }
    let min_x = positions.iter().map(|p| p.0).fold(f64::INFINITY, f64::min);
    let max_x = positions
        .iter()
        .map(|p| p.0)
        .fold(f64::NEG_INFINITY, f64::max);
    let min_y = positions.iter().map(|p| p.1).fold(f64::INFINITY, f64::min);
    let max_y = positions
        .iter()
        .map(|p| p.1)
        .fold(f64::NEG_INFINITY, f64::max);
    let width = ((max_x - min_x) * 1.4)
        .max((max_y - min_y) * 2.8)
        .clamp(16., 1480.);
    let bounds = [
        ((min_x + max_x) / 2. - width / 2.).clamp(60., 1540. - width),
        ((min_y + max_y) / 2. - width / 4.).clamp(90., 830. - width / 2.),
        width,
        width / 2.,
    ];
    Ok(
        json!({"current_id":"antilles","view_box":bounds,"sections":result,"scope":"Observed instrument positions and local one-sided diagnostic only; not current edges, axis, footprint, full width or annual range."}),
    )
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn scope_missing_values_and_invalid_casts_are_rejected() {
        let sample = json!({"cast_id":"cast:1","coordinates_lon_lat":[-76.,26.],"average_cast_time_utc":"2005-05-08T16:01:34Z","quality_class":"usable","northward_m_s":null,"error_velocity_m_s":null});
        let mut doc = json!({"schema":"osw.ladcp-section-diagnostic.v1","current_id":"antilles","status":"derived_local_diagnostic_requires_review","depth_m":400,
            "geographic_role":"transverse_observation_section_not_current_axis","tides_removed":false,"width_rank_eligible":false,"seasonal_playback_eligible":false,
            "whole_current_length_km":null,"whole_current_width_km":null,"annual_length_range_km":null,"annual_width_range_km":null,
            "sections":[{"id":"first","label":"First","half_peak_diagnostic":{"full_width_km":null,"offshore_span_km":null},"samples":[sample]},
                {"id":"repeat","label":"Repeat","half_peak_diagnostic":{"full_width_km":null,"offshore_span_km":37.35},"samples":[sample]}]});
        let actual = view(&doc).unwrap();
        assert_eq!(
            actual["sections"]["first"]["stations"][0]["color"],
            "#a6aeb1"
        );
        assert!(
            actual["sections"]["repeat"]["status"]
                .as_str()
                .unwrap()
                .contains("37 km one-sided")
        );
        assert_eq!(actual["view_box"][2], 16.);
        for key in ["whole_current_width_km", "annual_width_range_km"] {
            let mut bad = doc.clone();
            bad.as_object_mut().unwrap().remove(key);
            assert!(view(&bad).is_err());
            bad = doc.clone();
            bad[key] = json!(74);
            assert!(view(&bad).is_err());
        }
        for (key, value) in [
            ("coordinates_lon_lat", json!([-76., 91.])),
            ("coordinates_lon_lat", json!([-76., 26., 400.])),
            ("average_cast_time_utc", json!("2005-02-30T16:01:34Z")),
            ("quality_class", json!("unknown")),
            ("northward_m_s", json!("unknown")),
        ] {
            let mut bad = doc.clone();
            bad["sections"][0]["samples"][0][key] = value;
            assert!(view(&bad).is_err());
        }
        doc["sections"][0]["samples"]
            .as_array_mut()
            .unwrap()
            .push(sample);
        assert!(view(&doc).is_err());
    }
}
