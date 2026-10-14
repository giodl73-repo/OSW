//! Reviewed descriptions retain their identity when scope context is erased.
use serde_json::Value;
use sha2::{Digest, Sha256};
const SOURCES: &[(&str, &str, &str)] = &[
    (
        "persian-gulf-saline-overflow",
        "research/persian-gulf-gogp99-geostrophic-scales-scope-audit.json",
        include_str!("../../../research/persian-gulf-gogp99-geostrophic-scales-scope-audit.json"),
    ),
    (
        "atlantic-south-equatorial-undercurrent",
        "research/atlantic-seuc-molinari-1981-core-width-scope-audit.json",
        include_str!("../../../research/atlantic-seuc-molinari-1981-core-width-scope-audit.json"),
    ),
    (
        "antarctic-slope",
        "research/antarctic-slope-chavanne-2010-dated-width-constraint-scope-audit.json",
        include_str!(
            "../../../research/antarctic-slope-chavanne-2010-dated-width-constraint-scope-audit.json"
        ),
    ),
    (
        "balearic",
        "research/balearic-socib-2023-regional-width-scope-audit.json",
        include_str!("../../../research/balearic-socib-2023-regional-width-scope-audit.json"),
    ),
    (
        "azores",
        "research/azores-carracedo-2014-model-core-width-scope-audit.json",
        include_str!("../../../research/azores-carracedo-2014-model-core-width-scope-audit.json"),
    ),
    (
        "new-guinea-coastal-current",
        "research/ngcc-radenac-2016-seasonal-vein-width-scope-audit.json",
        include_str!("../../../research/ngcc-radenac-2016-seasonal-vein-width-scope-audit.json"),
    ),
    (
        "pacific-south-equatorial-countercurrent",
        "research/pacific-secc-rotschi-1972-width-range-scope-audit.json",
        include_str!("../../../research/pacific-secc-rotschi-1972-width-range-scope-audit.json"),
    ),
    (
        "hiri-current",
        "research/hiri-hughes-1993-local-decay-scales-scope-audit.json",
        include_str!("../../../research/hiri-hughes-1993-local-decay-scales-scope-audit.json"),
    ),
    (
        "east-adriatic",
        "research/east-adriatic-pasaric-2019-inflow-extent-scope-audit.json",
        include_str!("../../../research/east-adriatic-pasaric-2019-inflow-extent-scope-audit.json"),
    ),
    (
        "caribbean",
        "research/caribbean-duncan-1982-dated-width-scope-audit.json",
        include_str!("../../../research/caribbean-duncan-1982-dated-width-scope-audit.json"),
    ),
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

pub(crate) fn validate_ngcc_inventory(bundle: &crate::Bundle) -> Result<(), String> {
    let (_, path, raw) = SOURCES
        .iter()
        .find(|source| source.0 == "new-guinea-coastal-current")
        .copied()
        .ok_or("Missing frozen NGCC source")?;
    let owner = "current:new-guinea-coastal-current";
    let present = bundle.manifest["input_sha256"].get(path).is_some()
        || bundle
            .collections
            .get("objects")
            .into_iter()
            .flatten()
            .any(|r| r["id"] == owner);
    if !present {
        return Ok(());
    }
    let expected: Value = serde_json::from_str(raw).map_err(|e| e.to_string())?;
    let descriptors = expected["measurements"]
        .as_array()
        .ok_or("Invalid NGCC frozen descriptors")?;
    let actual: Vec<_> = bundle
        .collections
        .get("widths")
        .into_iter()
        .flatten()
        .filter(|r| r["current_id"] == "new-guinea-coastal-current")
        .collect();
    if actual.len() != descriptors.len()
        || descriptors
            .iter()
            .any(|e| actual.iter().filter(|r| r["id"] == e["id"]).count() != 1)
        || bundle.manifest["input_sha256"][path] != format!("{:x}", Sha256::digest(raw.as_bytes()))
    {
        return Err("Missing or rebound NGCC seasonal vein inventory".into());
    }
    Ok(())
}

pub(crate) fn validate_azores_inventory(bundle: &crate::Bundle) -> Result<(), String> {
    let (_, path, raw) = SOURCES
        .iter()
        .find(|s| s.0 == "azores")
        .copied()
        .ok_or("Missing Azores frozen source")?;
    let present = bundle.manifest["input_sha256"].get(path).is_some()
        || bundle
            .collections
            .get("objects")
            .into_iter()
            .flatten()
            .any(|r| r["id"] == "current:azores");
    if !present {
        return Ok(());
    }
    let doc: Value = serde_json::from_str(raw).map_err(|e| e.to_string())?;
    let expected = doc["measurements"]
        .as_array()
        .ok_or("Invalid Azores frozen source")?;
    let rows: Vec<_> = bundle
        .collections
        .get("widths")
        .into_iter()
        .flatten()
        .filter(|r| expected.iter().any(|e| e["id"] == r["id"]))
        .collect();
    if rows.len() != 2
        || expected
            .iter()
            .any(|e| rows.iter().filter(|r| r["id"] == e["id"]).count() != 1)
        || bundle.manifest["input_sha256"][path] != format!("{:x}", Sha256::digest(raw.as_bytes()))
    {
        return Err("Missing or rebound Azores model-core inventory".into());
    }
    for row in rows {
        validate(row)?;
    }
    Ok(())
}

pub(crate) fn validate_atlantic_seuc_inventory(bundle: &crate::Bundle) -> Result<(), String> {
    let (_, path, raw) = SOURCES
        .iter()
        .find(|s| s.0 == "atlantic-south-equatorial-undercurrent")
        .ok_or("Missing Atlantic SEUC frozen source")?;
    if bundle.manifest["input_sha256"].get(*path).is_none()
        && !bundle
            .collections
            .get("objects")
            .into_iter()
            .flatten()
            .any(|r| r["id"] == "current:atlantic-south-equatorial-undercurrent")
    {
        return Ok(());
    }
    let rows: Vec<_> = bundle
        .collections
        .get("widths")
        .into_iter()
        .flatten()
        .filter(|r| {
            r["id"] == "atlantic-seuc-molinari-1981-core-width"
                || r["current_id"] == "atlantic-south-equatorial-undercurrent"
        })
        .collect();
    if rows.len() != 1
        || bundle.manifest["input_sha256"][path] != format!("{:x}", Sha256::digest(raw.as_bytes()))
    {
        return Err("Missing or rebound Atlantic SEUC core inventory".into());
    }
    validate(rows[0])
}

pub(crate) fn validate_balearic_inventory(bundle: &crate::Bundle) -> Result<(), String> {
    let (_, path, raw) = SOURCES
        .iter()
        .find(|s| s.0 == "balearic")
        .ok_or("Missing SOCIB frozen source")?;
    if bundle.manifest["input_sha256"].get(*path).is_none()
        && !bundle
            .collections
            .get("objects")
            .into_iter()
            .flatten()
            .any(|r| r["id"] == "current:balearic")
    {
        return Ok(());
    }
    let rows: Vec<_> = bundle
        .collections
        .get("widths")
        .into_iter()
        .flatten()
        .filter(|r| {
            r["id"] == "balearic-socib-2023-regional-width" || r["current_id"] == "balearic"
        })
        .collect();
    if rows.len() != 1
        || bundle.manifest["input_sha256"][path] != format!("{:x}", Sha256::digest(raw.as_bytes()))
    {
        return Err("Missing or rebound SOCIB Balearic inventory".into());
    }
    validate(rows[0])
}

pub(crate) fn validate_antarctic_jet_inventory(bundle: &crate::Bundle) -> Result<(), String> {
    let (_, path, raw) = SOURCES
        .iter()
        .find(|s| s.0 == "antarctic-slope")
        .ok_or("Missing Antarctic jet frozen source")?;
    if bundle.manifest["input_sha256"].get(*path).is_none()
        && !bundle
            .collections
            .get("objects")
            .into_iter()
            .flatten()
            .any(|r| r["id"] == "current:antarctic-slope")
    {
        return Ok(());
    }
    let rows: Vec<_> = bundle
        .collections
        .get("widths")
        .into_iter()
        .flatten()
        .filter(|r| r["id"] == "antarctic-slope-chavanne-2009-02-23-jet-width-constraint")
        .collect();
    if rows.len() != 1
        || bundle.manifest["input_sha256"][path] != format!("{:x}", Sha256::digest(raw.as_bytes()))
    {
        return Err("Missing or rebound Antarctic Slope dated jet constraint".into());
    }
    validate(rows[0])
}

pub(crate) fn validate_gogp_inventory(bundle: &crate::Bundle) -> Result<(), String> {
    let (_, path, raw) = SOURCES
        .iter()
        .find(|s| s.0 == "persian-gulf-saline-overflow")
        .ok_or("Missing GOGP99 frozen source")?;
    if bundle.manifest["input_sha256"].get(*path).is_none()
        && !bundle
            .collections
            .get("objects")
            .into_iter()
            .flatten()
            .any(|r| r["id"] == "current:persian-gulf-saline-overflow")
    {
        return Ok(());
    }
    let document: Value = serde_json::from_str(raw).map_err(|e| e.to_string())?;
    let definitions = document["measurements"]
        .as_array()
        .ok_or("Missing GOGP99 definitions")?;
    let legacy = document["existing_salinity_records"]
        .as_array()
        .ok_or("Missing GOGP99 salinity definitions")?;
    let rows: Vec<_> = bundle
        .collections
        .get("widths")
        .into_iter()
        .flatten()
        .filter(|r| {
            r["current_id"] == "persian-gulf-saline-overflow"
                || definitions.iter().any(|e| r["id"] == e["id"])
        })
        .collect();
    if bundle.manifest["input_sha256"][path] != format!("{:x}", Sha256::digest(raw.as_bytes()))
        || rows.len() != definitions.len() + legacy.len()
        || definitions
            .iter()
            .chain(legacy.iter())
            .any(|e| rows.iter().filter(|r| r["id"] == e["id"]).count() != 1)
    {
        return Err("Missing or rebound GOGP99 velocity/salinity inventory".into());
    }
    for row in rows {
        validate(row)?;
    }
    Ok(())
}

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
        None if owner == "persian-gulf-saline-overflow" => {
            let (_, _, raw) = SOURCES
                .iter()
                .find(|s| s.0 == owner)
                .ok_or("Missing GOGP99 source")?;
            let doc: Value = serde_json::from_str(raw).map_err(|e| e.to_string())?;
            if doc["existing_salinity_records"]
                .as_array()
                .map_or(false, |rows| rows.contains(row))
            {
                return Ok(());
            }
            return Err("Changed GOGP99 salinity record or unknown velocity definition".into());
        }
        None if owner == "azores"
            && id == "azores-2009-section-width"
            && row.get("original_regional_context").is_none() =>
        {
            return Ok(());
        }
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
