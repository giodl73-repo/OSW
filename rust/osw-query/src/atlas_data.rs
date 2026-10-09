//! Checked source documents for the global route atlas and its almanac cards.
use crate::{Bundle, Store};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::BTreeSet;
const ADDITIONS: &str = "research/ocean-current-inventory-expansion-candidates.json";
const JOIN: &str = "research/ocean-current-reference-route-state-join.json";
const GULF_WIDTHS: &str = "research/gulf-stream-section-width-series.json";

fn gulf_width_scope(doc: &Value) -> Result<(), String> {
    if doc["current_id"] != "gulf-stream-system"
        || doc["status"] != "derived_width_candidate_requires_scientific_review"
        || doc["metric"] != "meridional_half_peak_eastward_velocity_section_span"
        || doc["section_longitude"].as_f64() != Some(-70.)
        || doc["latitude_window"] != json!([35, 41])
        || [
            "whole_current_representative",
            "width_rank_eligible",
            "annual_extrema_eligible",
            "is_confidence_interval",
        ]
        .iter()
        .any(|key| doc[*key] != false)
        || doc.get("annual_width_range_km") != Some(&Value::Null)
    {
        return Err("Invalid atlas dated section width scope".into());
    }
    let spans = doc["sample_value_spans"]
        .as_array()
        .ok_or("Missing atlas sampled width spans")?;
    if spans.iter().any(|s| {
        s["range_kind"] != "span_of_sampled_rounded_section_candidate_values_not_annual_extrema"
    }) {
        return Err("Invalid atlas sampled width span role".into());
    }
    Ok(())
}

fn gulf_width_document(bundle: &Bundle) -> Result<(), String> {
    let doc = document(bundle, GULF_WIDTHS, "osw.current-section-width-series.v1")?;
    gulf_width_scope(&doc)?;
    if !bundle
        .collections
        .get("diagnostics")
        .into_iter()
        .flatten()
        .any(|r| r["id"] == "diagnostic:gulf-stream-widths" && r["document"] == doc)
    {
        return Err("Atlas dated width source disagrees with query diagnostic".into());
    }
    for (path, hash) in [
        (
            doc["protocol_file"]
                .as_str()
                .ok_or("Missing dated width protocol")?,
            &doc["protocol_sha256"],
        ),
        (
            "plans/ocean-current-width-measurement-protocol-v1.md",
            &doc["general_protocol_sha256"],
        ),
        (
            "analysis/build_current_section_width_series.py",
            &doc["generator_sha256"],
        ),
        (
            "analysis/build_gulf_stream_geostrophic_path.py",
            &doc["velocity_sampler_sha256"],
        ),
    ] {
        if bundle.manifest["input_sha256"][path] != *hash {
            return Err("Stale atlas dated width dependency".into());
        }
    }
    let frames = doc["frames"]
        .as_array()
        .ok_or("Missing atlas dated width frames")?;
    let actual: Vec<_> = bundle
        .collections
        .get("geometry_frames")
        .into_iter()
        .flatten()
        .filter(|r| {
            r["timeline_file"]
                .as_str()
                .is_some_and(|p| TIMELINES.contains(&p))
        })
        .collect();
    if frames.is_empty() || frames.len() != actual.len() {
        return Err("Incomplete atlas dated width inventory".into());
    }
    let mut previous = "";
    for frame in frames {
        let date = frame["date"]
            .as_str()
            .filter(|d| crate::temporal::valid_day(d))
            .ok_or("Invalid atlas width date")?;
        let source = frame["source_subset"]
            .as_str()
            .ok_or("Missing atlas width source subset")?;
        if date <= previous
            || frame["range_kind"]
                != "finite_boundary_threshold_sensitivity_not_confidence_or_annual_range"
            || bundle.manifest["input_sha256"][source] != frame["source_subset_sha256"]
            || !actual.iter().any(|r| {
                r["date"] == date
                    && r["source_subset_sha256"] == frame["source_subset_sha256"]
                    && r["source_algorithm"] == frame["source_algorithm"]
            })
        {
            return Err("Atlas dated width frame disagrees with timeline source".into());
        }
        previous = date;
    }
    Ok(())
}
const WIDTH_DOCUMENTS: [(&str, &str, &str, &str); 3] = [
    (
        "research/leeuwin-a101-monthly-plot-extraction.json",
        "diagnostic:leeuwin-monthly-width",
        "osw.current-monthly-width-plot-extraction.v1",
        "leeuwin",
    ),
    (
        "research/kuroshio-ecs-seasonal-width-profile-extraction.json",
        "diagnostic:kuroshio-seasonal-width",
        "osw.current-seasonal-width-profile-plot-extraction.v1",
        "kuroshio",
    ),
    (
        "research/pacific-necc-oscar-2013-section-diagnostic.json",
        "diagnostic:necc-monthly-section",
        "osw.current-monthly-section-diagnostic.v1",
        "pacific-north-equatorial-countercurrent",
    ),
];

