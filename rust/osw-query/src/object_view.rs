//! Scoped canonical evidence for an object page; rows retain release fields.
use crate::Store;
use serde::Deserialize;
use serde_json::{Value, json};
use std::collections::BTreeSet;
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Request {
    id: String,
}
impl Store {
    pub fn object_view(&self, bytes: &[u8]) -> Result<Value, String> {
        let request: Request = serde_json::from_slice(bytes).map_err(|e| e.to_string())?;
        let id = request.id.as_str();
        for name in [
            "entities",
            "sources",
            "claims",
            "relations",
            "measurements",
            "geometries",
            "names",
            "length_assessments",
            "classification_vocabularies",
            "named_eddy_footprint_candidates",
            "footprint_movie_context",
            "media",
            "tiles",
            "tile_state_relations",
            "named_eddy_state_assessments",
            "named_eddy_source_observations",
            "named_current_source_observations",
            "operational_eddy_state_observations",
            "diagnosed_current_path_observations",
            "observation_sets",
        ] {
            if !self.bundle.collections.contains_key(name) {
                return Err(format!("Missing canonical object collection: {name}"));
            }
        }
        let entity = self.bundle.collections["entities"]
            .iter()
            .find(|r| r["id"] == id)
            .ok_or("Object not found in the canonical release")?;
        let names = self.bundle.manifest["canonical_collections"]
            .as_array()
            .ok_or("Missing canonical collection inventory")?;
        let mut data = json!({});
        for name in names {
            let name = name.as_str().ok_or("Invalid canonical collection name")?;
            let rows = self
                .bundle
                .collections
                .get(name)
                .ok_or("Missing canonical object collection")?;
            let selected: Vec<_> = rows
                .iter()
                .filter(|r| {
                    matches!(name, "entities" | "sources" | "length_assessments")
                        || name == "observation_sets" && entity["type"] == "osw_state"
                        || [
                            "entity_id",
                            "subject_id",
                            "object_id",
                            "state_id",
                            "eddy_id",
                            "operational_eddy_id",
                        ]
                        .iter()
                        .any(|k| r[k] == id)
                        || name == "named_eddy_footprint_candidates"
                            && r["state_assessments"]
                                .as_array()
                                .is_some_and(|rs| rs.iter().any(|a| a["state_id"] == id))
                })
                .cloned()
                .collect();
            data[name] = json!(selected);
        }
        let footprints = data["named_eddy_footprint_candidates"]
            .as_array()
            .ok_or("Missing footprint inventory")?
            .clone();
        data["eddy_recurrence"] = json!(
            self.bundle
                .collections
                .get("eddy_recurrence")
                .map(|rows| rows
                    .iter()
                    .filter(|r| r["entity_id"] == id)
                    .cloned()
                    .collect::<Vec<_>>())
                .unwrap_or_default()
        );
        let footprint_ids: BTreeSet<_> =
            footprints.iter().filter_map(|r| r["id"].as_str()).collect();
        let geometry_ids: BTreeSet<_> = footprints
            .iter()
            .filter_map(|r| r["geometry_id"].as_str())
            .collect();
        data["footprint_movie_context"] = json!(
            self.bundle.collections["footprint_movie_context"]
                .iter()
                .filter(|r| r["footprint_candidate_id"]
                    .as_str()
                    .is_some_and(|v| footprint_ids.contains(v)))
                .collect::<Vec<_>>()
        );
        data["geometries"] = json!(
            self.bundle.collections["geometries"]
                .iter()
                .filter(|r| r["entity_id"] == id
                    || r["id"].as_str().is_some_and(|v| geometry_ids.contains(v)))
                .collect::<Vec<_>>()
        );
        let relations = data["relations"].as_array().ok_or("Missing relations")?;
        let diagnosed: BTreeSet<_> = relations
            .iter()
            .filter(|r| {
                r["predicate"] == "dated_geostrophic_streamline_segment_intersection"
                    && r["object_id"] == id
            })
            .filter_map(|r| r["subject_id"].as_str())
            .collect();
        data["diagnosed_current_path_observations"] = json!(
            self.bundle.collections["diagnosed_current_path_observations"]
                .iter()
                .filter(|r| r["entity_id"] == id
                    || r["entity_id"]
                        .as_str()
                        .is_some_and(|v| diagnosed.contains(v)))
                .collect::<Vec<_>>()
        );
        let states: BTreeSet<_> = data["operational_eddy_state_observations"]
            .as_array()
            .ok_or("Missing detection observations")?
            .iter()
            .filter_map(|r| r["state_id"].as_str())
            .map(str::to_owned)
            .collect();
        let tile_relations: Vec<_> = self.bundle.collections["tile_state_relations"]
            .iter()
            .filter(|r| r["state_id"].as_str().is_some_and(|v| states.contains(v)))
            .collect();
        let tiles: BTreeSet<_> = tile_relations
            .iter()
            .filter_map(|r| r["tile_id"].as_str())
            .collect();
        let extra_claims: BTreeSet<_> = tile_relations
            .iter()
            .filter_map(|r| r["claim_id"].as_str())
            .chain(
                data["operational_eddy_state_observations"]
                    .as_array()
                    .unwrap()
                    .iter()
                    .filter_map(|r| r["claim_id"].as_str()),
            )
            .collect();
        data["claims"] = json!(
            self.bundle.collections["claims"]
                .iter()
                .filter(|r| r["subject_id"] == id
                    || r["object_id"] == id
                    || r["id"].as_str().is_some_and(|v| extra_claims.contains(v)))
                .collect::<Vec<_>>()
        );
        data["tiles"] = json!(
            self.bundle.collections["tiles"]
                .iter()
                .filter(|r| r["tile_id"].as_str().is_some_and(|v| tiles.contains(v)))
                .collect::<Vec<_>>()
        );
        data["tile_state_relations"] = json!(tile_relations);
        let detection_plot = if entity["type"] == "operational_eddy_detection" {
            let geometry = data["geometries"].as_array().and_then(|rs| {
                rs.iter()
                    .find(|r| r["entity_id"] == id && r["role"] == "dated_operational_eddy_polygon")
            });
            geometry.map(|g|crate::object_plot::scene(g,&data["operational_eddy_state_observations"][0]["provider_center_lon_lat"])).unwrap_or(json!({"available":false,"reason":"No dated provider polygon is recorded for this detection."}))
        } else {
            Value::Null
        };
        let mut footprint_plots = json!({});
        for candidate in &footprints {
            let Some(candidate_id) = candidate["id"].as_str() else {
                return Err("Footprint candidate has no ID".into());
            };
            let geometry = data["geometries"]
                .as_array()
                .and_then(|rs| rs.iter().find(|r| r["id"] == candidate["geometry_id"]));
            footprint_plots[candidate_id] = geometry.map(crate::object_plot::named_scene).unwrap_or(json!({"available":false,"reason":"No source geometry is recorded for this contour candidate."}));
        }
        Ok(
            json!({"ok":true,"engine":"rust-osw-query-v1","id":id,"bundle_sha256":self.metadata()["bundle_sha256"],"collections":data,"detection_plot":detection_plot,"footprint_plots":footprint_plots,"source_panel_scene":crate::eddy_source_panels::for_owner(&self.bundle,id)?}),
        )
    }
}
