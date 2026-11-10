//! Native-only acceptance harness: one Store per case batch, no production ABI change.
use osw_query::{Store, index_store::IndexStore};
use serde_json::{Value, json};
use std::{env, fs, io::{self, Read}, process, time::Instant};

fn run() -> Result<Value, String> {
    let args:Vec<_>=env::args().collect();
    if args.len()!=3 || !["main","index"].contains(&args[1].as_str()) {
        return Err("delivery_probe_v1 main|index PAYLOAD; case list on stdin".into());
    }
    let mut bytes=Vec::new();io::stdin().take(33554433).read_to_end(&mut bytes).map_err(|e|e.to_string())?;
    if bytes.len()>33554432 {return Err("Probe request exceeds32MiB".into());}
    let request:Value=serde_json::from_slice(&bytes).map_err(|e|e.to_string())?;
    let cases=request["cases"].as_array().ok_or("Missing probe case array")?;
    if cases.is_empty() || cases.len()>1000 {return Err("Probe requires1–1000 cases".into());}
    let start=Instant::now();let payload=fs::read(&args[2]).map_err(|e|e.to_string())?;
    let mut responses=Vec::new();
    let metadata=if args[1]=="index" {
        let store=IndexStore::load(&payload)?;
        for (i,case) in cases.iter().enumerate() {
            if case["kind"]!="query" {return Err("Index probe supports source queries only".into());}
            let value=store.query(&serde_json::to_vec(&case["request"]).map_err(|e|e.to_string())?)?;
            if value["ok"]!=true {return Err(format!("Index probe case{i}: {value}"));}
            let mut record=case.clone();record["expected"]=value;responses.push(record);
        }
        store.metadata()
    } else {
        let store=Store::load(&payload)?;
        for (i,case) in cases.iter().enumerate() {
            let data=serde_json::to_vec(&case["request"]).map_err(|e|e.to_string())?;
            let value=match case["kind"].as_str() {
                Some("query")=>store.execute(&data),
                Some("object")=>store.object_view(&data)?,
                Some("snapshot")=>match case["name"].as_str() {
                    Some("atlas")=>store.atlas_snapshot()?,Some("seasons")=>store.seasons_snapshot()?,
                    Some("dashboard")=>store.dashboard_snapshot()?,_=>return Err("Unknown snapshot".into())
                },
                _=>return Err("Unknown probe case kind".into())
            };
            if value["ok"]!=true {return Err(format!("Main probe case{i}: {value}"));}
            let mut record=case.clone();record["expected"]=value;responses.push(record);
        }
        store.metadata()
    };
    Ok(json!({"schema":"osw.delivery-native-probe.v1","metadata":metadata,"cases":responses,"elapsed_seconds":start.elapsed().as_secs_f64()}))
}
fn main(){match run(){Ok(value)=>println!("{}",value),Err(e)=>{eprintln!("{e}");process::exit(2);}}}
