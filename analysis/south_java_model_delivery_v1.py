"""Pure delivery projections: preserve scientific rows, extend generated custody."""
import copy
import gzip
import hashlib
import json
import re

from current_gap_index_extension import extend
from query_packet import descriptors

DASHBOARD = 'research/ocean-motion-dashboard.json'
INDEX = {'almanac/index-catalog.json', 'almanac/index-sources.json', 'almanac/index-data.json.gz'}
GENERATED = INDEX | {DASHBOARD, 'almanac/query-data.json'}
UI = {'almanac/query.js', 'almanac/model-section-card.js'}
DOCUMENTS = {'research/south-java-iskandar-2006-layer-source-facts-v1.json',
             'research/south-java-iskandar-2006-layer-figure-v1.json',
             'research/south-java-model-layer-query-contract-v1.json'}
FIGURE = 'figures/south-java-iskandar-2006-layer-context-v1.svg'
WASM = 'almanac/query-engine.wasm'
WASM_SHA = '75f57569b3bcc175bf31d66a50791718b0fa53f2165fafdcb23f528282ce64db'
PROVENANCE = 'south_java_model_delivery_v1'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False,
                       separators=(',', ':')) + '\n').encode()


def source_index(catalog, compressed, registry, documents, dashboard_raw):
    """The caller supplies cloud bytes; this function opens no files."""
    if set(documents) != DOCUMENTS:
        raise ValueError('Exact South Java source-document set required')
    if sha(compressed) != catalog['compressed_sha256']:
        raise ValueError('Changed compressed parent source index')
    raw = gzip.decompress(compressed)
    if sha(raw) != catalog['bundle_sha256'] or len(raw) != catalog['bundle_bytes']:
        raise ValueError('Changed logical parent source index')
    additions = {**documents, DASHBOARD: dashboard_raw}
    updated, corpus, registry, audit = extend(catalog, json.loads(raw), registry, additions)
    if set(audit['replaced_source_paths']) - {DASHBOARD}:
        raise ValueError('Unexpected historical source replacement')
    raw = encoded(corpus)
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    registry_raw = encoded(registry)
    updated.update(bundle_sha256=sha(raw), compressed_sha256=sha(compressed),
                   bundle_bytes=len(raw), compressed_bytes=len(compressed))
    updated['input_sha256'] = {**updated.get('input_sha256', {}),
                              **{path: sha(body) for path, body in additions.items()},
                              'almanac/index-sources.json': sha(registry_raw)}
    generated = {'almanac/index-catalog.json': encoded(updated),
                 'almanac/index-sources.json': registry_raw,
                 'almanac/index-data.json.gz': compressed}
    return generated, audit


def packet_manifest(parent, generated, documents, *, verified_candidate_sha, index_audit):
    if set(generated) != INDEX or set(documents) != DOCUMENTS or PROVENANCE in parent:
        raise ValueError('Exact generated indexes and unmodified candidate manifest required')
    if not re.fullmatch('[0-9a-f]{64}', verified_candidate_sha):
        raise ValueError('Verified native candidate identity required')
    result = copy.deepcopy(parent)
    updates = {**generated, **documents}
    result['input_sha256'] = {**parent['input_sha256'], **{path: sha(raw) for path, raw in updates.items()}}
    result[PROVENANCE] = {'schema': 'osw.south-java-model-delivery.v1',
                          'verified_temporary_candidate_sha256': verified_candidate_sha,
                          'index_audit': copy.deepcopy(index_audit),
                          'new_physical_dimensions_admitted': 0,
                          'scientific_source_processing': False,
                          'saved_wasm_sha256': WASM_SHA}
    return result


def engine_manifest(parent, replacements, packet, *, source_commit):
    """Refresh only declared generated/UI pins; preserve the existing binary."""
    if (parent.get('schema') != 'osw.query-engine-manifest.v1' or parent.get('abi_version') != 1
            or parent.get('sha256', {}).get(WASM) != WASM_SHA or PROVENANCE in parent
            or not re.fullmatch('[0-9a-f]{40}', source_commit)):
        raise ValueError('Verified installed engine and exact source commit required')
    parts = {'almanac/' + part['path']: part['sha256'] for part in descriptors(packet)}
    required = GENERATED | UI | DOCUMENTS | {FIGURE} | set(parts)
    if set(replacements) != required or any(not re.fullmatch('[0-9a-f]{64}', value) for value in replacements.values()):
        raise ValueError('Unexpected generated/source/UI pin set')
    for path, expected in parts.items():
        if replacements[path] != expected:
            raise ValueError('Packet part pin disagrees with descriptor')
    for path in DOCUMENTS | {FIGURE} | set(parts):
        if path in parent['sha256'] and parent['sha256'][path] != replacements[path]:
            raise ValueError('Existing source or content-addressed part would change: ' + path)
    result = copy.deepcopy(parent)
    result['sha256'].update(replacements)
    result[PROVENANCE] = {'schema': 'osw.south-java-model-engine-overlay.v1',
                          'source_commit': source_commit,
                          'changed_or_added_pin_paths': sorted(path for path, value in replacements.items()
                                                              if parent['sha256'].get(path) != value),
                          'wasm_rebuilt': False, 'scientific_source_processing': False}
    if result['sha256'][WASM] != parent['sha256'][WASM]:
        raise ValueError('Installed engine binary changed')
    return result
