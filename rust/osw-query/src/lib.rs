use serde::Deserialize;
use serde_json::{Value, json};
use std::collections::{BTreeMap, BTreeSet};
mod map;
mod rebase;
mod spatial;
mod svg;
mod temporal;
mod workspace;
use sha2::{Digest, Sha256};

impl Store {
    /// Standalone display SVG from the same complete query scene as the browser.
    pub fn query_svg(&self, query: &[u8]) -> Result<String, String> {
        let result = self.execute(query);
        if result["ok"] != true {
            return Err(result.to_string());
        }
        svg::render(
            &result["map_scene"],
            &serde_json::from_slice(query).map_err(|e| e.to_string())?,
            &self.metadata()["bundle_sha256"],
        )
    }
}

#[derive(Deserialize)]
pub struct Bundle {
    pub schema: String,
    pub manifest: Value,
    pub collections: BTreeMap<String, Vec<Value>>,
}

pub struct Store {
    bundle: Bundle,
    ids: BTreeMap<String, BTreeMap<String, usize>>,
    fields: BTreeMap<String, BTreeSet<String>>,
    spatial: spatial::Index,
    workspace: workspace::Journal,
}

#[derive(Deserialize, Default)]
#[serde(deny_unknown_fields)]
pub struct Query {
    #[serde(default = "objects")]
    pub collection: String,
    pub text: Option<String>,
    pub record_type: Option<String>,
    pub state_code: Option<String>,
    pub evidence: Option<String>,
    pub spatial: Option<spatial::SpatialQuery>,
    pub geometry_time: Option<temporal::GeometryTime>,
    #[serde(default)]
    pub filters: Vec<Filter>,
    pub sort: Option<Sort>,
    pub limit: Option<usize>,
    #[serde(default)]
    pub offset: usize,
}
fn objects() -> String {
    "objects".into()
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Filter {
    pub field: String,
    pub op: String,
    pub value: Value,
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Sort {
    pub field: String,
    #[serde(default = "asc")]
    pub direction: String,
}
fn asc() -> String {
    "asc".into()
}

fn field<'a>(record: &'a Value, path: &str) -> Option<&'a Value> {
    path.split('.')
        .try_fold(record, |value, key| value.as_object()?.get(key))
}
fn collect_fields(value: &Value, prefix: &str, fields: &mut BTreeSet<String>) {
    if let Some(object) = value.as_object() {
        for (key, child) in object {
            let path = if prefix.is_empty() {
                key.clone()
            } else {
                format!("{prefix}.{key}")
            };
            fields.insert(path.clone());
            collect_fields(child, &path, fields);
        }
    }
}
fn present(value: Option<&Value>) -> bool {
    value.is_some_and(|v| !v.is_null())
}
fn compare(a: &Value, b: &Value) -> std::cmp::Ordering {
    match (a.as_f64(), b.as_f64()) {
        (Some(a), Some(b)) => a.total_cmp(&b),
        _ => a
            .as_str()
            .unwrap_or("")
            .to_lowercase()
            .cmp(&b.as_str().unwrap_or("").to_lowercase()),
    }
}

