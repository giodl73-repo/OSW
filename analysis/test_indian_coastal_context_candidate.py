"""Small synthetic candidate/receipt fixtures; no complete atlas payload."""
import copy
import json
import pytest

import indian_coastal_context_candidate as candidate
from test_indian_coastal_dimension_context_v1 import contract, parent


def fixture():
    collections = parent()
    dashboard = {'schema': 'osw.motion-dashboard.v1', 'fingerprint_version': 2,
                 'entries': copy.deepcopy(collections['objects']),
                 'snapshot_fingerprint': candidate.fingerprint(collections['objects']),
                 'counts': {'named_current': 3}, 'built_at_utc': '2026-10-24T00:00:00Z'}
    raw = candidate.encoded(dashboard)
    manifest = {'baffin_latitude_gate_bound_version': '1', 'editorial_collections': ['objects'],
                'input_sha256': {candidate.DASHBOARD: candidate.digest(raw)},
                'dashboard_receipt': {'source_file': candidate.DASHBOARD,
                    'source_sha256': candidate.digest(raw), 'source_json': raw.decode()}}
    c = contract()
    c['input_sha256'] = {'research/synthetic-source.json': 'a' * 64}
    return manifest, collections, raw, c


def stage(f):
    return candidate.prepare(*f, prepared_at_utc='2026-10-24T01:00:00Z')


def test_coherent_dashboard_and_source_context_preserve_physical_inventory():
    f = fixture();before = copy.deepcopy(f)
    metadata, collections, raw, receipt = stage(f)
    assert f == before
    dashboard = json.loads(raw)
    assert dashboard['entries'] == collections['objects']
    assert dashboard['snapshot_fingerprint'] == candidate.fingerprint(collections['objects'])
    assert metadata[candidate.VERSION_KEY] == candidate.context.VERSION
    assert metadata['dashboard_receipt']['source_json'] == raw.decode()
    assert receipt['preservation']['unchanged_objects_verified'] == 1
    assert receipt['preservation']['physical_fields_and_capabilities_preserved'] is True
    assert receipt['new_rows'] == 7 and receipt['new_paired_widths'] == receipt['new_ranked_lengths'] == 0
    assert set(candidate.context.OWNER_FIELDS) <= set(metadata['editorial_collections'])


@pytest.mark.parametrize('change', ['receipt', 'snapshot', 'entries', 'counts', 'version', 'replay', 'dependency', 'editorial'])
def test_bad_parent_rejects_without_mutation(change):
    manifest, collections, raw, c = fixture()
    if change == 'receipt':manifest['dashboard_receipt']['source_sha256'] = '0' * 64
    if change in ['snapshot', 'entries', 'counts']:
        d = json.loads(raw)
        if change == 'snapshot':d['snapshot_fingerprint'] = 'changed'
        if change == 'entries':d['entries'][0]['published_length_km'] = 1000
        if change == 'counts':d['counts']['named_current'] = 106
        raw = candidate.encoded(d)
        manifest['input_sha256'][candidate.DASHBOARD] = candidate.digest(raw)
        manifest['dashboard_receipt'].update(source_sha256=candidate.digest(raw), source_json=raw.decode())
    if change == 'version':manifest['baffin_latitude_gate_bound_version'] = 'other'
    if change == 'replay':manifest[candidate.VERSION_KEY] = candidate.context.VERSION
    if change == 'dependency':manifest['input_sha256']['research/synthetic-source.json'] = 'b' * 64
    if change == 'editorial':manifest['editorial_collections'] = ['objects', 'objects']
    f = (manifest, collections, raw, c);before = copy.deepcopy(f)
    with pytest.raises(ValueError):stage(f)
    assert f == before


@pytest.mark.parametrize('collection', ['widths', 'measurements', 'geometries', 'source_arrays',
                                       'objects', 'claims', 'current_regional_reaches', 'current_cross_shore_context'])
def test_changed_parent_or_added_rows_cannot_pass_preservation(collection):
    f = fixture();_, staged, _, _ = stage(f)
    staged[collection] = copy.deepcopy(staged[collection])
    staged[collection][0]['id'] = 'changed'
    with pytest.raises(ValueError):candidate.verify_preservation(f[1], staged, f[3])


def test_physical_capability_change_cannot_hide_in_owner_update():
    f = fixture();_, staged, _, _ = stage(f)
    staged['objects'][0]['capabilities']['scoped_width'] = 1
    with pytest.raises(ValueError):candidate.verify_preservation(f[1], staged, f[3])
