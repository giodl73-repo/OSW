//! Author-reported meridional breadths are distinct isopycnal jet components.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
const OWNER: &str = "pacific-north-equatorial-undercurrent";
const SOURCE: &str = "research/pacific-neuc-li-2018-isopycnal-breadth-scope-audit.json";
const RAW: &str =
    include_str!("../../../research/pacific-neuc-li-2018-isopycnal-breadth-scope-audit.json");
const SHA: &str = "2edff326fd4b7bbc2c6a8cdd1ef0324bac77a62f7e85579cd8ff38753e2db9a6";
fn expected() -> Vec<Value> {
    let doc: Value = serde_json::from_str(RAW).unwrap();
    doc["measurements"]
        .as_array()
        .unwrap()
        .iter()
        .enumerate()
        .map(|(i, r)| {
            let mut r = r.clone();
            r["original_regional_context"]["audit_file"] = json!(SOURCE);
            r["original_regional_context"]["audit_sha256"] = json!(SHA);
            r["original_regional_context"]["audit_pointer"] = json!(format!("/measurements/{i}"));
            r
        })
        .collect()
}
pub(crate) fn validate(bundle: &Bundle) -> Result<(), String> {
    let empty = vec![];
    let widths = bundle.collections.get("widths").unwrap_or(&empty);
    let relevant = widths.iter().any(|r| {
        r["current_id"] == OWNER
            || r["id"]
                .as_str()
                .is_some_and(|s| s.starts_with("pacific-neuc-li-2018-"))
    });
    let claimed = bundle.collections.get("objects").is_some_and(|rs| {
        rs.iter().any(|r| {
            r["id"] == format!("current:{OWNER}")
                && r["capabilities"]["scoped_width"].as_u64().unwrap_or(0) > 0
        })
    });
    if bundle.manifest["input_sha256"][SOURCE].is_null() && !relevant && !claimed {
        return Ok(());
    }
    if format!("{:x}", Sha256::digest(RAW.as_bytes())) != SHA
        || bundle.manifest["input_sha256"][SOURCE] != SHA
    {
        return Err("Pacific NEUC breadth source proof differs".into());
    }
    let doc: Value = serde_json::from_str(RAW).unwrap();
    for kind in [
        "source_document",
        "acquisition",
        "protocol",
        "source_figure_receipt",
    ] {
        let path = doc[format!("{kind}_file")].as_str().unwrap();
        if bundle.manifest["input_sha256"][path] != doc[format!("{kind}_sha256")] {
            return Err(format!("Pacific NEUC breadth dependency differs: {kind}"));
        }
    }
    for figure in doc["source_figures"].as_array().unwrap() {
        if bundle.manifest["input_sha256"][figure["asset_file"].as_str().unwrap()]
            != figure["asset_sha256"]
        {
            return Err("Pacific NEUC breadth credited figure differs".into());
        }
    }
    let actual: Vec<_> = widths
        .iter()
        .filter(|r| {
            r["current_id"] == OWNER
                || r["id"]
                    .as_str()
                    .is_some_and(|s| s.starts_with("pacific-neuc-li-2018-"))
        })
        .cloned()
        .collect();
    if actual != expected() {
        return Err("Pacific NEUC breadth inventory, identity or isopycnal support differs".into());
    }
    Ok(())
}
pub(crate) fn scene(matches: &[&Value], widths: &[Value]) -> Value {
    let mut matching: Vec<_> = matches
        .iter()
        .filter(|r| r["current_id"] == OWNER)
        .map(|r| r["id"].clone())
        .collect();
    // Query sort order does not alter the shared scientific comparison scene.
    matching.sort_by(|a, b| a.as_str().cmp(&b.as_str()));
    if matching.is_empty() {
        return Value::Null;
    }
    let rows: Vec<_> = widths.iter().filter(|r| r["current_id"] == OWNER).collect();
    let points:Vec<_>=rows.iter().enumerate().map(|(i,r)|json!({"record":r,"matching":matching.contains(&r["id"]),"x_start":220,"x_end":220.0+r["approximate_width_km"].as_f64().unwrap()/400.0*480.0,"y":70+i*70})).collect();
    let doc: Value = serde_json::from_str(RAW).unwrap();
    json!({"kind":"pacific_neuc_isopycnal_breadths","title":"Pacific NEUC isopycnal jet breadths","scope":"Distinct southern and northern jets in the 2004–2014 Argo-based absolute-geostrophic mean on the 27.0 σθ density surface. Source meridional breadths are approximately 3° and 1° latitude; rounded WGS84 unit conversions are about 330 and 110 km. These are different components, not annual minimum and maximum widths.","source_file":SOURCE,"source_url":doc["source_url"],"source_citation":doc["source_citation"],"points":points,"records":rows,"matching_ids":matching,"view_box":[0,0,1000,240],"axis_max_km":400,"ticks":[0,100,200,300,400],"middle_component":doc["middle_component"],"notes":doc["scope_notes"],"geometry_role":"abstract_component_comparison_no_edges_or_footprint","source_image":{"href":"../figures/li-neuc-2018-source-isopycnal-jets.jpg","figure":1,"license_url":"https://creativecommons.org/licenses/by/4.0/","changes":"None; original source image.","caption":"Li, Liu and Lin (2018), Figure 1. Top-left: Argo absolute-geostrophic mean 2004–2014 on 27.0 σθ. Other panels are SODA/LICOM 1969–2007 comparisons; their widths are not the admitted measurements. Black curves are source zero-velocity contours, not OSW-digitized width edges. Units: cm/s. CC BY 4.0."},"interpretation":"The density surface has spatially varying depth. Meridional breadth is not a measured flow-normal section. No fixed longitude, paired endpoints, width error or monthly width series is supplied. Source degrees are retained; conversion origins are units only, not measured jet locations."})
}
pub(crate) fn full(widths: &[Value]) -> Value {
    let rows: Vec<_> = widths.iter().filter(|r| r["current_id"] == OWNER).collect();
    scene(&rows, widths)
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn components_do_not_become_temporal_extrema_or_mapped_edges() {
        let rows = expected();
        let s = full(&rows);
        assert_eq!(s["points"][0]["record"]["approximate_width_km"], 330);
        assert_eq!(s["points"][1]["record"]["approximate_width_km"], 110);
        assert!(s["middle_component"]["width_km"].is_null());
        assert!(rows.iter().all(|r| r["fixed_layer_bounds_m"].is_null()
            && r["width_range_km"].is_null()
            && r["seasonal_playback_eligible"] == false));
        let subset = scene(&[&rows[1]], &rows);
        assert_eq!(scene(&[&rows[1], &rows[0]], &rows), s);
        assert_eq!(subset["matching_ids"].as_array().unwrap().len(), 1);
        assert_eq!(subset["records"].as_array().unwrap().len(), 2);
    }
}
