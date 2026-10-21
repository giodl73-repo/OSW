//! Reviewed calculations remain evidence, with no width/identity promotion.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};

const PATH: &str = "research/current-research-evidence-registry.json";
const RAW: &str = include_str!("../../../research/current-research-evidence-registry.json");
const COMPOSITE_CONTOURS: &str = "research/loop-durante-2026-composite-contour-paths.json";
const STUDIES: [(&str, &str); 8] = [
    (
        "research/source-data/loop-durante-2026-v0/quality.json",
        include_str!("../../../research/source-data/loop-durante-2026-v0/quality.json"),
    ),
    (
        "research/aleutian-p14n-1993-component-spans.json",
        include_str!("../../../research/aleutian-p14n-1993-component-spans.json"),
    ),
    (
        "research/aleutian-p14n-1993-hydrography-correspondence.json",
        include_str!("../../../research/aleutian-p14n-1993-hydrography-correspondence.json"),
    ),
    (
        "research/aleutian-p14n-1993-observed-vector-section.json",
        include_str!("../../../research/aleutian-p14n-1993-observed-vector-section.json"),
    ),
    (
        "research/pacific-necc-paired-vector-direction-evidence.json",
        include_str!("../../../research/pacific-necc-paired-vector-direction-evidence.json"),
    ),
    (
        "research/source-data/norkyst-ingoy-months-2024/section-diagnostic-year.json",
        include_str!(
            "../../../research/source-data/norkyst-ingoy-months-2024/section-diagnostic-year.json"
        ),
    ),
    (
        "research/indian-secc-eof-classification-feasibility.json",
        include_str!("../../../research/indian-secc-eof-classification-feasibility.json"),
    ),
    (
        "research/redsox-lower-nc-dated-section-diagnostic.json",
        include_str!("../../../research/redsox-lower-nc-dated-section-diagnostic.json"),
    ),
];

fn registry() -> Value {
    serde_json::from_str(RAW).expect("reviewed current research registry")
}

const SUPPORT_ONLY: [&str; 7] = [
    "research/redsox-winter-section3-component-spans.json",
    COMPOSITE_CONTOURS,
    "research/loop-durante-2026-source-view.json",
    "research/aleutian-p14n-1993-native-product-metadata.json",
    "research/aleutian-p14n-1993-native-vector-support.json",
    "research/aleutian-p14n-1993-underway-averages.json",
    "research/aleutian-p14n-1993-run-composite.json",
];

fn is_research_source(value: &Value) -> bool {
    STUDIES.iter().any(|(path, _)| value == *path) || SUPPORT_ONLY.iter().any(|path| value == *path)
}

fn mentions_research(raw: &str) -> bool {
    raw.contains(PATH)
        || STUDIES.iter().any(|(path, _)| raw.contains(path))
        || SUPPORT_ONLY.iter().any(|path| raw.contains(path))
}

fn expected(scene: &Value, registry: &Value) -> Value {
    let path = scene["source_file"].as_str().unwrap();
    let raw = STUDIES.iter().find(|(p, _)| *p == path).unwrap().1;
    json!({"id":scene["diagnostic_id"],"label":format!("{} research evidence",scene["label"].as_str().unwrap()),
        "entity_id":format!("current:{}",scene["current_id"].as_str().unwrap()),"current_id":scene["current_id"],
        "status":registry["status"],"rank_eligible":false,"source_file":path,
        "source_file_sha256":format!("{:x}",Sha256::digest(raw.as_bytes())),
        "source_json":raw,"document":serde_json::from_str::<Value>(raw).unwrap(),"research_evidence":scene})
}

