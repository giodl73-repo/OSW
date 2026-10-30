"""Bind the client transport optimization to the unchanged verified engine."""
import copy
import hashlib
import json
import re

FILE='research/atlantic-nsec-reference-client-transport-engine-manifest-v1.json'
KEY='atlantic_nsec_reference_client_transport_v1'
PATHS={'almanac/query-packet.js'}
PARENT='bf958da200693e48e174ae87791473284ebcfefe3b718f66463ac5345e1792ed'


def overlay(original_raw,updates):
    if hashlib.sha256(original_raw).hexdigest()!=PARENT:
        raise ValueError('Exact verified native/WASM manifest required')
    parent=json.loads(original_raw)
    if KEY in parent or set(updates)!=PATHS or any(not re.fullmatch('[0-9a-f]{64}',v) for v in updates.values()):
        raise ValueError('Exactly one client transport binding required')
    result=copy.deepcopy(parent);result['sha256'].update(updates)
    result[KEY]={'schema':'osw.atlantic-nsec-reference-client-transport.v1',
        'original_engine_manifest_sha256':PARENT,'matching_binary_sha256':parent['sha256']['almanac/query-engine.wasm'],
        'client_transport_sha256':dict(updates),'previous_client_transport_sha256':{p:parent['sha256'][p] for p in PATHS},
        'scope':'Avoid a duplicate full JavaScript object allocation after exact packet verification. Unchanged Rust validates complete JSON, UTF-8 and bundle schema before load success.',
        'compiled_inputs_changed':False,'logical_bytes_changed':False,'native_or_wasm_rebuild':False}
    return result
