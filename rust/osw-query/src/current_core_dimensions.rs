//! Scoped regional reach and secondary width claims preserve their original operators.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
use std::sync::OnceLock;

const FILE: &str = "research/current-core-dimensions-query-contract-v1.json";
const RAW: &str = include_str!("../../../research/current-core-dimensions-query-contract-v1.json");
const KEY: &str = "published_current_core_dimensions_v1";
const REACHES: &str = "current_regional_reaches";
fn pin(raw: &str)->String {format!("{:x}",Sha256::digest(raw.as_bytes()))}
fn document()->&'static Value {static DOC:OnceLock<Value>=OnceLock::new();DOC.get_or_init(||serde_json::from_str(RAW).expect("compiled scoped dimensions"))}
fn marker()->Value {json!({"schema":"osw.current-core-dimensions-runtime.v1","parent_logical_sha256":document()["parent_logical_sha256"],
    "contract_file":FILE,"contract_sha256":pin(RAW),"width_records_added":1,"regional_reaches_added":1,"sources_added":2,
    "whole_current_lengths_added":0,"annual_ranges_added":0,"physical_geometries_added":0,"independent_observations_added":0})}
fn rows<'a>(collections:&'a BTreeMap<String,Vec<Value>>,name:&str)->&'a [Value] {collections.get(name).map(Vec::as_slice).unwrap_or(&[])}
fn owns(row:&Value,owner:&str)->bool {row["entity_id"]==owner || owner.strip_prefix("current:").is_some_and(|short|row["current_id"]==short)}
fn additions(name:&str)->&'static [Value] {
    let key=match name {"sources"=>"new_sources","widths"=>"width_records",REACHES=>"reach_records",_=>return &[]};
    document()[key].as_array().unwrap()
}
fn checked(collections:&BTreeMap<String,Vec<Value>>,manifest:&Value)->Result<bool,String> {
    crate::validation_scope::checked(collections,manifest,module_path!(),||checked_uncached(collections,manifest))
}
fn checked_uncached(collections:&BTreeMap<String,Vec<Value>>,manifest:&Value)->Result<bool,String> {
    let fail=||"Invalid scoped current reach or cited-width extension".to_owned();let doc=document();
    let trace=collections.values().flatten().any(|r|["sources","widths",REACHES].iter().any(|name|additions(name).iter().any(|e|e["id"]==r["id"])));
    if manifest[KEY].is_null() && manifest["input_sha256"][FILE].is_null() && !trace {return Ok(false);}
    if manifest[KEY]!=marker() || manifest["input_sha256"][FILE]!=pin(RAW) {return Err(fail());}
    for (path,hash) in doc["input_sha256"].as_object().ok_or_else(fail)? {if manifest["input_sha256"][path]!=*hash {return Err(fail());}}
    let mut ids=BTreeSet::new();
    for row in rows(collections,"sources") {if !row["id"].as_str().is_some_and(|id|!id.is_empty()&&ids.insert(id)) {return Err(fail());}}
    for expected in doc["prior_source_inventory"].as_array().ok_or_else(fail)?.iter().chain(additions("sources")) {
        if rows(collections,"sources").iter().filter(|r|r["id"]==expected["id"]).collect::<Vec<_>>()!=vec![expected] {return Err(fail());}
    }
    for (owner,prior) in doc["prior_owners"].as_object().ok_or_else(fail)? {
        if rows(collections,"objects").iter().filter(|r|r["id"]==*owner).collect::<Vec<_>>()!=vec![&doc["final_objects"][owner]]
            ||rows(collections,"entities").iter().filter(|r|r["id"]==*owner).collect::<Vec<_>>()!=prior["entities"].as_array().ok_or_else(fail)?.iter().collect::<Vec<_>>() {return Err(fail());}
        for name in ["widths",REACHES] {
            let mut expected=prior[name].as_array().ok_or_else(fail)?.iter().collect::<Vec<_>>();expected.extend(additions(name).iter().filter(|r|owns(r,owner)));
            if rows(collections,name).iter().filter(|r|owns(r,owner)).collect::<Vec<_>>()!=expected {return Err(fail());}
        }
    }
    for name in ["sources","widths",REACHES] {
        for expected in additions(name) {
            let actual=collections.iter().flat_map(|(collection,records)|records.iter().filter(|r|r["id"]==expected["id"]).map(move|r|(collection.as_str(),r))).collect::<Vec<_>>();
            if actual!=vec![(name,expected)] {return Err(fail());}
        }
    }
    Ok(true)
}
pub(crate) fn validate(bundle:&Bundle)->Result<(),String> {checked(&bundle.collections,&bundle.manifest).map(|_|())}
pub(crate) fn identity_overlay(bundle:&Bundle)->Result<bool,String> {checked(&bundle.collections,&bundle.manifest)}
pub(crate) fn parent_object<'a>(row:&'a Value,manifest:&Value)->&'a Value {
    if !manifest[KEY].is_null() {if let Some(owner)=row["id"].as_str() {if document()["final_objects"].get(owner)==Some(row) {return &document()["prior_owners"][owner]["objects"][0];}}}row
}
pub(crate) fn identity_parent_row<'a>(name:&str,row:&'a Value,enabled:bool)->Option<&'a Value> {
    if enabled {
        if additions(name).contains(row) {return None;}
        if name=="objects" {if let Some(owner)=row["id"].as_str() {if document()["final_objects"].get(owner)==Some(row) {return Some(&document()["prior_owners"][owner]["objects"][0]);}}}
    }Some(row)
}
pub(crate) fn additional_source_count(collections:&BTreeMap<String,Vec<Value>>,manifest:&Value)->Result<usize,String> {Ok(if checked(collections,manifest)? {2}else{0})}
pub(crate) fn validated_widths(bundle:&Bundle)->Result<Vec<Value>,String> {Ok(if identity_overlay(bundle)? {additions("widths").to_vec()}else{vec![]})}
fn scene(widths:Vec<&Value>,reaches:Vec<&Value>,owner:Option<&str>)->Value {
    let Some(first)=reaches.first().or(widths.first()) else {return Value::Null;};
    json!({"kind":"published_current_dimension_evidence","title":if reaches.is_empty(){"Indian SEC: cited upstream width"}else{"Red Sea: reported summer plume reach"},
        "entity_id":owner,"current_id":owner.and_then(|id|id.strip_prefix("current:")),"width_records":widths,"length_records":reaches,"event_records":[],
        "scope":"Each record retains its regional extent, evidence class and source operator. These records do not establish whole-current dimensions, measurement uncertainty or annual extrema.",
        "definition":"Red Sea summer reach: reported 110–120 km using speed and salinity contour support. Indian SEC width: about 650 km cited in the 2008 report; original attribution and methods remain unverified. Separate length and width scales.",
        "source_file":first["source_file"],"source_url":first["source_url"],"source_label":"Original source reporting this claim",
        "figure":"figures/current-core-gap-followup-scoped-dimensions-v1.svg"})
}
pub(crate) fn query_scene(selected:&[&Value],name:&str,bundle:&Bundle)->Value {
    if bundle.manifest[KEY].is_null() {return Value::Null;}
    let selected=selected.iter().copied().filter(|r|additions(name).contains(r)).collect::<Vec<_>>();
    let owners=selected.iter().filter_map(|r|r["entity_id"].as_str()).collect::<BTreeSet<_>>();let owner=if owners.len()==1 {owners.first().copied()}else{None};
    if name==REACHES {scene(vec![],selected,owner)}else{scene(selected,vec![],owner)}
}
fn for_owner(bundle:&Bundle,owner:&str)->Value {
    scene(rows(&bundle.collections,"widths").iter().filter(|r|owns(r,owner)&&additions("widths").contains(r)).collect(),
        rows(&bundle.collections,REACHES).iter().filter(|r|owns(r,owner)&&additions(REACHES).contains(r)).collect(),Some(owner))
}
pub(crate) fn by_current(bundle:&Bundle)->Value {
    let mut result=crate::pacific_sec_jet_widths::by_current(bundle);
    if !bundle.manifest[KEY].is_null() {for owner in document()["citation_owner_ids"].as_array().unwrap().iter().filter_map(Value::as_str) {result[owner.strip_prefix("current:").unwrap()]=for_owner(bundle,owner);}}result
}
pub(crate) fn object_projection(bundle:&Bundle,owner:&str,mut result:Value)->Value {
    if !bundle.manifest[KEY].is_null()&&document()["final_objects"].get(owner).is_some() {result["current_dimension_evidence_scene"]=for_owner(bundle,owner);}result
}
pub(crate) fn dashboard_row(bundle:&Bundle,row:&Value)->Result<Value,String> {
    if bundle.manifest[KEY].is_null() {return Ok(row.clone());}
    let Some(owner)=row["id"].as_str() else {return Ok(row.clone());};let Some(final_row)=document()["final_objects"].get(owner) else {return Ok(row.clone());};let mut result=row.clone();
    for key in ["width_ids","regional_reach_ids","capabilities","source_ids","linked_source_count","section_fingerprints","fingerprint","evidence_links"] {
        if final_row.get(key).is_none() {continue;}
        if row[key]!=document()["prior_owners"][owner]["objects"][0][key] {return Err(format!("Changed preceding scoped dimension dashboard {owner}/{key}"));}result[key]=final_row[key].clone();
    }Ok(result)
}
pub(crate) fn dashboard_document(bundle:&Bundle,mut value:Value)->Result<Value,String> {
    if bundle.manifest[KEY].is_null() {return Ok(value);}
    value["entries"]=json!(value["entries"].as_array().ok_or("Missing dashboard entries")?.iter().map(|r|dashboard_row(bundle,r)).collect::<Result<Vec<_>,_>>()?);
    value["snapshot_fingerprint"]=json!(pin(&format!("osw.current-core-dimensions.v1\n{}\n{}\n",value["snapshot_fingerprint"].as_str().ok_or("Missing dashboard fingerprint")?,pin(RAW))));
    value[KEY]=json!({"width_records_added":1,"regional_reaches_added":1,"publication_sources_added":2,"whole_current_dimensions_added":0});Ok(value)
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture()->Bundle {
        let doc=document();let mut collections=BTreeMap::new();let mut sources=doc["prior_source_inventory"].as_array().unwrap().clone();sources.extend_from_slice(additions("sources"));collections.insert("sources".into(),sources);
        for (owner,prior) in doc["prior_owners"].as_object().unwrap() {
            collections.entry("objects".into()).or_insert_with(Vec::new).push(doc["final_objects"][owner].clone());
            collections.entry("entities".into()).or_insert_with(Vec::new).extend(prior["entities"].as_array().unwrap().clone());
        }
        for name in ["widths",REACHES] {collections.insert(name.into(),additions(name).to_vec());}
        let mut manifest=json!({"input_sha256":doc["input_sha256"]});manifest["input_sha256"][FILE]=json!(pin(RAW));manifest[KEY]=marker();Bundle{schema:"osw.query-bundle.v1".into(),manifest,collections}
    }
    #[test] fn exact_scoped_records_and_parent_objects() {
        let b=fixture();validate(&b).unwrap();assert_eq!(additional_source_count(&b.collections,&b.manifest).unwrap(),2);
        assert_eq!(validated_widths(&b).unwrap().len(),1);
        for (owner,row) in document()["final_objects"].as_object().unwrap() {assert_eq!(parent_object(row,&b.manifest),&document()["prior_owners"][owner]["objects"][0]);}
        assert_eq!(b.collections[REACHES][0]["reported_length_interval_km"],json!([110,120]));assert!(b.collections[REACHES][0]["annual_length_range_km"].is_null());
    }
    #[test] fn missing_misplaced_promoted_inherited_or_duplicate_evidence_refused() {
        for case in 0..8 {let mut b=fixture();match case {
            0=>{b.collections.get_mut(REACHES).unwrap().clear();},
            1=>{b.collections.get_mut(REACHES).unwrap()[0]["rank_eligible"]=json!(true);},
            2=>{b.collections.get_mut("widths").unwrap()[0]["independent_observation_count"]=json!(1);},
            3=>{b.collections.get_mut("widths").unwrap()[0]["entity_id"]=json!("current:south-equatorial");},
            4=>{b.collections.get_mut(REACHES).unwrap()[0]["annual_length_range_km"]=json!([110,130]);},
            5=>{let r=b.collections[REACHES][0].clone();b.collections.insert("wrong".into(),vec![r]);},
            6=>{b.collections.get_mut("sources").unwrap().pop();},
            _=>{b.collections.get_mut("objects").unwrap()[0]["published_length_km"]=json!(115);},
        }assert!(validate(&b).is_err(),"case {case}");}
    }
    #[test] fn query_selection_and_family_do_not_inherit_values() {
        let b=fixture();let reach=&b.collections[REACHES][0];let s=query_scene(&[reach],REACHES,&b);
        assert_eq!(s["length_records"],json!([reach]));assert!(s["width_records"].as_array().unwrap().is_empty());
        assert!(by_current(&b)["south-equatorial"].is_null());assert!(query_scene(&[],REACHES,&b).is_null());
        assert_eq!(by_current(&b)["indian-south-equatorial"]["width_records"].as_array().unwrap().len(),1);
    }
}
