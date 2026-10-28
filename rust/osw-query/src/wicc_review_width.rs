//! A review-cited regional width does not become an independent observation.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};

const SOURCE: &str = "research/wicc-vinayachandran-2021-surface-width-source-facts-v1.json";
const RAW: &str =
    include_str!("../../../research/wicc-vinayachandran-2021-surface-width-source-facts-v1.json");
const KEY: &str = "published_wicc_review_width_v1";
const OWNER: &str = "current:west-india-coastal";
const ID: &str = "wicc-vinayachandran-2021-review-surface-width";
const PARENT: &str = "b7884cb7b9febf250c73d2402754f2794598d472b7687f45b9a57555691ab017";
const FIGURE: &str = "figures/wicc-vinayachandran-2021-surface-width-v1.svg";
fn pin() -> String {
    format!("{:x}", Sha256::digest(RAW.as_bytes()))
}
fn document() -> Value {
    serde_json::from_str(RAW).unwrap()
}

pub(crate) fn active(b: &Bundle) -> bool {
    !b.manifest[KEY].is_null()
        || !b.manifest["published_wicc_review_width_index_v1"].is_null()
        || !b.manifest["input_sha256"][SOURCE].is_null()
        || b.collections
            .get("widths")
            .into_iter()
            .flatten()
            .any(|r| r["id"] == ID || r.get("review_width_context").is_some())
        || b.collections.get("objects").into_iter().flatten().any(|r| {
            r["width_ids"]
                .as_array()
                .is_some_and(|a| a.iter().any(|v| v == ID))
        })
}
pub(crate) fn expected() -> Value {
    let doc = document();
    let mut row = doc["records"][0].clone();
    let extra = json!({"name":"West India Coastal Current","status":"editorial_review_cited_width_not_independent_measurement",
        "measurement_type":"published_review_cited_surface_width","width_metric":"review_cited_regional_surface_width",
        "width_metric_label":"Review-cited surface current width","approximate_width_km":150,"width_range_km":null,
        "range_interpretation":"One approximate review-cited estimate; no seasonal or uncertainty interval.",
        "time_convention":row["time_description"],"layer":row["layer_description"],"section_geometry":null,
        "width_sampling_depth_m":null,"boundary_sides":"source_described_coast_to_current_extent_no_georeferenced_edges",
        "source_file":SOURCE,"source_file_sha256":pin(),"source_pointer":"/records/0","source_url":doc["source"]["url"],
        "source_citation":"Vinayachandran et al. (2021), doi:10.5194/bg-18-5967-2021, section2.7.1, p.5991",
        "source_evidence_kind":"published_review_citing_prior_ship_observations",
        "extraction_method":"Transcribed explicit width description in the original review; no new observation or reconstruction of the cited1990 methods.",
        "phase_label":"About 150 km / review-cited surface width","phase_kind":"review_cited_surface_width",
        "full_width_inference_eligible":false,"is_confidence_interval":false,
        "review_width_context":{"source":doc["source"],"underlying_cited_work":doc["underlying_cited_work"],
            "excluded_inferences":doc["excluded_inferences"],"observational_independence_note":doc["observational_independence_note"],"full_context_figure":FIGURE}});
    row.as_object_mut()
        .unwrap()
        .extend(extra.as_object().unwrap().clone());
    row
}
pub(crate) fn widths(b: &Bundle) -> Vec<Value> {
    if active(b) { vec![expected()] } else { vec![] }
}
pub(crate) fn owner_ids(b: &Bundle, owner: &Value) -> Vec<Value> {
    if active(b) && owner == OWNER {
        vec![json!(ID)]
    } else {
        vec![]
    }
}
pub(crate) fn changed_fingerprint(prior: &str, group: &str) -> Result<String, String> {
    if prior.len() != 64
        || !prior
            .bytes()
            .all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b))
    {
        return Err("Prior WICC fingerprint required".into());
    }
    Ok(format!(
        "{:x}",
        Sha256::digest(
            format!(
                "osw.wicc-review-width.v1\n{group}\n{prior}\n{}\n{ID}\n",
                pin()
            )
            .as_bytes()
        )
    ))
}
pub(crate) fn dashboard_row(b: &Bundle, original: &Value) -> Result<Value, String> {
    if !active(b) || original["id"] != OWNER {
        return Ok(original.clone());
    }
    let marker = &b.manifest[KEY];
    let prior = marker["prior_dashboard_fingerprint"]
        .as_str()
        .ok_or("Missing WICC prior fingerprint")?;
    let measurements = marker["prior_measurements_fingerprint"]
        .as_str()
        .ok_or("Missing WICC prior measurement fingerprint")?;
    if original["capabilities"]["scoped_width"] != 0
        || original["fingerprint"] != prior
        || original["section_fingerprints"]["measurements"] != measurements
    {
        return Err("Historical WICC dashboard differs".into());
    }
    let mut row = original.clone();
    if let Some(ids) = row.get_mut("width_ids") {
        if *ids != json!([]) {
            return Err("Historical WICC dashboard join differs".into());
        }
        *ids = json!([ID]);
    }
    row["capabilities"]["scoped_width"] = json!(1);
    row["fingerprint"] = json!(changed_fingerprint(prior, "object")?);
    row["section_fingerprints"]["measurements"] =
        json!(changed_fingerprint(measurements, "measurements")?);
    Ok(row)
}
pub(crate) fn dashboard_document(b: &Bundle, mut doc: Value) -> Result<Value, String> {
    if !active(b) {
        return Ok(doc);
    }
    let rows = doc["entries"]
        .as_array()
        .ok_or("Missing dashboard entries")?;
    if rows.iter().filter(|r| r["id"] == OWNER).count() != 1 {
        return Err("One historical WICC dashboard row required".into());
    }
    let projected = rows
        .iter()
        .map(|r| dashboard_row(b, r))
        .collect::<Result<Vec<_>, _>>()?;
    let fingerprint = changed_fingerprint(
        doc["snapshot_fingerprint"]
            .as_str()
            .ok_or("Missing dashboard fingerprint")?,
        "snapshot",
    )?;
    doc["entries"] = json!(projected);
    doc["snapshot_fingerprint"] = json!(fingerprint);
    doc["published_wicc_review_width_projection_v1"] = json!({"source_file":SOURCE,"source_file_sha256":pin(),"source_dashboard_sha256":b.manifest["dashboard_receipt"]["source_sha256"],"scope":"One review-cited surface width; no independent sample, geometry or annual range."});
    Ok(doc)
}
pub(crate) fn validate(b: &Bundle) -> Result<(), String> {
    if !active(b) {
        return Ok(());
    }
    let owners = b
        .collections
        .get("objects")
        .into_iter()
        .flatten()
        .filter(|r| r["id"] == OWNER)
        .collect::<Vec<_>>();
    if owners.len() != 1 {
        return Err("One WICC review width owner required".into());
    }
    let retained = crate::wicc_winter_reference::retained_width_owner(b, owners[0])?;
    let owner = &retained;
    let marker = &b.manifest[KEY];
    let prior = marker["prior_dashboard_fingerprint"]
        .as_str()
        .ok_or("Missing WICC prior fingerprint")?;
    let measurements = marker["prior_measurements_fingerprint"]
        .as_str()
        .ok_or("Missing WICC prior measurement fingerprint")?;
    let expected_marker = json!({"logical_parent_sha256":PARENT,"source_file":SOURCE,"source_file_sha256":pin(),"records_added":1,"prior_width_records":174,"prior_owner_width_ids":[],"prior_dashboard_fingerprint":prior,"prior_measurements_fingerprint":measurements,"width_samples_added":0,"length_records_added":0,"independent_observations_added":0,"geometry_added":false});
    if *marker != expected_marker || b.manifest["input_sha256"][SOURCE] != pin() {
        return Err("WICC review source or admission marker differs".into());
    }
    if owner["width_ids"] != json!([ID])
        || owner["capabilities"]["scoped_width"] != 1
        || owner["fingerprint"] != changed_fingerprint(prior, "object")?
        || owner["section_fingerprints"]["measurements"]
            != changed_fingerprint(measurements, "measurements")?
    {
        return Err("WICC review width join or fingerprints differ".into());
    }
    let rows = b
        .collections
        .get("widths")
        .ok_or("Missing width records")?
        .iter()
        .filter(|r| {
            r["current_id"] == "west-india-coastal"
                || r["id"] == ID
                || r.get("review_width_context").is_some()
        })
        .collect::<Vec<_>>();
    if rows != vec![&expected()] {
        return Err("Review value, scope, lineage or unknown support differs".into());
    }
    if b.collections
        .get("objects")
        .into_iter()
        .flatten()
        .filter(|r| r["id"] != OWNER)
        .any(|r| {
            r["width_ids"]
                .as_array()
                .is_some_and(|a| a.iter().any(|v| v == ID))
        })
    {
        return Err("Review width joined to another owner".into());
    }
    Ok(())
}
pub(crate) fn scene(matches: &[&Value]) -> Value {
    let rows = matches
        .iter()
        .filter(|r| r["id"] == ID)
        .map(|r| (*r).clone())
        .collect::<Vec<_>>();
    if rows.is_empty() {
        return Value::Null;
    }
    json!({"kind":"published_review_cited_widths","title":"West India Coastal Current: review-cited width","scope":"Surface current in the west-coast-of-India summer-monsoon discussion; exact sampling dates and numerical width depth unspecified.","records":rows,"source_file":SOURCE,"full_context_figure":FIGURE})
}
pub(crate) fn by_current(b: &Bundle) -> Value {
    if active(b) {
        let rows = widths(b);
        json!({"west-india-coastal":scene(&rows.iter().collect::<Vec<_>>())})
    } else {
        json!({})
    }
}

