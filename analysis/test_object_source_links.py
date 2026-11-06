"""Provenance projection catches the observed Brazil media/count regression."""
import copy

import pytest

from object_source_links import project


def fixture():
    return {'id': 'current:brazil', 'source_ids': ['source:one', 'source:two', 'source:three'],
            'linked_source_count': 5, 'published_length_km': None,
            'width_ids': ['width:existing'], 'scope_notes': [{'text': 'Keep existing scope'}]}


def test_missing_registered_media_reference_is_restored_without_inventing_a_fifth_source():
    owner = fixture(); before = copy.deepcopy(owner)
    media = {'id': 'media:0016', 'entity_id': owner['id'], 'source_id': 'source:4f7441b953be4651'}
    registry = [*owner['source_ids'], media['source_id']]
    result = project(owner, registry, [media])
    assert result['linked_source_count'] == 4
    assert result['source_ids'] == sorted(registry)
    assert {k: v for k, v in result.items() if k not in ['source_ids', 'linked_source_count']} == {k: v for k, v in owner.items() if k not in ['source_ids', 'linked_source_count']}
    assert owner == before


def test_all_explicit_reference_fields_join_without_counting_metadata_dictionaries():
    owner = {'id': 'current:example', 'linked_source_count': 99}
    evidence = [{'id': owner['id'], 'source_id': 'source:identity'},
                {'entity_id': owner['id'], 'source_snapshot_id': 'source:snapshot', 'method_source_id': 'source:method'},
                {'subject_id': owner['id'], 'source_id': 'source:identity'},
                {'current_id': 'example', 'source_ids': ['source:route']},
                {'object_id': owner['id'], 'supporting_sources': [{'url': 'https://example.com/context'}]}]
    registry = ['source:identity', 'source:snapshot', 'source:method', 'source:route']
    result = project(owner, registry, evidence)
    assert result['source_ids'] == sorted(registry) and result['linked_source_count'] == 4
    result['source_ids'].clear()
    assert 'source_ids' not in owner


@pytest.mark.parametrize('failure', ['unregistered', 'duplicate_registry', 'duplicate_refs',
                                      'malformed_refs', 'malformed_scalar', 'foreign_owner'])
def test_invalid_projection_leaves_inputs_untouched(failure):
    owner = fixture(); registry = owner['source_ids'].copy(); evidence = []
    if failure == 'unregistered': registry.pop()
    elif failure == 'duplicate_registry': registry.append(registry[0])
    elif failure == 'duplicate_refs': owner['source_ids'].append(registry[0])
    elif failure == 'malformed_refs': owner['source_ids'] = 'invalid'
    elif failure == 'malformed_scalar': evidence = [{'entity_id': owner['id'], 'source_id': 17}]
    else: evidence = [{'entity_id': 'current:another', 'source_id': registry[0]}]
    before = copy.deepcopy((owner, registry, evidence))
    with pytest.raises(ValueError): project(owner, registry, evidence)
    assert (owner, registry, evidence) == before
