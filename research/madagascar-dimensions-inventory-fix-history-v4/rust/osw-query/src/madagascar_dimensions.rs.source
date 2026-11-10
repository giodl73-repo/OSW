//! Regional width summaries and dated examples are not a seasonal dimension series.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
use std::sync::OnceLock;

pub(crate) const COLLECTION: &str = "current_reported_flow_events";
const FILE: &str = "research/madagascar-dimensions-query-contract-v1.json";
const RAW: &str = include_str!("../../../research/madagascar-dimensions-query-contract-v1.json");
const KEY: &str = "published_madagascar_dimensions_v1";
const OWNER: &str = "current:southern-east-madagascar";
const CURRENT: &str = "southern-east-madagascar";
const SOURCE: &str = "source:ponsoni-emc-2016-inatex";
fn pin(raw: &str) -> String { format!("{:x}", Sha256::digest(raw.as_bytes())) }
fn document() -> &'static Value {
    static DOC: OnceLock<Value> = OnceLock::new();
    DOC.get_or_init(|| serde_json::from_str(RAW).expect("compiled Madagascar evidence contract"))
}
fn marker() -> Value {
    json!({"schema":"osw.madagascar-dimensions-runtime-receipt.v1","parent_logical_sha256":document()["parent_logical_sha256"],
        "contract_file":FILE,"contract_sha256":pin(RAW),"width_records_added":1,"flow_event_references_added":8,
        "publication_sources_added":1,"new_width_samples":0,"new_independent_observations":0})
}
fn title(value:&Value)->String {
    value.as_str().unwrap_or("").chars().filter(char::is_ascii_alphanumeric).flat_map(char::to_lowercase).collect()
}
fn doi(value:&Value)->String {
    let text=value.as_str().unwrap_or("").trim().to_lowercase();
    let text=text.split(['?','#']).next().unwrap_or("");
    for prefix in ["https://doi.org/","http://doi.org/","https://dx.doi.org/","http://dx.doi.org/","doi:"] {
        if let Some(tail)=text.strip_prefix(prefix) {return tail.trim().trim_end_matches('/').into();}
    }
    if let Some((_,tail))=text.split_once("/doi/") {
        return ["full/","abs/","epdf/","pdf/"].iter().find_map(|p|tail.strip_prefix(*p)).unwrap_or(tail).trim_end_matches('/').into();
    }
    text.trim_end_matches('/').into()
}
fn active(collections:&BTreeMap<String,Vec<Value>>,manifest:&Value)->Result<bool,String> {
    let fail=||"Invalid Madagascar regional dimension evidence".to_owned();
    let rows=|name:&str|collections.get(name).map(Vec::as_slice).unwrap_or(&[]);
    let doc=document();
    let trace=rows("sources").iter().any(|r|r["id"]==SOURCE)
        ||rows("objects").iter().any(|r|!r["reported_flow_event_ids"].is_null())
        ||rows("widths").iter().any(|r|r["id"]==doc["width_record"]["id"]);
    if manifest[KEY].is_null() && !collections.contains_key(COLLECTION) && !trace && manifest["input_sha256"][FILE].is_null() {return Ok(false);}
    if manifest[KEY]!=marker() || manifest["input_sha256"][FILE]!=pin(RAW)
        ||rows(COLLECTION)!=doc["event_records"].as_array().ok_or_else(fail)?.as_slice() {return Err(fail());}
    for (path,digest) in doc["input_sha256"].as_object().ok_or_else(fail)? {
        if manifest["input_sha256"][path]!=*digest {return Err(fail());}
    }
    if rows("sources").iter().filter(|r|r["id"]==SOURCE).collect::<Vec<_>>()!=vec![&doc["new_source"]] {return Err(fail());}
    let mut ids=BTreeSet::new();
    for source in rows("sources") {
        let id=source["id"].as_str().ok_or_else(fail)?;
        if id.is_empty() ||!ids.insert(id) {return Err(fail());}
        if id!=SOURCE && (doi(&source["doi"])=="10.1175/jpo-d-15-0154.1"
            ||doi(&source["url"])=="10.1175/jpo-d-15-0154.1"
            ||title(&source["title"])==title(&doc["new_source"]["title"])
            ||title(&source["label"])==title(&doc["new_source"]["title"])) {return Err(fail());}
    }
    for source in doc["prior_records"]["owner_sources"].as_array().ok_or_else(fail)? {
        if rows("sources").iter().find(|r|r["id"]==source["id"])!=Some(source) {return Err(fail());}
    }
    if rows("objects").iter().filter(|r|r["id"]==OWNER).collect::<Vec<_>>()!=vec![&doc["final_owner"]]
        ||rows("entities").iter().filter(|r|r["id"]==OWNER).collect::<Vec<_>>()!=vec![&doc["prior_records"]["entity"]]
        ||rows("objects").iter().any(|r|r["id"]!=OWNER&&!r["reported_flow_event_ids"].is_null()) {return Err(fail());}
    let mut expected_widths=doc["prior_records"]["widths"].as_array().ok_or_else(fail)?.iter().collect::<Vec<_>>();
    expected_widths.push(&doc["width_record"]);
    if rows("widths").iter().filter(|r|r["current_id"]==CURRENT).collect::<Vec<_>>()!=expected_widths
        ||rows("widths").iter().filter(|r|r["id"]==doc["width_record"]["id"]).count()!=1
        ||rows("reference_routes").iter().filter(|r|r["current_id"]==CURRENT).collect::<Vec<_>>()
            !=doc["prior_records"]["reference_routes"].as_array().ok_or_else(fail)?.iter().collect::<Vec<_>>() {return Err(fail());}
    Ok(true)
}
pub(crate) fn validate(bundle:&Bundle)->Result<(),String> {active(&bundle.collections,&bundle.manifest).map(|_|())}
pub(crate) fn additional_source_count(collections:&BTreeMap<String,Vec<Value>>,manifest:&Value)->Result<usize,String> {
    Ok(usize::from(active(collections,manifest)?))
}
fn scene(widths:&[&Value],events:&[&Value])->Value {
    if widths.is_empty()&&events.is_empty() {return Value::Null;}
    json!({"kind":"published_current_dimension_evidence","title":"Madagascar Current: regional width and dated flow examples",
        "current_id":CURRENT,"entity_id":OWNER,"width_records":widths,"event_records":events,
        "scope":"Separate regional studies and selected dated flow examples. The2010–2013 study reports a typical60–100km width, not an annual min/max, numerical uncertainty or a monthly width series. The April2001 survey is distinct.",
        "definition":"Width edges and fixed width layer are unspecified. Surface extrapolation and missing-instrument interpolation apply to INATEX. No event widths were digitized; selected snapshots are not a seasonal cycle.",
        "source_file":document()["width_record"]["source_file"],"source_url":document()["new_source"]["url"],
        "figure":"figures/ponsoni-emc-2016-dimensions-compact-v1.svg"})
}
pub(crate) fn event_scene(rows:&[&Value])->Value {scene(&[],rows)}
pub(crate) fn widths(bundle:&Bundle)->Vec<Value> {
    if bundle.manifest[KEY].is_null() {return vec![];}
    bundle.collections.get("widths").map(Vec::as_slice).unwrap_or(&[]).iter()
        .filter(|r|r["id"]==document()["width_record"]["id"]).cloned().collect()
}
pub(crate) fn seasonal_source_widths(bundle:&Bundle)->Result<Vec<Value>,String> {
    if !active(&bundle.collections,&bundle.manifest)? {return Ok(vec![]);}
    Ok(widths(bundle))
}
pub(crate) fn legacy_owner_projection(bundle:&Bundle,owner:&Value)->Result<Value,String> {
    if owner["id"]!=OWNER || !active(&bundle.collections,&bundle.manifest)? {return Ok(owner.clone());}
    if owner!=&document()["final_owner"] {return Err("Changed owner passed to legacy Madagascar guard".into());}
    Ok(document()["prior_records"]["owner"].clone())
}
pub(crate) fn width_scene(rows:&[&Value],bundle:&Bundle)->Value {
    if bundle.manifest[KEY].is_null() {return Value::Null;}
    let selected=rows.iter().copied().filter(|r|r["current_id"]==CURRENT).collect::<Vec<_>>();
    scene(&selected,&[])
}
pub(crate) fn by_current(bundle:&Bundle)->Value {
    if bundle.manifest[KEY].is_null() {return json!({});}
    let widths=bundle.collections.get("widths").map(Vec::as_slice).unwrap_or(&[]).iter().filter(|r|r["current_id"]==CURRENT).collect::<Vec<_>>();
    let events=bundle.collections.get(COLLECTION).map(Vec::as_slice).unwrap_or(&[]).iter().collect::<Vec<_>>();
    json!({"southern-east-madagascar":scene(&widths,&events)})
}
pub(crate) fn dashboard_row(bundle:&Bundle,original:&Value)->Result<Value,String> {
    if original["id"]!=OWNER||!active(&bundle.collections,&bundle.manifest)? {return Ok(original.clone());}
    if original!=&document()["dashboard_before"] {return Err("Changed preceding Madagascar dashboard row".into());}
    Ok(document()["dashboard_after"].clone())
}
pub(crate) fn dashboard_document(bundle:&Bundle,mut doc:Value)->Result<Value,String> {
    if !active(&bundle.collections,&bundle.manifest)? {return Ok(doc);}
    let rows=doc["entries"].as_array().ok_or("Missing dashboard entries")?;
    let updated=rows.iter().map(|r|dashboard_row(bundle,r)).collect::<Result<Vec<_>,_>>()?;
    let old=doc["snapshot_fingerprint"].as_str().ok_or("Missing preceding dashboard fingerprint")?;
    let fingerprint=pin(&format!("osw.madagascar-dimensions.v1\n{old}\n{}\n",pin(RAW)));
    doc["entries"]=json!(updated);doc["snapshot_fingerprint"]=json!(fingerprint);
    doc["published_madagascar_dimensions_projection_v1"]=json!({"contract_file":FILE,"contract_sha256":pin(RAW),"scope":"One regional width summary and eight dated flow examples; no seasonal dimension range."});
    Ok(doc)
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture()->Bundle {
        let input:Value=serde_json::from_str(include_str!("../../../research/madagascar-dimensions-query-fixture-v1.json")).unwrap();
        let mut b=Bundle{schema:"osw.query-bundle.v1".into(),manifest:input["manifest"].clone(),collections:serde_json::from_value(input["collections"].clone()).unwrap()};
        b.collections.get_mut("objects").unwrap()[0]=document()["final_owner"].clone();
        b.collections.get_mut("sources").unwrap().push(document()["new_source"].clone());
        b.collections.get_mut("widths").unwrap().push(document()["width_record"].clone());
        b.collections.insert(COLLECTION.into(),document()["event_records"].as_array().unwrap().clone());
        for (path,digest) in document()["input_sha256"].as_object().unwrap() {b.manifest["input_sha256"][path]=digest.clone();}
        b.manifest["input_sha256"][FILE]=json!(pin(RAW));b.manifest[KEY]=marker();b
    }
    #[test] fn source_scope_and_filtered_scenes() {
        let b=fixture();assert!(validate(&b).is_ok());assert_eq!(additional_source_count(&b.collections,&b.manifest).unwrap(),1);
        let selected=vec![&b.collections[COLLECTION][2]];let result=event_scene(&selected);
        assert_eq!(result["event_records"].as_array().unwrap().len(),1);assert_eq!(result["event_records"][0]["date"],"2011-01-19");
        assert!(result["width_records"].as_array().unwrap().is_empty());assert!(result["event_records"][0]["width_km"].is_null());
        let widths=width_scene(&[b.collections["widths"].last().unwrap()],&b);
        assert_eq!(widths["width_records"].as_array().unwrap().len(),1);assert_eq!(widths["width_records"][0]["width_range_km"],json!([60,100]));
        assert!(event_scene(&[]).is_null());assert_eq!(by_current(&b)[CURRENT]["event_records"].as_array().unwrap().len(),8);
    }
    #[test] fn altered_evidence_or_orphaned_joins_are_refused() {
        for change in ["width","event","owner","source","receipt","prior_width","prior_route"] {
            let mut b=fixture();
            match change {
                "width"=>b.collections.get_mut("widths").unwrap().last_mut().unwrap()["annual_width_range_km"]=json!([60,120]),
                "event"=>b.collections.get_mut(COLLECTION).unwrap()[0]["width_km"]=json!(80),
                "owner"=>b.collections.get_mut("objects").unwrap()[0]["capabilities"]["width_samples"]=json!(8),
                "source"=>b.collections.get_mut("sources").unwrap().last_mut().unwrap()["doi"]=json!("other"),
                "receipt"=>b.manifest[KEY]["new_width_samples"]=json!(8),
                "prior_width"=>b.collections.get_mut("widths").unwrap()[0]["unexpected"]=json!(true),
                _=>b.collections.get_mut("reference_routes").unwrap()[0]["unexpected"]=json!(true),
            }
            assert!(validate(&b).is_err(),"{change}");
        }
    }
    #[test] fn dashboard_projection_keeps_unrelated_rows() {
        let b=fixture();assert_eq!(dashboard_row(&b,&document()["dashboard_before"]).unwrap(),document()["dashboard_after"]);
        assert!(dashboard_row(&b,&json!({"id":OWNER})).is_err());
        let other=json!({"id":"current:other"});assert_eq!(dashboard_row(&b,&other).unwrap(),other);
    }
    #[test] fn seasonal_source_projection_requires_exact_regional_evidence() {
        let mut b=fixture();
        assert_eq!(seasonal_source_widths(&b).unwrap(),vec![document()["width_record"].clone()]);
        let mut combined=vec![json!({"id":"prior-source-row","keep":true})];
        combined.extend(seasonal_source_widths(&b).unwrap());
        assert_eq!(combined.len(),2);assert_eq!(combined[0]["keep"],true);
        assert_eq!(combined[1]["seasonal_playback_eligible"],false);
        b.collections.get_mut("widths").unwrap().last_mut().unwrap()["annual_width_range_km"]=json!([60,120]);
        assert!(seasonal_source_widths(&b).is_err());
        let legacy=Bundle{schema:"osw.query-bundle.v1".into(),manifest:json!({}),collections:BTreeMap::new()};
        assert!(seasonal_source_widths(&legacy).unwrap().is_empty());
    }
    #[test] fn legacy_owner_projection_is_exact_and_does_not_accept_arbitrary_extensions() {
        let mut b=fixture();let owner=document()["final_owner"].clone();
        assert_eq!(legacy_owner_projection(&b,&owner).unwrap(),document()["prior_records"]["owner"]);
        assert_eq!(b.collections["objects"][0],owner);
        let mut unrelated=owner.clone();unrelated["id"]=json!("current:other");
        assert_eq!(legacy_owner_projection(&b,&unrelated).unwrap(),unrelated);
        let mut forged=owner.clone();forged["capabilities"]["scoped_width"]=json!(99);
        assert!(legacy_owner_projection(&b,&forged).is_err());
        b.collections.get_mut("objects").unwrap()[0]["source_ids"].as_array_mut().unwrap().push(json!("unverified-source"));
        assert!(legacy_owner_projection(&b,&b.collections["objects"][0]).is_err());
    }
    #[test] fn additive_evidence_passes_legacy_coastal_and_identity_guards_without_physical_promotion() {
        let mut b=crate::current_catalogue::tests::fixture();
        let coastal=crate::madagascar_coastal_curve::tests::fixture();let added=fixture();
        for (path,digest) in coastal.manifest["input_sha256"].as_object().unwrap() {b.manifest["input_sha256"][path]=digest.clone();}
        b.manifest["madagascar_coastal_curve_version"]=json!("1");
        for (path,digest) in added.manifest["input_sha256"].as_object().unwrap() {b.manifest["input_sha256"][path]=digest.clone();}
        b.manifest[KEY]=marker();
        for name in ["reference_routes","diagnostics"] {b.collections.insert(name.into(),coastal.collections[name].clone());}
        for name in ["objects","sources","widths",COLLECTION] {b.collections.insert(name.into(),added.collections[name].clone());}
        b.collections.insert("current_measurement_admissions".into(),vec![]);
        let length=crate::current_measurements::document()["length_assessment"].clone();
        let lengths=b.collections.get_mut("length_assessments").unwrap();
        lengths.retain(|r|r["id"]!=length["id"]);lengths.push(length);
        b.collections.insert("state_links".into(),vec![json!({"entity_id":OWNER,"state_code":"EAFR",
            "source_file":crate::madagascar_coastal_curve::FILE,"kind":"editorial_coastal_reference_curve","observation_date":null})]);
        assert!(validate(&b).is_ok());
        crate::madagascar_coastal_curve::validate(&b).unwrap();
        crate::current_catalogue::validate(&b).unwrap();
        assert_eq!(b.collections["objects"][0]["capabilities"]["scoped_width"],2);
        assert_eq!(b.collections["objects"][0]["source_ids"].as_array().unwrap().len(),3);
        b.collections.get_mut("objects").unwrap()[0]["map_features"][0]["observation_date"]=json!("2011-01-19");
        assert!(crate::madagascar_coastal_curve::validate(&b).is_err());
        assert!(crate::current_catalogue::validate(&b).is_err());
    }
    #[test] fn old_bundles_work_but_new_orphans_fail() {
        let b=Bundle{schema:"osw.query-bundle.v1".into(),manifest:json!({}),collections:BTreeMap::new()};
        assert!(validate(&b).is_ok());assert_eq!(additional_source_count(&b.collections,&b.manifest).unwrap(),0);
        let mut orphan=b;orphan.collections.insert(COLLECTION.into(),vec![]);assert!(validate(&orphan).is_err());
    }
}
