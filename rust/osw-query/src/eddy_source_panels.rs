//! Source-image viewports are presentation pixels, never geographic rings.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
pub(crate) const PATH: &str = "research/thor-ursa-2022-dated-source-panels.json";
const SHA: &str = "5ec56eaf942007a146acedfadfe1def961522a8f30cc12c3f1bdde74a4da240d";
const OWNERS: [&str; 2] = ["eddy:published:thor-2020", "eddy:published:ursa-2021"];

pub(crate) fn validate_raw(raw: &str) -> Result<(), String> {
    if format!("{:x}", Sha256::digest(raw.as_bytes())) != SHA {
        return Err("Thor/Ursa panels: changed source dates, identity or scope".into());
    }
    Ok(())
}

pub(crate) fn validate(bundle: &Bundle) -> Result<(), String> {
    let receipt = &bundle.manifest["atlas_receipts"][PATH];
    let needed = !receipt.is_null()
        || bundle
            .collections
            .get("objects")
            .is_some_and(|rows| rows.iter().any(|r| OWNERS.iter().any(|id| r["id"] == *id)));
    if !needed {
        return Ok(());
    }
    let raw = receipt["source_json"]
        .as_str()
        .ok_or("Thor/Ursa panels: missing original source audit")?;
    validate_raw(raw)?;
    if format!("{:x}", Sha256::digest(raw.as_bytes())) != SHA
        || receipt["source_sha256"] != SHA
        || bundle.manifest["input_sha256"][PATH] != SHA
    {
        return Err("Thor/Ursa panels: changed source dates, identity or scope".into());
    }
    let doc: Value = serde_json::from_str(raw).map_err(|e| e.to_string())?;
    for (file, hash) in [
        ("source_document_file", "source_document_sha256"),
        ("acquisition_file", "acquisition_sha256"),
        ("protocol_file", "protocol_sha256"),
    ] {
        let path = doc[file]
            .as_str()
            .ok_or("Thor/Ursa panels: missing dependency")?;
        if bundle.manifest["input_sha256"][path] != doc[hash] {
            return Err("Thor/Ursa panels: changed original or protocol dependency".into());
        }
    }
    for event in doc["events"]
        .as_array()
        .ok_or("Thor/Ursa panels: missing event inventory")?
    {
        let file = event["source_image_file"]
            .as_str()
            .ok_or("Thor/Ursa panels: missing image")?;
        if bundle.manifest["input_sha256"][file] != event["source_image_sha256"] {
            return Err("Thor/Ursa panels: changed original figure dependency".into());
        }
    }
    Ok(())
}

pub(crate) fn scenes(bundle: &Bundle) -> Result<Value, String> {
    validate(bundle)?;
    let Some(raw) = bundle.manifest["atlas_receipts"][PATH]["source_json"].as_str() else {
        return Ok(json!({}));
    };
    let doc: Value = serde_json::from_str(raw).map_err(|e| e.to_string())?;
    let mut scenes = json!({});
    for event in doc["events"]
        .as_array()
        .ok_or("Thor/Ursa panels: missing events")?
    {
        let id = event["entity_id"]
            .as_str()
            .ok_or("Thor/Ursa panels: missing owner")?;
        scenes[id] = json!({"kind":"named_eddy_source_panels","engine":"rust-osw-query-v1",
            "entity_id":id,"name":event["name"],"figure_number":event["figure_number"],
            "image_href":format!("../{}",event["source_image_file"].as_str().unwrap()),
            "image_size_pixels":event["source_image_size_pixels"],"panels":event["panels"],
            "source_document":PATH,"source_pointer":format!("/events/{}",event["figure_number"].as_u64().unwrap()-2),
            "source_url":doc["source_url"],"source_citation":doc["source_citation"],
            "source_caption":event["source_caption"],"copyright":doc["copyright"],
            "license_url":doc["license_url"],"field_definition":doc["field_definition"],
            "contour_definition":doc["contour_definition"],"claim_limit":doc["claim_limit"],
            "display_transformation":doc["display_transformation"],
            "geometry_role":"source_image_pixels_no_geographic_geometry"});
    }
    Ok(scenes)
}

pub(crate) fn for_owner(bundle: &Bundle, id: &str) -> Result<Value, String> {
    if !OWNERS.contains(&id) {
        return Ok(Value::Null);
    }
    Ok(scenes(bundle)?[id].clone())
}
