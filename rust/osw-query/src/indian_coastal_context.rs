//! Reviewed source context is never a measured current dimension.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::BTreeSet;
use std::sync::OnceLock;

const FILE: &str = "research/indian-coastal-dimension-context-query-contract-v1.json";
const RAW: &str =
    include_str!("../../../research/indian-coastal-dimension-context-query-contract-v1.json");
const HELPER: &str = include_str!("../../../analysis/indian_coastal_dimension_context_v1.py");
const CATALOG: &str = include_str!("../../../almanac/index-catalog.json");
const OPERATOR: &str = "analysis/indian_coastal_dimension_context_v1.py";
const METHOD: &str = "source:indian-coastal-dimension-context-v1";
const VERSION_KEY: &str = "indian_coastal_dimension_context_version";
const OWNERS: [&str; 2] = ["current:east-african-coastal", "current:south-java"];
const CONTEXTS: [(&str, &str, &str); 2] = [
    (
        "current_regional_reaches",
        "regional_reach_ids",
        "reported_regional_reaches",
    ),
    (
        "current_cross_shore_context",
        "cross_shore_context_ids",
        "cross_shore_context",
    ),
];

fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}

fn contract() -> &'static Value {
    static DOCUMENT: OnceLock<Value> = OnceLock::new();
    DOCUMENT.get_or_init(|| serde_json::from_str(RAW).expect("compiled coastal context contract"))
}

fn mentions(value: &Value, markers: &BTreeSet<&str>) -> bool {
    match value {
        Value::String(text) => markers.contains(text.as_str()),
        Value::Array(items) => items.iter().any(|item| mentions(item, markers)),
        Value::Object(fields) => fields.values().any(|item| mentions(item, markers)),
        _ => false,
    }
}

fn decode_query(raw: &str) -> Option<String> {
    let mut decoded = Vec::with_capacity(raw.len());
    let mut bytes = raw.bytes();
    while let Some(byte) = bytes.next() {
        match byte {
            b'%' => {
                let hi = char::from(bytes.next()?).to_digit(16)?;
                let lo = char::from(bytes.next()?).to_digit(16)?;
                decoded.push((hi * 16 + lo) as u8);
            }
            b'+' => decoded.push(b' '),
            _ => decoded.push(byte),
        }
    }
    String::from_utf8(decoded).ok()
}

pub fn validate(bundle: &crate::Bundle) -> Result<(), String> {
    static DOCUMENT: OnceLock<Value> = OnceLock::new();
    validate_with_catalog(
        bundle,
        DOCUMENT.get_or_init(|| serde_json::from_str(CATALOG).unwrap()),
    )
}

