"""Small delivery fixtures; never load the complete packet or index locally."""
import copy
import json
import pytest
import current_gap_candidate_metadata as metadata

TIME = '2026-10-24T00:00:00Z'


def fixture():
    owners = [{'id': 'current:old', 'label': 'Old', 'basin': 'Ocean',
               'type': 'named_current', 'source_ids': ['source:old'],
               'linked_source_count': 1, 'dashboard_search': 'Old Ocean',
               'fingerprint': 'keep', 'section_fingerprints': {'sources': 'keep-sources'},
               'map_features': [], 'latest_observation_date': None}]
    dashboard = metadata.encoded({'schema': 'osw.motion-dashboard.v1', 'fingerprint_version': 2,
        'built_at_utc': '2026-10-20T00:00:00Z', 'entries': owners,
        'counts': {'named_current': 1}, 'connections': []})
    manifest = {'input_sha256': {metadata.DASHBOARD: metadata.digest(dashboard)},
        'taxonomy': {'node_count': 1, 'measurement_inheritance_eligible': False},
        'seasons_receipts': {'original': 'exact frozen source bytes'},
        'dashboard_receipt': {'source_file': metadata.DASHBOARD,
            'source_sha256': metadata.digest(dashboard), 'source_json': dashboard.decode()}}
    contracts = {path: metadata.encoded({'input_sha256': {'research/frozen.json': 'pin'}})
                 for path in metadata.CONTRACTS}
    added = copy.deepcopy(owners[0])
    added.update(id='current:new', label='New', dashboard_search='New Ocean', fingerprint='new')
    return manifest, {'objects': owners + [added]}, dashboard, contracts


def call(args):
    return metadata.prepare(*args, prepared_at_utc=TIME)


def test_coherent_candidate_receipts_preserve_sources_and_record_fingerprints():
    args = fixture()
    before = copy.deepcopy(args)
    manifest, raw = call(args)
    doc = json.loads(raw)
    assert args == before
    assert manifest['taxonomy']['node_count'] == 2
    assert manifest['taxonomy']['measurement_inheritance_eligible'] is False
    assert manifest['seasons_receipts'] == args[0]['seasons_receipts']
    assert manifest['current_gap_admission_version'] == metadata.VERSION
    assert manifest['dashboard_receipt']['source_json'] == raw.decode()
    assert manifest['input_sha256'][metadata.DASHBOARD] == metadata.digest(raw)
    assert doc['counts'] == {'named_current': 2}
    assert doc['entries'] == args[1]['objects']
    assert doc['entries'][0]['fingerprint'] == 'keep'
    assert doc['parent_built_at_utc'] == '2026-10-20T00:00:00Z'
    assert doc['built_at_utc'] == TIME
    assert doc['entries'][0]['latest_observation_date'] is None
    assert doc['candidate_delivery']['published'] is False
    assert set(metadata.CONTEXT_COLLECTIONS) <= set(manifest['supplemental_object_collections'])


@pytest.mark.parametrize('mutation', ['receipt', 'missing-contract', 'dependency', 'contract-cross-pin',
                                     'duplicate-owner', 'missing-owner', 'source-count', 'search'])
def test_rejects_incoherent_candidates_without_mutating_inputs(mutation):
    args = list(fixture())
    if mutation == 'receipt': args[0]['dashboard_receipt']['source_sha256'] = 'bad'
    if mutation == 'missing-contract': args[3].pop(metadata.CONTRACTS[0])
    if mutation == 'dependency': args[0]['input_sha256']['research/frozen.json'] = 'changed'
    if mutation == 'contract-cross-pin':
        args[3][metadata.CONTRACTS[-1]] = metadata.encoded({'input_sha256': {metadata.CONTRACTS[0]: 'wrong'}})
    if mutation == 'duplicate-owner': args[1]['objects'].append(copy.deepcopy(args[1]['objects'][0]))
    if mutation == 'missing-owner': args[1]['objects'].pop(0)
    if mutation == 'source-count': args[1]['objects'][0]['linked_source_count'] = 2
    if mutation == 'search': args[1]['objects'][0]['dashboard_search'] += ' alias'
    before = copy.deepcopy(args)
    with pytest.raises(ValueError): call(args)
    assert args == before


@pytest.mark.parametrize('arguments', [[], ['--cloud-candidate']])
def test_complete_export_cannot_start_in_local_workspace(monkeypatch, arguments):
    import export_current_gap_cloud_candidate as exporter
    monkeypatch.setattr('sys.argv', ['export_current_gap_cloud_candidate.py', *arguments])
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)
    def forbidden(*args):
        raise AssertionError('Local exporter reached resource or full-data work')
    monkeypatch.setattr(exporter.rehearsal, 'memory_available', forbidden)
    with pytest.raises(SystemExit) as error:
        exporter.main()
    assert error.value.code == 2
