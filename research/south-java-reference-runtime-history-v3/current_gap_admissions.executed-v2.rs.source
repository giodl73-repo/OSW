//! Exact delivery contracts for the Indian identities and scoped source batch.
//! These guards admit source descriptions, never inferred physical envelopes.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::BTreeSet;

const IDENTITY: (&str, &str) = (
    "research/indian-current-identity-query-contract-v1.json",
    include_str!("../../../research/indian-current-identity-query-contract-v1.json"),
);
const CONTEXT: (&str, &str) = (
    "research/indian-current-evidence-query-contract-v1.json",
    include_str!("../../../research/indian-current-evidence-query-contract-v1.json"),
);
const BRAZIL: (&str, &str) = (
    "research/brazil-regional-reach-query-contract-v1.json",
    include_str!("../../../research/brazil-regional-reach-query-contract-v1.json"),
);
const WIDTH: (&str, &str) = (
    "research/eicc-t24-published-width-admission-v1.json",
    include_str!("../../../research/eicc-t24-published-width-admission-v1.json"),
);
const PLANNING: (&str, &str) = (
    "research/indian-current-reference-route-planning-v1.json",
    include_str!("../../../research/indian-current-reference-route-planning-v1.json"),
);
const CONTRACTS: [(&str, &str); 5] = [IDENTITY, CONTEXT, BRAZIL, WIDTH, PLANNING];
const VERSION: &str = "indian-coastal-brazil-t24-v1";
fn doc(raw: &str) -> Value {
    serde_json::from_str(raw).expect("compiled delivery contract")
}
fn pin(raw: &str) -> String {
    format!("{:x}", Sha256::digest(raw.as_bytes()))
}
pub fn active_manifest(manifest: &Value) -> bool {
    manifest["current_gap_admission_version"] == VERSION
        || CONTRACTS
            .iter()
            .any(|(path, _)| manifest["input_sha256"][path].is_string())
}
pub fn active(bundle: &Bundle) -> bool {
    active_manifest(&bundle.manifest)
        || bundle
            .collections
            .get("entities")
            .into_iter()
            .flatten()
            .any(|row| {
                entities_from_contract()
                    .iter()
                    .any(|entity| entity["id"] == row["id"])
            })
}
fn entities_from_contract() -> Vec<Value> {
    doc(IDENTITY.1)["additions"]["entities"]
        .as_array()
        .unwrap()
        .clone()
}
pub fn entities(bundle: &Bundle) -> Vec<Value> {
    if active(bundle) {
        entities_from_contract()
    } else {
        vec![]
    }
}
pub fn atlas_sources(bundle: &Bundle) -> Vec<(&'static str, &'static str)> {
    if active(bundle) {
        CONTRACTS.to_vec()
    } else {
        vec![]
    }
}
pub fn widths(bundle: &Bundle) -> Vec<Value> {
    let mut widths = if active(bundle) {
        vec![doc(WIDTH.1)["width_record"].clone()]
    } else {
        vec![]
    };
    // Later source admissions remain independently gated while sharing the
    // complete-width-table checks and seasonal snapshot projection.
    widths.extend(crate::davidson_reported_width::widths(bundle));
    widths
}
pub fn verified_length_assessments(bundle: &Bundle) -> Result<Vec<Value>, String> {
    if !active(bundle) {
        return Ok(vec![]);
    }
    validate(bundle)?;
    Ok(doc(IDENTITY.1)["additions"]["length_assessments"]
        .as_array()
        .unwrap()
        .clone())
}
pub fn planning_source(current: &str, manifest: &Value) -> Option<(Value, &'static str)> {
    if !active_manifest(manifest) {
        return None;
    }
    doc(PLANNING.1)["entries"]
        .as_array()
        .unwrap()
        .iter()
        .find(|row| row["current_id"] == current)
        .map(|row| (row.clone(), PLANNING.0))
}

