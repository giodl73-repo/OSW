//! Pinned complete source evidence, never an inferred current dimension.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::sync::OnceLock;

const ID: &str = "diagnostic:caribbean-ru29-2024-source-fields";
const ENTITY: &str = "current:caribbean";
const FILE: &str = "research/caribbean-ru29-query-contract-v1.json";
const RAW: &str = include_str!("../../../research/caribbean-ru29-query-contract-v1.json");
const HELPER: &str = include_str!("../../../analysis/caribbean_ru29_query.py");
const CATALOG: &str = include_str!("../../../almanac/index-catalog.json");

fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}

fn contract() -> &'static Value {
    static DOCUMENT: OnceLock<Value> = OnceLock::new();
    DOCUMENT.get_or_init(|| serde_json::from_str(RAW).unwrap())
}

fn catalogue(c: &Value, inputs: &Value, catalog: &Value) -> Result<(), String> {
    for path in c["source_documents"].as_array().unwrap() {
        let path = path.as_str().unwrap();
        let matches = catalog["documents"]
            .as_array()
            .unwrap()
            .iter()
            .filter(|row| row["path"] == path)
            .collect::<Vec<_>>();
        if matches.len() != 1 || matches[0]["source_sha256"] != inputs[path] {
            return Err(format!(
                "Caribbean source catalogue binding changed: {path}"
            ));
        }
    }
    Ok(())
}

