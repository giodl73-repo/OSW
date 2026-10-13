//! Reviewed descriptions retain their identity when scope context is erased.
use serde_json::Value;
use sha2::{Digest, Sha256};
const SOURCES: &[(&str, &str, &str)] = &[
    (
        "pacific-north-equatorial-undercurrent",
        "research/pacific-neuc-li-2018-isopycnal-breadth-scope-audit.json",
        include_str!("../../../research/pacific-neuc-li-2018-isopycnal-breadth-scope-audit.json"),
    ),
    (
        "deep-western-boundary",
        "research/dwbc-richardson-1993-upper-core-width-scope-audit.json",
        include_str!("../../../research/dwbc-richardson-1993-upper-core-width-scope-audit.json"),
    ),
    (
        "antarctic-coastal",
        "research/antarctic-coastal-schubert-2021-composite-width-scope-audit.json",
        include_str!(
            "../../../research/antarctic-coastal-schubert-2021-composite-width-scope-audit.json"
        ),
    ),
    (
        "tasman-front",
        "research/tasman-front-nilsson-1980-meander-band-scope-audit.json",
        include_str!("../../../research/tasman-front-nilsson-1980-meander-band-scope-audit.json"),
    ),
    (
        "monsoon",
        "research/monsoon-webber-2018-distinct-widths-scope-audit.json",
        include_str!("../../../research/monsoon-webber-2018-distinct-widths-scope-audit.json"),
    ),
    (
        "acc",
        "research/acc-park-2019-udintsev-breadths-scope-audit.json",
        include_str!("../../../research/acc-park-2019-udintsev-breadths-scope-audit.json"),
    ),
    (
        "north-pacific",
        "research/north-pacific-tomczak-2005-broad-band-scope-audit.json",
        include_str!("../../../research/north-pacific-tomczak-2005-broad-band-scope-audit.json"),
    ),
    (
        "solomon-island-coastal-undercurrent",
        "research/solomon-melet-2010-coastal-confinement-scope-audit.json",
        include_str!("../../../research/solomon-melet-2010-coastal-confinement-scope-audit.json"),
    ),
    (
        "new-ireland-coastal-undercurrent",
        "research/solomon-melet-2010-coastal-confinement-scope-audit.json",
        include_str!("../../../research/solomon-melet-2010-coastal-confinement-scope-audit.json"),
    ),
    (
        "jutland",
        "research/jutland-nielsen-2000-cited-satellite-width-scope-audit.json",
        include_str!(
            "../../../research/jutland-nielsen-2000-cited-satellite-width-scope-audit.json"
        ),
    ),
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
    let mut reviewed_source = None;
    for (reviewed_owner, path, raw) in SOURCES {
        let doc: Value = serde_json::from_str(raw).map_err(|e| e.to_string())?;
        let known = (doc["measurement"]["id"].as_str() == Some(id)
            && doc["measurement"]["current_id"].as_str() == Some(*reviewed_owner))
            || doc["measurements"].as_array().map_or(false, |rows| {
                rows.iter().any(|r| {
                    r["id"].as_str() == Some(id)
                        && r["current_id"].as_str() == Some(*reviewed_owner)
                })
            });
        if known {
            if owner != *reviewed_owner {
                return Err("Original regional width identity reassigned".into());
            }
            reviewed_source = Some((*path, *raw));
            break;
        }
    }
    let (path, raw) = match reviewed_source {
        Some(source) => source,
        None if SOURCES.iter().any(|source| source.0 == owner) => {
            return Err("Unknown original regional description".into());
        }
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