pub(crate) fn validate(bundle: &crate::Bundle) -> Result<(), String> {
    for collection in ["reference_routes", "length_assessments", "measurements"] {
        if bundle
            .collections
            .get(collection)
            .into_iter()
            .flatten()
            .any(|row| row.to_string().contains(COMPOSITE_CONTOURS))
        {
            return Err(
                "Composite contour evidence cannot become an admitted route or length measurement"
                    .into(),
            );
        }
    }
    let doc = registry();
    let scenes = doc["scenes"]
        .as_array()
        .ok_or("Missing current research scenes")?;
    let objects = bundle
        .collections
        .get("objects")
        .map(Vec::as_slice)
        .unwrap_or(&[]);
    let diagnostics = bundle
        .collections
        .get("diagnostics")
        .map(Vec::as_slice)
        .unwrap_or(&[]);
    let present = bundle.manifest["input_sha256"].get(PATH).is_some()
        || diagnostics.iter().any(|row| {
            row.get("research_evidence").is_some()
                || is_research_source(&row["source_file"])
                || scenes
                    .iter()
                    .any(|scene| row["id"] == scene["diagnostic_id"])
        })
        || bundle
            .collections
            .get("widths")
            .into_iter()
            .flatten()
            .any(|r| mentions_research(&r.to_string()))
        || objects.iter().any(|o| {
            scenes
                .iter()
                .any(|s| o["id"] == format!("current:{}", s["current_id"].as_str().unwrap()))
        });
    if !present {
        return Ok(());
    }
    if bundle.manifest["input_sha256"][PATH] != format!("{:x}", Sha256::digest(RAW.as_bytes())) {
        return Err("Current research registry binding changed".into());
    }
    for (path, pin) in doc["input_sha256"]
        .as_object()
        .ok_or("Missing research source dependencies")?
    {
        if bundle.manifest["input_sha256"][path] != *pin {
            return Err(format!("Current research dependency changed: {path}"));
        }
    }
    for scene in scenes {
        let rows: Vec<_> = diagnostics
            .iter()
            .filter(|r| r["id"] == scene["diagnostic_id"])
            .collect();
        if rows.len() != 1 || rows[0] != &expected(scene, &doc) {
            return Err("Current research evidence missing, rebound or promoted".into());
        }
        let owner = format!("current:{}", scene["current_id"].as_str().unwrap());
        let object = objects
            .iter()
            .find(|o| o["id"] == owner)
            .ok_or("Missing current research owner")?;
        if object["research_evidence_ids"] != json!([scene["diagnostic_id"]]) {
            return Err("Current research owner evidence binding changed".into());
        }
    }
    for row in diagnostics {
        let owned =
            is_research_source(&row["source_file"]) || row.get("research_evidence").is_some();
        if owned && !scenes.iter().any(|s| s["diagnostic_id"] == row["id"]) {
            return Err("Unexpected duplicate current research evidence".into());
        }
    }
    if bundle
        .collections
        .get("widths")
        .into_iter()
        .flatten()
        .any(|row| {
            let raw = row.to_string();
            mentions_research(&raw)
        })
    {
        return Err("Research evidence cannot become an inventory width measurement".into());
    }
    Ok(())
}

pub(crate) fn scenes(bundle: &crate::Bundle) -> Value {
    let doc = registry();
    let mut result = json!({});
    for scene in doc["scenes"].as_array().unwrap() {
        if bundle
            .collections
            .get("diagnostics")
            .into_iter()
            .flatten()
            .any(|r| r["id"] == scene["diagnostic_id"])
        {
            result[scene["current_id"].as_str().unwrap()] = scene.clone();
        }
    }
    result
}

