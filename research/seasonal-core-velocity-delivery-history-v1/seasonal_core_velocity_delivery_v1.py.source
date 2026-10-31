"""Pure custody and manifest rules for the next indexed-engine delivery."""
import copy
import hashlib
import json
from pathlib import Path
import re
import published_seasonal_core_velocities_v1 as core
import published_seasonal_core_velocity_index_v1 as index

ROOT = Path(__file__).resolve().parents[1]
SCOPE = "research/atlantic-ax08-core-velocity-runtime-scope-v1.json"
INVENTORY = "research/published-current-speed-delivery-compile-inventory-v1.json"
MANIFEST = "almanac/query-engine.manifest.json"
WASM = "almanac/query-engine.wasm"
PARENT_MANIFEST = "6e5f7e0b2cbe710b911c24360b57c884e905c0a8707c29877ba7b9e39aa9a8d2"
PARENT_WASM = "a59352b7e3dc875d656f3f592ff7809386b8015bfe8412b307ae359818bb3f9b"
KEY = "published_seasonal_core_velocity_delivery_v1"


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def scopes():
    scope = json.loads((ROOT / SCOPE).read_bytes())
    for path, row in scope["runtime_source_changes"].items():
        original = (ROOT / row["archive_path"]).read_bytes()
        if (digest(original) != row["historical_sha256"] or len(original) != row["bytes"]
                or digest((ROOT / path).read_bytes()) != row["candidate_sha256"]):
            raise ValueError("Runtime custody differs: " + path)
    for path, pin in {**scope["added_source_sha256"], **scope["scientific_source_sha256"]}.items():
        if digest((ROOT / path).read_bytes()) != pin:
            raise ValueError("Frozen source differs: " + path)
    return scope


def compile_inventory(parent, scope, *, catalog_sha, logical_sha):
    if (len(parent["rust_source_sha256"]) != 102 or len(parent["compile_time_data_sha256"]) != 152
            or parent["saved_candidate_logical_sha256"] != core.PARENT
            or parent["saved_candidate_catalog_sha256"] != index.PARENT_CATALOG_SHA):
        raise ValueError("Exact installed compiler inventory required")
    result = copy.deepcopy(parent)
    for path, row in scope["runtime_source_changes"].items():
        if path in result["rust_source_sha256"]:
            if result["rust_source_sha256"][path] != row["historical_sha256"]:
                raise ValueError("Historical compiler source differs")
            result["rust_source_sha256"][path] = row["candidate_sha256"]
    path = "rust/osw-query/src/published_seasonal_core_velocities.rs"
    result["rust_source_sha256"][path] = scope["added_source_sha256"][path]
    result["compile_time_data_sha256"][core.SOURCE] = scope["scientific_source_sha256"][core.SOURCE]
    result["compile_time_data_sha256"]["almanac/index-catalog.json"] = catalog_sha
    result.update(schema="osw.seasonal-core-velocity-compiled-inputs.v1", parent_logical_sha256=core.PARENT,
                  saved_candidate_logical_sha256=logical_sha, saved_candidate_catalog_sha256=catalog_sha)
    return result


def engine_manifest(parent, replacements, scope, *, generated_paths, logical_sha, wasm_sha,
                    source_commit, compiler, inventory, proof):
    if (parent.get("schema") != "osw.query-engine-manifest.v1" or KEY in parent
            or parent["sha256"].get(WASM) != PARENT_WASM
            or not re.fullmatch("[0-9a-f]{40}", source_commit)
            or not compiler.startswith("rustc 1.95.0 ")
            or not all(re.fullmatch("[0-9a-f]{64}", v) for v in [logical_sha, wasm_sha])):
        raise ValueError("Exact installed engine and compiler required")
    allowed = set(generated_paths) | set(scope["runtime_source_changes"]) | {WASM}
    required = set(scope["runtime_source_changes"]) | set(scope["added_source_sha256"]) | set(scope["scientific_source_sha256"])
    if not required <= set(replacements):
        raise ValueError("Missing source replacements")
    for path, pin in replacements.items():
        if not re.fullmatch("[0-9a-f]{64}", pin):
            raise ValueError("Malformed source hash")
        if path in parent["sha256"] and parent["sha256"][path] != pin and path not in allowed:
            raise ValueError("Unrelated installed source would change: " + path)
    for path, row in scope["runtime_source_changes"].items():
        if parent["sha256"].get(path) != row["historical_sha256"] or replacements[path] != row["candidate_sha256"]:
            raise ValueError("Runtime source rebinding")
    for path, pin in {**scope["added_source_sha256"], **scope["scientific_source_sha256"]}.items():
        if replacements[path] != pin:
            raise ValueError("Added source rebinding")
    for group in ["rust_source_sha256", "compile_time_data_sha256"]:
        if any(replacements.get(p) != pin for p, pin in inventory[group].items()):
            raise ValueError("Compiler inventory differs")
    dependencies = proof.get("production_dependencies", [])
    required_dependencies = {core.SOURCE, "rust/osw-query/src/published_seasonal_core_velocities.rs",
                             "almanac/index-catalog.json", "rust/osw-query/src/index_store.rs"}
    allowed_dependencies = set(inventory["rust_source_sha256"]) | set(inventory["compile_time_data_sha256"])
    if (not required_dependencies <= set(dependencies) or not set(dependencies) <= allowed_dependencies
            or len(dependencies) != len(set(dependencies))
            or proof.get("production_dependency_count") != len(dependencies)
            or proof.get("compiled_catalog_dependency_verified") is not True
            or proof.get("test_only_fixtures_compiled") != 0
            or inventory["saved_candidate_logical_sha256"] != logical_sha
            or inventory["saved_candidate_catalog_sha256"] != replacements["almanac/index-catalog.json"]):
        raise ValueError("Production dependency proof differs")
    result = copy.deepcopy(parent)
    result["sha256"].update(replacements)
    result["sha256"][WASM] = wasm_sha
    result["rustc"] = compiler
    result[KEY] = {"parent_engine_manifest_sha256": PARENT_MANIFEST, "parent_logical_sha256": core.PARENT,
                   "logical_sha256": logical_sha, "matching_binary_sha256": wasm_sha,
                   "previous_binary_sha256": PARENT_WASM, "source_commit": source_commit,
                   "record_count": 6, "owner_count": 3, "new_length_records": 0, "new_width_records": 0,
                   "dependency_proof": copy.deepcopy(proof)}
    if any(result[k] != parent[k] for k in parent if k not in {"sha256", "rustc"}):
        raise ValueError("Historical engine namespace changed")
    return result
