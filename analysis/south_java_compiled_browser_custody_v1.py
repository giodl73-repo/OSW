"""Verify the exact declared compiled-engine overlay before browser admission."""
import json

from south_java_catalog_engine_v1 import overlay
from south_java_model_delivery_v1 import sha


def verify(parent_raw, manifest_raw, wasm_sha, wasm_bytes, result, inventory, scope):
    if (result.get('status') != 'PASS' or result.get('main_query_responses_equal') != 11
            or result.get('source_query_responses_equal') != 3
            or result.get('native_and_wasm_mismatched_corpus_refused') is not True):
        raise ValueError('Complete matching-catalog API proof required')
    parent_sha = sha(parent_raw)
    if parent_sha != result['restoration']['parent_manifest_sha256']:
        raise ValueError('Saved parent engine identity differs')
    if wasm_sha != result['wasm_sha256'] or wasm_bytes != result['wasm_bytes']:
        raise ValueError('Compiled engine binary differs from verified build')
    if sha(manifest_raw) != result['engine_manifest_sha256']:
        raise ValueError('Compiled engine manifest differs from verified build')
    expected = overlay(json.loads(parent_raw), inventory, scope, wasm_sha256=wasm_sha,
                       compiler=result['compiler'], parent_manifest_sha256=parent_sha,
                       dependency_proof=result['dependency_proof'])
    encoded = (json.dumps(expected, indent=2, allow_nan=False) + '\n').encode()
    if manifest_raw != encoded:
        raise ValueError('Compiled manifest exceeds the declared source/data/binary overlay')
    return {'compiled_wasm_sha256': wasm_sha, 'compiled_wasm_bytes': wasm_bytes,
            'compiled_manifest_sha256': sha(manifest_raw), 'saved_parent_manifest_sha256': parent_sha,
            'declared_manifest_overlay_recomputed': True,
            'main_and_source_api_proofs_verified': True,
            'compiled_catalog_guard_preserved': True}
