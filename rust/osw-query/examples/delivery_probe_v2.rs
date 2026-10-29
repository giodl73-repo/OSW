//! Native-only batch harness retaining exact API JSON strings.
use osw_query::{index_store::IndexStore, Store};
use serde_json::{json, Value};
use std::{env, fs, io::{self, Read}, process, time::Instant};

fn request_bytes(case: &Value) -> Result<&[u8], String> {
    let raw = case["request_json"].as_str().ok_or("Missing raw request JSON")?;
    serde_json::from_str::<Value>(raw).map_err(|e| e.to_string())?;
    Ok(raw.as_bytes())
}
fn response(case: &Value, value: Value) -> Result<Value, String> {
    if value["ok"] != true { return Err(format!("API failed: {value}")); }
    let mut record = case.clone();
    record["raw_response_json"] = Value::String(serde_json::to_string(&value).map_err(|e| e.to_string())?);
    Ok(record)
}
fn run() -> Result<Value, String> {
    let args: Vec<_> = env::args().collect();
    if args.len() != 3 || !["main", "index"].contains(&args[1].as_str()) {
        return Err("delivery_probe_v2 main|index PAYLOAD; raw case list on stdin".into());
    }
    let mut bytes = Vec::new();
    io::stdin().take(33554433).read_to_end(&mut bytes).map_err(|e| e.to_string())?;
    if bytes.len() > 33554432 { return Err("Probe request exceeds32MiB".into()); }
    let request: Value = serde_json::from_slice(&bytes).map_err(|e| e.to_string())?;
    let cases = request["cases"].as_array().ok_or("Missing probe case array")?;
    if cases.is_empty() || cases.len() > 1000 { return Err("Probe requires1–1000 cases".into()); }
    let start = Instant::now();
    let payload = fs::read(&args[2]).map_err(|e| e.to_string())?;
    let mut responses = Vec::new();
    let metadata = if args[1] == "index" {
        let store = IndexStore::load(&payload)?;
        for case in cases {
            if case["kind"] != "query" { return Err("Index probe supports queries only".into()); }
            responses.push(response(case, store.query(request_bytes(case)?)?)?);
        }
        store.metadata()
    } else {
        let store = Store::load(&payload)?;
        for case in cases {
            let value = match case["kind"].as_str() {
                Some("query") => store.execute(request_bytes(case)?),
                Some("object") => store.object_view(request_bytes(case)?)?,
                Some("snapshot") => match case["name"].as_str() {
                    Some("atlas") => store.atlas_snapshot()?,
                    Some("seasons") => store.seasons_snapshot()?,
                    Some("dashboard") => store.dashboard_snapshot()?,
                    _ => return Err("Unknown snapshot".into()),
                },
                _ => return Err("Unknown probe case kind".into()),
            };
            responses.push(response(case, value)?);
        }
        store.metadata()
    };
    Ok(json!({"schema":"osw.delivery-native-probe.v2",
        "metadata_json":serde_json::to_string(&metadata).map_err(|e|e.to_string())?,
        "cases":responses,"elapsed_seconds":start.elapsed().as_secs_f64()}))
}
fn main() {
    match run() {
        Ok(value) => println!("{value}"),
        Err(error) => { eprintln!("{error}"); process::exit(2); }
    }
}
