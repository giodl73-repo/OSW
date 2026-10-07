//! Four predeclared Loop method comparisons; failed traces stay unranked diagnostics.
use crate::{Bundle, Store};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
const COMPARISON: &str = "research/loop-current-recorded-date-comparison.json";
const SELECTION: &str = "research/loop-current-recorded-date-sources.json";
const DATES: [&str; 4] = ["2025-01-15", "2025-04-15", "2025-07-15", "2025-10-15"];

fn documents(bundle: &Bundle) -> Result<(Value, Value), String> {
    let receipts = bundle.manifest["loop_recorded_receipts"]
        .as_object()
        .ok_or("Loop recorded-date sources unavailable")?;
    if receipts.len() != 2
        || !receipts.contains_key(COMPARISON)
        || !receipts.contains_key(SELECTION)
    {
        return Err("Incomplete Loop recorded-date receipt inventory".into());
    }
    let mut docs = Vec::new();
    for (path, schema) in [
        (COMPARISON, "osw.loop-current-recorded-date-comparison.v1"),
        (SELECTION, "osw.loop-current-recorded-date-sources.v1"),
    ] {
        let receipt = &receipts[path];
        let raw = receipt["source_json"]
            .as_str()
            .ok_or("Missing Loop recorded-date source bytes")?;
        let hash = format!("{:x}", Sha256::digest(raw.as_bytes()));
        let doc: Value =
            serde_json::from_str(raw).map_err(|_| "Invalid Loop recorded-date source JSON")?;
        if receipt["source_file"] != path
            || receipt["source_sha256"] != hash
            || bundle.manifest["input_sha256"][path] != hash
            || doc["schema"] != schema
        {
            return Err("Changed Loop recorded-date source receipt or schema".into());
        }
        docs.push(doc);
    }
    Ok((docs.remove(0), docs.remove(0)))
}

fn diagnostic<'a>(bundle: &'a Bundle, method: &str, date: &str) -> Result<&'a Value, String> {
    let id = format!("diagnostic:loop-{method}-{}", date.replace('-', ""));
    bundle
        .collections
        .get("diagnostics")
        .into_iter()
        .flatten()
        .find(|r| r["id"] == id)
        .ok_or("Missing Loop recorded-date method diagnostic".into())
}

pub fn validate(bundle: &Bundle) -> Result<(), String> {
    if bundle.manifest.get("loop_recorded_receipts").is_none() {
        return Ok(());
    }
    let (comparison, selection) = documents(bundle)?;
    if comparison["current_id"] != "loop"
        || comparison["rank_eligible"] != false
        || [
            "whole_current_length_km",
            "width_km",
            "annual_length_range_km",
            "confidence_interval_km",
        ]
        .iter()
        .any(|k| comparison.get(*k) != Some(&Value::Null))
        || comparison["source_manifest"] != SELECTION
        || comparison["source_manifest_sha256"] != bundle.manifest["input_sha256"][SELECTION]
        || comparison["generator_sha256"]
            != bundle.manifest["input_sha256"]["analysis/build_loop_current_recorded_dates.py"]
        || selection["selection"]
            != "Four predeclared quarterly-spaced 2025 dates, not selected by path length, success, named phase or extrema."
        || selection["annual_coverage_status"] != "four_days_only_not_a_seasonal_climatology"
        || selection["source_use_review_status"] != "pending_for_new_regional_snapshots"
    {
        return Err("Invalid Loop recorded-date admission or selection scope".into());
    }
    let rows = comparison["dates"]
        .as_array()
        .ok_or("Missing Loop comparison dates")?;
    let sources = selection["dates"]
        .as_array()
        .ok_or("Missing Loop selected source dates")?;
    if rows.len() != 4 || sources.len() != 4 {
        return Err("Incomplete Loop predeclared dates".into());
    }
    for ((row, source), date) in rows.iter().zip(sources).zip(DATES) {
        if row["date"] != date || source["date"] != date {
            return Err("Changed Loop predeclared date order".into());
        }
        let noaa_record = diagnostic(bundle, "noaa", date)?;
        let adt_record = diagnostic(bundle, "adt", date)?;
        let noaa = &noaa_record["document"];
        let adt = &adt_record["document"];
        for (method, record, doc, file_key, hash_key) in [
            (
                "noaa",
                noaa_record,
                noaa,
                "source_subset",
                "source_subset_sha256",
            ),
            ("adt", adt_record, adt, "source_file", "source_sha256"),
        ] {
            if row[format!("{method}_diagnostic_file")] != record["source_file"]
                || row[format!("{method}_diagnostic_sha256")] != record["source_file_sha256"]
                || source[method]["file"] != doc[file_key]
                || source[method]["sha256"] != doc[hash_key]
                || source[method]["source_url"] != doc["source_url"]
            {
                return Err("Loop recorded-date diagnostic/source join mismatch".into());
            }
        }
        let nominal = &noaa["nominal"];
        if row["noaa_connected_length_km"] != nominal["open_path_length_km"]
            || row["noaa_stop_reason"] != nominal["stop_reason"]
            || row["noaa_selected_seed_longitude"] != nominal["seed_lon_lat"][0]
            || row["noaa_failed_scenario_count"] != noaa["failure_count"]
            || row["adt_selected_length_km"]
                != adt["comparison"]["duacs_selected_contour_length_km"]
            || row["adt_eligible_count"] != adt["eligible_count"]
            || row["adt_selected_level_m"] != adt["selected"]["adt_level_m"]
            || row["signed_difference_duacs_minus_noaa_km"]
                != adt["comparison"]["signed_difference_duacs_minus_noaa_km"]
        {
            return Err("Loop recorded-date outcomes disagree with method diagnostics".into());
        }
    }
    Ok(())
}

