//! Source-selected map velocities retain their distinct operators and time support.
use crate::Bundle;
use serde_json::{Value,json};
use sha2::{Digest,Sha256};
use std::collections::{BTreeMap,BTreeSet};
use std::sync::OnceLock;
const FILE:&str="research/richardson-walsh-1986-characteristic-velocity-query-contract-v1.json";
const RAW:&str=include_str!("../../../research/richardson-walsh-1986-characteristic-velocity-query-contract-v1.json");
const KEY:&str="published_characteristic_velocities_v1";
const COLLECTION:&str="current_characteristic_velocities";
fn pin(raw:&str)->String{format!("{:x}",Sha256::digest(raw.as_bytes()))}
fn document()->&'static Value{static DOC:OnceLock<Value>=OnceLock::new();DOC.get_or_init(||serde_json::from_str(RAW).expect("compiled characteristic velocity contract"))}
fn rows<'a>(collections:&'a BTreeMap<String,Vec<Value>>,name:&str)->&'a [Value]{collections.get(name).map(Vec::as_slice).unwrap_or(&[])}
fn marker()->Value{json!({"schema":"osw.characteristic-velocities-runtime.v1","parent_logical_sha256":document()["parent_logical_sha256"],"contract_file":FILE,"contract_sha256":pin(RAW),"collection":COLLECTION,"records_added":10,"sources_added":1,"collections_added":1,"lengths_added":0,"widths_added":0,"annual_ranges_added":0,"physical_geometries_added":0,"independent_observations_added":0})}
fn checked(collections:&BTreeMap<String,Vec<Value>>,manifest:&Value)->Result<bool,String>{
    let fail=||"Invalid characteristic current velocity extension".to_owned();let doc=document();
    let source=&doc["new_source"];let expected=doc["records"].as_array().ok_or_else(fail)?;
    let trace=collections.contains_key(COLLECTION)||collections.values().flatten().any(|r|r["id"]==source["id"]||r["id"].as_str().is_some_and(|id|id.starts_with("richardson-walsh1986-table1-")))||rows(collections,"objects").iter().any(|r|!r["characteristic_velocity_ids"].is_null());
    if manifest[KEY].is_null()&&manifest["input_sha256"][FILE].is_null()&&!trace{return Ok(false);}
    if manifest[KEY]!=marker()||manifest["input_sha256"][FILE]!=pin(RAW)||rows(collections,COLLECTION)!=expected.as_slice(){return Err(fail());}
    for(path,digest)in doc["input_sha256"].as_object().ok_or_else(fail)?{if manifest["input_sha256"][path]!=*digest{return Err(fail());}}
    let mut ids=BTreeSet::new();for row in rows(collections,"sources"){if !row["id"].as_str().is_some_and(|id|!id.is_empty()&&ids.insert(id)){return Err(fail());}}
    for expected in doc["prior_source_inventory"].as_array().ok_or_else(fail)?.iter().chain(std::iter::once(source)){if rows(collections,"sources").iter().filter(|r|r["id"]==expected["id"]).collect::<Vec<_>>()!=vec![expected]{return Err(fail());}}
    for(owner,prior)in doc["prior_owners"].as_object().ok_or_else(fail)?{
        let object=doc["final_objects"].get(owner).unwrap_or(&prior["objects"][0]);
        if rows(collections,"objects").iter().map(|r|crate::atlantic_nsec_reference::parent_object(r,manifest)).filter(|r|r["id"]==*owner).collect::<Vec<_>>()!=vec![object]
            ||rows(collections,"entities").iter().filter(|r|r["id"]==*owner).collect::<Vec<_>>() !=prior["entities"].as_array().ok_or_else(fail)?.iter().collect::<Vec<_>>(){return Err(fail());}
        if rows(collections,"widths").iter().filter(|r|r["entity_id"]==*owner||r["current_id"]==owner.strip_prefix("current:").unwrap_or("")).collect::<Vec<_>>() !=prior["widths"].as_array().ok_or_else(fail)?.iter().collect::<Vec<_>>(){return Err(fail());}
    }
    for(name,records)in collections{for row in records{if row["id"].as_str().is_some_and(|id|id.starts_with("richardson-walsh1986-table1-"))&&(name!=COLLECTION||!expected.contains(row)){return Err(fail());}}}
    for row in rows(collections,"objects"){
        if !row["characteristic_velocity_ids"].is_null()&&doc["final_objects"].get(row["id"].as_str().unwrap_or("")).is_none(){return Err(fail());}
    }
    Ok(true)
}
pub(crate)fn validate(bundle:&Bundle)->Result<(),String>{checked(&bundle.collections,&bundle.manifest).map(|_|())}
pub(crate)fn additional_source_count(collections:&BTreeMap<String,Vec<Value>>,manifest:&Value)->Result<usize,String>{Ok(usize::from(checked(collections,manifest)?))}
pub(crate)fn identity_overlay(bundle:&Bundle)->Result<bool,String>{checked(&bundle.collections,&bundle.manifest)}
// Older validators compare their exact preceding object; the new full validator remains mandatory.
pub(crate)fn parent_object<'a>(row:&'a Value,manifest:&Value)->&'a Value{
    let row=crate::atlantic_nsec_reference::parent_object(row,manifest);
    if !manifest[KEY].is_null(){if let Some(owner)=row["id"].as_str(){if document()["final_objects"].get(owner)==Some(row){return &document()["prior_owners"][owner]["objects"][0];}}}row
}
pub(crate)fn identity_parent_row<'a>(name:&str,row:&'a Value,enabled:bool)->Option<&'a Value>{
    if enabled{if name==COLLECTION&&document()["records"].as_array().unwrap().contains(row){return None;}
        if name=="objects"{if let Some(owner)=row["id"].as_str(){if document()["final_objects"].get(owner)==Some(row){return Some(&document()["prior_owners"][owner]["objects"][0]);}}}}
    Some(row)
}
pub(crate)fn scene(selected:&[&Value])->Value{
    if selected.is_empty(){return Value::Null;}
    json!({"kind":"published_characteristic_current_velocities","title":"Tropical Atlantic: characteristic velocity summaries","scope":"Author-selected characteristic values from spatially varying ship-drift maps. Mean-vector speed, seasonal variation and harmonic amplitudes are distinct quantities; these are not whole-current averages or annual extrema.","records":selected,"source_file":"research/richardson-walsh-1986-characteristic-velocity-source-facts-v1.json","source_url":document()["new_source"]["url"],"figure":"figures/richardson-walsh-1986-characteristic-velocities-v1.svg","time_support":"Historical observations1875–1976, strongly weighted toward1920–1940; fixed sampling depth unknown.","operator_note":"Seasonal variation: sqrt(mean(u_prime^2)+mean(v_prime^2)). Harmonic amplitude, as printed:0.5*sqrt(A_x^2+A_y^2). Phases and monthly series are not supplied by Table1.","unknowns":"Annual extrema, numerical uncertainty and monthly velocity series: unknown. No geometry or independent observations added."})
}
pub(crate)fn by_current(bundle:&Bundle)->Value{
    let mut result=crate::published_current_speeds::by_current(bundle);
    if !bundle.manifest[KEY].is_null(){for owner in document()["citation_owner_ids"].as_array().unwrap().iter().filter_map(Value::as_str){let short=owner.strip_prefix("current:").unwrap();let selected=rows(&bundle.collections,COLLECTION).iter().filter(|r|r["entity_id"]==owner).collect::<Vec<_>>();let next=scene(&selected);let prior=result[short].clone();result[short]=if prior.is_null(){next}else{json!({"kind":"published_velocity_evidence_groups","title":"Published velocity evidence with separate methods","scope":"Preserve characteristic map summaries and seasonal core estimates as separate evidence; shared source populations are not independent observations.","scenes":[prior,next]})};}}
    result
}
pub(crate)fn object_projection(bundle:&Bundle,owner:&str,mut result:Value)->Value{
    if !bundle.manifest[KEY].is_null(){let selected=rows(&bundle.collections,COLLECTION).iter().filter(|r|r["entity_id"]==owner).collect::<Vec<_>>();if !selected.is_empty(){result["collections"][COLLECTION]=json!(selected);result["characteristic_velocity_scene"]=scene(&selected);}}
    result
}
pub(crate)fn dashboard_row(bundle:&Bundle,row:&Value)->Result<Value,String>{
    if bundle.manifest[KEY].is_null(){return Ok(row.clone());}let Some(owner)=row["id"].as_str()else{return Ok(row.clone());};let Some(final_row)=document()["final_objects"].get(owner)else{return Ok(row.clone());};let mut result=row.clone();
    for key in ["characteristic_velocity_ids","capabilities","source_ids","linked_source_count","section_fingerprints","fingerprint","evidence_links"]{if row[key]!=document()["prior_owners"][owner]["objects"][0][key]{return Err(format!("Changed preceding characteristic-velocity dashboard {owner}/{key}"));}result[key]=final_row[key].clone();}Ok(result)
}
pub(crate)fn dashboard_document(bundle:&Bundle,mut value:Value)->Result<Value,String>{
    if bundle.manifest[KEY].is_null(){return Ok(value);}
    value["entries"]=json!(value["entries"].as_array().ok_or("Missing dashboard entries")?.iter().map(|r|dashboard_row(bundle,r)).collect::<Result<Vec<_>,_>>()?);
    value["snapshot_fingerprint"]=json!(pin(&format!("osw.characteristic-velocities.v1\n{}\n{}\n",value["snapshot_fingerprint"].as_str().ok_or("Missing dashboard fingerprint")?,pin(RAW))));
    value["published_characteristic_velocities_v1"]=json!({"records_added":10,"publication_sources_added":1,"whole_current_dimensions_added":0});Ok(value)
}

