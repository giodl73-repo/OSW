//! Checked map scene: locators, dated diagnostic lines and operational polygons.
use crate::index_store::IndexStore;
use serde_json::{Value, json};

fn project(coordinate: &Value) -> Result<Value, String> {
    let (x, y) =
        crate::cartography::root(crate::map::point(coordinate).ok_or("Invalid index locator")?);
    Ok(json!([x, y]))
}
fn path(coordinates: &Value, closed: bool) -> Result<String, String> {
    crate::map::path_formatted(coordinates, closed, |p| {
        let (x, y) = crate::cartography::root(p);
        format!("{x:.2},{y:.2}")
    })
    .ok_or("Invalid index map geometry".into())
}
impl IndexStore {
    pub fn map_view(&self, bytes: &[u8]) -> Result<Value, String> {
        #[derive(serde::Deserialize)]
        #[serde(deny_unknown_fields)]
        struct Request {}
        let _: Request = serde_json::from_slice(bytes).map_err(|e| e.to_string())?;
        let get = |source: &str| {
            self.documents
                .get(source)
                .ok_or_else(|| format!("Missing index map source {source}"))
        };
        let entries = |source: &str| {
            get(source)?["entries"]
                .as_array()
                .ok_or("Missing map entries".to_string())
        };
        let currents = entries("research/ocean-current-almanac.json")?;
        let index = get("research/ocean-current-atlas-index.json")?;
        let loops = entries("research/named-loop-current-eddy-identities.json")?;
        let loop_context = entries("research/named-loop-eddy-nasa-context.json")?;
        let nasa = get("research/nasa-perpetual-ocean-objects.json")?["objects"]
            .as_array()
            .ok_or("Missing NASA objects")?;
        let geography = entries("research/named-eddy-geography.json")?;
        let mut markers = Vec::new();
        for record in currents {
            let id = record["id"].as_str().ok_or("Missing current ID")?;
            let name = record["name"].as_str().ok_or("Missing current name")?;
            for coordinate in index["entries"][id]["locators"]
                .as_array()
                .ok_or("Missing current locators")?
            {
                markers.push(json!({"id":id,"kind":"current","point":project(coordinate)?,"radius":8,
                    "class":"map-marker","href":format!("#current-{id}"),"label":format!("Jump to {name} in the almanac"),
                    "title":format!("{name} · approximate atlas locator")}));
            }
        }
        markers.push(json!({"id":"loop-rings","kind":"loop","point":project(&index["named_loop_current_eddies"]["region_locator"])?,
            "radius":13,"class":"map-marker ring-marker","href":"#eddies-title",
            "label":format!("Jump to {} Loop Current eddy names in the Gulf of Mexico",loops.len()),
            "title":format!("{} Loop Current eddy names · region only, no individual positions",loops.len())}));
        let mut published = 0;
        for record in loop_context {
            let position = &record["published_observed_position"];
            if position.is_null() {
                continue;
            }
            let id = record["id"].as_str().ok_or("Missing Loop ID")?;
            let name = record["name"].as_str().ok_or("Missing Loop name")?;
            let period = position["period"]
                .as_str()
                .ok_or("Missing observed period")?;
            markers.push(json!({"id":id,"kind":"loop","point":project(&position["coordinate"])?,"radius":6,
                "class":"map-marker observed-loop-eddy-marker","href":format!("#eddy-{id}"),
                "label":format!("Jump to the published center point for {name}"),
                "title":format!("{name} · {period}; approximate source-reported center, not a footprint or NASA identity")}));
            published += 1;
        }
        let mut nasa_count = 0;
        for record in nasa {
            if record["locator"].is_null() || !record["almanac_current_id"].is_null() {
                continue;
            }
            let id = record["id"].as_str().ok_or("Missing NASA ID")?;
            let name = record["name"].as_str().ok_or("Missing NASA name")?;
            markers.push(json!({"id":id,"kind":"nasa","point":project(&record["locator"])?,"radius":6,
                "class":"map-marker nasa-marker","href":format!("#nasa-{id}"),
                "label":format!("Jump to NASA-described {name} in the almanac"),
                "title":format!("{name} · approximate NASA-object atlas locator; no footprint claim")}));
            nasa_count += 1;
        }
        for record in geography {
            let id = record["id"].as_str().ok_or("Missing geography ID")?;
            let name = record["name"].as_str().ok_or("Missing geography name")?;
            let title = if !record["observed_center"].is_null() {
                format!(
                    "{name} · {} study-reported center; not a closed footprint or NASA-era position",
                    record["observed_center"]["period"]
                        .as_str()
                        .ok_or("Missing observed center period")?
                )
            } else {
                format!(
                    "{name} · {}; not an eddy center",
                    if !record["sample_site"].is_null() {
                        "published core-water sample site"
                    } else {
                        "editorial regional locator"
                    }
                )
            };
            markers.push(
                json!({"id":id,"kind":"geography","point":project(&record["locator"])?,"radius":6,
                "class":"map-marker geography-eddy-marker","href":format!("#eddy-geography-{id}"),
                "label":format!("Jump to {name} in named eddy geography"),"title":title}),
            );
        }
        let front = get("research/gulf-stream-navo-front-20260928.json")?;
        let fronts = front["fronts"].as_object().ok_or("Missing front lines")?.iter()
            .map(|(side,record)| Ok(json!({"side":side,"record":record,"path":path(&record["geometry"]["coordinates"],false)?})))
            .collect::<Result<Vec<_>,String>>()?;
        let diagnosed = get(
            "almanac/release/v0.1.0/source-ledgers/gulf-stream-geostrophic-path-20260925.json",
        )?;
        let operational = get(
            "almanac/release/v0.1.0/source-ledgers/navo-freddies-eddy-state-join-20260925.json",
        )?;
        let polygons = operational["features"]
            .as_array()
            .ok_or("Missing operational polygons")?
            .iter()
            .map(|record| {
                Ok(json!({"record":record,"path":path(&record["display_outline_lon_lat"],true)?}))
            })
            .collect::<Result<Vec<_>, String>>()?;
        Ok(
            json!({"ok":true,"markers":markers,"counts":{"currents":currents.len(),"loop_names":loops.len(),
            "published_loop_positions":published,"nasa_markers":nasa_count,"geography_names":geography.len()},
            "fronts":fronts,"front_lengths_km":get("research/gulf-stream-navo-state-snapshot-20260928.json")?["front_lengths_km"],
            "diagnosed_path":path(&diagnosed["representative"]["coordinates_lon_lat"],false)?,
            "diagnosed_length_km":diagnosed["representative"]["segment_length_km"],
            "operational_polygons":polygons,"operational_date":operational["observation_date"]}),
        )
    }
}
