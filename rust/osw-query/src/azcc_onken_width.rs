//! A dependent historical regional width does not establish current length or seasonality.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
use std::sync::OnceLock;

const FILE: &str = "research/azcc-onken-query-contract-v1.json";
const RAW: &str = include_str!("../../../research/azcc-onken-query-contract-v1.json");
const KEY: &str = "published_azcc_onken_width_v1";
const OWNER: &str = "current:azores-countercurrent";
const CURRENT: &str = "azores-countercurrent";
const SOURCE: &str = "source:onken-azcc-1993";
fn pin(raw: &str) -> String { format!("{:x}", Sha256::digest(raw.as_bytes())) }
fn document() -> &'static Value {
    static DOC: OnceLock<Value> = OnceLock::new();
    DOC.get_or_init(|| serde_json::from_str(RAW).expect("compiled AzCC cited-width contract"))
}
fn marker() -> Value {
    json!({"schema":"osw.azcc-onken-runtime-receipt.v1","parent_logical_sha256":document()["parent_logical_sha256"],
        "contract_file":FILE,"contract_sha256":pin(RAW),"width_records_added":1,"publication_sources_added":1,
        "new_width_samples":0,"new_independent_observations":0,"new_length_records":0})
}
fn title(value:&Value)->String {
    value.as_str().unwrap_or("").chars().filter(char::is_ascii_alphanumeric).flat_map(char::to_lowercase).collect()
}
fn decoded(value:&Value)->String {
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
fn doi(value:&Value)->String {
    let decoded=decoded(value);let text=decoded.split(['?','#']).next().unwrap_or("");
    for prefix in ["https://doi.org/","http://doi.org/","https://dx.doi.org/","http://dx.doi.org/","doi:"] {
        if let Some(tail)=text.strip_prefix(prefix) {return tail.trim().trim_end_matches('/').into();}
    }
    if let Some((_,tail))=text.split_once("/doi/") {
        return ["full/","abs/","epdf/","pdf/"].iter().find_map(|p|tail.strip_prefix(*p)).unwrap_or(tail).trim_end_matches('/').into();
    }
    text.trim_end_matches('/').into()
}
fn url(value:&Value)->String {
    let decoded=decoded(value);let text=decoded.split(['?','#']).next().unwrap_or("");
    text.strip_prefix("https://").or_else(||text.strip_prefix("http://")).unwrap_or(text).trim_end_matches('/').into()
}
fn active(collections:&BTreeMap<String,Vec<Value>>,manifest:&Value)->Result<bool,String> {
    let fail=||"Invalid AzCC cited historical regional width evidence".to_owned();
    let rows=|name:&str|collections.get(name).map(Vec::as_slice).unwrap_or(&[]);
    let doc=document();let width_id=&doc["width_record"]["id"];
    let trace=rows("sources").iter().any(|r|r["id"]==SOURCE)
        ||rows("widths").iter().any(|r|r["id"]==*width_id)
        ||rows("objects").iter().any(|r|r["width_ids"].as_array().is_some_and(|ids|ids.contains(width_id)));
    if manifest[KEY].is_null()&&!trace&&manifest["input_sha256"][FILE].is_null() {return Ok(false);}
    if manifest[KEY]!=marker()||manifest["input_sha256"][FILE]!=pin(RAW) {return Err(fail());}
    for (path,digest) in doc["input_sha256"].as_object().ok_or_else(fail)? {
        if manifest["input_sha256"][path]!=*digest {return Err(fail());}
    }
    if rows("sources").iter().filter(|r|r["id"]==SOURCE).collect::<Vec<_>>()!=vec![&doc["new_source"]] {return Err(fail());}
    let mut ids=BTreeSet::new();
    for source in rows("sources") {
        let id=source["id"].as_str().ok_or_else(fail)?;
        if id.is_empty()||!ids.insert(id) {return Err(fail());}
        if id!=SOURCE&&(doi(&source["doi"])==doi(&doc["new_source"]["doi"])
            ||doi(&source["url"])==doi(&doc["new_source"]["doi"])
            ||url(&source["url"])==url(&doc["new_source"]["url"])
            ||title(&source["title"])==title(&doc["new_source"]["title"])
            ||title(&source["label"])==title(&doc["new_source"]["title"])) {return Err(fail());}
    }
    for source in doc["prior_records"]["owner_sources"].as_array().ok_or_else(fail)? {
        if rows("sources").iter().filter(|r|r["id"]==source["id"]).collect::<Vec<_>>()!=vec![source] {return Err(fail());}
    }
    if rows("objects").iter().filter(|r|r["id"]==OWNER).collect::<Vec<_>>()!=vec![&doc["final_owner"]]
        ||rows("entities").iter().filter(|r|r["id"]==OWNER).collect::<Vec<_>>()!=vec![&doc["prior_records"]["entity"]] {return Err(fail());}
    let mut expected=doc["prior_records"]["widths"].as_array().ok_or_else(fail)?.iter().collect::<Vec<_>>();
    expected.push(&doc["width_record"]);
    if rows("widths").iter().filter(|r|r["current_id"]==CURRENT).collect::<Vec<_>>()!=expected
        ||rows("widths").iter().filter(|r|r["id"]==*width_id).count()!=1
        ||rows("reference_routes").iter().filter(|r|r["current_id"]==CURRENT).collect::<Vec<_>>()
            !=doc["prior_records"]["reference_routes"].as_array().ok_or_else(fail)?.iter().collect::<Vec<_>>() {return Err(fail());}
    Ok(true)
}
pub(crate) fn validate(bundle:&Bundle)->Result<(),String> {active(&bundle.collections,&bundle.manifest).map(|_|())}
pub(crate) fn additional_source_count(collections:&BTreeMap<String,Vec<Value>>,manifest:&Value)->Result<usize,String> {
    Ok(usize::from(active(collections,manifest)?))
}
pub(crate) fn widths(bundle:&Bundle)->Vec<Value> {
    if bundle.manifest[KEY].is_null() {return vec![];}
    bundle.collections.get("widths").map(Vec::as_slice).unwrap_or(&[]).iter()
        .filter(|r|r["id"]==document()["width_record"]["id"]).cloned().collect()
}
pub(crate) fn validated_widths(bundle:&Bundle)->Result<Vec<Value>,String> {
    if !active(&bundle.collections,&bundle.manifest)? {return Ok(vec![]);}
    Ok(widths(bundle))
}
fn scene(widths:&[&Value])->Value {
    if widths.is_empty() {return Value::Null;}
    json!({"kind":"published_current_dimension_evidence","title":"Azores Countercurrent: separately scoped width evidence",
        "current_id":CURRENT,"entity_id":OWNER,"width_records":widths,"event_records":[],
        "scope":"The 110 km meridional section from 2009 and the approximately 200 km historical regional interpretation describe different places, periods and methods. They do not form a seasonal range, uncertainty interval or whole-current dimension.",
        "definition":"Onken (1993) interprets historical sections cited through Worthington (1962, 1976). Original observation dates, fixed width layer and paired edges remain unknown. Evidence at several longitudes from 17 to 55 W is not a diagnosed current axis or length.",
        "source_file":document()["width_record"]["source_file"],"source_url":document()["new_source"]["url"],
        "source_label":"Original historical study","figure":"figures/onken-azcc-1993-evidence-compact-v1.svg",
        "width_source_links":{"azores-countercurrent-2009-section-width":{"source_file":"research/azores-2009-section-record-bindings-v1.json","source_pointer":"/records/1"}}})
}
pub(crate) fn width_scene(rows:&[&Value],bundle:&Bundle)->Value {
    if bundle.manifest[KEY].is_null() {return Value::Null;}
    let selected=rows.iter().copied().filter(|r|r["current_id"]==CURRENT).collect::<Vec<_>>();scene(&selected)
}
pub(crate) fn by_current(bundle:&Bundle)->Value {
    let mut result=crate::madagascar_dimensions::by_current(bundle);
    if !bundle.manifest[KEY].is_null() {
        let widths=bundle.collections.get("widths").map(Vec::as_slice).unwrap_or(&[]).iter().filter(|r|r["current_id"]==CURRENT).collect::<Vec<_>>();
        result[CURRENT]=scene(&widths);
    }
    result
}
pub(crate) fn dashboard_row(bundle:&Bundle,original:&Value)->Result<Value,String> {
    if original["id"]!=OWNER||!active(&bundle.collections,&bundle.manifest)? {return Ok(original.clone());}
    if original!=&document()["dashboard_before"] {return Err("Changed preceding AzCC dashboard row".into());}
    Ok(document()["dashboard_after"].clone())
}
pub(crate) fn dashboard_document(bundle:&Bundle,mut doc:Value)->Result<Value,String> {
    if !active(&bundle.collections,&bundle.manifest)? {return Ok(doc);}
    let rows=doc["entries"].as_array().ok_or("Missing dashboard entries")?;
    let updated=rows.iter().map(|r|dashboard_row(bundle,r)).collect::<Result<Vec<_>,_>>()?;
    let old=doc["snapshot_fingerprint"].as_str().ok_or("Missing preceding dashboard fingerprint")?;
    let fingerprint=pin(&format!("osw.azcc-onken-width.v1\n{old}\n{}\n",pin(RAW)));
    doc["entries"]=json!(updated);doc["snapshot_fingerprint"]=json!(fingerprint);
    doc["published_azcc_onken_width_projection_v1"]=json!({"contract_file":FILE,"contract_sha256":pin(RAW),"scope":"One dependent historical regional width; no seasonal dimension range or length."});
    Ok(doc)
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture()->Bundle {
        let input:Value=serde_json::from_str(include_str!("../../../research/azcc-onken-query-fixture-v1.json")).unwrap();
        let mut b=Bundle{schema:"osw.query-bundle.v1".into(),manifest:input["manifest"].clone(),collections:serde_json::from_value(input["collections"].clone()).unwrap()};
        b.collections.get_mut("objects").unwrap()[0]=document()["final_owner"].clone();
        b.collections.get_mut("sources").unwrap().push(document()["new_source"].clone());
        b.collections.get_mut("widths").unwrap().push(document()["width_record"].clone());
        for (path,digest) in document()["input_sha256"].as_object().unwrap() {b.manifest["input_sha256"][path]=digest.clone();}
        b.manifest["input_sha256"][FILE]=json!(pin(RAW));b.manifest[KEY]=marker();b
    }
    #[test] fn exact_scope_filtered_widths_and_prior_scene_support() {
        let b=fixture();validate(&b).unwrap();assert_eq!(additional_source_count(&b.collections,&b.manifest).unwrap(),1);
        let row=b.collections["widths"].last().unwrap();let s=width_scene(&[row],&b);
        assert_eq!(s["width_records"],json!([row]));assert!(s["event_records"].as_array().unwrap().is_empty());
        assert_eq!(row["approximate_width_km"],200);assert!(row["annual_width_range_km"].is_null());assert!(row["observed_period"].is_null());
        assert_eq!(by_current(&b)[CURRENT]["width_records"].as_array().unwrap().len(),2);
        assert_eq!(s["width_source_links"]["azores-countercurrent-2009-section-width"]["source_pointer"],"/records/1");
        assert!(width_scene(&[],&b).is_null());assert_eq!(validated_widths(&b).unwrap(),vec![row.clone()]);
    }
    #[test] fn altered_rows_prior_evidence_and_orphaned_receipts_fail() {
        for change in ["width","prior_width","owner","source","receipt","route","pin"] {
            let mut b=fixture();
            match change {
                "width"=>b.collections.get_mut("widths").unwrap().last_mut().unwrap()["annual_width_range_km"]=json!([110,200]),
                "prior_width"=>b.collections.get_mut("widths").unwrap()[0]["observed_period"]["end"]=json!("1993-08-01"),
                "owner"=>b.collections.get_mut("objects").unwrap()[0]["latest_observation_date"]=json!("1993-08-01"),
                "source"=>b.collections.get_mut("sources").unwrap().last_mut().unwrap()["doi"]=json!("other"),
                "receipt"=>{b.manifest.as_object_mut().unwrap().remove(KEY);},
                "route"=>b.collections.get_mut("reference_routes").unwrap().push(json!({"id":"invented","current_id":CURRENT})),
                _=>b.manifest["input_sha256"][FILE]=json!("changed"),
            }
            assert!(validate(&b).is_err(),"{change}");
        }
    }
    #[test] fn legacy_bundles_and_encoded_publication_aliases() {
        let old=Bundle{schema:"osw.query-bundle.v1".into(),manifest:json!({}),collections:BTreeMap::new()};
        validate(&old).unwrap();assert!(validated_widths(&old).unwrap().is_empty());
        assert_eq!(doi(&json!("https://doi.org/10.1175/1520-0485%281993%29023%3C1638%3ATAC%3E2.0.CO%3B2")),doi(&document()["new_source"]["doi"]));
        for alias in [json!({"id":"other","doi":"https://doi.org/10.1175/1520-0485%281993%29023%3C1638%3ATAC%3E2.0.CO%3B2"}),
            json!({"id":"other","title":"THE AZORES COUNTERCURRENT"}),json!({"id":"other","url":document()["new_source"]["url"]})] {
            let mut b=fixture();b.collections.get_mut("sources").unwrap().push(alias);assert!(validate(&b).is_err());
        }
    }
    #[test] fn dashboard_changes_only_target_and_keeps_2009_date() {
        let b=fixture();let before=&document()["dashboard_before"];let after=&document()["dashboard_after"];
        assert_eq!(dashboard_row(&b,before).unwrap(),*after);assert_eq!(after["latest_observation_date"],"2009-11-01");
        let other=json!({"id":"current:other","keep":true});assert_eq!(dashboard_row(&b,&other).unwrap(),other);
        assert!(dashboard_row(&b,&json!({"id":OWNER})).is_err());
        let snapshot=json!({"entries":[before,other],"snapshot_fingerprint":"old","existing_namespace":{"keep":true}});
        let projected=dashboard_document(&b,snapshot).unwrap();assert_eq!(projected["entries"][1]["keep"],true);
        assert_eq!(projected["existing_namespace"]["keep"],true);assert!(after["published_length_km"].is_null());
    }
    #[test] fn exact_append_preserves_all_three_historical_width_inventories() {
        type Check=fn(&Bundle)->Result<(),String>;
        let cases:Vec<(&str,Bundle,Check)>=vec![
            ("ASAR",crate::hansen_asar_widths::tests::fixture(),crate::hansen_asar_widths::validate),
            ("NEUC",crate::neuc_glider_widths::tests::fixture(),crate::neuc_glider_widths::validate),
            ("Aleutian",crate::aleutian_onishi_width::tests::fixture(),crate::aleutian_onishi_width::validate)];
        for (name,mut b,check) in cases {
            let before=b.collections["widths"].clone();let added=fixture();
            assert_eq!(before.iter().filter(|r|r["current_id"]==CURRENT).collect::<Vec<_>>(),document()["prior_records"]["widths"].as_array().unwrap().iter().collect::<Vec<_>>());
            b.collections.get_mut("widths").unwrap().push(document()["width_record"].clone());
            for key in ["objects","entities"] {
                let rows=b.collections.entry(key.into()).or_default();rows.retain(|r|r["id"]!=OWNER);rows.push(added.collections[key][0].clone());
            }
            b.collections.entry("reference_routes".into()).or_default().retain(|r|r["current_id"]!=CURRENT);
            let sources=b.collections.entry("sources".into()).or_default();
            for row in document()["prior_records"]["owner_sources"].as_array().unwrap().iter().chain(std::iter::once(&document()["new_source"])) {
                sources.retain(|r|r["id"]!=row["id"]);sources.push(row.clone());
            }
            for (path,digest) in added.manifest["input_sha256"].as_object().unwrap() {b.manifest["input_sha256"][path]=digest.clone();}
            b.manifest[KEY]=marker();validate(&b).unwrap();check(&b).unwrap_or_else(|e|panic!("{name}: {e}"));
            assert_eq!(&b.collections["widths"][..before.len()],before.as_slice());
            b.collections.get_mut("widths").unwrap().push(document()["width_record"].clone());assert!(check(&b).is_err(),"{name} duplicate");
        }
    }
}
