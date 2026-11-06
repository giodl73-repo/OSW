"""Presentation-only correction against the exact saved EAC engine manifest."""
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FILE='research/eac-mean-core-dashboard-context-revision-v1.json'
SCOPE='research/eac-mean-core-runtime-scope-v1.json'
OLD='research/eac-mean-core-engine-run-v1/engine-manifest.json'
KEY='eac_mean_core_dashboard_context_v1'
sha=lambda path:hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
read=lambda path:json.loads((ROOT/path).read_bytes())


def verify_sources(manifest):
    revision=read(FILE);scope=read(SCOPE)
    if sha(OLD)!=revision['parent_engine_manifest_sha256'] or manifest!=read(OLD):
        raise ValueError('Exact saved EAC manifest required')
    bindings=revision['bindings'];added=revision['added_asset_sha256']
    if set(bindings)!={'almanac/dashboard.js','almanac/dashboard.html'} or set(added)!={'almanac/dashboard-evidence-schema.js'}:
        raise ValueError('Only dashboard presentation assets may change')
    expected={**{p:r['candidate_sha256'] for p,r in scope['runtime_source_changes'].items()},
        **scope['added_source_sha256'],**scope['source_dependencies_sha256']}
    for path,pin in expected.items():
        if manifest['sha256'].get(path)!=pin:raise ValueError('Saved source pin differs: '+path)
        if path in bindings:
            row=bindings[path]
            if pin!=row['historical_sha256'] or sha(row['archive_path'])!=pin or sha(path)!=row['candidate_sha256']:
                raise ValueError('Dashboard source/history differs: '+path)
        elif sha(path)!=pin:raise ValueError('Scientific/runtime source changed: '+path)
    for path,row in scope['runtime_source_changes'].items():
        if sha(row['archive_path'])!=row['historical_sha256']:raise ValueError('Original runtime history differs: '+path)
    for path,pin in added.items():
        if path in manifest['sha256'] or sha(path)!=pin:raise ValueError('New dashboard helper differs')
    if any(revision.get(k) is not False for k in ['scientific_records_changed','wasm_changed','native_or_wasm_rebuild']):
        raise ValueError('Presentation-only revision required')
    return revision


def marker(revision,source_commit):
    return {'contract_file':FILE,'contract_sha256':sha(FILE),
        'parent_manifest_sha256':revision['parent_engine_manifest_sha256'],'browser_source_commit':source_commit,
        'changed_assets':sorted(set(revision['bindings'])|set(revision['added_asset_sha256'])),
        'scientific_data_changed':False,'wasm_changed':False,'native_or_wasm_rebuild':False}


def updated_manifest(manifest,source_commit):
    revision=verify_sources(manifest)
    if KEY in manifest:raise ValueError('Repeated dashboard revision refused')
    result=copy.deepcopy(manifest)
    result['sha256'].update({p:r['candidate_sha256'] for p,r in revision['bindings'].items()})
    result['sha256'].update(revision['added_asset_sha256']);result[KEY]=marker(revision,source_commit)
    verify_manifest_delta(manifest,result,source_commit)
    return result


def verify_manifest_delta(old,new,source_commit):
    revision=read(FILE)
    if set(new)!=set(old)|{KEY} or new.get(KEY)!=marker(revision,source_commit):
        raise ValueError('Unexpected dashboard manifest namespace or custody')
    expected=copy.deepcopy(new);expected.pop(KEY)
    for path,row in revision['bindings'].items():
        if expected['sha256'].get(path)!=row['candidate_sha256']:raise ValueError('Updated dashboard asset differs')
        expected['sha256'][path]=row['historical_sha256']
    for path,pin in revision['added_asset_sha256'].items():
        if expected['sha256'].pop(path,None)!=pin:raise ValueError('Added dashboard helper differs')
    if expected!=old:raise ValueError('Non-presentation manifest value changed')