fn display(value: &Value) -> String {
    let Some(value) = value.as_f64() else {
        return "unresolved".into();
    };
    let digits = (((value / 100. + 0.5).floor() as i64) * 100).to_string();
    let chunks = digits
        .as_bytes()
        .rchunks(3)
        .map(|s| std::str::from_utf8(s).unwrap())
        .collect::<Vec<_>>();
    format!(
        "{} km",
        chunks.into_iter().rev().collect::<Vec<_>>().join(",")
    )
}
fn path(coordinates: &Value) -> Result<String, String> {
    crate::map::path_formatted(coordinates, false, |p| {
        let (x, y) = crate::cartography::root(p);
        format!("{x:.5} {y:.5}")
    })
    .ok_or("Invalid Loop diagnostic display geometry".into())
}
impl Store {
    pub fn loop_recorded_view(&self) -> Result<Value, String> {
        let (comparison, selection) = documents(&self.bundle)?;
        let mut frames = Vec::new();
        for row in comparison["dates"]
            .as_array()
            .ok_or("Missing recorded dates")?
        {
            let date = row["date"].as_str().ok_or("Missing recorded day")?;
            let noaa = &diagnostic(&self.bundle, "noaa", date)?["document"];
            let adt = &diagnostic(&self.bundle, "adt", date)?["document"];
            let query = json!({"collection":"objects","filters":[{"field":"id","op":"eq","value":"current:loop"}],
                "geometry_time":{"from":date,"to":date},"limit":1});
            frames.push(json!({"date":date,"noaa_path":path(&noaa["nominal"]["coordinates_lon_lat"])?,
                "adt_path":if adt["selected"].is_null(){Value::Null}else{json!(path(&adt["selected"]["coordinates_lon_lat"])?)},
                "noaa_connected":noaa["nominal"]["gate_connected"],"noaa_display":display(&row["noaa_connected_length_km"]),
                "adt_display":display(&row["adt_selected_length_km"]),"noaa_stop":row["noaa_stop_reason"].as_str().ok_or("Missing trace stop")?.replace('_'," "),
                "failed_scenarios":row["noaa_failed_scenario_count"],"difference":row["signed_difference_duacs_minus_noaa_km"],
                "query":query,"noaa_file":format!("../{}",row["noaa_diagnostic_file"].as_str().unwrap()),
                "adt_file":format!("../{}",row["adt_diagnostic_file"].as_str().unwrap())}));
        }
        let (west, north) = crate::cartography::root(crate::map::point(&json!([-93, 31])).unwrap());
        let (east, south) = crate::cartography::root(crate::map::point(&json!([-79, 20])).unwrap());
        Ok(
            json!({"ok":true,"engine":"rust-osw-query-v1","frames":frames,
            "bundle_sha256":self.metadata()["bundle_sha256"],"selection":selection["selection"],
            "scope":comparison["interpretation"],"view_box":[west,north,east-west,south-north],
            "gates":{"yucatan":path(&json!([[-86.875,21.875],[-85.125,21.875]]))?,
                     "florida":path(&json!([[-81.5,23],[-81.5,25]]))?},
            "source_sha256":self.bundle.manifest["loop_recorded_receipts"].as_object().unwrap().iter()
                .map(|(path,receipt)|(path.clone(),receipt["source_sha256"].clone())).collect::<std::collections::BTreeMap<_,_>>() }),
        )
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn display_rounding_and_shared_geometry_do_not_admit_a_current_dimension() {
        assert_eq!(display(&Value::Null), "unresolved");
        assert_eq!(display(&json!(1573.2)), "1,600 km");
        assert_eq!(
            path(&json!([[-86.875, 21.875], [-85.125, 21.875]])).unwrap(),
            "M 442.84722 370.06944 L 450.04167 370.06944 "
        );
        assert!(path(&json!([[200, 0], [0, 1]])).is_err());
    }
}
