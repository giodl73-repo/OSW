"""Bounded custody checks for the saved derived candidate; no data generation."""
import hashlib
import json
from pathlib import Path
import stat

from query_packet import descriptors
from south_java_model_delivery_v1 import DOCUMENTS, WASM, WASM_SHA


def members(infos, expected):
    files = [info for info in infos if not info.is_dir()]
    if len(set(expected)) != len(expected) or len(infos) > 64 or len(files) != len(expected) or {info.filename for info in files} != set(expected):
        raise ValueError('Unexpected saved-candidate archive inventory')
    for info in infos:
        name = info.filename
        if ('\\' in name or ':' in name or name.startswith('/')
                or any(part in ('', '.', '..') for part in name.rstrip('/').split('/'))
                or stat.S_ISLNK(info.external_attr >> 16)):
            raise ValueError('Unsafe saved-candidate member')
        if info.is_dir() and not any(path.startswith(name) for path in expected):
            raise ValueError('Unexpected archive directory')
        if not info.is_dir() and not 0 < info.file_size <= 201326592:
            raise ValueError('Saved file exceeded budget')
    if sum(info.file_size for info in files) > 402653184:
        raise ValueError('Saved candidate exceeded expanded-byte budget')
    return files


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify(root, result):
    root = Path(root).resolve()
    for path, expected in result['generated_sha256'].items():
        if path not in result['artifact_paths'] or digest(root / path) != expected:
            raise ValueError('Saved generated-file hash mismatch: ' + path)
    packet = json.loads((root / 'almanac/query-data.json').read_bytes())
    if packet['logical_sha256'] != result['logical_sha256'] or packet['logical_byte_length'] != result['logical_bytes']:
        raise ValueError('Saved logical candidate identity changed')
    logical = hashlib.sha256()
    total = 0
    parts = descriptors(packet)
    for part in parts:
        path = root / 'almanac' / part['path']
        if path.is_symlink() or path.stat().st_size != part['byte_length']:
            raise ValueError('Saved part size/address changed')
        part_hash = hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1048576), b''):
                part_hash.update(chunk); logical.update(chunk); total += len(chunk)
        if part_hash.hexdigest() != part['sha256']:
            raise ValueError('Saved part hash changed')
    if total != result['logical_bytes'] or logical.hexdigest() != result['logical_sha256']:
        raise ValueError('Saved logical candidate bytes changed')
    if digest(root / WASM) != WASM_SHA:
        raise ValueError('Installed WASM binary differs from verified saved engine')
    engine = json.loads((root / 'almanac/query-engine.manifest.json').read_bytes())
    if engine['sha256'][WASM] != WASM_SHA:
        raise ValueError('Engine manifest changed compiled identity')
    # Each manifest pin must agree with its actual source or generated file.
    # Older content-addressed parts are preserved and need no download/rebuild.
    required = set(result['generated_sha256']) - {'almanac/query-engine.manifest.json'}
    required |= {'almanac/' + part['path'] for part in parts}
    required |= {'almanac/query.js', 'almanac/model-section-card.js',
                 'figures/south-java-iskandar-2006-layer-context-v1.svg'}
    required |= DOCUMENTS
    for path in required:
        if digest(root / path) != engine['sha256'].get(path):
            raise ValueError('Candidate engine/source pin mismatch: ' + path)
    return {'logical_sha256': logical.hexdigest(), 'logical_bytes': total,
            'verified_packet_parts': len(parts), 'saved_wasm_sha256': WASM_SHA,
            'full_packet_parsed': False, 'source_index_decompressed_in_python': False}
