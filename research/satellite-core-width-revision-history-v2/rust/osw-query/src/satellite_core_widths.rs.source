//! Two reported satellite means remain distinct from temporal variability.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::BTreeSet;

const SOURCE: &str = "research/agulhas-krug-2012-core-widths-source-facts-v1.json";
const RAW: &str =
    include_str!("../../../research/agulhas-krug-2012-core-widths-source-facts-v1.json");
const KEY: &str = "published_satellite_core_widths_v1";
const OWNER: &str = "current:agulhas";
const PARENT: &str = "c27c5c8319ab59fa6069274df1b7d19c87cf5a2aea8a7a04ba808a1636b9e212";
const FIGURE: &str = "figures/agulhas-krug-2012-core-widths-v1.svg";
const IDS: [&str; 2] = [
    "agulhas-krug-2012-altimetry-gaussian-core-mean-width",
    "agulhas-krug-2012-sst-core-mean-width",
];
const OLD_IDS: [&str; 2] = [
    "agulhas-act-eulerian-mean-section-width",
    "agulhas-vinayachandran-2021-typical-core-description",
];

fn pin() -> String {
    format!("{:x}", Sha256::digest(RAW.as_bytes()))
}
fn document() -> Value {
    serde_json::from_str(RAW).unwrap()
}

fn expected() -> Vec<Value> {
    let doc = document();
    doc["records"].as_array().unwrap().iter().enumerate().map(|(index, original)| {
        let mut row = original.clone();
        let extra = json!({"name":"Agulhas Current","entity_id":OWNER,"status":"editorial_source_extraction_not_canonical",
            "measurement_type":"published_satellite_core_mean_width","width_metric":if index==0 {"satellite_gaussian_core_mean"}else{"satellite_thermal_core_mean"},
            "width_metric_label":original["label"],"approximate_width_km":original["reported_mean_width_km"],"width_range_km":null,
            "range_interpretation":"Separate method-specific means; not seasonal limits, confidence intervals or width errors.",
            "geographic_scope":doc["regional_support"]["section"],"section_geometry":null,
            "section_orientation":doc["regional_support"]["orientation"],"layer":"Satellite-derived surface core; no fixed measurement depth assigned.",
            "time_convention":original["source_time_description"],"boundary_rule":original["operator"],
            "source_url":doc["source"]["url"],"source_citation":"Krug and Tournadre (2012), doi:10.1029/2012GL052335",
            "source_evidence_kind":"published_satellite_regional_mean_core",
            "extraction_method":"Transcribed author-reported mean; no source-curve digitization or current-field processing.",
            "source_file":SOURCE,"source_file_sha256":pin(),"source_pointer":format!("/records/{index}"),
            "phase_label":format!("{} / published mean",original["label"].as_str().unwrap()),"phase_kind":"satellite_core_mean_width",
            "observed_period":null,"fixed_layer_bounds_m":null,"boundary_sides":"source_defined_paired_core_edges",
            "whole_current_representative":false,"width_rank_eligible":false,"full_width_inference_eligible":false,
            "annual_extrema_eligible":false,"seasonal_playback_eligible":false,"is_confidence_interval":false,
            "confidence_interval_km":null,"geometry":null,
            "satellite_core_context":{"regional_support":doc["regional_support"],"source_ambiguities":doc["source_ambiguities"],
                "seasonality_finding":doc["seasonality_finding"],"excluded_context":doc["excluded_context"],"full_context_figure":FIGURE}});
        row.as_object_mut().unwrap().extend(extra.as_object().unwrap().clone());
        row
    }).collect()
}

pub(crate) fn active(bundle: &Bundle) -> bool {
    !bundle.manifest[KEY].is_null()
        || !bundle.manifest["published_satellite_core_width_index_v1"].is_null()
        || !bundle.manifest["input_sha256"][SOURCE].is_null()
        || bundle
            .collections
            .get("widths")
            .into_iter()
            .flatten()
            .any(|r| {
                r.get("satellite_core_context").is_some()
                    || r["id"]
                        .as_str()
                        .is_some_and(|s| s.starts_with("agulhas-krug-2012-"))
            })
        || bundle
            .collections
            .get("objects")
            .into_iter()
            .flatten()
            .any(|r| {
                r["width_ids"].as_array().is_some_and(|ids| {
                    ids.iter().any(|id| {
                        id.as_str()
                            .is_some_and(|s| s.starts_with("agulhas-krug-2012-"))
                    })
                })
            })
}

pub(crate) fn added_count(bundle: &Bundle) -> u64 {
    if active(bundle) { 2 } else { 0 }
}
pub(crate) fn widths(bundle: &Bundle) -> Vec<Value> {
    if active(bundle) { expected() } else { vec![] }
}

