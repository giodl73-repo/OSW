"""Presentation-only revision of a saved engine manifest; no scientific rebinding."""
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FILE='research/wicc-reference-card-context-revision-v1.json'
SCOPE='research/wicc-winter-reference-runtime-scope-v2.json'
OLD='research/wicc-reference-engine-run-v1/engine-manifest.json'
KEY='wicc_reference_card_context_v1'

def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def read(path):return json.loads((ROOT/path).read_bytes())

def verify_sources(manifest):
    revision=read(FILE);scope=read(SCOPE)
    if sha(OLD)!=revision['parent_engine_manifest_sha256'] or manifest!=read(OLD):
        raise ValueError('Exact saved manifest required')
    bindings=revision['bindings']
    if set(bindings)!={'almanac/reference-route-text.js','almanac/reference-routes.js','almanac/reference-routes.html'}:
        raise ValueError('Only three presentation assets may change')
    expected={**{p:r['candidate_sha256'] for p,r in scope['runtime_source_changes'].items()},
              **scope['added_source_sha256'],**scope['source_dependencies_sha256']}
    for path,pin in expected.items():
        if manifest['sha256'].get(path)!=pin:raise ValueError('Saved source pin differs: '+path)
        if path in bindings:
            r=bindings[path]
            if pin!=r['historical_sha256'] or sha(r['archive_path'])!=pin or sha(path)!=r['candidate_sha256']:
                raise ValueError('Presentation source/history differs: '+path)
        elif sha(path)!=pin:raise ValueError('Scientific/runtime dependency changed: '+path)
    for path,r in scope['runtime_source_changes'].items():
        if sha(r['archive_path'])!=r['historical_sha256']:raise ValueError('Original runtime history differs')
    if not all(revision[k] is False for k in ['scientific_records_changed','wasm_changed','native_or_wasm_rebuild']):
        raise ValueError('Presentation-only scope required')
    return revision

def updated_manifest(manifest,source_commit):
    revision=verify_sources(manifest);updated=copy.deepcopy(manifest)
    if KEY in manifest:raise ValueError('Refuse repeated presentation revision')
    for path,r in revision['bindings'].items():updated['sha256'][path]=r['candidate_sha256']
    updated[KEY]={'contract_file':FILE,'contract_sha256':sha(FILE),
        'parent_manifest_sha256':revision['parent_engine_manifest_sha256'],'browser_source_commit':source_commit,
        'changed_assets':sorted(revision['bindings']),'scientific_data_changed':False,'wasm_changed':False,
        'native_or_wasm_rebuild':False}
    verify_manifest_delta(manifest,updated,source_commit)
    return updated

def verify_manifest_delta(old,new,source_commit):
    revision=read(FILE);expected=copy.deepcopy(new)
    if set(new)!=set(old)|{KEY}:raise ValueError('Unexpected manifest namespace')
    marker=expected.pop(KEY)
    if (marker.get('browser_source_commit')!=source_commit or marker.get('contract_sha256')!=sha(FILE)
            or marker.get('parent_manifest_sha256')!=revision['parent_engine_manifest_sha256']
            or marker.get('changed_assets')!=sorted(revision['bindings'])
            or any(marker.get(k) is not False for k in ['scientific_data_changed','wasm_changed','native_or_wasm_rebuild'])):
        raise ValueError('Presentation custody differs')
    for path,r in revision['bindings'].items():
        if expected['sha256'].get(path)!=r['candidate_sha256']:raise ValueError('Updated asset pin differs')
        expected['sha256'][path]=r['historical_sha256']
    if expected!=old:raise ValueError('Non-presentation manifest value changed')
