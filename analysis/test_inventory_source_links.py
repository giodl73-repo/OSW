"""Inventory projection retains omitted media/geometry/method provenance."""
import copy

import pytest

import inventory_source_links as a


def fixture():
    refs = ['source:paper', 'source:media', 'source:geometry', 'source:method', 'source:snapshot', 'source:route']
    return {
        'objects': [{'id': 'current:brazil', 'source_ids': ['source:paper'], 'linked_source_count': 5,
                     'published_length_km': None, 'width_ids': ['width:old'], 'map_features': [{'keep': True}]},
                    {'id': 'eddy:test', 'source_ids': [], 'linked_source_count': 0}],
        'sources': [{'id': ref, 'rights': 'keep'} for ref in refs],
        'entities': [{'id': 'current:brazil', 'source_id': refs[0]}],
        'measurements': [], 'claims': [],
        'geometries': [{'entity_id': 'current:brazil', 'source_id': refs[2], 'method_source_id': refs[3]}],
        'media': [{'entity_id': 'current:brazil', 'source_id': refs[1]}],
        'reference_routes': [{'current_id': 'brazil', 'source_ids': [refs[5]]}],
        'provider_rows': [{'subject_id': 'current:brazil', 'object_id': 'eddy:test', 'source_snapshot_id': refs[4]}],
        'context_rows': [{'entity_id': 'current:brazil', 'supporting_sources': [{'url': 'https://example.org/prose'}]}],
    }


def test_complete_registered_refs_and_other_owner_fields_preserved():
    collections = fixture()
    before = copy.deepcopy(collections)
    objects, audit = a.prepare(collections)
    assert collections == before
    brazil, eddy = objects
    assert brazil['linked_source_count'] == 6
    assert brazil['source_ids'] == sorted(row['id'] for row in collections['sources'])
    assert eddy['source_ids'] == ['source:snapshot']
    assert eddy['linked_source_count'] == 1
    assert {k: v for k, v in brazil.items() if k not in ('source_ids', 'linked_source_count')} == {
        k: v for k, v in before['objects'][0].items() if k not in ('source_ids', 'linked_source_count')}
    assert audit['changed_object_count'] == 2
    assert audit['independent_document_or_observation_count_inferred'] is False


def test_atomic_failure_on_late_owner_does_not_change_first_owner():
    collections = fixture()
    collections['provider_rows'].append({'entity_id': 'eddy:test', 'source_id': 'source:unregistered'})
    before = copy.deepcopy(collections)
    with pytest.raises(ValueError, match='Unresolved'):
        a.append(collections)
    assert collections == before


@pytest.mark.parametrize('missing', a.REQUIRED)
def test_missing_required_collection_cannot_claim_complete_projection(missing):
    collections = fixture()
    del collections[missing]
    before = copy.deepcopy(collections)
    with pytest.raises(ValueError, match='Incomplete'):
        a.append(collections)
    assert collections == before


def test_duplicates_in_registry_or_inventory_rejected_without_mutation():
    for key in ('objects', 'sources'):
        collections = fixture()
        collections[key].append(copy.deepcopy(collections[key][0]))
        before = copy.deepcopy(collections)
        with pytest.raises(ValueError, match='duplicate'):
            a.append(collections)
        assert collections == before


def test_apply_is_idempotent_and_does_not_alias_input_evidence():
    collections = fixture()
    before_evidence = copy.deepcopy(collections['provider_rows'])
    first = a.append(collections)
    assert first['changed_object_count'] == 2
    assert a.append(collections)['changed_object_count'] == 0
    collections['objects'][0]['source_ids'].clear()
    assert collections['provider_rows'] == before_evidence


@pytest.mark.parametrize('location', ['objects', 'sources', 'provider_rows'])
def test_malformed_inventory_inputs_reject_without_partial_projection(location):
    collections = fixture()
    if location == 'provider_rows':
        collections[location].append('not a record')
    else:
        collections[location][0]['id'] = ['not a string identity']
    before = copy.deepcopy(collections)
    with pytest.raises(ValueError):
        a.append(collections)
    assert collections == before
