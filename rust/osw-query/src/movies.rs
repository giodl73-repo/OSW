//! Movie navigation preserves the exact rights-screened preview subset.
use crate::{Bundle, Store};
use serde::Deserialize;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
const ROOT: &str = "almanac/release/v0.1.0-rights-screened-preview/";
const NAMES: [&str; 4] = ["tiles", "tile_state_relations", "media", "entities"];

fn source(bundle: &Bundle, name: &str) -> Result<Value, String> {
    let receipt = &bundle.manifest["movies_receipts"][name];
    let raw = receipt["source_json"]
        .as_str()
        .ok_or("Missing screened movie source receipt")?;
    let path = format!("{ROOT}{name}.json");
    let hash = format!("{:x}", Sha256::digest(raw.as_bytes()));
    if receipt["source_file"] != path
        || receipt["source_sha256"] != hash
        || bundle.manifest["input_sha256"][&path] != hash
    {
        return Err("Changed screened movie source receipt".into());
    }
    serde_json::from_str(raw).map_err(|e| e.to_string())
}

fn catalog(bundle: &Bundle) -> Result<BTreeMap<&'static str, Vec<Value>>, String> {
    let receipts = bundle.manifest["movies_receipts"]
        .as_object()
        .ok_or("Missing screened movie receipts")?;
    if receipts.keys().map(String::as_str).collect::<BTreeSet<_>>()
        != BTreeSet::from([
            "manifest",
            "tiles",
            "tile_state_relations",
            "media",
            "entities",
        ])
    {
        return Err("Invalid screened movie receipt inventory".into());
    }
    let manifest = source(bundle, "manifest")?;
    if manifest["status"] != "rights_screened_preview_not_published"
        || manifest["source_manifest_sha256"]
            != bundle.manifest["input_sha256"]["almanac/release/v0.1.0/manifest.json"]
    {
        return Err("Invalid screened movie export scope or parent".into());
    }
    let files = manifest["files"]
        .as_array()
        .ok_or("Missing screened movie file manifest")?;
    let mut result = BTreeMap::new();
    for name in NAMES {
        let rows = source(bundle, name)?
            .as_array()
            .ok_or("Invalid screened movie collection")?
            .clone();
        let mut ids = BTreeSet::new();
        let canonical = bundle
            .collections
            .get(name)
            .ok_or("Missing canonical movie collection")?;
        let matching: Vec<_> = files
            .iter()
            .filter(|r| r["path"] == format!("{name}.json"))
            .collect();
        if matching.len() != 1 || matching[0]["sha256"] != receipts[name]["source_sha256"] {
            return Err("Screened movie source disagrees with export manifest".into());
        }
        for row in &rows {
            let id = row["id"]
                .as_str()
                .ok_or("Missing screened movie record ID")?;
            if !ids.insert(id) || !canonical.iter().any(|r| r["id"] == id && r == row) {
                return Err("Screened movie record differs from canonical source".into());
            }
        }
        if ["tiles", "tile_state_relations"].contains(&name) && rows != *canonical {
            return Err("Incomplete screened crop or state-overlap inventory".into());
        }
        result.insert(name, rows);
    }
    let entities: BTreeSet<_> = result["entities"]
        .iter()
        .filter_map(|r| r["id"].as_str())
        .collect();
    let tiles: BTreeSet<_> = result["tiles"]
        .iter()
        .filter_map(|r| r["tile_id"].as_str())
        .collect();
    for row in &result["tile_state_relations"] {
        if !row["state_id"]
            .as_str()
            .is_some_and(|id| entities.contains(id))
            || !row["tile_id"].as_str().is_some_and(|id| tiles.contains(id))
            || row["predicate"] != "display_overlap"
            || row["physical_relation"] != "unresolved"
            || !row["display_coverage_fraction"]
                .as_f64()
                .is_some_and(|v| v.is_finite() && (0.0..=1.0).contains(&v))
        {
            return Err("Invalid screened movie display overlap".into());
        }
    }
    for row in &result["media"] {
        if !row["entity_id"]
            .as_str()
            .is_some_and(|id| entities.contains(id))
        {
            return Err("Unresolved screened movie entity".into());
        }
        if let Some(id) = row["tile_id"].as_str() {
            if !tiles.contains(id) {
                return Err("Unresolved screened movie crop".into());
            }
        }
    }
    Ok(result)
}
pub fn validate(bundle: &Bundle) -> Result<(), String> {
    if bundle.manifest.get("movies_receipts").is_some() {
        catalog(bundle)?;
    }
    Ok(())
}