fn width_scope(doc: &Value, owner: &str) -> Result<(), String> {
    if doc["current_id"] != owner
        || [
            "whole_current_representative",
            "width_rank_eligible",
            "seasonal_playback_eligible",
            "is_confidence_interval",
        ]
        .iter()
        .any(|key| doc[*key] != false)
        || ["whole_current_width_km", "annual_width_range_km"]
            .iter()
            .any(|key| doc.get(*key) != Some(&Value::Null))
    {
        return Err("Invalid atlas width diagnostic identity or scientific scope".into());
    }
    if owner == "pacific-north-equatorial-countercurrent" {
        if doc["is_climatology"] != false
            || doc["monthly_width_is_mean_of_instantaneous_widths"] != false
            || ["whole_current_length_km", "annual_length_range_km"]
                .iter()
                .any(|key| doc.get(*key) != Some(&Value::Null))
        {
            return Err("Invalid atlas monthly section scope".into());
        }
    } else if doc["annual_extrema_eligible"] != false
        || doc["geographic_playback_eligible"] != false
        || doc["chart_playback_eligible"] != true
    {
        return Err("Invalid atlas historical width chart scope".into());
    }
    Ok(())
}

fn width_document(
    bundle: &Bundle,
    path: &str,
    id: &str,
    schema: &str,
    owner: &str,
) -> Result<(), String> {
    let doc = document(bundle, path, schema)?;
    width_scope(&doc, owner)?;
    if !bundle
        .collections
        .get("diagnostics")
        .into_iter()
        .flatten()
        .any(|r| r["id"] == id && r["document"] == doc)
    {
        return Err(format!(
            "Atlas width source disagrees with query diagnostic: {path}"
        ));
    }
    Ok(())
}
const TIMELINES: [&str; 2] = [
    "research/ocean-current-dated-timeline-2025.json",
    "research/ocean-current-dated-timeline.json",
];
fn includes(source: &Value, actual: &Value) -> bool {
    match source {
        Value::Object(fields) => fields
            .iter()
            .all(|(key, value)| actual.get(key).is_some_and(|a| includes(value, a))),
        _ => source == actual,
    }
}
fn timeline_records(bundle: &Bundle, path: &str) -> Result<Vec<Value>, String> {
    let doc = document(bundle, path, "osw.current-dated-timeline.v1")?;
    if doc["current_id"] != "gulf-stream-system"
        || doc["annual_extrema_eligible"] != false
        || doc.get("annual_length_range_km") != Some(&Value::Null)
        || doc.get("annual_width_range_km") != Some(&Value::Null)
    {
        return Err("Invalid atlas timeline identity or annual scope".into());
    }
    let frames = doc["frames"]
        .as_array()
        .ok_or("Missing atlas timeline frames")?;
    let actual = bundle
        .collections
        .get("geometry_frames")
        .ok_or("Missing atlas query frames")?;
    if frames.is_empty()
        || frames.len() != actual.iter().filter(|r| r["timeline_file"] == path).count()
    {
        return Err("Incomplete atlas timeline frame inventory".into());
    }
    for (file, hash) in [
        (
            doc["audit_file"]
                .as_str()
                .ok_or("Missing atlas timeline audit")?,
            &doc["audit_sha256"],
        ),
        (
            "analysis/build_current_dated_timeline.py",
            &doc["generator_sha256"],
        ),
        (
            "analysis/build_gulf_stream_geostrophic_path.py",
            &doc["trace_algorithm_sha256"],
        ),
        (
            "figures/osw-province-atlas-interactive.svg",
            &doc["state_map_sha256"],
        ),
    ] {
        if bundle.manifest["input_sha256"][file] != *hash {
            return Err("Stale atlas timeline dependency".into());
        }
    }
    let mut previous = "";
    let mut records = Vec::new();
    for frame in frames {
        let date = frame["date"]
            .as_str()
            .ok_or("Missing atlas timeline date")?;
        if date <= previous {
            return Err("Atlas timeline dates must be unique and ordered".into());
        }
        previous = date;
        let row = actual
            .iter()
            .find(|r| r["timeline_file"] == path && r["date"] == date)
            .ok_or("Missing atlas query frame")?;
        if !includes(frame, row)
            || row["timeline_sha256"] != bundle.manifest["atlas_receipts"][path]["source_sha256"]
            || [
                "layer",
                "method",
                "geometry_role",
                "sampling_note",
                "limitations",
                "annual_extrema_eligible",
                "annual_length_range_km",
                "annual_width_range_km",
            ]
            .iter()
            .any(|key| doc[*key] != row[*key])
        {
            return Err("Atlas timeline disagrees with its query frames".into());
        }
        for (file_key, hash_key) in [
            ("source_subset", "source_subset_sha256"),
            ("figure", "figure_sha256"),
        ] {
            let file = frame[file_key]
                .as_str()
                .ok_or("Missing atlas timeline source dependency")?;
            if bundle.manifest["input_sha256"][file] != frame[hash_key] {
                return Err("Stale atlas timeline frame dependency".into());
            }
        }
        records.push(json!({"id":row["id"],"label":row["label"],"map_features":[{"geometry":{"type":"LineString","coordinates":frame["coordinates_lon_lat"]},"role":doc["geometry_role"],"observation_date":date}]}));
    }
    let scene = crate::map::scene(&records.iter().collect::<Vec<_>>());
    if !scene["omitted_features"]
        .as_array()
        .is_some_and(|v| v.is_empty())
    {
        return Err("Invalid atlas timeline geometry".into());
    }
    Ok(records)
}
fn observed_view(bundle: &Bundle) -> Result<Value, String> {
    let path = crate::observed_sections::SOURCE;
    let doc = document(bundle, path, "osw.ladcp-section-diagnostic.v1")?;
    let diagnostics = bundle
        .collections
        .get("diagnostics")
        .ok_or("Missing observed-section query diagnostics")?;
    if !diagnostics
        .iter()
        .any(|r| r["id"] == "diagnostic:antilles-observed-sections" && r["document"] == doc)
    {
        return Err("Atlas observed-section source disagrees with query diagnostic".into());
    }
    let inventory = doc["inventory_file"]
        .as_str()
        .ok_or("Missing observed-section inventory")?;
    if bundle.manifest["input_sha256"][inventory] != doc["inventory_sha256"] {
        return Err("Stale observed-section source inventory".into());
    }
    let series = bundle
        .collections
        .get("series")
        .ok_or("Missing observed-section query series")?;
    if !series.iter().any(|r| {
        r["entity_id"] == "current:antilles"
            && r["evidence_role"] == "observed_sections_with_unadmitted_one_sided_span"
            && r["evidence_sha256"] == bundle.manifest["atlas_receipts"][path]["source_sha256"]
            && r["inventory_sha256"] == doc["inventory_sha256"]
    }) {
        return Err("Atlas observed-section series disagrees with source hashes".into());
    }
    crate::observed_sections::view(&doc)
}

