//! Complete regional graphic readings retain their source and nonphysical scope.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::sync::OnceLock;

const FILE: &str = "research/ke-qiu-regional-length-query-contract-v1.json";
const RAW: &str = include_str!("../../../research/ke-qiu-regional-length-query-contract-v1.json");
const REPORT_FILE: &str = "research/ke-qiu-regional-plot-pathlength-v4.json";
const REPORT_RAW: &str = include_str!("../../../research/ke-qiu-regional-plot-pathlength-v4.json");
const ENTITY: &str = "current:kuroshio-extension";

fn document() -> &'static Value {
    static DOC: OnceLock<Value> = OnceLock::new();
    DOC.get_or_init(|| serde_json::from_str(RAW).unwrap())
}
fn report() -> &'static Value {
    static DOC: OnceLock<Value> = OnceLock::new();
    DOC.get_or_init(|| serde_json::from_str(REPORT_RAW).unwrap())
}
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
fn records() -> Vec<(&'static str, Value)> {
    let d = document();
    vec![
        ("current_length_series", d.clone()),
        ("length_assessments", d["length_assessment"].clone()),
        ("measurements", d["measurement"].clone()),
        ("claims", d["claim"].clone()),
        ("sources", d["source_record"].clone()),
        ("sources", d["method_source"].clone()),
    ]
}
fn readings() -> Vec<Value> {
    let d = document();
    report()["samples"]
        .as_array()
        .unwrap()
        .iter()
        .enumerate()
        .map(|(index, source)| {
            let mut row = source.clone();
            row["series_id"] = d["id"].clone();
            row["graph_reading_order"] = json!(index);
            row["source_id"] = d["source_record"]["id"].clone();
            row["method_source_id"] = d["method_source"]["id"].clone();
            row
        })
        .collect()
}
fn present(bundle: &Bundle) -> bool {
    let d = document();
    bundle.manifest["ke_regional_plot_length_version"].is_string()
        || bundle.manifest["input_sha256"][FILE].is_string()
        || bundle.manifest["input_sha256"][REPORT_FILE].is_string()
        || bundle.collections.values().flatten().any(|row| {
            row["measurement_admission_file"] == FILE
                || row["series_id"] == d["id"]
                || row["regional_length_series_id"] == d["id"]
                || row["method_source_id"] == d["method_source"]["id"]
                || row["id"] == d["id"]
                || row["id"] == d["measurement"]["id"]
                || row["id"] == d["claim"]["id"]
                || row["id"] == d["source_record"]["id"]
                || row["id"] == d["method_source"]["id"]
                || row["id"]
                    .as_str()
                    .is_some_and(|id| id.starts_with("ke-qiu-plot-v4:"))
        })
}

pub(crate) fn verified_assessment_overlay(bundle: &Bundle) -> Result<Option<Value>, String> {
    if !present(bundle) {
        return Ok(None);
    }
    validate(bundle)?;
    Ok(Some(document()["length_assessment"].clone()))
}

