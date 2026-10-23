import copy
import json
from urllib.parse import parse_qs, urlsplit

import pytest

import caribbean_ru29_query as admission


@pytest.fixture(scope='module')
def contract():
    return admission.evidence()[0]


def fixture(document):
    return {'diagnostics': [], 'sources': [], 'objects': [
        {'id': admission.ENTITY, 'provider_velocity_source': copy.deepcopy(document['card_context']),
         'source_ids': ['source:existing-caribbean'],
         'evidence_links': copy.deepcopy(document['card_links'])}]}


def test_complete_source_contract_retains_scope_and_all_documents(contract):
    assert contract['card_context']['source_variables'] == 306
    assert contract['card_context']['retained_source_values'] == 3609111
    assert contract['card_context']['physical_width_admitted'] is False
    assert contract['card_context']['whole_current_length_admitted'] is False
    assert contract['card_context']['seasonal_envelope_admitted'] is False
    assert contract['card_context']['eddy_pipeline_reproduced'] is False
    assert admission.method.MIRROR in contract['source_documents']
    assert len(contract['source_documents']) == 13
    assert json.loads(contract['diagnostic']['source_json']) == contract['diagnostic']['document']


def test_adds_three_records_and_one_explicit_owner_join(contract):
    collections = fixture(contract)
    admission.append(collections, contract)
    assert len(collections['diagnostics']) == 1
    assert len(collections['sources']) == 2
    assert collections['objects'][0]['diagnostic_ids'] == [admission.ID]
    assert collections['objects'][0]['source_ids'] == sorted(['source:existing-caribbean', admission.SOURCE_ID, admission.METHOD_ID])
    assert set(collections) == {'diagnostics', 'sources', 'objects'}


@pytest.mark.parametrize('failure', ['duplicate_source', 'duplicate_diagnostic', 'missing_owner', 'duplicate_owner', 'invalid_join'])
def test_rejected_admission_is_atomic(contract, failure):
    collections = fixture(contract)
    if failure == 'duplicate_source':
        collections['sources'].append(copy.deepcopy(contract['source_record']))
    elif failure == 'duplicate_diagnostic':
        collections['diagnostics'].append(copy.deepcopy(contract['diagnostic']))
    elif failure == 'missing_owner':
        collections['objects'].clear()
    elif failure == 'duplicate_owner':
        collections['objects'].append(copy.deepcopy(collections['objects'][0]))
    else:
        collections['objects'][0]['diagnostic_ids'] = 'invalid'
    before = copy.deepcopy(collections)
    with pytest.raises(ValueError):
        admission.append(collections, contract)
    assert collections == before


def test_changed_contract_cannot_be_admitted(contract):
    changed = copy.deepcopy(contract)
    changed['card_context']['physical_width_admitted'] = True
    collections = fixture(contract)
    before = copy.deepcopy(collections)
    with pytest.raises(ValueError, match='Unverified'):
        admission.append(collections, changed)
    assert collections == before


def test_every_source_navigation_pointer_resolves_to_complete_array_or_object(contract):
    cache = {}
    for link in contract['card_links']:
        query = parse_qs(urlsplit(link['url']).query)
        if 'source-q' not in query:
            continue
        request = json.loads(query['source-q'][0])
        path = request['document']
        assert path in contract['source_documents']
        if path not in cache:
            cache[path] = json.loads((admission.ROOT/path).read_bytes())
        value = cache[path]
        for part in request['pointer'].split('/')[1:]:
            value = value[part.replace('~1', '/').replace('~0', '~')]
        assert isinstance(value, (list, dict))
        assert 1 <= request['limit'] <= 500
