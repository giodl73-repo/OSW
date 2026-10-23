"""A scoped published width is distinct from raw samples and annual envelopes."""
import copy

import pytest

import current_gap_width_admission_batch as batch
import eicc_t24_width_admission as a
import indian_current_evidence_query as context
from test_current_gap_admission_batch import baseline


@pytest.fixture(scope='module')
def documents():
    return batch.documents()


def test_scoped_width_commits_after_identity_and_preserves_all_old_dimensions(documents):
    collections = baseline()
    collections['current_measurement_admissions'] = [{'id': 'admission:prior', 'scope': 'retain'}]
    before = copy.deepcopy(collections)
    stage, receipt = batch.prepare(collections, *documents)
    assert collections == before
    assert sum(receipt['added_rows'].values()) == 75
    assert receipt['scoped_published_width_records_added'] == 1
    assert stage['widths'][:-1] == before['widths']
    assert stage['widths'][0] is collections['widths'][0]
    for name in ('measurements', 'geometries', 'width_samples', 'length_ranks', 'source_arrays'):
        assert stage[name] is collections[name]
    assert stage['current_measurement_admissions'][0] == before['current_measurement_admissions'][0]
    width = stage['widths'][-1]
    assert width['approximate_width_km'] == 100 and width['source_reported_depth_level_m'] == 21
    assert width['observation_window'] == ['2013-12-23', '2013-12-24']
    assert width['uncertainty_km'] is width['fixed_layer_bounds_m'] is None
    assert width['annual_width_range_km'] is width['geographic_current_edges'] is None
    assert width['width_rank_eligible'] is width['seasonal_playback_eligible'] is False
    owner = next(row for row in stage['objects'] if row['id'] == a.ENTITY)
    assert owner['width_ids'] == [a.WIDTH_ID]
    assert owner['capabilities']['scoped_width'] == 1
    assert owner['capabilities']['width_samples'] == 0
    assert owner['width_sample_ids'] == [] and owner['map_features'] == []
    assert owner['latest_observation_date'] is None
    assert owner['linked_source_count'] == len(owner['source_ids'])
    claim = next(row for row in stage['claims'] if row['id'] == a.CLAIM_ID)
    assert claim['target_collection'] == 'widths' and claim['target_id'] == a.WIDTH_ID
    assert claim['observation_time'] is None and claim['source_publication_year'] == 2015
    assert claim['review_fingerprint'] == a.review_fingerprint(claim)


def test_only_t24_gets_a_new_admission_and_source_snapshots_remain_exact(documents):
    stage, _ = batch.prepare(baseline(), *documents)
    statements = stage['current_reported_width_evidence']
    assert [row['canonical_width_admitted'] for row in statements] == [True, False, False]
    assert statements[0]['source_stage_canonical_width_admitted'] is False
    assert statements[0]['width_admission_id'] == a.ADMISSION_ID
    assert all(row['current_id'] != 'east-african-coastal' for row in stage['widths'])
    for path, expected in context.PINS.items():
        assert a.identity.pin(path) == expected


@pytest.mark.parametrize('collection,key', [('widths', 'width_record'), ('claims', 'claim'), ('current_measurement_admissions', 'admission')])
def test_late_width_collision_rolls_back_complete_source_batch(documents, collection, key):
    collections = baseline()
    collections.setdefault(collection, []).append({'id': documents[3][key]['id']})
    before = copy.deepcopy(collections)
    with pytest.raises(ValueError, match='collision'):
        batch.append(collections, *documents)
    assert collections == before


@pytest.mark.parametrize('field,value', [
    ('approximate_width_km', 150), ('annual_width_range_km', [100, 250]),
    ('fixed_layer_bounds_m', [0, 100]), ('geographic_current_edges', [[80, 5.25], [81, 5.25]]),
    ('observation_window', ['2015-10-01', '2015-10-01']), ('seasonal_playback_eligible', True),
])
def test_dimension_date_and_geometry_promotions_are_rejected(documents, field, value):
    forged = copy.deepcopy(documents[3])
    forged['width_record'][field] = value
    collections = baseline()
    before = copy.deepcopy(collections)
    with pytest.raises(ValueError, match='Unverified'):
        batch.append(collections, *documents[:3], forged)
    assert collections == before


def test_identity_and_source_statement_are_separate_admission_gates(documents):
    import current_gap_admission_batch as source_batch
    for field in ('current_identity_admissions', 'current_reported_width_evidence'):
        stage, _ = source_batch.prepare(baseline(), *documents[:3])
        stage[field] = []
        before = copy.deepcopy(stage)
        with pytest.raises(ValueError):
            a.append(stage, documents[3])
        assert stage == before


def test_commit_is_atomic_and_duplicate_retry_adds_nothing(documents):
    collections = baseline()
    receipt = batch.append(collections, *documents)
    assert sum(receipt['added_rows'].values()) == 75
    before = copy.deepcopy(collections)
    with pytest.raises(ValueError):
        batch.append(collections, *documents)
    assert collections == before


def test_invalid_existing_claim_metadata_cannot_partially_append_width(documents):
    import current_gap_admission_batch as source_batch
    stage, _ = source_batch.prepare(baseline(), *documents[:3])
    stage['claims'].append({'id': 'claim:bad-metadata', 'subject_id': a.ENTITY, 'review_status': {'bad': 'type'}})
    before = copy.deepcopy(stage)
    with pytest.raises(ValueError, match='review metadata'):
        a.append(stage, documents[3])
    assert stage == before


@pytest.mark.parametrize('mutation', ['erase_locator', 'reassign_source'])
def test_missing_passage_or_reassigned_source_cannot_support_width(documents, mutation):
    forged = copy.deepcopy(documents[3])
    if mutation == 'erase_locator':
        del forged['width_record']['source_locator']
    else:
        forged['width_record']['source_id'] = a.identity.PRIMARY
        forged['claim']['source_id'] = a.identity.PRIMARY
        forged['claim']['review_fingerprint'] = a.review_fingerprint(forged['claim'])
    collections = baseline()
    before = copy.deepcopy(collections)
    with pytest.raises(ValueError, match='Unverified'):
        batch.append(collections, *documents[:3], forged)
    assert collections == before
