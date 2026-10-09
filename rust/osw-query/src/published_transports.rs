//! Published section statistics retain their original, unequal support.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::BTreeSet;
const SOURCE: &str = "research/australia-wijeratne-2018-section-transport-audit.json";
const RAW: &str =
    include_str!("../../../research/australia-wijeratne-2018-section-transport-audit.json");
const SHA: &str = "758f18afccfee1411434d59ff9a3d0c38daf8833abf285674a33f9386ec961dd";
const COLLECTIONS: [&str; 2] = ["section_transports", "transport_validations"];
fn projection(doc: &Value, collection: &str) -> Vec<Value> {
    doc[collection]
        .as_array()
        .unwrap()
        .iter()
        .map(|original| {
            let mut row = original.clone();
            row["source_file"] = json!(SOURCE);
            row["source_file_sha256"] = json!(SHA);
            row["label"] = json!(format!(
                "{} · {}",
                row["section_id"].as_str().unwrap(),
                row[if collection == "section_transports" {
                    "source_current_label"
                } else {
                    "place_label"
                }]
                .as_str()
                .unwrap()
            ));
            row
        })
        .collect()
}
pub(crate) fn validate(bundle: &Bundle) -> Result<(), String> {
    if bundle.manifest["input_sha256"][SOURCE].is_null()
        && COLLECTIONS
            .iter()
            .all(|c| !bundle.collections.contains_key(*c))
        && bundle.collections.get("objects").is_none_or(|objects| {
            objects.iter().all(|object| {
                object["capabilities"]["section_transport"].is_null()
                    && COLLECTIONS
                        .iter()
                        .all(|c| object[format!("{c}_ids")].is_null())
            })
        })
    {
        return Ok(());
    }
    if format!("{:x}", Sha256::digest(RAW.as_bytes())) != SHA
        || bundle.manifest["input_sha256"][SOURCE] != SHA
    {
        return Err("Published section transport source pin mismatch".into());
    }
    let doc: Value = serde_json::from_str(RAW).unwrap();
    for kind in ["source_document", "acquisition", "protocol"] {
        let path = doc[format!("{kind}_file")].as_str().unwrap();
        if bundle.manifest["input_sha256"][path] != doc[format!("{kind}_sha256")] {
            return Err(format!(
                "Published section transport dependency differs: {kind}"
            ));
        }
    }
    for c in COLLECTIONS {
        let rows = bundle
            .collections
            .get(c)
            .ok_or("Published section transport collection missing")?;
        if *rows != projection(&doc, c) {
            return Err(format!(
                "Published section transport scientific scope differs: {c}"
            ));
        }
    }
    for object in &bundle.collections["objects"] {
        let mut count = 0;
        for c in COLLECTIONS {
            let owned: Vec<_> = bundle.collections[c]
                .iter()
                .filter(|r| r["entity_id"] == object["id"])
                .map(|r| r["id"].clone())
                .collect();
            count += owned.len();
            let actual = &object[format!("{c}_ids")];
            if (!owned.is_empty() || !actual.is_null()) && actual != &json!(owned) {
                return Err("Published section transport owner joins differ".into());
            }
        }
        if object["capabilities"]["section_transport"]
            .as_u64()
            .unwrap_or(0)
            != count as u64
        {
            return Err("Published section transport dashboard scope differs".into());
        }
    }
    Ok(())
}
fn make(models: &[&Value], validations: &[&Value]) -> Value {
    if models.is_empty() && validations.is_empty() {
        return Value::Null;
    }
    let doc: Value = serde_json::from_str(RAW).unwrap();
    let owners: BTreeSet<_> = models
        .iter()
        .chain(validations.iter())
        .filter_map(|r| r["current_id"].as_str())
        .collect();
    let seasonal: Vec<_> = doc["seasonal_transport_context"]
        .as_array()
        .unwrap()
        .iter()
        .filter(|r| owners.contains(r["current_id"].as_str().unwrap()))
        .collect();
    let points:Vec<_>=models.iter().enumerate().map(|(i,r)|json!({"record":r,"x_start":260,"x_end":260.0+r["value_sv"].as_f64().unwrap()/40.0*500.0,"y":40+i*46})).collect();
    let project = |lon: f64, lat: f64| {
        crate::cartography::root(crate::map::point(&json!([lon, lat])).unwrap())
    };
    let (left, top) = project(95.0, -8.0);
    let (right, bottom) = project(160.0, -48.0);
    let mut seen = BTreeSet::new();
    let guides:Vec<_>=models.iter().filter(|r|seen.insert(r["section_id"].as_str().unwrap())).map(|r| {
        let value=r["coordinate_degrees"].as_f64().unwrap();let axis=r["coordinate_axis"].as_str().unwrap();
        json!({"section_id":r["section_id"],"axis":axis,"coordinate_degrees":value,"display_coordinate":if axis=="latitude" {project(95.0,value).1} else {project(value,-8.0).0}})
    }).collect();
    json!({"kind":"published_section_transports","title":"Published Australian section transport",
        "scope":"Source statistics, not a reprocessed ocean field. Model section means span 2000–2014; validation pairs use shorter, incompletely sampled periods. Sv means one million cubic metres per second.",
        "source_file":SOURCE,"source_citation":doc["source_citation"],"source_url":"https://doi.org/10.1029/2017JC013221",
        "points":points,"view_box":[0,0,1000,(models.len()*46+85).max(140)],"axis_max_sv":40,"ticks":[0,10,20,30,40],"model_records":models,"validation_records":validations,"seasonal_context":seasonal,
        "notes":doc["scope_notes"],"model_description":doc["model_description"],
        "geographic_view":{"view_box":[left,top,right-left,bottom-top],"projection":"OSW equirectangular","role":"partial_coordinate_context_not_section_geometry","guides":guides,"caption":"Australia context and source latitude/longitude guides only. Each section supplies one coordinate; line endpoints, current edges and physical state intersections remain unresolved. Guide lines across land or sea do not trace a transect."},
        "spread_note":"Model plus/minus values retain the source notation with the statistic definition unresolved. Bars show mean magnitudes only; directions remain separate. Validation standard deviations measure reported variability, not confidence intervals or measurement error. No width margins are inferred."})
}
pub(crate) fn query(matches: &[&Value], collection: &str) -> Value {
    if collection == "section_transports" {
        make(matches, &[])
    } else {
        make(&[], matches)
    }
}
pub(crate) fn by_current(bundle: &Bundle) -> Value {
    let mut output = json!({});
    let empty = vec![];
    let models = bundle.collections.get(COLLECTIONS[0]).unwrap_or(&empty);
    let validations = bundle.collections.get(COLLECTIONS[1]).unwrap_or(&empty);
    let owners: BTreeSet<_> = models
        .iter()
        .chain(validations.iter())
        .filter_map(|r| r["current_id"].as_str())
        .collect();
    for owner in owners {
        let m: Vec<_> = models.iter().filter(|r| r["current_id"] == owner).collect();
        let v: Vec<_> = validations
            .iter()
            .filter(|r| r["current_id"] == owner)
            .collect();
        output[owner] = make(&m, &v);
    }
    output
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn source_support_and_dispersion_are_distinct() {
        let doc: Value = serde_json::from_str(RAW).unwrap();
        let models = projection(&doc, COLLECTIONS[0]);
        let hiri: Vec<_> = models
            .iter()
            .filter(|r| r["current_id"] == "hiri-current")
            .collect();
        let s = make(&hiri, &[]);
        assert_eq!(s["points"][0]["record"]["value_sv"], 6.9);
        assert_eq!(s["model_records"][0]["standard_error_sv"], Value::Null);
        assert_eq!(s["geographic_view"]["guides"].as_array().unwrap().len(), 1);
        let pairs = projection(&doc, COLLECTIONS[1]);
        assert_eq!(pairs[0]["simulation"]["direction"], "S");
        assert_eq!(pairs[5]["source_month_count"], 18);
        assert!(make(&[], &[]).is_null());
    }
}
