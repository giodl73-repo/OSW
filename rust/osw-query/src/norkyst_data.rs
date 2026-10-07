//! Pinned hourly model sections; no current boundary or annual measurement.
use serde_json::{Value, json};
pub const TIMELINE: &str = "research/norkyst-ingoy-2024-section-timeline.json";
pub const MAPS: &str = "research/norkyst-ingoy-2024-map-frames.json";

pub fn scope(doc: &Value, path: &str) -> Result<(), String> {
    if doc["source_license"] != "CC-BY-4.0" || doc["annual_extrema_eligible"] != false {
        return Err("Invalid atlas NorKyst license or annual scope".into());
    }
    if path == TIMELINE {
        if doc["status"] != "model_section_diagnostic_not_canonical_current_measurement"
            || doc["current_context_id"] != "norwegian-coastal"
            || doc["year"] != 2024
            || doc["source_project"] != "Norkyst_v3"
            || doc["section"]
                != json!({"longitude_degrees_east":24,"start_latitude":71.1,"end_latitude":73,"depth_m":10,"sample_spacing_degrees":0.01,"orientation":"fixed meridional section, not a fitted flow-normal section","location_role":"Ingoy region coastal-to-offshore diagnostic; selected limits are not current boundaries"})
        {
            return Err("Invalid atlas NorKyst section scope".into());
        }
    } else if path == MAPS {
        if doc["status"] != "model_field_display_not_canonical_current_geometry"
            || doc["state_footprint_join_eligible"] != false
            || doc["rules"]
                != json!({"salinity_color_limits":[33.0,35.2],"velocity_arrow_grid_stride":5,"velocity_arrow_scale":0.07,"velocity_arrow_reference_m_s":0.5,"coordinate_system":"original source polar stereographic grid; relative projected kilometres","vector_rotation":"True east/north velocity bearing projected using a 1 km geodesic direction probe; direction normalized, speed preserved. Arrows indicate instantaneous model velocity, not trajectories.","temporal_interpolation":false,"named_current_footprint":false})
        {
            return Err("Invalid atlas NorKyst map scope".into());
        }
    } else {
        return Err("Unsupported atlas NorKyst source".into());
    }
    let frames = doc["frames"]
        .as_array()
        .ok_or("Missing atlas NorKyst frames")?;
    if frames.len() != 12 {
        return Err("Incomplete atlas NorKyst preselected dates".into());
    }
    for (i, frame) in frames.iter().enumerate() {
        let date = format!("2024-{:02}-15", i + 1);
        if frame["date"] != date || frame["sample_time_utc"] != format!("{date}T12:00:00Z") {
            return Err("Changed atlas NorKyst hourly sampling support".into());
        }
        if path == TIMELINE {
            if ["current_length_km", "current_width_km"]
                .iter()
                .any(|k| frame.get(*k) != Some(&Value::Null))
            {
                return Err("Invented atlas NorKyst current dimension".into());
            }
            let profile = frame["profile"]
                .as_array()
                .ok_or("Missing atlas NorKyst profile")?;
            if profile.len() != 191 {
                return Err("Incomplete atlas NorKyst section samples".into());
            }
            let mut previous = -1.;
            for (j, point) in profile.iter().enumerate() {
                let xy = point["coordinates_lon_lat"]
                    .as_array()
                    .ok_or("Missing model sample coordinates")?;
                let distance = point["distance_from_section_start_km"]
                    .as_f64()
                    .filter(|v| v.is_finite())
                    .ok_or("Invalid model section distance")?;
                if xy.len() != 2
                    || xy[0].as_f64() != Some(24.)
                    || !xy[1]
                        .as_f64()
                        .is_some_and(|v| (v - (71.1 + j as f64 * 0.01)).abs() < 1e-8)
                    || distance < 0.
                    || distance <= previous
                    || ["salinity", "u_eastward", "v_northward"].iter().any(|k| {
                        !point
                            .get(*k)
                            .is_some_and(|v| v.is_null() || v.as_f64().is_some_and(f64::is_finite))
                    })
                {
                    return Err("Invalid atlas NorKyst sample position, order or field".into());
                }
                previous = distance;
            }
        } else if frame["map_role"]
            != "regional_model_field_subset_not_named_current_boundary_or_state_footprint"
        {
            return Err("Invalid atlas NorKyst field display role".into());
        }
    }
    Ok(())
}

pub fn dependencies(doc: &Value, path: &str, inputs: &Value) -> Result<(), String> {
    let kinds = if path == MAPS {
        vec!["acquisition", "generator", "protocol", "projection_helper"]
    } else {
        vec!["acquisition", "generator", "protocol"]
    };
    for kind in kinds {
        let file = doc[format!("{kind}_file")]
            .as_str()
            .ok_or("Missing atlas NorKyst provenance file")?;
        let hash = &doc[format!("{kind}_sha256")];
        if !hash.is_string() || inputs.get(file) != Some(hash) {
            return Err("Stale atlas NorKyst provenance".into());
        }
    }
    for frame in doc["frames"]
        .as_array()
        .ok_or("Missing atlas model frames")?
    {
        let pairs = if path == MAPS {
            vec![
                ("receipt_file", "receipt_sha256"),
                ("figure", "figure_sha256"),
            ]
        } else {
            vec![("receipt_file", "receipt_sha256")]
        };
        for (file_key, hash_key) in pairs {
            let file = frame[file_key]
                .as_str()
                .ok_or("Missing atlas NorKyst source support")?;
            if !frame[hash_key].is_string() || inputs.get(file) != Some(&frame[hash_key]) {
                return Err("Stale atlas NorKyst frame support".into());
            }
        }
    }
    Ok(())
}

pub fn synchronized(timeline: &Value, maps: &Value) -> Result<(), String> {
    for (section, map) in timeline["frames"]
        .as_array()
        .ok_or("Missing section frames")?
        .iter()
        .zip(maps["frames"].as_array().ok_or("Missing map frames")?)
    {
        if ["date", "sample_time_utc", "receipt_file", "receipt_sha256"]
            .iter()
            .any(|k| section[*k] != map[*k])
        {
            return Err("Atlas NorKyst map and profile sources disagree".into());
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn hourly_samples_remain_model_sections_with_unknown_current_dimensions() {
        let timeline: Value = serde_json::from_str(include_str!(
            "../../../research/norkyst-ingoy-2024-section-timeline.json"
        ))
        .unwrap();
        let maps: Value = serde_json::from_str(include_str!(
            "../../../research/norkyst-ingoy-2024-map-frames.json"
        ))
        .unwrap();
        assert!(scope(&timeline, TIMELINE).is_ok());
        assert!(scope(&maps, MAPS).is_ok());
        assert!(synchronized(&timeline, &maps).is_ok());
        for key in ["current_length_km", "current_width_km"] {
            let mut bad = timeline.clone();
            bad["frames"][0][key] = json!(100);
            assert!(scope(&bad, TIMELINE).is_err());
        }
        let mut bad = timeline.clone();
        bad["frames"][0]["sample_time_utc"] = json!("2024-01-15T00:00:00Z");
        assert!(scope(&bad, TIMELINE).is_err());
        let mut bad = maps.clone();
        bad["rules"]["temporal_interpolation"] = json!(true);
        assert!(scope(&bad, MAPS).is_err());
        let mut bad = maps.clone();
        bad["frames"][0]["receipt_sha256"] = json!("other");
        assert!(synchronized(&timeline, &bad).is_err());
    }
}
