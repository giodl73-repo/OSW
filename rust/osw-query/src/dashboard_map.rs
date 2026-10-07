//! Dashboard geography uses the same display-only projector as query maps.
use serde_json::{Value, json};
use std::collections::{BTreeMap, BTreeSet};

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn grouped_gateways_and_omissions_keep_their_scope() {
        let row = |id: &str, geometry: Value, group: Value, covered: u64| {
            json!({"id":id,"label":id,"type":"named_eddy",
            "capabilities":{"geometry":covered},"map_features":[{"geometry":geometry,"group":group,"role":"source_context","note":"Context only; not a footprint"}]})
        };
        let point = json!({"type":"Point","coordinates":[-90,25]});
        let doc = json!({"entries":[row("a",point.clone(),json!("Gulf gateway"),1),
            row("b",point,json!("Gulf gateway"),0),
            row("line",json!({"type":"LineString","coordinates":[[-179,5],[179,6]]}),Value::Null,0),
            row("polygon",json!({"type":"Polygon","coordinates":[[[179,0],[-179,0],[-179,1],[179,0]]]}),Value::Null,0),
            row("invalid",json!({"type":"Point","coordinates":[0,95]}),Value::Null,0)]});
        let ids = ["a", "b", "line", "polygon", "invalid"]
            .map(str::to_owned)
            .to_vec();
        let result = scene(&doc, &ids, "geometry", &BTreeSet::from(["b"])).unwrap();
        assert_eq!(result["mapped_objects"], 3);
        assert_eq!(result["omitted_features"].as_array().unwrap().len(), 2);
        let markers: Vec<_> = result["features"]
            .as_array()
            .unwrap()
            .iter()
            .filter(|f| f["kind"] == "marker")
            .collect();
        assert_eq!(markers.len(), 1);
        assert_eq!(markers[0]["entity_ids"], json!(["a", "b"]));
        assert_eq!(markers[0]["covered_count"], 1);
        assert_eq!(markers[0]["updated"], true);
        assert_eq!(markers[0]["display_x"], json!(430.0));
        assert_eq!(
            result["features"][0]["primitive"]["d"]
                .as_str()
                .unwrap()
                .matches('M')
                .count(),
            2
        );
        let mut conflict = doc;
        conflict["entries"][1]["map_features"][0]["geometry"]["coordinates"] = json!([-89, 25]);
        assert!(
            scene(&conflict, &ids, "geometry", &BTreeSet::new())
                .unwrap_err()
                .contains("conflicting positions")
        );
    }
}

pub fn scene(
    doc: &Value,
    ids: &[String],
    metric: &str,
    changed: &BTreeSet<&str>,
) -> Result<Value, String> {
    let selected: BTreeSet<_> = ids.iter().map(String::as_str).collect();
    let rows: Vec<_> = doc["entries"]
        .as_array()
        .ok_or("Missing dashboard map records")?
        .iter()
        .filter(|r| selected.contains(r["id"].as_str().unwrap_or("")))
        .collect();
    let source = crate::map::scene(&rows);
    let index: BTreeMap<_, _> = rows
        .iter()
        .map(|r| (r["id"].as_str().unwrap_or(""), *r))
        .collect();
    let mut paths = Vec::new();
    let mut markers: Vec<Value> = Vec::new();
    let mut groups: BTreeMap<String, usize> = BTreeMap::new();
    for feature in source["features"]
        .as_array()
        .ok_or("Missing map primitives")?
    {
        let id = feature["entity_id"]
            .as_str()
            .ok_or("Missing map identity")?;
        let row = index[id];
        let source_feature = &row["map_features"][feature["feature_index"]
            .as_u64()
            .ok_or("Missing source feature index")?
            as usize];
        let primitive = &feature["primitive"];
        if primitive["kind"] == "point" {
            let group = source_feature["group"].as_str();
            let key = group
                .map(str::to_owned)
                .unwrap_or_else(|| format!("{id}:{}", source_feature["geometry"]["coordinates"]));
            if let Some(position) = groups.get(&key) {
                let marker = &mut markers[*position];
                if marker["primitive"] != *primitive {
                    return Err("Dashboard gateway has conflicting positions".into());
                }
                let names = marker["entity_ids"]
                    .as_array_mut()
                    .ok_or("Invalid gateway identities")?;
                if !names.iter().any(|v| v == id) {
                    names.push(json!(id));
                }
            } else {
                groups.insert(key, markers.len());
                markers.push(json!({"kind":"marker","primitive":primitive,"entity_ids":[id],"group":group,"note":source_feature["note"]}));
            }
        } else {
            paths.push(json!({"kind":"path","primitive":primitive,"entity_ids":[id],
                "note":format!("{}. {}",source_feature["role"].as_str().unwrap_or("").replace('_'," "),source_feature["note"].as_str().unwrap_or(""))}));
        }
    }
    paths.extend(markers);
    for feature in &mut paths {
        if feature["kind"] == "marker" {
            feature["display_x"] = json!(
                60.0 + feature["primitive"]["x"]
                    .as_f64()
                    .ok_or("Invalid point X")?
                    * 1480.0
                    / 360.0
            );
            feature["display_y"] = json!(
                90.0 + feature["primitive"]["y"]
                    .as_f64()
                    .ok_or("Invalid point Y")?
                    * 740.0
                    / 180.0
            );
        }
        let ids = feature["entity_ids"]
            .as_array()
            .ok_or("Invalid map identities")?;
        let covered = ids
            .iter()
            .filter(|id| {
                index[id.as_str().unwrap()]["capabilities"][metric]
                    .as_u64()
                    .unwrap_or(0)
                    > 0
            })
            .count();
        let updated = ids.iter().any(|id| changed.contains(id.as_str().unwrap()));
        feature["covered_count"] = json!(covered);
        feature["updated"] = json!(updated);
    }
    Ok(
        json!({"projection":source["projection"],"display_transform":"translate(60 90) scale(4.111111111111111)",
        "display_scale":1480.0/360.0,"matching_objects":source["matching_objects"],
        "mapped_objects":source["mapped_objects"],"unmapped_objects":source["unmapped_objects"],
        "features":paths,"omitted_features":source["omitted_features"],"scope":source["scope"]}),
    )
}
