"""Bind three reviewed presentation assets to the verified strict UTF-8 engine."""
import copy
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
FILE='research/current-query-map-focus-engine-manifest-v1.json'
KEY='current_query_map_focus_presentation_v1'
PATHS={'almanac/query.js','almanac/query.html','almanac/reference-routes.html'}
PARENT='75047c79e372694c63a69cf99fb57db8a89bfba7f5dd4c4d475f33d7c73f5722'
BINARY='8b2f63c2c643b5c15b51865678b1a0f496a169a9c95c1b770990f47d9d760edc'


def overlay(original_raw,updates):
    if hashlib.sha256(original_raw).hexdigest()!=PARENT:
        raise ValueError('Exact verified strict UTF-8 engine manifest required')
    parent=json.loads(original_raw)
    if parent['sha256']['almanac/query-engine.wasm']!=BINARY or KEY in parent:
        raise ValueError('Wrong or already presented engine')
    if set(updates)!=PATHS or any(not re.fullmatch('[0-9a-f]{64}',v) for v in updates.values()):
        raise ValueError('Exactly three reviewed presentation bindings required')
    result=copy.deepcopy(parent);result['sha256'].update(updates)
    result[KEY]={'schema':'osw.current-query-map-focus-presentation.v1',
        'original_engine_manifest_sha256':PARENT,'matching_binary_sha256':BINARY,
        'presentation_sha256':dict(updates),'previous_presentation_sha256':{p:parent['sha256'][p] for p in sorted(PATHS)},
        'scope':'Keep the focused map mark announcement stable against a competing hover; explicit pointer activation transfers focus. Preserve readable atlas preview labels and desktop width-table columns. No measurement or geometry changes.',
        'compiled_inputs_changed':False,'logical_bytes_changed':False,'native_or_wasm_rebuild':False}
    return result


def bind_client_manifest(original_raw):
    updates={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(PATHS)}
    raw=(ROOT/FILE).read_bytes()
    if json.loads(raw)!=overlay(original_raw,updates):
        raise ValueError('Reviewed presentation differs from saved engine or source assets')
    return raw,sorted(PATHS)
