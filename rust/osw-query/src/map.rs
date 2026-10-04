//! Display geometry only. Metric calculations must use geographic coordinates.
use serde_json::{Value, json};
use std::collections::BTreeSet;

fn point(value: &Value) -> Option<(f64, f64)> {
    let xy = value.as_array()?;
    let lon = xy.first()?.as_f64()?;
    let lat = xy.get(1)?.as_f64()?;
    if !lon.is_finite()
        || !lat.is_finite()
        || !(-180.0..=180.0).contains(&lon)
        || !(-90.0..=90.0).contains(&lat)
    {
        return None;
    }
    Some((lon + 180.0, 90.0 - lat))
}

fn path(value: &Value, closed: bool) -> Option<String> {
    let coordinates = value.as_array()?;
    if coordinates.len() < if closed { 4 } else { 2 } {
        return None;
    }
    let mut previous: Option<(f64, f64)> = None;
    let mut result = String::new();
    for coordinate in coordinates {
        let (x, y) = point(coordinate)?;
        let seam = previous.is_some_and(|(px, _)| (x - px).abs() > 180.0);
        // A polygon crossing the seam requires clipping, never a spurious closure.
        if closed && seam {
            return None;
        }
        result.push_str(&format!(
            "{} {x:.5} {y:.5} ",
            if previous.is_none() || seam { 'M' } else { 'L' }
        ));
        previous = Some((x, y));
    }
    if closed {
        result.push('Z');
    }
    Some(result)
}

