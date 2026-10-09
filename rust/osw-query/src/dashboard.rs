use crate::{Bundle, Store};
use serde::Deserialize;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::BTreeSet;

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Selection {
    #[serde(default)]
    text: String,
    record_type: Option<String>,
    metric: String,
    view_box: Option<[f64; 4]>,
    #[serde(default)]
    covered_only: bool,
    #[serde(default)]
    changed_only: bool,
    #[serde(default)]
    changed_ids: Vec<String>,
}

// Objects retain the dashboard's fields and may add checked query joins.
fn includes(actual: &Value, source: &Value) -> bool {
    match source {
        Value::Object(fields) => fields.iter().all(|(k, v)| includes(&actual[k], v)),
        _ => actual == source,
    }
}

fn document(bundle: &Bundle) -> Result<Value, String> {
    let receipt = &bundle.manifest["dashboard_receipt"];
    let path = "research/ocean-motion-dashboard.json";
    let raw = receipt["source_json"]
        .as_str()
        .ok_or("Missing dashboard source bytes")?;
    let hash = format!("{:x}", Sha256::digest(raw.as_bytes()));
    if receipt["source_file"] != path
        || receipt["source_sha256"] != hash
        || bundle.manifest["input_sha256"][path] != hash
    {
        return Err("Changed dashboard source receipt".into());
    }
    serde_json::from_str(raw).map_err(|e| format!("Invalid dashboard source JSON: {e}"))
}

pub fn validate(bundle: &Bundle) -> Result<(), String> {
    // Older journal snapshots remain readable without this new presentation API.
    if bundle.manifest.get("dashboard_receipt").is_none() {
        return Ok(());
    }
    let doc = document(bundle)?;
    if doc["schema"] != "osw.motion-dashboard.v1" || doc["fingerprint_version"] != 2 {
        return Err("Unsupported dashboard snapshot".into());
    }
    let rows = doc["entries"]
        .as_array()
        .ok_or("Missing dashboard entries")?;
    let objects = &bundle.collections["objects"];
    let mut ids = BTreeSet::new();
    if rows.len() != objects.len() {
        return Err("Incomplete dashboard identity coverage".into());
    }
    for row in rows {
        let id = row["id"].as_str().ok_or("Missing dashboard object ID")?;
        if !ids.insert(id) {
            return Err("Duplicate dashboard object ID".into());
        }
        let object = objects
            .iter()
            .find(|o| o["id"] == id)
            .ok_or("Unresolved dashboard object")?;
        if let Some(search) = object.get("dashboard_search") {
            if search
                != &format!(
                    "{} {}",
                    row["label"].as_str().ok_or("Missing dashboard label")?,
                    row["basin"].as_str().ok_or("Missing dashboard basin")?
                )
            {
                return Err("Dashboard search projection differs from its source".into());
            }
        }
        for (key, value) in row.as_object().ok_or("Invalid dashboard entry")? {
            if key == "map_features" {
                let source = value.as_array().ok_or("Invalid dashboard geometry")?;
                let actual = object[key].as_array().ok_or("Missing query geometry")?;
                if source
                    .iter()
                    .any(|f| !actual.iter().any(|a| includes(a, f)))
                {
                    return Err(format!("Dashboard map projection differs for {id}"));
                }
            } else if !includes(&object[key], value) {
                return Err(format!(
                    "Dashboard object projection differs for {id}/{key}"
                ));
            }
        }
    }
    for kind in ["named_current", "named_eddy", "operational_eddy_detection"] {
        let count = objects.iter().filter(|r| r["type"] == kind).count();
        if doc["counts"][kind] != count {
            return Err("Dashboard totals differ from the query inventory".into());
        }
    }
    Ok(())
}

