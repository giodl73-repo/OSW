//! Editorial identity membership, independent of physical flow and measurement joins.
use serde::Deserialize;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
pub const SCOPE: &str = "Existing editorial identity facets and ledger parent assignments; not flow connectivity, physical containment, equivalent identities or inherited measurements. Missing members remain unassessed.";
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Selection {
    pub root_id: String,
    pub relation: String,
    #[serde(default)]
    pub include_root: bool,
}

pub fn select(
    collections: &BTreeMap<String, Vec<Value>>,
    selection: &Selection,
) -> Result<BTreeSet<String>, String> {
    if !collections["objects"]
        .iter()
        .any(|r| r["id"] == selection.root_id)
    {
        return Err("Unknown taxonomy root".into());
    }
    if !["children", "parents", "descendants", "ancestors"].contains(&selection.relation.as_str()) {
        return Err("Unknown taxonomy relation".into());
    }
    let down = ["children", "descendants"].contains(&selection.relation.as_str());
    let recursive = ["descendants", "ancestors"].contains(&selection.relation.as_str());
    let mut seen = BTreeSet::from([selection.root_id.clone()]);
    let mut frontier = vec![selection.root_id.clone()];
    let edges = collections.get("taxonomy_links");
    while let Some(id) = frontier.pop() {
        for e in edges.into_iter().flatten() {
            let (from, to) = if down {
                ("parent_id", "child_id")
            } else {
                ("child_id", "parent_id")
            };
            if e[from] == id {
                let target = e[to].as_str().ok_or("Invalid taxonomy target")?.to_owned();
                if seen.insert(target.clone()) && recursive {
                    frontier.push(target);
                }
            }
        }
        if !recursive {
            break;
        }
    }
    if !selection.include_root {
        seen.remove(&selection.root_id);
    }
    Ok(seen)
}

pub fn context(collections: &BTreeMap<String, Vec<Value>>, id: &str) -> Value {
    let links = collections.get("taxonomy_links");
    json!({"scope":SCOPE,"parents":links.into_iter().flatten().filter(|e|e["child_id"]==id).collect::<Vec<_>>(),
        "children":links.into_iter().flatten().filter(|e|e["parent_id"]==id).collect::<Vec<_>>(),"physical_completeness":false,"measurement_inheritance_eligible":false})
}
pub fn metadata(collections: &BTreeMap<String, Vec<Value>>, manifest: &Value) -> Value {
    if manifest.get("taxonomy").is_none() {
        return Value::Null;
    }
    json!({"scope":SCOPE,"identity_levels":manifest["taxonomy"]["identity_levels"],"link_count":collections.get("taxonomy_links").map(Vec::len).unwrap_or(0),
        "nodes":collections["objects"].iter().map(|r|json!({"id":r["id"],"label":r["label"],"identity_level":r["identity_level"]})).collect::<Vec<_>>()})
}

