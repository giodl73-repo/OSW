//! Original regional width descriptions do not inherit an article's survey support.
use serde_json::Value;
use sha2::{Digest, Sha256};
pub(crate) fn validate(row: &Value) -> Result<(), String> {
    let (path, raw) = match row["current_id"].as_str().unwrap_or("") {
        "west-australian" => (
            "research/west-australian-glenn-2008-breadth-scope-audit.json",
            include_str!("../../../research/west-australian-glenn-2008-breadth-scope-audit.json"),
        ),
        "zeehan" => (
            "research/zeehan-cresswell-2000-width-section-scope-audit.json",
            include_str!("../../../research/zeehan-cresswell-2000-width-section-scope-audit.json"),
        ),
        "kuroshio-extension" => (
            "research/kuroshio-extension-sasaki-2013-width-averaging-scope-audit.json",
            include_str!(
                "../../../research/kuroshio-extension-sasaki-2013-width-averaging-scope-audit.json"
            ),
        ),
        "new-guinea-coastal-undercurrent" => (
            "research/ngcu-zenk-1999-width-constraint-scope-audit.json",
            include_str!("../../../research/ngcu-zenk-1999-width-constraint-scope-audit.json"),
        ),
        "algerian" => (
            "research/algerian-cotroneo-2019-regional-width-scope-audit.json",
            include_str!(
                "../../../research/algerian-cotroneo-2019-regional-width-scope-audit.json"
            ),
        ),
        "alaska" => (
            "research/alaska-weingartner-2002-regional-width-scope-audit.json",
            include_str!(
                "../../../research/alaska-weingartner-2002-regional-width-scope-audit.json"
            ),
        ),
        "atlantic-equatorial-undercurrent" => (
            "research/atlantic-euc-gouriou-1988-background-width-scope-audit.json",
            include_str!(
                "../../../research/atlantic-euc-gouriou-1988-background-width-scope-audit.json"
            ),
        ),
        "pacific-equatorial-undercurrent" => (
            "research/pacific-euc-wang-2022-background-width-scope-audit.json",
            include_str!(
                "../../../research/pacific-euc-wang-2022-background-width-scope-audit.json"
            ),
        ),
        _ if row.get("original_regional_context").is_none() => return Ok(()),
        _ => return Err("Unknown original regional width source owner".into()),
    };
    let doc: Value = serde_json::from_str(raw).map_err(|e| e.to_string())?;
    let mut expected = doc["measurement"].clone();
    expected["original_regional_context"]["audit_file"] = Value::String(path.into());
    expected["original_regional_context"]["audit_sha256"] =
        Value::String(format!("{:x}", Sha256::digest(raw.as_bytes())));
    if *row != expected {
        return Err("Original regional width source or survey scope mismatch".into());
    }
    Ok(())
}
