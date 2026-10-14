//! Frozen source receipts for local component diagnostics; no current-width admission.
use crate::Bundle;
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::collections::BTreeSet;

// Renew these receipts only after rebuilding/reviewing the original-data diagnostics.
const SOURCES: [(&str, &str, &str); 7] = [
    (
        "diagnostic:basin-portugal-40n",
        "research/portugal-40n-2013-monthly-component-spans.json",
        "635e77ba016c361c85ad9e49f425d3b8a90ebeff0bcc3a2bc1840b6b4a0d920c",
    ),
    (
        "diagnostic:basin-south-atlantic-30w",
        "research/south-atlantic-30w-2013-monthly-component-spans.json",
        "c576f4444d2b551ec46043861e464f8fc9e8ee06c80cfcd3158f0c69c9bcafc1",
    ),
    (
        "diagnostic:basin-south-pacific-100w",
        "research/south-pacific-100w-2013-monthly-component-spans.json",
        "ea1f41ba0378aa7306f6de0e3c17d117a2f77b00f110d276e390a9479d97f44d",
    ),
    (
        "diagnostic:basin-south-indian-80e",
        "research/south-indian-80e-2013-monthly-component-spans.json",
        "71242c8fe62379e4ed661dc2ad4a4ed4908aabc7558fe40ba715892883607346",
    ),
    (
        "diagnostic:basin-aleutian-160w",
        "research/aleutian-160w-2013-monthly-component-spans.json",
        "e712741722e85ecf0155f5d140b44799d0f02abcea05c484f2ccc41044f5f34e",
    ),
    (
        "diagnostic:basin-south-australian-132e-100m",
        "research/south-australian-132e-100m-2012-monthly-component-spans.json",
        "1a70cd4fdb8761b905c14ae7cce2419ae905a489c06421a57fbbd789f009e0e3",
    ),
    (
        "diagnostic:basin-west-australian-32s",
        "research/west-australian-32s-2013-monthly-component-spans.json",
        "11627cb0cbc74674c75abe46fee68222ee8877a546d5068dda55ddc69274adc2",
    ),
];

pub fn validate(bundle: &Bundle) -> Result<(), String> {
    for (id, file, pin) in SOURCES {
        let expected_owner = match id {
            "diagnostic:basin-portugal-40n" => "current:portugal",
            "diagnostic:basin-south-atlantic-30w" => "current:south-atlantic",
            "diagnostic:basin-south-pacific-100w" => "current:south-pacific",
            "diagnostic:basin-south-indian-80e" => "current:south-indian",
            "diagnostic:basin-aleutian-160w" => "current:aleutian",
            "diagnostic:basin-south-australian-132e-100m" => "current:south-australian",
            "diagnostic:basin-west-australian-32s" => "current:west-australian",
            _ => return Err("Unknown frozen basin source".into()),
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
