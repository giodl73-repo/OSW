//! Basin qualifications establish identities without inheriting family measurements.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::BTreeSet;
use std::sync::OnceLock;

pub(crate) const FILE: &str = "research/equatorial-basin-identity-query-contract-v3.json";
pub(crate) const RAW: &str = include_str!("../../../research/equatorial-basin-identity-query-contract-v3.json");
pub(crate) const PLANNING: &str = "research/equatorial-basin-reference-route-planning-v1.json";
const PLANNING_RAW: &str = include_str!("../../../research/equatorial-basin-reference-route-planning-v1.json");
const KEY: &str = "equatorial_basin_identities_v3";
const MEMBERSHIPS: &str = "current_basin_memberships";

fn pin(raw: &str) -> String { format!("{:x}", Sha256::digest(raw.as_bytes())) }
fn document() -> &'static Value {
    static DOC: OnceLock<Value> = OnceLock::new();
    DOC.get_or_init(|| serde_json::from_str(RAW).expect("compiled basin identity contract"))
}
fn rows<'a>(bundle: &'a Bundle, collection: &str) -> &'a [Value] {
    bundle.collections.get(collection).map(Vec::as_slice).unwrap_or(&[])
}
fn member_ids() -> Vec<&'static str> {
    document()["expected_entity_ids"].as_array().unwrap().iter().map(|r| r.as_str().unwrap()).collect()
}
fn owns(row: &Value) -> bool {
    member_ids().iter().any(|id| {
        ["id", "entity_id", "subject_id", "object_id", "child_id", "parent_id"].iter().any(|field| row[*field] == *id)
            || row["current_id"] == id.strip_prefix("current:").unwrap()
    })
}
fn normalized(value: &Value) -> String {
    value.as_str().unwrap_or("").chars().filter(char::is_ascii_alphanumeric).flat_map(char::to_lowercase).collect()
}
fn marker() -> Value {
    json!({"contract_file":FILE,"contract_sha256":pin(RAW),"parent_logical_sha256":document()["parent_logical_sha256"],
        "new_identity_ids":document()["expected_entity_ids"],"accepted_current_identities":111,
        "new_measurements":0,"new_publication_sources":0,"physical_geometry_added":false})
}
pub(crate) fn active(bundle: &Bundle) -> bool {
    !bundle.manifest[KEY].is_null() || !bundle.manifest["input_sha256"][FILE].is_null()
        || bundle.collections.contains_key(MEMBERSHIPS)
        || bundle.collections.values().flatten().any(owns)
        || rows(bundle, "names").iter().any(|row| {
            document()["additions"]["entities"].as_array().unwrap().iter().any(|r| normalized(&r["label"]) == normalized(&row["label"]))
        })
}
fn checked(bundle: &Bundle) -> Result<bool, String> {
    let fail = || "Invalid basin-qualified current identity extension".to_owned();
    if !active(bundle) { return Ok(false); }
    let product_overlay = crate::pacific_nec_product_axes::identity_overlay(bundle)?;
    let jet_overlay = crate::pacific_sec_jet_widths::identity_overlay(bundle)?;
    let characteristic_overlay = crate::characteristic_velocities::identity_overlay(bundle)?;
    let band_overlay = crate::atlantic_nec_band_spans::identity_overlay(bundle)?;
    let dimoune_overlay = crate::dimoune_section_widths::identity_overlay(bundle)?;
    let model_overlay = crate::indian_sec_model_grid_lengths::identity_overlay(bundle)?;
    let overlay = crate::pacific_nec_nominal_width::identity_overlay(bundle)?;
    let doc = document();
    if bundle.manifest[KEY] != marker() || bundle.manifest["input_sha256"][FILE] != pin(RAW) { return Err(fail()); }
    for (path, digest) in doc["input_sha256"].as_object().ok_or_else(fail)? {
        if bundle.manifest["input_sha256"][path] != *digest { return Err(fail()); }
    }
    if bundle.manifest["input_sha256"][PLANNING] != pin(PLANNING_RAW) { return Err(fail()); }
    for key in ["node_count", "link_count"] {
        if bundle.manifest["taxonomy"][key] != doc["taxonomy_counts"]["after"][key] { return Err(fail()); }
    }
    let additions = doc["additions"].as_object().ok_or_else(fail)?;
    for (name, expected) in additions {
        let expected = expected.as_array().ok_or_else(fail)?;
        if rows(bundle, name).iter().filter_map(|r| crate::pacific_sec_jet_widths::identity_parent_row(name,r,jet_overlay)).filter_map(|r| crate::characteristic_velocities::identity_parent_row(name,r,characteristic_overlay)).filter_map(|r| crate::atlantic_nec_band_spans::identity_parent_row(name,r,band_overlay)).filter_map(|r| crate::dimoune_section_widths::identity_parent_row(name,r,dimoune_overlay)).filter_map(|r| crate::pacific_nec_product_axes::identity_parent_row(name,r,product_overlay)).filter_map(|r| crate::indian_sec_model_grid_lengths::identity_parent_row(name,r,model_overlay)).filter_map(|r| crate::pacific_nec_nominal_width::identity_parent_row(name,r,overlay)).filter(|r| owns(r)).collect::<Vec<_>>() != expected.iter().collect::<Vec<_>>() { return Err(fail()); }
    }
    if rows(bundle, MEMBERSHIPS) != doc["additions"][MEMBERSHIPS].as_array().ok_or_else(fail)?.as_slice() { return Err(fail()); }
    for (name, records) in &bundle.collections {
        if !additions.contains_key(name) && name != "working_records" && records.iter().filter_map(|r| crate::pacific_sec_jet_widths::identity_parent_row(name,r,jet_overlay)).filter_map(|r| crate::characteristic_velocities::identity_parent_row(name,r,characteristic_overlay)).filter_map(|r| crate::atlantic_nec_band_spans::identity_parent_row(name,r,band_overlay)).filter_map(|r| crate::dimoune_section_widths::identity_parent_row(name,r,dimoune_overlay)).filter_map(|r| crate::pacific_nec_product_axes::identity_parent_row(name,r,product_overlay)).filter_map(|r| crate::indian_sec_model_grid_lengths::identity_parent_row(name,r,model_overlay)).filter_map(|r| crate::pacific_nec_nominal_width::identity_parent_row(name,r,overlay)).any(owns) { return Err(fail()); }
    }
    for expected in doc["additions"]["entities"].as_array().ok_or_else(fail)? {
        for name in ["entities", "objects", "names"] {
            for actual in rows(bundle, name) {
                if normalized(&actual["label"]) == normalized(&expected["label"])
                    && (if name == "names" { &actual["entity_id"] } else { &actual["id"] }) != &expected["id"] {
                    return Err(fail());
                }
            }
        }
    }
    for (owner, prior) in doc["prior_family_records"].as_object().ok_or_else(fail)? {
        for name in ["entities", "objects"] {
            if rows(bundle, name).iter().filter(|r| r["id"] == *owner).collect::<Vec<_>>()
                != prior[name].as_array().ok_or_else(fail)?.iter().collect::<Vec<_>>() { return Err(fail()); }
        }
        if rows(bundle, "names").iter().filter(|r| r["entity_id"] == *owner).collect::<Vec<_>>()
            != prior["names"].as_array().ok_or_else(fail)?.iter().collect::<Vec<_>>() { return Err(fail()); }
        let short = owner.strip_prefix("current:").ok_or_else(fail)?;
        if rows(bundle, "widths").iter().any(|r| r["current_id"] == short) { return Err(fail()); }
    }
    for source in doc["prior_glossary_sources"].as_array().ok_or_else(fail)? {
        if rows(bundle, "sources").iter().filter(|r| r["id"] == source["id"]).collect::<Vec<_>>() != vec![source] { return Err(fail()); }
    }
    Ok(true)
}
pub(crate) fn taxonomy_links(manifest: &Value) -> Result<Vec<Value>, String> {
    if manifest[KEY].is_null() { return Ok(vec![]); }
    if manifest[KEY] != marker() || manifest["input_sha256"][FILE] != pin(RAW) {
        return Err("Invalid basin taxonomy extension receipt".into());
    }
    for key in ["node_count", "link_count"] {
        if manifest["taxonomy"][key] != document()["taxonomy_counts"]["after"][key] {
            return Err("Invalid basin taxonomy extension counts".into());
        }
    }
    Ok(document()["additions"]["taxonomy_links"].as_array().unwrap().clone())
}
pub(crate) fn validate(bundle: &Bundle) -> Result<(), String> { checked(bundle).map(|_| ()) }
pub(crate) fn verified_length_assessments(bundle: &Bundle) -> Result<Vec<Value>, String> {
    if !checked(bundle)? { return Ok(vec![]); }
    Ok(document()["additions"]["length_assessments"].as_array().unwrap().clone())
}
pub(crate) fn entities(bundle: &Bundle) -> Vec<Value> {
    if active(bundle) { document()["additions"]["entities"].as_array().unwrap().clone() } else { vec![] }
}
pub(crate) fn planning_source(current: &str, manifest: &Value) -> Option<(Value, &'static str)> {
    if manifest[KEY].is_null() { return None; }
    document()["additions"]["route_decisions"].as_array().unwrap().iter()
        .find(|r| r["current_id"] == current).map(|r| (r["source_decision"].clone(), PLANNING))
}
pub(crate) fn dashboard_document(bundle: &Bundle, mut doc: Value) -> Result<Value, String> {
    if !checked(bundle)? { return Ok(doc); }
    let old = doc["entries"].as_array().ok_or("Missing preceding dashboard entries")?;
    if old.len() != 246 || doc["counts"]["named_current"] != 106 || old.iter().any(owns) {
        return Err("Changed preceding basin identity dashboard inventory".into());
    }
    let mut updated = old.clone();
    updated.extend(document()["additions"]["objects"].as_array().unwrap().clone());
    let previous = doc["snapshot_fingerprint"].as_str().ok_or("Missing preceding dashboard fingerprint")?;
    let fingerprint = pin(&format!("osw.equatorial-basin-identities.v3\n{previous}\n{}\n", pin(RAW)));
    let pending = doc["proposed_current_additions"].as_u64().and_then(|v| v.checked_sub(5)).ok_or("Invalid preceding proposal count")?;
    doc["entries"] = json!(updated); doc["counts"]["named_current"] = json!(111);
    doc["proposed_current_additions"] = json!(pending); doc["snapshot_fingerprint"] = json!(fingerprint);
    doc["equatorial_basin_identity_projection_v3"] = json!({"contract_file":FILE,"contract_sha256":pin(RAW),"new_identities":5,"new_measurements":0});
    Ok(doc)
}
pub(crate) fn catalogue_projection(bundle: &Bundle, mut catalogue: Value) -> Result<Value, String> {
    if !checked(bundle)? { return Ok(catalogue); }
    let plans: Vec<Value> = document()["additions"]["route_decisions"].as_array().unwrap().iter().map(|r| r["source_decision"].clone()).collect();
    let decisions = catalogue["remaining_current_decisions"].as_array_mut().ok_or("Missing preceding route worklist")?;
    if plans.iter().any(|p| decisions.iter().any(|r| r["current_id"] == p["current_id"])) { return Err("Duplicate basin route plan".into()); }
    decisions.extend(plans); let count = decisions.len();
    let strategies = catalogue["planning_taxonomy"]["strategies"].as_array_mut().ok_or("Missing preceding route strategies")?;
    let matching: Vec<usize> = strategies.iter().enumerate().filter(|(_,r)| r["id"] == "source_axis_definition_required").map(|(i,_)|i).collect();
    if matching.len() != 1 { return Err("One source-axis strategy required".into()); }
    for key in ["current_count", "unbuilt_count"] {
        let old = strategies[matching[0]][key].as_u64().ok_or("Invalid strategy count")?;
        strategies[matching[0]][key] = json!(old + 5);
    }
    for key in ["accepted_current_names", "currents_without_any_reference_card", "currents_without_route_candidates", "currents_without_published_ranked_estimate"] {
        let old = catalogue["counts"][key].as_u64().ok_or("Invalid preceding route count")?;
        catalogue["counts"][key] = json!(old + 5);
    }
    catalogue["counts"]["route_decision_records"] = json!(count);
    catalogue["effective_accepted_current_count"] = catalogue["counts"]["accepted_current_names"].clone();
    catalogue["equatorial_basin_identity_projection_v3"] = json!({"contract_file":FILE,"contract_sha256":pin(RAW),"new_route_plans":5,"new_routes":0});
    Ok(catalogue)
}
fn scene(selected: Vec<&Value>, selected_owner: Option<&str>, bundle: &Bundle) -> Value {
    if selected.is_empty() { return Value::Null; }
    let doc = document();
    let members: Vec<_> = selected.into_iter().map(|r| {
        let entity = doc["additions"]["entities"].as_array().unwrap().iter().find(|e| e["id"] == r["entity_id"]).unwrap();
        let family = &doc["prior_family_records"][r["family_entity_id"].as_str().unwrap()]["entities"][0];
        let mut member = json!({"membership_record":r,"entity_id":entity["id"],"label":entity["label"],"object_url":entity["almanac_url"],
            "family_entity_id":family["id"],"family_label":family["label"],
            "family_url":format!("object.html?id=current%3A{}",r["family_entity_id"].as_str().unwrap().strip_prefix("current:").unwrap())});
        let evidence = crate::pacific_nec_nominal_width::member_context(bundle,&entity["id"]);
        if !evidence.is_null() {member["nominal_width_evidence"] = evidence;}
        member
    }).collect();
    let has_width = members.iter().any(|r| !r["nominal_width_evidence"].is_null());
    let dimension_status = if has_width {"Separately sourced nominal regional width evidence is linked for the Pacific NEC. Family and sibling measurements are not inherited; lengths, annual ranges and physical edges remain unresolved."} else {"Lengths, widths, observation dates and annual ranges remain unmeasured by this identity admission."};
    json!({"kind":"equatorial_basin_identity_context","title":"Basin-specific current identities","members":members,
        "selected_entity_id":selected_owner,"source_file":FILE,"source_pointer":"/additions/current_basin_memberships",
        "source_url":"https://www.tidesandcurrents.noaa.gov/glossary.html","figure":"figures/equatorial-basin-identity-members-v1.svg",
        "scope":"These editorial basin qualifications separate measurement targets. Family relationships do not establish physical connections, shared dimensions or observed current geometry.",
        "dimension_status":dimension_status})
}
pub(crate) fn membership_scene(selected: &[&Value], bundle: &Bundle) -> Value {
    if !active(bundle) { return Value::Null; }
    scene(selected.iter().copied().filter(|r| rows(bundle, MEMBERSHIPS).contains(r)).collect(), None, bundle)
}
pub(crate) fn for_owner(bundle: &Bundle, owner: &str) -> Value {
    if !active(bundle) { return Value::Null; }
    let family = rows(bundle, MEMBERSHIPS).iter().find(|r| r["entity_id"] == owner)
        .and_then(|r| r["family_entity_id"].as_str()).unwrap_or(owner);
    scene(rows(bundle, MEMBERSHIPS).iter().filter(|r| r["family_entity_id"] == family).collect(), Some(owner), bundle)
}
pub(crate) fn scenes(bundle: &Bundle) -> Value {
    let mut result = json!({});
    if active(bundle) {
        let mut owners: BTreeSet<String> = member_ids().iter().map(|v| (*v).to_owned()).collect();
        owners.extend(document()["prior_family_records"].as_object().unwrap().keys().cloned());
        for owner in owners { result[&owner] = for_owner(bundle, &owner); }
    }
    result
}
pub(crate) fn snapshot_projection(bundle: &Bundle, mut result: Value) -> Value {
    if active(bundle) {
        result["basin_identity_scenes"] = scenes(bundle);
        result["basin_identity_contract"] = document().clone();
        result["basin_identity_planning"] = serde_json::from_str(PLANNING_RAW).expect("compiled basin route planning");
    }
    result
}
pub(crate) fn object_projection(bundle: &Bundle, owner: &str, mut result: Value) -> Value {
    let scene = for_owner(bundle, owner);
    if !scene.is_null() { result["basin_identity_context_scene"] = scene; }
    result
}

