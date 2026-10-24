"""Compatible source evidence commits together without changing measured data."""
import copy
from unittest.mock import patch

import pytest

import current_gap_admission_batch as batch
import indian_current_evidence_query as e
import indian_current_identity_query as identity


@pytest.fixture(scope='module')
def documents():
    return batch.documents()


def baseline():
    ids = ['current:brazil', 'current:monsoon', 'current:somali', 'current:indonesian-throughflow']
    sources = ['source:old-one', 'source:old-two', 'source:old-three', 'source:4f7441b953be4651']
    objects = [{'id': value, 'label': value, 'source_ids': [], 'linked_source_count': 0,
                'capabilities': {}, 'section_fingerprints': {}, 'fingerprint': 'old'} for value in ids]
    objects[0].update(source_ids=sources[:3], linked_source_count=5,
        published_length_km=123, width_ids=['width:old'], map_features=[{'sentinel': 'keep'}])
    return {
        'entities': [{'id': value, 'label': value} for value in ids],
        'objects': objects, 'sources': [{'id': value, 'rights': 'retain'} for value in sources],
        'names': [], 'claims': [], 'length_assessments': [],
        'measurements': [{'id': 'measurement:old', 'entity_id': ids[0], 'value': 123, 'source_id': sources[0]}],
        'widths': [{'id': 'width:old', 'current_id': 'brazil', 'approximate_width_km': 42}],
        'geometries': [{'id': 'geometry:old', 'entity_id': ids[0], 'coordinates': [0, 0], 'source_id': sources[0]}],
        'media': [{'id': 'media:0016', 'entity_id': ids[0], 'source_id': sources[3]}],
        'reference_routes': [], 'width_samples': [], 'length_ranks': [],
        'source_arrays': [{'id': 'array:old', 'entity_id': ids[0], 'source_id': sources[0], 'values': list(range(100))}],
    }


def test_all_76_rows_are_staged_without_copying_or_changing_physical_payload(documents):
    collections = baseline()
    before = copy.deepcopy(collections)
    stage, receipt = batch.prepare(collections, *documents)
    assert collections == before
    assert sum(receipt['added_rows'].values()) == 76
    assert receipt['physical_collections_unchanged'] is True
    assert receipt['canonical_delivery_verified'] is False
    for name in ('measurements', 'widths', 'geometries', 'source_arrays', 'width_samples', 'length_ranks'):
        assert stage[name] is collections[name]
    for name in ('entities', 'sources', 'names', 'claims'):
        assert stage[name][:len(before[name])] == before[name]
    assert len(stage['objects']) == len(before['objects']) + 4
    brazil = next(r for r in stage['objects'] if r['id'] == 'current:brazil')
    allowed = {'source_ids', 'linked_source_count', 'fingerprint', 'section_fingerprints', 'regional_reach_ids',
               'evidence_links', 'regional_reach_scope_note', 'recorded_claims', 'claim_review_counts', 'capabilities'}
    assert {k: v for k, v in brazil.items() if k not in allowed} == {k: v for k, v in before['objects'][0].items() if k not in allowed}
    assert brazil['linked_source_count'] == 6
    assert 'source:4f7441b953be4651' in brazil['source_ids']
    assert brazil['published_length_km'] == 123
    assert brazil['recorded_claims'] == 1
    assert brazil['capabilities']['reported_regional_reaches'] == 1
    assert all(link in brazil['evidence_links'] for link in documents[2]['card_links'])
    assert brazil['regional_reach_scope_note'] == documents[2]['host_explanation']
    registry = {r['id'] for r in stage['sources']}
    for owner in stage['objects']:
        assert owner['linked_source_count'] == len(owner['source_ids']) == len(set(owner['source_ids']))
        assert set(owner['source_ids']) <= registry


def test_calendar_unknowns_and_dated_episode_are_not_observations(documents):
    stage, _ = batch.prepare(baseline(), *documents)
    months = stage['current_direction_descriptions']
    assert len(months) == 24
    assert all(r['is_observation'] is False and r['observed_velocity_m_s'] is None for r in months)
    wicc = [r for r in months if r['entity_id'] == 'current:west-india-coastal']
    assert [(r['month'], r['direction']) for r in wicc if r['direction'] is None] == [(3, None), (10, None)]
    episode, = stage['current_regime_context']
    assert episode['reported_hydrographic_survey_window'] == ['1994-03-06', '1994-03-21']
    assert episode['altimeter_sample_window'] is None
    assert episode['named_eddies_admitted'] == [] and episode['zero_current_claimed'] is False
    owner = next(r for r in stage['objects'] if r['id'] == 'current:west-india-coastal')
    assert owner['capabilities']['direction_descriptions'] == 12
    assert owner['capabilities']['time_samples'] == 0
    assert owner['latest_observation_date'] is None