pub fn validate(
    collections: &BTreeMap<String, Vec<Value>>,
    manifest: &Value,
) -> Result<(), String> {
    if !collections.contains_key("taxonomy_links") && manifest.get("taxonomy").is_none() {
        return Ok(());
    }
    let graph = &manifest["taxonomy"];
    if graph["schema"] != "osw.query-taxonomy.v1"
        || graph["scope"] != SCOPE
        || graph["complete_physical_taxonomy"] != false
        || graph["measurement_inheritance_eligible"] != false
    {
        return Err("Invalid taxonomy scope".into());
    }
    let receipts = graph["source_receipts"]
        .as_array()
        .ok_or("Missing taxonomy receipts")?;
    if receipts.len() != 2 {
        return Err("Taxonomy requires two source receipts".into());
    }
    let mut docs = BTreeMap::new();
    for receipt in receipts {
        let file = receipt["file"]
            .as_str()
            .ok_or("Missing taxonomy receipt file")?;
        let raw = receipt["source_json"]
            .as_str()
            .ok_or("Missing taxonomy source JSON")?;
        let hash = format!("{:x}", Sha256::digest(raw.as_bytes()));
        if receipt["sha256"] != hash || manifest["input_sha256"][file] != hash {
            return Err("Changed taxonomy receipt".into());
        }
        let doc: Value = serde_json::from_str(raw).map_err(|_| "Invalid taxonomy source JSON")?;
        if docs.insert(file.to_owned(), doc).is_some() {
            return Err("Duplicate taxonomy receipt".into());
        }
    }
    let ledger = docs
        .get("research/ocean-current-almanac.json")
        .ok_or("Missing taxonomy ledger")?;
    let vocabulary = docs
        .get("research/ocean-motion-taxonomy.json")
        .ok_or("Missing taxonomy vocabulary")?;
    if graph["identity_levels"] != vocabulary["axes"]["identity_level"] {
        return Err("Changed taxonomy vocabulary projection".into());
    }
    let objects: &Vec<Value> = &collections["objects"];
    if graph["node_count"] != json!(objects.len()) {
        return Err("Taxonomy node count mismatch".into());
    }
    let nodes: BTreeMap<&str, &Value> = objects
        .iter()
        .map(|r| (r["id"].as_str().unwrap(), r))
        .collect();
    let entities = collections
        .get("entities")
        .ok_or("Missing taxonomy identity sources")?;
    let expected_nodes: BTreeSet<&str> = entities
        .iter()
        .filter(|r| {
            matches!(
                r["type"].as_str(),
                Some("named_current" | "named_eddy" | "operational_eddy_detection")
            )
        })
        .filter_map(|r| r["id"].as_str())
        .collect();
    if nodes.keys().copied().collect::<BTreeSet<_>>() != expected_nodes {
        return Err("Incomplete taxonomy object inventory".into());
    }
    for node in objects {
        let entity = entities
            .iter()
            .find(|r| r["id"] == node["id"])
            .ok_or("Unresolved taxonomy identity")?;
        for key in [
            "type",
            "identity_level",
            "setting",
            "time_behavior",
            "basin",
            "label",
        ] {
            if node[key] != entity[key] {
                return Err("Taxonomy facet differs from identity source".into());
            }
        }
        let kind = node["identity_level"]
            .as_str()
            .ok_or("Missing taxonomy identity kind")?;
        if vocabulary["axes"]["identity_level"].get(kind).is_none() {
            return Err("Unknown taxonomy identity kind".into());
        }
    }
    let entries = ledger["entries"]
        .as_array()
        .ok_or("Missing taxonomy ledger entries")?;
    let actual = collections
        .get("taxonomy_links")
        .ok_or("Missing taxonomy links")?;
    let mut expected = Vec::new();
    for (i, row) in entries.iter().enumerate() {
        let Some(parent) = row["part_of_system"].as_str() else {
            continue;
        };
        let child = row["id"].as_str().ok_or("Missing taxonomy child")?;
        let child_id = format!("current:{child}");
        let parent_id = format!("current:{parent}");
        let c = nodes
            .get(child_id.as_str())
            .ok_or("Unresolved taxonomy child")?;
        let p = nodes
            .get(parent_id.as_str())
            .ok_or("Unresolved taxonomy parent")?;
        if child_id == parent_id
            || !matches!(p["identity_level"].as_str(), Some("family" | "system"))
        {
            return Err("Unsupported taxonomy parent".into());
        }
        let name_source = row["name_source"]
            .as_str()
            .ok_or("Missing taxonomy naming source")?;
        expected.push(json!({"id":format!("taxonomy-link:{child}"),"child_id":child_id,"parent_id":parent_id,"child_label":c["label"],"parent_label":p["label"],
            "predicate":if p["identity_level"]=="family"{"basin_or_subfamily_member_of"}else{"named_system_component_of"},
            "status":"existing_editorial_ledger_assignment_not_new_canonical_relation","source_file":"research/ocean-current-almanac.json","source_pointer":format!("/entries/{i}/part_of_system"),
            "evidence_role":"existing_editorial_parent_assignment","naming_source_url":ledger["sources"][name_source],"naming_source_is_parent_relation_evidence":false,
            "physical_connectivity_eligible":false,"measurement_inheritance_eligible":false,"scope":SCOPE}));
    }
    expected.sort_by(|a, b| a["id"].as_str().cmp(&b["id"].as_str()));
    let mut sorted = actual.clone();
    sorted.sort_by(|a, b| a["id"].as_str().cmp(&b["id"].as_str()));
    if sorted != expected || graph["link_count"] != json!(actual.len()) {
        return Err("Taxonomy links differ from ledger parent assignments".into());
    }
    // Every lineage must terminate; connected branches may share a parent.
    for id in nodes.keys() {
        let mut ancestors = BTreeSet::new();
        let mut cursor = *id;
        loop {
            if !ancestors.insert(cursor) {
                return Err("Cyclic taxonomy parent assignments".into());
            }
            let Some(edge) = actual.iter().find(|e| e["child_id"] == cursor) else {
                break;
            };
            cursor = edge["parent_id"]
                .as_str()
                .ok_or("Invalid taxonomy parent")?;
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn lineage_keeps_depth_direction_and_root_explicit() {
        let c = BTreeMap::from([
            (
                "objects".into(),
                vec![
                    json!({"id":"f"}),
                    json!({"id":"s"}),
                    json!({"id":"a"}),
                    json!({"id":"b"}),
                ],
            ),
            (
                "taxonomy_links".into(),
                vec![
                    json!({"parent_id":"f","child_id":"s"}),
                    json!({"parent_id":"s","child_id":"a"}),
                    json!({"parent_id":"s","child_id":"b"}),
                ],
            ),
        ]);
        let q = |id: &str, relation: &str, include_root| Selection {
            root_id: id.into(),
            relation: relation.into(),
            include_root,
        };
        assert_eq!(
            select(&c, &q("f", "children", false)).unwrap(),
            BTreeSet::from(["s".into()])
        );
        assert_eq!(
            select(&c, &q("f", "descendants", false)).unwrap(),
            BTreeSet::from(["s".into(), "a".into(), "b".into()])
        );
        assert_eq!(
            select(&c, &q("a", "ancestors", true)).unwrap(),
            BTreeSet::from(["a".into(), "s".into(), "f".into()])
        );
        assert!(select(&c, &q("a", "children", false)).unwrap().is_empty());
        assert!(select(&c, &q("unknown", "parents", false)).is_err());
        assert!(select(&c, &q("f", "physical_flow", false)).is_err());
    }
}
