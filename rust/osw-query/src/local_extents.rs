//! Small, immutable research dataset using the existing query semantics.
//! It never loads or modifies the complete atlas or its workspace journal.
use crate::{Bundle, Query, Store, collect_fields, spatial, workspace};
use serde::Deserialize;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};

pub const EXPECTED_BYTES: usize = 835839;
pub const EXPECTED_SHA256: &str =
    "e4ca7c532c39d22efc2d6600a89424f48558669fe6e6682b1c6ec9442d00cdf8";
pub const MAX_REQUEST_BYTES: usize = 20_000;
pub const COLLECTIONS: [&str; 2] = ["current_local_extent_cases", "current_local_extents"];
pub const SCOPE: &str = "2013 monthly mean-field local extents at15m. Candidate-region research evidence; original failures retained. No physical whole-current widths, annual ranges, ranks or OSW state joins admitted.";

pub struct LocalExtentStore {
    engine: Store,
    provenance: Value,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct RecordRequest {
    collection: String,
    id: String,
}

impl LocalExtentStore {
    pub fn load(bytes: &[u8]) -> Result<Self, String> {
        // Validate exact custody before parsing or accepting any classifications.
        if bytes.len() != EXPECTED_BYTES
            || format!("{:x}", Sha256::digest(bytes)) != EXPECTED_SHA256
        {
            return Err("Changed local-extent research snapshot; use the reviewed version".into());
        }
        let document: Value = serde_json::from_slice(bytes).map_err(|e| e.to_string())?;
        if document["schema"] != "osw.current-local-extent-evidence.v1"
            || document["admission"]["whole_current_width_admitted"] != false
            || document["admission"]["width_inventory_count_increment"] != 0
        {
            return Err("Unsupported local-extent research scope".into());
        }
        let mut collections: BTreeMap<String, Vec<Value>> =
            serde_json::from_value(document["collections"].clone()).map_err(|e| e.to_string())?;
        if collections.len() != 2
            || collections.get(COLLECTIONS[0]).map(Vec::len) != Some(72)
            || collections.get(COLLECTIONS[1]).map(Vec::len) != Some(864)
        {
            return Err("Incomplete local-extent research collections".into());
        }
        // Internal empty objects support the shared query implementation only.
        // They are not exposed as an atlas or a named-current inventory.
        collections.insert("objects".into(), vec![]);
        let mut ids = BTreeMap::new();
        let mut fields = BTreeMap::new();
        for (name, rows) in &collections {
            let mut index = BTreeMap::new();
            let mut keys = BTreeSet::new();
            for (position, row) in rows.iter().enumerate() {
                let id = row["id"].as_str().ok_or("Missing local-extent ID")?;
                if index.insert(id.to_owned(), position).is_some() {
                    return Err("Duplicate local-extent ID".into());
                }
                collect_fields(row, "", &mut keys);
            }
            ids.insert(name.clone(), index);
            fields.insert(name.clone(), keys);
        }
        let spatial = spatial::Index::build(&collections)?;
        let bundle = Bundle {
            schema: "osw.local-extent-research-store.v1".into(),
            manifest: json!({"dataset":"current-local-extents-v1","source_sha256":EXPECTED_SHA256}),
            collections,
        };
        Ok(Self {
            engine: Store {
                bundle,
                ids,
                fields,
                spatial,
                workspace: workspace::Journal::empty(EXPECTED_SHA256.into()),
            },
            provenance: json!({"source":document["source"],"source_scope":document["source_scope"],
                "admission":document["admission"],"input_sha256":document["input_sha256"]}),
        })
    }

    pub fn metadata(&self) -> Value {
        json!({"ok":true,"engine":"rust-osw-query-v1","dataset":"current-local-extents-v1",
            "bundle_sha256":EXPECTED_SHA256,"source_bytes":EXPECTED_BYTES,"scope":SCOPE,
            "complete_atlas_loaded":false,"workspace_available":false,"physical_width_inventory_increment":0,
            "provenance":self.provenance,"evidence_figure":"../figures/eacc-local-extent-primary-months-v1.svg",
            "collections":COLLECTIONS.iter().map(|name|json!({"name":name,
                "count":self.engine.bundle.collections[*name].len(),"fields":self.engine.fields[*name]})).collect::<Vec<_>>()})
    }