def test_width_and_offshore_context_keep_distinct_support(documents):
    stage, _ = batch.prepare(baseline(), *documents)
    widths = stage['current_reported_width_evidence']
    assert [r['reported_width_km'] for r in widths] == [100, 200, 250]
    assert widths[0]['reported_time_window'] == ['2013-12-23', '2013-12-24']
    assert widths[0]['width_depth_level_m'] == 21
    assert widths[1]['reported_time_window'] is widths[2]['reported_time_window'] is None
    assert all(r['annual_width_range_km'] is None and r['canonical_width_admitted'] is False for r in widths)
    offshore = stage['current_cross_shore_context']
    assert len(offshore) == len({r['quantity'] for r in offshore}) == 4
    assert all(r['width_interval'] is False and r['annual_min_max'] is False for r in offshore)
    assert stage['widths'] == baseline()['widths'] and stage['width_samples'] == []
    owner = next(r for r in stage['objects'] if r['id'] == 'current:east-india-coastal')
    assert owner['capabilities']['reported_width_evidence'] == 3
    assert owner['capabilities']['scoped_width'] == owner['capabilities']['width_samples'] == 0


def test_original_access_and_rights_do_not_get_upgraded(documents):
    rows = {r['id']: r for r in documents[1]['additions']['sources']}
    assert rows[e.SHE]['original_asset_retained'] is False
    assert rows[e.SHE]['full_original_independently_checked'] is False
    assert rows[e.VIJ]['access_scope'] == 'publisher_abstract_only'
    assert rows[e.WIJ]['provider_asset_redistributed'] is False and rows[e.WIJ]['license'] is None
    assert rows[e.PAI]['provider_asset_redistributed'] is True and rows[e.PAI]['license'] == 'CC-BY-4.0'


@pytest.mark.parametrize('collection', [*e.OWNER_FIELDS, 'sources'])
def test_evidence_collision_in_any_collection_rolls_back_identity_extension(documents, collection):
    collections = baseline()
    collections.setdefault(collection, []).append(copy.deepcopy(documents[1]['additions'][collection][-1]))
    before = copy.deepcopy(collections)
    with pytest.raises(ValueError):
        batch.append(collections, *documents)
    assert collections == before


def test_late_brazil_collision_does_not_commit_prior_identity_evidence_or_projection(documents):
    collections = baseline()
    collections['current_regional_reaches'] = [{'id': documents[2]['record']['id'], 'entity_id': 'current:brazil'}]
    before = copy.deepcopy(collections)
    with pytest.raises(ValueError, match='Duplicate Brazil'):
        batch.append(collections, *documents)
    assert collections == before


def test_unresolved_provider_reference_aborts_complete_batch(documents):
    collections = baseline()
    collections['other_provider'] = [{'entity_id': 'current:brazil', 'source_snapshot_id': 'source:unregistered'}]
    before = copy.deepcopy(collections)
    with pytest.raises(ValueError, match='Unresolved'):
        batch.append(collections, *documents)
    assert collections == before


@pytest.mark.parametrize('collection,field,value', [
    ('current_direction_descriptions', 'is_observation', True),
    ('current_direction_calendars', 'geographic_seasonal_playback_eligible', True),
    ('current_reported_width_evidence', 'canonical_width_admitted', True),
    ('current_cross_shore_context', 'width_interval', True),
    ('current_regime_context', 'named_eddies_admitted', ['invented-eddy']),
])
def test_promoted_context_cannot_replace_the_reviewed_contract(documents, collection, field, value):
    forged = copy.deepcopy(documents[1])
    forged['additions'][collection][0][field] = value
    collections = baseline()
    before = copy.deepcopy(collections)
    with pytest.raises(ValueError, match='Unverified'):
        batch.append(collections, documents[0], forged, documents[2])
    assert collections == before


def test_complete_commit_and_duplicate_rejection(documents):
    collections = baseline()
    receipt = batch.append(collections, *documents)
    assert sum(receipt['added_rows'].values()) == 76
    before = copy.deepcopy(collections)
    with pytest.raises(ValueError):
        batch.append(collections, *documents)
    assert collections == before


def test_changed_frozen_source_context_is_rejected():
    real_pin = identity.pin
    with patch.object(identity, 'pin', side_effect=lambda path: '0' * 64 if path == e.REGIME else real_pin(path)):
        with pytest.raises(ValueError, match='Changed reviewed'):
            e.build_contract()