impl Store {
    pub fn load(bytes: &[u8]) -> Result<Self, String> {
        let mut bundle: Bundle =
            serde_json::from_slice(bytes).map_err(|e| format!("Invalid bundle JSON: {e}"))?;
        if bundle.schema != "osw.query-bundle.v1" {
            return Err("Unsupported bundle schema".into());
        }
        if !bundle.collections.contains_key("objects") {
            return Err("Missing objects collection".into());
        }
        if bundle.collections.contains_key("working_records") {
            return Err("Working records belong in a workspace journal".into());
        }
        bundle.collections.insert("working_records".into(), vec![]);
        let mut ids = BTreeMap::new();
        let mut fields = BTreeMap::new();
        for (name, records) in &bundle.collections {
            let mut index = BTreeMap::new();
            let mut keys = BTreeSet::new();
            for (i, record) in records.iter().enumerate() {
                let id = record
                    .get("id")
                    .and_then(Value::as_str)
                    .filter(|s| !s.is_empty())
                    .ok_or_else(|| format!("Missing record ID in {name}"))?;
                if index.insert(id.to_owned(), i).is_some() {
                    return Err(format!("Duplicate ID {id} in {name}"));
                }
                collect_fields(record, "", &mut keys);
            }
            ids.insert(name.clone(), index);
            fields.insert(name.clone(), keys);
        }
        // Joined object IDs must resolve in the imported collections.
        for object in &bundle.collections["objects"] {
            for (key, collection) in [
                ("width_ids", "widths"),
                ("measurement_ids", "measurements"),
                ("route_ids", "reference_routes"),
                ("source_ids", "sources"),
                ("frame_ids", "geometry_frames"),
            ] {
                if let Some(list) = object.get(key) {
                    let list = list.as_array().ok_or_else(|| format!("Invalid {key}"))?;
                    for id in list {
                        let id = id
                            .as_str()
                            .ok_or_else(|| format!("Invalid {key} reference"))?;
                        if !ids
                            .get(collection)
                            .is_some_and(|index| index.contains_key(id))
                        {
                            return Err(format!("Unresolved {collection} ID {id}"));
                        }
                        if collection == "geometry_frames"
                            && bundle.collections[collection][ids[collection][id]]["entity_id"]
                                != object["id"]
                        {
                            return Err(format!("Geometry frame {id} belongs to another object"));
                        }
                    }
                }
            }
        }
        for object in &bundle.collections["objects"] {
            for feature in object["map_features"].as_array().into_iter().flatten() {
                if let Some(frame_id) = feature.get("frame_id") {
                    let id = frame_id
                        .as_str()
                        .ok_or("Invalid geometry frame reference")?;
                    let index = ids
                        .get("geometry_frames")
                        .and_then(|i| i.get(id))
                        .ok_or_else(|| format!("Unresolved geometry frame {id}"))?;
                    let frame = &bundle.collections["geometry_frames"][*index];
                    if frame["entity_id"] != object["id"]
                        || frame["date"] != feature["observation_date"]
                        || frame["coordinates_lon_lat"] != feature["geometry"]["coordinates"]
                        || frame["geometry_role"] != feature["role"]
                    {
                        return Err(format!(
                            "Geometry frame {id} does not match its map feature"
                        ));
                    }
                }
            }
        }
        let spatial = spatial::Index::build(&bundle.collections)?;
        fields.insert(
            "working_records".into(),
            BTreeSet::from([
                "id".into(),
                "label".into(),
                "summary".into(),
                "status".into(),
                "target.collection".into(),
                "target.id".into(),
            ]),
        );
        Ok(Self {
            bundle,
            ids,
            fields,
            spatial,
            workspace: workspace::Journal::empty(format!("{:x}", Sha256::digest(bytes))),
        })
    }

