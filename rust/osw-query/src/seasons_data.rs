//! Checked presentation sources for the seasonal evidence page.
use crate::{Bundle, Store};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::BTreeSet;
const SOURCES: [(&str, &str, &str); 4] = [
    (
        "widths",
        "research/ocean-current-width-inventory.json",
        "osw.current-width-inventory.v1",
    ),
    (
        "routes",
        "research/ocean-current-reference-path-candidates.json",
        "osw.current-reference-path-candidates.v1",
    ),
    (
        "frames",
        "research/ocean-current-seasonal-route-frames.json",
        "osw.current-seasonal-route-frames.v1",
    ),
    (
        "directions",
        "research/new-guinea-coastal-current-seasonal-direction-scope-audit.json",
        "osw.current-seasonal-direction-scope-audit.v1",
    ),
];
fn documents(bundle: &Bundle) -> Result<Value, String> {
    let mut docs = json!({});
    for (key, path, schema) in SOURCES {
        let receipt = &bundle.manifest["seasons_receipts"][key];
        let raw = receipt["source_json"]
            .as_str()
            .ok_or("Missing seasonal source bytes")?;
        let hash = format!("{:x}", Sha256::digest(raw.as_bytes()));
        if receipt["source_file"] != path
            || receipt["source_sha256"] != hash
            || bundle.manifest["input_sha256"][path] != hash
        {
            return Err("Changed seasonal source receipt".into());
        }
        let doc: Value = serde_json::from_str(raw).map_err(|e| e.to_string())?;
        if doc["schema"] != schema {
            return Err("Unsupported seasonal source schema".into());
        }
        docs[key] = doc;
    }
    Ok(docs)
}
fn projection(source: &Value, actual: &Value) -> bool {
    match source {
        Value::Object(fields) => fields
            .iter()
            .all(|(k, v)| actual.get(k).is_some_and(|a| projection(v, a))),
        _ => source == actual,
    }
}
fn adcp_width_scope(row: &Value) -> Result<(), String> {
    let id = row["id"].as_str().unwrap_or("");
    if row["phase_kind"] != "survey_layer_median_threshold_width"
        && row.get("adcp_threshold_context").is_none()
        && !id.starts_with("agulhas-return-boebel-2003-adcp-")
    {
        return Ok(());
    }
    let crossing = id
        .strip_prefix("agulhas-return-boebel-2003-adcp-")
        .ok_or("ADCP width identity mismatch")?;
    let (width, error, projection) = match crossing {
        "a" => (48, 14, 1),
        "b1" => (73, 18, 6),
        "b2" => (78, 18, 1),
        "c" => (48, 18, 17),
        _ => return Err("ADCP width crossing mismatch".into()),
    };
    let context = &row["adcp_threshold_context"];
    if row["current_id"] != "agulhas-return"
        || row["phase_kind"] != "survey_layer_median_threshold_width"
        || row["measurement_type"] != "published_multilayer_ADCP_threshold_width"
        || row["width_metric"]
            != "median_across_ADCP_depth_bins_of_flow_normal_half_maximum_isotach_distance"
        || row["boundary_sides"] != "paired_half_maximum_isotachs_per_bin_median"
        || row["approximate_width_km"] != width
        || row["reported_total_error_km"] != error
        || context["crossing_id"] != crossing
        || context["velocity_threshold_fraction"] != 0.5
        || context["reported_projection_uncertainty_km"] != projection
        || context["projection_error_is_included_in_total"] != true
        || context["campaign_context_year"] != 1997
        || context["deepest_reported_ADCP_bin_m"] != json!([325, 375])
        || ["confidence_level"]
            .iter()
            .any(|k| context.get(k) != Some(&Value::Null))
        || [
            "boundary_coordinates_extracted",
            "depth_bin_range_is_fixed_width_layer",
            "exact_crossing_dates_extracted",
        ]
        .iter()
        .any(|k| context.get(k) != Some(&json!(false)))
        || [
            "width_range_km",
            "observed_period",
            "calendar_months",
            "section_geometry",
            "fixed_layer_bounds_m",
        ]
        .iter()
        .any(|k| row.get(k) != Some(&Value::Null))
        || [
            "whole_current_representative",
            "width_rank_eligible",
            "annual_extrema_eligible",
            "seasonal_playback_eligible",
            "full_width_inference_eligible",
            "is_confidence_interval",
        ]
        .iter()
        .any(|k| row.get(k) != Some(&json!(false)))
    {
        return Err("ADCP layer-median width or source-error scope mismatch".into());
    }
    Ok(())
}
pub(crate) fn norwegian_coastal_width_scope(row: &Value) -> Result<(), String> {
    // A different publication has its own exact compiled admission. Edited
    // copies still fall through to the original regional-scope guard.
    if crate::hansen_asar_widths::recognizes_width(row) {
        return Ok(());
    }
    let id = "norwegian-coastal-saetre-1999-halten-regional-width";
    if row["id"] != id && row["current_id"] != "norwegian-coastal" {
        return Ok(());
    }
    let context = &row["regional_range_context"];
    if row["id"] != id
        || row["current_id"] != "norwegian-coastal"
        || row["phase_kind"] != "regional_summary"
        || row["measurement_type"] != "published_regional_summary"
        || row["width_metric"] != "author_reported_current_width"
        || row["width_range_km"] != json!([20, 30])
        || row["range_kind"] != "reported_typical_regional_width_span"
        || row["source_url"]
            != "https://www.sciencedirect.com/science/article/abs/pii/S0278434399000412"
        || [
            "approximate_width_km",
            "observed_period",
            "calendar_months",
            "section_geometry",
            "fixed_layer_bounds_m",
        ]
        .iter()
        .any(|k| row.get(k) != Some(&Value::Null))
        || [
            "whole_current_representative",
            "width_rank_eligible",
            "annual_extrema_eligible",
            "seasonal_playback_eligible",
            "full_width_inference_eligible",
            "is_confidence_interval",
        ]
        .iter()
        .any(|k| row.get(k) != Some(&json!(false)))
        || [
            "boundary_coordinates_supplied",
            "adjacent_hydrography_is_width_sampling_period",
            "water_mass_extent_is_current_width",
            "shelf_width_is_current_width",
            "drifter_speed_filter_is_width_boundary",
        ]
        .iter()
        .any(|k| context.get(k) != Some(&json!(false)))
    {
        return Err("Norwegian coastal regional width scope mismatch".into());
    }
    Ok(())
}
pub fn validate(bundle: &Bundle) -> Result<(), String> {
    if bundle.manifest.get("seasons_receipts").is_none() {
        return Ok(());
    }
    let docs = documents(bundle)?;
    for (key, field, collection) in [
        ("widths", "measurements", "widths"),
        ("routes", "candidates", "reference_routes"),
        ("frames", "frames", "seasonal_routes"),
    ] {
        let mut source = docs[key][field]
            .as_array()
            .ok_or("Missing seasonal source records")?
            .clone();
        if key == "widths" {
            source.extend(crate::current_measurements::widths(bundle));
            source.extend(crate::current_gap_admissions::widths(bundle));
            source.extend(crate::agulhas_reported::widths(bundle));
            source.extend(crate::satellite_core_widths::widths(bundle));
            source.extend(crate::wicc_review_width::widths(bundle));
            source.extend(crate::eacc_cited_width::widths(bundle));
            source.extend(crate::nwasc_admission::widths(bundle));
            source.extend(crate::hansen_asar_widths::widths(bundle));
            source.extend(crate::neuc_glider_widths::widths(bundle));
            source.extend(crate::aleutian_onishi_width::widths(bundle));
            source.extend(crate::madagascar_dimensions::seasonal_source_widths(bundle)?);
            source.extend(crate::azcc_onken_width::validated_widths(bundle)?);
            source.extend(crate::pacific_nec_nominal_width::validated_widths(bundle)?);
            source.extend(crate::dimoune_section_widths::validated_widths(bundle)?);
            source.extend(crate::atlantic_nec_band_spans::validated_widths(bundle)?);
            source.extend(crate::pacific_sec_jet_widths::validated_widths(bundle)?);
            source.extend(crate::current_core_dimensions::validated_widths(bundle)?);
        }
        if key == "routes" && crate::madagascar_coastal_curve::active(bundle) {
            source = crate::nwasc_reference_route::catalogue(bundle)["candidates"]
                .as_array()
                .unwrap()
                .clone();
        }
        if key == "routes" {
            source.extend(crate::planning::eicc_reference_routes(
                &bundle.collections,
                &bundle.manifest,
            )?);
            source.extend(crate::pacific_secc_reference::routes(
                &bundle.collections,
                &bundle.manifest,
            )?);
            source.extend(crate::south_java_reference::routes(
                &bundle.collections,
                &bundle.manifest,
            )?);
            source.extend(crate::wicc_winter_reference::routes(
                &bundle.collections,
                &bundle.manifest,
            )?);
        }
        let actual = bundle
            .collections
            .get(collection)
            .ok_or("Missing seasonal query collection")?;
        let mut ids = BTreeSet::new();
        if source.len() != actual.len() {
            return Err("Incomplete seasonal source projection".into());
        }
        for row in &source {
            if key == "widths" {
                adcp_width_scope(row)?;
                crate::stream_tube_widths::validate(row)?;
                crate::somali_width::validate(row)?;
                crate::guinea_width::validate(row)?;
                crate::original_regional_widths::validate(row)?;
                crate::portugal_section_span::validate_row(row)?;
                crate::modal_decay_widths::validate(row)?;
                crate::abstract_regional_widths::validate(row)?;
                norwegian_coastal_width_scope(row)?;
            }
            let id = row["id"]
                .as_str()
                .ok_or("Missing seasonal record identity")?;
            if !ids.insert(id) || !actual.iter().any(|r| r["id"] == id && projection(row, r)) {
                return Err("Seasonal source differs from shared records".into());
            }
        }
    }
    let decisions = docs["widths"]["current_decisions"]
        .as_array()
        .ok_or("Missing seasonal current index")?;
    let actual: BTreeSet<_> = bundle.collections["objects"]
        .iter()
        .filter(|r| r["type"] == "named_current")
        .filter_map(|r| r["id"].as_str())
        .collect();
    let mut ids = BTreeSet::new();
    for row in decisions {
        if !row["name"].is_string() {
            return Err("Missing seasonal current name".into());
        }
        let id = format!(
            "current:{}",
            row["current_id"]
                .as_str()
                .ok_or("Missing seasonal current identity")?
        );
        if !ids.insert(id.clone()) || !actual.contains(id.as_str()) {
            return Err("Invalid seasonal current index".into());
        }
    }
    for row in crate::current_catalogue::decisions(bundle) {
        let id = format!("current:{}", row["current_id"].as_str().unwrap());
        if !actual.contains(id.as_str()) || !ids.insert(id) {
            return Err("Invalid admitted seasonal current".into());
        }
    }
    if ids.len() != actual.len() {
        return Err("Incomplete seasonal current index".into());
    }
    let direction = &docs["directions"];
    let phases = direction["phases"]
        .as_array()
        .ok_or("Missing local direction phases")?;
    if direction["current_id"] != "new-guinea-coastal-current" || phases.len() != 3 {
        return Err("Invalid local direction inventory".into());
    }
    for (i, p) in phases.iter().enumerate() {
        let months = [
            json!([11, 12, 1, 2, 3, 4]),
            json!([5, 6, 7, 8, 9, 10]),
            Value::Null,
        ];
        if p["current_id"] != direction["current_id"]
            || p["flow_direction"]
                != [
                    "southeastward",
                    "northwestward",
                    "southeastward NGCC absent; northwestward undercurrent shoals",
                ][i]
            || p["geometry_role"] != "local_direction_symbol_not_current_axis"
            || p["site_lon_lat"] != json!([141.4, -1.7])
            || p["calendar_months"] != months[i]
            || p["playback_eligible"] != json!(i < 2)
            || p["phase_kind"]
                != if i < 2 {
                    "seasonal_direction_composite"
                } else {
                    "event_exception"
                }
            || [
                "length_km",
                "width_km",
                "route_coordinates",
                "annual_length_range_km",
                "annual_width_range_km",
            ]
            .iter()
            .any(|k| p.get(k) != Some(&Value::Null))
        {
            return Err("Invalid local direction scope".into());
        }
    }
    Ok(())
}
fn plans(docs: &Value) -> Result<Value, String> {
    let widths = docs["widths"]["measurements"]
        .as_array()
        .ok_or("Missing widths")?;
    let frames = docs["frames"]["frames"]
        .as_array()
        .ok_or("Missing frames")?;
    let directions = &docs["directions"];
    let mut plans = json!({});
    for current in docs["widths"]["current_decisions"]
        .as_array()
        .ok_or("Missing current index")?
    {
        let id = current["current_id"].as_str().ok_or("Missing current ID")?;
        let owned: Vec<_> = frames.iter().filter(|r| r["current_id"] == id).collect();
        let linked: BTreeSet<_> = owned
            .iter()
            .flat_map(|r| r["width_measurement_ids"].as_array().into_iter().flatten())
            .filter_map(Value::as_str)
            .collect();
        let mut phases = Vec::new();
        for row in widths.iter().filter(|r| {
            r["current_id"] == id && !r["id"].as_str().is_some_and(|w| linked.contains(w))
        }) {
            let label = row["phase_label"]
                .as_str()
                .filter(|v| !v.is_empty())
                .unwrap_or_else(|| {
                    row["time_convention"]
                        .as_str()
                        .unwrap_or("Recorded evidence")
                        .split(' ')
                        .next()
                        .unwrap()
                });
            phases.push(json!({"id":row["id"],"width_id":row["id"],"frame_id":null,"direction_id":null,"label":label,"playback_step_eligible":row["seasonal_playback_eligible"] != false}));
        }
        for row in owned {
            let linked = row["width_measurement_ids"]
                .as_array()
                .ok_or("Missing linked phase widths")?;
            let width = widths.iter().find(|w| linked.contains(&w["id"]));
            phases.push(json!({"id":row["id"],"width_id":width.map(|w|&w["id"]),"frame_id":row["id"],"direction_id":null,"label":row["phase_label"],"playback_step_eligible":true}));
        }
        if directions["current_id"] == id {
            for row in directions["phases"]
                .as_array()
                .ok_or("Missing direction phases")?
            {
                phases.push(json!({"id":row["id"],"width_id":null,"frame_id":null,"direction_id":row["id"],"label":row["phase_label"],"playback_step_eligible":row["playback_eligible"]}));
            }
        }
        let summary = docs["widths"]["seasonal_summaries"]
            .as_array()
            .and_then(|rows| rows.iter().find(|r| r["current_id"] == id));
        let restriction = docs["widths"]["comparability_notes"]
            .as_array()
            .and_then(|rows| rows.iter().find(|r| r["current_id"] == id));
        let comparable = summary.is_some_and(|r| {
            r["measurement_ids"].as_array().is_some_and(|ids| {
                phases
                    .iter()
                    .all(|p| !p["width_id"].is_null() && ids.contains(&p["width_id"]))
            })
        });
        let route_only = phases.iter().filter(|p| !p["frame_id"].is_null()).count() > 1
            && phases
                .iter()
                .filter(|p| p["playback_step_eligible"] == true)
                .all(|p| !p["frame_id"].is_null());
        let direction_count = phases
            .iter()
            .filter(|p| !p["direction_id"].is_null() && p["playback_step_eligible"] == true)
            .count();
        let can_play = phases.len() >= 2
            && restriction.is_none()
            && (comparable || route_only || direction_count > 1);
        let eligible: Vec<_> = if can_play {
            phases
                .iter()
                .enumerate()
                .filter(|(_, p)| p["playback_step_eligible"] == true)
                .map(|(i, _)| i)
                .collect()
        } else {
            Vec::new()
        };
        let mut note="Annual width range and measurement uncertainty: not available. A single dated section does not establish a seasonal cycle.".to_owned();
        if widths.iter().any(|r| {
            r["current_id"] == id && r["phase_kind"] == "published_near_surface_survey_summary"
        }) {
            note="One April 2001 near-surface survey summary. Physical whole-current width, uncertainty and annual ranges remain unknown; this is not April climatology or a seasonal cycle.".to_owned();
        }
        if widths
            .iter()
            .any(|r| r["current_id"] == id && r["phase_kind"] == "model_snapshot_width_summary")
        {
            note = "Local model snapshot on an elapsed model day. Annual climatological forcing is not an annual mean width; observed dates, annual ranges and seasonal playback are unavailable.".to_owned();
        }
        if widths
            .iter()
            .any(|r| r["current_id"] == id && r["phase_kind"] == "multi_year_jet_width_range")
        {
            note="Two local repeat-section jet ranges from the2009-2014 study, separate from mean isopycnal breadths. No dated width series, annual extrema or width uncertainty; no seasonal playback inferred.".to_owned();
        }
        if widths.iter().any(|r| {
            r["current_id"] == id && r["phase_kind"] == "source_reported_current_width_constraint"
        }) {
            note="Published regional width>400km, with unspecified width layer and epoch. The source does not give a finite width, annual range or width error; seasonal playback remains unavailable.".to_owned();
        }
        if let Some(r) = summary {
            let span = r["reported_seasonal_value_span_km"]
                .as_array()
                .ok_or("Missing reported seasonal span")?
                .iter()
                .map(|v| {
                    v.as_f64()
                        .map(|f| f.to_string())
                        .ok_or("Invalid reported seasonal value")
                })
                .collect::<Result<Vec<_>, _>>()?
                .join("â€“");
            note = format!(
                "{span} km: {}",
                r["interpretation"]
                    .as_str()
                    .ok_or("Missing seasonal interpretation")?
            );
        }
        if let Some(r) = docs["frames"]["comparability"]
            .as_array()
            .and_then(|rows| rows.iter().find(|r| r["current_id"] == id))
        {
            note = r["reason"]
                .as_str()
                .ok_or("Missing route comparison scope")?
                .to_owned();
        }
        if let Some(r) = restriction {
            note = r["reason"]
                .as_str()
                .ok_or("Missing width comparison restriction")?
                .to_owned();
        }
        if directions["current_id"] == id {
            note = directions["interpretation"]
                .as_str()
                .ok_or("Missing direction interpretation")?
                .to_owned();
        }
        plans[id] = json!({"current_id":id,"phases":phases,"can_play":can_play,"eligible_indices":eligible,"range_note":note,
            "playback_scope":"Recorded comparable states only; no annual extrema or interpolated boundaries inferred."});
    }
    Ok(plans)
}

