//! A review-cited regional width does not become an independent observation.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};

const SOURCE: &str = "research/eacc-dekeyzer-2012-cited-width-lower-bound-source-facts-v1.json";
const RAW: &str = include_str!(
    "../../../research/eacc-dekeyzer-2012-cited-width-lower-bound-source-facts-v1.json"
);
const SOURCE_SHA: &str = "6c910c3e9ec09ff82c5d40fddb99b890a453a2ab35d994ee81e6ccc07b74012a";
const KEY: &str = "published_eacc_cited_width_constraint_v1";
const OWNER: &str = "current:east-african-coastal";
const ID: &str = "eacc-dekeyzer-2012-bell-cited-width-lower-bound";
const PARENT: &str = "360e775a1dbb49d5c7934cca1f288ab2f2f8cd71bfa8fd1368fb35b086f4e1e0";
const FIGURE: &str = "figures/eacc-dekeyzer-2012-cited-width-lower-bound-v2.svg";
fn pin() -> String {
    format!("{:x}", Sha256::digest(RAW.as_bytes()))
}
fn document() -> Value {
    serde_json::from_str(RAW).unwrap()
}

pub(crate) fn active(b: &Bundle) -> bool {
    !b.manifest[KEY].is_null()
        || !b.manifest["published_eacc_cited_width_constraint_index_v1"].is_null()
        || !b.manifest["input_sha256"][SOURCE].is_null()
        || b.collections
            .get("widths")
            .into_iter()
            .flatten()
            .any(|r| r["id"] == ID || r.get("cited_width_constraint_context").is_some())
        || b.collections.get("objects").into_iter().flatten().any(|r| {
            r["width_ids"]
                .as_array()
                .is_some_and(|a| a.iter().any(|v| v == ID))
        })
}
pub(crate) fn expected() -> Value {
    let doc = document();
    let mut row = doc["records"][0].clone();
    let extra = json!({"name":"East African Coastal Current","status":"editorial_cited_width_constraint_not_independent_measurement","measurement_type":"published_thesis_cited_width_constraint","width_metric":"review_cited_current_width_lower_bound","width_metric_label":"Thesis-cited exclusive width lower bound","approximate_width_km":null,"range_interpretation":"Over160km is an exclusive lower bound, not a central width, finite interval or annual range.","time_convention":"No width observation date or seasonal range supplied. The nearby year-round statement describes current position, not a dated width occupation.","layer":"Surface-circulation discussion; no numerical width sampling depth is supplied.","section_geometry":null,"width_sampling_depth_m":null,"boundary_sides":"not_supplied_for_the_cited_width_constraint","source_file":"research/eacc-dekeyzer-2012-cited-width-lower-bound-source-facts-v1.json","source_file_sha256":pin(),"source_pointer":"/records/0","source_url":"https://media.suub.uni-bremen.de/entities/publication/6e65bc8a-fb95-4916-917e-f9638fde7ade","source_download_url":"https://media.suub.uni-bremen.de/bitstreams/bc3eab24-8913-4fb3-bc33-b763a8e61d6f/download#page=74","source_citation":"Dekeyzer (2012), thesis section7.2, printed p.56 / PDF p.74; cites Bell (1972).","source_evidence_kind":"doctoral_thesis_citing_earlier_width_literature","extraction_method":"Retain the original thesis prose lower bound; no reconstruction of the cited Bell methods.","phase_label":"Over 160 km / cited width lower bound","phase_kind":"review_cited_width_constraint","full_width_inference_eligible":false,"is_confidence_interval":false,"cited_width_constraint_context":{"source":{"author":"Stefanie Dekeyzer","title":"Minor element composition and stable oxygen isotopes of calcareous shells of the dinoflagellate Thoracosphaera heimii","repository_publication_date":"2012-02-09","cover_date":"2011-10","primary_repository_record":"https://media.suub.uni-bremen.de/entities/publication/6e65bc8a-fb95-4916-917e-f9638fde7ade","source_url":"https://media.suub.uni-bremen.de/bitstreams/bc3eab24-8913-4fb3-bc33-b763a8e61d6f/download","final_url":"https://media-api.suub.uni-bremen.de/server/api/core/bitstreams/bc3eab24-8913-4fb3-bc33-b763a8e61d6f/content","urn":"urn:nbn:de:gbv:46-00102543-14"},"passage":{"section":"7.2 Oceanographic setting","pdf_page":74,"printed_page":56,"paragraph":"Final paragraph, surface circulation discussion","short_anchor":"width of the current is over 160 km","reference_pdf_page":95,"reference_printed_page":77},"underlying_cited_work":{"author":"B. E. Bell","year_as_cited":1972,"chapter_title":"Marine fisheries","book_title_as_cited":"East Africa: Its people and resources","editor_as_cited":"W. T. W. Morgan","publisher_as_cited":"Oxford University Press, New York","pages_as_cited":"243-253","original_full_text_reviewed":false,"original_file_sha256":null,"doi":null,"edition_or_pagination_independently_verified":false},"excluded_inferences":["Do not convert over160km into an exact160km width, an at-least160km inclusive bound or a160-200km interval.","The nearby11S-3S position statement is not an alongflow path or measured current length.","Do not transfer thesis sediment-sampling dates, monsoon month descriptions, transport layers or isotope uncertainties to the cited width.","Do not infer paired velocity edges, current footprint, area, state intersections, annual extrema or confidence intervals."],"lineage_note":"This is one thesis-cited historical width constraint. Bell is also cited in later circulation literature; repeated descriptions are not independent observational corroboration. A future original Bell review must reconcile this report rather than duplicate it.","full_context_figure":"figures/eacc-dekeyzer-2012-cited-width-lower-bound-v2.svg"}});
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
        return Err("Prior EACC fingerprint required".into());
    }
    Ok(format!(
        "{:x}",
        Sha256::digest(
            format!(
                "osw.eacc-cited-width-constraint.v1\n{group}\n{prior}\n{}\n{ID}\n",
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
        .ok_or("Missing EACC prior fingerprint")?;
    let measurements = marker["prior_measurements_fingerprint"]
        .as_str()
        .ok_or("Missing EACC prior measurement fingerprint")?;
    if original["capabilities"]["scoped_width"] != 0
        || original["fingerprint"] != prior
        || original["section_fingerprints"]["measurements"] != measurements
    {
        return Err("Historical EACC dashboard differs".into());
    }
    let mut row = original.clone();
    if let Some(ids) = row.get_mut("width_ids") {
        if *ids != json!([]) {
            return Err("Historical EACC dashboard join differs".into());
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
        return Err("One historical EACC dashboard row required".into());
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
    doc["published_eacc_cited_width_constraint_projection_v1"] = json!({"source_file":SOURCE,"source_file_sha256":pin(),"source_dashboard_sha256":b.manifest["dashboard_receipt"]["source_sha256"],"scope":"One thesis-cited exclusive width lower bound; no independent sample, geometry or annual range."});
    Ok(doc)
}
pub(crate) fn validate(b: &Bundle) -> Result<(), String> {
    if !active(b) {
        return Ok(());
    }
    if pin() != SOURCE_SHA {
        return Err("Compiled EACC source differs".into());
    }
    let owners = b
        .collections
        .get("objects")
        .into_iter()
        .flatten()
        .filter(|r| r["id"] == OWNER)
        .collect::<Vec<_>>();
    if owners.len() != 1 {
        return Err("One EACC review width owner required".into());
    }
    let owner = owners[0];
    let marker = &b.manifest[KEY];
    let prior = marker["prior_dashboard_fingerprint"]
        .as_str()
        .ok_or("Missing EACC prior fingerprint")?;
    let measurements = marker["prior_measurements_fingerprint"]
        .as_str()
        .ok_or("Missing EACC prior measurement fingerprint")?;
    let expected_marker = json!({"logical_parent_sha256":PARENT,"source_file":SOURCE,"source_file_sha256":pin(),"records_added":1,"prior_width_records":175,"prior_owner_width_ids":[],"prior_dashboard_fingerprint":prior,"prior_measurements_fingerprint":measurements,"width_samples_added":0,"length_records_added":0,"independent_observations_added":0,"geometry_added":false});
    if *marker != expected_marker || b.manifest["input_sha256"][SOURCE] != pin() {
        return Err("EACC review source or admission marker differs".into());
    }
    if owner["width_ids"] != json!([ID])
        || owner["capabilities"]["scoped_width"] != 1
        || owner["fingerprint"] != changed_fingerprint(prior, "object")?
        || owner["section_fingerprints"]["measurements"]
            != changed_fingerprint(measurements, "measurements")?
    {
        return Err("EACC review width join or fingerprints differ".into());
    }
    let rows = b
        .collections
        .get("widths")
        .ok_or("Missing width records")?
        .iter()
        .filter(|r| {
            r["current_id"] == "east-african-coastal"
                || r["id"] == ID
                || r.get("cited_width_constraint_context").is_some()
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
    json!({"kind":"published_cited_width_constraints","title":"East African Coastal Current: cited width lower bound","scope":"Historical width constraint cited in a doctoral thesis; no width occupation, fixed depth or boundary geometry supplied.","records":rows,"source_file":SOURCE,"full_context_figure":FIGURE})
}
pub(crate) fn by_current(b: &Bundle) -> Value {
    if active(b) {
        let rows = widths(b);
        json!({"east-african-coastal":scene(&rows.iter().collect::<Vec<_>>())})
    } else {
        json!({})
    }
}

pub(crate) fn extend_phase_plan(prior: &Value) -> Result<Value, String> {
    if !prior.is_object()
        || prior["current_id"] != "east-african-coastal"
        || !prior["can_play"].is_boolean()
    {
        return Err("Exact preceding EACC phase plan required".into());
    }
    let phases = prior["phases"].as_array().ok_or("Missing prior phases")?;
    let indices = prior["eligible_indices"]
        .as_array()
        .ok_or("Missing prior playback support")?;
    if phases.iter().any(|p| p["id"] == ID)
        || indices
            .iter()
            .any(|i| i.as_u64().is_none_or(|i| i as usize >= phases.len()))
    {
        return Err("Constraint duplicate or prior playback support differs".into());
    }
    let mut result = prior.clone();
    result["phases"].as_array_mut().unwrap().push(json!({"id":ID,"width_id":ID,"frame_id":null,"direction_id":null,"label":expected()["phase_label"],"playback_step_eligible":false}));
    Ok(result)
}
pub(crate) fn apply_phase_plan(b: &Bundle, plans: &mut Value) -> Result<(), String> {
    if active(b) {
        plans["east-african-coastal"] = extend_phase_plan(&plans["east-african-coastal"])?;
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> Bundle {
        let prior = "a".repeat(64);
        let measurements = "b".repeat(64);
        Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest: json!({"input_sha256":{SOURCE:pin()},KEY:{"logical_parent_sha256":PARENT,"source_file":SOURCE,"source_file_sha256":pin(),"records_added":1,"prior_width_records":175,"prior_owner_width_ids":[],"prior_dashboard_fingerprint":prior,"prior_measurements_fingerprint":measurements,"width_samples_added":0,"length_records_added":0,"independent_observations_added":0,"geometry_added":false}}),
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
            ("reported_bound_km", json!(400)),
            ("reported_operator", json!("gte")),
            ("reported_width_km", json!(160)),
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
        b.collections.get_mut("widths").unwrap()[0]["cited_width_constraint_context"]["underlying_cited_work"]
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
        let mut plans = json!({"other":{"preserve":true},"east-african-coastal":{"current_id":"east-african-coastal","phases":[],"eligible_indices":[],"can_play":false}});
        apply_phase_plan(&fixture(), &mut plans).unwrap();
        assert_eq!(plans["other"], json!({"preserve":true}));
        assert_eq!(plans["east-african-coastal"]["can_play"], false);
        assert_eq!(plans["east-african-coastal"]["eligible_indices"], json!([]));
        assert_eq!(
            plans["east-african-coastal"]["phases"][0]["playback_step_eligible"],
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
    #[test]
    fn existing_seasons_and_playback_survive_the_static_constraint_append() {
        let prior = json!({"current_id":"east-african-coastal","phases":[{"id":"old-season","preserve":true}],"can_play":true,"eligible_indices":[0],"range_note":"prior scope"});
        let after = extend_phase_plan(&prior).unwrap();
        assert_eq!(after["phases"][0], prior["phases"][0]);
        for key in ["current_id", "can_play", "eligible_indices", "range_note"] {
            assert_eq!(after[key], prior[key]);
        }
        assert_eq!(after["phases"][1]["playback_step_eligible"], false);
        assert!(extend_phase_plan(&after).is_err());
        let mut invalid = prior.clone();
        invalid["eligible_indices"] = json!([1]);
        assert!(extend_phase_plan(&invalid).is_err());
    }
}
