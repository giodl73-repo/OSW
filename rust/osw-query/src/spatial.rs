//! Planar topology on coarse display-state geometry, not ocean occupancy.
use geo::{
    BoundingRect, Coord, Geometry, Intersects, LineString, MapCoords, MultiPolygon, Point, Polygon,
    Relate,
};
use serde::Deserialize;
use serde_json::{Value, json};
use std::collections::BTreeMap;

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SpatialQuery {
    pub state_code: String,
    pub predicate: String,
    #[serde(default)]
    pub include_excluded: bool,
}

pub struct Feature {
    geometry: Geometry<f64>,
    metadata: Value,
}
pub struct Index {
    states: BTreeMap<String, MultiPolygon<f64>>,
    objects: BTreeMap<String, Vec<Feature>>,
}

fn coordinates(value: &Value, unwrap: bool) -> Result<LineString<f64>, String> {
    let mut points: Vec<Coord<f64>> = Vec::new();
    for pair in value.as_array().ok_or("Invalid coordinates")? {
        let x = pair[0].as_f64().ok_or("Invalid longitude")?;
        let y = pair[1].as_f64().ok_or("Invalid latitude")?;
        if !x.is_finite()
            || !y.is_finite()
            || !(-180.000001..=180.000001).contains(&x)
            || !(-90.000001..=90.000001).contains(&y)
        {
            return Err("Out-of-range spatial coordinate".into());
        }
        let mut x = x;
        if unwrap {
            if let Some(previous) = points.last() {
                x += 360.0 * ((previous.x - x) / 360.0).round();
                if (previous.x - x).abs() == 180.0 {
                    return Err("Ambiguous 180-degree spatial leg".into());
                }
            }
        }
        points.push(Coord { x, y });
    }
    Ok(LineString::new(points))
}
fn polygon(value: &Value, unwrap: bool) -> Result<Polygon<f64>, String> {
    let rings = value.as_array().ok_or("Invalid polygon rings")?;
    let outer = coordinates(rings.first().ok_or("Empty polygon")?, unwrap)?;
    if outer.0.len() < 4 || outer.0.first() != outer.0.last() {
        return Err("Unclosed or short polygon ring".into());
    }
    let mut holes = Vec::new();
    for ring in &rings[1..] {
        let mut hole = coordinates(ring, unwrap)?;
        if hole.0.len() < 4 || hole.0.first() != hole.0.last() {
            return Err("Unclosed polygon hole".into());
        }
        if unwrap {
            let dx = 360.0 * ((outer.0[0].x - hole.0[0].x) / 360.0).round();
            for p in &mut hole.0 {
                p.x += dx;
            }
        }
        holes.push(hole);
    }
    Ok(Polygon::new(outer, holes))
}
fn geometry(value: &Value, unwrap: bool) -> Result<Geometry<f64>, String> {
    let c = &value["coordinates"];
    match value["type"].as_str() {
        Some("Point") => {
            let p = coordinates(&json!([c]), false)?;
            Ok(Point::from(p.0[0]).into())
        }
        Some("LineString") => {
            let line = coordinates(c, unwrap)?;
            if line.0.len() < 2 {
                return Err("Short spatial line".into());
            }
            Ok(line.into())
        }
        Some("Polygon") => Ok(polygon(c, unwrap)?.into()),
        Some("MultiPolygon") => Ok(MultiPolygon::new(
            c.as_array()
                .ok_or("Invalid multipolygon")?
                .iter()
                .map(|p| polygon(p, unwrap))
                .collect::<Result<_, _>>()?,
        )
        .into()),
        _ => Err("Unsupported spatial geometry".into()),
    }
}

