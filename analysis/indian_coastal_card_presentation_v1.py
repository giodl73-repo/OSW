"""Bound a display-only overlay to an unchanged, previously validated engine."""
import copy
import hashlib
import json
from pathlib import Path

UI = 'almanac/current-source-evidence-ui.js'
MANIFEST = 'almanac/query-engine.manifest.json'
COVERAGE_FIELDS = ['id', 'label', 'type', 'identity_level', 'basin', 'measurement_ids', 'width_ids', 'width_sample_ids',
                   'route_ids', 'published_length_km', 'latest_observation_date', 'capabilities']


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def local_path(root, relative):
    if (not isinstance(relative, str) or '\\' in relative or ':' in relative
            or any(part in ('', '.', '..') for part in relative.split('/'))):
        raise ValueError('Invalid saved-engine source path')
    root = Path(root).resolve()
    target = (root / relative).resolve()
    if not target.is_relative_to(root):raise ValueError('Saved-engine path leaves site')
    return target


def verify_files(root, manifest):
    if (manifest.get('schema') != 'osw.query-engine-manifest.v1'
            or manifest.get('engine') != 'rust-osw-query-v1' or manifest.get('abi_version') != 1
            or not isinstance(manifest.get('sha256'), dict)):
        raise ValueError('Unsupported saved engine manifest')
    pins = manifest['sha256']
    if not {UI, 'almanac/query-engine.wasm', 'almanac/query-data.json',
            'almanac/index-catalog.json', 'almanac/index-data.json.gz'} <= set(pins):
        raise ValueError('Saved engine omitted required data/UI pins')
    for path, expected in pins.items():
        target = local_path(root, path)
        actual = hashlib.sha256()
        with target.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):actual.update(chunk)
        if actual.hexdigest() != expected:raise ValueError('Saved engine/source/data changed: ' + path)


def overlay_manifest(parent, ui_raw, *, parent_manifest_sha, source_run_id, control_commit):
    """Only one display file may change; all data and compiled code pins survive."""
    if (not isinstance(parent.get('sha256'), dict) or UI not in parent['sha256']
            or not isinstance(ui_raw, bytes) or not ui_raw
            or len(parent_manifest_sha) != 64 or type(source_run_id) is not int
            or source_run_id <= 0 or len(control_commit) != 40 or 'presentation_adjustment' in parent):
        raise ValueError('Unmodified source engine and explicit presentation identity required')
    result = copy.deepcopy(parent)
    result['sha256'][UI] = digest(ui_raw)
    if result['sha256'][UI] == parent['sha256'][UI]:raise ValueError('No display change to validate')
    result['presentation_adjustment'] = {
        'schema': 'osw.indian-coastal-card-presentation.v1',
        'parent_engine_manifest_sha256': parent_manifest_sha,
        'source_run_id': source_run_id, 'presentation_control_commit': control_commit,
        'changed_source_paths': [UI], 'scientific_source_recomputation': False,
        'native_rebuild': False, 'wasm_rebuild': False,
    }
    validate_overlay(parent, result)
    return result


def validate_overlay(parent, updated):
    adjustment = updated.get('presentation_adjustment', {})
    if (set(updated) != set(parent) | {'presentation_adjustment'}
            or any(updated[key] != value for key, value in parent.items() if key != 'sha256')
            or set(updated['sha256']) != set(parent['sha256'])
            or [path for path, sha in parent['sha256'].items() if updated['sha256'][path] != sha] != [UI]
            or adjustment.get('changed_source_paths') != [UI]
            or any(adjustment.get(key) is not False for key in
                   ['scientific_source_recomputation', 'native_rebuild', 'wasm_rebuild'])):
        raise ValueError('Presentation overlay changed compiled code, data or source scope')


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + '\n').encode()
