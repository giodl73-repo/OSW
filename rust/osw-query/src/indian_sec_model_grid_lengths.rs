//! Complete regional model-grid evidence preserves failed cases and physical gaps.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
use std::sync::OnceLock;

pub(crate) const FILE: &str = "research/chen-indian-sec-ridge-length-query-contract-v1.json";
pub(crate) const RAW: &str =
    include_str!("../../../research/chen-indian-sec-ridge-length-query-contract-v1.json");
const REPORT: &str =
    include_str!("../../../research/chen-indian-sec-regional-ridge-lengths-v1.json");
const KEY: &str = "indian_sec_model_grid_lengths_v1";
pub(crate) const OWNER: &str = "current:indian-south-equatorial";
const SERIES: &str = "current_length_series";
const READINGS: &str = "current_length_readings";
const SENSITIVITIES: &str = "current_length_sensitivities";
const PREFIXES: [&str; 3] = [
    "model_core_series:indian-sec:chen-2022:",
    "model_core_length:indian-sec:chen-2022:",
    "model_core_sensitivity:indian-sec:chen-2022:",
];

fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
fn document() -> &'static Value {
    static DOC: OnceLock<Value> = OnceLock::new();
    DOC.get_or_init(|| {
        serde_json::from_str(RAW).expect("compiled Indian SEC regional model-length contract")
    })
}
fn marker() -> Value {
    json!({"schema":"osw.indian-sec-model-grid-length-runtime.v1","contract_file":FILE,
        "contract_sha256":pin(RAW),"parent_logical_sha256":document()["parent_logical_sha256"],
        "series_added":1,"readings_added":75,"sensitivities_added":120,"qualified_model_grid_lengths":8,
        "withheld_readings":67,"reported_lengths_added":0,"reference_routes_added":0,"widths_added":0,"physical_state_joins_added":0})
}
fn prefix(row: &Value) -> bool {
    row["id"]
        .as_str()
        .is_some_and(|id| PREFIXES.iter().any(|p| id.starts_with(p)))
}
fn owns(row: &Value, owner: &str) -> bool {
    row["entity_id"] == owner
        || row["family_entity_id"] == owner
        || owner
            .strip_prefix("current:")
            .is_some_and(|short| row["current_id"] == short)
}
fn normalized(value: &Value) -> String {
    value
        .as_str()
        .unwrap_or("")
        .chars()
        .filter(char::is_ascii_alphanumeric)
        .flat_map(char::to_lowercase)
        .collect()
}
fn decoded(value: &Value) -> String {
    let bytes = value.as_str().unwrap_or("").trim().as_bytes();
    let mut result = Vec::new();
    let mut index = 0;
    while index < bytes.len() {
        if bytes[index] == b'%' && index + 2 < bytes.len() {
            if let (Some(a), Some(b)) = (
                (bytes[index + 1] as char).to_digit(16),
                (bytes[index + 2] as char).to_digit(16),
            ) {
                result.push((a * 16 + b) as u8);
                index += 3;
                continue;
            }
        }
        result.push(bytes[index]);
        index += 1;
    }
    String::from_utf8_lossy(&result).to_lowercase()
}
fn url(value: &Value) -> String {
    let text = decoded(value);
    let text = text.split(['?', '#']).next().unwrap_or("");
    text.strip_prefix("https://")
        .or_else(|| text.strip_prefix("http://"))
        .unwrap_or(text)
        .trim_end_matches('/')
        .into()
}
fn doi(value: &Value) -> String {
    let text = decoded(value);
    let text = text.split(['?', '#']).next().unwrap_or("");
    for p in [
        "https://doi.org/",
        "http://doi.org/",
        "https://dx.doi.org/",
        "http://dx.doi.org/",
        "doi:",
    ] {
        if let Some(tail) = text.strip_prefix(p) {
            return tail.trim().trim_end_matches('/').into();
        }
    }
    if let Some((_, tail)) = text.split_once("/doi/") {
        return ["full/", "abs/", "epdf/", "pdf/"]
            .iter()
            .find_map(|p| tail.strip_prefix(*p))
            .unwrap_or(tail)
            .trim_end_matches('/')
            .into();
    }
    text.trim_end_matches('/').into()
}

