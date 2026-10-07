//! Exact query projections of checked hourly model sections, not current geometry.
use crate::{Bundle, norkyst_data};
use serde_json::{Value, json};

fn available(point: &Value) -> bool {
    ["salinity", "u_eastward", "v_northward"]
        .iter()
        .all(|key| !point[*key].is_null())
}

fn projection(timeline: &Value, maps: &Value, inputs: &Value) -> (Vec<Value>, Vec<Value>) {
    let mut frames = Vec::new();
    let mut samples = Vec::new();
    for (frame_index, original) in timeline["frames"].as_array().unwrap().iter().enumerate() {
        let date = original["date"].as_str().unwrap();
        let mapped = &maps["frames"][frame_index];
        let frame_id = format!("model-frame:norkyst-ingoy:{date}");
        let points = original["profile"].as_array().unwrap();
        let context = json!({
            "entity_id":format!("current:{}",timeline["current_context_id"].as_str().unwrap()),
            "current_id":timeline["current_context_id"],"date":date,"year":2024,
            "month":frame_index+1,"sample_time_utc":original["sample_time_utc"],
            "depth_m":timeline["section"]["depth_m"],"annual_extrema_eligible":false,
            "width_rank_eligible":false,"state_footprint_join_eligible":false,
            "source_file":norkyst_data::TIMELINE,"source_sha256":inputs[norkyst_data::TIMELINE]
        });
        let mut frame = context.clone();
        frame.as_object_mut().unwrap().extend(json!({
            "id":frame_id,"label":format!("NorKyst Ingøy section — {date}"),
            "record_type":"model_section_frame","source_project":timeline["source_project"],
            "source_license":timeline["source_license"],"credit":timeline["credit"],
            "source_catalog_url":timeline["source_catalog_url"],"source_url":original["source_url"],
            "receipt_file":original["receipt_file"],"receipt_sha256":original["receipt_sha256"],
            "section":timeline["section"],"sampling_rule":timeline["sampling_rule"],
            "interpolation":timeline["interpolation"],"limitations":timeline["limitations"],
            "current_length_km":null,"current_width_km":null,
            "field_units":{"salinity":"1","u_eastward":"m/s","v_northward":"m/s"},
            "sample_count":points.len(),"available_sample_count":points.iter().filter(|p|available(p)).count(),
            "map_figure":mapped["figure"],"map_figure_sha256":mapped["figure_sha256"],
            "map_role":mapped["map_role"],"map_source_file":norkyst_data::MAPS,
            "map_source_sha256":inputs[norkyst_data::MAPS],
            "url":format!("norkyst-section.html?date={date}")
        }).as_object().unwrap().clone());
        frames.push(frame);
        for (sample_index, point) in points.iter().enumerate() {
            let mut sample = context.clone();
            let row = sample.as_object_mut().unwrap();
            row.extend(json!({
                "id":format!("model-sample:norkyst-ingoy:{date}:{sample_index:03}"),
                "label":format!("NorKyst {date} — section sample {sample_index:03}"),
                "record_type":"model_section_sample","model_frame_id":frame_id,
                "sample_index":sample_index,"source_path":format!("/frames/{frame_index}/profile/{sample_index}"),
                "sample_role":"interpolated_fixed_section_model_field_not_current_boundary",
                "field_values_available":available(point)
            }).as_object().unwrap().clone());
            row.extend(point.as_object().unwrap().clone());
            samples.push(sample);
        }
    }
    (frames, samples)
}

pub fn validate(bundle: &Bundle) -> Result<(), String> {
    if !["model_frames", "model_samples"]
        .iter()
        .any(|name| bundle.collections.contains_key(*name))
    {
        return Ok(()); // Earlier source snapshots have no query projection.
    }
    let timeline = crate::atlas_data::document(
        bundle,
        norkyst_data::TIMELINE,
        "osw.norkyst-section-timeline.v1",
    )?;
    let maps =
        crate::atlas_data::document(bundle, norkyst_data::MAPS, "osw.norkyst-map-frames.v1")?;
    norkyst_data::scope(&timeline, norkyst_data::TIMELINE)?;
    norkyst_data::scope(&maps, norkyst_data::MAPS)?;
    norkyst_data::synchronized(&timeline, &maps)?;
    let (frames, samples) = projection(&timeline, &maps, &bundle.manifest["input_sha256"]);
    for (name, expected) in [("model_frames", &frames), ("model_samples", &samples)] {
        if bundle.collections.get(name) != Some(expected) {
            return Err(format!(
                "Model query projection disagrees with checked source: {name}"
            ));
        }
    }
    let owner = bundle.collections["objects"]
        .iter()
        .find(|row| row["id"] == "current:norwegian-coastal")
        .ok_or("Missing model section context owner")?;
    let expected_ids = Value::Array(frames.iter().map(|row| row["id"].clone()).collect());
    if owner["model_frame_ids"] != expected_ids
        || owner["capabilities"]["model_frames"] != frames.len()
        || owner["capabilities"]["model_samples"] != samples.len()
    {
        return Err("Invalid model section context links or counts".into());
    }
    Ok(())
}

