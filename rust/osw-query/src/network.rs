//! Source-bound conceptual flow networks; connectivity never implies metric length.
use serde::Deserialize;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PathQuery {
    pub network_id: String,
    pub from_id: String,
    pub to_id: String,
    pub max_hops: usize,
}

pub fn validate(
    collections: &BTreeMap<String, Vec<Value>>,
    manifest: &Value,
) -> Result<(), String> {
    for name in [
        "flow_network_nodes",
        "flow_network_edges",
        "passage_samples",
    ] {
        for row in collections.get(name).into_iter().flatten() {
            if !collections
                .get("flow_networks")
                .into_iter()
                .flatten()
                .any(|n| n["id"] == row["network_id"])
            {
                return Err("Orphan network projection".into());
            }
        }
    }
    for record in collections.get("flow_networks").into_iter().flatten() {
        let doc = &record["document"];
        let raw = record["source_json"]
            .as_str()
            .ok_or("Missing network source JSON")?;
        let original: Value =
            serde_json::from_str(raw).map_err(|_| "Invalid network source JSON")?;
        let file = record["source_file"]
            .as_str()
            .ok_or("Missing network source file")?;
        if original != *doc
            || json!(format!("{:x}", Sha256::digest(raw.as_bytes())))
                != record["source_file_sha256"]
            || record["source_file_sha256"] != manifest["input_sha256"][file]
        {
            return Err("Network source binding mismatch".into());
        }
        if record["id"] != doc["id"]
            || record["entity_id"] != doc["entity_id"]
            || record["rank_eligible"] != false
            || doc["rank_eligible"] != false
            || [
                "length_km",
                "width_km",
                "annual_length_range_km",
                "annual_width_range_km",
            ]
            .iter()
            .any(|k| !doc.get(k).is_some_and(Value::is_null))
        {
            return Err("Network identity or dimension admission mismatch".into());
        }
        let owner = collections
            .get("objects")
            .into_iter()
            .flatten()
            .find(|o| o["id"] == record["entity_id"])
            .ok_or("Missing network owner")?;
        if !owner["flow_network_ids"]
            .as_array()
            .is_some_and(|ids| ids.contains(&record["id"]))
        {
            return Err("Missing owner network join".into());
        }
        for sample in doc["passage_samples"]
            .as_array()
            .ok_or("Missing network samples")?
        {
            if !owner["passage_sample_ids"]
                .as_array()
                .is_some_and(|ids| ids.contains(&sample["id"]))
            {
                return Err("Missing owner passage join".into());
            }
        }
        let node_ids: BTreeSet<_> = doc["nodes"]
            .as_array()
            .ok_or("Missing network nodes")?
            .iter()
            .filter_map(|n| n["id"].as_str())
            .collect();
        for edge in doc["edges"].as_array().ok_or("Missing network edges")? {
            if !node_ids.contains(edge["from_id"].as_str().unwrap_or(""))
                || !node_ids.contains(edge["to_id"].as_str().unwrap_or(""))
                || !edge["geometry"].is_null()
                || !edge["length_km"].is_null()
            {
                return Err("Network endpoint or geometry mismatch".into());
            }
        }
        for (key, name) in [
            ("nodes", "flow_network_nodes"),
            ("edges", "flow_network_edges"),
            ("passage_samples", "passage_samples"),
        ] {
            let originals = doc[key]
                .as_array()
                .ok_or("Missing network source records")?;
            let rows: Vec<_> = collections
                .get(name)
                .into_iter()
                .flatten()
                .filter(|r| r["network_id"] == record["id"])
                .collect();
            if rows.len() != originals.len() {
                return Err("Network record inventory mismatch".into());
            }
            for source in originals {
                let row = rows
                    .iter()
                    .find(|r| r["id"] == source["id"])
                    .ok_or("Missing network projection")?;
                if row["source_record"] != *source
                    || row["entity_id"] != record["entity_id"]
                    || row["source_file_sha256"] != record["source_file_sha256"]
                    || row["rank_eligible"] != false
                    || source
                        .as_object()
                        .ok_or("Invalid source record")?
                        .iter()
                        .any(|(k, v)| row.get(k) != Some(v))
                {
                    return Err("Network projection differs from source".into());
                }
                if name == "passage_samples" {
                    let sites = source["moorings"]
                        .as_array()
                        .ok_or("Missing mooring sites")?;
                    let marks = row["map_features"]
                        .as_array()
                        .ok_or("Missing mooring map marks")?;
                    if sites.iter().zip(marks).any(|(s, m)| {
                        m["mooring_label"] != s["label"]
                            || m["deployment_start"] != s["deployment_start"]
                            || m["deployment_end"] != s["deployment_end"]
                            || m["source_url"] != doc["source_url"]
                            || m["source_file_sha256"] != record["source_file_sha256"]
                    }) {
                        return Err("Network mooring provenance mismatch".into());
                    }
                    if sites.len()!=marks.len() || sites.iter().zip(marks).any(|(s,m)|m["geometry"]["type"]!="Point" || m["geometry"]["coordinates"]!=s["coordinates_lon_lat"] || m["role"]!="published_mooring_locator_not_axis_edge_or_whole_current_footprint"){return Err("Network mooring geometry mismatch".into());}
                }
            }
        }
    }
    Ok(())
}

