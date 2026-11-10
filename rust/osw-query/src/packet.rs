//! Transport manifests do not change logical bundle/workspace identity.
use serde::Deserialize;
use sha2::{Digest, Sha256};
use std::path::Path;

const LIMIT: usize = 16 * 1024 * 1024;
#[derive(Deserialize)]
struct Schema {
    schema: String,
}
#[derive(Deserialize)]
struct Part {
    index: usize,
    path: String,
    byte_length: usize,
    sha256: String,
}
#[derive(Deserialize)]
struct Packet {
    logical_schema: String,
    hash_algorithm: String,
    logical_sha256: String,
    logical_byte_length: usize,
    part_byte_limit: usize,
    parts: Vec<Part>,
}
fn hash(raw: &[u8]) -> String {
    format!("{:x}", Sha256::digest(raw))
}
fn pin(s: &str) -> bool {
    s.len() == 64
        && s.bytes()
            .all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b))
}

pub fn assemble<F>(raw: Vec<u8>, mut read: F) -> Result<Vec<u8>, String>
where
    F: FnMut(&str) -> Result<Vec<u8>, String>,
{
    let root: Schema = serde_json::from_slice(&raw).map_err(|e| e.to_string())?;
    if root.schema == "osw.query-bundle.v1" {
        return Ok(raw);
    }
    if root.schema != "osw.query-packet.v1" {
        return Err("Unsupported query packet".into());
    }
    let p: Packet = serde_json::from_slice(&raw).map_err(|e| e.to_string())?;
    if p.logical_schema != "osw.query-bundle.v1"
        || p.hash_algorithm != "sha256"
        || p.part_byte_limit != LIMIT
        || !pin(&p.logical_sha256)
        || p.logical_byte_length == 0
        || p.parts.len() != p.logical_byte_length.div_ceil(LIMIT)
    {
        return Err("Invalid query packet size or schema".into());
    }
    // Validate every descriptor before reading any path or reserving the payload.
    for (i, part) in p.parts.iter().enumerate() {
        if part.index != i
            || !pin(&part.sha256)
            || part.path != format!("query-parts/{i:06}-{}.bin", part.sha256)
            || part.byte_length != LIMIT.min(p.logical_byte_length - i * LIMIT)
        {
            return Err("Invalid query packet part".into());
        }
    }
    let mut result = Vec::new();
    for part in p.parts {
        let chunk = read(&part.path)?;
        if chunk.len() != part.byte_length || hash(&chunk) != part.sha256 {
            return Err("Changed query packet part".into());
        }
        result.extend_from_slice(&chunk);
    }
    if result.len() != p.logical_byte_length || hash(&result) != p.logical_sha256 {
        return Err("Changed logical query bundle".into());
    }
    let logical: Schema = serde_json::from_slice(&result).map_err(|e| e.to_string())?;
    if logical.schema != p.logical_schema {
        return Err("Wrong logical query schema".into());
    }
    Ok(result)
}

pub fn read_bundle(path: impl AsRef<Path>) -> Result<Vec<u8>, String> {
    let path = path.as_ref();
    let parent = path
        .parent()
        .filter(|parent| !parent.as_os_str().is_empty())
        .unwrap_or(Path::new("."))
        .canonicalize()
        .map_err(|e| e.to_string())?;
    assemble(
        std::fs::read(path).map_err(|e| e.to_string())?,
        |relative| {
            let target = parent
                .join(relative)
                .canonicalize()
                .map_err(|e| e.to_string())?;
            if !target.starts_with(&parent) {
                return Err("Query part leaves bundle directory".into());
            }
            std::fs::read(target).map_err(|e| e.to_string())
        },
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    fn manifest(raw: &[u8]) -> Vec<u8> {
        let pin = hash(raw);
        serde_json::to_vec(&json!({"schema":"osw.query-packet.v1","logical_schema":"osw.query-bundle.v1",
            "hash_algorithm":"sha256","logical_sha256":pin,"logical_byte_length":raw.len(),"part_byte_limit":LIMIT,
            "parts":[{"index":0,"path":format!("query-parts/000000-{pin}.bin"),"byte_length":raw.len(),"sha256":pin}]})).unwrap()
    }
    #[test]
    fn legacy_and_verified_parts_preserve_bytes() {
        let raw = b"{\"schema\":\"osw.query-bundle.v1\"}\r\n";
        assert_eq!(
            assemble(raw.to_vec(), |_| panic!("legacy must not fetch")).unwrap(),
            raw
        );
        assert_eq!(assemble(manifest(raw), |_| Ok(raw.to_vec())).unwrap(), raw);
        assert!(assemble(manifest(raw), |_| Ok(b"changed".to_vec())).is_err());
        assert!(assemble(manifest(raw), |_| Err("missing".into())).is_err());
    }
    #[test]
    fn malformed_descriptors_never_read_paths() {
        let raw = b"{\"schema\":\"osw.query-bundle.v1\"}";
        for field in ["path", "index", "byte_length", "sha256"] {
            let mut m: serde_json::Value = serde_json::from_slice(&manifest(raw)).unwrap();
            m["parts"][0][field] = json!("../outside");
            assert!(
                assemble(serde_json::to_vec(&m).unwrap(), |_| panic!(
                    "invalid descriptor fetched"
                ))
                .is_err()
            );
        }
        let mut m: serde_json::Value = serde_json::from_slice(&manifest(raw)).unwrap();
        m["logical_sha256"] = json!("0".repeat(64));
        assert!(assemble(serde_json::to_vec(&m).unwrap(), |_| Ok(raw.to_vec())).is_err());
    }
}
