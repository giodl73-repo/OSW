use osw_query::Store;
use std::{
    env, fs,
    io::{self, Read, Write},
    process,
};
fn output_workspace(
    value: serde_json::Value,
    args: &[String],
    position: usize,
) -> Result<serde_json::Value, String> {
    if args.len() == position {
        return Ok(value);
    }
    if args.get(position).map(String::as_str) != Some("--output") || args.len() != position + 2 {
        return Err("Expected --output NEW-JOURNAL.json".into());
    }
    let path = &args[position + 1];
    let mut file = fs::OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(path)
        .map_err(|e| format!("Cannot create new journal {path}: {e}"))?;
    let bytes = serde_json::to_vec_pretty(&value["journal"]).map_err(|e| e.to_string())?;
    file.write_all(&bytes)
        .and_then(|_| file.sync_all())
        .map_err(|e| {
            format!("Journal write failed; incomplete new file may remain at {path}: {e}")
        })?;
    Ok(value)
}
fn main() {
    let args: Vec<_> = env::args().collect();
    let result = (|| -> Result<serde_json::Value, String> {
        let path = args.get(1).ok_or(
            "Usage: osw-query-cli BUNDLE.json [--workspace JOURNAL.json] [QUERY.json | --transaction TX.json | --export-workspace] [--output NEW-JOURNAL.json]; map: --svg QUERY.json --output NEW-MAP.svg; migration: --rebase OLD-BUNDLE.json REQUEST.json [--prepare --output NEW-JOURNAL.json]; '-' query reads stdin",
        )?;
        if path == "--cartography" {
            if args.len() != 2 {
                return Err("--cartography reads one request from stdin".into());
            }
            let mut request = Vec::new();
            io::stdin()
                .read_to_end(&mut request)
                .map_err(|e| e.to_string())?;
            return osw_query::cartography::execute(&request);
        }
        if path == "--index" {
            let file = args
                .get(2)
                .ok_or("--index needs decompressed bundle JSON")?;
            let index = osw_query::index_store::IndexStore::load(
                &fs::read(file).map_err(|e| e.to_string())?,
            )?;
            if args.len() == 3 {
                return Ok(index.metadata());
            }
            let currents = args.len() == 5 && args[3] == "--currents" && args[4] == "-";
            let eddies = args.len() == 5 && args[3] == "--eddies" && args[4] == "-";
            let nasa = args.len() == 5 && args[3] == "--nasa" && args[4] == "-";
            let release_media = args.len() == 5 && args[3] == "--release-media" && args[4] == "-";
            let memberships = args.len() == 5 && args[3] == "--state-memberships" && args[4] == "-";
            let state_context = args.len() == 5 && args[3] == "--state-context" && args[4] == "-";
            let noaa_state = args.len() == 5 && args[3] == "--noaa-state" && args[4] == "-";
            let noaa_track = args.len() == 5 && args[3] == "--noaa-track" && args[4] == "-";
            let support = args.len() == 5 && args[3] == "--support" && args[4] == "-";
            let map = args.len() == 5 && args[3] == "--map" && args[4] == "-";
            if !currents
                && !eddies
                && !nasa
                && !release_media
                && !memberships
                && !state_context
                && !noaa_state
                && !noaa_track
                && !support
                && !map
                && (args.len() != 4 || args[3] != "-")
            {
                return Err("--index BUNDLE - reads a source query from stdin".into());
            }
            let mut request = Vec::new();
            io::stdin()
                .read_to_end(&mut request)
                .map_err(|e| e.to_string())?;
            return if currents {
                index.current_view(&request)
            } else if eddies {
                index.eddy_view(&request)
            } else if nasa {
                index.nasa_view(&request)
            } else if release_media {
                index.release_media_view(&request)
            } else if memberships {
                index.state_membership_view(&request)
            } else if map {
                index.map_view(&request)
            } else if support {
                index.support_view(&request)
            } else if noaa_state {
                index.noaa_state_view(&request)
            } else if noaa_track {
                index.noaa_track_view(&request)
            } else if state_context {
                index.state_context_view(&request)
            } else {
                index.query(&request)
            };
        }
        let mut store = Store::load(&fs::read(path).map_err(|e| e.to_string())?)?;
        let mut position = 2;
        if args.get(position).map(String::as_str) == Some("--movies") {
            if args.len() != 3 {
                return Err("--movies reads a selection from stdin".into());
            }
            let mut request = Vec::new();
            io::stdin()
                .read_to_end(&mut request)
                .map_err(|e| e.to_string())?;
            return store.movie_view(&request);
        }
        if args.get(position).map(String::as_str) == Some("--object-view") {
            if args.len() != 4 {
                return Err("--object-view requires one object ID".into());
            }
            return store.object_view(
                &serde_json::to_vec(&serde_json::json!({"id":args[3]}))
                    .map_err(|e| e.to_string())?,
            );
        }
        if args.get(position).map(String::as_str) == Some("--seasons") {
            if args.len() != 3 {
                return Err("--seasons takes no additional arguments".into());
            }
            return store.seasons_snapshot();
        }
        if args.get(position).map(String::as_str) == Some("--loop-recorded") {
            if args.len() != 3 {
                return Err("--loop-recorded takes no additional arguments".into());
            }
            return store.loop_recorded_view();
        }
        if args.get(position).map(String::as_str) == Some("--atlas") {
            if args.len() != 3 {
                return Err("--atlas takes no additional arguments".into());
            }
            return store.atlas_snapshot();
        }
        if args.get(position).map(String::as_str) == Some("--dashboard-query") {
            if args.len() != 3 {
                return Err("--dashboard-query reads a request from stdin".into());
            }
            let mut request = Vec::new();
            io::stdin()
                .read_to_end(&mut request)
                .map_err(|e| e.to_string())?;
            return store.dashboard_select(&request);
        }
        if args.get(position).map(String::as_str) == Some("--dashboard") {
            if args.len() != 3 {
                return Err("--dashboard takes no additional arguments".into());
            }
            return store.dashboard_snapshot();
        }
        if args.get(position).map(String::as_str) == Some("--workspace") {
            let journal = args
                .get(position + 1)
                .ok_or("--workspace requires a journal path")?;
            store.workspace_import(&fs::read(journal).map_err(|e| e.to_string())?)?;
            position += 2;
        }
        if args.get(position).map(String::as_str) == Some("--transaction") {
            let transaction = args
                .get(position + 1)
                .ok_or("--transaction requires a JSON path")?;
            let prepared =
                store.workspace_prepare(&fs::read(transaction).map_err(|e| e.to_string())?)?;
            return output_workspace(prepared, &args, position + 2);
        }
        if args.get(position).map(String::as_str) == Some("--svg") {
            if args.len() != position + 4
                || args.get(position + 2).map(String::as_str) != Some("--output")
            {
                return Err("Use --svg QUERY.json --output NEW-MAP.svg".into());
            }
            let query = fs::read(&args[position + 1]).map_err(|e| e.to_string())?;
            let svg = store.query_svg(&query)?;
            let path = &args[position + 3];
            let mut file = fs::OpenOptions::new()
                .write(true)
                .create_new(true)
                .open(path)
                .map_err(|e| format!("Cannot create new map {path}: {e}"))?;
            file.write_all(svg.as_bytes())
                .and_then(|_| file.sync_all())
                .map_err(|e| {
                    format!("Map write failed; incomplete new file may remain at {path}: {e}")
                })?;
            return Ok(
                serde_json::json!({"ok":true,"output":path,"bytes":svg.len(),"format":"svg","bundle_sha256":store.metadata()["bundle_sha256"]}),
            );
        }
        if args.get(position).map(String::as_str) == Some("--rebase") {
            let old_path = args
                .get(position + 1)
                .ok_or("--rebase requires OLD-BUNDLE.json REQUEST.json")?;
            let request_path = args
                .get(position + 2)
                .ok_or("--rebase requires REQUEST.json")?;
            let old = Store::load(&fs::read(old_path).map_err(|e| e.to_string())?)?;
            let prepare = args.get(position + 3).map(String::as_str) == Some("--prepare");
            let result = store.workspace_rebase(
                &old,
                &fs::read(request_path).map_err(|e| e.to_string())?,
                prepare,
            )?;
            if prepare {
                return output_workspace(result, &args, position + 4);
            }
            if args.len() != position + 3 {
                return Err("Rebase preview takes no output flags; use --prepare --output for a saved journal".into());
            }
            return Ok(result);
        }
        if args.get(position).map(String::as_str) == Some("--export-workspace") {
            return output_workspace(store.workspace_export(), &args, position + 1);
        }
        if let Some(query) = args.get(position) {
            let bytes = if query == "-" {
                let mut bytes = Vec::new();
                io::stdin()
                    .read_to_end(&mut bytes)
                    .map_err(|e| e.to_string())?;
                bytes
            } else {
                fs::read(query).map_err(|e| e.to_string())?
            };
            Ok(store.execute(&bytes))
        } else {
            Ok(store.metadata())
        }
    })();
    match result {
        Ok(value) => {
            println!("{}", serde_json::to_string(&value).unwrap());
            if value["ok"] == false {
                process::exit(2);
            }
        }
        Err(error) => {
            eprintln!("{error}");
            process::exit(2);
        }
    }
}