#[cfg(test)]
pub(crate) mod tests {
    use super::*;
    pub(crate) fn fixture() -> Bundle {
        let doc = document();
        let mut b = Bundle { schema:"osw.query-bundle.v1".into(), manifest:json!({"input_sha256":{}}),
            collections:serde_json::from_value(doc["additions"].clone()).unwrap() };
        for prior in doc["prior_family_records"].as_object().unwrap().values() {
            for name in ["entities", "objects", "names"] {
                b.collections.get_mut(name).unwrap().extend(prior[name].as_array().unwrap().clone());
            }
        }
        b.collections.insert("sources".into(), doc["prior_glossary_sources"].as_array().unwrap().clone());
        for (path,digest) in doc["input_sha256"].as_object().unwrap() { b.manifest["input_sha256"][path] = digest.clone(); }
        b.manifest["input_sha256"][FILE] = json!(pin(RAW)); b.manifest[KEY] = marker();
        b.manifest["taxonomy"] = json!({"node_count":251,"link_count":25}); b
    }
    //Synthetic historical nodes and ledger receipts exercise the complete taxonomy validator.
    //This fixture is not a reconstruction of the installed ocean observations.
    fn full_taxonomy_fixture() -> Bundle {
        let mut b = fixture();
        let mut entries = Vec::new();
        let mut historical_links = Vec::new();
        let parent = document()["prior_family_records"]["current:north-equatorial"]["entities"][0].clone();
        for i in 0..244 {
            let short = format!("fixture-taxonomy-{i}");
            let id = format!("current:{short}");
            let label = format!("Historical taxonomy fixture {i}");
            let node = json!({"id":id,"label":label,"type":"named_current","identity_level":"current",
                "setting":"equatorial","time_behavior":"persistent_variable","basin":"Fixture basin"});
            b.collections.get_mut("entities").unwrap().push(node.clone());
            b.collections.get_mut("objects").unwrap().push(node);
            if i < 20 {
                entries.push(json!({"id":short,"part_of_system":"north-equatorial","name_source":"fixture"}));
                historical_links.push(json!({"id":format!("taxonomy-link:{short}"),"child_id":id,"parent_id":parent["id"],
                    "child_label":label,"parent_label":parent["label"],"predicate":"basin_or_subfamily_member_of",
                    "status":"existing_editorial_ledger_assignment_not_new_canonical_relation",
                    "source_file":"research/ocean-current-almanac.json","source_pointer":format!("/entries/{i}/part_of_system"),
                    "evidence_role":"existing_editorial_parent_assignment","naming_source_url":"https://example.invalid/fixture",
                    "naming_source_is_parent_relation_evidence":false,"physical_connectivity_eligible":false,
                    "measurement_inheritance_eligible":false,"scope":crate::taxonomy::SCOPE}));
            }
        }
        historical_links.extend(rows(&b,"taxonomy_links").iter().cloned());
        b.collections.insert("taxonomy_links".into(),historical_links);
        let vocabulary = json!({"axes":{"identity_level":{"current":{},"family":{}}}});
        let ledger = json!({"entries":entries,"sources":{"fixture":"https://example.invalid/fixture"}});
        let mut receipts = Vec::new();
        for (file, value) in [("research/ocean-current-almanac.json",ledger),
                               ("research/ocean-motion-taxonomy.json",vocabulary.clone())] {
            let raw = value.to_string(); let hash = pin(&raw);
            b.manifest["input_sha256"][file] = json!(hash);
            receipts.push(json!({"file":file,"source_json":raw,"sha256":hash}));
        }
        b.manifest["taxonomy"] = json!({"schema":"osw.query-taxonomy.v1","scope":crate::taxonomy::SCOPE,
            "complete_physical_taxonomy":false,"measurement_inheritance_eligible":false,
            "node_count":251,"link_count":25,"source_receipts":receipts,"identity_levels":vocabulary["axes"]["identity_level"]});
        b
    }
    #[test] fn basin_members_participate_in_general_taxonomy_selection_and_context() {
        let b = fixture();
        for (root, relation, count) in [("current:north-equatorial","children",2),
            ("current:south-equatorial","descendants",3),("current:pacific-north-equatorial","ancestors",1)] {
            let selection = crate::taxonomy::Selection { root_id:root.into(),relation:relation.into(),include_root:false };
            assert_eq!(crate::taxonomy::select(&b.collections,&selection).unwrap().len(),count);
        }
        let context = crate::taxonomy::context(&b.collections,"current:indian-south-equatorial");
        assert_eq!(context["parents"],json!([document()["additions"]["taxonomy_links"][4]]));
        assert_eq!(context["measurement_inheritance_eligible"],false);
        assert_eq!(context["physical_completeness"],false);
    }
    #[test] fn complete_taxonomy_validator_accepts_twenty_preserved_and_five_new_links() {
        let b = full_taxonomy_fixture();
        validate(&b).unwrap();
        crate::taxonomy::validate(&b.collections,&b.manifest).unwrap();
        assert_eq!(rows(&b,"objects").len(),251);
        assert_eq!(rows(&b,"taxonomy_links").len(),25);
        let mut bad = full_taxonomy_fixture();
        bad.manifest["taxonomy"]["source_receipts"][0]["source_json"] = json!("{}");
        assert!(crate::taxonomy::validate(&bad.collections,&bad.manifest).is_err());
        let mut bad = full_taxonomy_fixture();
        bad.collections.get_mut("taxonomy_links").unwrap().remove(0);
        assert!(crate::taxonomy::validate(&bad.collections,&bad.manifest).is_err());
    }
    #[test] fn taxonomy_counts_and_coherent_link_promotions_are_rejected() {
        for key in ["node_count","link_count"] {
            let mut b = fixture(); b.manifest["taxonomy"][key] = json!(999);
            assert!(validate(&b).is_err()); assert!(taxonomy_links(&b.manifest).is_err());
        }
        for key in ["physical_connectivity_eligible","measurement_inheritance_eligible"] {
            let mut b = fixture(); b.collections.get_mut("taxonomy_links").unwrap()[0][key] = json!(true);
            assert!(validate(&b).is_err());
            assert!(crate::taxonomy::validate(&b.collections,&b.manifest).is_err());
        }
    }
    #[test] fn shared_length_table_appends_only_five_unmeasured_assessments_and_preserves_ranks() {
        let b = fixture();
        let previous = json!([{"id":"length_assessment:fixture","entity_id":"current:fixture",
            "published_length_km":1234,"published_rank":4,"rank_eligible":true,"source":"synthetic test sentinel"}]);
        let actual = crate::length_assessment_overlays::expected(&b,&previous).unwrap();
        assert_eq!(actual[0],previous[0]);
        assert_eq!(&actual.as_array().unwrap()[1..],document()["additions"]["length_assessments"].as_array().unwrap().as_slice());
        assert_eq!(actual.as_array().unwrap().len(),6);
        for row in actual.as_array().unwrap().iter().skip(1) {
            assert!(row["published_length_km"].is_null()); assert!(row["published_rank"].is_null());
            assert_eq!(row["rank_eligible"],false);
        }
    }
    #[test] fn shared_length_table_rejects_duplicate_owners_or_promoted_basin_ranks() {
        let b = fixture();
        let duplicate = json!([document()["additions"]["length_assessments"][0]]);
        assert!(crate::length_assessment_overlays::expected(&b,&duplicate).is_err());
        for key in ["published_rank","published_length_km"] {
            let mut bad = fixture(); bad.collections.get_mut("length_assessments").unwrap()[0][key] = json!(1);
            assert!(crate::length_assessment_overlays::expected(&bad,&json!([])).is_err());
        }
    }
    #[test] fn shared_length_table_preserves_legacy_and_refuses_partial_basin_receipt() {
        let b = Bundle { schema:"osw.query-bundle.v1".into(),manifest:json!({}),collections:Default::default() };
        let previous = json!([{"id":"old","published_rank":7}]);
        assert_eq!(crate::length_assessment_overlays::expected(&b,&previous).unwrap(),previous);
        let mut bad = fixture(); bad.manifest.as_object_mut().unwrap().remove(KEY);
        assert!(crate::length_assessment_overlays::expected(&bad,&previous).is_err());
    }
    #[test] fn legacy_bundle_remains_inactive() {
        let b=Bundle { schema:"osw.query-bundle.v1".into(), manifest:json!({}), collections:Default::default() };
        validate(&b).unwrap(); assert!(!active(&b)); assert!(entities(&b).is_empty()); assert_eq!(scenes(&b),json!({}));
    }
    #[test] fn exact_identity_rows_keep_all_dimensions_and_geography_unmeasured() {
        let b=fixture(); validate(&b).unwrap(); assert_eq!(entities(&b).len(),5);
        for owner in rows(&b,"objects").iter().filter(|r| owns(r)) {
            assert!(owner["capabilities"].as_object().unwrap().values().all(|v| *v==0));
            assert_eq!(owner["map_features"],json!([])); assert!(owner["published_length_km"].is_null());
        }
        for current in document()["additions"]["route_decisions"].as_array().unwrap() {
            let (plan,path)=planning_source(current["current_id"].as_str().unwrap(),&b.manifest).unwrap();
            assert_eq!(path,PLANNING); assert_eq!(plan,current["source_decision"]);
        }
    }
    #[test] fn orphan_alias_receipt_and_coherently_changed_measurement_rows_are_refused() {
        let mut b=fixture(); b.manifest[KEY]=Value::Null; assert!(validate(&b).is_err());
        let mut b=fixture(); b.collections.get_mut("objects").unwrap()[0]["capabilities"]["scoped_width"]=json!(1);
        b.collections.get_mut("objects").unwrap()[0]["fingerprint"]=json!("rehash"); assert!(validate(&b).is_err());
        let mut b=fixture(); b.collections.get_mut("names").unwrap().push(json!({"id":"alias:other","entity_id":"current:other","label":"Atlantic North Equatorial Current"}));
        assert!(validate(&b).is_err());
        let mut b=fixture(); b.collections.insert("widths".into(),vec![json!({"id":"bad:width","current_id":"pacific-north-equatorial","value":123})]);
        assert!(validate(&b).is_err());
    }
    #[test] fn audited_families_historical_sources_and_planning_pins_are_preserved() {
        let mut b=fixture(); b.collections.get_mut("sources").unwrap()[0]["record_count"]=json!(999); assert!(validate(&b).is_err());
        let mut b=fixture(); let owner=b.collections.get_mut("objects").unwrap().iter_mut().find(|r|r["id"]=="current:north-equatorial").unwrap();
        owner["published_length_km"]=json!(123); assert!(validate(&b).is_err());
        let mut b=fixture(); b.manifest["input_sha256"][PLANNING]=json!("changed"); assert!(validate(&b).is_err());
    }
    #[test] fn dashboard_only_appends_members_and_updates_coverage_and_proposal_counts() {
        let b=fixture(); let entries:Vec<_>=(0..246).map(|i|json!({"id":format!("old:{i}"),"value":i})).collect();
        let old=json!({"entries":entries,"counts":{"named_current":106,"named_eddy":136},"proposed_current_additions":23,
            "snapshot_fingerprint":"old","historical":{"keep":1}});
        let after=dashboard_document(&b,old.clone()).unwrap();
        assert_eq!(&after["entries"].as_array().unwrap()[..246],old["entries"].as_array().unwrap().as_slice());
        assert_eq!(after["entries"].as_array().unwrap().len(),251); assert_eq!(after["counts"]["named_current"],111);
        assert_eq!(after["proposed_current_additions"],18); assert_eq!(after["historical"],old["historical"]);
        assert!(dashboard_document(&b,after).is_err());
    }
    #[test] fn filtered_membership_scenes_do_not_expand_into_other_basins_or_dimensions() {
        let b=fixture(); let records=rows(&b,MEMBERSHIPS);
        let filtered=membership_scene(&[&records[0]],&b); assert_eq!(filtered["members"].as_array().unwrap().len(),1);
        assert_eq!(filtered["members"][0]["entity_id"],"current:atlantic-north-equatorial");
        assert_eq!(for_owner(&b,"current:north-equatorial")["members"].as_array().unwrap().len(),2);
        assert_eq!(for_owner(&b,"current:indian-south-equatorial")["members"].as_array().unwrap().len(),3);
        assert!(for_owner(&b,"current:other").is_null()); assert_eq!(scenes(&b).as_object().unwrap().len(),7);
    }
    #[test] fn catalogue_and_api_projections_keep_previous_data_and_add_only_declared_context() {
        let b=fixture();
        let old=json!({"remaining_current_decisions":[],"planning_taxonomy":{"strategies":[
            {"id":"source_axis_definition_required","current_count":4,"unbuilt_count":4}]},
            "counts":{"accepted_current_names":106,"currents_without_any_reference_card":30,
                "currents_without_route_candidates":30,"currents_without_published_ranked_estimate":93,
                "route_candidates":83},"historical":{"keep":1}});
        let after=catalogue_projection(&b,old.clone()).unwrap();
        assert_eq!(after["counts"]["accepted_current_names"],111);
        assert_eq!(after["counts"]["route_candidates"],old["counts"]["route_candidates"]);
        assert_eq!(after["historical"],old["historical"]);
        assert_eq!(after["remaining_current_decisions"].as_array().unwrap().len(),5);
        assert!(catalogue_projection(&b,after).is_err());
        let prior=json!({"ok":true,"scientific":{"preserved":[1,2]}});
        assert_eq!(object_projection(&b,"current:other",prior.clone()),prior);
        let extended=snapshot_projection(&b,prior.clone());
        assert_eq!(extended["scientific"],prior["scientific"]);
        assert_eq!(extended["basin_identity_scenes"].as_object().unwrap().len(),7);
    }
}
