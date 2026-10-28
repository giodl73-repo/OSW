//! Published model-mean section geometry remains distinct from dated widths.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
use std::sync::OnceLock;

pub(crate) const COLLECTION: &str = "current_mean_core_sections";
const FILE: &str = "research/eac-mean-core-query-contract-v1.json";
const RAW: &str = include_str!("../../../research/eac-mean-core-query-contract-v1.json");
const KEY: &str = "published_eac_mean_core_sections_v1";
const OWNER: &str = "current:east-australian";
const SOURCE: &str = "source:eac-kerry-2020-mean-core";
fn pin(raw: &str) -> String { format!("{:x}", Sha256::digest(raw.as_bytes())) }
fn document() -> &'static Value {
    static DOC: OnceLock<Value> = OnceLock::new();
    DOC.get_or_init(|| serde_json::from_str(RAW).expect("compiled mean-core contract"))
}
fn marker() -> Value {
    json!({"schema":"osw.eac-mean-core-runtime-receipt.v1","parent_logical_sha256":document()["parent_logical_sha256"],
        "contract_file":FILE,"contract_sha256":pin(RAW),"records_added":5,"publication_sources_added":1,
        "new_width_records":0,"new_length_records":0,"new_independent_observations":0})
}
fn normalized_title(value: &Value) -> String {
    value.as_str().unwrap_or("").chars().filter(char::is_ascii_alphanumeric).flat_map(char::to_lowercase).collect()
}
fn normalized_doi(value: &Value) -> String {
    let text=value.as_str().unwrap_or("").trim().to_lowercase();
    let text=text.split(['?', '#']).next().unwrap_or("");
    for prefix in ["https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "http://dx.doi.org/", "doi:"] {
        if let Some(tail)=text.strip_prefix(prefix) { return tail.trim().trim_end_matches('/').into(); }
    }
    if let Some((_, tail))=text.split_once("/doi/") {
        let tail=["full/", "abs/", "pdf/", "epdf/"].iter().find_map(|p| tail.strip_prefix(*p)).unwrap_or(tail);
        return tail.trim_end_matches('/').into();
    }
    text.trim_end_matches('/').into()
}
fn active(collections: &BTreeMap<String, Vec<Value>>, manifest: &Value) -> Result<bool, String> {
    let fail=|| "Invalid published mean-core section evidence".to_owned();
    let rows=|name:&str| collections.get(name).map(Vec::as_slice).unwrap_or(&[]);
    let doc=document();
    let source_trace=rows("sources").iter().any(|r|r["id"]==SOURCE);
    let owner_trace=rows("objects").iter().any(|r|!r["mean_core_section_ids"].is_null());
    if manifest[KEY].is_null() && !collections.contains_key(COLLECTION) && !source_trace && !owner_trace && manifest["input_sha256"][FILE].is_null() {
        return Ok(false);
    }
    if manifest[KEY]!=marker() || manifest["input_sha256"][FILE]!=pin(RAW)
        || rows(COLLECTION)!=doc["records"].as_array().ok_or_else(fail)?.as_slice() { return Err(fail()); }
    for (path,digest) in doc["input_sha256"].as_object().ok_or_else(fail)? {
        if manifest["input_sha256"][path]!=*digest { return Err(fail()); }
    }
    let actual:Vec<_>=rows("sources").iter().filter(|r|r["id"]==SOURCE).collect();
    if actual!=vec![&doc["new_source"]] { return Err(fail()); }
    let mut ids=BTreeSet::new();
    for source in rows("sources") {
        let id=source["id"].as_str().ok_or_else(fail)?;
        if !ids.insert(id) { return Err(fail()); }
        if source["id"]!=SOURCE && (normalized_doi(&source["doi"])=="10.1029/2019jc015227"
            || normalized_doi(&source["url"])=="10.1029/2019jc015227"
            || normalized_title(&source["title"])==normalized_title(&doc["new_source"]["title"])
            || normalized_title(&source["label"])==normalized_title(&doc["new_source"]["title"])) { return Err(fail()); }
    }
    for source in doc["prior_records"]["owner_sources"].as_array().ok_or_else(fail)? {
        if rows("sources").iter().find(|r|r["id"]==source["id"])!=Some(source) { return Err(fail()); }
    }
    if rows("objects").iter().filter(|r|r["id"]==OWNER).collect::<Vec<_>>()!=vec![&doc["final_owner"]]
        || rows("entities").iter().filter(|r|r["id"]==OWNER).collect::<Vec<_>>()!=vec![&doc["prior_records"]["entity"]] { return Err(fail()); }
    if rows("objects").iter().any(|r|r["id"]!=OWNER && !r["mean_core_section_ids"].is_null()) { return Err(fail()); }
    for name in ["widths","reference_routes"] {
        if rows(name).iter().filter(|r|r["current_id"]=="east-australian").collect::<Vec<_>>()
            !=doc["prior_records"][name].as_array().ok_or_else(fail)?.iter().collect::<Vec<_>>() { return Err(fail()); }
    }
    Ok(true)
}
pub(crate) fn validate(bundle:&Bundle)->Result<(),String> { active(&bundle.collections,&bundle.manifest).map(|_|()) }
pub(crate) fn additional_source_count(collections:&BTreeMap<String,Vec<Value>>,manifest:&Value)->Result<usize,String> {
    Ok(usize::from(active(collections,manifest)?))
}
pub(crate) fn scene(rows:&[&Value])->Value {
    if rows.is_empty() { return Value::Null; }
    json!({"kind":"published_mean_core_sections","title":"East Australian Current: regional mean model core",
        "scope":"Five source-defined regional sections from a1994–2016 ROMS simulation mean. Offshore extent is not a fixed-depth paired width; maximum contour depth is not uniform current thickness. Spatial differences are not seasonal ranges or uncertainty.",
        "records":rows,"source_file":rows[0]["source_file"],"source_url":document()["new_source"]["url"],
        "boundary":"−0.05 m/s contour in mean alongshore velocity; negative is poleward",
        "definition":"Geometry of the mean velocity, not a mean of daily dimensions. No annual dimension extrema or numerical errors supplied.",
        "labeling_note":"Forster follows Table1 at32.3°S; Figure5(c) is labeled32.0°S. Source labeling discrepancy remains unresolved.",
        "figure":"figures/eac-kerry-2020-mean-core-dimensions-v2.svg",
        "compact_figure":"figures/eac-kerry-2020-mean-core-dimensions-compact-v2.svg"})
}
pub(crate) fn by_current(bundle:&Bundle)->Value {
    let rows=bundle.collections.get(COLLECTION).map(Vec::as_slice).unwrap_or(&[]);
    if rows.is_empty() { return json!({}); }
    json!({"east-australian":scene(&rows.iter().collect::<Vec<_>>())})
}
pub(crate) fn dashboard_row(bundle:&Bundle,original:&Value)->Result<Value,String> {
    if original["id"]!=OWNER || !active(&bundle.collections,&bundle.manifest)? { return Ok(original.clone()); }
    if original!=&document()["dashboard_before"] { return Err("Changed preceding EAC dashboard row".into()); }
    Ok(document()["dashboard_after"].clone())
}
pub(crate) fn dashboard_document(bundle:&Bundle,mut doc:Value)->Result<Value,String> {
    if !active(&bundle.collections,&bundle.manifest)? { return Ok(doc); }
    let rows=doc["entries"].as_array().ok_or("Missing dashboard entries")?;
    let updated=rows.iter().map(|r|dashboard_row(bundle,r)).collect::<Result<Vec<_>,_>>()?;
    let previous=doc["snapshot_fingerprint"].as_str().ok_or("Missing preceding dashboard fingerprint")?;
    let fingerprint=pin(&format!("osw.mean-core-sections.v1\n{previous}\n{}\n",pin(RAW)));
    doc["entries"]=json!(updated);doc["snapshot_fingerprint"]=json!(fingerprint);
    doc["published_mean_core_sections_projection_v1"]=json!({"contract_file":FILE,"contract_sha256":pin(RAW),"scope":"Five regional model-mean sections; no seasonal dimensions or physical footprint."});
    Ok(doc)
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture()->Bundle { serde_json::from_str(include_str!("../../../research/eac-mean-core-query-fixture-v1.json")).unwrap() }
    #[test]
    fn exact_mean_core_fixture_and_filtered_scene_preserve_scope() {
        let b=fixture();assert!(validate(&b).is_ok());assert_eq!(additional_source_count(&b.collections,&b.manifest).unwrap(),1);
        let rows=&b.collections[COLLECTION];let selected=vec![&rows[2]];let output=scene(&selected);
        assert_eq!(output["records"].as_array().unwrap().len(),1);assert_eq!(output["records"][0]["offshore_extent_km"],178.7);
        assert!(output["records"][0]["geometry"].is_null());assert_eq!(output["records"][0]["seasonal_playback_eligible"],false);
        assert!(scene(&[]).is_null());
    }
    #[test]
    fn changed_geometry_range_source_owner_and_receipt_refused() {
        for change in ["extent","geometry","range","source","owner","receipt","width"] {
            let mut b=fixture();
            match change {
                "extent"=>b.collections.get_mut(COLLECTION).unwrap()[0]["offshore_extent_km"]=json!(999),
                "geometry"=>b.collections.get_mut(COLLECTION).unwrap()[0]["geometry"]=json!({"type":"Point","coordinates":[154,-27.5]}),
                "range"=>b.collections.get_mut(COLLECTION).unwrap()[0]["annual_width_range_km"]=json!([150,200]),
                "source"=>b.collections.get_mut("sources").unwrap().last_mut().unwrap()["doi"]=json!("other"),
                "owner"=>b.collections.get_mut("objects").unwrap()[0]["capabilities"]["scoped_width"]=json!(6),
                "receipt"=>b.manifest[KEY]["new_width_records"]=json!(5),
                _=>b.collections.get_mut("widths").unwrap()[0]["unexpected"]=json!(true),
            }
            assert!(validate(&b).is_err(),"{change}");
        }
    }
    #[test]
    fn dashboard_projection_is_exact_and_unrelated_rows_are_preserved() {
        let b=fixture();assert_eq!(dashboard_row(&b,&document()["dashboard_before"]).unwrap(),document()["dashboard_after"]);
        assert!(dashboard_row(&b,&json!({"id":OWNER})).is_err());let other=json!({"id":"current:other"});
        assert_eq!(dashboard_row(&b,&other).unwrap(),other);
    }
    #[test]
    fn old_bundles_remain_compatible_but_orphan_new_evidence_is_refused() {
        let b=Bundle{schema:"osw.query-bundle.v1".into(),manifest:json!({}),collections:BTreeMap::new()};
        assert!(validate(&b).is_ok());assert_eq!(additional_source_count(&b.collections,&b.manifest).unwrap(),0);
        let mut bad=b;bad.collections.insert(COLLECTION.into(),vec![]);assert!(validate(&bad).is_err());
    }
}