pub(crate) fn document(bundle: &Bundle, path: &str, schema: &str) -> Result<Value, String> {
    let receipt = &bundle.manifest["atlas_receipts"][path];
    let raw = receipt["source_json"]
        .as_str()
        .ok_or("Missing atlas source bytes")?;
    let hash = format!("{:x}", Sha256::digest(raw.as_bytes()));
    if receipt["source_sha256"] != hash || bundle.manifest["input_sha256"][path] != hash {
        return Err(format!("Changed atlas source receipt: {path}"));
    }
    let doc: Value = serde_json::from_str(raw).map_err(|e| e.to_string())?;
    if doc["schema"] != schema {
        return Err(format!("Unsupported atlas source schema: {path}"));
    }
    Ok(doc)
}
pub fn validate(bundle: &Bundle) -> Result<(), String> {
    let Some(receipts) = bundle.manifest.get("atlas_receipts") else {
        return Ok(());
    };
    let receipts = receipts
        .as_object()
        .ok_or("Invalid atlas receipt inventory")?;
    let additions = document(
        bundle,
        ADDITIONS,
        "osw.current-inventory-expansion-candidates.v1",
    )?;
    crate::proposed_widths::validate_proposals(&additions)?;
    if additions["current_ledger_sha256"]
        != bundle.manifest["input_sha256"]["research/ocean-current-almanac.json"]
    {
        return Err("Atlas proposed additions refer to a different current ledger".into());
    }
    let astrid_path = crate::astrid_scales::PATH;
    let mut paths = BTreeSet::from([ADDITIONS]);
    if receipts.contains_key(crate::qualitative_calendar::PATH) {
        document(
            bundle,
            crate::qualitative_calendar::PATH,
            "osw.current-qualitative-seasonal-scope-audit.v1",
        )?;
        paths.insert(crate::qualitative_calendar::PATH);
    }
    if receipts.contains_key(crate::atlantic_euc_sections::PATH) {
        document(
            bundle,
            crate::atlantic_euc_sections::PATH,
            "osw.current-source-scope-audit.v1",
        )?;
        paths.insert(crate::atlantic_euc_sections::PATH);
    }
    if receipts.contains_key(astrid_path)
        || bundle
            .collections
            .get("objects")
            .is_some_and(|rows| rows.iter().any(|r| r["id"] == "eddy:geography:astrid-2000"))
    {
        let astrid = document(bundle, astrid_path, "osw.named-eddy-radial-scale-audit.v1")?;
        crate::astrid_scales::validate(&astrid)?;
        paths.insert(astrid_path);
    }
    let radius_path = crate::ring_radii::PATH;
    if receipts.contains_key(radius_path)
        || bundle.collections.get("objects").is_some_and(|rows| {
            rows.iter().any(|r| {
                matches!(
                    r["id"].as_str(),
                    Some(
                        "eddy:geography:ana-2004"
                            | "eddy:geography:eliza-2007"
                            | "eddy:geography:jeannette-2012"
                    )
                )
            })
        })
    {
        let radii = document(
            bundle,
            radius_path,
            "osw.agulhas-ring-radius-scope-audit.v1",
        )?;
        crate::ring_radii::validate(&radii)?;
        paths.insert(radius_path);
    }
    let routes = bundle
        .collections
        .get("reference_routes")
        .ok_or("Missing atlas routes")?;
    let objects = bundle
        .collections
        .get("objects")
        .ok_or("Missing atlas objects")?;
    for route in routes {
        let path = route["candidate_file"]
            .as_str()
            .ok_or("Atlas route has no candidate file")?;
        if !paths.insert(path) {
            return Err("Duplicate atlas candidate file".into());
        }
        let doc = document(bundle, path, "osw.current-reference-path-input.v1")?;
        if route["candidate_sha256"] != receipts[path]["source_sha256"]
            || doc["current_id"] != route["current_id"]
            || doc["reported_approximate_reference_path_km"].as_f64()
                != route["approximate_reference_path_km"].as_f64()
        {
            return Err(format!(
                "Atlas route report disagrees with its catalog: {path}"
            ));
        }
        let owner = format!(
            "current:{}",
            route["current_id"]
                .as_str()
                .ok_or("Invalid atlas route owner")?
        );
        let matches = objects
            .iter()
            .find(|r| r["id"] == owner)
            .and_then(|r| r["map_features"].as_array())
            .is_some_and(|fs| {
                fs.iter().any(|f| {
                    f["candidate_id"] == route["id"]
                        && f["geometry"]["coordinates"] == doc["coordinates_lon_lat"]
                })
            });
        if !matches {
            return Err(format!(
                "Atlas report geometry disagrees with its query route: {path}"
            ));
        }
    }
    if receipts.contains_key(JOIN) {
        paths.insert(JOIN);
        let join = document(bundle, JOIN, "osw.current-reference-route-state-join.v1")?;
        for (path, hash) in join["input_sha256"]
            .as_object()
            .ok_or("Missing atlas join dependencies")?
        {
            if bundle.manifest["input_sha256"][path] != *hash {
                return Err(format!("Stale atlas state join dependency: {path}"));
            }
        }
        let states = join["states"]
            .as_object()
            .ok_or("Missing atlas joined states")?;
        let actual = bundle
            .collections
            .get("states")
            .ok_or("Missing atlas state collection")?;
        if states.len() != actual.len()
            || actual.iter().any(|r| {
                !r["code"]
                    .as_str()
                    .is_some_and(|code| states.contains_key(code))
            })
        {
            return Err("Atlas joined state inventory disagrees with query states".into());
        }
    }
    for path in TIMELINES {
        if receipts.contains_key(path) {
            paths.insert(path);
            timeline_records(bundle, path)?;
        }
    }
    if receipts.contains_key(crate::observed_sections::SOURCE) {
        paths.insert(crate::observed_sections::SOURCE);
        observed_view(bundle)?;
    }
    for (path, id, schema, owner) in WIDTH_DOCUMENTS {
        if receipts.contains_key(path) {
            paths.insert(path);
            width_document(bundle, path, id, schema, owner)?;
        }
    }
    if receipts.contains_key(GULF_WIDTHS) {
        paths.insert(GULF_WIDTHS);
        gulf_width_document(bundle)?;
    }
    let mut model_documents = std::collections::BTreeMap::new();
    for (path, schema) in [
        (
            crate::norkyst_data::TIMELINE,
            "osw.norkyst-section-timeline.v1",
        ),
        (crate::norkyst_data::MAPS, "osw.norkyst-map-frames.v1"),
    ] {
        if receipts.contains_key(path) {
            paths.insert(path);
            let doc = document(bundle, path, schema)?;
            crate::norkyst_data::scope(&doc, path)?;
            crate::norkyst_data::dependencies(&doc, path, &bundle.manifest["input_sha256"])?;
            model_documents.insert(path, doc);
        }
    }
    if let (Some(timeline), Some(maps)) = (
        model_documents.get(crate::norkyst_data::TIMELINE),
        model_documents.get(crate::norkyst_data::MAPS),
    ) {
        crate::norkyst_data::synchronized(timeline, maps)?;
    }
    if receipts.keys().map(String::as_str).collect::<BTreeSet<_>>() != paths {
        return Err("Unexpected or missing atlas source receipt".into());
    }
    Ok(())
}
impl Store {
    pub fn atlas_snapshot(&self) -> Result<Value, String> {
        validate(&self.bundle)?;
        let receipts = self.bundle.manifest["atlas_receipts"]
            .as_object()
            .ok_or("Missing atlas source receipts")?;
        let mut sources = json!({});
        for (path, receipt) in receipts {
            sources[path] = receipt["source_json"].clone();
        }
        let seasons = self.seasons_snapshot()?;
        for (key, path) in [
            ("widths", "research/ocean-current-width-inventory.json"),
            (
                "routes",
                "research/ocean-current-reference-path-candidates.json",
            ),
            (
                "frames",
                "research/ocean-current-seasonal-route-frames.json",
            ),
        ] {
            sources[path] = seasons["sources_json"][key].clone();
        }
        sources["research/ocean-motion-dashboard.json"] =
            self.dashboard_snapshot()?["snapshot_json"].clone();
        let mut timeline_scenes = json!({});
        for path in TIMELINES {
            if receipts.contains_key(path) {
                let records = timeline_records(&self.bundle, path)?;
                let mut scene = crate::map::scene(&records.iter().collect::<Vec<_>>());
                scene["display_transform"] =
                    json!(format!("translate(60 90) scale({})", 1480. / 360.));
                timeline_scenes[path] = scene;
            }
        }
        let mut observed_section_views = json!({});
        if receipts.contains_key(crate::observed_sections::SOURCE) {
            observed_section_views[crate::observed_sections::SOURCE] = observed_view(&self.bundle)?;
        }
        Ok(
            json!({"ok":true,"engine":"rust-osw-query-v1","bundle_sha256":self.metadata()["bundle_sha256"],
                "sources_json":sources,"state_join_available":receipts.contains_key(JOIN),"timeline_scenes":timeline_scenes,"observed_section_views":observed_section_views,"coastal_composite_width_scene":seasons["coastal_composite_width_scene"]}),
        )
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn dated_widths_keep_local_metric_and_sample_span_roles() {
        let doc: Value = serde_json::from_str(include_str!(
            "../../../research/gulf-stream-section-width-series.json"
        ))
        .unwrap();
        assert!(gulf_width_scope(&doc).is_ok());
        for (key, value) in [
            ("metric", json!("flow_normal_width")),
            ("annual_width_range_km", json!([70, 150])),
            ("annual_extrema_eligible", json!(true)),
            ("section_longitude", json!(-71)),
        ] {
            let mut bad = doc.clone();
            bad[key] = value;
            assert!(gulf_width_scope(&bad).is_err());
        }
        let mut bad = doc.clone();
        bad["sample_value_spans"][0]["range_kind"] = json!("annual_extrema");
        assert!(gulf_width_scope(&bad).is_err());
    }
    #[test]
    fn historical_width_sources_cannot_be_promoted_to_whole_current_ranges() {
        for (raw, owner) in [
            (
                include_str!("../../../research/leeuwin-a101-monthly-plot-extraction.json"),
                "leeuwin",
            ),
            (
                include_str!(
                    "../../../research/kuroshio-ecs-seasonal-width-profile-extraction.json"
                ),
                "kuroshio",
            ),
            (
                include_str!("../../../research/pacific-necc-oscar-2013-section-diagnostic.json"),
                "pacific-north-equatorial-countercurrent",
            ),
        ] {
            let doc: Value = serde_json::from_str(raw).unwrap();
            assert!(width_scope(&doc, owner).is_ok());
            for key in [
                "whole_current_representative",
                "width_rank_eligible",
                "seasonal_playback_eligible",
                "is_confidence_interval",
            ] {
                let mut bad = doc.clone();
                bad[key] = json!(true);
                assert!(width_scope(&bad, owner).is_err(), "{owner}: {key}");
            }
            let mut bad = doc.clone();
            bad["annual_width_range_km"] = json!([10, 20]);
            assert!(width_scope(&bad, owner).is_err());
            let mut bad = doc.clone();
            bad.as_object_mut()
                .unwrap()
                .remove("whole_current_width_km");
            assert!(width_scope(&bad, owner).is_err());
        }
    }
    fn receipt(doc: &Value) -> Value {
        let raw = doc.to_string();
        json!({"source_sha256":format!("{:x}",Sha256::digest(raw.as_bytes())),"source_json":raw})
    }
    #[test]
    fn report_identity_and_geometry_are_bound_to_the_catalog() {
        let path = "research/test-route.json";
        let coords = json!([[1., 2.], [3., 4.]]);
        let report = json!({"schema":"osw.current-reference-path-input.v1","current_id":"test","coordinates_lon_lat":coords,"reported_approximate_reference_path_km":5});
        let additions = json!({"schema":"osw.current-inventory-expansion-candidates.v1","current_ledger_sha256":"ledger"});
        let mut bundle = Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest: json!({"atlas_receipts":{ADDITIONS:receipt(&additions),path:receipt(&report)},"input_sha256":{"research/ocean-current-almanac.json":"ledger"}}),
            collections: std::collections::BTreeMap::new(),
        };
        for p in [ADDITIONS, path] {
            bundle.manifest["input_sha256"][p] =
                bundle.manifest["atlas_receipts"][p]["source_sha256"].clone();
        }
        bundle.collections.insert("reference_routes".into(),vec![json!({"id":"route:test","candidate_file":path,"candidate_sha256":bundle.manifest["atlas_receipts"][path]["source_sha256"],"current_id":"test","approximate_reference_path_km":5})]);
        bundle.collections.insert("objects".into(),vec![json!({"id":"current:test","map_features":[{"candidate_id":"route:test","geometry":{"coordinates":coords}}]})]);
        assert!(validate(&bundle).is_ok());
        let mut changed = report.clone();
        changed["coordinates_lon_lat"] = json!([[1., 2.], [4., 5.]]);
        bundle.manifest["atlas_receipts"][path] = receipt(&changed);
        bundle.manifest["input_sha256"][path] =
            bundle.manifest["atlas_receipts"][path]["source_sha256"].clone();
        bundle.collections.get_mut("reference_routes").unwrap()[0]["candidate_sha256"] =
            bundle.manifest["atlas_receipts"][path]["source_sha256"].clone();
        assert!(validate(&bundle).unwrap_err().contains("geometry"));
        changed["current_id"] = json!("other");
        bundle.manifest["atlas_receipts"][path] = receipt(&changed);
        bundle.manifest["input_sha256"][path] =
            bundle.manifest["atlas_receipts"][path]["source_sha256"].clone();
        bundle.collections.get_mut("reference_routes").unwrap()[0]["candidate_sha256"] =
            bundle.manifest["atlas_receipts"][path]["source_sha256"].clone();
        assert!(validate(&bundle).unwrap_err().contains("catalog"));
    }
}
