//! Regional pooled speed statistics retain distinct, overlapping time support.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};

const SOURCE: &str = "research/eacc-pemba-semba-2019-seasonal-speed-v1.json";
const RAW: &str = include_str!("../../../research/eacc-pemba-semba-2019-seasonal-speed-v1.json");
const COLLECTION: &str = "current_speed_statistics";
const OWNER: &str = "current:east-african-coastal";

fn pin() -> String {
    format!("{:x}", Sha256::digest(RAW.as_bytes()))
}

fn expected() -> Vec<Value> {
    let doc: Value = serde_json::from_str(RAW).unwrap();
    let mut rows = Vec::new();
    for (key, period) in [("records", "seasonal"), ("monthly_records", "monthly")] {
        for (index, original) in doc[key].as_array().unwrap().iter().enumerate() {
            let mut row = original.clone();
            let label = row["season"]
                .as_str()
                .map(str::to_owned)
                .unwrap_or_else(|| row["month"].to_string());
            let extra = json!({"entity_id":OWNER,"current_id":"east-african-coastal",
                "label":format!("Pemba Channel / {label}"),"region":"Pemba Channel",
                "statistic_period":period,"observation_support_group":"semba-2019-pemba-gdp-1986-2017",
                "overlapping_summary_groups":true,"quantity":"near_surface_speed_magnitude","unit":"m/s",
                "time_support":doc["method"]["window"],"fixed_depth_m":null,
                "source_file":SOURCE,"source_file_sha256":pin(),"source_pointer":format!("/{key}/{index}"),
                "source_doi":doc["source"]["doi"],"range_meaning":doc["admission"]["range_meaning"],
                "independent_drifter_count":null,"confidence_interval":null,"whole_current":false,
                "geometry":null,"source_conflicts":doc["source_conflicts"]});
            row.as_object_mut()
                .unwrap()
                .extend(extra.as_object().unwrap().clone());
            rows.push(row);
        }
    }
    rows
}

pub(crate) fn validate(bundle: &Bundle) -> Result<(), String> {
    let owners = bundle
        .collections
        .get("objects")
        .map(Vec::as_slice)
        .unwrap_or(&[]);
    let marker = &bundle.manifest["published_current_speed_statistics_v1"];
    if !bundle.collections.contains_key(COLLECTION)
        && bundle.manifest["input_sha256"][SOURCE].is_null()
        && marker.is_null()
        && owners.iter().all(|r| r["speed_statistic_ids"].is_null())
    {
        return Ok(());
    }
    let rows = expected();
    if bundle.manifest["input_sha256"][SOURCE] != pin()
        || marker["source_file"] != SOURCE
        || marker["source_file_sha256"] != pin()
        || marker["logical_parent_sha256"]
            != "9d35ca1c8cebee0f48e49dd66bb83321b506fa43260f1dd5db4b1e06102293da"
        || marker["records_added"] != rows.len()
        || marker["length_or_width_records_added"] != 0
        || bundle.collections.get(COLLECTION) != Some(&rows)
    {
        return Err("Published regional speed statistics or source binding differ".into());
    }
    if owners.iter().filter(|r| r["id"] == OWNER).count() != 1 {
        return Err("Published regional speed owner missing or duplicated".into());
    }
    for owner in owners {
        let ids: Vec<_> = rows
            .iter()
            .filter(|r| r["entity_id"] == owner["id"])
            .map(|r| r["id"].clone())
            .collect();
        if (!ids.is_empty() || !owner["speed_statistic_ids"].is_null())
            && owner["speed_statistic_ids"] != json!(ids)
        {
            return Err("Published regional speed owner join differs".into());
        }
    }
    Ok(())
}

pub(crate) fn by_current(bundle: &Bundle) -> Value {
    let mut output = json!({});
    let rows = bundle
        .collections
        .get(COLLECTION)
        .map(Vec::as_slice)
        .unwrap_or(&[]);
    let matches: Vec<_> = rows.iter().filter(|r| r["entity_id"] == OWNER).collect();
    if !matches.is_empty() {
        output["east-african-coastal"] = scene(&matches);
    }
    output
}