#[cfg(test)]mod tests{
    use super::*;
    fn fixture()->Bundle{let doc=document();let mut collections=BTreeMap::new();let mut sources=doc["prior_source_inventory"].as_array().unwrap().clone();sources.push(doc["new_source"].clone());collections.insert("sources".into(),sources);for(owner,prior)in doc["prior_owners"].as_object().unwrap(){collections.entry("objects".into()).or_insert_with(Vec::new).push(doc["final_objects"].get(owner).unwrap_or(&prior["objects"][0]).clone());collections.entry("entities".into()).or_insert_with(Vec::new).extend(prior["entities"].as_array().unwrap().clone());collections.entry("widths".into()).or_insert_with(Vec::new).extend(prior["widths"].as_array().unwrap().clone());}collections.insert(COLLECTION.into(),doc["records"].as_array().unwrap().clone());let mut manifest=json!({"input_sha256":doc["input_sha256"]});manifest["input_sha256"][FILE]=json!(pin(RAW));manifest[KEY]=marker();Bundle{schema:"osw.query-bundle.v1".into(),manifest,collections}}
    #[test]fn typed_summaries_and_exact_prior_objects(){let b=fixture();validate(&b).unwrap();assert_eq!(additional_source_count(&b.collections,&b.manifest).unwrap(),1);for row in &b.collections[COLLECTION]{assert!(identity_parent_row(COLLECTION,row,true).is_none());assert!(row["annual_speed_extrema"].is_null());}let owner="current:atlantic-north-equatorial";assert_eq!(parent_object(&document()["final_objects"][owner],&b.manifest),&document()["prior_owners"][owner]["objects"][0]);}
    #[test]fn corruption_inheritance_and_false_series_refused(){for case in 0..6{let mut b=fixture();match case{0=>{b.collections.get_mut(COLLECTION).unwrap().pop();},1=>{b.collections.get_mut(COLLECTION).unwrap()[0]["characteristic_mean_vector_speed_m_s"]=json!(99);},2=>{b.collections.get_mut(COLLECTION).unwrap()[0]["annual_speed_extrema"]=json!([0.3,0.4]);},3=>{b.collections.get_mut(COLLECTION).unwrap()[0]["entity_id"]=json!("current:north-equatorial");},4=>{b.collections.get_mut(COLLECTION).unwrap()[0]["monthly_speed_playback_eligible"]=json!(true);},_=>{b.collections.get_mut("sources").unwrap().pop();}}assert!(validate(&b).is_err(),"case {case}");}}
    #[test]fn filtered_scene_and_prior_velocity_operator_remain_distinct(){let b=fixture();let all=b.collections[COLLECTION].iter().collect::<Vec<_>>();assert_eq!(scene(&all)["records"].as_array().unwrap().len(),10);assert_eq!(scene(&[all[6]])["records"].as_array().unwrap().len(),1);assert!(scene(&[]).is_null());let map=by_current(&b);assert!(map["north-equatorial"].is_null());assert_eq!(map["atlantic-south-equatorial"]["records"].as_array().unwrap().len(),3);}
}
