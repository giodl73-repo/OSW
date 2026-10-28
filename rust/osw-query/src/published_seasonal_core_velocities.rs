//! Published seasonal fits are distinct from pooled sample-speed statistics.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};

const SOURCE: &str = "research/atlantic-ax08-goes-2013-seasonal-core-speeds-v1.json";
const RAW: &str =
    include_str!("../../../research/atlantic-ax08-goes-2013-seasonal-core-speeds-v1.json");
const COLLECTION: &str = "current_core_velocity_estimates";
const JOIN: &str = "core_velocity_estimate_ids";
const KEY: &str = "published_seasonal_core_velocities_v1";
const PARENT: &str = "037ef0045d75dac4b8893df9bf200bd55e049d4708ceaa56195df9d6da9f5cc4";

fn pin() -> String {
    format!("{:x}", Sha256::digest(RAW.as_bytes()))
}

fn expected() -> Vec<Value> {
    let doc: Value = serde_json::from_str(RAW).unwrap();
    doc["records"].as_array().unwrap().iter().enumerate().map(|(index, original)| {
        let mut row = original.clone();
        let scope = doc["current_scopes"].as_array().unwrap().iter()
            .find(|r| r["current_id"] == row["current_id"]).unwrap();
        let discrepancies: Vec<_> = doc["method_discrepancies"].as_array().unwrap().iter()
            .filter(|r| r["current_id"] == row["current_id"]).cloned().collect();
        let extra = json!({"entity_id":format!("current:{}",row["current_id"].as_str().unwrap()),
            "label":format!("{} / {}",scope["source_label"].as_str().unwrap(),row["season_label"].as_str().unwrap()),
            "quantity":"geostrophic_core_velocity_seasonal_fit","unit":"m/s", "current_scope":scope,
            "common_support":doc["common_support"],"method_discrepancies":discrepancies,
            "source_file":SOURCE,"source_file_sha256":pin(),"source_pointer":format!("/records/{index}"),
            "source_doi":doc["source"]["doi"],"source_url":doc["source"]["url"],
            "observation_count":null,"confidence_interval":null,"whole_current":false,"geometry":null});
        row.as_object_mut().unwrap().extend(extra.as_object().unwrap().clone());
        row
    }).collect()
}

pub(crate) fn validate(bundle: &Bundle) -> Result<(), String> {
    let owners = bundle
        .collections
        .get("objects")
        .map(Vec::as_slice)
        .unwrap_or(&[]);
    let marker = &bundle.manifest[KEY];
    if !bundle.collections.contains_key(COLLECTION)
        && marker.is_null()
        && bundle.manifest["input_sha256"][SOURCE].is_null()
        && owners.iter().all(|r| r[JOIN].is_null())
    {
        return Ok(());
    }
    let rows = expected();
    if bundle.manifest["input_sha256"][SOURCE] != pin()
        || marker
            != &json!({"logical_parent_sha256":PARENT,"source_file":SOURCE,
            "source_file_sha256":pin(),"records_added":rows.len(),"length_or_width_records_added":0})
        || bundle.collections.get(COLLECTION) != Some(&rows)
    {
        return Err("Published seasonal core estimates or source binding differ".into());
    }
    for row in &rows {
        if owners
            .iter()
            .filter(|o| o["id"] == row["entity_id"])
            .count()
            != 1
        {
            return Err("Published seasonal core owner missing or duplicated".into());
        }
    }
    for owner in owners {
        let ids: Vec<_> = rows
            .iter()
            .filter(|r| r["entity_id"] == owner["id"])
            .map(|r| r["id"].clone())
            .collect();
        if (!ids.is_empty() || !owner[JOIN].is_null()) && owner[JOIN] != json!(ids) {
            return Err("Published seasonal core owner join differs".into());
        }
    }
    Ok(())
}

pub(crate) fn scene(matches: &[&Value]) -> Value {
    if matches.is_empty() {
        return Value::Null;
    }
    let doc: Value = serde_json::from_str(RAW).unwrap();
    json!({"kind":"published_seasonal_core_velocities",
        "title":"Atlantic AX08: published seasonal core velocities",
        "scope":"Regional XBT-derived seasonal fits, not direct speed samples. Boreal season labels have no exact month windows. The31 sections are shared across currents; no February section was sampled. Not observed annual extrema or current dimensions.",
        "records":matches,"common_support":doc["common_support"],
        "source_file":SOURCE,"source_url":doc["source"]["url"],
        "full_context_figure":doc["visualization"]["figure"]})
}

