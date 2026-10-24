//! A reported regional campaign span; no annual range or geographic envelope.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::BTreeSet;

pub const FILE: &str = "research/davidson-wallace-2008-width-admission-v1.json";
pub const RAW: &str =
    include_str!("../../../research/davidson-wallace-2008-width-admission-v1.json");
const VERSION_KEY: &str = "davidson_reported_width_version";
const VERSION: &str = "wallace-line67-v1";
const ENTITY: &str = "current:davidson";
const WIDTH: &str = "davidson-wallace-2008-line67-27-59m-reported-span";
const OLD_WIDTH: &str = "davidson-historical-winter-width";
const CLAIM: &str = "claim:width:davidson-wallace-2008-line67-27-59m-reported-span";
const ADMISSION: &str = "current_measurement_admission:davidson:wallace-2008-line67";

fn document() -> Value {
    serde_json::from_str(RAW).expect("compiled Davidson admission contract")
}
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
pub fn active(bundle: &Bundle) -> bool {
    bundle.manifest.get(VERSION_KEY).is_some()
        || bundle.collections.values().flatten().any(|row| {
            row["id"] == WIDTH
                || row["id"] == CLAIM
                || row["id"] == ADMISSION
                || row["id"] == ENTITY
                    && row["width_ids"]
                        .as_array()
                        .is_some_and(|ids| ids.contains(&json!(WIDTH)))
        })
}
pub fn widths(bundle: &Bundle) -> Vec<Value> {
    if active(bundle) {
        vec![document()["width_record"].clone()]
    } else {
        vec![]
    }
}
fn exact(bundle: &Bundle, collection: &str, expected: &Value) -> Result<(), String> {
    let rows: Vec<_> = bundle
        .collections
        .get(collection)
        .into_iter()
        .flatten()
        .filter(|row| row["id"] == expected["id"])
        .collect();
    if rows != vec![expected] {
        return Err(format!(
            "Changed Davidson {collection} record: {}",
            expected["id"]
        ));
    }
    Ok(())
}
pub fn validate(bundle: &Bundle) -> Result<(), String> {
    if !active(bundle) {
        return Ok(());
    }
    if bundle.manifest[VERSION_KEY] != VERSION || bundle.manifest["input_sha256"][FILE] != pin(RAW)
    {
        return Err("Missing or changed Davidson admission version/contract".into());
    }
    let doc = document();
    if doc["manifest_fields"][VERSION_KEY] != VERSION {
        return Err("Compiled Davidson contract has a different manifest edition".into());
    }
    let width = &doc["width_record"];
    if width["source_reported_value"] != 35
        || width["source_unit_label"] != "NM"
        || width["normalized_width_km_decimal"] != "64.82"
        || width["approximate_width_km"] != 65
        || width["conversion_factor_m_per_nautical_mile"] != 1852
        || width["depth_average_interval_m"] != json!([27, 59])
        || width["observation_window"] != json!(["2008-01-23", "2008-01-30"])
        || width["source_evidence_kind"] != "primary_course_cruise_report"
        || doc["claim"]["value"] != 65
        || doc["claim"]["unit"] != "km"
        || !doc["claim"]["source_publication_year"].is_null()
        || !doc["claim"]["observation_time"].is_null()
    {
        return Err("Changed compiled Davidson source support".into());
    }
    let paper = doc["source_records"]
        .as_array()
        .unwrap()
        .iter()
        .find(|source| source["id"] == width["source_id"])
        .ok_or("Missing compiled Davidson primary report")?;
    if paper["kind"] != "report"
        || paper["peer_review_verified"] != false
        || !paper["publication_date"].is_null()
        || !paper["publication_year"].is_null()
    {
        return Err(
            "Course report cannot acquire peer review or an inferred publication date".into(),
        );
    }
    for key in [
        "width_range_km",
        "annual_width_range_km",
        "whole_current_width_km",
        "uncertainty_km",
        "exact_occupation_date",
        "source_publication_year",
        "geographic_current_edges",
        "section_geometry",
        "numeric_velocity_cutoff",
        "calendar_months",
        "fixed_layer_bounds_m",
        "area_km2",
    ] {
        if !width[key].is_null() {
            return Err(format!("Unspecified Davidson support promoted: {key}"));
        }
    }
    for key in [
        "peer_review_verified",
        "transect_normal_to_flow_verified",
        "seasonal_playback_eligible",
        "geographic_width_bar_eligible",
        "width_rank_eligible",
        "independent_width_samples_admitted",
        "physical_current_envelope_admitted",
        "historical_release_admitted",
    ] {
        if width[key] != false {
            return Err(format!("Unadmitted Davidson physical coverage: {key}"));
        }
    }
    for (path, sha) in doc["input_sha256"]
        .as_object()
        .ok_or("Missing Davidson input pins")?
    {
        if bundle.manifest["input_sha256"][path] != *sha {
            return Err(format!("Changed Davidson dependency: {path}"));
        }
    }
    for source in doc["source_records"].as_array().unwrap() {
        exact(bundle, "sources", source)?;
    }
    for (collection, key) in [
        ("widths", "width_record"),
        ("claims", "claim"),
        ("current_measurement_admissions", "admission"),
    ] {
        exact(bundle, collection, &doc[key])?;
    }
    exact(bundle, "entities", &doc["accepted_entity"])?;
    let owners: Vec<_> = bundle
        .collections
        .get("objects")
        .into_iter()
        .flatten()
        .filter(|row| row["id"] == ENTITY)
        .collect();
    if owners.len() != 1 {
        return Err("Missing or duplicate Davidson owner".into());
    }
    let owner = owners[0];
    if owner["type"] != "named_current"
        || owner["width_ids"] != json!([OLD_WIDTH, WIDTH])
        || !owner["latest_observation_date"].is_null()
    {
        return Err("Changed Davidson width ownership or fabricated exact observation date".into());
    }
    let mut actual_ids: Vec<_> = bundle
        .collections
        .get("widths")
        .into_iter()
        .flatten()
        .filter(|row| row["current_id"] == "davidson")
        .map(|row| row["id"].as_str().unwrap_or("").to_owned())
        .collect();
    actual_ids.sort();
    let mut expected_ids = vec![OLD_WIDTH.to_owned(), WIDTH.to_owned()];
    expected_ids.sort();
    if actual_ids != expected_ids {
        return Err("Changed prior or duplicate Davidson width".into());
    }
    for (key, expected) in [
        ("scoped_width", 2),
        ("observed_velocity", 0),
        ("radius_evidence", 0),
        ("reported_length", 0),
        ("geometry", 0),
        ("reference_route", 1),
        ("time_samples", 1),
        ("width_samples", 0),
        ("dated_diagnostics", 0),
        ("passage_transport", 0),
    ] {
        let actual = &owner["capabilities"][key];
        if !(actual == &json!(expected) || expected == 0 && actual.is_null()) {
            return Err(format!(
                "Davidson admission changed prior physical coverage: {key}"
            ));
        }
    }
    if owner["map_features"].as_array().map(Vec::len) != Some(2) {
        return Err("Davidson scalar evidence added or erased map features".into());
    }
    if bundle
        .collections
        .get("width_samples")
        .into_iter()
        .flatten()
        .any(|row| row["current_id"] == "davidson" || row["entity_id"] == ENTITY)
    {
        return Err("Reported Davidson width cannot add raw width samples".into());
    }
    let sources = owner["source_ids"]
        .as_array()
        .ok_or("Missing Davidson source references")?;
    let mut seen = BTreeSet::new();
    for value in sources {
        let id = value.as_str().ok_or("Invalid Davidson source reference")?;
        if !seen.insert(id) {
            return Err("Duplicate Davidson source reference".into());
        }
        let count = bundle
            .collections
            .get("sources")
            .into_iter()
            .flatten()
            .filter(|row| row["id"] == id)
            .count();
        if count != 1 {
            return Err("Unregistered or duplicate Davidson provenance".into());
        }
    }
    if owner["linked_source_count"] != json!(seen.len())
        || !doc["source_records"]
            .as_array()
            .unwrap()
            .iter()
            .all(|source| source["id"].as_str().is_some_and(|id| seen.contains(id)))
    {
        return Err("Incomplete Davidson source ownership".into());
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> Bundle {
        let d = document();
        let mut pins = d["input_sha256"].clone();
        pins[FILE] = json!(pin(RAW));
        let mut sources = d["source_records"].as_array().unwrap().clone();
        sources.push(json!({"id":d["accepted_entity"]["source_id"]}));
        serde_json::from_value(json!({"schema":"osw.query-bundle.v1",
            "manifest":{VERSION_KEY:VERSION,"input_sha256":pins},
            "collections":{"entities":[d["accepted_entity"]],"sources":sources,
                "widths":[{"id":OLD_WIDTH,"current_id":"davidson","approximate_width_km":64},d["width_record"]],
                "claims":[d["claim"]],"current_measurement_admissions":[d["admission"]],
                "objects":[{"id":ENTITY,"type":"named_current","width_ids":[OLD_WIDTH,WIDTH],"latest_observation_date":null,
                    "map_features":[{"existing":1},{"existing":2}],
                    "source_ids":[d["accepted_entity"]["source_id"],d["source_records"][0]["id"],
                        d["source_records"][1]["id"],d["source_records"][2]["id"]],"linked_source_count":4,
                    "capabilities":{"scoped_width":2,"reference_route":1,"time_samples":1}}]}})).unwrap()
    }
    #[test]
    fn accepts_separate_reported_span_without_new_physical_frames() {
        let b = fixture();
        validate(&b).unwrap();
        assert_eq!(widths(&b).len(), 1);
        assert_eq!(widths(&b)[0]["normalized_width_km_decimal"], "64.82");
        assert!(widths(&b)[0]["exact_occupation_date"].is_null());
    }
    #[test]
    fn rejects_neighbor_transfer_invented_ranges_dates_and_source_grade() {
        for (key, value) in [
            ("current_id", json!("california")),
            ("approximate_width_km", json!(64.82)),
            ("annual_width_range_km", json!([64, 65])),
            ("exact_occupation_date", json!("2008-01-30")),
            ("peer_review_verified", json!(true)),
            ("source_publication_year", json!(2008)),
            ("seasonal_playback_eligible", json!(true)),
            ("section_geometry", json!([0, 1])),
        ] {
            let mut b = fixture();
            b.collections.get_mut("widths").unwrap()[1][key] = value;
            assert!(validate(&b).is_err(), "{key}");
        }
        let mut b = fixture();
        b.collections.get_mut("sources").unwrap().pop();
        assert!(validate(&b).is_err());
        let mut b = fixture();
        let row = b.collections["widths"][1].clone();
        b.collections.get_mut("widths").unwrap().push(row);
        assert!(validate(&b).is_err());
    }
    #[test]
    fn cannot_strip_manifest_marker_or_promote_owner_physics() {
        let mut b = fixture();
        b.manifest.as_object_mut().unwrap().remove(VERSION_KEY);
        assert!(active(&b));
        assert!(validate(&b).is_err());
        for (key, value) in [
            ("width_samples", json!(1)),
            ("time_samples", json!(2)),
            ("reported_length", json!(1)),
        ] {
            let mut b = fixture();
            b.collections.get_mut("objects").unwrap()[0]["capabilities"][key] = value;
            assert!(validate(&b).is_err(), "{key}");
        }
    }
    #[test]
    fn indexing_prepared_contract_or_registering_sources_does_not_admit_width() {
        let d = document();
        let b: Bundle = serde_json::from_value(json!({"schema":"osw.query-bundle.v1",
            "manifest":{"input_sha256":{FILE:pin(RAW)}},"collections":{"sources":d["source_records"]}})).unwrap();
        assert!(!active(&b));
        assert!(widths(&b).is_empty());
        validate(&b).unwrap();
    }
}