pub fn paths(
    collections: &BTreeMap<String, Vec<Value>>,
    query: &PathQuery,
) -> Result<Value, String> {
    if query.max_hops == 0 || query.max_hops > 16 {
        return Err("Network max_hops must be 1–16".into());
    }
    let network = collections
        .get("flow_networks")
        .into_iter()
        .flatten()
        .find(|r| r["id"] == query.network_id)
        .ok_or("Unknown flow network")?;
    let doc = &network["document"];
    let nodes: BTreeSet<_> = doc["nodes"]
        .as_array()
        .ok_or("Missing nodes")?
        .iter()
        .filter_map(|n| n["id"].as_str())
        .collect();
    if !nodes.contains(query.from_id.as_str()) || !nodes.contains(query.to_id.as_str()) {
        return Err("Unknown network node".into());
    }
    let mut paths = Vec::new();
    let mut stack = vec![vec![query.from_id.clone()]];
    let mut steps = 0;
    let mut truncated = false;
    let mut hop_limit_reached = false;
    while let Some(path) = stack.pop() {
        steps += 1;
        if steps > 4096 {
            truncated = true;
            break;
        }
        let last = path.last().unwrap();
        if last == &query.to_id {
            if paths.len() == 64 {
                truncated = true;
                break;
            }
            paths.push(path);
            continue;
        }
        if path.len() - 1 >= query.max_hops {
            hop_limit_reached = true;
            continue;
        }
        for edge in doc["edges"]
            .as_array()
            .ok_or("Missing edges")?
            .iter()
            .rev()
            .filter(|e| e["from_id"] == *last)
        {
            let next = edge["to_id"].as_str().ok_or("Missing edge target")?;
            if !path.iter().any(|v| v == next) {
                let mut branch = path.clone();
                branch.push(next.into());
                stack.push(branch);
            }
        }
    }
    Ok(
        json!({"network_id":query.network_id,"from_id":query.from_id,"to_id":query.to_id,"node_labels":doc["nodes"].as_array().unwrap().iter().map(|n|(n["id"].as_str().unwrap().to_owned(),n["label"].clone())).collect::<BTreeMap<_,_>>(),"paths":paths,"truncated":truncated,"hop_limit_reached":hop_limit_reached,"max_hops":query.max_hops,"length_km":null,"scope":"Simple source-described conceptual connections, bounded search. Not a particle trajectory, travel time, continuous velocity axis or measurable current length."}),
    )
}