fn phase_plans(bundle: &Bundle, docs: &Value) -> Result<Value, String> {
    let mut result = plans(docs)?;
    crate::current_catalogue::add_plans(bundle, &mut result);
    crate::wicc_review_width::apply_phase_plan(bundle, &mut result);
    crate::eacc_cited_width::apply_phase_plan(bundle, &mut result)?;
    crate::pacific_nec_nominal_width::apply_phase_plan(bundle, &mut result)?;
    Ok(result)
}

impl Store {
    pub fn seasons_snapshot(&self) -> Result<Value, String> {
        let mut docs = documents(&self.bundle)?;
        if crate::current_measurements::active(&self.bundle) {
            docs["widths"]["measurements"]
                .as_array_mut()
                .unwrap()
                .extend(crate::current_measurements::widths(&self.bundle));
            docs["widths"]["current_decisions"]
                .as_array_mut()
                .unwrap()
                .extend(crate::current_catalogue::decisions(&self.bundle));
        }
        docs["widths"]["measurements"]
            .as_array_mut()
            .unwrap()
            .extend(crate::agulhas_reported::widths(&self.bundle));
        docs["widths"]["measurements"]
            .as_array_mut()
            .unwrap()
            .extend(crate::nwasc_admission::widths(&self.bundle));
        docs["widths"]["measurements"]
            .as_array_mut()
            .unwrap()
            .extend(crate::hansen_asar_widths::widths(&self.bundle));
        docs["widths"]["measurements"]
            .as_array_mut()
            .unwrap()
            .extend(crate::neuc_glider_widths::widths(&self.bundle));
        docs["widths"]["measurements"]
            .as_array_mut()
            .unwrap()
            .extend(crate::aleutian_onishi_width::widths(&self.bundle));
        docs["widths"]["measurements"]
            .as_array_mut()
            .unwrap()
            .extend(crate::satellite_core_widths::widths(&self.bundle));
        let mut supplemental = crate::current_measurements::widths(&self.bundle);
        docs["widths"]["measurements"]
            .as_array_mut()
            .unwrap()
            .extend(crate::wicc_review_width::widths(&self.bundle));
        supplemental.extend(crate::satellite_core_widths::widths(&self.bundle));
        supplemental.extend(crate::wicc_review_width::widths(&self.bundle));
        supplemental.extend(crate::eacc_cited_width::widths(&self.bundle));
        // Keep the static constraint outside the legacy phase derivation.
        // It is returned in supplemental widths and appended exactly once below.
        let gap_widths = crate::current_gap_admissions::widths(&self.bundle);
        docs["widths"]["measurements"]
            .as_array_mut()
            .unwrap()
            .extend(gap_widths.clone());
        supplemental.extend(gap_widths);
        supplemental.extend(crate::agulhas_reported::widths(&self.bundle));
        supplemental.extend(crate::nwasc_admission::widths(&self.bundle));
        supplemental.extend(crate::hansen_asar_widths::widths(&self.bundle));
        supplemental.extend(crate::neuc_glider_widths::widths(&self.bundle));
        supplemental.extend(crate::aleutian_onishi_width::widths(&self.bundle));
        // Retain the study-summary range outside monthly phase derivation.
        supplemental.extend(crate::madagascar_dimensions::widths(&self.bundle));
        supplemental.extend(crate::azcc_onken_width::widths(&self.bundle));
        supplemental.extend(crate::pacific_nec_nominal_width::widths(&self.bundle));
        supplemental.extend(crate::dimoune_section_widths::validated_widths(&self.bundle)?);
        supplemental.extend(crate::atlantic_nec_band_spans::validated_widths(&self.bundle)?);
        supplemental.extend(crate::pacific_sec_jet_widths::validated_widths(&self.bundle)?);
        supplemental.extend(crate::current_core_dimensions::validated_widths(&self.bundle)?);
        let plans = phase_plans(&self.bundle, &docs)?;
        let mut sources = json!({});
        for (key, _, _) in SOURCES {
            sources[key] = self.bundle.manifest["seasons_receipts"][key]["source_json"].clone();
            if !sources[key].is_string() {
                return Err("Missing seasonal source bytes".into());
            }
        }
        let reference_catalogue = if crate::madagascar_coastal_curve::active(&self.bundle) {
            crate::current_gap_admissions::route_catalogue(
                crate::nwasc_reference_route::catalogue(&self.bundle),
                &self.bundle,
            )?
        } else {
            Value::Null
        };
        let reference_catalogue = if reference_catalogue.is_null() {
            reference_catalogue
        } else {
            crate::wicc_winter_reference::catalogue_projection(
                &self.bundle,
                crate::south_java_reference::catalogue_projection(
                &self.bundle,
                crate::pacific_secc_reference::catalogue_projection(
                    &self.bundle,
                    crate::planning::eicc_catalogue_projection(&self.bundle, reference_catalogue)?,
                )?,
                )?,
            )?
        };
        let reference_catalogue = if reference_catalogue.is_null() { reference_catalogue } else {
            crate::atlantic_nsec_reference::catalogue_projection(&self.bundle, crate::equatorial_basin_identities::catalogue_projection(&self.bundle, reference_catalogue)?)?
        };
        let projected = crate::indian_sec_model_grid_lengths::atlas_projection(&self.bundle, crate::equatorial_basin_identities::snapshot_projection(&self.bundle,
            json!({"ok":true,"engine":"rust-osw-query-v1","bundle_sha256":self.metadata()["bundle_sha256"],"sources_json":sources,"phase_plans":plans,"admitted_current_decisions":crate::current_catalogue::decisions(&self.bundle),"supplemental_widths":supplemental,"working_reference_routes":reference_catalogue,"south_australian_context_scene":crate::south_australian_context::scene(&self.bundle),"eac_source_field_scene":crate::eac_source_fields::scene(&self.bundle),"asca_component_span_scene":crate::asca_component_spans::scene(&self.bundle),"kuroshio_filtered_width_scene":crate::kuroshio_filtered_width::scene(&self.bundle),"agulhas_reported_scene":crate::agulhas_reported::scene(&self.bundle),"kuroshio_daily_scene":crate::kuroshio_daily::scene(&self.bundle),"width_source_review_scenes":crate::current_width_source_reviews::scenes(&self.bundle),"research_evidence_scenes":crate::current_research_evidence::scenes(&self.bundle),"published_transport_scenes":crate::published_transports::by_current(&self.bundle),"published_speed_scenes":crate::characteristic_velocities::by_current(&self.bundle),"mean_core_section_scenes":crate::mean_core_sections::by_current(&self.bundle),"current_dimension_evidence_scenes":crate::current_core_dimensions::by_current(&self.bundle),"satellite_core_width_scenes":crate::satellite_core_widths::by_current(&self.bundle),"review_cited_width_scenes":crate::wicc_review_width::by_current(&self.bundle),"cited_width_constraint_scenes":crate::eacc_cited_width::by_current(&self.bundle),"azores_2009_section_scene":crate::azores_section_review::full(&self.bundle),"pacific_neuc_breadth_scene":crate::pacific_neuc_breadths::full(self.bundle.collections.get("widths").map(Vec::as_slice).unwrap_or(&[])),"dwbc_float_composite_scene":crate::dwbc_float_composite::full(self.bundle.collections.get("widths").map(Vec::as_slice).unwrap_or(&[])),"coastal_composite_width_scene":crate::coastal_composite_widths::full(self.bundle.collections.get("widths").map(Vec::as_slice).unwrap_or(&[]))}),
        ))?;
        crate::pacific_nec_product_axes::atlas_projection(&self.bundle, projected)
    }
}