#[derive(Deserialize, Default)]
#[serde(deny_unknown_fields)]
struct Selection {
    #[serde(default)]
    query: String,
    zoom: Option<u8>,
    state_id: Option<String>,
}
impl Store {
    pub fn movie_view(&self, bytes: &[u8]) -> Result<Value, String> {
        let selection: Selection = serde_json::from_slice(bytes).map_err(|e| e.to_string())?;
        if selection.zoom.is_some_and(|z| z > 2) {
            return Err("Unsupported movie zoom level".into());
        }
        let data = catalog(&self.bundle)?;
        let entities: BTreeMap<_, _> = data["entities"]
            .iter()
            .map(|r| (r["id"].as_str().unwrap(), r))
            .collect();
        let mut states: Vec<_> = data["entities"]
            .iter()
            .filter(|r| r["type"] == "osw_state")
            .collect();
        states.sort_by_key(|r| {
            (
                r["label"].as_str().unwrap_or("").to_lowercase(),
                r["id"].as_str().unwrap(),
            )
        });
        if selection
            .state_id
            .as_ref()
            .is_some_and(|id| !states.iter().any(|r| r["id"] == *id))
        {
            return Err("Unknown movie state".into());
        }
        let query = selection.query.trim().to_lowercase();
        let mut rows = Vec::new();
        for tile in &data["tiles"] {
            if selection.zoom.is_some_and(|z| tile["zoom"] != z) {
                continue;
            }
            let mut overlaps: Vec<_> = data["tile_state_relations"]
                .iter()
                .filter(|r| r["tile_id"] == tile["tile_id"])
                .collect();
            if selection
                .state_id
                .as_ref()
                .is_some_and(|id| !overlaps.iter().any(|r| r["state_id"] == *id))
            {
                continue;
            }
            let ids: BTreeSet<_> = data["media"]
                .iter()
                .filter(|r| r["tile_id"] == tile["tile_id"])
                .filter_map(|r| r["entity_id"].as_str())
                .collect();
            let mut objects: Vec<_> = ids.iter().map(|id| entities[id]).collect();
            if !query.is_empty()
                && !tile["tile_id"]
                    .as_str()
                    .unwrap()
                    .to_lowercase()
                    .contains(&query)
                && !objects.iter().any(|r| {
                    r["label"]
                        .as_str()
                        .unwrap_or("")
                        .to_lowercase()
                        .contains(&query)
                })
            {
                continue;
            }
            overlaps.sort_by(|a, b| {
                b["display_coverage_fraction"]
                    .as_f64()
                    .unwrap()
                    .total_cmp(&a["display_coverage_fraction"].as_f64().unwrap())
                    .then_with(|| a["id"].as_str().cmp(&b["id"].as_str()))
            });
            objects.sort_by_key(|r| {
                (
                    r["label"].as_str().unwrap_or("").to_lowercase(),
                    r["id"].as_str().unwrap(),
                )
            });
            let state_links: Vec<_> = overlaps
                .iter()
                .map(|r| json!({"entity":entities[r["state_id"].as_str().unwrap()],"relation":r}))
                .collect();
            rows.push(json!({"tile":tile,"states":state_links,"objects":objects}));
        }
        Ok(
            json!({"ok":true,"engine":"rust-osw-query-v1","bundle_sha256":self.metadata()["bundle_sha256"],"source_scope":"rights_screened_preview_not_published","selection":{"query":query,"zoom":selection.zoom,"state_id":selection.state_id},"states":states,"total":data["tiles"].len(),"matched":rows.len(),"rows":rows}),
        )
    }
}