    pub fn metadata(&self) -> Value {
        let mut object_type_counts = BTreeMap::<String, usize>::new();
        let mut geometry_dates = BTreeSet::new();
        for row in &self.bundle.collections["objects"] {
            for feature in row["map_features"].as_array().into_iter().flatten() {
                if let Some(day) = feature["observation_date"]
                    .as_str()
                    .filter(|d| temporal::valid_day(d))
                {
                    geometry_dates.insert(day);
                }
            }
            if let Some(kind) = row.get("type").and_then(Value::as_str) {
                *object_type_counts.entry(kind.to_owned()).or_default() += 1;
            }
        }
        json!({"ok":true,"engine":"rust-osw-query-v1","manifest":self.bundle.manifest,
            "workspace_revision":self.workspace.events.len(),"bundle_sha256":self.workspace.bundle_sha256,
            "object_type_counts":object_type_counts,
            "geometry_observation_dates":geometry_dates,
            "collections":self.bundle.collections.iter().map(|(name,records)| json!({"name":name,"count":records.len(),"fields":self.fields[name]})).collect::<Vec<_>>()})
    }
    fn known_field(&self, collection: &str, name: &str) -> Result<(), String> {
        if !self.fields[collection].contains(name) {
            return Err(format!("Unknown field {name} in {collection}"));
        }
        Ok(())
    }
    pub fn query(&self, query: Query) -> Result<Value, String> {
        let records = self
            .bundle
            .collections
            .get(&query.collection)
            .ok_or_else(|| format!("Unknown collection {}", query.collection))?;
        let limit = query.limit.unwrap_or(100);
        if let Some(time) = &query.geometry_time {
            if query.collection != "objects" {
                return Err("Geometry time applies to objects".into());
            }
            time.validate()?;
        }
        if !(1..=500).contains(&limit) {
            return Err("Limit must be 1..500".into());
        }
        if query.filters.len() > 20 || query.text.as_ref().is_some_and(|s| s.len() > 1000) {
            return Err("Query exceeds input limits".into());
        }
        if (query.state_code.is_some() || query.evidence.is_some()) && query.collection != "objects"
        {
            return Err("State and evidence joins apply to objects".into());
        }
        if let Some(spatial) = &query.spatial {
            if query.collection != "objects" {
                return Err("Spatial queries apply to objects".into());
            }
            self.spatial.validate(spatial)?;
        }
        if let Some(kind) = &query.record_type {
            self.known_field(&query.collection, "type")?;
            if !records
                .iter()
                .any(|r| r.get("type").and_then(Value::as_str) == Some(kind))
            {
                return Err(format!("Unknown record type {kind}"));
            }
        }
        if let Some(state) = &query.state_code {
            let known = self.bundle.collections.get("states").is_some_and(|rows| {
                rows.iter()
                    .any(|r| r.get("code").and_then(Value::as_str) == Some(state))
            });
            if !known {
                return Err(format!("Unknown OSW state {state}"));
            }
        }
        if let Some(evidence) = &query.evidence {
            self.known_field("objects", &format!("capabilities.{evidence}"))?;
        }
        for filter in &query.filters {
            self.known_field(&query.collection, &filter.field)?;
            if !["eq", "ne", "contains", "exists", "gt", "lt"].contains(&filter.op.as_str()) {
                return Err(format!("Unsupported operator {}", filter.op));
            }
            if ["gt", "lt"].contains(&filter.op.as_str()) && !filter.value.is_number() {
                return Err("Numeric comparison requires a number".into());
            }
            if filter.op == "contains" && !filter.value.is_string() {
                return Err("Contains requires text".into());
            }
            if filter.op == "exists" && !filter.value.is_boolean() {
                return Err("Exists requires true or false".into());
            }
        }
        if let Some(sort) = &query.sort {
            self.known_field(&query.collection, &sort.field)?;
            if !["asc", "desc"].contains(&sort.direction.as_str()) {
                return Err("Sort direction must be asc or desc".into());
            }
            if records
                .iter()
                .filter_map(|r| field(r, &sort.field))
                .any(|v| !v.is_null() && !v.is_string() && !v.is_number())
            {
                return Err("Sort field must be text or numeric".into());
            }
        }
        let text = query.text.as_ref().map(|s| s.trim().to_lowercase());
        let spatial_matches: BTreeMap<String, Vec<Value>> = if let Some(spatial) = &query.spatial {
            records
                .iter()
                .filter_map(|row| {
                    let id = row["id"].as_str().unwrap();
                    let mut matches = self.spatial.matches(id, spatial);
                    if let Some(time) = &query.geometry_time {
                        matches.retain(|relation| {
                            relation["feature_index"]
                                .as_u64()
                                .and_then(|i| row["map_features"].get(i as usize))
                                .is_some_and(|feature| time.includes(feature))
                        });
                    }
                    if matches.is_empty() {
                        None
                    } else {
                        Some((id.to_owned(), matches))
                    }
                })
                .collect()
        } else {
            BTreeMap::new()
        };
        let mut matches: Vec<&Value> = records
            .iter()
            .filter(|r| {
                if query.geometry_time.as_ref().is_some_and(|t| {
                    !r["map_features"]
                        .as_array()
                        .is_some_and(|fs| fs.iter().any(|f| t.includes(f)))
                }) {
                    return false;
                }
                if query.spatial.is_some()
                    && !spatial_matches.contains_key(r["id"].as_str().unwrap())
                {
                    return false;
                }
                if let Some(text) = &text {
                    if !text.is_empty() && !r.to_string().to_lowercase().contains(text) {
                        return false;
                    }
                }
                if let Some(kind) = &query.record_type {
                    if r.get("type").and_then(Value::as_str) != Some(kind) {
                        return false;
                    }
                }
                if let Some(state) = &query.state_code {
                    if !r
                        .get("state_codes")
                        .and_then(Value::as_array)
                        .is_some_and(|a| a.iter().any(|v| v.as_str() == Some(state)))
                    {
                        return false;
                    }
                }
                if let Some(evidence) = &query.evidence {
                    if field(r, &format!("capabilities.{evidence}"))
                        .and_then(Value::as_u64)
                        .unwrap_or(0)
                        == 0
                    {
                        return false;
                    }
                }
                query.filters.iter().all(|filter| {
                    let actual = field(r, &filter.field).unwrap_or(&Value::Null);
                    match filter.op.as_str() {
                        "eq" => actual == &filter.value,
                        "ne" => actual != &filter.value,
                        "exists" => {
                            present(field(r, &filter.field)) == filter.value.as_bool().unwrap()
                        }
                        "contains" => {
                            if let Some(text) = actual.as_str() {
                                text.to_lowercase()
                                    .contains(&filter.value.as_str().unwrap().to_lowercase())
                            } else if let Some(array) = actual.as_array() {
                                array.iter().any(|v| v == &filter.value)
                            } else {
                                false
                            }
                        }
                        "gt" => actual
                            .as_f64()
                            .is_some_and(|n| n > filter.value.as_f64().unwrap()),
                        "lt" => actual
                            .as_f64()
                            .is_some_and(|n| n < filter.value.as_f64().unwrap()),
                        _ => false,
                    }
                })
            })
            .collect();
        if let Some(sort) = &query.sort {
            matches.sort_by(|a, b| {
                let av = field(a, &sort.field);
                let bv = field(b, &sort.field);
                let ordering = match (present(av), present(bv)) {
                    (false, true) => std::cmp::Ordering::Greater,
                    (true, false) => std::cmp::Ordering::Less,
                    (false, false) => std::cmp::Ordering::Equal,
                    _ => {
                        let result = compare(av.unwrap(), bv.unwrap());
                        if sort.direction == "desc" {
                            result.reverse()
                        } else {
                            result
                        }
                    }
                };
                ordering.then_with(|| a["id"].as_str().cmp(&b["id"].as_str()))
            });
        } else {
            matches.sort_by(|a, b| a["id"].as_str().cmp(&b["id"].as_str()));
        }
        let total = matches.len();
        let mut map_scene = if query.collection == "objects" {
            map::scene_selected(&matches, query.geometry_time.as_ref())
        } else {
            Value::Null
        };
        if let Some(time) = &query.geometry_time {
            map_scene["geometry_time"] = json!({"from":time.from,"to":time.to,"include_undated":time.include_undated,
                "scope":"Exact recorded observation days, inclusive. Undated marks are context only. No interpolation, persistence or seasonal inference."});
        }
        if let Some(spatial) = &query.spatial {
            for feature in map_scene["features"].as_array_mut().unwrap() {
                let relations = &spatial_matches[feature["entity_id"].as_str().unwrap()];
                feature["matches_selected_state"] = json!(
                    relations
                        .iter()
                        .any(|r| r["feature_index"] == feature["feature_index"])
                );
            }
            let relations: BTreeMap<_, _> = matches
                .iter()
                .map(|r| {
                    let id = r["id"].as_str().unwrap();
                    (id, &spatial_matches[id])
                })
                .collect();
            map_scene["spatial_relations"] = json!(relations);
            let state = self.bundle.collections["states"]
                .iter()
                .find(|s| s["code"] == spatial.state_code)
                .unwrap();
            let display = json!({"id":state["id"],"label":state["label"],"type":"osw_state","map_features":[{"geometry":state["display_geometry"],"role":"approximate_masked_state","note":state["geometry_scope"]}]});
            map_scene["state_features"] = map::scene(&[&display])["features"].clone();
            map_scene["selected_state_code"] = json!(spatial.state_code);
        }
        let rows: Vec<_> = matches
            .into_iter()
            .skip(query.offset)
            .take(limit)
            .map(|row| {
                let mut row = row.clone();
                if query.spatial.is_some() {
                    row["spatial_matches"] = json!(spatial_matches[row["id"].as_str().unwrap()]);
                }
                row
            })
            .collect();
        Ok(
            json!({"ok":true,"engine":"rust-osw-query-v1","collection":query.collection,"total":total,"offset":query.offset,"limit":limit,"rows":rows,"map_scene":map_scene,
                "spatial_scope":if query.spatial.is_some(){json!("Computed display geometry, separate from recorded state links. Point locators and shared gateways require their own predicates; neither is current or eddy containment.")}else{Value::Null}}),
        )
    }
    pub fn record(&self, collection: &str, id: &str) -> Result<Value, String> {
        let index = self
            .ids
            .get(collection)
            .and_then(|ids| ids.get(id))
            .ok_or_else(|| format!("Record not found: {collection}/{id}"))?;
        Ok(
            json!({"ok":true,"collection":collection,"record":self.bundle.collections[collection][*index]}),
        )
    }
    pub fn execute(&self, bytes: &[u8]) -> Value {
        let result = serde_json::from_slice(bytes)
            .map_err(|e| format!("Invalid query: {e}"))
            .and_then(|q| self.query(q));
        result.unwrap_or_else(|error| json!({"ok":false,"error":error}))
    }
}

