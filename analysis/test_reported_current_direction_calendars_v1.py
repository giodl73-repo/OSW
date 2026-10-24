"""Prospective synthetic calendar semantics; no actual source report executed."""
import copy
import xml.etree.ElementTree as ET

import pytest

import reported_current_direction_calendars_v1 as method


def fixture():
    return {'id': 'synthetic', 'entity_id': 'current:synthetic',
            'reported_periods': [{'start_month': 11, 'end_month': 2, 'direction': 'northward'}],
            'time_support_kind': 'source_described_annual_direction_pattern_not_monthly_observations',
            'observation_window': None, 'observation_year': None, 'velocity_m_s': None,
            'length_km': None, 'width_km': None, 'annual_dimension_ranges': None,
            'physical_geometry_admitted': False, 'geographic_seasonal_playback_eligible': False,
            'ranking_eligible': False}


@pytest.mark.parametrize('start,end,expected', [(11, 2, [11, 12, 1, 2]),
                                             (4, 6, [4, 5, 6]), (5, 5, [5]),
                                             (1, 12, list(range(1, 13)))])
def test_inclusive_source_periods_wrap_without_inventing_a_year(start, end, expected):
    assert method.interval(start, end) == expected


@pytest.mark.parametrize('value', [0, 13, True, 1.0, '1', None])
def test_invalid_month_values_reject(value):
    with pytest.raises(ValueError): method.interval(value, 2)
    with pytest.raises(ValueError): method.interval(2, value)


def test_unknown_months_are_null_not_transition_or_zero_flow():
    source = fixture(); before = copy.deepcopy(source)
    rows = method.calendar(source)
    assert [r['month'] for r in rows] == list(range(1, 13))
    assert [r['month'] for r in rows if r['direction'] == 'northward'] == [1, 2, 11, 12]
    assert all(r['direction'] is None and r['value_status'] == 'not_specified_by_source'
               for r in rows if r['month'] in range(3, 11))
    assert all(r['is_observation'] is False and r['observed_velocity_m_s'] is None
               and r['observation_date'] is None and r['observation_year'] is None
               and r['physical_geometry'] is None and r['ranking_eligible'] is False for r in rows)
    assert source == before


@pytest.mark.parametrize('field,value', [('entity_id', 'eddy:synthetic'),
                                       ('time_support_kind', 'monthly_observations'),
                                       ('observation_window', ['1998-01-01', '1998-12-31']),
                                       ('observation_year', 1998), ('velocity_m_s', 0),
                                       ('length_km', 100), ('width_km', 0),
                                       ('annual_dimension_ranges', [0, 1]),
                                       ('physical_geometry_admitted', True),
                                       ('geographic_seasonal_playback_eligible', True),
                                       ('ranking_eligible', True)])
def test_invented_physical_and_temporal_support_rejects(field, value):
    source = fixture(); source[field] = value
    with pytest.raises(ValueError): method.calendar(source)


@pytest.mark.parametrize('periods', [[],
    [{'start_month': 1, 'end_month': 3, 'direction': 'northward'},
     {'start_month': 3, 'end_month': 4, 'direction': 'southward'}],
    [{'start_month': 1, 'end_month': 3, 'direction': 'northward'},
     {'start_month': 1, 'end_month': 3, 'direction': 'northward'}],
    [{'start_month': 1, 'end_month': 3, 'direction': 'eastward'}]])
def test_empty_overlapping_duplicate_or_unsupported_source_periods_reject(periods):
    source = fixture(); source['reported_periods'] = periods
    with pytest.raises(ValueError): method.calendar(source)


def test_saved_figure_format_has_textual_qualifications_and_non_color_unknowns():
    source = fixture(); rows = method.calendar(source)
    profile = {'display_name': 'Synthetic & Coastal Current', 'figure_source_label': 'Synthetic source', 'months': rows}
    output = method.figure({'profiles': [profile, profile]})
    tree = ET.fromstring(output); text = ' '.join(tree.itertext())
    assert tree.attrib['aria-labelledby'] == 'title desc'
    assert 'Synthetic & Coastal Current' in text
    assert 'not monthly measurements or daily predictions' in text
    assert 'not zero flow or inferred transition phases' in text
    assert 'not specified in the source summary' in text
    assert 'publisher abstract only' in text
    assert text.count('?') >= 8
