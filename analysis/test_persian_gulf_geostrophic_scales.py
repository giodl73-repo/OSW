"""The same section can support distinct scales without a variability range."""
import copy
import json
import subprocess
import pytest
from check_persian_gulf_geostrophic_scales import ROOT, OWNER, IDS, load, records, validate_row, validate_inventory


def test_two_spatial_operators_preserve_reference_and_missing_support():
    rows = records()
    assert [r['approximate_width_km'] for r in rows] == [30, 5]
    assert len({r['width_metric'] for r in rows}) == 2
    for row in rows:
        validate_row(row)
        c = row['original_regional_context']
        assert c['velocity_reference_depth_m'] == 30
        assert c['added_reference_velocity_m_s'] == .09
        assert c['velocity_boundary_threshold_m_s'] is None
        assert not c['r13_r12_adcp_available']
        assert c['width_description_section'] == 'R13'
        assert c['method_figure_section'] == 'R13b'
        assert row['fixed_layer_bounds_m'] is None and row['observed_period'] is None


@pytest.mark.parametrize('key,value', [
    ('approximate_width_km', 17.5), ('width_range_km', [5, 30]),
    ('uncertainty_km', 25), ('fixed_layer_bounds_m', [30, 45]),
    ('observed_period', {'start': '1999-10-22', 'end': '1999-10-22'}),
    ('annual_width_range_km', [5, 30]), ('seasonal_playback_eligible', True),
    ('current_id', 'red-sea-saline-overflow'),
])
def test_cannot_pool_operators_or_transfer_dates_layers_and_ownership(key, value):
    row = records()[0]
    row[key] = value
    with pytest.raises(ValueError): validate_row(row)


def test_velocity_description_is_not_edge_cutoff_or_direct_adcp():
    for key, value in [('velocity_boundary_threshold_m_s', .1),
                       ('velocity_description_is_boundary_cutoff', True),
                       ('reference_velocity_is_contemporaneous_adcp', True),
                       ('width_occupation_date_verified', True),
                       ('band_peak_difference_is_error_or_seasonal_range', True)]:
        row = records()[0]
        row['original_regional_context'][key] = value
        with pytest.raises(ValueError): validate_row(row)


def test_existing_salinity_records_unchanged_and_new_scales_cannot_disappear():
    document = json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
    validate_inventory(document)
    assert len(load()['existing_salinity_records']) == 6
    for mode in ['missing', 'duplicate', 'changed_salinity']:
        bad = copy.deepcopy(document)
        row = next(r for r in bad['measurements'] if r['id'] == IDS[0])
        if mode == 'missing': bad['measurements'].remove(row)
        if mode == 'duplicate': bad['measurements'].append(copy.deepcopy(row))
        if mode == 'changed_salinity':
            next(r for r in bad['measurements'] if r['id'] == load()['existing_salinity_records'][0]['id'])['approximate_width_km'] = 30
        with pytest.raises(ValueError): validate_inventory(bad)


def test_editorial_reach_is_not_source_distance_or_ranked_current_length():
    from build_current_reference_path_candidate import length_km
    report = json.loads((ROOT/'research/persian-gulf-cascading-reach-reference-path-candidate.json').read_bytes())
    assert report['current_id'] == OWNER
    assert report['candidate_comparison_group'] == 'osw_studied_reach_routes'
    assert report['rank_eligible_published_estimates'] is False
    assert report['whole_system_length'] is False
    assert report['scenario_count'] == 81
    assert report['reported_approximate_reference_path_km'] == 140
    assert report['reported_scenario_range_km'] == [120, 160]
    assert abs(report['nominal_reference_path_km']-length_km(report['coordinates_lon_lat'])) < .001
    catalog = json.loads((ROOT/'research/ocean-current-reference-path-candidates.json').read_bytes())
    assert 'persian-gulf-cascading-reach-reference-path-candidate' not in catalog['reference_route_length_order']
