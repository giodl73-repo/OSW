"""Bind an atlas request-lifecycle fix while retaining the verified binary and data."""
import copy
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FILE='research/current-core-dimensions-atlas-load-engine-manifest-v1.json'
ORIGINAL='06d618d3daed9d3aabfa51cb5bfd67d13b0ab36a6d0ee6290161b3840c48462a'
PATHS={'almanac/reference-routes.js','almanac/reference-routes.html'}
KEY='current_core_dimensions_atlas_load_presentation_v1'

def overlay(original,updates):
    if hashlib.sha256(original).hexdigest()!=ORIGINAL:raise ValueError('Exact verified engine manifest required')
    parent=json.loads(original)
    if set(updates)!=PATHS or KEY in parent or any(not re.fullmatch('[0-9a-f]{64}',v) for v in updates.values()):raise ValueError('Exact two presentation bindings required')
    result=copy.deepcopy(parent);result['sha256'].update(updates)
    result[KEY]={'schema':'osw.current-core-dimensions-atlas-load-presentation.v1',
        'presentation_source_parent_commit':'f7c08229a5c41e5696caacc5c2d7d03405a067b6','original_engine_manifest_sha256':ORIGINAL,
        'presentation_sha256':updates,'matching_binary_sha256':parent['sha256']['almanac/query-engine.wasm'],
        'logical_sha256':parent['published_current_core_dimensions_engine_v1']['logical_sha256'],
        'compiled_rust_and_data_inputs_changed':False,'scientific_records_changed':False,'native_or_wasm_rebuild':False}
    if {k:v for k,v in result.items() if k not in ['sha256',KEY]}!={k:v for k,v in parent.items() if k!='sha256'}:raise ValueError('Historical engine namespace changed')
    return result

if __name__=='__main__':
    original=(ROOT/'research/current-core-dimensions-delivery-run-v1/engine-manifest.json').read_bytes()
    updates={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(PATHS)}
    value=overlay(original,updates);raw=(json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode();(ROOT/FILE).write_bytes(raw)
    print(hashlib.sha256(raw).hexdigest())
