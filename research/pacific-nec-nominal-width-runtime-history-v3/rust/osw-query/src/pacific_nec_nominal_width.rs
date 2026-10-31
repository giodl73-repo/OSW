//! A nominal regional latitude span supplies no annual envelope or physical edges.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
use std::sync::OnceLock;

pub(crate) const FILE: &str = "research/pacific-nec-nominal-width-query-contract-v1.json";
pub(crate) const RAW: &str = include_str!("../../../research/pacific-nec-nominal-width-query-contract-v1.json");
const KEY: &str = "published_pacific_nec_nominal_width_v1";
pub(crate) const OWNER: &str = "current:pacific-north-equatorial";
const CURRENT: &str = "pacific-north-equatorial";
const FAMILY: &str = "current:north-equatorial";
fn pin(raw: &str) -> String { format!("{:x}", Sha256::digest(raw.as_bytes())) }
fn document() -> &'static Value {
    static DOC: OnceLock<Value> = OnceLock::new();
    DOC.get_or_init(|| serde_json::from_str(RAW).expect("compiled Pacific NEC nominal-width contract"))
}
fn marker() -> Value {
    json!({"schema":"osw.pacific-nec-nominal-width-runtime-receipt.v1","parent_logical_sha256":document()["parent_logical_sha256"],
        "contract_file":FILE,"contract_sha256":pin(RAW),"width_records_added":1,"publication_sources_added":2,
        "new_width_samples":0,"new_independent_observations":0,"new_length_records":0,"physical_geometry_added":false})
}
fn normalized(value: &Value) -> String {
    value.as_str().unwrap_or("").chars().filter(char::is_ascii_alphanumeric).flat_map(char::to_lowercase).collect()
}
fn decoded(value: &Value) -> String {
    let input=value.as_str().unwrap_or("").trim().as_bytes();let mut output=Vec::new();let mut i=0;
    while i<input.len() {
        if input[i]==b'%' && i+2<input.len() {
            if let (Some(a),Some(b))=((input[i+1] as char).to_digit(16),(input[i+2] as char).to_digit(16)) {
                output.push((a*16+b) as u8);i+=3;continue;
            }
        }
        output.push(input[i]);i+=1;
    }
    String::from_utf8_lossy(&output).to_lowercase()
}
fn doi(value: &Value) -> String {
    let decoded=decoded(value);let text=decoded.split(['?','#']).next().unwrap_or("");
    for prefix in ["https://doi.org/","http://doi.org/","https://dx.doi.org/","http://dx.doi.org/","doi:"] {
        if let Some(tail)=text.strip_prefix(prefix) {return tail.trim().trim_end_matches('/').into();}
    }
    if let Some((_,tail))=text.split_once("/doi/") {
        return ["full/","abs/","epdf/","pdf/"].iter().find_map(|p|tail.strip_prefix(*p)).unwrap_or(tail).trim_end_matches('/').into();
    }
    text.trim_end_matches('/').into()
}
fn url(value: &Value) -> String {
    let decoded=decoded(value);let text=decoded.split(['?','#']).next().unwrap_or("");
    text.strip_prefix("https://").or_else(||text.strip_prefix("http://")).unwrap_or(text).trim_end_matches('/').into()
}
fn checked(collections: &BTreeMap<String,Vec<Value>>, manifest: &Value) -> Result<bool,String> {
    let fail=||"Invalid Pacific NEC nominal regional width extension".to_owned();
    let rows=|name:&str|collections.get(name).map(Vec::as_slice).unwrap_or(&[]);
    let doc=document();let width=&doc["width_record"];let sources=doc["new_sources"].as_array().ok_or_else(fail)?;
    let trace=rows("sources").iter().any(|r|sources.iter().any(|s|r["id"]==s["id"]))
        ||rows("widths").iter().any(|r|r["id"]==width["id"])
        ||rows("objects").iter().any(|r|r["width_ids"].as_array().is_some_and(|ids|ids.contains(&width["id"])));
    if manifest[KEY].is_null() && manifest["input_sha256"][FILE].is_null() && !trace {return Ok(false);}
    if manifest[KEY]!=marker() || manifest["input_sha256"][FILE]!=pin(RAW) {return Err(fail());}
    for (path,digest) in doc["input_sha256"].as_object().ok_or_else(fail)? {
        if manifest["input_sha256"][path]!=*digest {return Err(fail());}
    }
    let mut ids=BTreeSet::new();
    for actual in rows("sources") {
        let id=actual["id"].as_str().ok_or_else(fail)?;
        if id.is_empty() || !ids.insert(id) {return Err(fail());}
        for expected in sources {
            if actual["id"]==expected["id"] {
                if actual!=expected {return Err(fail());}
            } else if doi(&actual["doi"])==doi(&expected["doi"])
                ||doi(&actual["url"])==doi(&expected["doi"])
                ||url(&actual["url"])==url(&expected["url"])
                ||normalized(&actual["title"])==normalized(&expected["title"])
                ||normalized(&actual["label"])==normalized(&expected["title"]) {return Err(fail());}
        }
    }
    for expected in sources {
        if rows("sources").iter().filter(|r|r["id"]==expected["id"]).collect::<Vec<_>>()!=vec![expected] {return Err(fail());}
    }
    for (owner,prior) in doc["prior_records"]["identities"].as_object().ok_or_else(fail)? {
        let object=if owner==OWNER {&doc["final_owner"]} else {&prior["object"]};
        if rows("objects").iter().filter(|r|r["id"]==*owner).collect::<Vec<_>>()!=vec![object]
            ||rows("entities").iter().filter(|r|r["id"]==*owner).collect::<Vec<_>>()!=vec![&prior["entity"]] {return Err(fail());}
        let short=owner.strip_prefix("current:").ok_or_else(fail)?;
        let mut expected=prior["widths"].as_array().ok_or_else(fail)?.iter().collect::<Vec<_>>();
        if owner==OWNER {expected.push(width);}
        if rows("widths").iter().filter(|r|r["current_id"]==short ||r["entity_id"]==*owner).collect::<Vec<_>>()!=expected
            ||rows("reference_routes").iter().filter(|r|r["current_id"]==short ||r["entity_id"]==*owner).collect::<Vec<_>>()
                !=prior["reference_routes"].as_array().ok_or_else(fail)?.iter().collect::<Vec<_>>() {return Err(fail());}
        for source in prior["owner_sources"].as_array().ok_or_else(fail)? {
            if rows("sources").iter().filter(|r|r["id"]==source["id"]).collect::<Vec<_>>()!=vec![source] {return Err(fail());}
        }
    }
    if rows("widths").iter().filter(|r|r["id"]==width["id"]).count()!=1 {return Err(fail());}
    Ok(true)
}
pub(crate) fn validate(bundle:&Bundle)->Result<(),String> {checked(&bundle.collections,&bundle.manifest).map(|_|())}
pub(crate) fn identity_overlay(bundle:&Bundle)->Result<bool,String> {checked(&bundle.collections,&bundle.manifest)}
// Call only after identity_overlay has validated the entire exact extension.
// No other row or member measurement is hidden from the frozen identity validator.
pub(crate) fn identity_parent_row<'a>(collection:&str,row:&'a Value,enabled:bool)->Option<&'a Value> {
    if enabled && collection=="widths" && row["id"]==document()["width_record"]["id"] {return None;}
    if enabled && collection=="objects" && row["id"]==OWNER {return Some(&document()["dashboard_before"]);}
    Some(row)
}
pub(crate) fn additional_source_count(collections:&BTreeMap<String,Vec<Value>>,manifest:&Value)->Result<usize,String> {
    Ok(if checked(collections,manifest)? {2} else {0})
}
pub(crate) fn widths(bundle:&Bundle)->Vec<Value> {
    if bundle.manifest[KEY].is_null() {vec![]} else {vec![document()["width_record"].clone()]}
}
pub(crate) fn validated_widths(bundle:&Bundle)->Result<Vec<Value>,String> {
    if !checked(&bundle.collections,&bundle.manifest)? {return Ok(vec![]);}
    Ok(widths(bundle))
}
fn scene(records:Vec<&Value>)->Value {
    if records.is_empty() {return Value::Null;}
    json!({"kind":"published_current_dimension_evidence","title":"Pacific NEC: nominal near-surface width",
        "current_id":CURRENT,"entity_id":OWNER,"width_records":records,"event_records":[],
        "scope":"About 1,000 km is a WGS84 conversion of the nominal regional 8–17°N band, rounded to 100 km. It is not a whole-current width, annual range, numerical uncertainty or diagnosed flow-normal width.",
        "definition":"The project synthesis describes a near-surface band west of the dateline. Its related JPO study describes 7–17°N in a mapped 0–100 m mean field. Keep those source descriptions separate; no paired physical edges or uniform sampling dates are established.",
        "source_file":document()["width_record"]["source_file"],"source_url":document()["new_sources"][0]["url"],
        "source_label":"Reviewed original project synthesis","figure":"figures/pacific-nec-nominal-width-v1.svg"})
}
pub(crate) fn width_scene(records:&[&Value],bundle:&Bundle)->Value {
    if bundle.manifest[KEY].is_null() {return Value::Null;}
    scene(records.iter().copied().filter(|r|r["id"]==document()["width_record"]["id"]).collect())
}
pub(crate) fn by_current(bundle:&Bundle)->Value {
    let mut result=crate::azcc_onken_width::by_current(bundle);
    if !bundle.manifest[KEY].is_null() {result[CURRENT]=scene(vec![&document()["width_record"]]);}
    result
}
pub(crate) fn object_scene(bundle:&Bundle,owner:&str)->Value {
    if owner!=OWNER || bundle.manifest[KEY].is_null() {Value::Null} else {scene(vec![&document()["width_record"]])}
}
pub(crate) fn object_projection(bundle:&Bundle,owner:&str,mut result:Value)->Value {
    let scene=object_scene(bundle,owner);
    if !scene.is_null() {result["current_dimension_evidence_scene"]=scene;}
    result
}
pub(crate) fn member_context(bundle:&Bundle,owner:&Value)->Value {
    if owner.as_str()!=Some(OWNER) || bundle.manifest[KEY].is_null() {return Value::Null;}
    json!({"label":"Nominal regional width: about 1,000 km","query_url":document()["width_query_after_installation"],
        "scope":"Near-surface regional summary; annual range and physical edges unknown."})
}
pub(crate) fn identity_decision(bundle:&Bundle,admission:&Value)->Option<Value> {
    if admission["proposal_id"]!=CURRENT || bundle.manifest[KEY].is_null() {return None;}
    Some(json!({"current_id":CURRENT,"name":document()["final_owner"]["label"],
        "measurement_ids":[document()["width_record"]["id"]],"status":"nominal_regional_width_admitted",
        "whole_current_width_km":null,"annual_width_range_km":null,"admission_id":admission["id"]}))
}
pub(crate) fn apply_phase_plan(bundle:&Bundle,plans:&mut Value)->Result<(),String> {
    if bundle.manifest[KEY].is_null() {return Ok(());}
    let plan=&mut plans[CURRENT];
    if plan["current_id"]!=CURRENT || plan["phases"]!=json!([]) || plan["can_play"]!=false || plan["eligible_indices"]!=json!([]) {
        return Err("Nominal Pacific NEC width cannot acquire dated seasonal phases".into());
    }
    plan["range_note"]=json!("Nominal regional width about 1,000 km; sampling dates, annual ranges and numerical uncertainty remain unknown.");
    plan["playback_scope"]=json!("Static nominal summary; no comparable dated states for seasonal animation.");
    Ok(())
}
pub(crate) fn dashboard_row(bundle:&Bundle,original:&Value)->Result<Value,String> {
    if original["id"]!=OWNER || !checked(&bundle.collections,&bundle.manifest)? {return Ok(original.clone());}
    if original!=&document()["dashboard_before"] {return Err("Changed preceding Pacific NEC dashboard row".into());}
    Ok(document()["dashboard_after"].clone())
}
pub(crate) fn dashboard_document(bundle:&Bundle,mut doc:Value)->Result<Value,String> {
    if !checked(&bundle.collections,&bundle.manifest)? {return Ok(doc);}
    let rows=doc["entries"].as_array().ok_or("Missing preceding dashboard entries")?;
    let updated=rows.iter().map(|r|dashboard_row(bundle,r)).collect::<Result<Vec<_>,_>>()?;
    if rows.iter().filter(|r|r["id"]==OWNER).count()!=1 {return Err("One Pacific NEC dashboard row required".into());}
    let old=doc["snapshot_fingerprint"].as_str().ok_or("Missing preceding dashboard fingerprint")?;
    let fingerprint=pin(&format!("osw.pacific-nec-nominal-width.v1\n{old}\n{}\n",pin(RAW)));
    doc["entries"]=json!(updated);doc["snapshot_fingerprint"]=json!(fingerprint);
    doc["published_pacific_nec_nominal_width_projection_v1"]=json!({"contract_file":FILE,"contract_sha256":pin(RAW),"new_width_records":1,"new_independent_observations":0});
    Ok(doc)
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture()->Bundle {
        let doc=document();let mut b=Bundle{schema:"osw.query-bundle.v1".into(),manifest:json!({"input_sha256":{}}),collections:BTreeMap::new()};
        for prior in doc["prior_records"]["identities"].as_object().unwrap().values() {
            for (name,key) in [("objects","object"),("entities","entity")] {b.collections.entry(name.into()).or_default().push(prior[key].clone());}
            for source in prior["owner_sources"].as_array().unwrap() {
                let rows=b.collections.entry("sources".into()).or_default();
                if !rows.iter().any(|r|r["id"]==source["id"]) {rows.push(source.clone());}
            }
        }
        for row in b.collections.get_mut("objects").unwrap() {if row["id"]==OWNER {*row=doc["final_owner"].clone();}}
        b.collections.entry("sources".into()).or_default().extend(doc["new_sources"].as_array().unwrap().clone());
        b.collections.insert("widths".into(),vec![doc["width_record"].clone()]);b.collections.insert("reference_routes".into(),vec![]);
        for (p,h) in doc["input_sha256"].as_object().unwrap() {b.manifest["input_sha256"][p]=h.clone();}
        b.manifest["input_sha256"][FILE]=json!(pin(RAW));b.manifest[KEY]=marker();b
    }
    #[test] fn exact_scoped_width_and_source_count_with_filtered_scene() {
        let b=fixture();validate(&b).unwrap();assert_eq!(additional_source_count(&b.collections,&b.manifest).unwrap(),2);
        let w=&b.collections["widths"][0];assert_eq!(validated_widths(&b).unwrap(),vec![w.clone()]);
        assert_eq!(w["approximate_width_km"],1000.0);assert!(w["observed_period"].is_null());assert!(w["annual_width_range_km"].is_null());
        assert_eq!(width_scene(&[w],&b)["width_records"],json!([w]));assert!(width_scene(&[],&b).is_null());
        assert!(object_scene(&b,FAMILY).is_null());assert!(!object_scene(&b,OWNER).is_null());
    }
    #[test] fn changed_rows_or_orphan_receipts_are_refused() {
        for change in ["range","width","owner","source","pin","receipt","route","family"] {
            let mut b=fixture();match change {
                "range"=>b.collections.get_mut("widths").unwrap()[0]["annual_width_range_km"]=json!([900,1100]),
                "width"=>b.collections.get_mut("widths").unwrap().push(document()["width_record"].clone()),
                "owner"=>b.collections.get_mut("objects").unwrap().iter_mut().find(|r|r["id"]==OWNER).unwrap()["latest_observation_date"]=json!("2014-06-01"),
                "source"=>b.collections.get_mut("sources").unwrap().last_mut().unwrap()["doi"]=json!("different"),
                "pin"=>b.manifest["input_sha256"][FILE]=json!("changed"),
                "receipt"=>{b.manifest.as_object_mut().unwrap().remove(KEY);},
                "route"=>b.collections.get_mut("reference_routes").unwrap().push(json!({"id":"made-up","current_id":CURRENT})),
                _=>b.collections.get_mut("objects").unwrap().iter_mut().find(|r|r["id"]==FAMILY).unwrap()["width_ids"]=json!(["inherited"]),
            }
            assert!(validate(&b).is_err(),"{change}");assert!(identity_overlay(&b).is_err(),"{change}");
        }
    }
    #[test] fn publication_aliases_are_rejected_even_under_other_ids() {
        for alias in [json!({"id":"alias","doi":"https://doi.org/10.5670/OCEANOG.2015.78"}),
            json!({"id":"alias","url":"http://www.soest.hawaii.edu/oceanography/bo/Qiu_etal_TOS2015.pdf?tracking=1"}),
            json!({"id":"alias","title":document()["new_sources"][1]["title"]})] {
            let mut b=fixture();b.collections.get_mut("sources").unwrap().push(alias);assert!(validate(&b).is_err());
        }
    }
    #[test] fn validated_identity_parent_view_only_normalizes_exact_two_rows() {
        let b=fixture();let enabled=identity_overlay(&b).unwrap();
        let owner=b.collections["objects"].iter().find(|r|r["id"]==OWNER).unwrap();
        assert_eq!(identity_parent_row("objects",owner,enabled),Some(&document()["dashboard_before"]));
        assert!(identity_parent_row("widths",&b.collections["widths"][0],enabled).is_none());
        let arbitrary=json!({"id":"unreviewed","current_id":"atlantic-north-equatorial"});
        assert_eq!(identity_parent_row("widths",&arbitrary,enabled),Some(&arbitrary));
        assert_eq!(identity_parent_row("widths",&b.collections["widths"][0],false),Some(&b.collections["widths"][0]));
    }
    #[test] fn dashboard_updates_only_target_and_keeps_unknown_date_and_length() {
        let b=fixture();let other=json!({"id":"current:other","keep":true});
        let view=dashboard_document(&b,json!({"entries":[document()["dashboard_before"],other],"snapshot_fingerprint":"old","history":{"keep":true}})).unwrap();
        assert_eq!(view["entries"][0],document()["final_owner"]);assert_eq!(view["entries"][1],other);
        assert!(view["entries"][0]["latest_observation_date"].is_null());assert!(view["entries"][0]["published_length_km"].is_null());
        assert_eq!(view["history"]["keep"],true);
        assert!(dashboard_row(&b,&json!({"id":OWNER})).is_err());
    }
    #[test] fn old_bundles_have_no_new_counts_or_member_context() {
        let old=Bundle{schema:"osw.query-bundle.v1".into(),manifest:json!({}),collections:BTreeMap::new()};
        validate(&old).unwrap();assert!(!identity_overlay(&old).unwrap());assert!(validated_widths(&old).unwrap().is_empty());
        assert_eq!(additional_source_count(&old.collections,&old.manifest).unwrap(),0);assert!(member_context(&old,&json!(OWNER)).is_null());
    }
    #[test] fn measured_identity_status_does_not_enable_seasonal_playback() {
        let b=fixture();let admission=json!({"proposal_id":CURRENT,"id":"current_admission:pacific-north-equatorial"});
        let decision=identity_decision(&b,&admission).unwrap();assert_eq!(decision["status"],"nominal_regional_width_admitted");
        assert_eq!(decision["measurement_ids"],json!([document()["width_record"]["id"]]));
        assert!(identity_decision(&b,&json!({"proposal_id":"atlantic-north-equatorial"})).is_none());
        let original=json!({"current_id":CURRENT,"phases":[],"can_play":false,"eligible_indices":[],"range_note":"old","playback_scope":"old"});
        let mut plans=json!({"other":{"keep":true}});plans[CURRENT]=original;apply_phase_plan(&b,&mut plans).unwrap();
        assert_eq!(plans[CURRENT]["phases"],json!([]));assert_eq!(plans[CURRENT]["can_play"],false);assert_eq!(plans["other"]["keep"],true);
        plans[CURRENT]["can_play"]=json!(true);assert!(apply_phase_plan(&b,&mut plans).is_err());
    }
    #[test] fn frozen_basin_identity_guarantees_coexist_with_only_the_reviewed_width() {
        let identity:Value=serde_json::from_str(crate::equatorial_basin_identities::RAW).unwrap();
        let mut b=Bundle{schema:"osw.query-bundle.v1".into(),manifest:json!({"input_sha256":{}}),
            collections:serde_json::from_value(identity["additions"].clone()).unwrap()};
        for prior in identity["prior_family_records"].as_object().unwrap().values() {
            for name in ["entities","objects","names"] {b.collections.get_mut(name).unwrap().extend(prior[name].as_array().unwrap().clone());}
        }
        b.collections.insert("sources".into(),identity["prior_glossary_sources"].as_array().unwrap().clone());
        for (path,digest) in identity["input_sha256"].as_object().unwrap() {b.manifest["input_sha256"][path]=digest.clone();}
        b.manifest["input_sha256"][crate::equatorial_basin_identities::FILE]=json!(pin(crate::equatorial_basin_identities::RAW));
        b.manifest["equatorial_basin_identities_v3"]=json!({"contract_file":crate::equatorial_basin_identities::FILE,
            "contract_sha256":pin(crate::equatorial_basin_identities::RAW),"parent_logical_sha256":identity["parent_logical_sha256"],
            "new_identity_ids":identity["expected_entity_ids"],"accepted_current_identities":111,
            "new_measurements":0,"new_publication_sources":0,"physical_geometry_added":false});
        b.manifest["taxonomy"]=json!({"node_count":251,"link_count":25});
        crate::equatorial_basin_identities::validate(&b).unwrap();
        let added=fixture();
        b.collections.insert("widths".into(),added.collections["widths"].clone());
        *b.collections.get_mut("objects").unwrap().iter_mut().find(|r|r["id"]==OWNER).unwrap()=document()["final_owner"].clone();
        b.collections.get_mut("sources").unwrap().extend(document()["new_sources"].as_array().unwrap().clone());
        for (path,digest) in document()["input_sha256"].as_object().unwrap() {b.manifest["input_sha256"][path]=digest.clone();}
        b.manifest["input_sha256"][FILE]=json!(pin(RAW));b.manifest[KEY]=marker();
        validate(&b).unwrap();crate::equatorial_basin_identities::validate(&b).unwrap();
        let member=crate::equatorial_basin_identities::for_owner(&b,OWNER);
        assert_eq!(member["members"].as_array().unwrap().iter().filter(|r|!r["nominal_width_evidence"].is_null()).count(),1);
        assert!(member["dimension_status"].as_str().unwrap().contains("not inherited"));
        let mut bad=Bundle{schema:b.schema.clone(),manifest:b.manifest.clone(),collections:b.collections.clone()};
        bad.collections.get_mut("widths").unwrap().push(json!({"id":"unreviewed","current_id":"atlantic-north-equatorial"}));
        assert!(crate::equatorial_basin_identities::validate(&bad).is_err());
        let mut bad=Bundle{schema:b.schema.clone(),manifest:b.manifest.clone(),collections:b.collections.clone()};
        bad.collections.get_mut("widths").unwrap()[0]["numerical_width_uncertainty_km"]=json!(100);
        assert!(crate::equatorial_basin_identities::validate(&bad).is_err());
    }
}