pub(crate) fn apply_phase_plan(b: &Bundle, plans: &mut Value) {
    if active(b) {
        plans["west-india-coastal"] = json!({"current_id":"west-india-coastal",
            "phases":[{"id":ID,"width_id":ID,"frame_id":null,"direction_id":null,"label":expected()["phase_label"],"playback_step_eligible":false}],
            "can_play":false,"eligible_indices":[],
            "range_note":"One approximate review-cited surface width. Exact sampling dates, numerical width depth, uncertainty and annual ranges are unreported; the cited original methods remain unverified.",
            "playback_scope":"Static review-cited evidence; no comparable recorded seasonal sequence."});
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> Bundle {
        let prior = "a".repeat(64);
        let measurements = "b".repeat(64);
        Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest: json!({"input_sha256":{SOURCE:pin()},KEY:{"logical_parent_sha256":PARENT,"source_file":SOURCE,"source_file_sha256":pin(),"records_added":1,"prior_width_records":174,"prior_owner_width_ids":[],"prior_dashboard_fingerprint":prior,"prior_measurements_fingerprint":measurements,"width_samples_added":0,"length_records_added":0,"independent_observations_added":0,"geometry_added":false}}),
            collections: std::collections::BTreeMap::from([
                (
                    "objects".into(),
                    vec![
                        json!({"id":OWNER,"width_ids":[ID],"capabilities":{"scoped_width":1},"fingerprint":changed_fingerprint(&prior,"object").unwrap(),"section_fingerprints":{"measurements":changed_fingerprint(&measurements,"measurements").unwrap()}}),
                    ],
                ),
                ("widths".into(), vec![expected()]),
            ]),
        }
    }
    #[test]
    fn exact_review_lineage_and_unknown_support_are_required() {
        validate(&fixture()).unwrap();
        for (key, value) in [
            ("approximate_width_km", json!(400)),
            ("fixed_layer_bounds_m", json!([0, 100])),
            ("calendar_months", json!([6, 7, 8])),
            ("independent_observational_sample", json!(true)),
            ("seasonal_playback_eligible", json!(true)),
        ] {
            let mut b = fixture();
            b.collections.get_mut("widths").unwrap()[0][key] = value;
            assert!(validate(&b).is_err(), "{key}");
        }
        let mut b = fixture();
        b.collections.get_mut("widths").unwrap()[0]["review_width_context"]["underlying_cited_work"]
            ["original_full_text_reviewed"] = json!(true);
        assert!(validate(&b).is_err());
    }
    #[test]
    fn duplication_source_rebinding_and_lost_update_signal_fail() {
        let mut b = fixture();
        b.collections.get_mut("widths").unwrap().push(expected());
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.manifest["input_sha256"][SOURCE] = json!("wrong");
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections.get_mut("objects").unwrap()[0]["fingerprint"] = json!("a".repeat(64));
        assert!(validate(&b).is_err());
    }
    #[test]
    fn filtered_scene_and_dashboard_projection_preserve_identity() {
        let mut plans = json!({"other":{"preserve":true}});
        apply_phase_plan(&fixture(), &mut plans);
        assert_eq!(plans["other"], json!({"preserve":true}));
        assert_eq!(plans["west-india-coastal"]["can_play"], false);
        assert_eq!(plans["west-india-coastal"]["eligible_indices"], json!([]));
        assert_eq!(
            plans["west-india-coastal"]["phases"][0]["playback_step_eligible"],
            false
        );
        assert!(scene(&[]).is_null());
        let row = expected();
        assert_eq!(scene(&[&row])["records"][0], row);
        let b = fixture();
        let old = json!({"id":OWNER,"width_ids":[],"capabilities":{"scoped_width":0},"fingerprint":"a".repeat(64),"section_fingerprints":{"measurements":"b".repeat(64),"identity":"unchanged"}});
        let projected = dashboard_row(&b, &old).unwrap();
        assert_eq!(projected["capabilities"]["scoped_width"], 1);
        assert_eq!(projected["section_fingerprints"]["identity"], "unchanged");
        assert_eq!(
            dashboard_row(&b, &json!({"id":"current:agulhas","preserve":true})).unwrap(),
            json!({"id":"current:agulhas","preserve":true})
        );
    }
    #[test]
    fn admitted_indian_owner_guard_accepts_only_the_exact_review_extension() {
        let admitted = fixture();
        let mut b = crate::current_gap_admissions::tests::fixture();
        b.manifest[KEY] = admitted.manifest[KEY].clone();
        b.manifest["input_sha256"][SOURCE] = json!(pin());
        let owner = b
            .collections
            .get_mut("objects")
            .unwrap()
            .iter_mut()
            .find(|r| r["id"] == OWNER)
            .unwrap();
        let projected = &admitted.collections["objects"][0];
        for key in ["width_ids", "fingerprint", "section_fingerprints"] {
            owner[key] = projected[key].clone();
        }
        owner["capabilities"]["scoped_width"] = json!(1);
        b.collections.get_mut("widths").unwrap().push(expected());
        validate(&b).unwrap();
        crate::current_gap_admissions::validate(&b).unwrap();
        let admission = b.collections["current_identity_admissions"]
            .iter()
            .find(|r| r["entity_id"] == OWNER)
            .unwrap();
        assert_eq!(
            crate::current_gap_admissions::decision(&b, admission).unwrap()["measurement_ids"],
            json!([ID])
        );
        b.collections
            .get_mut("objects")
            .unwrap()
            .iter_mut()
            .find(|r| r["id"] == OWNER)
            .unwrap()["capabilities"]["scoped_width"] = json!(2);
        assert!(crate::current_gap_admissions::validate(&b).is_err());
    }
}