pub(crate) fn by_current(bundle: &Bundle) -> Value {
    let mut result = json!({});
    let rows = bundle
        .collections
        .get(COLLECTION)
        .map(Vec::as_slice)
        .unwrap_or(&[]);
    for row in rows {
        if let Some(id) = row["current_id"].as_str() {
            if result.get(id).is_none() {
                let matches: Vec<_> = rows.iter().filter(|r| r["current_id"] == id).collect();
                result[id] = scene(&matches);
            }
        }
    }
    result
}

#[cfg(test)]
mod tests {
    use super::*;

    fn candidate() -> Bundle {
        let rows = expected();
        let ids = [
            "atlantic-north-equatorial-countercurrent",
            "atlantic-north-equatorial-undercurrent",
            "atlantic-south-equatorial-undercurrent",
        ];
        let owners: Vec<_> = ids
            .iter()
            .map(|id| {
                let owner = format!("current:{id}");
                let joined: Vec<_> = rows
                    .iter()
                    .filter(|r| r["entity_id"] == owner)
                    .map(|r| r["id"].clone())
                    .collect();
                json!({"id":owner,(JOIN):joined})
            })
            .collect();
        Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest: json!({"input_sha256":{(SOURCE):pin()},(KEY):{
                "logical_parent_sha256":PARENT,"source_file":SOURCE,"source_file_sha256":pin(),
                "records_added":6,"length_or_width_records_added":0}}),
            collections: std::collections::BTreeMap::from([
                ("objects".into(), owners),
                (COLLECTION.into(), rows),
            ]),
        }
    }

    #[test]
    fn filtered_queries_preserve_qualifiers_without_map_geometry() {
        let bundle = candidate();
        let store = crate::Store::load(json!({"schema":bundle.schema,"manifest":bundle.manifest,"collections":bundle.collections}).to_string().as_bytes()).unwrap();
        let all = store.execute(br#"{"collection":"current_core_velocity_estimates","limit":1}"#);
        assert_eq!(all["ok"], true);
        assert_eq!(all["total"], 6);
        assert_eq!(all["rows"].as_array().unwrap().len(), 1);
        assert_eq!(
            all["chart_scene"]["kind"],
            "published_seasonal_core_velocities"
        );
        assert_eq!(all["chart_scene"]["records"].as_array().unwrap().len(), 6);
        assert!(all["map_scene"].is_null());
        let threshold = store.execute(br#"{"collection":"current_core_velocity_estimates","filters":[{"field":"estimate_kind","op":"eq","value":"reported_greater_than"}]}"#);
        assert_eq!(threshold["total"], 1);
        assert_eq!(threshold["rows"][0]["lower_threshold_m_s"], 0.3);
        assert!(threshold["rows"][0]["value_m_s"].is_null());
        assert!(threshold["rows"][0]["interval_m_s"].is_null());
        let empty = store.execute(br#"{"collection":"current_core_velocity_estimates","filters":[{"field":"current_id","op":"eq","value":"agulhas"}]}"#);
        assert_eq!(empty["total"], 0);
        assert!(empty["chart_scene"].is_null());
    }

    #[test]
    fn reject_borrowed_owner_invented_precision_and_source_rebinding() {
        assert!(validate(&candidate()).is_ok());
        for (key, value) in [
            ("current_id", json!("agulhas")),
            ("value_m_s", json!(0.3)),
            ("calendar_months", json!([3, 4, 5])),
            ("confidence_interval", json!([0.2, 0.4])),
            ("geometry", json!({"type":"Point","coordinates":[-23,0]})),
        ] {
            let mut changed = candidate();
            changed.collections.get_mut(COLLECTION).unwrap()[5][key] = value;
            assert!(validate(&changed).is_err(), "{key}");
        }
        let mut changed = candidate();
        changed.manifest["input_sha256"][SOURCE] = json!("different");
        assert!(validate(&changed).is_err());
        let mut changed = candidate();
        changed.collections.get_mut("objects").unwrap()[0][JOIN] = json!([]);
        assert!(validate(&changed).is_err());
        let scenes = by_current(&candidate());
        assert_eq!(scenes.as_object().unwrap().len(), 3);
        assert!(
            scenes
                .as_object()
                .unwrap()
                .values()
                .all(|v| v["records"].as_array().unwrap().len() == 2)
        );
    }
}