impl Store {
    pub fn dashboard_select(&self, bytes: &[u8]) -> Result<Value, String> {
        let request: Selection = serde_json::from_slice(bytes).map_err(|e| e.to_string())?;
        if ![
            "reported_length",
            "reference_route",
            "scoped_width",
            "radius_evidence",
            "geometry",
            "time_samples",
            "observed_velocity",
            "source_connectivity",
            "scope_notes",
            "dated_diagnostics",
            "flow_network",
            "passage_transport",
        ]
        .contains(&request.metric.as_str())
        {
            return Err("Unknown dashboard evidence metric".into());
        }
        if request.record_type.as_ref().is_some_and(|t| {
            !["named_current", "named_eddy", "operational_eddy_detection"].contains(&t.as_str())
        }) {
            return Err("Unknown dashboard object type".into());
        }
        let objects = &self.bundle.collections["objects"];
        let changed: BTreeSet<_> = request.changed_ids.iter().map(String::as_str).collect();
        if changed.len() != request.changed_ids.len()
            || changed
                .iter()
                .any(|id| !self.ids["objects"].contains_key(*id))
        {
            return Err("Unresolved or duplicate dashboard changed ID".into());
        }
        let mut query = json!({"collection":"objects","filters":[{"field":"dashboard_search","op":"contains","value":request.text.trim()}],"sort":{"field":"label"},"limit":500,"offset":0});
        if let Some(kind) = &request.record_type {
            query["record_type"] = json!(kind);
        }
        if request.covered_only {
            query["evidence"] = json!(request.metric);
        }
        let mut ids = Vec::new();
        loop {
            let result = self.execute(&serde_json::to_vec(&query).map_err(|e| e.to_string())?);
            if result["ok"] != true {
                return Err(result["error"]
                    .as_str()
                    .unwrap_or("Dashboard query failed")
                    .to_owned());
            }
            let rows = result["rows"]
                .as_array()
                .ok_or("Missing dashboard query rows")?;
            ids.extend(
                rows.iter()
                    .filter_map(|r| r["id"].as_str())
                    .map(str::to_owned),
            );
            if ids.len()
                >= result["total"]
                    .as_u64()
                    .ok_or("Missing dashboard query total")? as usize
            {
                break;
            }
            if rows.is_empty() {
                return Err("Incomplete dashboard query page".into());
            }
            query["offset"] = json!(ids.len());
        }
        if request.changed_only {
            ids.retain(|id| changed.contains(id.as_str()));
        }
        let beck_scene = if self.bundle.manifest.get("dashboard_receipt").is_some() {
            crate::dashboard_beck::scene(
                &document(&self.bundle)?,
                &ids,
                &request.metric,
                &changed,
                request.view_box.unwrap_or([60., 90., 1480., 740.]),
            )?
        } else {
            Value::Null
        };
        let map_scene = if self.bundle.manifest.get("dashboard_receipt").is_some() {
            crate::dashboard_map::scene(&document(&self.bundle)?, &ids, &request.metric, &changed)?
        } else {
            Value::Null
        };
        Ok(
            json!({"ok":true,"engine":"rust-osw-query-v1","ids":ids,"map_scene":map_scene,"beck_scene":beck_scene,"total":objects.len(),
            "covered_count":objects.iter().filter(|r| r["capabilities"][&request.metric].as_u64().unwrap_or(0)>0).count(),
            "changed_count":changed.len()}),
        )
    }
    pub fn dashboard_snapshot(&self) -> Result<Value, String> {
        Ok(json!({"ok":true,"engine":"rust-osw-query-v1",
                  "bundle_sha256":self.metadata()["bundle_sha256"],
            "snapshot_json":self.bundle.manifest["dashboard_receipt"]["source_json"].as_str().ok_or("Missing dashboard source bytes")?}))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn selection_keeps_records_beyond_a_query_page() {
        let rows: Vec<_> = (0..640).map(|i| json!({"id":format!("current:{i:04}"),
            "type":"named_current","label":format!("Current {i:04}"),"basin":"Example",
            "dashboard_search":format!("Current {i:04} Example"),"capabilities":{"reference_route":1}})).collect();
        let store = Store::load(
            &serde_json::to_vec(&json!({"schema":"osw.query-bundle.v1",
            "manifest":{},"collections":{"objects":rows}}))
            .unwrap(),
        )
        .unwrap();
        let result = store
            .dashboard_select(br#"{"metric":"reference_route","covered_only":true}"#)
            .unwrap();
        assert_eq!(result["ids"].as_array().unwrap().len(), 640);
        assert_eq!(result["ids"][639], "current:0639");
        assert_eq!(result["covered_count"], 640);
        let changed = store.dashboard_select(br#"{"metric":"reference_route","changed_only":true,"changed_ids":["current:0639"]}"#).unwrap();
        assert_eq!(changed["ids"], json!(["current:0639"]));
    }
}
