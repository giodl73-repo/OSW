//! Published regional jet widths retain component, nonsynoptic campaign and layer scope.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
use std::sync::OnceLock;

const FILE: &str = "research/pacific-sec-gourdeau-2008-query-contract-v1.json";
const RAW: &str = include_str!("../../../research/pacific-sec-gourdeau-2008-query-contract-v1.json");
const KEY: &str = "published_pacific_sec_jet_widths_v1";
fn pin(raw: &str) -> String { format!("{:x}", Sha256::digest(raw.as_bytes())) }
fn document() -> &'static Value {
    static DOC: OnceLock<Value> = OnceLock::new();
    DOC.get_or_init(|| serde_json::from_str(RAW).expect("compiled Pacific SEC jet-width contract"))
}
fn marker() -> Value {
    json!({"schema":"osw.pacific-sec-jet-widths-runtime.v1","parent_logical_sha256":document()["parent_logical_sha256"],
        "contract_file":FILE,"contract_sha256":pin(RAW),"width_records_added":2,"sources_added":1,
        "width_samples_added":0,"lengths_added":0,"annual_ranges_added":0,"physical_geometries_added":0,
        "independent_observations_added":0})
}
fn rows<'a>(collections: &'a BTreeMap<String,Vec<Value>>, name: &str) -> &'a [Value] {
    collections.get(name).map(Vec::as_slice).unwrap_or(&[])
}
fn owns(row:&Value,owner:&str)->bool {
    row["entity_id"]==owner || owner.strip_prefix("current:").is_some_and(|short| row["current_id"]==short)
}
fn checked(collections:&BTreeMap<String,Vec<Value>>,manifest:&Value)->Result<bool,String> {
    let fail=||"Invalid Pacific SEC regional jet-width extension".to_owned();
    let doc=document();let additions=doc["width_records"].as_array().ok_or_else(fail)?;
    let source=&doc["new_source"];
    let trace=collections.values().flatten().any(|r| r["id"]==source["id"]
        ||r["id"].as_str().is_some_and(|id| id.starts_with("pacific-sec-gourdeau2008-")));
    if manifest[KEY].is_null() && manifest["input_sha256"][FILE].is_null() && !trace {return Ok(false);}
    if manifest[KEY]!=marker() || manifest["input_sha256"][FILE]!=pin(RAW) {return Err(fail());}
    for (path,digest) in doc["input_sha256"].as_object().ok_or_else(fail)? {
        if manifest["input_sha256"][path]!=*digest {return Err(fail());}
    }
    let mut ids=BTreeSet::new();
    for row in rows(collections,"sources") {
        if !row["id"].as_str().is_some_and(|id| !id.is_empty() && ids.insert(id)) {return Err(fail());}
    }
    for expected in doc["prior_source_inventory"].as_array().ok_or_else(fail)?.iter().chain(std::iter::once(source)) {
        if rows(collections,"sources").iter().filter(|r|r["id"]==expected["id"]).collect::<Vec<_>>()!=vec![expected] {return Err(fail());}
    }
    for (owner,prior) in doc["prior_owners"].as_object().ok_or_else(fail)? {
        let object=doc["final_objects"].get(owner).unwrap_or(&prior["objects"][0]);
        if rows(collections,"objects").iter().map(|r|crate::characteristic_velocities::parent_object(r,manifest)).filter(|r|r["id"]==*owner).collect::<Vec<_>>()!=vec![object]
            ||rows(collections,"entities").iter().filter(|r|r["id"]==*owner).collect::<Vec<_>>()
                !=prior["entities"].as_array().ok_or_else(fail)?.iter().collect::<Vec<_>>() {return Err(fail());}
        let mut expected=prior["widths"].as_array().ok_or_else(fail)?.iter().collect::<Vec<_>>();
        expected.extend(additions.iter().filter(|r|owns(r,owner)));
        if rows(collections,"widths").iter().filter(|r|owns(r,owner)).collect::<Vec<_>>()!=expected {return Err(fail());}
    }
    for (name,records) in collections {
        for row in records {
            if row["id"].as_str().is_some_and(|id|id.starts_with("pacific-sec-gourdeau2008-"))
                &&(name!="widths" || !additions.contains(row)) {return Err(fail());}
        }
    }
    for expected in additions {
        if rows(collections,"widths").iter().filter(|r|r["id"]==expected["id"]).collect::<Vec<_>>()!=vec![expected] {return Err(fail());}
    }
    Ok(true)
}
pub(crate) fn validate(bundle:&Bundle)->Result<(),String> {checked(&bundle.collections,&bundle.manifest).map(|_|())}
pub(crate) fn identity_overlay(bundle:&Bundle)->Result<bool,String> {checked(&bundle.collections,&bundle.manifest)}
pub(crate) fn identity_parent_row<'a>(collection:&str,row:&'a Value,enabled:bool)->Option<&'a Value> {
    if enabled {
        if collection=="widths" && document()["width_records"].as_array().unwrap().contains(row) {return None;}
        if collection=="objects" {
            if let Some(owner)=row["id"].as_str() {
                if document()["final_objects"].get(owner)==Some(row) {return Some(&document()["prior_owners"][owner]["objects"][0]);}
            }
        }
    }
    Some(row)
}
pub(crate) fn additional_source_count(collections:&BTreeMap<String,Vec<Value>>,manifest:&Value)->Result<usize,String> {
    Ok(usize::from(checked(collections,manifest)?))
}
pub(crate) fn validated_widths(bundle:&Bundle)->Result<Vec<Value>,String> {
    Ok(if identity_overlay(bundle)? {document()["width_records"].as_array().unwrap().clone()} else {vec![]})
}
fn scene(selected:Vec<&Value>,owner:Option<&str>)->Value {
    if selected.is_empty() {return Value::Null;}
    json!({"kind":"published_current_dimension_evidence","title":"Pacific SEC: regional inflow jet widths",
        "entity_id":owner,"current_id":owner.and_then(|id|id.strip_prefix("current:")),
        "width_records":selected,"event_records":[],
        "scope":"North Vanuatu and North Caledonian regional inflow jets sampled during 17 July–17 October 2005 in the glider 0–600 m layer. Individual crossing dates are unspecified. These component widths are not annual bounds, uncertainty or whole-current widths.",
        "definition":"Author-reported approximate component widths from the July-October 2005 glider campaign. The two jets retain separate scopes; exact edge thresholds, fixed-depth widths, annual bounds and numerical width uncertainty remain unknown.",
        "source_file":"research/pacific-sec-gourdeau-2008-width-source-facts-v1.json",
        "source_url":document()["new_source"]["url"],"source_label":"Original glider study and regional sections",
        "figure":"figures/pacific-sec-gourdeau-2008-regional-widths-v1.svg"})
}
fn relevant(row:&Value)->bool {
    document()["width_records"].as_array().unwrap().iter().any(|r|r["id"]==row["id"])
        ||document()["prior_owners"].as_object().unwrap().values().any(|p|p["widths"].as_array().unwrap().iter().any(|r|r["id"]==row["id"]))
}
pub(crate) fn width_scene(selected:&[&Value],bundle:&Bundle)->Value {
    if bundle.manifest[KEY].is_null() {return Value::Null;}
    let selected=selected.iter().copied().filter(|r|relevant(r)).collect::<Vec<_>>();
    let owners=selected.iter().filter_map(|r|r["current_id"].as_str()).collect::<BTreeSet<_>>();
    let owner=if owners.len()==1 {Some(format!("current:{}",owners.first().unwrap()))} else {None};
    scene(selected,owner.as_deref())
}
pub(crate) fn by_current(bundle:&Bundle)->Value {
    let mut result=crate::atlantic_nec_band_spans::by_current(bundle);
    if !bundle.manifest[KEY].is_null() {
        for owner in document()["citation_owner_ids"].as_array().unwrap().iter().filter_map(Value::as_str) {
            result[owner.strip_prefix("current:").unwrap()]=scene(rows(&bundle.collections,"widths").iter().filter(|r|owns(r,owner)).collect(),Some(owner));
        }
    }
    result
}
pub(crate) fn object_projection(bundle:&Bundle,owner:&str,mut result:Value)->Value {
    if !bundle.manifest[KEY].is_null() && document()["final_objects"].get(owner).is_some() {
        result["current_dimension_evidence_scene"]=scene(rows(&bundle.collections,"widths").iter().filter(|r|owns(r,owner)).collect(),Some(owner));
    }
    result
}
pub(crate) fn dashboard_row(bundle:&Bundle,row:&Value)->Result<Value,String> {
    if bundle.manifest[KEY].is_null() {return Ok(row.clone());}
    let Some(owner)=row["id"].as_str() else {return Ok(row.clone());};
    let Some(final_row)=document()["final_objects"].get(owner) else {return Ok(row.clone());};
    let mut result=row.clone();
    for key in ["width_ids","capabilities","source_ids","linked_source_count","section_fingerprints","fingerprint","evidence_links"] {
        if row[key]!=document()["prior_owners"][owner]["objects"][0][key] {return Err(format!("Changed preceding Pacific SEC dashboard {owner}/{key}"));}
        result[key]=final_row[key].clone();
    }
    Ok(result)
}
pub(crate) fn dashboard_document(bundle:&Bundle,mut value:Value)->Result<Value,String> {
    if bundle.manifest[KEY].is_null() {return Ok(value);}
    value["entries"]=json!(value["entries"].as_array().ok_or("Missing dashboard entries")?.iter()
        .map(|r|dashboard_row(bundle,r)).collect::<Result<Vec<_>,_>>()?);
    value["snapshot_fingerprint"]=json!(pin(&format!("osw.pacific-sec-jet-widths.v1\n{}\n{}\n",value["snapshot_fingerprint"].as_str().ok_or("Missing dashboard fingerprint")?,pin(RAW))));
    value["published_pacific_sec_jet_widths_v1"]=json!({"width_records_added":2,"publication_sources_added":1,"whole_current_dimensions_added":0});
    Ok(value)
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture()->Bundle {
        let doc=document();let mut collections=BTreeMap::new();
        let mut sources=doc["prior_source_inventory"].as_array().unwrap().clone();sources.push(doc["new_source"].clone());collections.insert("sources".into(),sources);
        for (owner,prior) in doc["prior_owners"].as_object().unwrap() {
            collections.entry("objects".into()).or_insert_with(Vec::new).push(doc["final_objects"].get(owner).unwrap_or(&prior["objects"][0]).clone());
            collections.entry("entities".into()).or_insert_with(Vec::new).extend(prior["entities"].as_array().unwrap().clone());
            collections.entry("widths".into()).or_insert_with(Vec::new).extend(prior["widths"].as_array().unwrap().clone());
        }
        collections.get_mut("widths").unwrap().extend(doc["width_records"].as_array().unwrap().clone());
        let mut manifest=json!({"input_sha256":doc["input_sha256"]});manifest["input_sha256"][FILE]=json!(pin(RAW));manifest[KEY]=marker();
        Bundle{schema:"osw.query-bundle.v1".into(),manifest,collections}
    }
    #[test] fn regional_spans_reverse_to_exact_basin_parent() {
        let b=fixture();validate(&b).unwrap();assert_eq!(validated_widths(&b).unwrap().len(),2);
        assert_eq!(additional_source_count(&b.collections,&b.manifest).unwrap(),1);
        for row in document()["width_records"].as_array().unwrap() {
            assert!(identity_parent_row("widths",row,true).is_none());
            assert!(matches!(row["approximate_width_km"].as_u64(),Some(100 | 300)));
            assert!(row["annual_width_range_km"].is_null());
        }
        let owner="current:pacific-south-equatorial";
        assert_eq!(identity_parent_row("objects",&document()["final_objects"][owner],true),Some(&document()["prior_owners"][owner]["objects"][0]));
    }
    #[test] fn corrupted_missing_inherited_or_misplaced_rows_refused() {
        for case in 0..7 {
            let mut b=fixture();let width=b.collections["widths"].last().unwrap().clone();
            match case {
                0=>{b.collections.get_mut("widths").unwrap().pop();},
                1=>{b.collections.get_mut("widths").unwrap().last_mut().unwrap()["approximate_width_km"]=json!(1400);},
                2=>{b.collections.get_mut("widths").unwrap().last_mut().unwrap()["annual_width_range_km"]=json!([100,300]);},
                3=>{b.collections.insert("wrong_collection".into(),vec![width]);},
                4=>{b.collections.get_mut("widths").unwrap().last_mut().unwrap()["entity_id"]=json!("current:south-equatorial");},
                5=>{b.collections.get_mut("sources").unwrap().pop();},
                _=>{b.collections.get_mut("widths").unwrap().last_mut().unwrap()["seasonal_playback_eligible"]=json!(true);},
            }
            assert!(validate(&b).is_err(),"case {case}");
        }
    }
    #[test] fn pagination_and_family_do_not_expand_jet_evidence() {
        let b=fixture();let row=b.collections["widths"].last().unwrap();let result=width_scene(&[row],&b);
        assert_eq!(result["width_records"],json!([row]));assert!(result["event_records"].as_array().unwrap().is_empty());
        assert_eq!(by_current(&b)["pacific-south-equatorial"]["width_records"].as_array().unwrap().len(),2);
        assert!(by_current(&b)["south-equatorial"].is_null());assert!(width_scene(&[],&b).is_null());
    }
}
