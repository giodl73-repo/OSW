"""Prepared query admission preserves dimensions and rejects partial joins."""
import copy
import json
from urllib.parse import parse_qs, urlsplit

import pytest

import brazil_regional_reach_query as admission


@pytest.fixture(scope='module')
def contract():
    return admission.evidence()[0]


def fixture():
    return {'objects': [{'id': admission.ENTITY, 'source_ids': ['source:existing'], 'linked_source_count': 1}],
            'sources': [{'id': 'source:existing'}], 'claims': [],
            'measurements': [{'id': 'old', 'value': 17}],
            'widths': [{'id': 'old-width', 'value': [30, 50]}],
            'length_assessments': [{'id': 'length:brazil', 'length_km': None}],
            'ranked_currents': [{'id': 'current:elsewhere', 'length_km': 500}]}


def test_admission_adds_only_four_records_and_retains_source_semantics(contract):
    data = fixture(); before = copy.deepcopy(data)
    admission.append(data, contract)
    for field in ['measurements', 'widths', 'length_assessments', 'ranked_currents']:
        assert data[field] == before[field]
    assert len(data[admission.COLLECTION]) == 1
    assert len(data['claims']) == 1 and len(data['sources']) == 3
    record = data[admission.COLLECTION][0]; c = record['constraint']
    assert c['reported_value_km'] == 1500 and c['relation'] == 'source_reported_value'
    assert c['study_window'] is None and c['reported_uncertainty_km'] is None
    assert c['whole_current_length_km'] is None and c['physical_length_lower_bound_km'] is None
    assert c['rank_eligible'] is False and record['physical_width_admitted'] is False
    owner = data['objects'][0]
    assert owner['regional_reach_ids'] == [admission.ID]
    assert owner['source_ids'] == sorted(['source:existing', admission.SOURCE_ID, admission.METHOD_ID])
    assert owner['linked_source_count'] == len(owner['source_ids']) == 3
    assert data['claims'][0]['value'] == c
    assert data['claims'][0]['observation_window'] is None
    assert data['claims'][0]['publication_year'] is None
    assert data['claims'][0]['chapter_pdf_version_month'] == '2002-09'


@pytest.mark.parametrize('failure', ['no_owner', 'two_owners', 'bad_source_ids', 'bad_reach_ids',
                                      'duplicate_join', 'duplicate_method', 'duplicate_claim',
                                      'duplicate_reach', 'duplicate_source_refs', 'orphan_source',
                                      'bad_count', 'bool_count', 'float_count', 'duplicate_existing_source'])
def test_rejections_precede_every_mutation(contract, failure):
    data = fixture(); owner = data['objects'][0]
    if failure == 'no_owner': data['objects'].clear()
    elif failure == 'two_owners': data['objects'].append(copy.deepcopy(owner))
    elif failure == 'bad_source_ids': owner['source_ids'] = 'invalid'
    elif failure == 'bad_reach_ids': owner['regional_reach_ids'] = [42]
    elif failure == 'duplicate_join': owner['regional_reach_ids'] = [admission.ID]
    elif failure == 'duplicate_method': data['sources'].append(copy.deepcopy(contract['method_source']))
    elif failure == 'duplicate_claim': data['claims'].append(copy.deepcopy(contract['claim']))
    elif failure == 'duplicate_reach': data[admission.COLLECTION] = [copy.deepcopy(contract['record'])]
    elif failure == 'duplicate_source_refs': owner['source_ids'].append('source:existing')
    elif failure == 'orphan_source': data['sources'].clear()
    elif failure == 'bad_count': owner['linked_source_count'] = 99
    elif failure == 'bool_count': owner['linked_source_count'] = True
    elif failure == 'float_count': owner['linked_source_count'] = 1.0
    else: data['sources'].append({'id': 'source:existing'})
    before = copy.deepcopy(data)
    with pytest.raises(ValueError): admission.append(data, contract)
    assert data == before


@pytest.mark.parametrize('field,value', [('whole_current_length_admitted', True),
                                       ('physical_width_admitted', True),
                                       ('annual_or_seasonal_range_admitted', True)])
def test_changed_contract_rejects_atomically(contract, field, value):
    changed = copy.deepcopy(contract); changed['record'][field] = value
    data = fixture(); before = copy.deepcopy(data)
    with pytest.raises(ValueError, match='Unverified'): admission.append(data, changed)
    assert data == before


def test_provenance_does_not_upgrade_rights_completeness_or_observation_class(contract):
    source = contract['source_record']
    assert source['provider_asset_redistributed'] is False
    assert source['source_copy_complete'] is None
    assert source['source_kind'] == 'textbook_synthesis_not_a_new_observation_campaign'
    assert source['document_identity_sha256'] == source['original_sha256']
    assert 'not another independent document' in source['metadata_note']
    assert 'Independent section-width evidence is separate' in contract['host_explanation']
    for path, expected in contract['input_sha256'].items():
        assert admission.pin(path) == expected
    for path in contract['source_documents']:
        assert isinstance(json.loads((admission.ROOT/path).read_bytes()), dict)


def test_prepared_links_resolve_to_the_proposed_records_not_a_runtime_claim(contract):
    rows = admission.records(contract)
    for link in contract['card_links']:
        request = parse_qs(urlsplit(link['url']).query)
        if 'q' not in request:
            assert (admission.ROOT/'almanac'/link['url']).resolve().is_file()
            continue
        query = json.loads(request['q'][0]); wanted = query['filters'][0]['value']
        assert len([r for name, r in rows if name == query['collection'] and r['id'] == wanted]) == 1