pub(crate) fn original_planning_decision(current: &str, manifest: &Value) -> Result<Value, String> {
    if manifest["current_gap_admission_version"] != VERSION
        || manifest["input_sha256"][IDENTITY.0] != pin(IDENTITY.1)
        || manifest["input_sha256"][PLANNING.0] != pin(PLANNING.1)
    {
        return Err("Original current-gap planning receipts differ".into());
    }
    let identity = doc(IDENTITY.1);
    let record = identity["additions"]["route_decisions"].as_array().unwrap().iter()
        .find(|row| row["current_id"] == current).cloned().ok_or("Missing original admitted planning decision")?;
    let plan = planning_source(current, manifest).ok_or("Missing original admitted planning source")?;
    if record["source_decision"] != plan.0 || record["source_catalog_file"] != plan.1
        || record["source_catalog_sha256"] != pin(PLANNING.1)
    {
        return Err("Original admitted planning projection differs".into());
    }
    Ok(record)
}

pub fn route_catalogue(mut catalogue: Value, bundle: &Bundle) -> Result<Value, String> {
    if !active(bundle) {
        return Ok(catalogue);
    }
    validate(bundle)?;
    let identities = entities_from_contract();
    let plans = doc(PLANNING.1)["entries"].as_array().unwrap().clone();
    let ids: BTreeSet<_> = identities
        .iter()
        .map(|r| r["id"].as_str().unwrap().to_owned())
        .collect();
    let planned_ids: BTreeSet<_> = plans
        .iter()
        .map(|r| format!("current:{}", r["current_id"].as_str().unwrap()))
        .collect();
    if plans.is_empty()
        || ids.len() != plans.len()
        || ids != planned_ids
        || plans.iter().any(|r| {
            !r["geometry"].is_null()
                || !r["candidate_ids"]
                    .as_array()
                    .is_some_and(|rows| rows.is_empty())
                || r["rank_eligible"] != false
                || r["route_strategy_id"] != "source_axis_definition_required"
        })
    {
        return Err("Changed identity-only current route-planning scope".into());
    }
    let previous_counts = catalogue["counts"].clone();
    let total_decisions = {
        let decisions = catalogue["remaining_current_decisions"]
            .as_array_mut()
            .ok_or("Missing route worklist")?;
        if plans.iter().any(|plan| {
            decisions
                .iter()
                .any(|row| row["current_id"] == plan["current_id"])
        }) {
            return Err("Duplicate admitted-current route plan".into());
        }
        decisions.extend(plans.clone());
        decisions.len()
    };
    let strategies = catalogue["planning_taxonomy"]["strategies"]
        .as_array_mut()
        .ok_or("Missing route strategies")?;
    if strategies
        .iter()
        .any(|row| row["id"] == "source_axis_definition_required")
    {
        return Err("Duplicate source-axis planning strategy".into());
    }
    strategies.push(json!({
        "id":"source_axis_definition_required", "label":plans[0]["route_strategy_label"],
        "description":plans[0]["planning_basis"], "current_count":plans.len(), "unbuilt_count":plans.len()
    }));
    for key in [
        "accepted_current_names",
        "currents_without_any_reference_card",
        "currents_without_route_candidates",
        "currents_without_published_ranked_estimate",
    ] {
        let previous = previous_counts[key]
            .as_u64()
            .ok_or("Invalid historical route count")?;
        catalogue["counts"][key] = json!(previous + plans.len() as u64);
    }
    catalogue["counts"]["route_decision_records"] = json!(total_decisions);
    catalogue["effective_accepted_current_count"] =
        catalogue["counts"]["accepted_current_names"].clone();
    catalogue["planning_extension_version"] = json!(VERSION);
    Ok(catalogue)
}
pub fn decision(bundle: &Bundle, admission: &Value) -> Option<Value> {
    if !active(bundle) {
        return None;
    }
    let entity = entities_from_contract()
        .into_iter()
        .find(|row| row["id"] == admission["entity_id"])?;
    let measured = entity["id"] == "current:east-india-coastal";
    Some(
        json!({"current_id":admission["proposal_id"],"name":entity["label"],
        "measurement_ids":if measured { json!([doc(WIDTH.1)["width_record"]["id"]]) } else { json!([]) },
        "status":if measured { "scoped_published_width_admitted" } else { "identity_admitted_width_not_admitted" },
        "whole_current_width_km":null,"annual_width_range_km":null,"admission_id":admission["id"]}),
    )
}
fn expected_records() -> Vec<(String, Value)> {
    let mut records = vec![];
    for raw in [IDENTITY.1, CONTEXT.1] {
        for (name, rows) in doc(raw)["additions"].as_object().unwrap() {
            if name != "objects" {
                records.extend(
                    rows.as_array()
                        .unwrap()
                        .iter()
                        .map(|row| (name.clone(), row.clone())),
                );
            }
        }
    }
    let width = doc(WIDTH.1);
    for (name, row) in &mut records {
        if name == "current_reported_width_evidence"
            && row["id"] == width["width_record"]["source_statement_id"]
        {
            row["source_stage_canonical_width_admitted"] = row["canonical_width_admitted"].clone();
            row["canonical_width_admitted"] = json!(true);
            row["width_id"] = width["width_record"]["id"].clone();
            row["width_admission_id"] = width["admission"]["id"].clone();
        }
    }
    let brazil = doc(BRAZIL.1);
    for (name, key) in [
        ("current_regional_reaches", "record"),
        ("claims", "claim"),
        ("sources", "source_record"),
        ("sources", "method_source"),
    ] {
        records.push((name.into(), brazil[key].clone()));
    }
    for (name, key) in [
        ("widths", "width_record"),
        ("claims", "claim"),
        ("current_measurement_admissions", "admission"),
    ] {
        records.push((name.into(), width[key].clone()));
    }
    records
}
pub fn validate(bundle: &Bundle) -> Result<(), String> {
    if !active(bundle) {
        return Ok(());
    }
    if bundle.manifest["current_gap_admission_version"] != VERSION {
        return Err("Missing current-gap cohort version".into());
    }
    for (path, raw) in CONTRACTS {
        if bundle.manifest["input_sha256"][path] != pin(raw) {
            return Err(format!("Changed current-gap contract: {path}"));
        }
        if let Some(inputs) = doc(raw)["input_sha256"].as_object() {
            for (dependency, digest) in inputs {
                if bundle.manifest["input_sha256"][dependency] != *digest {
                    return Err(format!("Changed current-gap dependency: {dependency}"));
                }
            }
        }
    }
    let eicc_references = crate::planning::eicc_reference_routes(&bundle.collections, &bundle.manifest)?;
    let revised_eicc = !eicc_references.is_empty();
    let revised_south_java = !crate::south_java_reference::routes(&bundle.collections, &bundle.manifest)?.is_empty();
    for (name, expected) in expected_records() {
        let actual: Vec<_> = bundle
            .collections
            .get(&name)
            .into_iter()
            .flatten()
            .filter(|row| row["id"] == expected["id"])
            .collect();
        // Each revised route is fully validated above before its retained prior row is accepted.
        let retained_revision = name == "route_decisions" && actual.len() == 1
            && actual[0]["prior_route_decision"] == expected
            && ((revised_eicc && expected["entity_id"] == "current:east-india-coastal")
                || (revised_south_java && expected["entity_id"] == "current:south-java"));
        if actual != vec![&expected] && !retained_revision {
            return Err(format!(
                "Changed current-gap {name} record: {}",
                expected["id"]
            ));
        }
    }
    let width = doc(WIDTH.1);
    for entity in entities_from_contract() {
        let owners: Vec<_> = bundle
            .collections
            .get("objects")
            .into_iter()
            .flatten()
            .filter(|row| row["id"] == entity["id"])
            .collect();
        if owners.len() != 1 {
            return Err("Missing current-gap owner".into());
        }
        let owner = owners[0];
        let identity_contract = doc(IDENTITY.1);
        let identity_owner = identity_contract["additions"]["objects"]
            .as_array()
            .unwrap()
            .iter()
            .find(|row| row["id"] == entity["id"])
            .unwrap();
        if owner["search_aliases"] != identity_owner["search_aliases"] {
            return Err("Changed admitted current search aliases".into());
        }
        let measured = entity["id"] == width["width_record"]["entity_id"];
        let expected_widths = if measured {
            json!([width["width_record"]["id"]])
        } else {
            json!([])
        };
        if owner["width_ids"] != expected_widths
            || owner["capabilities"]["scoped_width"] != json!(usize::from(measured))
            || owner["capabilities"]["width_samples"] != 0
            || owner["capabilities"]["reported_length"] != 0
            || owner["capabilities"]["time_samples"] != 0
            || owner["measurement_ids"] != json!([])
            || owner["width_sample_ids"] != json!([])
            || owner["state_codes"] != json!([])
            || owner["state_evidence"] != json!([])
            || (!((revised_eicc && entity["id"] == "current:east-india-coastal")
                    || (revised_south_java && entity["id"] == "current:south-java"))
                && (owner["route_ids"] != json!([]) || owner["map_features"] != json!([])))
            || !owner["published_length_km"].is_null()
            || !owner["latest_observation_date"].is_null()
        {
            return Err("Current-gap owner promoted unadmitted physical coverage".into());
        }
        for (collection, field, capability) in [
            (
                "current_direction_calendars",
                "direction_calendar_ids",
                "direction_calendars",
            ),
            (
                "current_direction_descriptions",
                "direction_description_ids",
                "direction_descriptions",
            ),
            (
                "current_reported_width_evidence",
                "reported_width_evidence_ids",
                "reported_width_evidence",
            ),
            (
                "current_cross_shore_context",
                "cross_shore_context_ids",
                "cross_shore_context",
            ),
            (
                "current_regime_context",
                "regime_context_ids",
                "regime_context",
            ),
        ] {
            let refs: Vec<_> = bundle
                .collections
                .get(collection)
                .into_iter()
                .flatten()
                .filter(|row| row["entity_id"] == entity["id"])
                .map(|row| row["id"].clone())
                .collect();
            // Owners without any context in this collection may omit the field.
            if (!refs.is_empty() || !owner[field].is_null()) && owner[field] != json!(refs)
                || owner["capabilities"][capability].as_u64().unwrap_or(0) != refs.len() as u64
            {
                return Err(format!("Changed current-gap context ownership: {field}"));
            }
        }
    }
    let registry: std::collections::BTreeSet<_> = bundle
        .collections
        .get("sources")
        .into_iter()
        .flatten()
        .filter_map(|row| row["id"].as_str())
        .collect();
    for owner in bundle.collections.get("objects").into_iter().flatten() {
        let refs = owner["source_ids"]
            .as_array()
            .ok_or("Missing current-gap owner provenance")?;
        let unique: std::collections::BTreeSet<_> = refs.iter().filter_map(Value::as_str).collect();
        if unique.len() != refs.len()
            || unique.iter().any(|id| !registry.contains(id))
            || owner["linked_source_count"].as_u64() != Some(refs.len() as u64)
        {
            return Err("Invalid current-gap owner provenance projection".into());
        }
    }
    Ok(())
}