#[cfg(test)]
mod eacc_phase_integration_tests {
    use super::*;
    #[test]
    fn dynamically_admitted_eacc_gets_one_constraint_after_legacy_plan() {
        let bundle = Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest: json!({"published_eacc_cited_width_constraint_v1": {}}),
            collections: std::collections::BTreeMap::new(),
        };
        // current_measurements dynamically supplies this decision even though
        // it is absent from the frozen width inventory's current index.
        let docs = json!({"widths":{"measurements":[],"current_decisions":[{"current_id":"east-african-coastal"}]},"frames":{"frames":[]},"directions":{}});
        let prior = plans(&docs).unwrap();
        let actual = phase_plans(&bundle, &docs).unwrap();
        let expected =
            crate::eacc_cited_width::extend_phase_plan(&prior["east-african-coastal"]).unwrap();
        assert_eq!(actual["east-african-coastal"], expected);
        assert_eq!(
            actual["east-african-coastal"]["phases"]
                .as_array()
                .unwrap()
                .len(),
            1
        );
        assert_eq!(
            actual["east-african-coastal"]["eligible_indices"],
            json!([])
        );
        assert_eq!(actual["east-african-coastal"]["can_play"], false);
        // Preserve the duplicate refusal; never make the append idempotent.
        let mut duplicate = docs.clone();
        duplicate["widths"]["measurements"] = json!([crate::eacc_cited_width::expected()]);
        assert!(phase_plans(&bundle, &duplicate).is_err());
    }
}
