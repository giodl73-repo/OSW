//! Two regional NEC drawings and source-plot core migration retain distinct quantities.
use crate::Bundle;
use serde_json::{Value,json};
use sha2::{Digest,Sha256};
use std::collections::{BTreeMap,BTreeSet};
use std::sync::OnceLock;

const FILE:&str="research/current-reference-profile-batch-query-contract-v1.json";
const RAW:&str=include_str!("../../../research/current-reference-profile-batch-query-contract-v1.json");
const KEY:&str="current_reference_profile_batch_v1";
pub(crate)const COLLECTION:&str="current_core_migration_profiles";
const NEC:&str="current:atlantic-north-equatorial";
const SEC:&str="current:pacific-south-equatorial";
fn pin(raw:&str)->String{format!("{:x}",Sha256::digest(raw.as_bytes()))}
fn doc()->&'static Value{static DOC:OnceLock<Value>=OnceLock::new();DOC.get_or_init(||serde_json::from_str(RAW).expect("compiled regional reference/profile contract"))}
fn rows<'a>(c:&'a BTreeMap<String,Vec<Value>>,name:&str)->&'a[Value]{c.get(name).map(Vec::as_slice).unwrap_or(&[])}
fn owns(row:&Value,owner:&str)->bool{row["entity_id"]==owner||row["current_id"]==owner.strip_prefix("current:").unwrap_or("")}
fn additions(name:&str)->&'static[Value]{match name{"reference_routes"=>doc()["routes"].as_array().unwrap(),"sources"=>doc()["new_sources"].as_array().unwrap(),COLLECTION=>doc()["records"].as_array().unwrap(),_=>&[]}}
fn marker()->Value{json!({"schema":"osw.current-reference-profile-batch-runtime.v1","parent_logical_sha256":doc()["parent_logical_sha256"],"contract_file":FILE,"contract_sha256":pin(RAW),"reference_routes_added":2,"profile_records_added":24,"collection":COLLECTION,"sources_added":3,"collections_added":1,"whole_current_lengths_added":0,"widths_added":0,"annual_ranges_added":0,"physical_geometries_added":0,"independent_observations_added":0})}
fn checked(c:&BTreeMap<String,Vec<Value>>,m:&Value)->Result<bool,String>{
    crate::validation_scope::checked(c,m,module_path!(),||checked_uncached(c,m))
}
fn checked_uncached(c:&BTreeMap<String,Vec<Value>>,m:&Value)->Result<bool,String>{
    let fail=||"Invalid source-bound regional reference/core-migration batch".to_owned();
    let trace=c.contains_key(COLLECTION)||c.values().flatten().any(|r|["reference_routes","sources",COLLECTION].iter().any(|name|additions(name).iter().any(|x|x["id"]==r["id"])));
    if m[KEY].is_null()&&m["input_sha256"][FILE].is_null()&&!trace{return Ok(false);}
    if m[KEY]!=marker()||m["input_sha256"][FILE]!=pin(RAW){return Err(fail());}
    for(p,h)in doc()["input_sha256"].as_object().ok_or_else(fail)?{if m["input_sha256"][p]!=*h{return Err(fail());}}
    if rows(c,COLLECTION)!=additions(COLLECTION){return Err(fail());}
    for(owner,prior)in doc()["prior_owners"].as_object().ok_or_else(fail)?{
        if rows(c,"objects").iter().filter(|r|r["id"]==*owner).collect::<Vec<_>>()!=vec![&doc()["final_objects"][owner]]
            ||rows(c,"entities").iter().filter(|r|r["id"]==*owner).collect::<Vec<_>>()!=prior["entities"].as_array().ok_or_else(fail)?.iter().collect::<Vec<_>>(){return Err(fail());}
        for name in ["widths","length_assessments","reference_routes"]{
            let expected=if owner==NEC&&name=="reference_routes"{additions(name)}else{prior[name].as_array().ok_or_else(fail)?.as_slice()};
            if rows(c,name).iter().filter(|r|owns(r,owner)).collect::<Vec<_>>()!=expected.iter().collect::<Vec<_>>(){return Err(fail());}
        }
    }
    if rows(c,"route_decisions").iter().filter(|r|r["id"]==doc()["prior_decision"]["id"]).collect::<Vec<_>>()!=vec![&doc()["final_decision"]]{return Err(fail());}
    let mut ids=BTreeSet::new();for r in rows(c,"sources"){if !r["id"].as_str().is_some_and(|id|ids.insert(id)){return Err(fail());}}
    for expected in doc()["prior_source_inventory"].as_array().ok_or_else(fail)?.iter().chain(std::iter::once(&doc()["prior_publication"])).chain(additions("sources")){
        if rows(c,"sources").iter().filter(|r|r["id"]==expected["id"]).collect::<Vec<_>>()!=vec![expected]{return Err(fail());}
    }
    for name in ["reference_routes","sources",COLLECTION]{for expected in additions(name){
        let found=c.iter().flat_map(|(n,rs)|rs.iter().filter(|r|r["id"]==expected["id"]).map(move|r|(n.as_str(),r))).collect::<Vec<_>>();
        if found!=vec![(name,expected)]{return Err(fail());}
    }}
    Ok(true)
}
pub(crate)fn validate(b:&Bundle)->Result<(),String>{checked(&b.collections,&b.manifest).map(|_|())}
pub(crate)fn active(b:&Bundle)->Result<bool,String>{checked(&b.collections,&b.manifest)}
pub(crate)fn additional_source_count(c:&BTreeMap<String,Vec<Value>>,m:&Value)->Result<usize,String>{Ok(if checked(c,m)?{3}else{0})}
pub(crate)fn additional_reference_route_count(c:&BTreeMap<String,Vec<Value>>,m:&Value)->Result<usize,String>{Ok(if checked(c,m)?{2}else{0})}
pub(crate)fn validated_routes(b:&Bundle)->Result<Vec<Value>,String>{Ok(if active(b)?{additions("reference_routes").to_vec()}else{vec![]})}
pub(crate)fn parent_object<'a>(row:&'a Value,m:&Value)->&'a Value{
    if !m[KEY].is_null(){if let Some(owner)=row["id"].as_str(){if doc()["final_objects"].get(owner)==Some(row){return &doc()["prior_owners"][owner]["objects"][0];}}}row
}
pub(crate)fn identity_parent_row<'a>(name:&str,row:&'a Value,enabled:bool)->Option<&'a Value>{
    if enabled{
        if additions(name).contains(row){return None;}
        if name=="objects"{if let Some(owner)=row["id"].as_str(){if doc()["final_objects"].get(owner)==Some(row){return Some(&doc()["prior_owners"][owner]["objects"][0]);}}}
        if name=="route_decisions"&&row==&doc()["final_decision"]{return Some(&doc()["prior_decision"]);}
    }Some(row)
}
pub(crate)fn planning_source(record:&Value,c:&BTreeMap<String,Vec<Value>>,m:&Value)->Result<Option<&'static str>,String>{
    Ok(if record["entity_id"]==NEC&&checked(c,m)?{Some("research/atlantic-nec-schematic-reference-reaches-prepared-v1.json")}else{None})
}
pub(crate)fn scene(selected:&[&Value])->Value{
    if selected.is_empty(){return Value::Null;}
    json!({"kind":"published_core_migration_profiles","title":"Pacific SEC: core movement by depth","records":selected,
        "scope":"Regional southern-branch core migration in two longitude sections. Source-plot readings of1960-2020 change; no annual series or exact endpoint displacement inferred.",
        "operator_note":"Reading intervals are pixel-pick allowances, not confidence intervals. Underlying IAP field is1degree; plot precision adds no physical resolution. No current length, width, footprint or monthly animation is established.",
        "source_url":"https://doi.org/10.1186/s40562-025-00393-7","figure":"figures/pacific-sec-sun-2025-core-migration-profile-v1.svg","compact_figure":"figures/pacific-sec-sun-2025-core-migration-profile-compact-v1.svg"})
}
pub(crate)fn by_current(b:&Bundle)->Value{
    let mut out=json!({});if !b.manifest[KEY].is_null(){out["pacific-south-equatorial"]=scene(&rows(&b.collections,COLLECTION).iter().collect::<Vec<_>>());}out
}
pub(crate)fn object_projection(b:&Bundle,owner:&str,mut value:Value)->Value{
    if !b.manifest[KEY].is_null()&&owner==SEC{value["core_migration_scene"]=scene(&rows(&b.collections,COLLECTION).iter().collect::<Vec<_>>());}value
}
pub(crate)fn dashboard_row(b:&Bundle,row:&Value)->Result<Value,String>{
    if b.manifest[KEY].is_null(){return Ok(row.clone());}
    let Some(owner)=row["id"].as_str() else{return Ok(row.clone())};let Some(expected)=doc()["final_objects"].get(owner) else{return Ok(row.clone())};
    let mut value=row.clone();
    for key in ["route_ids","route_url","core_migration_profile_ids","capabilities","map_features","evidence_links","source_ids","linked_source_count","section_fingerprints","fingerprint"]{
        if expected.get(key).is_none(){continue;}
        if row[key]!=doc()["prior_owners"][owner]["objects"][0][key]{return Err(format!("Changed preceding reference/profile dashboard {owner}/{key}"));}
        value[key]=expected[key].clone();
    }Ok(value)
}
pub(crate)fn dashboard_document(b:&Bundle,mut value:Value)->Result<Value,String>{
    if b.manifest[KEY].is_null(){return Ok(value);}
    value["entries"]=json!(value["entries"].as_array().ok_or("Missing dashboard entries")?.iter().map(|r|dashboard_row(b,r)).collect::<Result<Vec<_>,_>>()?);
    value["snapshot_fingerprint"]=json!(pin(&format!("osw.reference-profiles.v1\n{}\n{}",value["snapshot_fingerprint"].as_str().ok_or("Missing dashboard fingerprint")?,pin(RAW))));Ok(value)
}
pub(crate)fn catalogue_projection(b:&Bundle,mut catalog:Value)->Result<Value,String>{
    if !active(b)?{return Ok(catalog);}
    let fail=||"Invalid NEC interior atlas projection".to_owned();
    let candidates=catalog["candidates"].as_array_mut().ok_or_else(fail)?;
    if candidates.iter().any(|r|owns(r,NEC)){return Err(fail());}
    for route in additions("reference_routes"){
        let mut entry=route.clone();entry["candidate_file"]=route["source_file"].clone();entry["candidate_sha256"]=route["source_file_sha256"].clone();entry["figure"]=route["figure_file"].clone();
        entry["route_extent_kind"]=json!("interior NEC schematic reference");
        let bounds=route["editorial_probe_length_range_km"].as_array().ok_or_else(fail)?;
        entry["scenario_range_km"]=json!([100.0*(bounds[0].as_f64().ok_or_else(fail)?/100.0).floor(),100.0*(bounds[1].as_f64().ok_or_else(fail)?/100.0).ceil()]);
        entry["nominal_atlas_state_crossings"]=json!([]);entry["state_intersection_status"]=json!("unassessed_no_physical_join_admitted");
        entry["remaining_gates"]=json!(["Whole-current endpoints and the other parallel NEC flows remain unresolved.","No annual range, physical axis, width or seasonal playback is established."]);
        let mut report=entry.clone();report["figure_aspect_ratio"]=json!(0.65);report["source_citation"]=json!("Stramma and Schott1999, Figure4");report["coordinate_selection"]=json!("Rounded OSW waypoints adjacent to the NEC schematic label between selected30W and55W gates; not digitized velocity cores.");
        report["scenario_rule"]=route["editorial_probe_interpretation"].clone();report["method"]=json!("WGS84 shortest-geodesic segment sums;18 drawing/gate cases per phase.");
        report["map_land_check"]=json!("All36 cases clear both source-bound land masks under at-most1km geodesic sampling. No physical current footprint established.");report["nasa_movie_context"]=json!([]);report["rendering_role"]=json!("derived_inline_editorial_reach_card_not_additional_observation");entry["report_inline"]=report;candidates.push(entry);
    }
    let plans=catalog["remaining_current_decisions"].as_array_mut().ok_or_else(fail)?;
    let matches=plans.iter().enumerate().filter(|(_,r)|r["current_id"]=="atlantic-north-equatorial").map(|(i,_)|i).collect::<Vec<_>>();
    if matches.len()!=1||plans[matches[0]]!=doc()["prior_decision"]["source_decision"]{return Err(fail());}
    plans[matches[0]]=doc()["final_decision"]["source_decision"].clone();
    for(key,delta)in [("route_candidates",2),("studied_reach_candidates",2),("currents_with_route_candidates",1),("currents_without_route_candidates",-1),("currents_without_any_reference_card",-1)]{
        catalog["counts"][key]=json!(catalog["counts"][key].as_i64().and_then(|v|v.checked_add(delta)).filter(|v|*v>=0).ok_or_else(fail)?);
    }
    let strategies=catalog["planning_taxonomy"]["strategies"].as_array_mut().ok_or_else(fail)?;
    let matches=strategies.iter().enumerate().filter(|(_,r)|r["id"]==doc()["final_decision"]["strategy_id"]).map(|(i,_)|i).collect::<Vec<_>>();
    if matches.len()!=1{return Err(fail());}
    let strategy=&mut strategies[matches[0]];strategy["unbuilt_count"]=json!(strategy["unbuilt_count"].as_u64().and_then(|v|v.checked_sub(1)).ok_or_else(fail)?);Ok(catalog)
}

