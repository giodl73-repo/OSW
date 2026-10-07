//! NOAA file-scoped detections and tracks; no cross-file identity inference.
use crate::index_store::IndexStore;
use serde::Deserialize;
use serde_json::{Value, json};

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Selection {
    date: String,
    state_code: String,
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct TrackSelection {
    date: String,
    state_code: String,
    detection_id: String,
    focus_date: String,
}
impl IndexStore {
    fn noaa_source(&self, path: &str) -> Result<&Value, String> {
        self.documents
            .get(path)
            .ok_or_else(|| format!("Missing NOAA context source {path}"))
    }
    fn noaa_snapshot(&self, date: &str, state: &str) -> Result<(String, &Value, bool), String> {
        let manifest =
            self.noaa_source("research/noaa-munster-eddy-seasonal-manifest-2021-2023.json")?;
        let row = manifest["snapshots"]
            .as_array()
            .ok_or("Missing NOAA manifest snapshots")?
            .iter()
            .find(|r| r["date"].as_str() == Some(date))
            .ok_or("Unsupported NOAA sample date")?;
        let path = row["path"]
            .as_str()
            .ok_or("Missing NOAA snapshot path")?
            .strip_prefix("../")
            .ok_or("Unsupported NOAA snapshot path")?
            .to_string();
        let doc = self.noaa_source(&path)?;
        if doc["date"].as_str() != Some(date) || doc["source_sha256"] != row["source_sha256"] {
            return Err("NOAA snapshot date/source mismatch".into());
        }
        if doc["states"].get(state).is_none() {
            return Err("Unknown NOAA state".into());
        }
        Ok((
            path,
            doc,
            row["weekly_track_join"].as_bool().unwrap_or(false),
        ))
    }
    fn noaa_weekly(&self, date: &str, kind: &str) -> Result<(String, &Value), String> {
        // Only the manifest's declared June samples have weekly joins.
        let stamp = date.replace('-', "");
        let end = format!("{}0607", &stamp[..4]);
        let path = format!("research/noaa-munster-eddy-weekly{kind}-join-{stamp}-{end}.json");
        let doc = self.noaa_source(&path)?;
        if doc["start_date"].as_str() != Some(date) {
            return Err("NOAA weekly date mismatch".into());
        }
        Ok((path, doc))
    }
    fn noaa_crop(&self, date: &str, id: &str) -> Result<Value, String> {
        let crops = self.noaa_source("research/noaa-nasa-eddy-crop-join.json")?;
        let row = &crops["dates"][date];
        let Some(tile_id) = row["detections"][id].as_str() else {
            return Ok(Value::Null);
        };
        let tiles = self.noaa_source("research/nasa-perpetual-ocean-tile-join.json")?;
        let tile = tiles["tiles"]
            .as_array()
            .ok_or("Missing NASA tiles")?
            .iter()
            .find(|t| t["id"].as_str() == Some(tile_id))
            .ok_or("Unknown detection crop tile")?;
        Ok(
            json!({"tile":tile,"date":date,"estimated_crop_seconds":row["estimated_crop_seconds"],
            "identity_limit":crops["identity_limit"],"method":crops["method"]}),
        )
    }
    pub fn noaa_state_view(&self, bytes: &[u8]) -> Result<Value, String> {
        let r: Selection = serde_json::from_slice(bytes).map_err(|e| e.to_string())?;
        let (source, daily, has_weekly) = self.noaa_snapshot(&r.date, &r.state_code)?;
        let entries = daily["entries"]
            .as_array()
            .ok_or("Missing NOAA detections")?;
        let lookup: std::collections::BTreeMap<_, _> = entries
            .iter()
            .enumerate()
            .filter_map(|(index, v)| v["id"].as_str().map(|id| (id, (index, v))))
            .collect();
        if lookup.len() != entries.len() {
            return Err("Duplicate or missing NOAA detection ID".into());
        }
        let weekly = if has_weekly {
            Some(self.noaa_weekly(&r.date, "")?)
        } else {
            None
        };
        let mut groups = Vec::new();
        for status in ["contained", "intersected"] {
            let ids = daily["states"][&r.state_code][status]
                .as_array()
                .ok_or("Missing NOAA state relations")?;
            let mut rows = Vec::new();
            for id in ids {
                let key = id.as_str().ok_or("Invalid NOAA detection address")?;
                let (index, record) = lookup.get(key).ok_or("Unknown NOAA state detection")?;
                let point = crate::map::point(&record["center"])
                    .map(crate::cartography::root)
                    .map(|(x, y)| json!([x, y]))
                    .unwrap_or(Value::Null);
                rows.push(json!({"id":key,"record":record,"point":point,"source":source,
                    "source_pointer":format!("/entries/{}", index),
                    "track_available":weekly.as_ref().is_some_and(|(_,w)| w["tracks"].get(key).is_some()),
                    "crop":self.noaa_crop(&r.date,key)?}));
            }
            groups.push(json!({"status":status,"rows":rows}));
        }
        let weekly_context = if has_weekly {
            let (track_source, tracks) = weekly.unwrap();
            let (center_source, centers) = self.noaa_weekly(&r.date, "-state")?;
            let (contour_source, contours) = self.noaa_weekly(&r.date, "-contour-state")?;
            Some(
                json!({"track_source":track_source,"center_source":center_source,"contour_source":contour_source,
                "start_date":tracks["start_date"],"end_date":tracks["end_date"],"identity_limit":tracks["identity_limit"],
                "center_relations":centers["states"][&r.state_code],"contour_relations":contours["states"][&r.state_code],
                "center_claim_limit":centers["claim_limit"],"contour_claim_limit":contours["claim_limit"]}),
            )
        } else {
            None
        };
        Ok(
            json!({"ok":true,"date":r.date,"state_code":r.state_code,"source":source,
            "source_sha256":daily["source_sha256"],"identity_limit":daily["identity_limit"],
            "coverage_limit":daily["coverage_limit"],"method":daily["method"],"groups":groups,"weekly":weekly_context}),
        )
    }
    pub fn noaa_track_view(&self, bytes: &[u8]) -> Result<Value, String> {
        let r: TrackSelection = serde_json::from_slice(bytes).map_err(|e| e.to_string())?;
        let (_, daily, has_weekly) = self.noaa_snapshot(&r.date, &r.state_code)?;
        if !has_weekly {
            return Err("No weekly track file for this sample date".into());
        }
        if !daily["entries"]
            .as_array()
            .ok_or("Missing NOAA detections")?
            .iter()
            .any(|e| e["id"].as_str() == Some(&r.detection_id))
        {
            return Err("Detection does not belong to this source date".into());
        }
        let (source, weekly) = self.noaa_weekly(&r.date, "")?;
        let record = weekly["tracks"]
            .get(&r.detection_id)
            .ok_or("Unknown NOAA track address")?;
        let positions = record["positions"]
            .as_array()
            .ok_or("Missing track positions")?;
        if positions.is_empty()
            || !positions
                .iter()
                .any(|p| p["date"].as_str() == Some(&r.focus_date))
        {
            return Err("Focus date is not an observed position in this track file".into());
        }
        let coordinates = Value::Array(positions.iter().map(|p| p["center"].clone()).collect());
        let path = if positions.len() == 1 {
            let (x, y) = crate::cartography::root(
                crate::map::point(&positions[0]["center"]).ok_or("Invalid NOAA center")?,
            );
            format!("M {x:.1},{y:.1} ")
        } else {
            crate::map::path_formatted(&coordinates, false, |p| {
                let (x, y) = crate::cartography::root(p);
                format!("{x:.1},{y:.1}")
            })
            .ok_or("Invalid NOAA track geometry")?
        };
        let points = positions
            .iter()
            .map(|p| {
                crate::map::point(&p["center"])
                    .map(crate::cartography::root)
                    .map(|(x, y)| json!([x, y]))
                    .ok_or("Invalid NOAA center")
            })
            .collect::<Result<Vec<_>, _>>()?;
        let (_, centers) = self.noaa_weekly(&r.date, "-state")?;
        let (_, contours) = self.noaa_weekly(&r.date, "-contour-state")?;
        let selection = self.noaa_source("research/nasa-perpetual-ocean-state-tile-join.json")?;
        let movie = &selection["states"][&r.state_code];
        let tile = movie["matches"].as_array().and_then(|a| {
            a.iter()
                .find(|v| v["tile_id"] == movie["recommended_regional_tiles"][0])
        });
        let timeline = self.noaa_source("research/nasa-perpetual-ocean-crop-timeline.json")?;
        let seek = &timeline["dates"][&r.focus_date];
        let movie_context = if tile.is_some() && !seek.is_null() {
            json!({"tile":tile,"seek":seek,
            "date":r.focus_date,"scope":"Approximate regional model-date context; no NOAA to NASA eddy identity match."})
        } else {
            Value::Null
        };
        Ok(
            json!({"ok":true,"date":r.date,"state_code":r.state_code,"detection_id":r.detection_id,
            "focus_date":r.focus_date,"source":source,"source_pointer":format!("/tracks/{}",r.detection_id),
            "record":record,"path":path,"points":points,"identity_limit":weekly["identity_limit"],
            "center_visits":centers["tracks"][&r.detection_id],"contour_visits":contours["tracks"][&r.detection_id],
            "movie_context":movie_context}),
        )
    }
}