#[cfg(target_arch = "wasm32")]
mod wasm {
    use super::*;
    use std::cell::RefCell;
    thread_local! { static STORE: RefCell<Option<Store>>=const{RefCell::new(None)}; static RESULT:RefCell<Vec<u8>>=const{RefCell::new(Vec::new())}; }
    thread_local! {static REBASE_SOURCE:RefCell<Option<Store>>=const{RefCell::new(None)};}
    fn output(value: Value) {
        RESULT.with(|result| *result.borrow_mut() = serde_json::to_vec(&value).unwrap());
    }
    #[unsafe(no_mangle)]
    pub extern "C" fn osw_alloc(len: usize) -> *mut u8 {
        Box::into_raw(vec![0u8; len].into_boxed_slice()) as *mut u8
    }
    #[unsafe(no_mangle)]
    pub unsafe extern "C" fn osw_dealloc(ptr: *mut u8, len: usize) {
        unsafe {
            drop(Box::from_raw(std::ptr::slice_from_raw_parts_mut(ptr, len)));
        }
    }
    #[unsafe(no_mangle)]
    pub unsafe extern "C" fn osw_load(ptr: *const u8, len: usize) -> i32 {
        let bytes = unsafe { std::slice::from_raw_parts(ptr, len) };
        match Store::load(bytes) {
            Ok(store) => {
                output(store.metadata());
                STORE.with(|s| *s.borrow_mut() = Some(store));
                1
            }
            Err(error) => {
                output(json!({"ok":false,"error":error}));
                0
            }
        }
    }
    #[unsafe(no_mangle)]
    pub unsafe extern "C" fn osw_query(ptr: *const u8, len: usize) {
        let bytes = unsafe { std::slice::from_raw_parts(ptr, len) };
        STORE.with(|s| {
            output(
                s.borrow()
                    .as_ref()
                    .map(|s| s.execute(bytes))
                    .unwrap_or_else(|| json!({"ok":false,"error":"Store not loaded"})),
            )
        });
    }
    #[unsafe(no_mangle)]
    pub unsafe extern "C" fn osw_record(ptr: *const u8, len: usize) {
        let bytes = unsafe { std::slice::from_raw_parts(ptr, len) };
        let request: Result<Value, _> = serde_json::from_slice(bytes);
        let result = request.map_err(|e| e.to_string()).and_then(|r| {
            STORE.with(|s| {
                s.borrow()
                    .as_ref()
                    .ok_or("Store not loaded".into())
                    .and_then(|s| {
                        s.record(
                            r["collection"].as_str().unwrap_or(""),
                            r["id"].as_str().unwrap_or(""),
                        )
                    })
            })
        });
        output(result.unwrap_or_else(|error| json!({"ok":false,"error":error})));
    }
    #[unsafe(no_mangle)]
    pub unsafe extern "C" fn osw_query_svg(ptr: *const u8, len: usize) {
        let bytes = unsafe { std::slice::from_raw_parts(ptr, len) };
        let result = STORE.with(|s| {
            s.borrow()
                .as_ref()
                .ok_or("Store not loaded".into())
                .and_then(|s| s.query_svg(bytes))
        });
        output(match result {
            Ok(svg) => json!({"ok":true,"svg":svg}),
            Err(error) => json!({"ok":false,"error":error}),
        });
    }
    #[unsafe(no_mangle)]
    pub extern "C" fn osw_result_ptr() -> *const u8 {
        RESULT.with(|r| r.borrow().as_ptr())
    }
    #[unsafe(no_mangle)]
    pub extern "C" fn osw_result_len() -> usize {
        RESULT.with(|r| r.borrow().len())
    }
    #[unsafe(no_mangle)]
    pub unsafe extern "C" fn osw_rebase_source(ptr: *const u8, len: usize) {
        REBASE_SOURCE.with(|old| *old.borrow_mut() = None);
        if len > 100_000_000 {
            output(json!({"ok":false,"error":"Source snapshot exceeds 100 MB"}));
            return;
        }
        let bytes = unsafe { std::slice::from_raw_parts(ptr, len) };
        let result = Store::load(bytes).map(|store| {
            let metadata = store.metadata();
            REBASE_SOURCE.with(|old| *old.borrow_mut() = Some(store));
            metadata
        });
        output(result.unwrap_or_else(|error| json!({"ok":false,"error":error})));
    }
    #[unsafe(no_mangle)]
    pub unsafe extern "C" fn osw_workspace_rebase(ptr: *const u8, len: usize) {
        let bytes = unsafe { std::slice::from_raw_parts(ptr, len) };
        let envelope: Result<Value, _> = serde_json::from_slice(bytes);
        let result = envelope.map_err(|e| e.to_string()).and_then(|r| {
            STORE.with(|s| {
                REBASE_SOURCE.with(|old| {
                    s.borrow()
                        .as_ref()
                        .ok_or("Store not loaded".into())
                        .and_then(|s| {
                            old.borrow()
                                .as_ref()
                                .ok_or("Matching old source snapshot is required".into())
                                .and_then(|old| {
                                    s.workspace_rebase(
                                        old,
                                        r["request"].to_string().as_bytes(),
                                        r["prepare"] == true,
                                    )
                                })
                        })
                })
            })
        });
        output(result.unwrap_or_else(|error| json!({"ok":false,"error":error})));
    }
    #[unsafe(no_mangle)]
    pub unsafe extern "C" fn osw_workspace_prepare(ptr: *const u8, len: usize) {
        let bytes = unsafe { std::slice::from_raw_parts(ptr, len) };
        let result = STORE.with(|s| {
            s.borrow()
                .as_ref()
                .ok_or("Store not loaded".into())
                .and_then(|s| s.workspace_prepare(bytes))
        });
        output(result.unwrap_or_else(|error| json!({"ok":false,"error":error})));
    }
    #[unsafe(no_mangle)]
    pub unsafe extern "C" fn osw_workspace_import(ptr: *const u8, len: usize) {
        let bytes = unsafe { std::slice::from_raw_parts(ptr, len) };
        let result = STORE.with(|s| {
            s.borrow_mut()
                .as_mut()
                .ok_or("Store not loaded".into())
                .and_then(|s| s.workspace_import(bytes))
        });
        output(result.unwrap_or_else(|error| json!({"ok":false,"error":error})));
    }
    #[unsafe(no_mangle)]
    pub extern "C" fn osw_workspace_export() {
        output(STORE.with(|s| {
            s.borrow()
                .as_ref()
                .map(|s| s.workspace_export())
                .unwrap_or_else(|| json!({"ok":false,"error":"Store not loaded"}))
        }));
    }
    #[unsafe(no_mangle)]
    pub extern "C" fn osw_metadata() {
        output(STORE.with(|s| {
            s.borrow()
                .as_ref()
                .map(|s| s.metadata())
                .unwrap_or_else(|| json!({"ok":false,"error":"Store not loaded"}))
        }));
    }
    #[unsafe(no_mangle)]
    pub unsafe extern "C" fn osw_workspace_check(ptr: *const u8, len: usize) {
        let bytes = unsafe { std::slice::from_raw_parts(ptr, len) };
        let result = STORE.with(|s| {
            s.borrow()
                .as_ref()
                .ok_or("Store not loaded".into())
                .and_then(|s| s.workspace_check(bytes))
        });
        output(result.unwrap_or_else(|error| json!({"ok":false,"error":error})));
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn store() -> Store {
        Store::load(json!({"schema":"osw.query-bundle.v1","manifest":{},"collections":{"objects":[
        {"id":"a","label":"Alpha","type":"named_current","width_ids":["w"],"state_codes":["KURO"],"capabilities":{"scoped_width":1},"published_length_km":null},
        {"id":"b","label":"Beta","type":"named_current","width_ids":[],"state_codes":[],"capabilities":{"scoped_width":0},"published_length_km":3000},
        {"id":"c","label":"Gamma","type":"named_eddy","width_ids":[],"state_codes":[],"capabilities":{"scoped_width":0},"published_length_km":20000}],"widths":[{"id":"w","approximate_width_km":218,"fixed_layer_bounds_m":null}],"states":[{"id":"state:KURO","code":"KURO"}]}}).to_string().as_bytes()).unwrap()
    }
    #[test]
    fn joins_and_missing() {
        let s = store();
        let r = s.execute(br#"{"state_code":"KURO","evidence":"scoped_width"}"#);
        assert_eq!(r["total"], 1);
        assert_eq!(r["rows"][0]["id"], "a");
        assert!(r["rows"][0]["published_length_km"].is_null());
    }
    #[test]
    fn frame_identity_and_geometry_binding() {
        let mut bundle = json!({"schema":"osw.query-bundle.v1","manifest":{},"collections":{"states":[],"objects":[{"id":"a","frame_ids":["f"],"map_features":[{"frame_id":"f","observation_date":"2025-01-15","role":"diagnostic","geometry":{"type":"LineString","coordinates":[[0,0],[1,1]]}}]}],"geometry_frames":[{"id":"f","entity_id":"a","date":"2025-01-15","geometry_role":"diagnostic","coordinates_lon_lat":[[0,0],[1,1]]}]}});
        assert!(Store::load(bundle.to_string().as_bytes()).is_ok());
        bundle["collections"]["geometry_frames"][0]["date"] = json!("2025-02-15");
        assert!(
            Store::load(bundle.to_string().as_bytes())
                .err()
                .unwrap()
                .contains("does not match")
        );
    }
    #[test]
    fn numeric_sort_null_last_and_page() {
        let s = store();
        let r = s.execute(
            br#"{"sort":{"field":"published_length_km","direction":"desc"},"limit":1,"offset":1}"#,
        );
        assert_eq!(r["rows"][0]["id"], "b");
        assert_eq!(r["total"], 3);
        let r =
            s.execute(br#"{"sort":{"field":"published_length_km","direction":"desc"},"offset":2}"#);
        assert_eq!(r["rows"][0]["id"], "a");
    }
    #[test]
    fn reject_bad_queries() {
        let s = store();
        for q in [
            r#"{"limit":0}"#,
            r#"{"state_code":"NOPE"}"#,
            r#"{"evidence":"unknown"}"#,
            r#"{"sort":{"field":"width_ids"}}"#,
            r#"{"filters":[{"field":"label","op":"execute","value":"x"}]}"#,
            r#"{"filters":[{"field":"missing","op":"eq","value":0}]}"#,
            r#"{"filters":[{"field":"published_length_km","op":"gt","value":"3"}]}"#,
            r#"{"sql":"drop table"}"#,
        ] {
            assert_eq!(s.execute(q.as_bytes())["ok"], false, "{q}");
        }
    }
    #[test]
    fn filter_null_is_not_zero() {
        let s = store();
        let r = s.execute(br#"{"filters":[{"field":"published_length_km","op":"eq","value":0}]}"#);
        assert_eq!(r["total"], 0);
        let r = s.execute(
            br#"{"filters":[{"field":"published_length_km","op":"exists","value":false}]}"#,
        );
        assert_eq!(r["total"], 1);
    }
    #[test]
    fn duplicate_and_unresolved_ids_fail() {
        let mut b = store().bundle;
        b.collections.remove("working_records");
        let duplicate = b.collections["objects"][0].clone();
        b.collections.get_mut("objects").unwrap().push(duplicate);
        let raw = json!({"schema":b.schema,"manifest":b.manifest,"collections":b.collections});
        assert!(
            Store::load(&serde_json::to_vec(&raw).unwrap())
                .err()
                .unwrap()
                .contains("Duplicate ID")
        );
        let s=br#"{"schema":"osw.query-bundle.v1","manifest":{},"collections":{"objects":[{"id":"a","width_ids":["missing"]}],"widths":[]}}"#;
        assert!(Store::load(s).is_err());
    }
}
