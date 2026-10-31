"""Prospective synthetic scope, comparator, uncertainty and chronology tests."""
import pytest

import published_current_regional_reaches_v1 as method


def fixture():
    return {'entity_id': 'current:synthetic', 'current_id': 'synthetic',
            'quantity': 'reported_nearshore_regional_extent', 'reported_threshold_km': 42,
            'relation': 'gt', 'unit': 'km', 'reported_upper_bound_km': None, 'source_uncertainty_km': None,
            'whole_current_length_admitted': False, 'physical_width_admitted': False,
            'annual_or_seasonal_range_admitted': False, 'current_geometry_admitted': False,
            'coast_proximity_is_current_width': False, 'coast_proximity_context_km': 7,
            'reported_study_window': ['2000-01-01', '2000-01-20'],
            'ship_cruise_window': ['2000-01-02', '2000-01-19'], 'publication_year': 2001,
            'spatial_support': ['A', 'B'], 'time_support_kind': 'combined_study_window'}


def test_strict_threshold_does_not_become_point_length_or_closed_range():
    f = fixture()
    result = method.constraint(f)
    assert result['threshold_km'] == 42 and result['relation'] == 'gt'
    assert result['display'] == '>42 km'
    assert result['upper_bound_km'] is None and result['reported_uncertainty_km'] is None
    assert result['whole_current_length_km'] is None and result['physical_length_lower_bound_km'] is None
    assert result['rank_eligible'] is False
    assert result['coast_proximity_context_km'] == 7 and result['coast_proximity_is_current_width'] is False
    assert f == fixture()


@pytest.mark.parametrize('value', [0, -1, float('nan'), float('inf'), True, '42'])
def test_invalid_thresholds_reject(value):
    f = fixture(); f['reported_threshold_km'] = value
    with pytest.raises(ValueError): method.constraint(f)


@pytest.mark.parametrize('field,value', [
    ('relation', 'ge'), ('quantity', 'whole_current_length'), ('unit', 'm'),
    ('reported_upper_bound_km', 100), ('source_uncertainty_km', 0),
    ('whole_current_length_admitted', True), ('physical_width_admitted', True),
    ('annual_or_seasonal_range_admitted', True), ('current_geometry_admitted', True),
    ('coast_proximity_is_current_width', True), ('entity_id', 'current:another'),
    ('spatial_support', ['A'])])
def test_scope_changes_and_fabricated_information_reject(field, value):
    f = fixture(); f[field] = value
    with pytest.raises(ValueError): method.constraint(f)


@pytest.mark.parametrize('field,value', [
    ('reported_study_window', ['2000-01-20', '2000-01-01']),
    ('ship_cruise_window', ['1999-12-31', '2000-01-19']),
    ('ship_cruise_window', ['2000-01-02', '2000-01-21']),
    ('publication_year', 1999)])
def test_inconsistent_support_chronology_rejects(field, value):
    f = fixture(); f[field] = value
    with pytest.raises(ValueError): method.constraint(f)


def test_temporal_and_spatial_support_copies_are_not_shared():
    f = fixture(); result = method.constraint(f)
    result['regional_support'].append('C'); result['study_window'][0] = 'bad'
    assert f == fixture()


def test_figure_preserves_open_bound_and_textual_alternative():
    report = {'constraint': method.constraint(fixture())}
    output = method.figure(report).decode('utf8')
    assert '&gt;42 km' in output
    assert 'No finite upper endpoint' in output
    assert 'arrow is not geography' in output
    assert 'not current width' in output
    assert 'aria-labelledby="title desc"' in output
