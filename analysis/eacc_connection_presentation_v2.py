"""Versioned display overlay with explicit historical-source custody."""
import copy
import json
from pathlib import Path
from eacc_connection_presentation_v1 import UI, FIGURE, MANIFEST, BASE, PARENT_MANIFEST, PACKET, WASM, digest, encoded, local_path
from eacc_connection_parent_custody_v2 import verify_parent

ROOT = Path(__file__).resolve().parents[1]
KEY = 'eacc_regional_connection_presentation_v2'
BINDINGS = 'research/eacc-connection-presentation-parent-source-bindings-v2.json'


def bindings():
    document = json.loads((ROOT/BINDINGS).read_bytes())
    if document['parent_commit'] != BASE or document['parent_manifest_sha256'] != PARENT_MANIFEST:
        raise ValueError('Changed parent source binding identity')
    return document['bindings']


def repairs():
    return {row['manifest_path']: row['installed_path_sha256'] for row in bindings()
            if row['role'] == 'existing_navigation_presentation_revision'}


def overlay(parent, ui, figure, *, control_commit):
    if (KEY in parent or UI not in parent.get('sha256', {}) or FIGURE in parent['sha256']
            or not isinstance(ui, bytes) or not ui or not isinstance(figure, bytes) or not figure
            or len(control_commit) != 40 or any(c not in '0123456789abcdef' for c in control_commit)):
        raise ValueError('Exact parent and explicit presentation identity required')
    for row in bindings():
        if parent['sha256'].get(row['manifest_path']) != row['historical_sha256']:
            raise ValueError('Parent historical pin changed')
    result = copy.deepcopy(parent)
    result['sha256'].update({UI: digest(ui), FIGURE: digest(figure), **repairs()})
    result[KEY] = {
        'base_commit': BASE, 'parent_engine_manifest_sha256': PARENT_MANIFEST,
        'control_commit': control_commit, 'changed_existing_files': [UI], 'added_files': [FIGURE],
        'preexisting_navigation_pin_repairs': repairs(),
        'historical_source_bindings_file': BINDINGS,
        'historical_source_bindings_sha256': digest((ROOT/BINDINGS).read_bytes()),
        'historical_source_archives': {r['archive_path']: r['historical_sha256'] for r in bindings()},
        'data_or_wasm_changed': False, 'native_rebuild': False, 'wasm_rebuild': False,
        'new_scientific_records': 0,
    }
    validate(parent, result)
    return result


def validate(parent, updated):
    if set(updated) != set(parent) | {KEY}:
        raise ValueError('Unexpected manifest fields')
    if any(updated[k] != v for k,v in parent.items() if k != 'sha256'):
        raise ValueError('Inherited manifest metadata changed')
    if set(updated['sha256']) != set(parent['sha256']) | {FIGURE}:
        raise ValueError('Unexpected added or removed pins')
    changed = {p for p,v in parent['sha256'].items() if updated['sha256'][p] != v}
    scope = updated[KEY]
    if (changed != {UI, *repairs()} or any(updated['sha256'][p] != v for p,v in repairs().items())
            or scope.get('changed_existing_files') != [UI] or scope.get('added_files') != [FIGURE]
            or scope.get('preexisting_navigation_pin_repairs') != repairs()
            or scope.get('historical_source_bindings_file') != BINDINGS
            or scope.get('historical_source_bindings_sha256') != digest((ROOT/BINDINGS).read_bytes())
            or scope.get('historical_source_archives') != {r['archive_path']: r['historical_sha256'] for r in bindings()}
            or scope.get('base_commit') != BASE or scope.get('parent_engine_manifest_sha256') != PARENT_MANIFEST
            or type(scope.get('new_scientific_records')) is not int or scope['new_scientific_records'] != 0
            or any(scope.get(k) is not False for k in ['data_or_wasm_changed','native_rebuild','wasm_rebuild'])):
        raise ValueError('Presentation overlay exceeded registered scope')


def verify_files(site, manifest):
    view = copy.deepcopy(manifest)
    if KEY in manifest:
        scope = manifest[KEY]
        if scope['historical_source_bindings_sha256'] != digest((ROOT/BINDINGS).read_bytes()):
            raise ValueError('Changed historical source registry')
        if scope['preexisting_navigation_pin_repairs'] != repairs():
            raise ValueError('Changed navigation pin repairs')
        for row in bindings():
            path = row['manifest_path']
            if row['role'] == 'existing_navigation_presentation_revision':
                if manifest['sha256'][path] != row['installed_path_sha256']:
                    raise ValueError('Changed actual HTML presentation pin')
                # The parent verifier checks both archived and active bytes.
                view['sha256'][path] = row['historical_sha256']
    return verify_parent(site, ROOT, view, bindings())
