//! Source limitations explain missing dimensions without admitting measurements.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};

const PATH: &str = "research/southern-current-width-source-limitations-audit.json";
const RAW: &str =
    include_str!("../../../research/southern-current-width-source-limitations-audit.json");

fn document() -> Value {
    serde_json::from_str(RAW).expect("reviewed source limitations")
}

fn diagnostic_id(owner: &str) -> String {
    format!("diagnostic:current-width-source-limits:{owner}")
}

pub(crate) fn validate(bundle: &crate::Bundle) -> Result<(), String> {
    let doc = document();
    let reviews = doc["reviews"]
        .as_array()
        .ok_or("Missing source limitation reviews")?;
    let present = bundle.manifest["input_sha256"].get(PATH).is_some()
        || bundle
            .collections
            .get("objects")
            .into_iter()
            .flatten()
            .any(|r| {
                reviews.iter().any(|review| {
                    r["id"] == format!("current:{}", review["current_id"].as_str().unwrap())
                })
            });
    if !present {
        return Ok(());
    }
    let pin = format!("{:x}", Sha256::digest(RAW.as_bytes()));
    if bundle.manifest["input_sha256"][PATH] != pin {
        return Err("Current width source review audit binding changed".into());
    }
    for source in doc["sources"]
        .as_array()
        .ok_or("Missing source limitation originals")?
    {
        for (file_key, hash_key) in [
            ("source_document_file", "source_document_sha256"),
            ("acquisition_file", "acquisition_sha256"),
        ] {
            let file = source[file_key]
                .as_str()
                .ok_or("Missing source limitation dependency")?;
            if bundle.manifest["input_sha256"][file] != source[hash_key] {
                return Err("Current width source review original dependency changed".into());
            }
        }
    }
    for review in reviews {
        let owner = review["current_id"]
            .as_str()
            .ok_or("Missing source review owner")?;
        let id = diagnostic_id(owner);
        let rows: Vec<_> = bundle
            .collections
            .get("diagnostics")
            .into_iter()
            .flatten()
            .filter(|r| r["id"] == id)
            .collect();
        let expected = json!({"id":id,"label":format!("{owner} current width source limitations"),
            "entity_id":format!("current:{owner}"),"current_id":owner,"status":doc["status"],"rank_eligible":false,
            "source_file":PATH,"source_file_sha256":pin,"source_json":RAW,"document":doc});
        if rows.len() != 1 || rows[0] != &expected {
            return Err("Current width source review missing, rebound or promoted".into());
        }
    }
    if bundle
        .collections
        .get("widths")
        .into_iter()
        .flatten()
        .any(|r| r.to_string().contains(PATH))
    {
        return Err("Current width source review cannot be a width measurement".into());
    }
    Ok(())
}

pub(crate) fn scenes(bundle: &crate::Bundle) -> Value {
    let doc = document();
    let mut result = json!({});
    for (index, review) in doc["reviews"].as_array().unwrap().iter().enumerate() {
        let owner = review["current_id"].as_str().unwrap();
        if !bundle
            .collections
            .get("diagnostics")
            .into_iter()
            .flatten()
            .any(|r| r["id"] == diagnostic_id(owner))
        {
            continue;
        }
        let label = if owner == "south-indian" {
            "South Indian Current"
        } else {
            "South Australian Current"
        };
        result[owner] = json!({"kind":"current_width_source_review","current_id":owner,"label":label,
            "diagnostic_id":diagnostic_id(owner),"review":review,"source":doc["sources"][review["source_index"].as_u64().unwrap() as usize],
            "source_file":PATH,"source_pointer":format!("/reviews/{index}"),
            "geometry_role":"source_limitation_context_no_current_geometry_or_width",
            "scope":"Reviewed source limitations. Width and annual range remain unresolved; no numeric measurement added."});
    }
    result
}

pub(crate) fn query(matches: &[&Value], bundle: &crate::Bundle) -> Value {
    let all = scenes(bundle);
    let selected: Vec<_> = all
        .as_object()
        .unwrap()
        .values()
        .filter(|scene| matches.iter().any(|r| r["id"] == scene["diagnostic_id"]))
        .cloned()
        .collect();
    if selected.is_empty() {
        Value::Null
    } else {
        json!({"kind":"current_width_source_reviews","scope":"Source review context; no measured width or annual range admitted.","scenes":selected})
    }
}