// Use only after a complete checked() result. No unreviewed row is projected away.
pub(crate) fn identity_parent_row<'a>(
    collection: &str,
    row: &'a Value,
    enabled: bool,
) -> Option<&'a Value> {
    if !enabled {
        return Some(row);
    }
    let doc = document();
    if collection == "objects" && row["id"] == OWNER {
        return Some(&doc["prior_records"]["identities"][OWNER]["object"]);
    }
    if collection == "length_assessments" && row["entity_id"] == OWNER {
        return Some(&doc["prior_records"]["identities"][OWNER]["length_assessments"][0]);
    }
    let hidden = match collection {
        SERIES => row["id"] == doc["series_record"]["id"],
        READINGS => doc["reading_records"]
            .as_array()
            .unwrap()
            .iter()
            .any(|r| r["id"] == row["id"]),
        SENSITIVITIES => doc["sensitivity_records"]
            .as_array()
            .unwrap()
            .iter()
            .any(|r| r["id"] == row["id"]),
        _ => false,
    };
    if hidden { None } else { Some(row) }
}

fn checked(collections: &BTreeMap<String, Vec<Value>>, manifest: &Value) -> Result<bool, String> {
    let fail = || "Invalid Indian SEC regional model-grid length extension".to_owned();
    let doc = document();
    let rows = |name: &str| collections.get(name).map(Vec::as_slice).unwrap_or(&[]);
    let sources = doc["new_sources"].as_array().ok_or_else(fail)?;
    let present = !manifest[KEY].is_null()
        || !manifest["input_sha256"][FILE].is_null()
        || [SERIES, READINGS, SENSITIVITIES]
            .iter()
            .any(|name| rows(name).iter().any(prefix))
        || rows("sources")
            .iter()
            .any(|r| sources.iter().any(|s| r["id"] == s["id"]))
        || rows("objects").iter().any(|r| {
            r["regional_length_series_ids"]
                .as_array()
                .is_some_and(|a| a.contains(&doc["series_record"]["id"]))
        });
    if !present {
        return Ok(false);
    }
    if manifest[KEY] != marker()
        || manifest["input_sha256"][FILE] != pin(RAW)
        || doc["series_record"]["scientific_report_sha256"] != pin(REPORT)
    {
        return Err(fail());
    }
    for (path, digest) in doc["input_sha256"].as_object().ok_or_else(fail)? {
        if manifest["input_sha256"][path] != *digest {
            return Err(fail());
        }
    }
    let groups = [
        (SERIES, vec![&doc["series_record"]]),
        (
            READINGS,
            doc["reading_records"]
                .as_array()
                .ok_or_else(fail)?
                .iter()
                .collect(),
        ),
        (
            SENSITIVITIES,
            doc["sensitivity_records"]
                .as_array()
                .ok_or_else(fail)?
                .iter()
                .collect(),
        ),
    ];
    let mut locations = BTreeMap::new();
    for (name, expected) in &groups {
        if rows(name)
            .iter()
            .filter(|r| prefix(r) || owns(r, OWNER) || r["series_id"] == doc["series_record"]["id"])
            .collect::<Vec<_>>()
            != *expected
        {
            return Err(fail());
        }
        for row in expected {
            let id = row["id"].as_str().ok_or_else(fail)?;
            if locations.insert(id, *name).is_some() {
                return Err(fail());
            }
        }
    }
    for (name, records) in collections {
        for row in records {
            if prefix(row)
                && locations.get(row["id"].as_str().ok_or_else(fail)?).copied()
                    != Some(name.as_str())
            {
                return Err(fail());
            }
        }
    }
    let mut source_ids = BTreeSet::new();
    for actual in rows("sources") {
        let id = actual["id"].as_str().ok_or_else(fail)?;
        if id.is_empty() || !source_ids.insert(id) {
            return Err(fail());
        }
        for expected in sources {
            if actual["id"] == expected["id"] {
                if actual != expected {
                    return Err(fail());
                }
            } else {
                let expected_doi = doi(&expected["doi"]);
                if (!expected_doi.is_empty()
                    && (doi(&actual["doi"]) == expected_doi || doi(&actual["url"]) == expected_doi))
                    || (!url(&expected["url"]).is_empty()
                        && url(&actual["url"]) == url(&expected["url"]))
                    || (!normalized(&expected["title"]).is_empty()
                        && (normalized(&actual["title"]) == normalized(&expected["title"])
                            || normalized(&actual["label"]) == normalized(&expected["title"])))
                {
                    return Err(fail());
                }
            }
        }
    }
    for expected in sources {
        if rows("sources")
            .iter()
            .filter(|r| r["id"] == expected["id"])
            .collect::<Vec<_>>()
            != vec![expected]
        {
            return Err(fail());
        }
    }
    for (owner, prior) in doc["prior_records"]["identities"]
        .as_object()
        .ok_or_else(fail)?
    {
        let object = if owner == OWNER {
            &doc["final_owner"]
        } else {
            &prior["object"]
        };
        if rows("objects")
            .iter()
            .filter(|r| r["id"] == *owner)
            .collect::<Vec<_>>()
            != vec![object]
            || rows("entities")
                .iter()
                .filter(|r| r["id"] == *owner)
                .collect::<Vec<_>>()
                != vec![&prior["entity"]]
        {
            return Err(fail());
        }
        if owner == OWNER
            && rows("length_assessments")
                .iter()
                .filter(|r| r["entity_id"] == OWNER)
                .collect::<Vec<_>>()
                != vec![&doc["final_length_assessment"]]
        {
            return Err(fail());
        }
        for (name, actual) in collections {
            let expected = prior["linked_records"][name]
                .as_array()
                .map(|r| r.iter().collect::<Vec<_>>())
                .unwrap_or_default();
            if actual
                .iter()
                .filter_map(|r| identity_parent_row(name, r, true))
                .filter(|r| owns(r, owner))
                .collect::<Vec<_>>()
                != expected
            {
                return Err(fail());
            }
        }
        for (name, expected) in prior["linked_records"].as_object().ok_or_else(fail)? {
            if !collections.contains_key(name) && expected.as_array().is_some_and(|a| !a.is_empty())
            {
                return Err(fail());
            }
        }
        for source in prior["owner_sources"].as_array().ok_or_else(fail)? {
            if rows("sources")
                .iter()
                .filter(|r| r["id"] == source["id"])
                .collect::<Vec<_>>()
                != vec![source]
            {
                return Err(fail());
            }
        }
    }
    Ok(true)
}
pub(crate) fn validate(bundle: &Bundle) -> Result<(), String> {
    checked(&bundle.collections, &bundle.manifest).map(|_| ())
}
pub(crate) fn identity_overlay(bundle: &Bundle) -> Result<bool, String> {
    checked(&bundle.collections, &bundle.manifest)
}
pub(crate) fn additional_source_count(
    collections: &BTreeMap<String, Vec<Value>>,
    manifest: &Value,
) -> Result<usize, String> {
    Ok(if checked(collections, manifest)? {
        3
    } else {
        0
    })
}
pub(crate) fn verified_assessment_overlay(bundle: &Bundle) -> Result<Option<Value>, String> {
    Ok(if identity_overlay(bundle)? {
        Some(document()["final_length_assessment"].clone())
    } else {
        None
    })
}
pub(crate) fn query_scene(
    collection: &str,
    selected: &[&Value],
    bundle: &Bundle,
) -> Result<Value, String> {
    if ![SERIES, READINGS, SENSITIVITIES].contains(&collection) || selected.is_empty() {
        return Ok(Value::Null);
    }
    if !selected.iter().all(|r| {
        r["id"] == document()["series_record"]["id"]
            || r["series_id"] == document()["series_record"]["id"]
    }) {
        return Ok(Value::Null);
    }
    if !identity_overlay(bundle)? {
        return Err("Regional model scene lacks complete validated evidence".into());
    }
    Ok(
        json!({"kind":"regional_model_core_length_series","entity_id":OWNER,"title":"Indian SEC: regional model-grid lengths",
        "series":document()["series_record"],"selected_collection":collection,"selected_count":selected.len(),"selected_records":selected,
        "scope":document()["series_record"]["scope"],"figure":"figures/chen-indian-sec-regional-ridge-lengths-v1.svg"}),
    )
}
pub(crate) fn object_projection(
    bundle: &Bundle,
    id: &str,
    mut value: Value,
) -> Result<Value, String> {
    if id != OWNER || !identity_overlay(bundle)? {
        return Ok(value);
    }
    value["regional_model_length_scene"] = json!({"kind":"regional_model_core_length_series","entity_id":OWNER,
        "title":"Indian SEC: regional model-grid lengths","series":document()["series_record"],
        "readings":document()["reading_records"],"sensitivities":document()["sensitivity_records"],
        "scope":document()["series_record"]["scope"],"figure":"figures/chen-indian-sec-regional-ridge-lengths-v1.svg"});
    Ok(value)
}
pub(crate) fn dashboard_row(bundle: &Bundle, row: &Value) -> Result<Value, String> {
    if row["id"] != OWNER || !identity_overlay(bundle)? {
        return Ok(row.clone());
    }
    if row != &document()["prior_records"]["identities"][OWNER]["object"]
        && row != &document()["final_owner"]
    {
        return Err("Changed preceding Indian SEC dashboard row".into());
    }
    Ok(document()["final_owner"].clone())
}
pub(crate) fn dashboard_document(bundle: &Bundle, mut value: Value) -> Result<Value, String> {
    if !identity_overlay(bundle)? {
        return Ok(value);
    }
    let fail = || "Invalid preceding regional-model dashboard projection".to_owned();
    let previous = value["snapshot_fingerprint"]
        .as_str()
        .ok_or_else(fail)?
        .to_owned();
    let entries = value["entries"].as_array_mut().ok_or_else(fail)?;
    if entries.iter().filter(|r| r["id"] == OWNER).count() != 1 {
        return Err(fail());
    }
    for row in entries.iter_mut().filter(|r| r["id"] == OWNER) {
        *row = dashboard_row(bundle, row)?;
    }
    value["snapshot_fingerprint"] = json!(pin(&format!(
        "osw.indian-sec-model-grid-lengths.v1\n{previous}\n{}\n",
        pin(RAW)
    )));
    value["indian_sec_model_grid_length_projection_v1"] = json!({"contract_file":FILE,"contract_sha256":pin(RAW),
        "regional_series_added":1,"qualified_grid_lengths":8,"withheld_readings":67,"reported_lengths_added":0});
    Ok(value)
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> Bundle {
        let doc = document();
        let mut b = Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest: json!({"input_sha256":{}}),
            collections: BTreeMap::new(),
        };
        for owner in ["current:south-equatorial", OWNER] {
            let prior = &doc["prior_records"]["identities"][owner];
            for (name, key) in [("objects", "object"), ("entities", "entity")] {
                let row = if name == "objects" && owner == OWNER {
                    &doc["final_owner"]
                } else {
                    &prior[key]
                };
                b.collections
                    .entry(name.into())
                    .or_default()
                    .push(row.clone());
            }
            for (name, records) in prior["linked_records"].as_object().unwrap() {
                for row in records.as_array().unwrap() {
                    let row = if name == "length_assessments" && row["entity_id"] == OWNER {
                        &doc["final_length_assessment"]
                    } else {
                        row
                    };
                    let output = b.collections.entry(name.clone()).or_default();
                    if !output.iter().any(|r| r["id"] == row["id"]) {
                        output.push(row.clone());
                    }
                }
            }
            for row in prior["owner_sources"].as_array().unwrap() {
                let output = b.collections.entry("sources".into()).or_default();
                if !output.iter().any(|r| r["id"] == row["id"]) {
                    output.push(row.clone());
                }
            }
        }
        b.collections
            .entry("sources".into())
            .or_default()
            .extend(doc["new_sources"].as_array().unwrap().clone());
        b.collections
            .insert(SERIES.into(), vec![doc["series_record"].clone()]);
        b.collections.insert(
            READINGS.into(),
            doc["reading_records"].as_array().unwrap().clone(),
        );
        b.collections.insert(
            SENSITIVITIES.into(),
            doc["sensitivity_records"].as_array().unwrap().clone(),
        );
        for (p, h) in doc["input_sha256"].as_object().unwrap() {
            b.manifest["input_sha256"][p] = h.clone();
        }
        b.manifest["input_sha256"][FILE] = json!(pin(RAW));
        b.manifest[KEY] = marker();
        b
    }
    #[test]
    fn complete_series_retains_values_failures_and_scope() {
        let b = fixture();
        validate(&b).unwrap();
        assert_eq!(
            additional_source_count(&b.collections, &b.manifest).unwrap(),
            3
        );
        assert_eq!(b.collections[READINGS].len(), 75);
        assert_eq!(b.collections[SENSITIVITIES].len(), 120);
        assert_eq!(
            b.collections[READINGS]
                .iter()
                .filter(|r| !r["length_km"].is_null())
                .count(),
            8
        );
        let assessment = verified_assessment_overlay(&b).unwrap().unwrap();
        assert!(assessment["published_length_km"].is_null());
        assert_eq!(assessment["whole_current_evidence_status"], "unmeasured");
    }
    #[test]
    fn incomplete_or_reassigned_data_and_orphan_receipts_fail() {
        for change in [
            "missing_failed",
            "duplicate",
            "owner",
            "uncertainty",
            "scenario",
            "marker",
            "source",
            "family",
        ] {
            let mut b = fixture();
            match change {
                "missing_failed" => {
                    b.collections.get_mut(READINGS).unwrap().remove(0);
                }
                "duplicate" => {
                    let row = b.collections[READINGS][0].clone();
                    b.collections.get_mut(READINGS).unwrap().push(row);
                }
                "owner" => {
                    b.collections.get_mut(READINGS).unwrap()[0]["entity_id"] =
                        json!("current:south-equatorial")
                }
                "uncertainty" => {
                    b.collections.get_mut(SENSITIVITIES).unwrap()[0]["is_physical_uncertainty"] =
                        json!(true)
                }
                "scenario" => {
                    b.collections.get_mut(SENSITIVITIES).unwrap().pop();
                }
                "marker" => {
                    b.manifest.as_object_mut().unwrap().remove(KEY);
                }
                "source" => {
                    b.collections.get_mut("sources").unwrap().pop();
                }
                _ => {
                    b.collections
                        .get_mut("objects")
                        .unwrap()
                        .iter_mut()
                        .find(|r| r["id"] == "current:south-equatorial")
                        .unwrap()["published_length_km"] = json!(4700)
                }
            }
            assert!(validate(&b).is_err(), "{change}");
        }
    }
    #[test]
    fn source_aliases_and_candidate_prefixes_cannot_bypass_checks() {
        for row in [
            json!({"id":"alias","doi":"https://doi.org/10.1029/2022JC018969"}),
            json!({"id":"alias","url":"http://data.scsio.ac.cn/metaData-detail/1567926827663917056?lang=ENG"}),
        ] {
            let mut b = fixture();
            b.collections.get_mut("sources").unwrap().push(row);
            assert!(validate(&b).is_err());
        }
        let mut b = fixture();
        b.collections
            .entry("widths".into())
            .or_default()
            .push(json!({"id":"model_core_length:indian-sec:chen-2022:rogue"}));
        assert!(validate(&b).is_err());
    }
    #[test]
    fn historical_projection_hides_only_complete_known_extension() {
        let b = fixture();
        let enabled = identity_overlay(&b).unwrap();
        let row = &b.collections[READINGS][0];
        assert!(identity_parent_row(READINGS, row, enabled).is_none());
        let unknown = json!({"id":"unreviewed","entity_id":OWNER});
        assert_eq!(
            identity_parent_row(READINGS, &unknown, enabled),
            Some(&unknown)
        );
        let object = b.collections["objects"]
            .iter()
            .find(|r| r["id"] == OWNER)
            .unwrap();
        assert_eq!(
            identity_parent_row("objects", object, enabled),
            Some(&document()["prior_records"]["identities"][OWNER]["object"])
        );
    }
    #[test]
    fn query_scene_preserves_selection_and_refuses_mixed_owner_chart() {
        let b = fixture();
        let rows = b.collections[READINGS]
            .iter()
            .filter(|r| r["kernel_cells"] == 3 && !r["length_km"].is_null())
            .collect::<Vec<_>>();
        let scene = query_scene(READINGS, &rows, &b).unwrap();
        assert_eq!(scene["selected_count"], 3);
        assert_eq!(scene["selected_records"], json!(rows));
        assert!(query_scene(READINGS, &[], &b).unwrap().is_null());
        let other = json!({"id":"other","entity_id":"current:other"});
        assert!(query_scene(READINGS, &[&other], &b).unwrap().is_null());
    }
    #[test]
    fn owner_and_dashboard_keep_whole_current_and_observation_gaps() {
        let b = fixture();
        let old = &document()["prior_records"]["identities"][OWNER]["object"];
        let other = json!({"id":"other","keep":true});
        let doc=dashboard_document(&b,json!({"entries":[old,other],"snapshot_fingerprint":"previous","counts":{"named_current":111}})).unwrap();
        assert!(doc["entries"][0]["published_length_km"].is_null());
        assert!(doc["entries"][0]["latest_observation_date"].is_null());
        assert_eq!(doc["entries"][0]["capabilities"]["reported_length"], 0);
        assert_eq!(doc["entries"][0]["capabilities"]["reference_route"], 0);
        assert_eq!(doc["counts"]["named_current"], 111);
        assert_eq!(doc["entries"][1], other);
        assert!(
            !object_projection(&b, OWNER, json!({})).unwrap()["regional_model_length_scene"]
                .is_null()
        );
        assert_eq!(
            object_projection(&b, "current:south-equatorial", json!({"keep":true})).unwrap(),
            json!({"keep":true})
        );
    }
}
