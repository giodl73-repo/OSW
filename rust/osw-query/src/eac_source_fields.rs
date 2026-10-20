//! Processed source fields remain source evidence, with exact lazy-query binding.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
pub const ID: &str = "diagnostic:eac-csiro100m-source-fields";
const FILE: &str = "research/eac-csiro-v23-100m-source-quality.json";
const RAW: &str = include_str!("../../../research/eac-csiro-v23-100m-source-quality.json");
const CONTRACT_FILE: &str = "research/eac-csiro-v23-100m-source-query-contract.json";
const CONTRACT: &str =
    include_str!("../../../research/eac-csiro-v23-100m-source-query-contract.json");
const FIGURE_FILE: &str = "research/eac-csiro-v23-100m-source-fields-figure.json";
const FIGURE: &str = include_str!("../../../research/eac-csiro-v23-100m-source-fields-figure.json");
const HELPER: &str = include_str!("../../../analysis/eac_source_fields.py");
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
fn document() -> Value {
    serde_json::from_str(RAW).unwrap()
}
fn contract() -> Value {
    serde_json::from_str(CONTRACT).unwrap()
}
fn figure() -> Value {
    serde_json::from_str(FIGURE).unwrap()
}
fn record(doc: &Value) -> Value {
    json!({"id":ID,"label":"East Australian Current daily100m source fields","entity_id":"current:east-australian",
        "current_id":"east-australian","status":doc["status"],"rank_eligible":false,"source_file":FILE,
        "source_file_sha256":pin(RAW),"source_json":RAW,"document":doc})
}
pub fn validate(bundle: &crate::Bundle) -> Result<(), String> {
    let empty = Vec::new();
    let diagnostics = bundle.collections.get("diagnostics").unwrap_or(&empty);
    let widths = bundle.collections.get("widths").unwrap_or(&empty);
    let c = contract();
    let profile_file = c["raw_profile_file"].as_str().unwrap();
    let promoted = widths.iter().any(|w| {
        w.to_string().contains(FILE)
            || w.to_string().contains(profile_file)
            || w["diagnostic_id"] == ID
    });
    let present = bundle.manifest["input_sha256"].get(FILE).is_some()
        || diagnostics.iter().any(|d| {
            d["id"] == ID || d["document"]["schema"] == "osw.eac-fixed-depth-source-quality.v1"
        })
        || promoted;
    if !present {
        return Ok(());
    }
    let doc = document();
    let fig = figure();
    let inputs = &bundle.manifest["input_sha256"];
    if inputs[FILE] != pin(RAW)
        || inputs[CONTRACT_FILE] != pin(CONTRACT)
        || inputs[FIGURE_FILE] != pin(FIGURE)
        || inputs["analysis/eac_source_fields.py"] != pin(HELPER)
        || inputs[profile_file] != c["raw_profile_sha256"]
    {
        return Err("EAC exact source/contract/figure binding changed".into());
    }
    for (path, expected) in c["input_sha256"].as_object().unwrap() {
        if inputs[path] != *expected {
            return Err("EAC source-view dependency changed".into());
        }
    }
    if inputs[fig["generator_file"].as_str().unwrap()] != fig["generator_sha256"] {
        return Err("EAC source figure operator changed".into());
    }
    for asset in fig["figures"].as_object().unwrap().values() {
        if inputs[asset["file"].as_str().unwrap()] != asset["sha256"] {
            return Err("EAC source figure asset changed".into());
        }
    }
    let found = diagnostics
        .iter()
        .filter(|d| d["id"] == ID)
        .collect::<Vec<_>>();
    if found.len() != 1 || *found[0] != record(&doc) {
        return Err("EAC source quality projection changed".into());
    }
    let owners = bundle.collections.get("objects").unwrap_or(&empty);
    let owner = owners
        .iter()
        .find(|o| o["id"] == "current:east-australian")
        .ok_or("Missing EAC source owner")?;
    if !owner["diagnostic_ids"]
        .as_array()
        .is_some_and(|ids| ids.contains(&json!(ID)))
    {
        return Err("Missing EAC source diagnostic join".into());
    }
    if promoted {
        return Err("Processed source fields cannot become inventory current widths".into());
    }
    Ok(())
}
pub fn scene(bundle: &crate::Bundle) -> Value {
    if !bundle
        .collections
        .get("diagnostics")
        .into_iter()
        .flatten()
        .any(|d| d["id"] == ID)
    {
        return Value::Null;
    }
    let doc = document();
    let c = contract();
    let fig = figure();
    let fields=[("UCUR","Eastward velocity","m/s"),("VCUR","Northward velocity","m/s"),
        ("TEMP","Temperature","°C"),("PSAL","Practical salinity","1")].into_iter().map(|(name,label,unit)| {
        let error=doc["fields"][format!("{name}_uncertainty")]["maximum_finite"].as_f64().unwrap();
        let low=doc["fields"][name]["minimum_finite"].as_f64().unwrap()-error;
        let high=doc["fields"][name]["maximum_finite"].as_f64().unwrap()+error;
        let pad=(high-low)*0.05;
        json!({"key":name,"label":label,"unit":unit,"uncertainty_key":format!("{name}_uncertainty"),"y_domain":[low-pad,high+pad]})
    }).collect::<Vec<_>>();
    json!({"kind":"eac_daily_source_fields","title":"East Australian Current: daily100m source fields",
        "diagnostic_id":ID,"source_file":FILE,"source_sha256":pin(RAW),"raw_source_file":c["raw_profile_file"],
        "raw_source_sha256":c["raw_profile_sha256"],"source_url":doc["source_url"],"source_citation":doc["source_citation"],
        "figure_file":fig["figures"][".svg"]["file"],"figure_sha256":fig["figures"][".svg"]["sha256"],
        "figure_alt":"Eight daily source-field and provider-uncertainty panels at100m,2012–2022, preserve629missing dates. A fixed WGS84 processing grid and prescribed bottom zeros are shown. No physical current widths or annual extrema are admitted.",
        "fields":fields,"months":doc["monthly_support"],"geometry":doc["fixed_source_geometry"],"core_spans":crate::eac_core_spans::scene(bundle),
        "method_scope":doc["method_scope"],"source_bottom_support":doc["source_bottom_support"],
        "documentary_disagreements":doc["documentary_disagreements"],"profiles":3770,"profiles_with_data":3141,"missing_profiles":629})
}
pub fn query(matches: &[&Value], bundle: &crate::Bundle) -> Value {
    if matches
        .iter()
        .any(|r| r["id"] == ID || r["id"] == crate::eac_core_spans::ID)
    {
        scene(bundle)
    } else {
        Value::Null
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> crate::Bundle {
        let c = contract();
        let doc = document();
        let fig = figure();
        let mut inputs = c["input_sha256"].clone();
        inputs[FILE] = json!(pin(RAW));
        inputs[CONTRACT_FILE] = json!(pin(CONTRACT));
        inputs[FIGURE_FILE] = json!(pin(FIGURE));
        inputs["analysis/eac_source_fields.py"] = json!(pin(HELPER));
        inputs[c["raw_profile_file"].as_str().unwrap()] = c["raw_profile_sha256"].clone();
        inputs[fig["generator_file"].as_str().unwrap()] = fig["generator_sha256"].clone();
        for asset in fig["figures"].as_object().unwrap().values() {
            inputs[asset["file"].as_str().unwrap()] = asset["sha256"].clone();
        }
        crate::Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest: json!({"input_sha256":inputs}),
            collections: std::collections::BTreeMap::from([
                ("diagnostics".into(), vec![record(&doc)]),
                (
                    "objects".into(),
                    vec![json!({"id":"current:east-australian","diagnostic_ids":[ID]})],
                ),
                ("widths".into(), vec![]),
            ]),
        }
    }
    #[test]
    fn source_scene_keeps_calendar_missing_and_uncertainty_scope() {
        let b = fixture();
        assert!(validate(&b).is_ok());
        let s = scene(&b);
        assert_eq!(s["months"].as_array().unwrap().len(), 124);
        assert_eq!(s["missing_profiles"], 629);
        assert_eq!(s["fields"].as_array().unwrap().len(), 4);
        assert!(s.get("raw_profiles").is_none());
        assert_eq!(
            s["method_scope"]["provider_uncertainty_names_are_a_universal_confidence_convention"],
            false
        );
    }
    #[test]
    fn source_contract_figures_and_exact_quality_are_frozen() {
        for mode in ["source", "raw", "bottom", "confidence", "join"] {
            let mut bad = fixture();
            match mode {
                "source" => bad.manifest["input_sha256"][FILE] = json!("0".repeat(64)),
                "raw" => {
                    bad.manifest["input_sha256"][contract()["raw_profile_file"].as_str().unwrap()] =
                        json!("0".repeat(64))
                }
                "bottom" => {
                    bad.collections.get_mut("diagnostics").unwrap()[0]["document"]["finite_paired_velocity_cells_at_or_below_source_bottom"] =
                        json!(0)
                }
                "confidence" => {
                    bad.collections.get_mut("diagnostics").unwrap()[0]["document"]["method_scope"]
                        ["provider_uncertainty_names_are_a_universal_confidence_convention"] =
                        json!(true)
                }
                _ => bad.collections.get_mut("objects").unwrap()[0]["diagnostic_ids"] = json!([]),
            }
            assert!(validate(&bad).is_err(), "{mode}");
        }
    }
    #[test]
    fn source_width_laundering_rejects_after_join_erasure() {
        let mut bad = fixture();
        bad.collections.get_mut("objects").unwrap().clear();
        bad.collections.get_mut("diagnostics").unwrap().clear();
        bad.collections
            .get_mut("widths")
            .unwrap()
            .push(json!({"source_file":contract()["raw_profile_file"],"approximate_width_km":173}));
        assert!(validate(&bad).is_err());
    }
}
