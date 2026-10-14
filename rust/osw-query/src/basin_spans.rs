//! Frozen source receipts for local component diagnostics; no current-width admission.
use crate::Bundle;
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::collections::BTreeSet;

// Renew these receipts only after rebuilding/reviewing the original-data diagnostics.
const SOURCES: [(&str, &str, &str); 4] = [
    (
        "diagnostic:basin-portugal-40n",
        "research/portugal-40n-2013-monthly-component-spans.json",
        "032abd513cc49dffecdac40851cd25bde7209f8900ee9d7446799f15515303fd",
    ),
    (
        "diagnostic:basin-south-atlantic-30w",
        "research/south-atlantic-30w-2013-monthly-component-spans.json",
        "b547b05aa9565627197ac2e624e5947ad1c4ced969c1d322ac4b0f150528e5ed",
    ),
    (
        "diagnostic:basin-south-pacific-100w",
        "research/south-pacific-100w-2013-monthly-component-spans.json",
        "24d513f31b9fc045755d4ca833896077222d078aec38023d74c06c17ebf02885",
    ),
    (
        "diagnostic:basin-south-indian-80e",
        "research/south-indian-80e-2013-monthly-component-spans.json",
        "408b1d5a67d60668c111e0fd4d68f5a07132ff50c1f4b56efeaba2c7ae6082c7",
    ),
];

pub fn validate(bundle: &Bundle) -> Result<(), String> {
    for (id, file, pin) in SOURCES {
        let expected_owner = match id {
            "diagnostic:basin-portugal-40n" => "current:portugal",
            "diagnostic:basin-south-atlantic-30w" => "current:south-atlantic",
            "diagnostic:basin-south-pacific-100w" => "current:south-pacific",
            _ => "current:south-indian",
        };
        let present = bundle.manifest["input_sha256"].get(file).is_some()
            || bundle
                .collections
                .get("diagnostics")
                .into_iter()
                .flatten()
                .any(|r| r["id"] == id)
            || bundle
                .collections
                .get("objects")
                .into_iter()
                .flatten()
                .any(|r| r["id"] == expected_owner);
        if !present {
            continue;
        }
        let rows: Vec<_> = bundle
            .collections
            .get("diagnostics")
            .into_iter()
            .flatten()
            .filter(|r| r["id"] == id)
            .collect();
        if rows.len() != 1 {
            return Err("Missing or duplicate basin component diagnostic".into());
        }
        let row = rows[0];
        let raw = row["source_json"]
            .as_str()
            .ok_or("Missing basin original JSON")?;
        let original: Value =
            serde_json::from_str(raw).map_err(|_| "Invalid basin original JSON")?;
        if row["source_file"] != file
            || row["source_file_sha256"] != pin
            || bundle.manifest["input_sha256"][file] != pin
            || format!("{:x}", Sha256::digest(raw.as_bytes())) != pin
            || row["document"] != original
        {
            return Err("Changed frozen basin original or source binding".into());
        }
        let owner = original["current_id"]
            .as_str()
            .ok_or("Missing basin owner")?;
        let entity = format!("current:{owner}");
        let samples: Vec<_> = bundle
            .collections
            .get("width_samples")
            .into_iter()
            .flatten()
            .filter(|r| r["diagnostic_id"] == id)
            .collect();
        let paths: BTreeSet<_> = samples
            .iter()
            .filter_map(|r| r["sample_path"].as_str().map(str::to_owned))
            .collect();
        let expected: BTreeSet<_> = (0..12).map(|i| format!("/months/{i}")).collect();
        let object = bundle
            .collections
            .get("objects")
            .into_iter()
            .flatten()
            .find(|o| o["id"] == entity)
            .ok_or("Missing basin sample owner")?;
        if samples.len() != 12
            || paths != expected
            || samples.iter().any(|r| {
                r["entity_id"] != entity
                    || r["sample_family"] != "basin_monthly_component_section"
                    || r["current_association_verified"] != false
                    || r["scope"] != original["scope_note"]
                    || !object["width_sample_ids"]
                        .as_array()
                        .is_some_and(|ids| ids.contains(&r["id"]))
            })
        {
            return Err("Incomplete or promoted basin component sample join".into());
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    #[test]
    fn unchanged_sources_and_rebound_forgery() {
        let path =
            std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../almanac/query-data.json");
        let mut bundle: Bundle = serde_json::from_slice(&std::fs::read(path).unwrap()).unwrap();
        validate(&bundle).unwrap();
        let row = bundle
            .collections
            .get_mut("diagnostics")
            .unwrap()
            .iter_mut()
            .find(|r| r["id"] == SOURCES[0].0)
            .unwrap();
        row["document"]["months"][0]["approximate_section_span_km"] = json!(999);
        let raw = serde_json::to_string(&row["document"]).unwrap();
        let pin = format!("{:x}", Sha256::digest(raw.as_bytes()));
        row["source_json"] = json!(raw);
        row["source_file_sha256"] = json!(pin);
        bundle.manifest["input_sha256"][SOURCES[0].1] = json!(pin);
        assert!(validate(&bundle).is_err());
    }
}
