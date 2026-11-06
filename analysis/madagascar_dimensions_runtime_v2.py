"""Revised source scope for the exact missing seasonal validation join."""
import madagascar_dimensions_runtime_v1 as previous

query=previous.query
index=previous.index
ROOT=previous.ROOT
PARENT_MANIFEST=previous.PARENT_MANIFEST
PARENT_WASM=previous.PARENT_WASM
SCOPE='research/madagascar-dimensions-runtime-scope-v2.json'
verify_collections=previous.verify_collections
dashboard_document=previous.dashboard_document
verify_snapshot=previous.verify_snapshot

def scopes():
    scope=query.read(SCOPE)
    if query.sha(scope['parent_engine_manifest_file'])!=PARENT_MANIFEST:raise ValueError('Installed source receipt differs')
    for path,row in scope['runtime_source_changes'].items():
        if query.sha(path)!=row['candidate_sha256'] or query.sha(row['archive_path'])!=row['historical_sha256']:
            raise ValueError('Changed revised runtime source/history: '+path)
    for path,pin in {**scope['added_source_sha256'],**scope['source_dependencies_sha256'],**scope['candidate_rust_source_sha256']}.items():
        if query.sha(path)!=pin:raise ValueError('Changed revised frozen source: '+path)
    for path,row in scope['failed_candidate_source_bindings'].items():
        if query.sha(row['archive_path'])!=row['failed_candidate_sha256']:raise ValueError('Changed failed execution source: '+path)
    return scope
