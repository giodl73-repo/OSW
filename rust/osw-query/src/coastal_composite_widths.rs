//! Seven spatial composites share one source axis; they are not seasonal states.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
const SOURCE: &str = "research/antarctic-coastal-schubert-2021-composite-width-scope-audit.json";
const RAW: &str = include_str!(
    "../../../research/antarctic-coastal-schubert-2021-composite-width-scope-audit.json"
);
fn coastal(row: &Value) -> bool {
    row["current_id"] == "antarctic-coastal"
        || row["id"]
            .as_str()
            .unwrap_or("")
            .starts_with("antarctic-coastal-schubert-2021-")
}
pub(crate) fn validate(bundle: &Bundle) -> Result<(), String> {
    let empty = vec![];
    let rows = bundle.collections.get("widths").unwrap_or(&empty);
    if bundle.manifest["input_sha256"][SOURCE].is_null() && !rows.iter().any(coastal) {
        return Ok(()); // Earlier bundles do not claim this reviewed source.
    }
    let audit: Value = serde_json::from_str(RAW).map_err(|e| e.to_string())?;
    if bundle.manifest["input_sha256"][SOURCE] != format!("{:x}", Sha256::digest(RAW.as_bytes())) {
        return Err("Coastal composite source audit mismatch".into());
    }
    let expected = audit["measurements"]
        .as_array()
        .ok_or("Coastal composite source rows missing")?;
    if rows.iter().filter(|r| coastal(r)).count() != expected.len()
        || expected
            .iter()
            .any(|e| rows.iter().filter(|r| r["id"] == e["id"]).count() != 1)
    {
        return Err("Coastal composite seven-section inventory incomplete".into());
    }
    for row in rows.iter().filter(|r| coastal(r)) {
        crate::original_regional_widths::validate(row)?;
    }
    Ok(())
}
pub(crate) fn scene(matches: &[&Value], corpus: &[Value]) -> Value {
    if !matches.iter().any(|r| coastal(r)) {
        return Value::Null;
    }
    let mut source: Vec<_> = corpus.iter().filter(|r| coastal(r)).collect();
    source.sort_by_key(|r| r["original_regional_context"]["section_number"].as_u64());
    let audit: Value = serde_json::from_str(RAW).expect("reviewed source audit");
    let bars: Vec<_> = source.iter().enumerate().map(|(i, row)| {
        let width = row["approximate_width_km"].as_f64().expect("reviewed width");
        json!({"id":row["id"],"section_number":row["original_regional_context"]["section_number"],
            "width_km":width,"x":125,"y":44+i*44,"width":width/175.0*525.0,"height":24,
            "matching":matches.iter().any(|r| r["id"]==row["id"]),"record":row})
    }).collect();
    json!({"kind":"coastal_composite_widths","title":"Antarctic Coastal Current · seven composite sections",
        "scope":"Spatial composites of historical seal profiles, ordered east to west. These are not seasonal states or annual width limits. Numerical width uncertainty is unknown.",
        "view_box":[0,0,760,390],"axis_max_km":175,"ticks":[0,25,50,75,100,125,150,175],
        "bars":bars,"source_image":audit["source_figure"],"source_url":audit["measurements"][0]["source_url"],
        "source_citation":audit["measurements"][0]["source_citation"],
        "method":"Coast or ice-shelf face to the 15% depth-integrated velocity edge. Geostrophic reference: 400 m; integration: surface to the variable 34.4 psu isohaline.",
        "sampling_note":"Table 1 has more summer than winter profiles in sections 1 and 6. Section 6 conflicts with the prose assertion that all sections except 1 are winter-dominated. Counts are preserved.",
        "property_note":"Depth ranges and transport bootstrap errors are not width uncertainty. Cross-shelf transect length is not along-current length. Negative transport and velocity indicate westward flow. Spatial mean geostrophic speeds are source diagnostics to interpret cautiously.",
        "audit_file":SOURCE})
}
pub(crate) fn full(corpus: &[Value]) -> Value {
    let matches: Vec<_> = corpus.iter().filter(|r| coastal(r)).collect();
    scene(&matches, corpus)
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn filtered_query_keeps_complete_spatial_context_and_common_axis() {
        let audit: Value = serde_json::from_str(RAW).unwrap();
        let rows = audit["measurements"].as_array().unwrap();
        let result = scene(&[&rows[5]], rows);
        assert_eq!(result["bars"].as_array().unwrap().len(), 7);
        assert_eq!(result["axis_max_km"], 175);
        assert_eq!(result["bars"][5]["matching"], true);
        assert_eq!(result["bars"][0]["matching"], false);
        assert_eq!(
            result["bars"][5]["record"]["original_regional_context"]["source_properties"]["summer_profiles"],
            150
        );
        assert_eq!(
            result["bars"][5]["record"]["original_regional_context"]["sampling_prose_discrepancy"],
            true
        );
        assert!(scene(&[], rows).is_null());
    }
}
