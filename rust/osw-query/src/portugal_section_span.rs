//! Published coordinate separation is local section evidence, not physical width.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};

const PATH: &str = "research/portugal-perez-2013-orca-section-span-scope-audit.json";
const RAW: &str =
    include_str!("../../../research/portugal-perez-2013-orca-section-span-scope-audit.json");
const ID: &str = "portugal-perez-2009-orca-source-section-span";

fn audit() -> Result<Value, String> {
    serde_json::from_str(RAW).map_err(|e| e.to_string())
}

pub(crate) fn scene(matches: &[&Value]) -> Value {
    let Some(row) = matches.iter().find(|r| r["id"] == ID) else {
        return Value::Null;
    };
    json!({"kind":"published_coordinate_section_span",
        "title":"Portugal ORCA local section span",
        "scope":"OSW geodesic separation of published section limits. No flow-normal or whole-current width, physical uncertainty or seasonal range inferred.",
        "geometry_role":"local_source_section_limits_not_axis_or_physical_edges",
        "record":row})
}

pub(crate) fn validate_row(row: &Value) -> Result<(), String> {
    if row["id"] != ID
        && row["current_id"] != "portugal"
        && row.get("published_section_context").is_none()
    {
        return Ok(());
    }
    let mut expected = audit()?["measurement"].clone();
    expected["published_section_context"]["audit_file"] = Value::String(PATH.into());
    expected["published_section_context"]["audit_sha256"] =
        Value::String(format!("{:x}", Sha256::digest(RAW.as_bytes())));
    if row != &expected {
        return Err(
            "Portugal ORCA section span identity, provenance or physical scope changed".into(),
        );
    }
    Ok(())
}

pub(crate) fn validate_inventory(bundle: &crate::Bundle) -> Result<(), String> {
    let present = bundle.manifest["input_sha256"].get(PATH).is_some()
        || bundle
            .collections
            .get("objects")
            .into_iter()
            .flatten()
            .any(|r| r["id"] == "current:portugal");
    if !present {
        return Ok(());
    }
    let doc = audit()?;
    if bundle.manifest["input_sha256"][PATH] != format!("{:x}", Sha256::digest(RAW.as_bytes())) {
        return Err("Portugal ORCA section span audit binding changed".into());
    }
    let rows: Vec<_> = bundle
        .collections
        .get("widths")
        .into_iter()
        .flatten()
        .filter(|r| r["id"] == ID || r["current_id"] == "portugal")
        .collect();
    if rows.len() != 1 {
        return Err("Portugal ORCA section span missing or duplicated".into());
    }
    validate_row(rows[0])?;
    for (file_key, hash_key) in [
        ("source_event_file", "source_event_file_sha256"),
        ("protocol_file", "protocol_sha256"),
        ("figure_file", "figure_sha256"),
    ] {
        let path = doc[file_key]
            .as_str()
            .ok_or("Portugal ORCA dependency missing")?;
        if bundle.manifest["input_sha256"][path] != doc[hash_key] {
            return Err("Portugal ORCA section span source dependency changed".into());
        }
    }
    let diagnostics: Vec<_> = bundle
        .collections
        .get("diagnostics")
        .into_iter()
        .flatten()
        .filter(|r| r["id"] == "diagnostic:portugal-orca-section-span")
        .collect();
    if diagnostics.len() != 1
        || diagnostics[0]["document"] != doc
        || diagnostics[0]["source_file"] != PATH
        || diagnostics[0]["source_file_sha256"] != bundle.manifest["input_sha256"][PATH]
        || diagnostics[0]["source_json"].as_str() != Some(RAW)
    {
        return Err("Portugal ORCA section span source diagnostic changed".into());
    }
    Ok(())
}