fn validate_with_catalog(bundle: &crate::Bundle, catalog: &Value) -> Result<(), String> {
    let c = contract();
    let additions = c["additions"].as_object().unwrap();
    let rows = |name: &str| {
        bundle
            .collections
            .get(name)
            .map(Vec::as_slice)
            .unwrap_or(&[])
    };
    let markers: BTreeSet<&str> = additions
        .values()
        .flat_map(|group| group.as_array().unwrap())
        .flat_map(|row| [row["id"].as_str(), row["source_file"].as_str()])
        .flatten()
        .collect();
    let inputs = &bundle.manifest["input_sha256"];
    let active = !bundle.manifest[VERSION_KEY].is_null()
        || !inputs[FILE].is_null()
        || !inputs[OPERATOR].is_null()
        || bundle
            .collections
            .values()
            .flatten()
            .any(|row| mentions(row, &markers));
    if !active {
        return Ok(());
    }
    if bundle.manifest[VERSION_KEY] != c["version"]
        || inputs[FILE] != pin(RAW)
        || inputs[OPERATOR] != pin(HELPER)
    {
        return Err("Coastal source-context contract/helper changed".into());
    }
    for (path, expected) in c["input_sha256"].as_object().unwrap() {
        if inputs[path] != *expected {
            return Err(format!("Coastal source-context dependency changed: {path}"));
        }
    }
    for path in c["source_documents"].as_array().unwrap() {
        let path = path.as_str().unwrap();
        let found = catalog["documents"]
            .as_array()
            .into_iter()
            .flatten()
            .filter(|row| row["path"] == path)
            .collect::<Vec<_>>();
        if found.len() != 1 || found[0]["source_sha256"] != inputs[path] {
            return Err(format!(
                "Coastal context source catalogue missing/changed: {path}"
            ));
        }
    }
    for (name, expected) in additions {
        for record in expected.as_array().unwrap() {
            let found = rows(name)
                .iter()
                .filter(|row| row["id"] == record["id"])
                .collect::<Vec<_>>();
            if found.len() != 1 || found[0] != record {
                return Err(format!(
                    "Coastal source-context row missing/changed: {name}"
                ));
            }
        }
    }
    // A later editorial reference may cite the publication only after its complete
    // source-bound route, planning record and exact owner have been validated.
    let reviewed_reference = crate::south_java_reference::routes(&bundle.collections, &bundle.manifest)?;
    // All other references outside the admitted rows and owners remain forbidden.
    for (name, group) in &bundle.collections {
        for row in group {
            if !mentions(row, &markers) || name == "objects" {
                continue;
            }
            let exact = additions
                .get(name)
                .and_then(Value::as_array)
                .is_some_and(|expected| expected.contains(row));
            let reviewed_citation = !reviewed_reference.is_empty()
                && ((name == "reference_routes" && reviewed_reference.contains(row))
                    || (name == "route_decisions" && row["entity_id"] == "current:south-java"));
            if !exact && !reviewed_citation {
                return Err(format!(
                    "Coastal source context promoted or misattached in {name}"
                ));
            }
        }
    }
    for (index, (collection, field, capability)) in CONTEXTS.iter().enumerate() {
        let entity = OWNERS[index];
        let expected = &c["additions"][*collection][0];
        if rows("entities")
            .iter()
            .filter(|row| row["id"] == entity)
            .count()
            != 1
        {
            return Err("Missing/duplicate coastal context entity".into());
        }
        let owners = rows("objects")
            .iter()
            .filter(|row| row["id"] == entity)
            .collect::<Vec<_>>();
        if owners.len() != 1 || owners[0]["type"] != "named_current" {
            return Err("Missing/duplicate coastal context owner".into());
        }
        let owner = owners[0];
        let ids: Vec<Value> = rows(collection)
            .iter()
            .filter(|row| row["entity_id"] == entity)
            .map(|row| row["id"].clone())
            .collect();
        if owner[*field] != json!(ids)
            || owner["capabilities"][*capability].as_u64() != Some(ids.len() as u64)
            || ids.iter().filter(|id| **id == expected["id"]).count() != 1
        {
            return Err("Coastal context owner references/count changed".into());
        }
        let refs = owner["source_ids"]
            .as_array()
            .ok_or("Missing coastal source references")?;
        let unique: BTreeSet<&str> = refs.iter().filter_map(Value::as_str).collect();
        if unique.len() != refs.len()
            || owner["linked_source_count"].as_u64() != Some(refs.len() as u64)
            || !refs.contains(&expected["source_id"])
            || !refs.contains(&json!(METHOD))
            || refs.iter().any(|id| {
                rows("sources")
                    .iter()
                    .filter(|row| row["id"] == *id)
                    .count()
                    != 1
            })
        {
            return Err("Coastal context owner provenance changed".into());
        }
        let linked = owner["evidence_links"]
            .as_array()
            .into_iter()
            .flatten()
            .any(|link| {
                link["url"]
                    .as_str()
                    .and_then(|url| url.strip_prefix("query.html?q="))
                    .and_then(decode_query)
                    .and_then(|query| serde_json::from_str::<Value>(&query).ok())
                    .is_some_and(|query| {
                        query
                            == json!({"collection":collection,"filters":[
                    {"field":"id","op":"eq","value":expected["id"]}],"limit":1})
                    })
            });
        if !linked {
            return Err("Coastal source-context card query navigation missing".into());
        }
    }
    for owner in rows("objects") {
        if !OWNERS.iter().any(|id| owner["id"] == *id) && mentions(owner, &markers) {
            return Err("Coastal source context attached to another object".into());
        }
        for (index, (collection, field, _)) in CONTEXTS.iter().enumerate() {
            let expected = &c["additions"][*collection][0];
            if owner["id"] != OWNERS[index]
                && (owner[*field]
                    .as_array()
                    .is_some_and(|ids| ids.contains(&expected["id"]))
                    || owner["source_ids"]
                        .as_array()
                        .is_some_and(|ids| ids.contains(&expected["source_id"])))
            {
                return Err(
                    "Coastal context or scoped publication attached to the wrong current".into(),
                );
            }
        }
        if let Some(fields) = owner.as_object() {
            for (field, value) in fields {
                if ![
                    "source_ids",
                    "regional_reach_ids",
                    "cross_shore_context_ids",
                    "evidence_links",
                ]
                .contains(&field.as_str())
                    && !(field == "map_features" && owner["id"] == "current:south-java" && !reviewed_reference.is_empty())
                    && mentions(value, &markers)
                {
                    return Err("Coastal context attached to a physical owner field".into());
                }
            }
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn fixture() -> (crate::Bundle, Value) {
        let c = contract();
        let mut inputs = c["input_sha256"].clone();
        inputs[FILE] = json!(pin(RAW));
        let mut collections: std::collections::BTreeMap<String, Vec<Value>> = c["additions"]
            .as_object()
            .unwrap()
            .iter()
            .map(|(key, rows)| (key.clone(), rows.as_array().unwrap().clone()))
            .collect();
        let mut owners = vec![];
        for (index, (collection, field, capability)) in CONTEXTS.iter().enumerate() {
            let row = &c["additions"][*collection][0];
            let mut owner = json!({"id":OWNERS[index],"type":"named_current","linked_source_count":2,
                "source_ids":[row["source_id"],METHOD],"capabilities":{},"evidence_links":[{
                    "url":format!("query.html?q={}",json!({"collection":collection,"filters":[{
                        "field":"id","op":"eq","value":row["id"]}],"limit":1}))}]});
            owner[*field] = json!([row["id"]]);
            owner["capabilities"][*capability] = json!(1);
            owners.push(owner);
        }
        collections.insert("objects".into(), owners);
        collections.insert(
            "entities".into(),
            OWNERS.iter().map(|id| json!({"id":id})).collect(),
        );
        let catalog = json!({"documents":c["source_documents"].as_array().unwrap().iter().map(|path|
            json!({"path":path,"source_sha256":inputs[path.as_str().unwrap()]})).collect::<Vec<_>>()});
        let mut manifest = json!({"input_sha256":inputs});
        manifest[VERSION_KEY] = c["version"].clone();
        (
            crate::Bundle {
                schema: "osw.query-bundle.v1".into(),
                manifest,
                collections,
            },
            catalog,
        )
    }

    #[test]
    fn reviewed_reference_cites_context_without_promoting_or_reassigning_it() {
        let selected: crate::Bundle = serde_json::from_str(include_str!("../../../research/south-java-reference-runtime-fixture-v1.json")).unwrap();
        let (mut b, catalog) = fixture();
        for (key, value) in selected.manifest["input_sha256"].as_object().unwrap() {
            b.manifest["input_sha256"][key] = value.clone();
        }
        b.manifest["south_java_reference_delivery_v1"] = selected.manifest["south_java_reference_delivery_v1"].clone();
        for name in ["objects", "entities"] {
            let expected = selected.collections[name].iter().find(|r| r["id"] == "current:south-java").unwrap();
            *b.collections.get_mut(name).unwrap().iter_mut().find(|r| r["id"] == expected["id"]).unwrap() = expected.clone();
        }
        for name in ["route_decisions", "reference_routes"] {
            b.collections.insert(name.into(), selected.collections[name].clone());
        }
        let sources = b.collections.get_mut("sources").unwrap();
        for row in &selected.collections["sources"] {
            if row["id"].as_str().unwrap().starts_with("fixture:") { continue; }
            if let Some(prior) = sources.iter().find(|prior| prior["id"] == row["id"]) {
                assert_eq!(prior, row);
            } else { sources.push(row.clone()); }
        }
        while sources.len() < 211 {
            sources.push(json!({"id":format!("fixture:coastal-source:{}", sources.len())}));
        }
        assert_eq!(sources.len(), 211);
        validate_with_catalog(&b, &catalog).unwrap();
        for mode in ["physical", "receipt", "foreign-route", "foreign-map"] {
            let mut bad = crate::Bundle { schema: b.schema.clone(), manifest: b.manifest.clone(), collections: b.collections.clone() };
            match mode {
                "physical" => bad.collections.get_mut("reference_routes").unwrap().last_mut().unwrap()["physical_width_km"] = json!(15),
                "receipt" => { bad.manifest.as_object_mut().unwrap().remove("south_java_reference_delivery_v1"); },
                "foreign-route" => bad.collections.get_mut("reference_routes").unwrap().push(json!({"id":"invented", "source_id":METHOD})),
                "foreign-map" => bad.collections.get_mut("objects").unwrap().iter_mut()
                    .find(|r| r["id"] == "current:east-african-coastal").unwrap()["map_features"] = json!([{"source_id":METHOD}]),
                _ => unreachable!(),
            }
            assert!(validate_with_catalog(&bad, &catalog).is_err(), "{mode}");
        }
    }
    #[test]
    fn complete_context_and_unrelated_legacy_pass() {
        let (mut bundle, catalog) = fixture();
        validate_with_catalog(&bundle, &catalog).unwrap();
        bundle.collections.clear();
        bundle.manifest = json!({});
        validate_with_catalog(&bundle, &json!({})).unwrap();
    }

    #[test]
    fn missing_duplicate_and_changed_rows_reject() {
        for name in [
            "sources",
            "claims",
            "current_regional_reaches",
            "current_cross_shore_context",
            "objects",
            "entities",
        ] {
            for change in ["missing", "duplicate", "altered"] {
                let (mut bundle, catalog) = fixture();
                let group = bundle.collections.get_mut(name).unwrap();
                match change {
                    "missing" => {
                        group.remove(0);
                    }
                    "duplicate" => {
                        group.push(group[0].clone());
                    }
                    _ => {
                        group[0]["source_id"] = json!("source:forged");
                    }
                }
                // Entity provenance isn't carried on identity rows, so change
                // its required ID rather than adding an unrelated field.
                if name == "entities" && change == "altered" {
                    bundle.collections.get_mut(name).unwrap()[0]["id"] = json!("current:wrong");
                }
                if name == "objects" && change == "altered" {
                    bundle.collections.get_mut(name).unwrap()[0]["linked_source_count"] = json!(99);
                }
                assert!(
                    validate_with_catalog(&bundle, &catalog).is_err(),
                    "{name}: {change}"
                );
            }
        }
    }

    #[test]
    fn rejects_scope_rank_date_review_and_proxy_promotions() {
        for (collection, field, value) in [
            (
                "current_cross_shore_context",
                "paired_current_width_km",
                json!(15),
            ),
            (
                "current_cross_shore_context",
                "annual_width_range_km",
                json!([10, 15]),
            ),
            (
                "current_cross_shore_context",
                "proxy_note",
                json!("Measured velocity width"),
            ),
            ("current_regional_reaches", "rank_eligible", json!(true)),
            ("claims", "observation_time", json!("2005-06-01")),
            ("claims", "review_status", json!("independently_approved")),
        ] {
            let (mut bundle, catalog) = fixture();
            bundle.collections.get_mut(collection).unwrap()[0][field] = value;
            assert!(
                validate_with_catalog(&bundle, &catalog).is_err(),
                "{collection}: {field}"
            );
        }
    }

    #[test]
    fn rejects_physical_collection_and_foreign_owner_references() {
        for name in [
            "measurements",
            "widths",
            "length_assessments",
            "length_ranks",
            "geometries",
            "geometry_frames",
            "reference_routes",
            "width_samples",
            "current_dimension_samples",
            "current_section_measurements",
            "source_arrays",
        ] {
            let (mut bundle, catalog) = fixture();
            bundle.collections.insert(
                name.into(),
                vec![json!({"id":"invented","nested":{"source_ids":[METHOD]}})],
            );
            assert!(validate_with_catalog(&bundle, &catalog).is_err(), "{name}");
        }
        let (mut bundle, catalog) = fixture();
        bundle
            .collections
            .get_mut("objects")
            .unwrap()
            .push(json!({"id":"eddy:foreign","source_ids":[METHOD]}));
        assert!(validate_with_catalog(&bundle, &catalog).is_err());
        let (mut bundle, catalog) = fixture();
        bundle.collections.get_mut("objects").unwrap()[0]["cross_shore_context_ids"] =
            json!([contract()["additions"]["current_cross_shore_context"][0]["id"]]);
        assert!(validate_with_catalog(&bundle, &catalog).is_err());
    }

    #[test]
    fn rejects_owner_counts_provenance_and_navigation_corruption() {
        for (field, value) in [
            ("linked_source_count", json!(3)),
            ("source_ids", json!([METHOD, METHOD])),
            ("evidence_links", json!([])),
            ("regional_reach_ids", json!([])),
            ("map_features", json!([{"source_id":METHOD}])),
            ("capabilities", json!({"reported_regional_reaches":0})),
        ] {
            let (mut bundle, catalog) = fixture();
            bundle.collections.get_mut("objects").unwrap()[0][field] = value;
            assert!(validate_with_catalog(&bundle, &catalog).is_err(), "{field}");
        }
    }

    #[test]
    fn rejects_manifest_and_source_catalogue_corruption() {
        let (mut bundle, catalog) = fixture();
        bundle.manifest[VERSION_KEY] = json!("changed");
        assert!(validate_with_catalog(&bundle, &catalog).is_err());
        for path in contract()["input_sha256"]
            .as_object()
            .unwrap()
            .keys()
            .map(String::as_str)
            .chain([FILE])
        {
            let (mut bundle, catalog) = fixture();
            bundle.manifest["input_sha256"][path] = json!("changed");
            assert!(validate_with_catalog(&bundle, &catalog).is_err(), "{path}");
        }
        let (bundle, mut catalog) = fixture();
        catalog["documents"][0]["source_sha256"] = json!("changed");
        assert!(validate_with_catalog(&bundle, &catalog).is_err());
        let (bundle, mut catalog) = fixture();
        let repeated = catalog["documents"][0].clone();
        catalog["documents"].as_array_mut().unwrap().push(repeated);
        assert!(validate_with_catalog(&bundle, &catalog).is_err());
    }

    #[test]
    fn query_navigation_decodes_percent_encoding_and_rejects_bad_bytes() {
        assert_eq!(
            decode_query("%7B%22id%22%3A%22a%3Ab%22%7D"),
            Some("{\"id\":\"a:b\"}".into())
        );
        for invalid in ["%", "%2", "%XX", "%FF"] {
            assert!(decode_query(invalid).is_none());
        }
    }
}
