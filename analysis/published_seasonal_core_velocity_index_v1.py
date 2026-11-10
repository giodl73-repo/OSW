"""Cloud-only callers extend the installed index losslessly; no artifact CLI."""
import copy
import gzip
import hashlib
import json
from current_gap_index_extension import extend
import published_seasonal_core_velocities_v1 as core

PARENT_CATALOG_SHA = "e1393726b1fa73d6adf9bfe7494ffe4077efe86c82ff2c31dbc55b63c137fbc2"
KEY = "published_seasonal_core_velocity_index_v1"
INDEX = {"almanac/index-catalog.json", "almanac/index-data.json.gz", "almanac/index-sources.json"}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n").encode()


def _extend_verified(catalog, compressed, registry, source):
    if sha(compressed) != catalog["compressed_sha256"] or len(compressed) != catalog["compressed_bytes"]:
        raise ValueError("Compressed parent index differs")
    raw = gzip.decompress(compressed)
    if sha(raw) != catalog["bundle_sha256"] or len(raw) != catalog["bundle_bytes"]:
        raise ValueError("Logical parent index differs")
    updated, corpus, next_registry, audit = extend(catalog, json.loads(raw), registry, {core.SOURCE: source})
    if (audit["replaced_source_paths"] or audit["added_source_paths"] != [core.SOURCE]
            or audit["original_source_strings_preserved"] != catalog["source_count"]):
        raise ValueError("Only one new source document permitted")
    body = encode(corpus)
    packed = gzip.compress(body, compresslevel=9, mtime=0)
    registry_raw = encode(next_registry)
    updated.update(bundle_sha256=sha(body), bundle_bytes=len(body),
                   compressed_sha256=sha(packed), compressed_bytes=len(packed))
    updated["input_sha256"] = {**updated.get("input_sha256", {}), core.SOURCE: sha(source),
                               "almanac/index-sources.json": sha(registry_raw)}
    return {"almanac/index-catalog.json": encode(updated), "almanac/index-data.json.gz": packed,
            "almanac/index-sources.json": registry_raw}, audit


def source_index(catalog_raw, compressed, registry_raw):
    if sha(catalog_raw) != PARENT_CATALOG_SHA:
        raise ValueError("Exact installed source catalog required")
    source = (core.ROOT / core.SOURCE).read_bytes()
    return _extend_verified(json.loads(catalog_raw), compressed, json.loads(registry_raw), source)


def attach(bundle, generated, audit):
    if set(generated) != INDEX or KEY in bundle["manifest"]:
        raise ValueError("Exact new source-index artifacts required once")
    if (audit["added_source_paths"] != [core.SOURCE] or audit["replaced_source_paths"]
            or audit["original_sources_verified"] != 628
            or audit["original_source_strings_preserved"] != 628):
        raise ValueError("All628 installed source strings must survive")
    if bundle["collections"].get(core.COLLECTION) != core.records():
        raise ValueError("Seasonal core estimates differ before index attachment")
    catalog = json.loads(generated["almanac/index-catalog.json"])
    if catalog["source_count"] != 629:
        raise ValueError("Unexpected source count")
    result = dict(bundle)
    result["manifest"] = copy.deepcopy(bundle["manifest"])
    result["manifest"]["input_sha256"].update({p: sha(raw) for p, raw in generated.items()})
    result["manifest"][KEY] = copy.deepcopy(audit)
    return result