pub fn validate(bundle: &Bundle) -> Result<(), String> {
    if !present(bundle) {
        return Ok(());
    }
    let d = document();
    let r = report();
    if bundle.manifest["ke_regional_plot_length_version"] != "4"
        || bundle.manifest["input_sha256"][FILE] != pin(RAW)
        || bundle.manifest["input_sha256"][REPORT_FILE] != pin(REPORT_RAW)
        || d["scientific_report_sha256"] != pin(REPORT_RAW)
    {
        return Err("Changed KE regional graphic edition/source".into());
    }
    for (path, hash) in d["input_sha256"].as_object().unwrap() {
        if bundle.manifest["input_sha256"][path] != *hash {
            return Err(format!("Changed KE regional graphic dependency: {path}"));
        }
    }
    let range = &r["plotted_graph_reading_range_km"];
    if d["entity_id"] != ENTITY
        || d["graph_reading_count"] != r["graph_reading_count"]
        || d["measurement"]["value"] != *range
        || d["claim"]["value"] != *range
        || d["length_assessment"]["regional_plotted_length_range_km"] != *range
        || d["length_assessment"]["rank_eligible"] != false
        || !d["length_assessment"]["published_length_km"].is_null()
        || !d["length_assessment"]["lower_bound_km"].is_null()
        || d["seasonal_playback_eligible"] != false
        || d["annual_extrema_eligible"] != false
    {
        return Err("KE graph readings promoted or source range changed".into());
    }
    for (name, expected) in records() {
        let actual: Vec<_> = bundle
            .collections
            .get(name)
            .into_iter()
            .flatten()
            .filter(|row| {
                row["id"] == expected["id"]
                    || (name == "current_length_series" && row["entity_id"] == ENTITY)
            })
            .collect();
        if actual != vec![&expected] {
            return Err(format!("Changed KE regional graphic {name}"));
        }
    }
    if bundle.collections["length_assessments"]
        .iter()
        .filter(|row| row["entity_id"] == ENTITY)
        .count()
        != 1
    {
        return Err("Ambiguous KE length assessment owner".into());
    }
    let expected = readings();
    let actual: Vec<_> = bundle
        .collections
        .get("current_length_readings")
        .into_iter()
        .flatten()
        .filter(|row| {
            row["entity_id"] == ENTITY
                || row["series_id"] == d["id"]
                || row["id"]
                    .as_str()
                    .is_some_and(|id| id.starts_with("ke-qiu-plot-v4:"))
        })
        .collect();
    if actual != expected.iter().collect::<Vec<_>>() {
        return Err("Changed, missing, reordered or duplicate KE graph readings".into());
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> Bundle {
        let d = document();
        let mut inputs = d["input_sha256"].clone();
        inputs[FILE] = json!(pin(RAW));
        let mut collections = std::collections::BTreeMap::new();
        for (name, row) in records() {
            collections
                .entry(name.into())
                .or_insert_with(Vec::new)
                .push(row);
        }
        collections.insert("current_length_readings".into(), readings());
        Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest: json!({"input_sha256":inputs,"ke_regional_plot_length_version":"4"}),
            collections,
        }
    }
    #[test]
    fn accepts_complete_graph_and_legacy_bundle_without_new_evidence() {
        validate(&fixture()).unwrap();
        let mut legacy = fixture();
        legacy.manifest = json!({});
        legacy.collections.clear();
        legacy.collections.insert(
            "length_assessments".into(),
            vec![json!({"entity_id":ENTITY,"evidence_status":"no_numeric_length"})],
        );
        validate(&legacy).unwrap();
    }
    #[test]
    fn rejects_changed_numeric_scope_owner_time_or_rank() {
        for (name, field, value) in [
            (
                "current_length_readings",
                "approximate_length_km",
                json!(9999),
            ),
            (
                "current_length_readings",
                "entity_id",
                json!("current:kuroshio"),
            ),
            (
                "current_length_readings",
                "exact_observation_time",
                json!("2000-01-01"),
            ),
            (
                "current_length_readings",
                "reading_kind",
                json!("direct_observation"),
            ),
            (
                "current_length_readings",
                "length_reading_allowance_km",
                json!(1),
            ),
            (
                "current_length_readings",
                "seasonal_playback_eligible",
                json!(true),
            ),
            ("length_assessments", "rank_eligible", json!(true)),
            ("measurements", "value", json!([1000, 5000])),
            ("claims", "source_id", json!("source:other")),
        ] {
            let mut b = fixture();
            b.collections.get_mut(name).unwrap()[0][field] = value;
            assert!(validate(&b).is_err(), "{name}/{field}");
        }
    }
    #[test]
    fn rejects_missing_dependencies_records_and_duplicate_or_reordered_readings() {
        let mut b = fixture();
        b.manifest = json!({});
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.manifest["input_sha256"][REPORT_FILE] = json!("changed");
        assert!(validate(&b).is_err());
        for name in [
            "current_length_series",
            "current_length_readings",
            "length_assessments",
            "measurements",
            "claims",
            "sources",
        ] {
            let mut b = fixture();
            b.collections.remove(name);
            assert!(validate(&b).is_err(), "{name}");
        }
        let mut b = fixture();
        b.collections
            .get_mut("current_length_readings")
            .unwrap()
            .swap(0, 1);
        assert!(validate(&b).is_err());
        let mut b = fixture();
        let row = b.collections["current_length_readings"][0].clone();
        b.collections
            .get_mut("current_length_readings")
            .unwrap()
            .push(row);
        assert!(validate(&b).is_err());
    }
    #[test]
    fn shared_historical_overlay_requires_all_readings_and_retains_other_currents() {
        let mut b = fixture();
        let previous = json!([{"entity_id":ENTITY,"evidence_status":"no_numeric_length"},
                              {"entity_id":"current:other","published_length_km":1234}]);
        let actual = crate::length_assessment_overlays::expected(&b, &previous).unwrap();
        assert_eq!(actual[0], document()["length_assessment"]);
        assert_eq!(actual[1], previous[1]);
        b.collections
            .get_mut("current_length_readings")
            .unwrap()
            .pop();
        assert!(crate::length_assessment_overlays::expected(&b, &previous).is_err());
    }
}
