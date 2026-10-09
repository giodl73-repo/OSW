//! Reviewed descriptions retain their identity when scope context is erased.
use serde_json::Value;
use sha2::{Digest, Sha256};
const SOURCES: &[(&str, &str, &str)] = &[
    (
        "jutland",
        "research/jutland-skov-2019-water-mass-breadth-scope-audit.json",
        include_str!("../../../research/jutland-skov-2019-water-mass-breadth-scope-audit.json"),
    ),
    (
        "western-adriatic",
        "research/western-adriatic-chavanne-2007-mean-width-scope-audit.json",
        include_str!(
            "../../../research/western-adriatic-chavanne-2007-mean-width-scope-audit.json"
        ),
    ),
    (
        "baffin",
        "research/baffin-fissel-1982-regional-width-scope-audit.json",
        include_str!("../../../research/baffin-fissel-1982-regional-width-scope-audit.json"),
    ),
    (
        "peru-humboldt",
        "research/humboldt-fuenzalida-2008-regional-width-scope-audit.json",
        include_str!("../../../research/humboldt-fuenzalida-2008-regional-width-scope-audit.json"),
    ),
    (
        "west-australian",
        "research/west-australian-glenn-2008-breadth-scope-audit.json",
        include_str!("../../../research/west-australian-glenn-2008-breadth-scope-audit.json"),
    ),
    (
        "zeehan",
        "research/zeehan-cresswell-2000-width-section-scope-audit.json",
        include_str!("../../../research/zeehan-cresswell-2000-width-section-scope-audit.json"),
    ),
    (
        "kuroshio-extension",
        "research/kuroshio-extension-sasaki-2013-width-averaging-scope-audit.json",
        include_str!(
            "../../../research/kuroshio-extension-sasaki-2013-width-averaging-scope-audit.json"
        ),
    ),
    (
        "new-guinea-coastal-undercurrent",
        "research/ngcu-zenk-1999-width-constraint-scope-audit.json",
        include_str!("../../../research/ngcu-zenk-1999-width-constraint-scope-audit.json"),
    ),
    (
        "algerian",
        "research/algerian-cotroneo-2019-regional-width-scope-audit.json",
        include_str!("../../../research/algerian-cotroneo-2019-regional-width-scope-audit.json"),
    ),
    (
        "alaska",
        "research/alaska-weingartner-2002-regional-width-scope-audit.json",
        include_str!("../../../research/alaska-weingartner-2002-regional-width-scope-audit.json"),
    ),
    (
        "atlantic-equatorial-undercurrent",
        "research/atlantic-euc-gouriou-1988-background-width-scope-audit.json",
        include_str!(
            "../../../research/atlantic-euc-gouriou-1988-background-width-scope-audit.json"
        ),
    ),
    (
        "pacific-equatorial-undercurrent",
        "research/pacific-euc-wang-2022-background-width-scope-audit.json",
        include_str!("../../../research/pacific-euc-wang-2022-background-width-scope-audit.json"),
    ),
];

pub(crate) fn validate(row: &Value) -> Result<(), String> {
    let owner = row["current_id"].as_str().unwrap_or("");
    let id = row["id"].as_str().unwrap_or("");
    // Find the reviewed identity independently of editable owner/context fields.
    for (reviewed_owner, _, raw) in SOURCES {
        let doc: Value = serde_json::from_str(raw).map_err(|e| e.to_string())?;
        let known = doc["measurement"]["id"].as_str() == Some(id)
            || doc["measurements"].as_array().map_or(false, |rows| {
                rows.iter().any(|r| r["id"].as_str() == Some(id))
            });
        if known && owner != *reviewed_owner {
            return Err("Original regional width identity reassigned".into());
        }
    }
    let (path, raw) = match SOURCES.iter().find(|source| source.0 == owner) {
        Some((_, path, raw)) => (*path, *raw),
        None if row.get("original_regional_context").is_none() => return Ok(()),
        None => return Err("Unknown original regional width source owner".into()),
    };
    let doc: Value = serde_json::from_str(raw).map_err(|e| e.to_string())?;
    let mut expected = if let Some(list) = doc["measurements"].as_array() {
        let i = list
            .iter()
            .position(|r| r["id"] == row["id"])
            .ok_or("Unknown original regional description")?;
        let mut source = list[i].clone();
        source["original_regional_context"]["audit_pointer"] =
            Value::String(format!("/measurements/{i}"));
        source
    } else {
        doc["measurement"].clone()
    };
    expected["original_regional_context"]["audit_file"] = Value::String(path.into());
    expected["original_regional_context"]["audit_sha256"] =
        Value::String(format!("{:x}", Sha256::digest(raw.as_bytes())));
    if *row != expected {
        return Err("Original regional width source or survey scope mismatch".into());
    }
    Ok(())
}
