//! A display package is a read-only view of frozen data, never a query-store substitute.
use serde::Deserialize;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{collections::BTreeMap, fs, path::{Component, Path}, time::Instant};

#[allow(dead_code, unused_imports)]
mod map { include!(concat!(env!("OUT_DIR"), "/display_map.rs")); }
#[path = "../../osw-query/src/cartography.rs"]
mod cartography;

#[derive(Deserialize)]
struct Packet { schema: String, logical_sha256: String, logical_byte_length: usize, parts: Vec<Part> }
#[derive(Deserialize)]
struct Part { path: String, sha256: String, byte_length: usize }
#[derive(Deserialize)]
struct DisplayInput { schema: String, collections: Collections }
#[derive(Deserialize)]
struct Collections {
    objects: Vec<Value>,
    #[serde(default)] reference_routes: Vec<Value>,
    #[serde(default)] widths: Vec<Value>,
    #[serde(default)] measurements: Vec<Value>,
    #[serde(default)] sources: Vec<Value>,
}

fn hash(bytes: impl AsRef<[u8]>) -> String { format!("{:x}", Sha256::digest(bytes.as_ref())) }
fn run_map(request: Value) -> Result<Value, String> {
    cartography::execute(&serde_json::to_vec(&request).map_err(|e| e.to_string())?)
}

fn display(feature: &Value) -> Value {
    let geometry = &feature["geometry"];
    let coordinates = &geometry["coordinates"];
    let kind = geometry["type"].as_str().unwrap_or("");
    let result = match kind {
        "Point" => run_map(json!({"op":"project", "coordinates":coordinates})),
        "LineString" => run_map(json!({"op":"path", "coordinates":coordinates})),
        "Polygon" => run_map(json!({"op":"path", "coordinates":coordinates[0], "closed":true})),
        _ => Err("Geometry requires a different display renderer".into()),
    };
    match result {
        Ok(projected) => {
            let points = match kind { "Point" => json!([coordinates]), "Polygon" => coordinates[0].clone(), _ => coordinates.clone() };
            let fit = run_map(json!({"op":"fit", "coordinates":points})).ok();
            json!({"role":feature["role"], "note":feature["note"], "kind":kind,
                   "projected":projected, "view_box":fit.map(|v|v["view_box"].clone())})
        },
        Err(reason) => json!({"role":feature["role"], "kind":kind, "omitted_reason":reason}),
    }
}

fn numeric_values(value: &Value) -> usize {
    match value { Value::Number(_) => 1, Value::Array(a) => a.iter().map(numeric_values).sum(),
        Value::Object(m) => m.values().map(numeric_values).sum(), _ => 0 }
}

fn write_json(root: &Path, path: &str, value: &Value, total: &mut usize, numeric: &mut usize) -> Result<Value, String> {
    let raw = serde_json::to_vec(value).map_err(|e| e.to_string())?;
    *total += raw.len(); *numeric += numeric_values(value);
    if raw.len() > 2_400_000 || *total > 32_000_000 || *numeric > 250_000 { return Err("Display export exceeds its declared resource limits".into()); }
    let target = root.join(path); fs::create_dir_all(target.parent().unwrap()).map_err(|e|e.to_string())?;
    fs::write(target, &raw).map_err(|e|e.to_string())?;
    Ok(json!({"path":path, "bytes":raw.len(), "sha256":hash(&raw)}))
}

