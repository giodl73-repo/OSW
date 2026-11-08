use std::{env, fs, path::PathBuf};

fn main() {
    let path = "../osw-query/src/map.rs";
    let source = fs::read_to_string(path).expect("shared display geometry source");
    let (kernel, _) = source.split_once("pub fn scene(").expect("shared display kernel boundary");
    // Reuse the original point and seam-aware path functions, without the query store.
    let kernel = kernel.lines().filter(|line| !line.starts_with("//!")).collect::<Vec<_>>().join("\n");
    fs::write(PathBuf::from(env::var("OUT_DIR").unwrap()).join("display_map.rs"), kernel).unwrap();
    println!("cargo:rerun-if-changed={path}");
    println!("cargo:rerun-if-changed=../osw-query/src/cartography.rs");
}