#[cfg(test)]
pub(crate) mod tests {
    use super::*;
    pub(crate) fn fixture() -> Bundle {
        let mut manifest = json!({"current_gap_admission_version":VERSION,"input_sha256":{}});
        for (path, raw) in CONTRACTS {
            manifest["input_sha256"][path] = json!(pin(raw));
            if let Some(inputs) = doc(raw)["input_sha256"].as_object() {
                for (key, value) in inputs {
                    manifest["input_sha256"][key] = value.clone();
                }
            }
        }
        let mut collections = std::collections::BTreeMap::<String, Vec<Value>>::new();
        for (name, row) in expected_records() {
            collections.entry(name).or_default().push(row);
        }
        let mut objects = doc(IDENTITY.1)["additions"]["objects"]
            .as_array()
            .unwrap()
            .clone();
        for owner in &mut objects {
            let mut refs = std::collections::BTreeSet::new();
            for rows in collections.values() {
                for row in rows.iter().filter(|row| row["entity_id"] == owner["id"]) {
                    for field in ["source_id", "method_source_id"] {
                        if let Some(id) = row[field].as_str() {
                            refs.insert(id.to_owned());
                        }
                    }
                    for id in row["source_ids"]
                        .as_array()
                        .into_iter()
                        .flatten()
                        .filter_map(Value::as_str)
                    {
                        refs.insert(id.to_owned());
                    }
                }
            }
            owner["source_ids"] = json!(refs);
            owner["linked_source_count"] = json!(refs.len());
            for (collection, field, capability) in [
                (
                    "current_direction_calendars",
                    "direction_calendar_ids",
                    "direction_calendars",
                ),
                (
                    "current_direction_descriptions",
                    "direction_description_ids",
                    "direction_descriptions",
                ),
                (
                    "current_reported_width_evidence",
                    "reported_width_evidence_ids",
                    "reported_width_evidence",
                ),
                (
                    "current_cross_shore_context",
                    "cross_shore_context_ids",
                    "cross_shore_context",
                ),
                (
                    "current_regime_context",
                    "regime_context_ids",
                    "regime_context",
                ),
            ] {
                let refs: Vec<_> = collections
                    .get(collection)
                    .unwrap()
                    .iter()
                    .filter(|row| row["entity_id"] == owner["id"])
                    .map(|row| row["id"].clone())
                    .collect();
                owner[field] = json!(refs);
                owner["capabilities"][capability] = json!(refs.len());
            }
            if owner["id"] == "current:east-india-coastal" {
                owner["width_ids"] = json!([doc(WIDTH.1)["width_record"]["id"]]);
                owner["capabilities"]["scoped_width"] = json!(1);
            }
        }
        collections.insert("objects".into(), objects);
        Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest,
            collections,
        }
    }
    #[test]
    fn reviewed_south_java_reference_composes_with_existing_cohort_without_physical_promotion() {
        let selected: Bundle = serde_json::from_str(include_str!("../../../research/south-java-reference-runtime-fixture-v1.json")).unwrap();
        let mut b = fixture();
        for (key, value) in selected.manifest["input_sha256"].as_object().unwrap() {
            b.manifest["input_sha256"][key] = value.clone();
        }
        b.manifest["south_java_reference_delivery_v1"] = selected.manifest["south_java_reference_delivery_v1"].clone();
        for name in ["objects", "route_decisions"] {
            let rows = b.collections.get_mut(name).unwrap();
            let changed = selected.collections[name].iter().find(|row|
                row["id"] == "current:south-java" || row["entity_id"] == "current:south-java").unwrap();
            let row = rows.iter_mut().find(|row| row["id"] == changed["id"]).unwrap();
            *row = changed.clone();
        }
        b.collections.insert("reference_routes".into(), selected.collections["reference_routes"].clone());
        let sources = b.collections.get_mut("sources").unwrap();
        for row in &selected.collections["sources"] {
            if row["id"].as_str().unwrap().starts_with("fixture:") { continue; }
            if let Some(prior) = sources.iter().find(|prior| prior["id"] == row["id"]) {
                assert_eq!(prior, row);
            } else { sources.push(row.clone()); }
        }
        while sources.len() < 211 {
            sources.push(json!({"id":format!("fixture:cohort-source:{}", sources.len())}));
        }
        assert_eq!(sources.len(), 211);
        validate(&b).unwrap();
        for mode in ["physical", "prior", "receipt", "other"] {
            let mut bad = Bundle { schema: b.schema.clone(), manifest: b.manifest.clone(), collections: b.collections.clone() };
            match mode {
                "physical" => bad.collections.get_mut("objects").unwrap().iter_mut()
                    .find(|r| r["id"] == "current:south-java").unwrap()["published_length_km"] = json!(1100),
                "prior" => bad.collections.get_mut("route_decisions").unwrap().iter_mut()
                    .find(|r| r["entity_id"] == "current:south-java").unwrap()["prior_route_decision"]["candidate_count"] = json!(1),
                "receipt" => { bad.manifest.as_object_mut().unwrap().remove("south_java_reference_delivery_v1"); },
                "other" => bad.collections.get_mut("route_decisions").unwrap().iter_mut()
                    .find(|r| r["entity_id"] != "current:south-java").unwrap()["candidate_count"] = json!(1),
                _ => unreachable!(),
            }
            assert!(validate(&bad).is_err(), "{mode}");
        }
    }
    #[test]
    fn exact_cohort_retains_scoped_source_semantics() {
        assert!(validate(&fixture()).is_ok());
        let mut b = fixture();
        b.collections.get_mut("widths").unwrap()[0]["annual_width_range_km"] = json!([100, 250]);
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections
            .get_mut("current_cross_shore_context")
            .unwrap()[0]["canonical_width_admitted"] = json!(true);
        assert!(validate(&b).is_err());
    }
    #[test]
    fn rejects_missing_receipt_rows_and_wrong_owner() {
        let mut b = fixture();
        b.manifest["input_sha256"][WIDTH.0] = json!("changed");
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections.get_mut("objects").unwrap()[0]["search_aliases"] =
            json!(["Unrelated Current"]);
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections
            .get_mut("current_direction_descriptions")
            .unwrap()
            .pop();
        assert!(validate(&b).is_err());
        let mut b = fixture();
        b.collections.get_mut("objects").unwrap()[0]["width_ids"] =
            json!([doc(WIDTH.1)["width_record"]["id"]]);
        assert!(validate(&b).is_err());
    }
    #[test]
    fn identity_decisions_do_not_borrow_another_currents_width() {
        let b = fixture();
        for admission in &b.collections["current_identity_admissions"] {
            let row = decision(&b, admission).unwrap();
            assert_eq!(
                row["measurement_ids"].as_array().unwrap().len(),
                usize::from(admission["entity_id"] == "current:east-india-coastal")
            );
            assert!(row["annual_width_range_km"].is_null());
        }
    }
    #[test]
    fn historical_length_guards_append_only_verified_unranked_identities() {
        let b = fixture();
        let prior = json!([{"id":"old","entity_id":"current:old","published_rank":7}]);
        let expected = crate::length_assessment_overlays::expected(&b, &prior).unwrap();
        assert_eq!(expected.as_array().unwrap().len(), 5);
        assert_eq!(expected[0], prior[0]);
        for row in expected.as_array().unwrap().iter().skip(1) {
            assert_eq!(row["rank_eligible"], false);
            assert!(row["published_rank"].is_null());
            assert!(row["published_length_km"].is_null());
        }
        let collision = json!([verified_length_assessments(&b).unwrap()[0]]);
        assert!(crate::length_assessment_overlays::expected(&b, &collision).is_err());
        let mut bad = fixture();
        bad.collections.get_mut("length_assessments").unwrap()[0]["published_rank"] = json!(1);
        assert!(crate::length_assessment_overlays::expected(&bad, &prior).is_err());
    }
    #[test]
    fn route_coverage_includes_all_four_unlocated_identities_without_new_routes() {
        let mut b = fixture();
        b.manifest["nwasc_reference_route_version"] = json!("1");
        let previous = crate::nwasc_reference_route::catalogue(&b);
        let actual = route_catalogue(previous.clone(), &b).unwrap();
        assert_eq!(actual["candidates"], previous["candidates"]);
        assert_eq!(actual["counts"]["route_candidates"], 78);
        assert_eq!(actual["counts"]["currents_with_route_candidates"], 72);
        assert_eq!(actual["counts"]["accepted_current_names"], 106);
        assert_eq!(actual["counts"]["currents_without_any_reference_card"], 34);
        assert_eq!(actual["counts"]["currents_without_route_candidates"], 23);
        assert_eq!(
            actual["counts"]["currents_without_published_ranked_estimate"],
            93
        );
        assert_eq!(actual["counts"]["route_decision_records"], 95);
        let old = previous["remaining_current_decisions"].as_array().unwrap();
        let rows = actual["remaining_current_decisions"].as_array().unwrap();
        assert_eq!(&rows[..old.len()], old.as_slice());
        assert_eq!(
            rows[old.len()..],
            doc(PLANNING.1)["entries"].as_array().unwrap()[..]
        );
        assert!(route_catalogue(actual, &b).is_err());
    }
    #[test]
    fn route_coverage_preserves_legacy_catalogue_and_rejects_unverified_cohort() {
        let mut b = fixture();
        let previous = crate::madagascar_coastal_curve::catalogue();
        b.manifest["input_sha256"][PLANNING.0] = json!("changed");
        assert!(route_catalogue(previous.clone(), &b).is_err());
        let old = Bundle {
            schema: "osw.query-bundle.v1".into(),
            manifest: json!({}),
            collections: std::collections::BTreeMap::new(),
        };
        assert_eq!(route_catalogue(previous.clone(), &old).unwrap(), previous);
    }
}
