"""Presentation overlay for the existing EACC source-context record."""
import copy
from indian_coastal_card_presentation_v1 import digest, encoded, local_path, verify_files

UI = 'almanac/current-source-evidence-ui.js'
FIGURE = 'figures/eacc-regional-connection-v1.svg'
MANIFEST = 'almanac/query-engine.manifest.json'
KEY = 'eacc_regional_connection_presentation_v1'
BASE = '1d98d9768959f1a357f3aa9933b86f203a4290bd'
PARENT_MANIFEST = '61a430e3db980104bfe6ec80a08192d04d00d9742d4a68b6276421a93bb04a63'
PACKET = '93c7c184e547ad0c2801ff2183cc5f88f2e11f6150b69b7583fc2f0db05ab696'
WASM = '969930518d3f64a95699f4f7ed0335d96b01e13639d1bb5eb4498bfaf1cc1a17'


def overlay(parent, ui, figure, *, control_commit):
    if (KEY in parent or UI not in parent.get('sha256', {}) or FIGURE in parent['sha256']
            or not isinstance(ui, bytes) or not ui or not isinstance(figure, bytes) or not figure
            or not isinstance(control_commit, str) or len(control_commit) != 40
            or any(c not in '0123456789abcdef' for c in control_commit)):
        raise ValueError('Exact preceding manifest and new presentation identity required')
    updated = copy.deepcopy(parent)
    updated['sha256'][UI] = digest(ui)
    updated['sha256'][FIGURE] = digest(figure)
    updated[KEY] = {
        'base_commit': BASE, 'parent_engine_manifest_sha256': PARENT_MANIFEST,
        'control_commit': control_commit, 'changed_existing_paths': [UI],
        'added_paths': [FIGURE], 'data_or_wasm_changed': False,
        'native_rebuild': False, 'wasm_rebuild': False, 'new_scientific_records': 0,
    }
    validate(parent, updated)
    return updated


def validate(parent, updated):
    if set(updated) != set(parent) | {KEY}:
        raise ValueError('Unexpected manifest fields')
    for key in parent:
        if key != 'sha256' and updated[key] != parent[key]:
            raise ValueError('Changed inherited manifest field: '+key)
    if set(updated['sha256']) != set(parent['sha256']) | {FIGURE}:
        raise ValueError('Unexpected added or removed assets')
    changed = {p for p,h in parent['sha256'].items() if updated['sha256'][p] != h}
    scope = updated[KEY]
    if (changed != {UI} or scope.get('changed_existing_paths') != [UI]
            or scope.get('added_paths') != [FIGURE]
            or any(scope.get(k) is not False for k in ['data_or_wasm_changed','native_rebuild','wasm_rebuild'])
            or type(scope.get('new_scientific_records')) is not int or scope['new_scientific_records'] != 0
            or scope.get('base_commit') != BASE or scope.get('parent_engine_manifest_sha256') != PARENT_MANIFEST):
        raise ValueError('Overlay exceeded presentation scope')
