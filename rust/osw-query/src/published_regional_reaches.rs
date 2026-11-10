//! Source-reported regional reach cannot become a whole-current dimension.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::sync::OnceLock;

const FILE: &str = "research/published-regional-reaches-query-contract-v1.json";
const RAW: &str =
    include_str!("../../../research/published-regional-reaches-query-contract-v1.json");
const HELPER: &str = include_str!("../../../analysis/published_regional_reaches_query.py");
const CATALOG: &str = include_str!("../../../almanac/index-catalog.json");
const ID: &str = "regional-reach:algerian:arnone-1990";
const ENTITY: &str = "current:algerian";
const COLLECTION: &str = "current_regional_reaches";

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
            return Err(format!("Regional-reach source catalogue changed: {path}"));
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
        c["record"]["source_file"].as_str().unwrap(),
    ];
    let mentions = |row: &Value| {
        [
            "id",
            "source_id",
            "method_source_id",
            "source_file",
            "regional_reach_id",
        ]
        .iter()
        .any(|field| {
            row[*field]
                .as_str()
                .is_some_and(|text| markers.contains(&text))
        }) || row["source_ids"]
            .as_array()
            .is_some_and(|ids| markers.iter().any(|id| ids.contains(&json!(id))))
    };
    let promoted = [
        "measurements",
        "widths",
        "length_assessments",
        "geometries",
        "geometry_frames",
        "reference_routes",
        "current_dimension_samples",
        "current_section_measurements",
        "width_samples",
    ]
    .iter()
    .any(|name| rows(name).iter().any(&mentions));
    let joined = rows("objects").iter().any(|row| {
        row["regional_reach_ids"]
            .as_array()
            .is_some_and(|ids| ids.contains(&json!(ID)))
    });
    let present = !inputs[FILE].is_null()
        || promoted
        || joined
        || rows(COLLECTION).iter().any(&mentions)
        || rows("sources").iter().any(&mentions)
        || rows("claims")
            .iter()
            .any(|row| row["target_id"] == ID || row["source_id"] == c["source_record"]["id"]);
    if !present {
        return Ok(());
    }
    if promoted {
        return Err(
            "Regional reach is not a whole-current length, width, geometry or seasonal observation"
                .into(),
        );
    }
    if inputs[FILE] != pin(RAW)
        || inputs["analysis/published_regional_reaches_query.py"] != pin(HELPER)
    {
        return Err("Regional-reach query contract/helper changed".into());
    }
    for (path, expected) in c["input_sha256"].as_object().unwrap() {
        if inputs[path] != *expected {
            return Err(format!("Regional-reach dependency changed: {path}"));
        }
    }
    static SOURCE_CATALOG: OnceLock<Value> = OnceLock::new();
    catalogue(
        c,
        inputs,
        SOURCE_CATALOG.get_or_init(|| serde_json::from_str(CATALOG).unwrap()),
    )?;
    for (name, expected) in [
        (COLLECTION, &c["record"]),
        ("claims", &c["claim"]),
        ("sources", &c["source_record"]),
        ("sources", &c["method_source"]),
    ] {
        let found = rows(name)
            .iter()
            .filter(|row| row["id"] == expected["id"])
            .collect::<Vec<_>>();
        if found.len() != 1 || found[0] != expected {
            return Err(format!("Regional-reach record changed: {name}"));
        }
    }
    let owners = rows("objects")
        .iter()
        .filter(|row| row["id"] == ENTITY)
        .collect::<Vec<_>>();
    if owners.len() != 1 {
        return Err("Missing/duplicate regional-reach owner".into());
    }
    let owner = owners[0];
    if !owner["regional_reach_ids"]
        .as_array()
        .is_some_and(|ids| ids.iter().filter(|id| **id == json!(ID)).count() == 1)
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
        return Err(
            "Regional-reach card provenance, source reference or navigation changed".into(),
        );
    }
    let ids = owner["source_ids"].as_array().unwrap();
    let unique = ids
        .iter()
        .filter_map(Value::as_str)
        .collect::<std::collections::BTreeSet<_>>();
    if owner["linked_source_count"].as_u64() != Some(ids.len() as u64)
        || unique.len() != ids.len()
        || ids.iter().any(|id| {
            rows("sources")
                .iter()
                .filter(|row| row["id"] == *id)
                .count()
                != 1
        })
    {
        return Err("Regional-reach source count or registered references changed".into());
    }
    if rows("objects").iter().any(|row| {
        row["id"] != ENTITY
            && row["regional_reach_ids"]
                .as_array()
                .is_some_and(|ids| ids.contains(&json!(ID)))
    }) {
        return Err("Regional reach attached to a different current".into());
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
            collections: [(COLLECTION.into(), vec![c["record"].clone()]), ("claims".into(), vec![c["claim"].clone()]),
                ("sources".into(), vec![c["source_record"].clone(),c["method_source"].clone()]),
                ("objects".into(), vec![json!({"id":ENTITY,"regional_reach_ids":[ID],
                    "source_ids":[c["source_record"]["id"],c["method_source"]["id"]],"linked_source_count":2,"evidence_links":c["card_links"]})])].into() }
    }
    #[test]
    fn complete_admission_and_unrelated_legacy_pass() {
        validate(&fixture()).unwrap();
        let mut b = fixture();
        b.collections.clear();
        b.manifest = json!({});
        validate(&b).unwrap();
    }
    #[test]
    fn rejects_scope_changes_and_partial_admissions() {
        for name in [COLLECTION, "claims", "sources", "objects"] {
            let mut b = fixture();
            b.collections.remove(name);
            assert!(validate(&b).is_err());
            let mut b = fixture();
            let row = b.collections[name][0].clone();
            b.collections.get_mut(name).unwrap().push(row);
            assert!(validate(&b).is_err());
        }
        for (field, value) in [
            ("constraint", json!({"threshold_km":300,"relation":"ge"})),
            ("physical_width_admitted", json!(true)),
            ("source_file_sha256", json!("changed")),
        ] {
            let mut b = fixture();
            b.collections.get_mut(COLLECTION).unwrap()[0][field] = value;
            assert!(validate(&b).is_err());
        }
    }
    #[test]
    fn rejects_physical_promotion_and_broken_owner_or_source_pins() {
        for name in ["widths", "measurements", "length_assessments", "geometries"] {
            let mut b = fixture();
            b.collections.insert(
                name.into(),
                vec![json!({"source_id":contract()["source_record"]["id"],"value":300})],
            );
            assert!(validate(&b).is_err());
        }
        for field in ["regional_reach_ids", "source_ids", "evidence_links"] {
            let mut b = fixture();
            b.collections.get_mut("objects").unwrap()[0][field] = json!([]);
            assert!(validate(&b).is_err());
        }
        let mut b = fixture();
        b.collections.get_mut("objects").unwrap()[0]["linked_source_count"] = json!(999);
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.manifest["input_sha256"][FILE] = json!("changed");
        assert!(validate(&b).is_err());
        let mut catalog: Value = serde_json::from_str(CATALOG).unwrap();
        catalog["documents"]
            .as_array_mut()
            .unwrap()
            .retain(|d| d["path"] != FILE);
        assert!(catalogue(contract(), &fixture().manifest["input_sha256"], &catalog).is_err());
    }
}
