//! Shared, source-bound local measurements; unresolved cases are records too.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};

pub const COLLECTION: &str = "current_section_measurements";
const OWNER: &str = "current:red-sea-saline-overflow";
const PROVIDERS: [(&str, &str, &str, &str, &str); 2] = [
    (
        "research/redsox-winter-section3-component-spans.json",
        include_str!("../../../research/redsox-winter-section3-component-spans.json"),
        "layers",
        "RSX1",
        "plans/redsox-section3-width-protocol-v1.md",
    ),
    (
        "research/redsox-section3-repeat-surveys.json",
        include_str!("../../../research/redsox-section3-repeat-surveys.json"),
        "summer_layers",
        "RSX2",
        "plans/redsox-section3-repeat-survey-protocol-v1.md",
    ),
];
const EXTRA_PINS: [(&str, &[u8]); 2] = [
    (
        "plans/current-section-measurement-records-v1.md",
        include_bytes!("../../../plans/current-section-measurement-records-v1.md"),
    ),
    (
        "analysis/current_section_measurements.py",
        include_bytes!("../../../analysis/current_section_measurements.py"),
    ),
];

fn expected() -> Vec<Value> {
    let mut rows = Vec::new();
    for (path, raw, key, campaign, protocol) in PROVIDERS {
        let doc: Value = serde_json::from_str(raw).unwrap();
        let pin = format!("{:x}", Sha256::digest(raw.as_bytes()));
        for (li, layer) in doc[key].as_array().unwrap().iter().enumerate() {
            let low = layer["height_layer_m"][0].as_i64().unwrap();
            let high = layer["height_layer_m"][1].as_i64().unwrap();
            let times: Vec<_> = layer["profiles"]
                .as_array()
                .unwrap()
                .iter()
                .map(|p| p["time_utc"].as_str().unwrap())
                .collect();
            for (ci, case) in layer["cases"].as_array().unwrap().iter().enumerate() {
                let fraction = (case["fraction"].as_f64().unwrap() * 100.).round() as i64;
                let offset =
                    (case["uniform_component_offset_m_s"].as_f64().unwrap() * 1000.).round() as i64;
                let branch = case["branch"].as_str().unwrap();
                rows.push(json!({
                    "id":format!("section-measurement:redsox-section3:{}:{branch}:{low}-{high}:f{fraction}:dq{offset}",campaign.to_ascii_lowercase()),
                    "label":format!("Red Sea Section 3 / {campaign} / {branch} / {low}-{high} m / f{fraction} / dq{offset} mm/s"),
                    "current_id":"red-sea-saline-overflow","entity_id":OWNER,"campaign":campaign,"branch":branch,
                    "observation_start_utc":times.iter().min().unwrap(),"observation_end_utc":times.iter().max().unwrap(),
                    "height_low_m":low,"height_high_m":high,"metric":"local_section_normal_component_span",
                    "component_span_km":case["span_km"],"boundary_fraction":case["fraction"],
                    "normal_component_velocity_offset_m_s":case["uniform_component_offset_m_s"],
                    "status":case["status"],"saline_outflow_screen":case["saline_outflow_screen"],
                    "peak_station":case["peak_station"],"is_primary_convention":low==20 && high==60 && fraction==50 && offset==0,
                    "source_file":path,"source_file_sha256":pin,"source_pointer":format!("/{key}/{li}/cases/{ci}"),
                    "protocol_file":protocol,"source_case":case,
                    "new_width_record_admitted":false,"rank_eligible":false,"current_association_verified":false,
                    "whole_current_width_km":null,"annual_width_range_km":null,"tides_removed":false
                }));
            }
        }
    }
    rows
}

pub(crate) fn validate(bundle: &crate::Bundle) -> Result<(), String> {
    let owners = bundle
        .collections
        .get("objects")
        .map(Vec::as_slice)
        .unwrap_or(&[]);
    let present = bundle.collections.contains_key(COLLECTION)
        || owners.iter().any(|o| o["id"] == OWNER)
        || PROVIDERS
            .iter()
            .any(|(path, _, _, _, _)| bundle.manifest["input_sha256"].get(*path).is_some());
    if !present {
        return Ok(());
    }
    for (path, raw, _, _, _) in PROVIDERS {
        if bundle.manifest["input_sha256"][path] != format!("{:x}", Sha256::digest(raw.as_bytes()))
        {
            return Err("Current section source binding changed".into());
        }
    }
    for (path, raw) in EXTRA_PINS {
        if bundle.manifest["input_sha256"][path] != format!("{:x}", Sha256::digest(raw)) {
            return Err("Current section record adapter or schema changed".into());
        }
    }
    let rows = bundle
        .collections
        .get(COLLECTION)
        .ok_or("Missing current section measurements")?;
    if *rows != expected() {
        return Err("Current section measurements edited, missing, duplicated or promoted".into());
    }
    let owner = owners
        .iter()
        .find(|o| o["id"] == OWNER)
        .ok_or("Missing current section measurement owner")?;
    if owner["current_section_measurement_ids"]
        != json!(rows.iter().map(|r| r["id"].clone()).collect::<Vec<_>>())
    {
        return Err("Current section measurement owner binding changed".into());
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> crate::Bundle {
        let rows = expected();
        let mut pins = json!({});
        for (path, raw, _, _, _) in PROVIDERS {
            pins[path] = json!(format!("{:x}", Sha256::digest(raw.as_bytes())));
        }
        for (path, raw) in EXTRA_PINS {
            pins[path] = json!(format!("{:x}", Sha256::digest(raw)));
        }
        let ids = rows.iter().map(|r| r["id"].clone()).collect::<Vec<_>>();
        crate::Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest: json!({"input_sha256":pins}),
            collections: std::collections::BTreeMap::from([
                (COLLECTION.into(), rows),
                (
                    "objects".into(),
                    vec![json!({"id":OWNER,"current_section_measurement_ids":ids})],
                ),
            ]),
        }
    }
    #[test]
    fn all_cases_and_conditional_scopes_survive() {
        let b = fixture();
        assert!(validate(&b).is_ok());
        let rows = &b.collections[COLLECTION];
        assert_eq!(rows.len(), 60);
        assert_eq!(
            rows.iter()
                .filter(|r| !r["component_span_km"].is_null())
                .count(),
            14
        );
        assert_eq!(
            rows.iter()
                .filter(|r| r["is_primary_convention"] == true)
                .count(),
            4
        );
        assert_eq!(rows.iter().filter(|r|!r["component_span_km"].is_null() && r["saline_outflow_screen"]==false).count(),4);
        assert!(rows.iter().all(|r| r["annual_width_range_km"].is_null()
            && r["whole_current_width_km"].is_null()
            && r["rank_eligible"] == false));
    }
    #[test]
    fn edits_missing_cases_and_orphaned_rows_reject() {
        for field in [
            "component_span_km",
            "rank_eligible",
            "boundary_fraction",
            "source_pointer",
            "source_case",
        ] {
            let mut b = fixture();
            b.collections.get_mut(COLLECTION).unwrap()[0][field] = json!(123);
            assert!(validate(&b).is_err(), "{field}");
        }
        let mut b = fixture();
        b.collections.get_mut(COLLECTION).unwrap().pop();
        assert!(validate(&b).is_err());
        let mut b = fixture();
        let duplicate = b.collections[COLLECTION][0].clone();
        b.collections.get_mut(COLLECTION).unwrap().push(duplicate);
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections.get_mut("objects").unwrap().clear();
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections.remove(COLLECTION);
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.manifest = json!({});
        assert!(validate(&b).is_err());
    }
}
