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
    scene_selected(records, None)
}
pub fn scene_selected(records: &[&Value], time: Option<&crate::temporal::GeometryTime>) -> Value {
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