pub fn scene(records: &[&Value], collection: &str) -> Value {
    let projected: Vec<Value> = records.iter().map(|row| {
        let (geometry, role) = if collection == "model_frames" {
            let section = &row["section"];
            (json!({"type":"LineString","coordinates":[
                [section["longitude_degrees_east"],section["start_latitude"]],
                [section["longitude_degrees_east"],section["end_latitude"]]
            ]}), "fixed_model_section_support_not_current_boundary")
        } else {
            (json!({"type":"Point","coordinates":row["coordinates_lon_lat"]}),
             "model_section_sampling_site_including_missing_field_values")
        };
        json!({"id":row["id"],"label":row["label"],"type":row["record_type"],
            "map_features":[{"geometry":geometry,"role":role,
                "note":"Fixed 24 E meridional model section at 10 m. Sampling limits and positions are not current boundaries or state footprints. Missing field values remain gaps."}]})
    }).collect();
    let refs = projected.iter().collect::<Vec<_>>();
    let mut scene = crate::map::scene(&refs);
    scene["inspection_collection"] = json!(collection);
    scene["scope"] = json!(
        "All matching hourly model records across every results page. Fixed section support and sampling positions only; missing fields retain their known sample locations. These are not observations, monthly means, current axes, edges, widths, occupied footprints or state containment. No time interpolation or annual extrema."
    );
    let mut bounds: Option<[f64; 4]> = None;
    for row in &projected {
        let geometry = &row["map_features"][0]["geometry"];
        let coordinates = if geometry["type"] == "Point" {
            vec![&geometry["coordinates"]]
        } else {
            geometry["coordinates"].as_array().unwrap().iter().collect()
        };
        for coordinate in coordinates {
            if let Some((x, y)) = crate::map::point(coordinate) {
                bounds = Some(match bounds {
                    None => [x, y, x, y],
                    Some(b) => [b[0].min(x), b[1].min(y), b[2].max(x), b[3].max(y)],
                });
            }
        }
    }
    scene["display_bounds"] = json!(bounds);
    for feature in scene["features"].as_array_mut().unwrap() {
        let row = records
            .iter()
            .find(|r| r["id"] == feature["entity_id"])
            .unwrap();
        feature["inspection_collection"] = json!(collection);
        feature["owner_entity_id"] = row["entity_id"].clone();
        feature["model_date"] = row["date"].clone();
        feature["sample_time_utc"] = row["sample_time_utc"].clone();
        feature["depth_m"] = row["depth_m"].clone();
        if collection == "model_samples" {
            feature["field_values_available"] = row["field_values_available"].clone();
            feature["model_frame_id"] = row["model_frame_id"].clone();
        }
    }
    scene
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn model_projection_preserves_hourly_support_nulls_and_unranked_scope() {
        let mut timeline: Value = serde_json::from_str(include_str!(
            "../../../research/norkyst-ingoy-2024-section-timeline.json"
        ))
        .unwrap();
        let maps: Value = serde_json::from_str(include_str!(
            "../../../research/norkyst-ingoy-2024-map-frames.json"
        ))
        .unwrap();
        timeline["frames"][0]["profile"][1]["u_eastward"] = Value::Null;
        let (frames, samples) = projection(&timeline, &maps, &json!({}));
        assert_eq!(frames.len(), 12);
        assert_eq!(samples.len(), 2292);
        assert_eq!(samples[1]["u_eastward"], Value::Null);
        assert_eq!(samples[1]["field_values_available"], false);
        assert_eq!(frames[0]["sample_time_utc"], "2024-01-15T12:00:00Z");
        assert_eq!(frames[0]["current_width_km"], Value::Null);
        assert_eq!(frames[0]["current_length_km"], Value::Null);
        assert_eq!(
            samples[2291]["coordinates_lon_lat"],
            timeline["frames"][11]["profile"][190]["coordinates_lon_lat"]
        );
        assert_eq!(samples[2291]["state_footprint_join_eligible"], false);
        let mapped = scene(&[&samples[1]], "model_samples");
        assert_eq!(mapped["mapped_objects"], 1); // Position is known despite a missing field.
        assert_eq!(mapped["features"][0]["field_values_available"], false);
        assert!(mapped["features"][0]["observation_date"].is_null());
        assert_eq!(mapped["features"][0]["model_date"], "2024-01-15");
        assert_eq!(
            mapped["features"][0]["inspection_collection"],
            "model_samples"
        );
        let support = scene(&[&frames[0]], "model_frames");
        assert_eq!(support["mapped_objects"], 1);
        assert_eq!(
            support["features"][0]["role"],
            "fixed_model_section_support_not_current_boundary"
        );
    }
}
