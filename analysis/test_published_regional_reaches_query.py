"""Admission preserves strict constraints and all established dimension rows."""
import copy
import json
from urllib.parse import parse_qs, urlsplit

import pytest

import published_regional_reaches_query as admission


@pytest.fixture(scope='module')
def contract():
    return admission.evidence()[0]


def fixture():
    return {'objects': [{'id': admission.ENTITY, 'source_ids': ['source:existing'], 'source_count': 1}],
            'claims': [], 'sources': [], 'measurements': [{'id': 'old', 'value': 17}],
            'widths': [{'id': 'old-width', 'value': [30, 50]}],
            'length_assessments': [{'id': 'length:algerian', 'length_km': None}],
            'ranked_currents': [{'id': 'current:elsewhere', 'length_km': 500}]}


def test_preserves_constraint_and_adds_only_four_scoped_records(contract):
    data = fixture(); previous = copy.deepcopy(data)
    admission.append(data, contract)
    assert len(data[admission.COLLECTION]) == 1
    assert len(data['claims']) == 1 and len(data['sources']) == 2
    for field in ['measurements', 'widths', 'length_assessments', 'ranked_currents']:
        assert data[field] == previous[field]
    row = data[admission.COLLECTION][0]
    c = row['constraint']
    assert c['threshold_km'] == 300 and c['relation'] == 'gt'
    assert c['upper_bound_km'] is None and c['reported_uncertainty_km'] is None
    assert c['physical_length_lower_bound_km'] is None and c['rank_eligible'] is False
    assert row['physical_width_admitted'] is False
    assert data['objects'][0]['regional_reach_ids'] == [admission.ID]
    assert data['objects'][0]['source_ids'] == sorted(['source:existing', admission.SOURCE_ID, admission.METHOD_ID])
    assert data['objects'][0]['source_count'] == 3
    assert data['claims'][0]['target_collection'] == admission.COLLECTION
    assert data['claims'][0]['value'] == c


@pytest.mark.parametrize('failure', ['no_owner', 'two_owners', 'bad_source_ids', 'bad_reach_ids',
                                      'duplicate_join', 'duplicate_source', 'duplicate_claim', 'duplicate_reach'])
def test_rejects_partial_or_duplicate_joins_before_mutating(contract, failure):
    data = fixture()
    if failure == 'no_owner': data['objects'].clear()
    elif failure == 'two_owners': data['objects'].append(copy.deepcopy(data['objects'][0]))
    elif failure == 'bad_source_ids': data['objects'][0]['source_ids'] = 'invalid'
    elif failure == 'bad_reach_ids': data['objects'][0]['regional_reach_ids'] = [42]
    elif failure == 'duplicate_join': data['objects'][0]['regional_reach_ids'] = [admission.ID]
    elif failure == 'duplicate_source': data['sources'].append(copy.deepcopy(contract['method_source']))
    elif failure == 'duplicate_claim': data['claims'].append(copy.deepcopy(contract['claim']))
    else: data[admission.COLLECTION] = [copy.deepcopy(contract['record'])]
    before = copy.deepcopy(data)
    with pytest.raises(ValueError): admission.append(data, contract)
    assert data == before


@pytest.mark.parametrize('field,value', [('whole_current_length_admitted', True),
                                       ('physical_width_admitted', True),
                                       ('annual_or_seasonal_range_admitted', True)])
def test_altered_scope_rejects_atomically(contract, field, value):
    changed = copy.deepcopy(contract); changed['record'][field] = value
    data = fixture(); before = copy.deepcopy(data)
    with pytest.raises(ValueError, match='Unverified'): admission.append(data, changed)
    assert data == before


def test_custody_pins_and_every_card_query_resolve(contract):
    assert contract['source_record']['source_copy_complete'] is False
    assert contract['source_record']['missing_printed_journal_pages'] == [1596, 1597]
    for path, digest in contract['input_sha256'].items():
        assert admission.pin(path) == digest
    for path in contract['source_documents']:
        assert isinstance(json.loads((admission.ROOT/path).read_bytes()), dict)
    rows = admission.records(contract)
    for link in contract['card_links']:
        request = parse_qs(urlsplit(link['url']).query)
        if 'q' not in request:
            assert (admission.ROOT/'almanac'/link['url']).resolve().is_file()
            continue
        query = json.loads(request['q'][0]); wanted = query['filters'][0]['value']
        assert len([r for name, r in rows if name == query['collection'] and r['id'] == wanted]) == 1
