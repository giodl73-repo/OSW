"""Admit the named branch without conflating its local dimensions or source scopes."""
import copy
import json

import pytest
import nwasc_working_admission as n


def test_effective_catalogue_keeps_all_previous_names_exact():
    doc, _ = n.verify_inputs()
    catalogue = n.catalogue(doc)
    previous = n.identities.catalogue()
    assert catalogue['entries'][:-1] == previous['entries']
    assert catalogue['entries'][-1]['id'] == n.ENTITY
    assert catalogue['current_count'] == len(catalogue['entries']) == 102
    assert len({r['id'] for r in catalogue['entries']}) == 102
    assert doc['entity']['identity_scope_note'].startswith('Atlantic-water eastern slope branch')
    assert doc['identity_entry']['geometry'] is None


def test_five_historical_widths_have_exactly_scoped_admitted_copies():
    doc = n.build()
    old = {r['id']: r for r in n.historical_widths()}
    assert len(doc['width_records']) == 6 and len(doc['width_migrations']) == 5
    for row in doc['width_records'][:5]:
        original = old[row['previous_proposed_record_id']]
        for key in ['width_metric', 'measurement_type', 'approximate_width_km', 'width_range_km', 'geographic_scope',
                    'layer', 'boundary_rule', 'observed_period', 'calendar_months', 'fixed_layer_bounds_m',
                    'support_dates', 'source_url', 'source_citation', 'source_locator', 'sampling_context',
                    'width_plane_depth_m', 'reported_maximum_core_depth_m', 'scope_isobath_m', 'mean_transport_fraction']:
            assert row.get(key) == original.get(key), (row['id'], key)
        assert row['current_id'] == n.ID
        assert 'proposed_current_id' not in row
        assert row['id'] != original['id']
        assert row['source_file'] == n.FILE


def test_mean_flow_description_is_not_a_midpoint_or_width_distribution():
    row = n.build()['width_records'][-1]
    assert row['approximate_width_km'] == 40
    assert row['width_range_km'] is None
    assert row['width_metric'] == 'width_of_described_annual_mean_flow'
    assert row['source_locator'].startswith('Introduction paragraph[4]')
    assert 'not a midpoint' in row['extraction_method']
    assert row['is_mean_field_geometry'] and not row['is_mean_of_widths']
    assert row['observed_period'] is row['fixed_layer_bounds_m'] is row['uncertainty_km'] is None


def test_all_six_widths_preserve_nonseasonal_and_nonphysical_limits():
    for row in n.build()['width_records']:
        for key in ['rank_eligible', 'width_rank_eligible', 'whole_current_representative', 'full_width_inference_eligible',
                    'annual_extrema_eligible', 'seasonal_playback_eligible', 'is_confidence_interval', 'independent_new_observation']:
            assert row[key] is False, (row['id'], key)
        for key in ['whole_current_width_km', 'annual_width_range_km', 'geographic_current_edges']:
            assert row[key] is None


def test_broad_historical_extent_has_no_invented_axis_or_modern_scope():
    doc = n.build()
    row = doc['measurement']
    assert row['value'] == 3500 and row['rank_eligible']
    assert row['source_locator'].startswith('Introduction paragraph[3]')
    assert 'West Spitsbergen' in row['scope'] and 'not an additive component length' in row['scope']
    for key in ['geometry_id', 'observation_time', 'fixed_layer_bounds_m', 'endpoint_coordinates_lon_lat', 'reference_period', 'uncertainty_km', 'annual_length_range_km']:
        assert row[key] is None
    assert doc['new_independent_width_observations'] == 0
    custody = n.read(n.CUSTODY)
    assert not custody['original_redistributed'] and not custody['abstract_redistributed']
    assert custody['original_publication_year'] == 2001
    assert custody['repository_deposit_date'].startswith('2024-')


def test_live_export_has_nac_bound_method_source_and_all_thirteen_ranks():
    doc, _ = n.verify_inputs()
    live = n.working_export(doc)
    assert len(live['widths']) == live['scoped_width_count'] == 164
    assert len({w['current_id'] for w in live['widths']}) == live['scoped_width_owners'] == 84
    assert len(live['length_assessments']) == 102
    ranked = [r for r in live['length_assessments'] if r['rank_eligible']]
    assert len(ranked) == live['ranked_length_count'] == 13
    assert doc['length_assessment']['published_rank'] == 6
    for row in ranked:
        assert row['published_rank'] == 1 + len([r for r in ranked if r['published_length_km'] > row['published_length_km']])
    assert doc['working_published_ranks']['current:southern-east-madagascar'] == 13
    source_ids = {r['id'] for r in live['sources']}
    assert len(source_ids) == len(live['sources'])
    for row in live['measurements']:
        for key in ['source_id', 'method_source_id']:
            if row.get(key):
                assert row[key] in source_ids, (row['id'], key)
    bound = next(r for r in live['length_assessments'] if r['entity_id'] == 'current:north-atlantic')
    assert bound == n.nac.verify_inputs()[0]['length_assessment']


def test_recomputed_working_ranks_do_not_rewrite_other_fields():
    doc = n.build()
    earlier = n.previous.effective_export()['length_assessments']
    earlier = [n.nac.verify_inputs()[0]['length_assessment'] if r['entity_id'] == n.nac.ENTITY else r for r in earlier]
    after = {r['id']: r for r in doc['working_length_assessments']}
    for row in earlier:
        current = copy.deepcopy(after[row['id']])
        current['published_rank'] = row['published_rank']
        assert current == row


def test_competition_ranks_keep_ties_and_input_immutable():
    rows = [{'id': str(i), 'rank_eligible': True, 'published_length_km': v, 'published_rank': None} for i, v in enumerate([50, 100, 50, 20])]
    before = copy.deepcopy(rows)
    assert [r['published_rank'] for r in n.rank_assessments(rows)] == [2, 1, 2, 4]
    assert rows == before


@pytest.mark.parametrize('value', [0, -1, None])
def test_ranked_values_must_be_positive(value):
    with pytest.raises(ValueError):
        n.rank_assessments([{'id': 'bad', 'rank_eligible': True, 'published_length_km': value}])