fn build(root: &Path, output: &Path) -> Result<Value, String> {
    let started = Instant::now();
    let manifest_raw = fs::read(root.join("almanac/query-engine.manifest.json")).map_err(|e| e.to_string())?;
    let manifest: Value = serde_json::from_slice(&manifest_raw).map_err(|e| e.to_string())?;
    let packet_raw = fs::read(root.join("almanac/query-data.json")).map_err(|e| e.to_string())?;
    if json!(hash(&packet_raw)) != manifest["sha256"]["almanac/query-data.json"] { return Err("Changed installed packet".into()); }
    let packet: Packet = serde_json::from_slice(&packet_raw).map_err(|e| e.to_string())?;
    if packet.schema != "osw.query-packet.v1" || packet.logical_byte_length > 220_000_000 { return Err("Unexpected display input packet".into()); }
    let mut bytes = Vec::with_capacity(packet.logical_byte_length);
    for part in &packet.parts {
        if !part.path.starts_with("query-parts/") || Path::new(&part.path).components().any(|p| !matches!(p, Component::Normal(_))) { return Err("Invalid installed packet path".into()); }
        let raw = fs::read(root.join("almanac").join(&part.path)).map_err(|e| e.to_string())?;
        if raw.len() != part.byte_length || hash(&raw) != part.sha256 || json!(part.sha256) != manifest["sha256"][format!("almanac/{}", part.path)] { return Err("Changed installed packet part".into()); }
        bytes.extend_from_slice(&raw);
    }
    if bytes.len() != packet.logical_byte_length || hash(&bytes) != packet.logical_sha256 { return Err("Changed logical corpus".into()); }
    // Validate complete UTF-8, then deserialize only existing display collections.
    // Raw field documents remain in the research store and are never copied here.
    let text = std::str::from_utf8(&bytes).map_err(|e|e.to_string())?;
    let input: DisplayInput = serde_json::from_str(text).map_err(|e|e.to_string())?;
    if input.schema != "osw.query-bundle.v1" { return Err("Unsupported display input schema".into()); }
    let data = input.collections;
    let current_count = data.objects.iter().filter(|o|o["type"] == "named_current").count();
    if current_count != 111 { return Err(format!("Expected all 111 current identities; received {current_count}")); }
    let mut seen = std::collections::BTreeSet::new();
    let mut total = 0; let mut numeric = 0; let mut entries = vec![]; let mut files = vec![];
    let mut counts = BTreeMap::<String, usize>::new();
    for object in &data.objects {
        let id = object["id"].as_str().ok_or("Object lacks stable ID")?;
        if !seen.insert(id) { return Err("Duplicate object ID".into()); }
        let features: Vec<_> = object["map_features"].as_array().into_iter().flatten().map(display).collect();
        let related = |rows: &[Value], field: &str| -> Vec<Value> {
            let ids: std::collections::BTreeSet<_> = object[field].as_array().into_iter().flatten().filter_map(Value::as_str).collect();
            rows.iter().filter(|r| r["entity_id"] == id || r["object_id"] == id || r["current_id"] == id || r["id"].as_str().is_some_and(|key|ids.contains(key))).cloned().collect()
        };
        let source_ids: std::collections::BTreeSet<_> = object["source_ids"].as_array().into_iter().flatten().filter_map(Value::as_str).collect();
        let sources: Vec<_> = data.sources.iter().filter(|s|s["id"].as_str().is_some_and(|id|source_ids.contains(id))).cloned().collect();
        let record = json!({"schema":"osw.atlas-display-record.v1", "id":id, "object":object,
            "reference_routes":related(&data.reference_routes,"route_ids"), "widths":related(&data.widths,"width_ids"),
            "measurements":related(&data.measurements,"measurement_ids"), "sources":sources,
            "scope":"Read-only display of the pinned research snapshot; not a new measurement or publication decision"});
        let record_file = format!("records/{}.json",hash(id));
        let receipt = write_json(output, &record_file, &record, &mut total, &mut numeric)?;
        entries.push(json!({"id":id,"label":object["label"],"type":object["type"],"basin":object["basin"],
            "identity_level":object["identity_level"],"display_features":features,"record":receipt}));
        files.push(receipt);
        *counts.entry(object["type"].as_str().unwrap_or("unclassified").to_owned()).or_default() += 1;
    }
    let index = json!({"schema":"osw.atlas-display-index.v1", "status":"research_preview_candidate_source_use_review_pending",
        "bundle_sha256":packet.logical_sha256,"engine_manifest_sha256":hash(manifest_raw),
        "projection_source":"rust/osw-query/src/cartography.rs", "counts":counts,"entries":entries,
        "limits":"Routes, locators, observations and model outputs retain their different scopes. This is not a complete global census."});
    files.push(write_json(output,"index.json",&index,&mut total,&mut numeric)?);
    Ok(json!({"schema":"osw.atlas-display-build.v1","status":"PASS_DISPLAY_EXPORT_ONLY", "current_count":current_count,
        "object_count":data.objects.len(),"counts":counts,"files":files,"json_bytes":total,"numeric_values":numeric,
        "active_seconds":started.elapsed().as_secs_f64(),"logical_sha256":packet.logical_sha256,
        "physics_recomputed":false,"full_query_store_replaced":false,"publication_approved":false}))
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    if args.len()!=3 { eprintln!("Usage: osw-display ROOT NEW_OUTPUT"); std::process::exit(2); }
    let output = Path::new(&args[2]);
    if output.exists() { eprintln!("Fresh output required"); std::process::exit(2); }
    fs::create_dir_all(output).unwrap();
    match build(Path::new(&args[1]),output) {
        Ok(report) => fs::write(output.join("build.json"),serde_json::to_vec_pretty(&report).unwrap()).unwrap(),
        Err(error) => { fs::write(output.join("failure.json"),serde_json::to_vec(&json!({"status":"FAIL","error":error})).unwrap()).unwrap(); eprintln!("{error}");std::process::exit(1); }
    }
}
