use osw_local_extents::local_extents::{EXPECTED_BYTES, LocalExtentStore, MAX_REQUEST_BYTES};
use std::{
    env, fs,
    io::{self, Read},
    process,
};

fn execute() -> Result<serde_json::Value, String> {
    let args: Vec<_> = env::args().collect();
    if args.get(1).map(String::as_str) != Some("--local-extents") {
        return Err(
            "Usage: osw-local-extents-cli --local-extents FILE [QUERY.json|-|--record -]".into(),
        );
    }
    let file = args
        .get(2)
        .ok_or("--local-extents needs the reviewed scalar bundle")?;
    if fs::metadata(file).map_err(|e| e.to_string())?.len() != EXPECTED_BYTES as u64 {
        return Err("Unexpected local-extent research snapshot size".into());
    }
    let store = LocalExtentStore::load(&fs::read(file).map_err(|e| e.to_string())?)?;
    if args.len() == 3 {
        return Ok(store.metadata());
    }
    let record = args.len() == 5 && args[3] == "--record" && args[4] == "-";
    if !record && args.len() != 4 {
        return Err("--local-extents FILE [QUERY.json|-|--record -]".into());
    }
    let path = if record { "-" } else { &args[3] };
    let mut bytes = Vec::new();
    let cap = (MAX_REQUEST_BYTES + 1) as u64;
    if path == "-" {
        io::stdin()
            .take(cap)
            .read_to_end(&mut bytes)
            .map_err(|e| e.to_string())?;
    } else {
        fs::File::open(path)
            .map_err(|e| e.to_string())?
            .take(cap)
            .read_to_end(&mut bytes)
            .map_err(|e| e.to_string())?;
    }
    if record {
        store.record(&bytes)
    } else {
        store.query(&bytes)
    }
}
fn main() {
    match execute() {
        Ok(value) => println!("{}", serde_json::to_string(&value).unwrap()),
        Err(error) => {
            eprintln!("{error}");
            process::exit(2);
        }
    }
}