pub(crate) fn query(matches: &[&Value], bundle: &crate::Bundle) -> Value {
    let all = scenes(bundle);
    let selected: Vec<_> = all
        .as_object()
        .unwrap()
        .values()
        .filter(|s| matches.iter().any(|r| r["id"] == s["diagnostic_id"]))
        .cloned()
        .collect();
    if selected.is_empty() {
        Value::Null
    } else {
        json!({"kind":"current_research_evidence_panels","scope":"Research calculations and source support; no whole-current width, annual extrema or physical geometry admitted.","scenes":selected})
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> crate::Bundle {
        let doc = registry();
        let mut manifest = json!({"input_sha256":doc["input_sha256"]});
        manifest["input_sha256"][PATH] = json!(format!("{:x}", Sha256::digest(RAW.as_bytes())));
        let studies = doc["scenes"].as_array().unwrap();
        crate::Bundle{schema:"osw.query-bundle.v1".into(),manifest,collections:std::collections::BTreeMap::from([
            ("objects".into(),studies.iter().map(|s|json!({"id":format!("current:{}",s["current_id"].as_str().unwrap()),"research_evidence_ids":[s["diagnostic_id"]]})).collect()),
            ("diagnostics".into(),studies.iter().map(|s|expected(s,&doc)).collect()),("widths".into(),vec![])])}
    }
    #[test]
    fn research_scenes_preserve_primary_and_physical_limits() {
        let bundle = fixture();
        assert!(validate(&bundle).is_ok());
        let all = scenes(&bundle);
        assert_eq!(
            all["red-sea-saline-overflow"]["whole_current_width_km"],
            Value::Null
        );
        assert_eq!(
            all["red-sea-saline-overflow"]["new_width_record_admitted"],
            false
        );
        assert_eq!(
            all["indian-south-equatorial-countercurrent"]["rank_eligible"],
            false
        );
    }
    #[test]
    fn observed_section_keeps_vectors_and_rejects_rehashed_changes() {
        let bundle = fixture();
        let rows = &bundle.collections["diagnostics"];
        let index = rows
            .iter()
            .position(|r| r["current_id"] == "aleutian")
            .unwrap();
        let doc = &rows[index]["document"]["hydrography_context"]["velocity_section"];
        assert_eq!(doc["retained_time_count"], 132);
        assert_eq!(doc["joint_valid_vector_positions"], 4030);
        assert_eq!(doc["new_width_record_admitted"], false);
        assert_eq!(doc["current_association_verified"], false);
        for field in ["whole_current_width_km", "annual_width_range_km"] {
            assert!(doc[field].is_null());
        }
        for mutation in ["velocity", "mask", "units", "annual", "association"] {
            let mut bad = fixture();
            let row = &mut bad.collections.get_mut("diagnostics").unwrap()[index];
            match mutation {
                "velocity" => {
                    row["document"]["hydrography_context"]["velocity_section"]["profiles"][0]["profile"]
                        [0]["eastward_m_s"] = json!(3)
                }
                "mask" => {
                    row["document"]["hydrography_context"]["velocity_section"]["profiles"][0]["profile"]
                        [0]["joint_valid"] = json!(false)
                }
                "units" => {
                    row["document"]["hydrography_context"]["velocity_section"]["provider_units"] =
                        json!("centimetres per second")
                }
                "annual" => row["document"]["annual_width_range_km"] = json!([1, 2]),
                _ => row["document"]["current_association_verified"] = json!(true),
            }
            let raw = row["document"].to_string();
            let pin = format!("{:x}", Sha256::digest(raw.as_bytes()));
            let path = row["source_file"].as_str().unwrap().to_string();
            row["source_json"] = json!(raw);
            row["source_file_sha256"] = json!(pin);
            bad.manifest["input_sha256"][path] = json!(pin);
            assert!(validate(&bad).is_err(), "{mutation}");
        }
    }
    #[test]
    fn research_row_promotion_and_deletion_reject() {
        let mut bundle = fixture();
        bundle.collections.get_mut("diagnostics").unwrap()[0]["rank_eligible"] = json!(true);
        assert!(validate(&bundle).is_err());
        let mut bundle = fixture();
        bundle.collections.get_mut("diagnostics").unwrap().pop();
        assert!(validate(&bundle).is_err());
    }

    #[test]
    fn native_support_widths_reject_even_after_owner_and_registry_erasure() {
        for path in SUPPORT_ONLY {
            let mut bundle = fixture();
            bundle.collections.get_mut("widths").unwrap().push(json!({"id":"unsupported-native-width","source_file":path,"approximate_width_km":100}));
            assert!(validate(&bundle).is_err(), "{path}");
            bundle.collections.get_mut("objects").unwrap().clear();
            bundle.collections.get_mut("diagnostics").unwrap().clear();
            bundle.manifest = json!({});
            assert!(validate(&bundle).is_err(), "orphan {path}");
        }
    }

    #[test]
    fn orphaned_research_cannot_bypass_validation_by_removing_owners_and_registry_pin() {
        let mut bundle = fixture();
        bundle.manifest["input_sha256"]
            .as_object_mut()
            .unwrap()
            .remove(PATH);
        bundle.collections.get_mut("objects").unwrap().clear();
        assert!(validate(&bundle).is_err());
    }
}