pub fn scene(records: &[&Value]) -> Value {
    scene_selected(records, None, None)
}
/// Derive only the local nominal section from source-bound sample coordinates.
/// No route, width buffer, polygon or state containment is inferred.
pub fn sample_scene(records: &[&Value]) -> Value {
    if !records
        .iter()
        .any(|r| r["sample_family"] == "gulf_stream_dated_half_peak_section")
    {
        return Value::Null;
    }
    let projected: Vec<Value> = records.iter().map(|row| {
        let mut record = json!({"id":row["id"],"label":row["label"],"type":"local_section_sample","map_features":[]});
        if row["sample_family"] != "gulf_stream_dated_half_peak_section" || row["status"] != "paired_boundaries" || row["value_km"].is_null() {
            return record;
        }
        let nominal = &row["source_sample"]["nominal"];
        let coordinates = json!([[row["longitude_degrees_east"],nominal["south_boundary"]["latitude"]],[row["longitude_degrees_east"],nominal["north_boundary"]["latitude"]]]);
        let valid = coordinates.as_array().is_some_and(|c| c.iter().all(|p| point(p).is_some()))
            && nominal["south_boundary"]["latitude"].as_f64().zip(nominal["north_boundary"]["latitude"].as_f64()).is_some_and(|(s,n)| s < n);
        if valid {
            record["map_features"] = json!([{"geometry":{"type":"LineString","coordinates":coordinates},
                "role":"local_diagnostic_section_span","note":"Nominal half-peak eastward-component section at 70 W. Surface diagnostic; not a flow-normal width, current route or occupied footprint. Paired interpolated boundaries and resolution remain under review.",
                "observation_date":row["observation_date"],"source_url":row["source_url"],"source_algorithm":row["source_algorithm"],
                "source_subset_sha256":row["source_sample"]["source_subset_sha256"],"layer":row["source_context"]["layer"]}]);
        }
        record
    }).collect();
    let refs: Vec<&Value> = projected.iter().collect();
    let mut scene = scene(&refs);
    scene["inspection_collection"] = json!("width_samples");
    scene["recorded_days"] = json!(
        records
            .iter()
            .filter(|r| r["sample_family"] == "gulf_stream_dated_half_peak_section")
            .filter_map(|r| r["observation_date"].as_str())
            .collect::<BTreeSet<_>>()
    );
    let mut bounds: Option<[f64; 4]> = None;
    for record in &projected {
        for coordinate in record["map_features"][0]["geometry"]["coordinates"]
            .as_array()
            .into_iter()
            .flatten()
        {
            if let Some((x, y)) = point(coordinate) {
                bounds = Some(match bounds {
                    None => [x, y, x, y],
                    Some(b) => [b[0].min(x), b[1].min(y), b[2].max(x), b[3].max(y)],
                });
            }
        }
    }
    scene["display_bounds"] = json!(bounds);
    scene["scope"] = json!(
        "All matching sample records across every results page. Only supported nominal paired section boundaries are mapped. Other samples retain their records without invented geography. These local surface spans are not current axes, flow-normal widths, occupied footprints or state containment. Overlapping dates remain separate marks; no time interpolation."
    );
    for feature in scene["features"].as_array_mut().unwrap() {
        let row = records
            .iter()
            .find(|r| r["id"] == feature["entity_id"])
            .unwrap();
        feature["inspection_collection"] = json!("width_samples");
        feature["owner_entity_id"] = row["entity_id"].clone();
        feature["metric"] = row["metric"].clone();
        feature["value_km"] = row["value_km"].clone();
        feature["diagnostic_sensitivity_interval_km"] =
            row["diagnostic_sensitivity_interval_km"].clone();
        feature["sampling_bracket_interval_km"] = row["sampling_bracket_interval_km"].clone();
        feature["resolution_review_required"] = row["resolution_review_required"].clone();
        feature["source_sample"] = json!({"diagnostic_id":row["diagnostic_id"],"sample_path":row["sample_path"],"coordinates":projected.iter().find(|r| r["id"] == row["id"]).unwrap()["map_features"][0]["geometry"]["coordinates"]});
    }
    scene
}
pub fn scene_selected(
    records: &[&Value],
    time: Option<&crate::temporal::GeometryTime>,
    seasonal: Option<&crate::seasonal::SeasonalSelection>,
) -> Value {
    let mut features = Vec::new();
    let mut mapped = BTreeSet::new();
    let mut omitted = Vec::new();
    for record in records {
        for (feature_index, feature) in record["map_features"]
            .as_array()
            .into_iter()
            .flatten()
            .enumerate()
        {
            if time.is_some_and(|t| !t.includes(feature)) {
                continue;
            }
            if seasonal.is_some_and(|s| !s.includes(feature)) {
                continue;
            }
            let geometry = &feature["geometry"];
            let coordinates = &geometry["coordinates"];
            let primitive = match geometry["type"].as_str() {
                Some("Point") => {
                    point(coordinates).map(|(x, y)| json!({"kind":"point","x":x,"y":y}))
                }
                Some("LineString") => {
                    path(coordinates, false).map(|d| json!({"kind":"line","d":d}))
                }
                Some("Polygon") => coordinates.as_array().and_then(|rings| {
                    if rings.is_empty() {
                        return None;
                    }
                    let paths: Option<Vec<_>> = rings.iter().map(|r| path(r, true)).collect();
                    paths.map(|p| json!({"kind":"polygon","d":p.join(" ")}))
                }),
                Some("MultiPolygon") => coordinates.as_array().and_then(|polygons| {
                    let paths: Option<Vec<_>> = polygons
                        .iter()
                        .map(|polygon| {
                            let rings = polygon.as_array()?;
                            let paths: Option<Vec<_>> =
                                rings.iter().map(|r| path(r, true)).collect();
                            paths.map(|p| p.join(" "))
                        })
                        .collect();
                    paths.map(|p| json!({"kind":"polygon","d":p.join(" ")}))
                }),
                _ => None,
            };
            if let Some(primitive) = primitive {
                mapped.insert(record["id"].as_str().unwrap_or(""));
                let mut rendered = json!({"entity_id":record["id"],"feature_index":feature_index,"label":record["label"],"type":record["type"],
                    "role":feature["role"],"note":feature["note"],"observation_date":feature["observation_date"],"primitive":primitive});
                if time.is_some() {
                    rendered["undated_context"] = json!(feature["observation_date"].is_null());
                }
                for key in [
                    "frame_id",
                    "phase_id",
                    "phase_label",
                    "flow_direction",
                    "calendar_months",
                    "source_locator",
                    "time_convention",
                    "layer",
                    "route_candidate_sha256",
                    "seasonal_inventory_sha256",
                    "comparability",
                    "series_id",
                    "source_url",
                    "source_subset_sha256",
                    "source_response_sha256",
                    "timeline_sha256",
                    "source_algorithm",
                    "source_product_status",
                ] {
                    if let Some(value) = feature.get(key) {
                        rendered[key] = value.clone();
                    }
                }
                features.push(rendered);
            } else {
                omitted.push(json!({"entity_id":record["id"],"role":feature["role"],"reason":"Unsupported or invalid geometry, or polygon needs antimeridian clipping"}));
            }
        }
    }
    json!({"projection":"equirectangular_display_only","view_box":[0,0,360,180],
        "matching_objects":records.len(),"mapped_objects":mapped.len(),"unmapped_objects":records.len()-mapped.len(),
        "features":features,"omitted_features":omitted,
        "scope":"All matching objects, independent of table pagination. Shared gateways and locators are not occupied footprints. Overlapping marks may represent several objects."})
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn section_samples_require_resolved_ordered_source_boundaries() {
        let original = json!({"id":"width-sample:one","entity_id":"current:gulf-stream-system","label":"Section","sample_family":"gulf_stream_dated_half_peak_section","status":"paired_boundaries","value_km":90,"longitude_degrees_east":-70,"source_sample":{"nominal":{"south_boundary":{"latitude":37},"north_boundary":{"latitude":38}}}});
        let valid = sample_scene(&[&original]);
        assert_eq!(
            valid["features"][0]["primitive"]["d"],
            "M 110.00000 53.00000 L 110.00000 52.00000 "
        );
        assert_eq!(
            valid["features"][0]["inspection_collection"],
            "width_samples"
        );
        for bad in [json!(null), json!(36), json!(91)] {
            let mut row = original.clone();
            row["source_sample"]["nominal"]["north_boundary"]["latitude"] = bad;
            assert_eq!(sample_scene(&[&row])["unmapped_objects"], 1);
        }
        let mut missing = original.clone();
        missing["value_km"] = Value::Null;
        assert_eq!(sample_scene(&[&missing])["mapped_objects"], 0);
        let mut other = original.clone();
        other["sample_family"] = json!("leeuwin_monthly_fitted_plot");
        assert!(sample_scene(&[&other]).is_null());
    }
    #[test]
    fn geography_seams_and_invalid_coordinates() {
        assert_eq!(point(&json!([0, 0])), Some((180.0, 90.0)));
        assert_eq!(point(&json!([181, 0])), None);
        let line = path(&json!([[179, 1], [-179, 2]]), false).unwrap();
        assert_eq!(line.matches('M').count(), 2);
        assert!(!line.contains('L'));
        assert!(path(&json!([[179, 1], [-179, 2], [-178, 0], [179, 1]]), true).is_none());
        assert!(
            path(&json!([[0, 0], [1, 0], [1, 1], [0, 0]]), true)
                .unwrap()
                .ends_with('Z')
        );
    }
}