pub fn validate(bundle: &crate::Bundle) -> Result<(), String> {
    let c = contract();
    let rows = |name: &str| {
        bundle
            .collections
            .get(name)
            .map(Vec::as_slice)
            .unwrap_or(&[])
    };
    let inputs = &bundle.manifest["input_sha256"];
    let markers = [
        ID,
        c["source_record"]["id"].as_str().unwrap(),
        c["method_source"]["id"].as_str().unwrap(),
        c["diagnostic"]["source_file"].as_str().unwrap(),
        c["card_context"]["source_mirror"].as_str().unwrap(),
    ];
    let promoted = [
        "widths",
        "measurements",
        "length_assessments",
        "current_dimension_samples",
        "current_section_measurements",
        "current_velocity_samples",
        "geometries",
        "geometry_frames",
        "reference_routes",
    ]
    .iter()
    .any(|name| {
        rows(name).iter().any(|row| {
            [
                "id",
                "source_id",
                "method_source_id",
                "diagnostic_id",
                "source_file",
                "source_mirror",
            ]
            .iter()
            .any(|key| {
                row[*key]
                    .as_str()
                    .is_some_and(|text| markers.iter().any(|marker| text.contains(*marker)))
            }) || row["source_ids"].as_array().is_some_and(|ids| {
                ids.iter()
                    .any(|id| id.as_str().is_some_and(|text| markers.contains(&text)))
            })
        })
    });
    let present = !inputs[FILE].is_null()
        || promoted
        || rows("diagnostics").iter().any(|r| r["id"] == ID)
        || rows("sources")
            .iter()
            .any(|r| r["id"] == markers[1] || r["id"] == markers[2])
        || rows("objects")
            .iter()
            .any(|r| r["id"] == ENTITY && !r["provider_velocity_source"].is_null());
    if !present {
        return Ok(());
    }
    if promoted {
        return Err("Caribbean provider source evidence cannot become physical dimensions or reconstructed observations".into());
    }
    if inputs[FILE] != pin(RAW) || inputs["analysis/caribbean_ru29_query.py"] != pin(HELPER) {
        return Err("Caribbean source admission contract/helper changed".into());
    }
    for (path, expected) in c["input_sha256"].as_object().unwrap() {
        if inputs[path] != *expected {
            return Err(format!("Caribbean source dependency changed: {path}"));
        }
    }
    static SOURCE_CATALOG: OnceLock<Value> = OnceLock::new();
    catalogue(
        c,
        inputs,
        SOURCE_CATALOG.get_or_init(|| serde_json::from_str(CATALOG).unwrap()),
    )?;
    for (collection, expected) in [
        ("diagnostics", &c["diagnostic"]),
        ("sources", &c["source_record"]),
        ("sources", &c["method_source"]),
    ] {
        let matches = rows(collection)
            .iter()
            .filter(|row| row["id"] == expected["id"])
            .collect::<Vec<_>>();
        if matches.len() != 1 || matches[0] != expected {
            return Err(format!("Caribbean source record changed: {collection}"));
        }
    }
    let owners = rows("objects")
        .iter()
        .filter(|row| row["id"] == ENTITY)
        .collect::<Vec<_>>();
    if owners.len() != 1 {
        return Err("Missing/duplicate Caribbean source owner".into());
    }
    let owner = owners[0];
    if owner["provider_velocity_source"] != c["card_context"]
        || !owner["diagnostic_ids"]
            .as_array()
            .is_some_and(|ids| ids.contains(&json!(ID)))
        || !owner["source_ids"].as_array().is_some_and(|ids| {
            ids.contains(&c["source_record"]["id"]) && ids.contains(&c["method_source"]["id"])
        })
        || !owner["evidence_links"].as_array().is_some_and(|links| {
            c["card_links"]
                .as_array()
                .unwrap()
                .iter()
                .all(|link| links.contains(link))
        })
    {
        return Err("Caribbean source card provenance/join/scope changed".into());
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> crate::Bundle {
        let c = contract();
        let mut inputs = c["input_sha256"].clone();
        inputs[FILE] = json!(pin(RAW));
        crate::Bundle { schema: "osw.query-bundle.v1".into(), manifest: json!({"input_sha256":inputs}),
            collections: [
                ("diagnostics".into(), vec![c["diagnostic"].clone()]),
                ("sources".into(), vec![c["source_record"].clone(),c["method_source"].clone()]),
                ("objects".into(), vec![json!({"id":ENTITY,"provider_velocity_source":c["card_context"],
                    "diagnostic_ids":[ID],"source_ids":[c["source_record"]["id"],c["method_source"]["id"]],
                    "evidence_links":c["card_links"]})])].into() }
    }
    #[test]
    fn complete_source_admission_and_unrelated_legacy_bundle_pass() {
        validate(&fixture()).unwrap();
        let mut legacy = fixture();
        legacy.manifest = json!({});
        legacy.collections.clear();
        legacy.collections.insert(
            "objects".into(),
            vec![json!({"id":"current:other","provider_velocity_source":{}})],
        );
        validate(&legacy).unwrap();
    }
    #[test]
    fn rejects_changed_values_scope_source_records_and_owner_joins() {
        for (collection, index, field, value) in [
            ("diagnostics", 0, "rank_eligible", json!(true)),
            ("diagnostics", 0, "physical_width_admitted", json!(true)),
            ("diagnostics", 0, "source_json", json!("truncated")),
            ("sources", 0, "license", json!("unverified")),
            ("objects", 0, "provider_velocity_source", json!({})),
            ("objects", 0, "source_ids", json!([])),
            ("objects", 0, "diagnostic_ids", json!([])),
            ("objects", 0, "evidence_links", json!([])),
        ] {
            let mut b = fixture();
            b.collections.get_mut(collection).unwrap()[index][field] = value;
            assert!(validate(&b).is_err(), "{collection}/{field}");
        }
    }
    #[test]
    fn rejects_missing_dependencies_duplicate_records_and_dimension_promotion() {
        let mut b = fixture();
        b.manifest["input_sha256"][FILE] = json!("changed");
        assert!(validate(&b).is_err());
        for collection in ["diagnostics", "sources", "objects"] {
            let mut b = fixture();
            let row = b.collections[collection][0].clone();
            b.collections.get_mut(collection).unwrap().push(row);
            assert!(validate(&b).is_err());
            let mut b = fixture();
            b.collections.remove(collection);
            assert!(validate(&b).is_err());
        }
        let mut b = fixture();
        b.collections.insert(
            "widths".into(),
            vec![json!({"source_id":contract()["source_record"]["id"],"width_km":600})],
        );
        assert!(validate(&b).is_err());
    }
    #[test]
    fn rejects_dropped_or_changed_source_catalogue_documents() {
        let b = fixture();
        let mut catalog: Value = serde_json::from_str(CATALOG).unwrap();
        let mirror = contract()["card_context"]["source_mirror"]
            .as_str()
            .unwrap();
        let docs = catalog["documents"].as_array_mut().unwrap();
        docs.iter_mut().find(|d| d["path"] == mirror).unwrap()["source_sha256"] = json!("changed");
        assert!(catalogue(contract(), &b.manifest["input_sha256"], &catalog).is_err());
        let mut catalog: Value = serde_json::from_str(CATALOG).unwrap();
        catalog["documents"]
            .as_array_mut()
            .unwrap()
            .retain(|d| d["path"] != mirror);
        assert!(catalogue(contract(), &b.manifest["input_sha256"], &catalog).is_err());
    }
}