    pub fn query(&self, bytes: &[u8]) -> Result<Value, String> {
        if bytes.len() > MAX_REQUEST_BYTES {
            return Err("Local-extent query is too large".into());
        }
        let query: Query =
            serde_json::from_slice(bytes).map_err(|e| format!("Invalid query: {e}"))?;
        if !COLLECTIONS.contains(&query.collection.as_str()) {
            return Err("Choose a local-extent research collection".into());
        }
        if query.spatial.is_some()
            || query.state_code.is_some()
            || query.evidence.is_some()
            || query.geometry_time.is_some()
            || query.seasonal.is_some()
            || query.network_path.is_some()
            || query.taxonomy.is_some()
            || query.record_type.is_some()
        {
            return Err("Local-extent research queries do not support physical state, geometry, taxonomy or seasonal joins".into());
        }
        let mut result = self.engine.query(query)?;
        result["dataset"] = json!("current-local-extents-v1");
        result["scope"] = json!(SCOPE);
        result["bundle_sha256"] = json!(EXPECTED_SHA256);
        result["physical_width_inventory_increment"] = json!(0);
        Ok(result)
    }

    pub fn record(&self, bytes: &[u8]) -> Result<Value, String> {
        if bytes.len() > MAX_REQUEST_BYTES {
            return Err("Local-extent record request is too large".into());
        }
        let request: RecordRequest = serde_json::from_slice(bytes).map_err(|e| e.to_string())?;
        if !COLLECTIONS.contains(&request.collection.as_str()) {
            return Err("Choose a local-extent research collection".into());
        }
        let mut result = self.engine.record(&request.collection, &request.id)?;
        if let Some(case_id) = result["record"]["case_id"].as_str().map(str::to_owned) {
            result["case_context"] =
                self.engine.record(COLLECTIONS[0], &case_id)?["record"].clone();
        }
        result["dataset"] = json!("current-local-extents-v1");
        result["scope"] = json!(SCOPE);
        Ok(result)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    const RAW: &[u8] =
        include_bytes!("../../../research/eacc-local-extent-evidence-bundle-v1.json");
    fn store() -> LocalExtentStore {
        LocalExtentStore::load(RAW).unwrap()
    }
    fn execute(store: &LocalExtentStore, query: Value) -> Value {
        store.query(&serde_json::to_vec(&query).unwrap()).unwrap()
    }

    #[test]
    fn scoped_metadata_never_claims_complete_atlas_coverage() {
        let store = store();
        let metadata = store.metadata();
        assert_eq!(metadata["collections"][0]["count"], 72);
        assert_eq!(metadata["collections"][1]["count"], 864);
        assert_eq!(metadata["collections"].as_array().unwrap().len(), 2);
        assert_eq!(metadata["complete_atlas_loaded"], false);
        assert_eq!(metadata["physical_width_inventory_increment"], 0);
        assert!(Store::load(RAW).is_err());
    }

    #[test]
    fn primary_half_peak_core_query_keeps_exact_monthly_brackets() {
        let result = execute(
            &store(),
            json!({"collection":COLLECTIONS[1],"filters":[
            {"field":"native_latitude_offset","op":"eq","value":0},
            {"field":"normal_sample_step_km","op":"eq","value":5},
            {"field":"threshold_fraction","op":"eq","value":0.5},
            {"field":"quantity","op":"eq","value":"core_to_positive_normal_threshold_extent"}],
            "sort":{"field":"month","direction":"asc"},"limit":100}),
        );
        assert_eq!(result["total"], 12);
        assert_eq!(result["rows"][0]["month"], 1);
        assert_eq!(result["rows"][11]["month"], 12);
        assert!(
            result["rows"]
                .as_array()
                .unwrap()
                .iter()
                .all(|r| r["source_scale_gate_passed"] == true)
        );
        let raw: Value = serde_json::from_slice(RAW).unwrap();
        for row in result["rows"].as_array().unwrap() {
            let original = raw["collections"][COLLECTIONS[1]]
                .as_array()
                .unwrap()
                .iter()
                .find(|r| r["id"] == row["id"])
                .unwrap();
            assert_eq!(row, original);
        }
    }

    #[test]
    fn coarse_primary_missing_peaks_are_queryable_as_six_failures() {
        let result = execute(
            &store(),
            json!({"collection":COLLECTIONS[0],"filters":[
            {"field":"native_latitude_offset","op":"eq","value":0},
            {"field":"normal_sample_step_km","op":"eq","value":10},
            {"field":"status","op":"eq","value":"missing_supported_profile"}],
            "sort":{"field":"month"}}),
        );
        let months: Vec<_> = result["rows"]
            .as_array()
            .unwrap()
            .iter()
            .map(|r| r["month"].as_u64().unwrap())
            .collect();
        assert_eq!(months, vec![3, 5, 7, 8, 9, 12]);
    }

    #[test]
    fn null_width_is_not_zero_and_paging_preserves_every_attempt() {
        let store = store();
        let nulls = execute(
            &store,
            json!({"collection":COLLECTIONS[1],"filters":[{"field":"whole_current_width_km","op":"eq","value":null}],"limit":500}),
        );
        let zeros = execute(
            &store,
            json!({"collection":COLLECTIONS[1],"filters":[{"field":"whole_current_width_km","op":"eq","value":0}]}),
        );
        let second = execute(
            &store,
            json!({"collection":COLLECTIONS[1],"offset":500,"limit":500}),
        );
        assert_eq!(nulls["total"], 864);
        assert_eq!(zeros["total"], 0);
        assert_eq!(second["rows"].as_array().unwrap().len(), 364);
        let ids: BTreeSet<_> = nulls["rows"]
            .as_array()
            .unwrap()
            .iter()
            .chain(second["rows"].as_array().unwrap())
            .map(|r| r["id"].as_str().unwrap())
            .collect();
        assert_eq!(ids.len(), 864);
    }

    #[test]
    fn record_resolves_original_seed_case_without_claiming_a_boundary() {
        let store = store();
        let row = &store.engine.bundle.collections[COLLECTIONS[1]][0];
        let result = store
            .record(
                &serde_json::to_vec(&json!({"collection":COLLECTIONS[1],"id":row["id"]})).unwrap(),
            )
            .unwrap();
        assert_eq!(result["case_context"]["id"], row["case_id"]);
        assert_eq!(
            result["case_context"]["reference_position_kind"],
            "original_model_seed_not_current_boundary_or_shore"
        );
    }

    #[test]
    fn changed_or_oversized_data_cannot_replace_the_reviewed_snapshot() {
        let mut changed = RAW.to_vec();
        changed[0] = b' ';
        assert!(LocalExtentStore::load(&changed).is_err());
        assert!(LocalExtentStore::load(&RAW[..RAW.len() - 1]).is_err());
        changed.push(b' ');
        assert!(LocalExtentStore::load(&changed).is_err());
    }

    #[test]
    fn physical_and_unknown_queries_are_refused() {
        let store = store();
        for request in [
            json!({"collection":"objects"}),
            json!({"collection":"widths"}),
            json!({"collection":COLLECTIONS[1],"state_code":"NAT"}),
            json!({"collection":COLLECTIONS[1],"seasonal":{"month":7}}),
            json!({"collection":COLLECTIONS[1],"filters":[{"field":"width_km","op":"eq","value":100}]}),
            json!({"collection":COLLECTIONS[1],"limit":501}),
            json!({"collection":COLLECTIONS[1],"unrecognized":true}),
        ] {
            assert!(store.query(&serde_json::to_vec(&request).unwrap()).is_err());
        }
        assert!(store.query(&vec![b' '; MAX_REQUEST_BYTES + 1]).is_err());
    }
}
