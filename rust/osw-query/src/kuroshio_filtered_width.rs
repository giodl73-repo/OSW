//! Published filtered-curve samples keep their graphical time and scope.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
pub const ID: &str = "diagnostic:kuroshio-filtered-width";
const FILE: &str = "research/kuroshio-ecs-filtered-width-time-series.json";
const RAW: &str = include_str!("../../../research/kuroshio-ecs-filtered-width-time-series.json");
const FIGURE_FILE: &str = "research/kuroshio-ecs-filtered-width-time-series-figure.json";
const FIGURE_RAW: &str =
    include_str!("../../../research/kuroshio-ecs-filtered-width-time-series-figure.json");
const HELPER: &str = include_str!("../../../analysis/kuroshio_filtered_width.py");
const FAMILY: &str = "kuroshio_filtered_curve_plot";
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
fn document() -> Value {
    serde_json::from_str(RAW).expect("compiled filtered width readings")
}
fn figure() -> Value {
    serde_json::from_str(FIGURE_RAW).expect("compiled filtered width figure")
}
fn expected_record(doc: &Value) -> Value {
    json!({"id":ID,"label":"Kuroshio filtered regional width curve readings","entity_id":"current:kuroshio","current_id":"kuroshio",
  "status":doc["status"],"rank_eligible":false,"source_file":FILE,"source_file_sha256":pin(RAW),"source_json":RAW,"document":doc})
}
pub fn validate(bundle: &crate::Bundle) -> Result<(), String> {
    let diagnostics = bundle
        .collections
        .get("diagnostics")
        .map(Vec::as_slice)
        .unwrap_or(&[]);
    let rows = bundle
        .collections
        .get("width_samples")
        .map(Vec::as_slice)
        .unwrap_or(&[]);
    let widths = bundle
        .collections
        .get("widths")
        .map(Vec::as_slice)
        .unwrap_or(&[]);
    let owned = |r: &&Value| {
        r["sample_family"] == FAMILY
            || r["diagnostic_id"] == ID
            || r["source_context"]["schema"] == "osw.filtered-current-width-plot-time-series.v1"
    };
    let mentioned = widths.iter().any(|r| r.to_string().contains(FILE));
    let present = bundle.manifest["input_sha256"].get(FILE).is_some()
        || diagnostics.iter().any(|d| {
            d["id"] == ID
                || d["document"]["schema"] == "osw.filtered-current-width-plot-time-series.v1"
        })
        || rows.iter().any(|r| owned(&r))
        || mentioned;
    if !present {
        return Ok(());
    }
    let doc = document();
    let fig = figure();
    let inputs = &bundle.manifest["input_sha256"];
    if inputs[FILE] != pin(RAW)
        || inputs[FIGURE_FILE] != pin(FIGURE_RAW)
        || inputs["analysis/kuroshio_filtered_width.py"] != pin(HELPER)
    {
        return Err("Kuroshio filtered-width source/figure binding mismatch".into());
    }
    for (file, expected) in doc["input_sha256"].as_object().unwrap() {
        if inputs[file] != *expected {
            return Err("Kuroshio filtered-width input changed".into());
        }
    }
    for value in [&doc, &fig] {
        if inputs[value["generator_file"].as_str().unwrap()] != value["generator_sha256"] {
            return Err("Kuroshio filtered-width operator changed".into());
        }
    }
    for asset in fig["figures"].as_object().unwrap().values() {
        if inputs[asset["file"].as_str().unwrap()] != asset["sha256"] {
            return Err("Kuroshio filtered-width figure asset changed".into());
        }
    }
    let found = diagnostics
        .iter()
        .filter(|d| d["id"] == ID)
        .collect::<Vec<_>>();
    if found.len() != 1 || *found[0] != expected_record(&doc) {
        return Err("Kuroshio filtered-width scope/source projection changed".into());
    }
    let owner = bundle
        .collections
        .get("objects")
        .into_iter()
        .flatten()
        .find(|o| o["id"] == "current:kuroshio")
        .ok_or("Missing filtered-width owner")?;
    if !owner["diagnostic_ids"]
        .as_array()
        .is_some_and(|ids| ids.contains(&json!(ID)))
    {
        return Err("Missing filtered-width diagnostic owner join".into());
    }
    let selected = rows.iter().filter(owned).collect::<Vec<_>>();
    if selected.len() != 192 {
        return Err("Incomplete Kuroshio filtered plot readings".into());
    }
    for (i, sample) in doc["samples"].as_array().unwrap().iter().enumerate() {
        let id = format!("width-sample:kuroshio-filtered-width:samples:{i}");
        let matches = selected
            .iter()
            .filter(|r| r["id"] == id)
            .collect::<Vec<_>>();
        if matches.len() != 1
            || matches[0]["source_sample"] != *sample
            || matches[0]["entity_id"] != "current:kuroshio"
            || !owner["width_sample_ids"]
                .as_array()
                .is_some_and(|ids| ids.contains(&json!(id)))
        {
            return Err("Kuroshio filtered plot sample/owner mismatch".into());
        }
    }
    if mentioned {
        return Err("Filtered plot readings cannot become inventory widths".into());
    }
    Ok(())
}
pub fn scene(bundle: &crate::Bundle) -> Value {
    if !bundle
        .collections
        .get("diagnostics")
        .into_iter()
        .flatten()
        .any(|d| d["id"] == ID)
    {
        return Value::Null;
    }
    let doc = document();
    let fig = figure();
    let mut rows = bundle
        .collections
        .get("width_samples")
        .into_iter()
        .flatten()
        .filter(|r| r["diagnostic_id"] == ID)
        .collect::<Vec<_>>();
    rows.sort_by(|a, b| {
        a["plot_year"]
            .as_f64()
            .unwrap()
            .total_cmp(&b["plot_year"].as_f64().unwrap())
    });
    let samples=rows.iter().map(|r|json!({"id":r["id"],"sample_label":r["source_sample"]["sample_label"],
  "plot_year":r["plot_year"],"plot_year_label":r["plot_year_label"],"plot_month_label":r["plot_month_label"],
  "value_km":r["value_km"],"plot_reading_interval_km":r["plot_reading_interval_km"],"source_pointer":r["sample_path"]})).collect::<Vec<_>>();
    json!({"kind":"kuroshio_filtered_width_curve","title":"Kuroshio: published filtered regional width curve", "scope":doc["scope_note"],
  "source_file":FILE,"source_sha256":pin(RAW),"source_url":doc["source_url"],"source_citation":doc["source_citation"],
  "source_locator":doc["source_locator"],"source_temporal_filter":doc["source_temporal_filter"],"cautions":doc["cautions"],
  "figure_file":fig["figures"][".svg"]["file"],"figure_sha256":fig["figures"][".svg"]["sha256"],
  "figure_alt":"192 month-midpoint plot readings of a half-year-filtered regional width curve. Values are about190–225km with a separate five-kilometre graphical allowance. Month labels are not raw monthly means or exact observation dates. No annual extrema or physical map edges are supplied.",
  "diagnostic_id":ID,"sample_family":FAMILY,"samples":samples,"sample_count":samples.len()})
}
pub fn query(matches: &[&Value], bundle: &crate::Bundle) -> Value {
    if matches.iter().any(|r| r["id"] == ID) {
        scene(bundle)
    } else {
        Value::Null
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> crate::Bundle {
        let doc = document();
        let fig = figure();
        let mut inputs = doc["input_sha256"].clone();
        inputs[FILE] = json!(pin(RAW));
        inputs[FIGURE_FILE] = json!(pin(FIGURE_RAW));
        inputs["analysis/kuroshio_filtered_width.py"] = json!(pin(HELPER));
        for value in [&doc, &fig] {
            inputs[value["generator_file"].as_str().unwrap()] = value["generator_sha256"].clone();
        }
        for asset in fig["figures"].as_object().unwrap().values() {
            inputs[asset["file"].as_str().unwrap()] = asset["sha256"].clone();
        }
        let mut context = doc.clone();
        context.as_object_mut().unwrap().remove("samples");
        let rows=doc["samples"].as_array().unwrap().iter().enumerate().map(|(i,s)|json!({
   "id":format!("width-sample:kuroshio-filtered-width:samples:{i}"),"entity_id":"current:kuroshio","current_id":"kuroshio",
   "sample_family":FAMILY,"diagnostic_id":ID,"sample_path":format!("/samples/{i}"),"phase_path":null,"source_phase":null,
   "source_sample":s,"source_context":context,"value_km":s["approximate_width_km"],"plot_reading_interval_km":s["plot_reading_interval_km"],
   "month":null,"year":null,"phase_label":s["sample_label"],"longitude_degrees_east":null,"metric":doc["width_metric"],"source_url":doc["source_url"],"status":s["status"],
   "observation_date":null,"source_algorithm":null,"diagnostic_sensitivity_interval_km":null,"sampling_bracket_interval_km":null,
   "resolution_review_required":null,"whole_current_representative":false,"width_rank_eligible":false,"is_confidence_interval":false,
   "annual_width_range_km":null,"measurement_uncertainty_interval_km":null,"plot_year":s["plot_year"],"plot_year_label":s["plot_year_label"],
   "plot_month_label":s["plot_month_label"],"sample_time_kind":doc["sample_time_kind"],"source_temporal_filter":doc["source_temporal_filter"],
   "sample_time_is_observation_date":false,"samples_are_raw_monthly_means":false})).collect::<Vec<_>>();
        let ids = rows.iter().map(|r| r["id"].clone()).collect::<Vec<_>>();
        crate::Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest: json!({"input_sha256":inputs}),
            collections: std::collections::BTreeMap::from([
                ("diagnostics".into(), vec![expected_record(&doc)]),
                ("width_samples".into(), rows),
                (
                    "objects".into(),
                    vec![
                        json!({"id":"current:kuroshio","diagnostic_ids":[ID],"width_sample_ids":ids}),
                    ],
                ),
                ("widths".into(), vec![]),
            ]),
        }
    }
    #[test]
    fn exact_filtered_source_projects_all_samples_and_rejects_fake_calendar_support() {
        let bundle = fixture();
        assert!(validate(&bundle).is_ok());
        assert!(crate::samples::validate(&bundle.collections, &bundle.manifest).is_ok());
        assert_eq!(scene(&bundle)["sample_count"], 192);
        for (key, value) in [
            ("plot_year", json!(2026.)),
            ("month", json!(1)),
            ("year", json!(1993)),
            ("observation_date", json!("1993-01-15")),
            ("samples_are_raw_monthly_means", json!(true)),
            ("sample_time_is_observation_date", json!(true)),
        ] {
            let mut bad = fixture();
            bad.collections.get_mut("width_samples").unwrap()[0][key] = value;
            assert!(
                crate::samples::validate(&bad.collections, &bad.manifest).is_err(),
                "{key}"
            );
        }
    }
    #[test]
    fn coherent_source_rebinding_missing_samples_and_asset_changes_reject() {
        let mut bad = fixture();
        let row = &mut bad.collections.get_mut("diagnostics").unwrap()[0];
        row["document"]["samples_are_raw_monthly_means"] = json!(true);
        let raw = row["document"].to_string();
        row["source_json"] = json!(raw);
        row["source_file_sha256"] = json!(pin(&raw));
        bad.manifest["input_sha256"][FILE] = json!(pin(&raw));
        assert!(validate(&bad).is_err());
        let mut bad = fixture();
        bad.collections.get_mut("width_samples").unwrap().pop();
        assert!(validate(&bad).is_err());
        let mut bad = fixture();
        bad.collections.get_mut("objects").unwrap()[0]["width_sample_ids"] = json!([]);
        assert!(validate(&bad).is_err());
        for file in [
            FILE,
            FIGURE_FILE,
            "plans/kuroshio-filtered-width-time-series-protocol-v1.md",
            "figures/kuroshio-ecs-filtered-width-time-series.svg",
        ] {
            let mut bad = fixture();
            bad.manifest["input_sha256"][file] = json!("0".repeat(64));
            assert!(validate(&bad).is_err(), "{file}");
        }
    }
    #[test]
    fn plot_width_laundering_rejects_after_source_and_owner_erasure() {
        let mut bad = fixture();
        bad.collections
            .get_mut("widths")
            .unwrap()
            .push(json!({"id":"fake-width","source_file":FILE,"approximate_width_km":210}));
        assert!(validate(&bad).is_err());
        bad.collections.get_mut("objects").unwrap().clear();
        bad.collections.get_mut("diagnostics").unwrap().clear();
        bad.collections.get_mut("width_samples").unwrap().clear();
        bad.manifest = json!({});
        assert!(validate(&bad).is_err());
    }
}