impl Index {
    pub fn build(collections: &BTreeMap<String, Vec<Value>>) -> Result<Self, String> {
        let mut states = BTreeMap::new();
        for state in collections.get("states").into_iter().flatten() {
            if let Some(shape) = state.get("display_geometry") {
                let polygons = match geometry(shape, false)? {
                    Geometry::Polygon(p) => MultiPolygon::new(vec![p]),
                    Geometry::MultiPolygon(p) => p,
                    _ => return Err("State requires polygon geometry".into()),
                };
                states.insert(
                    state["code"].as_str().ok_or("Missing state code")?.into(),
                    polygons,
                );
            }
        }
        let mut objects = BTreeMap::new();
        for object in &collections["objects"] {
            let mut features = Vec::new();
            for feature in object["map_features"].as_array().into_iter().flatten() {
                features.push(Feature {
                    geometry: geometry(
                        feature
                            .get("spatial_geometry")
                            .unwrap_or(&feature["geometry"]),
                        true,
                    )?,
                    metadata: feature.clone(),
                });
            }
            objects.insert(
                object["id"].as_str().ok_or("Missing object ID")?.into(),
                features,
            );
        }
        Ok(Self { states, objects })
    }
    pub fn validate(&self, query: &SpatialQuery) -> Result<(), String> {
        if query.state_code.is_empty() {
            return Err("Select an OSW state for a spatial query".into());
        }
        if !self.states.contains_key(&query.state_code) {
            return Err(format!(
                "No spatial state geometry for {}",
                query.state_code
            ));
        }
        if !["intersects", "within", "locator", "gateway"].contains(&query.predicate.as_str()) {
            return Err("Spatial predicate must be intersects, within, locator or gateway".into());
        }
        Ok(())
    }
    pub fn matches(&self, id: &str, query: &SpatialQuery) -> Vec<Value> {
        let state = &self.states[&query.state_code];
        let state_bounds = state.bounding_rect();
        let mut matches = Vec::new();
        for (i, feature) in self.objects.get(id).into_iter().flatten().enumerate() {
            let point = matches!(feature.geometry, Geometry::Point(_));
            let area = matches!(
                feature.geometry,
                Geometry::Polygon(_) | Geometry::MultiPolygon(_)
            );
            let gateway = feature.metadata["role"] == "shared_regional_gateway";
            if match query.predicate.as_str() {
                "locator" => !point || gateway,
                "gateway" => !point || !gateway,
                "within" => !area,
                _ => point,
            } {
                continue;
            }
            let exclusion = feature.metadata["state_semantic_exclusions"]
                .as_array()
                .and_then(|items| items.iter().find(|r| r["state_code"] == query.state_code));
            if exclusion.is_some() && !query.include_excluded {
                continue;
            }
            for shift in [-360.0, 0.0, 360.0] {
                let shifted = feature.geometry.map_coords(|c| Coord {
                    x: c.x + shift,
                    y: c.y,
                });
                if !state_bounds
                    .zip(shifted.bounding_rect())
                    .is_some_and(|(a, b)| a.intersects(&b))
                {
                    continue;
                }
                let relation = match &shifted {
                    Geometry::Point(p) => state.relate(p),
                    Geometry::LineString(p) => state.relate(p),
                    Geometry::Polygon(p) => state.relate(p),
                    Geometry::MultiPolygon(p) => state.relate(p),
                    _ => continue,
                };
                let accepts = if query.predicate == "intersects" {
                    relation.is_intersects()
                } else {
                    relation.is_covers()
                };
                if accepts {
                    matches.push(json!({"feature_index":i,"state_code":query.state_code,"predicate":query.predicate,
                        "frame_id":feature.metadata["frame_id"],"series_id":feature.metadata["series_id"],"source_url":feature.metadata["source_url"],"source_subset_sha256":feature.metadata["source_subset_sha256"],"timeline_sha256":feature.metadata["timeline_sha256"],
                        "role":feature.metadata["role"],"note":feature.metadata["note"],"candidate_id":feature.metadata["candidate_id"],
                        "observation_date":feature.metadata["observation_date"],"boundary_touch_only":relation.is_touches(),
                        "geometry_id":feature.metadata["geometry_id"],"coordinate_reference_system":feature.metadata["coordinate_reference_system"],
                        "positional_uncertainty":feature.metadata["positional_uncertainty"],"source_id":feature.metadata["source_id"],
                        "semantic_exclusion":exclusion,"geometry_method":feature.metadata["spatial_geometry_method"],
                        "scope":"Computed topology against coarse, land-masked OSW display polygons; not physical passage, footprint confidence or containment of the full named current."}));
                    break;
                }
            }
        }
        matches
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn holes_edges_locators_and_seams() {
        let shape = json!({"type":"Polygon","coordinates":[[[170,-10],[180,-10],[180,10],[170,10],[170,-10]],[[172,-2],[174,-2],[174,2],[172,2],[172,-2]]]});
        let make = |id: &str, g: Value, role: &str| json!({"id":id,"map_features":[{"geometry":g,"role":role}]});
        let collections = BTreeMap::from([
            (
                "states".into(),
                vec![json!({"code":"TEST","display_geometry":shape})],
            ),
            (
                "objects".into(),
                vec![
                    make(
                        "hole",
                        json!({"type":"Point","coordinates":[173,0]}),
                        "editorial_locator",
                    ),
                    make(
                        "edge",
                        json!({"type":"Point","coordinates":[170,0]}),
                        "editorial_locator",
                    ),
                    make(
                        "gateway",
                        json!({"type":"Point","coordinates":[175,0]}),
                        "shared_regional_gateway",
                    ),
                    make(
                        "line",
                        json!({"type":"LineString","coordinates":[[179,5],[-179,5]]}),
                        "editorial_reference_route",
                    ),
                ],
            ),
        ]);
        let index = Index::build(&collections).unwrap();
        let q = |predicate: &str| SpatialQuery {
            state_code: "TEST".into(),
            predicate: predicate.into(),
            include_excluded: false,
        };
        assert!(index.matches("hole", &q("locator")).is_empty());
        assert_eq!(index.matches("edge", &q("locator")).len(), 1);
        assert!(index.matches("gateway", &q("locator")).is_empty());
        assert_eq!(index.matches("gateway", &q("gateway")).len(), 1);
        assert_eq!(index.matches("line", &q("intersects")).len(), 1);
        assert!(index.matches("edge", &q("intersects")).is_empty());
        assert!(index.validate(&q("fake")).is_err());
        assert!(geometry(&json!({"type":"Point","coordinates":[0,100]}), true).is_err());
    }
}
