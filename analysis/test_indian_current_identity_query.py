"""Identity extension is separate from dimensions and commits atomically."""
import copy
import json
from unittest.mock import patch

import pytest

import indian_current_identity_query as a


@pytest.fixture(scope='module')
def document():
    return a.evidence()[0]


def baseline(document):
    refs = {item['entity_id'] for row in document['additions']['current_identity_admissions'] for item in row['distinguished_from']}
    return {
        'entities': [{'id': ref, 'label': ref} for ref in sorted(refs)],
        'sources': [{'id': 'source:old', 'rights': 'unchanged'}],
        'names': [{'id': 'name:old', 'entity_id': 'current:monsoon', 'label': 'Existing monsoon name'}],
        'objects': [{'id': 'current:monsoon', 'published_length_km': 123, 'map_features': [{'sentinel': 'retained'}]}],
        'measurements': [{'id': 'measurement:old', 'value': 123, 'unit': 'km'}],
        'widths': [{'id': 'width:old', 'approximate_width_km': 42}],
        'unrelated': [{'id': 'unchanged', 'nested': {'value': [1, 2, 3]}}],
    }


def test_four_identities_and_ten_names_without_egc(document):
    rows = document['additions']
    assert [r['id'] for r in rows['entities']] == list(a.EXPECTED)
    assert len(rows['names']) == 10
    assert not any(r['id'] == 'current:east-gyral' for r in rows['entities'])
    assert document['unresolved_candidate']['canonical_admitted'] is False
    assert document['canonical_delivery_verified'] is False
    eicc = next(r for r in rows['entities'] if r['id'] == 'current:east-india-coastal')
    assert eicc['time_behavior'] == 'seasonal_intraseasonal_variable'
    assert 'Some sources distinguish' in eicc['identity_scope_note']


def test_append_preserves_every_old_row_and_unrelated_collection(document):
    collections = baseline(document)
    before = copy.deepcopy(collections)
    a.append(collections, document)
    for name, old in before.items():
        assert collections[name][:len(old)] == old
        if name not in document['additions']:
            assert collections[name] == old
    for owner in collections['objects'][1:]:
        assert owner['linked_source_count'] == len(owner['source_ids'])
        assert owner['published_length_km'] is owner['latest_observation_date'] is None
        assert owner['map_features'] == owner['width_ids'] == owner['measurement_ids'] == owner['state_codes'] == []
        assert all(value == 0 for value in owner['capabilities'].values())
    with pytest.raises(ValueError):
        a.append(collections, document)


@pytest.mark.parametrize('collection', ['entities', 'names', 'sources', 'length_assessments', 'current_identity_admissions', 'objects'])
def test_collision_in_any_collection_rejects_before_any_mutation(document, collection):
    collections = baseline(document)
    collections.setdefault(collection, []).append(copy.deepcopy(document['additions'][collection][-1]))
    before = copy.deepcopy(collections)
    with pytest.raises(ValueError):
        a.append(collections, document)
    assert collections == before


def test_existing_spelling_or_abbreviation_requires_explicit_reconciliation(document):
    for label in ['  west INDIA coastal current ', 'WICC', 'East Indian Coastal Current']:
        collections = baseline(document)
        collections['names'].append({'id': 'name:collision', 'entity_id': 'current:other', 'label': label})
        before = copy.deepcopy(collections)
        with pytest.raises(ValueError, match='reconciliation'):
            a.append(collections, document)
        assert collections == before


def test_missing_distinguished_identity_cannot_be_silently_replaced(document):
    collections = baseline(document)
    collections['entities'] = [r for r in collections['entities'] if r['id'] != 'current:somali']
    before = copy.deepcopy(collections)
    with pytest.raises(ValueError, match='distinguished'):
        a.append(collections, document)
    assert collections == before


@pytest.mark.parametrize('field,value', [('rank_eligible', True), ('geometry', {'type': 'Point', 'coordinates': [0, 0]}), ('annual_width_range_km', [100, 400])])
def test_coherent_record_promotion_cannot_replace_saved_contract(document, field, value):
    mutated = copy.deepcopy(document)
    mutated['additions']['current_identity_admissions'][0][field] = value
    collections = baseline(document)
    before = copy.deepcopy(collections)
    with pytest.raises(ValueError, match='Unverified'):
        a.append(collections, mutated)
    assert collections == before


def test_frozen_review_and_original_guards():
    original_pin = a.pin
    for target in [a.REVIEW, 'research/source-data/vinayachandran-indian-upwelling-2021/article.pdf']:
        with patch.object(a, 'pin', side_effect=lambda path: '0' * 64 if path == target else original_pin(path)):
            with pytest.raises(ValueError):
                a.build_contract()


def test_complete_existing_base_and_prior_identity_are_preserved(document):
    import current_identity_admissions as previous
    collections = {name: json.loads((a.ROOT / (previous.BASE + name + '.json')).read_bytes())
                   for name in ('entities', 'sources', 'names', 'length_assessments')}
    previous.append(collections)
    before = copy.deepcopy(collections)
    a.append(collections, document)
    for name, old in before.items():
        assert collections[name][:len(old)] == old
    assert len(collections['entities']) == len(before['entities']) + 4
    assert len(collections['current_identity_admissions']) == len(before['current_identity_admissions']) + 4