pub(crate) fn validate(bundle: &Bundle) -> Result<(), String> {
    if !active(bundle) {
        return Ok(());
    }
    let owners: Vec<_> = bundle
        .collections
        .get("objects")
        .into_iter()
        .flatten()
        .filter(|r| r["id"] == OWNER)
        .collect();
    if owners.len() != 1 {
        return Err("Missing or duplicate satellite-core owner".into());
    }
    let owner = owners[0];
    let ids = owner["width_ids"]
        .as_array()
        .ok_or("Missing satellite width join")?;
    if ids.len() != 4
        || ids[..2]
            .iter()
            .filter_map(Value::as_str)
            .collect::<BTreeSet<_>>()
            != OLD_IDS.into_iter().collect()
        || ids[2..] != IDS.iter().map(|id| json!(id)).collect::<Vec<_>>()
        || owner["capabilities"]["scoped_width"] != 4
    {
        return Err("Changed satellite width owner, prior join or capability".into());
    }
    let marker = json!({"logical_parent_sha256":PARENT,"source_file":SOURCE,"source_file_sha256":pin(),
        "records_added":2,"prior_width_records":172,"prior_agulhas_width_ids":ids[..2],
        "width_samples_added":0,"length_records_added":0,"geometry_added":false});
    if bundle.manifest[KEY] != marker || bundle.manifest["input_sha256"][SOURCE] != pin() {
        return Err("Changed satellite width source or marker".into());
    }
    let all = bundle.collections.get("widths").ok_or("Missing widths")?;
    let actual: Vec<_> = all
        .iter()
        .filter(|r| {
            r.get("satellite_core_context").is_some()
                || r["id"]
                    .as_str()
                    .is_some_and(|s| s.starts_with("agulhas-krug-2012-"))
        })
        .collect();
    let expected = expected();
    if actual.len() != 2
        || expected
            .iter()
            .any(|e| actual.iter().filter(|r| ***r == *e).count() != 1)
    {
        return Err("Satellite mean, operator, uncertainty, source or identity differs".into());
    }
    for other in bundle
        .collections
        .get("objects")
        .into_iter()
        .flatten()
        .filter(|r| r["id"] != OWNER)
    {
        if other["width_ids"]
            .as_array()
            .is_some_and(|a| a.iter().any(|id| IDS.iter().any(|expected| id == expected)))
        {
            return Err("Satellite width joined to unrelated owner".into());
        }
    }
    Ok(())
}

pub(crate) fn scene(matches: &[&Value]) -> Value {
    let rows: Vec<_> = matches
        .iter()
        .filter(|r| r["id"].as_str().is_some_and(|id| IDS.contains(&id)))
        .map(|r| (*r).clone())
        .collect();
    if rows.is_empty() {
        return Value::Null;
    }
    let doc = document();
    json!({"kind":"published_satellite_core_widths","title":"Agulhas satellite core widths",
        "scope":"Track020 offshore Port Elizabeth; method-specific regional mean core widths, not the full current.",
        "records":rows,"source_file":SOURCE,"full_context_figure":FIGURE,
        "seasonality_finding":doc["seasonality_finding"],"source_ambiguities":doc["source_ambiguities"]})
}

pub(crate) fn by_current(bundle: &Bundle) -> Value {
    if !active(bundle) {
        return json!({});
    }
    let rows = widths(bundle);
    let refs = rows.iter().collect::<Vec<_>>();
    json!({"agulhas":scene(&refs)})
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> Bundle {
        let ids: Vec<_> = OLD_IDS
            .iter()
            .chain(IDS.iter())
            .map(|id| json!(id))
            .collect();
        Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest: json!({"input_sha256":{SOURCE:pin()},KEY:{"logical_parent_sha256":PARENT,"source_file":SOURCE,"source_file_sha256":pin(),"records_added":2,"prior_width_records":172,"prior_agulhas_width_ids":ids[..2],"width_samples_added":0,"length_records_added":0,"geometry_added":false}}),
            collections: std::collections::BTreeMap::from([
                (
                    "objects".into(),
                    vec![json!({"id":OWNER,"width_ids":ids,"capabilities":{"scoped_width":4}})],
                ),
                ("widths".into(), expected()),
            ]),
        }
    }
    #[test]
    fn changed_means_scopes_and_ambiguity_fail() {
        validate(&fixture()).unwrap();
        for (key, value) in [
            ("approximate_width_km", json!(80)),
            ("width_range_km", json!([64, 80])),
            ("current_id", json!("agulhas-return")),
            ("seasonal_playback_eligible", json!(true)),
            ("geometry", json!({"invented":true})),
        ] {
            let mut b = fixture();
            b.collections.get_mut("widths").unwrap()[0][key] = value;
            assert!(validate(&b).is_err(), "{key}");
        }
        let mut b = fixture();
        b.collections.get_mut("widths").unwrap()[0]["satellite_core_context"]["source_ambiguities"] =
            json!([]);
        assert!(validate(&b).is_err());
    }
    #[test]
    fn deletion_duplication_source_and_join_mutations_fail() {
        let mut b = fixture();
        b.collections.get_mut("widths").unwrap().pop();
        assert!(validate(&b).is_err());
        let mut b = fixture();
        let row = b.collections["widths"][0].clone();
        b.collections.get_mut("widths").unwrap().push(row);
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.manifest["input_sha256"][SOURCE] = json!("wrong");
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections.get_mut("objects").unwrap()[0]["capabilities"]["scoped_width"] = json!(2);
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections
            .get_mut("objects")
            .unwrap()
            .push(json!({"id":"current:other","width_ids":[IDS[0]]}));
        assert!(validate(&b).is_err());
    }
    #[test]
    fn scene_respects_filtered_matches_without_inventing_a_range() {
        let rows = expected();
        let s = scene(&[&rows[1]]);
        assert_eq!(s["records"].as_array().unwrap().len(), 1);
        assert_eq!(s["records"][0]["reported_mean_width_km"], 80);
        assert!(s["records"][0]["width_range_km"].is_null());
        assert!(scene(&[]).is_null());
    }
}