pub(crate) fn scene(matches: &[&Value]) -> Value {
    if matches.is_empty() {
        return Value::Null;
    }
    let doc: Value = serde_json::from_str(RAW).unwrap();
    json!({"kind":"published_current_speed_statistics","title":"Pemba Channel: published speed statistics",
        "scope":"Regional near-surface drifter speeds pooled across1986–2017. Monthly and seasonal summaries overlap the same328observations from45drifters. Not current dimensions, one observed year, or confidence intervals.",
        "records":matches,"source_file":SOURCE,"source_url":doc["source"]["url"],
        "source_conflicts":doc["source_conflicts"],"method":doc["method"],
        "monthly_figure":"figures/eacc-pemba-monthly-speed-v1.svg",
        "seasonal_figure":"figures/eacc-pemba-seasonal-speed-v1.svg"})
}

#[cfg(test)]
mod tests {
    use super::*;
    fn candidate() -> Bundle {
        let rows = expected();
        let ids: Vec<_> = rows.iter().map(|r| r["id"].clone()).collect();
        Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest: json!({"input_sha256":{(SOURCE):pin()},"published_current_speed_statistics_v1":{
                "source_file":SOURCE,"source_file_sha256":pin(),"records_added":15,"length_or_width_records_added":0,
                "logical_parent_sha256":"9d35ca1c8cebee0f48e49dd66bb83321b506fa43260f1dd5db4b1e06102293da"}}),
            collections: std::collections::BTreeMap::from([
                (
                    "objects".into(),
                    vec![json!({"id":OWNER,"speed_statistic_ids":ids})],
                ),
                (COLLECTION.into(), rows),
            ]),
        }
    }

    #[test]
    fn store_dispatch_returns_chart_without_inventing_map_geometry() {
        let bundle = candidate();
        let raw = json!({"schema":bundle.schema,"manifest":bundle.manifest,"collections":bundle.collections});
        let store = crate::Store::load(raw.to_string().as_bytes()).unwrap();
        let all = store.execute(br#"{"collection":"current_speed_statistics","limit":100}"#);
        assert_eq!(all["ok"], true);
        assert_eq!(all["total"], 15);
        assert_eq!(
            all["chart_scene"]["kind"],
            "published_current_speed_statistics"
        );
        assert_eq!(all["chart_scene"]["records"].as_array().unwrap().len(), 15);
        assert!(all["map_scene"].is_null());
        let page = store.execute(br#"{"collection":"current_speed_statistics","filters":[{"field":"statistic_period","op":"eq","value":"monthly"}],"sort":{"field":"month","direction":"asc"},"offset":1,"limit":2}"#);
        assert_eq!(page["total"], 12);
        assert_eq!(page["rows"].as_array().unwrap().len(), 2);
        assert_eq!(page["rows"][0]["month"], 2);
        assert_eq!(page["chart_scene"]["records"].as_array().unwrap().len(), 12);
        let empty = store.execute(br#"{"collection":"current_speed_statistics","filters":[{"field":"current_id","op":"eq","value":"agulhas"}]}"#);
        assert_eq!(empty["total"], 0);
        assert!(empty["chart_scene"].is_null());
    }

    #[test]
    fn reject_changed_statistics_source_and_owner_joins() {
        assert!(validate(&candidate()).is_ok());
        let mut changed = candidate();
        changed.collections.get_mut(COLLECTION).unwrap()[0]["median"] = json!(99);
        assert!(validate(&changed).is_err());
        let mut changed = candidate();
        changed.manifest["input_sha256"][SOURCE] = json!("different");
        assert!(validate(&changed).is_err());
        let mut changed = candidate();
        changed.collections.get_mut("objects").unwrap()[0]["speed_statistic_ids"] = json!([]);
        assert!(validate(&changed).is_err());
    }

    #[test]
    fn pooled_statistics_are_distinct_from_dimensions_and_independent_samples() {
        let rows = expected();
        assert_eq!(rows.len(), 15);
        for period in ["monthly", "seasonal"] {
            assert_eq!(
                rows.iter()
                    .filter(|r| r["statistic_period"] == period)
                    .map(|r| r["observation_count"].as_u64().unwrap())
                    .sum::<u64>(),
                328
            );
        }
        assert!(
            rows.iter()
                .all(|r| r["confidence_interval"].is_null() && r["geometry"].is_null())
        );
        let ne = rows.iter().find(|r| r["season"] == "NE").unwrap();
        assert_eq!(ne["minimum"], 0.05);
        let selected = scene(&[ne]);
        assert_eq!(selected["records"].as_array().unwrap().len(), 1);
        assert!(scene(&[]).is_null());
    }
}