#[cfg(test)]mod tests{
    use super::*;
    fn fixture()->Bundle{
        let mut c=BTreeMap::new();for name in ["objects","entities","widths","length_assessments","reference_routes"]{c.insert(name.into(),vec![]);}
        for(owner,prior)in doc()["prior_owners"].as_object().unwrap(){c.get_mut("objects").unwrap().push(doc()["final_objects"][owner].clone());for name in ["entities","widths","length_assessments"]{c.get_mut(name).unwrap().extend(prior[name].as_array().unwrap().clone());}if owner!=NEC{c.get_mut("reference_routes").unwrap().extend(prior["reference_routes"].as_array().unwrap().clone());}}
        c.get_mut("reference_routes").unwrap().extend(additions("reference_routes").to_vec());c.insert(COLLECTION.into(),additions(COLLECTION).to_vec());c.insert("route_decisions".into(),vec![doc()["final_decision"].clone()]);
        let mut sources=doc()["prior_source_inventory"].as_array().unwrap().clone();sources.push(doc()["prior_publication"].clone());sources.extend(additions("sources").to_vec());c.insert("sources".into(),sources);
        let mut m=json!({"input_sha256":doc()["input_sha256"]});m["input_sha256"][FILE]=json!(pin(RAW));m[KEY]=marker();Bundle{schema:"osw.query-bundle.v1".into(),collections:c,manifest:m}
    }
    #[test]fn exact_batch_retains_operators_and_parent_projection(){let b=fixture();validate(&b).unwrap();assert_eq!(additional_source_count(&b.collections,&b.manifest).unwrap(),3);assert_eq!(validated_routes(&b).unwrap().len(),2);for owner in [NEC,SEC]{assert_eq!(parent_object(&doc()["final_objects"][owner],&b.manifest),&doc()["prior_owners"][owner]["objects"][0]);}}
    #[test]fn missing_changed_misplaced_inherited_or_promoted_rows_refused(){for case in 0..9{let mut b=fixture();match case{0=>{b.collections.get_mut(COLLECTION).unwrap().pop();},1=>{b.collections.get_mut(COLLECTION).unwrap()[0]["approximate_migration_degrees"]=json!(99);},2=>{b.collections.get_mut(COLLECTION).unwrap()[0]["plot_reading_interval_is_measurement_uncertainty"]=json!(true);},3=>{b.collections.get_mut(COLLECTION).unwrap()[0]["entity_id"]=json!("current:south-equatorial");},4=>{b.collections.get_mut("reference_routes").unwrap().last_mut().unwrap()["rank_eligible"]=json!(true);},5=>{let r=b.collections[COLLECTION][0].clone();b.collections.insert("wrong".into(),vec![r]);},6=>{b.collections.get_mut("sources").unwrap().pop();},7=>{b.collections.get_mut(COLLECTION).unwrap()[0]["geometry"]=json!({"type":"Point","coordinates":[-170,-20]});},_=>{b.manifest.as_object_mut().unwrap().remove(KEY);}}assert!(validate(&b).is_err(),"case {case}");}}
    #[test]fn query_scene_filters_and_families_do_not_inherit(){let b=fixture();let one=scene(&[&b.collections[COLLECTION][0]]);assert_eq!(one["records"].as_array().unwrap().len(),1);assert!(scene(&[]).is_null());assert!(by_current(&b)["south-equatorial"].is_null());assert!(by_current(&b)["atlantic-north-equatorial"].is_null());assert!(b.collections[COLLECTION].iter().any(|r|r["interval_includes_zero"]==true));}
    #[test]fn stripped_namespace_and_duplicate_publication_refused(){let mut b=fixture();b.manifest["input_sha256"].as_object_mut().unwrap().remove(FILE);assert!(validate(&b).is_err());let mut b=fixture();b.collections.get_mut("sources").unwrap().push(doc()["prior_publication"].clone());assert!(validate(&b).is_err());}
}
