"""Bounded synthetic diagnostics; no source fields, IO, builds or rendering."""
import json
import math

import numpy as np
import pytest

from eacc_model_core_diagnostic_v2 import (
    connected_spans, diagnose_months, diagnose_year, diagnostic_case, section,
)
from indian_secc_local_normals import Field, GEOD, peak_audit, profile


def jet(sigma=40, coarse=False):
    x = np.linspace(38, 44, 121)
    y = np.array([-11., -10., -9., -8., -7.]) if coarse else np.linspace(-11, -7, 81)
    distance = np.array([GEOD.inv(40, -9, float(lon), -9)[2] / 1000 for lon in x])
    v = np.tile(.4 * np.exp(-.5 * (distance / sigma) ** 2), (len(y), 1))
    return Field(x, y, np.zeros_like(v), v)


@pytest.mark.parametrize('step', [5, 10])
def test_northward_gaussian_recovers_independent_threshold_spans(step):
    field = jet()
    station = section(field, (40, -9), step, 0)
    assert station['local_candidate_axis_check']
    for threshold in station['threshold_cases']:
        expected = 2 * 40 * math.sqrt(-2 * math.log(threshold['fraction']))
        assert threshold['status'] == 'resolved_regional_model_core_diagnostic'
        assert abs(threshold['resolved_span_km'] - expected) < 1
        assert threshold['native_cell_scale_km'] > 5
        assert threshold['span_in_native_cell_scales'] >= 4
        assert threshold['current_association_verified'] is False
        assert threshold['effective_resolution_verified'] is False
        edges = threshold['edges']
        assert edges['negative_normal']['offset_km'] < 0 < edges['positive_normal']['offset_km']
        assert edges['negative_normal']['point_lon_lat'][0] < 40 < edges['positive_normal']['point_lon_lat'][0]


def test_anisotropic_native_grid_cannot_be_resolved_by_finer_display_steps():
    field = jet(coarse=True)
    station = section(field, (40, -9), 5, 0)
    assert station['local_candidate_axis_check']
    for threshold in station['threshold_cases']:
        assert threshold['diagnostic_span_km'] > 0
        assert threshold['resolved_span_km'] is None
        assert threshold['status'] == 'insufficient_native_resolution'
        assert threshold['native_cell_scale_km'] > 100


def test_resolution_includes_wider_cells_away_from_peak():
    x = np.array([38, 39, 39.8, 40, 40.05, 40.1, 40.8, 41, 42, 44])
    y = np.linspace(-11, -7, 81)
    distance = np.array([GEOD.inv(40, -9, float(lon), -9)[2] / 1000 for lon in x])
    v = np.tile(.4 * np.exp(-.5 * (distance / 40) ** 2), (len(y), 1))
    field = Field(x, y, np.zeros_like(v), v)
    half = section(field, (40, -9), 5, 0)['threshold_cases'][1]
    assert half['diagnostic_span_km'] > 0
    assert half['native_cell_scale_km'] > 75  # center alone would imply about 5.5 km
    assert half['status'] == 'insufficient_native_resolution'
    assert half['resolved_span_km'] is None


def test_one_sided_mask_retains_other_edge_without_doubling_it():
    field = jet()
    field.u[:, 49] = np.nan  # just past +40 km, before the half-peak crossing
    station = section(field, (40, -9), 5, 0)
    assert station['local_candidate_axis_check']
    half = station['threshold_cases'][1]
    assert half['status'] == 'unresolved_edge_pair'
    assert half['diagnostic_span_km'] is half['resolved_span_km'] is None
    assert half['edges']['negative_normal']['status'] == 'connected_sampled_crossing'
    assert 'before_crossing' in half['edges']['positive_normal']['status']
    assert any(row[-1] != 'ok' for row in station['samples'])


def test_domain_edge_is_not_a_velocity_crossing():
    field = jet()
    field = Field(field.x[:49], field.y, field.u[:, :49], field.v[:, :49])
    station = section(field, (40, -9), 5, 0)
    assert station['local_candidate_axis_check']
    half = station['threshold_cases'][1]
    assert half['status'] == 'unresolved_edge_pair'
    assert half['edges']['positive_normal']['status'] == 'outside_source_before_crossing'
    assert half['resolved_span_km'] is None


def test_unseparated_secondary_rise_censors_connected_core():
    field = jet(sigma=50)
    signed = np.array([math.copysign(GEOD.inv(40, -9, float(x), -9)[2] / 1000, x - 40) for x in field.x])
    field.v += .35 * np.exp(-.5 * ((signed - 85) / 15) ** 2)
    station = section(field, (40, -9), 5, 0)
    assert station['local_candidate_axis_check']
    for threshold in station['threshold_cases']:
        assert threshold['status'] == 'unresolved_edge_pair'
        assert threshold['edges']['positive_normal']['status'] == 'unresolved_rise_before_crossing'
        assert threshold['resolved_span_km'] is None


def test_separated_second_band_does_not_replace_first_crossing():
    field = jet(sigma=25)
    signed = np.array([math.copysign(GEOD.inv(40, -9, float(x), -9)[2] / 1000, x - 40) for x in field.x])
    field.v += .6 * np.exp(-.5 * ((signed - 170) / 15) ** 2)
    half = section(field, (40, -9), 5, 0)['threshold_cases'][1]
    assert half['status'] == 'resolved_regional_model_core_diagnostic'
    assert half['edges']['positive_normal']['offset_km'] < 35


def test_displaced_peak_does_not_pass_the_local_axis_gate():
    field = jet()
    station = section(field, (39.8, -9), 5, 0)
    assert station['local_candidate_axis_check'] is False
    assert 'streamline_peak_displacement_exceeds_10km' in station['failed_axis_checks']
    half = station['threshold_cases'][1]
    assert half['diagnostic_span_km'] > 0
    assert half['status'] == 'local_axis_unresolved'
    assert half['resolved_span_km'] is None


def test_direction_change_at_peak_prevents_axis_support():
    field = jet()
    field.u[:, 40] = .2
    station = section(field, (39.9, -9), 5, 0)
    assert station['local_candidate_axis_check'] is False
    assert 'peak_direction_difference_exceeds_15degrees' in station['failed_axis_checks']


def test_tied_profile_peaks_are_not_forced_into_spans():
    field = jet()
    data = profile(field, (40, -9), 5)
    center = next(i for i, row in enumerate(data['rows']) if row['s'] == 0)
    data['rows'][center + 1]['q'] = data['rows'][center]['q']
    peak = peak_audit(data)
    assert peak['status'] == 'numerically_tied_peak'
    assert all(row['resolved_span_km'] is None for row in connected_spans(field, data, peak, False))


@pytest.mark.parametrize('step', [5, 10])
def test_five_station_northward_case_does_not_claim_current_identity(step):
    result = diagnostic_case(jet(), 6, 0, step)
    assert result['status'] == 'five_station_diagnostic_supported'
    assert result['all_five_local_axis_checks_pass']
    assert result['all_five_half_peak_spans_resolved']
    assert [row['station_arc_parameter_km'] for row in result['stations']] == [-100, -50, 0, 50, 100]
    assert len(result['paths']) == 4
    assert all(row['status'] == 'target_station_reached' for row in result['paths'])
    for name in ['current_association_verified', 'annual_physical_range_admitted',
                 'physical_state_join_eligible', 'length_rank_eligible', 'width_rank_eligible']:
        assert result[name] is False
    assert result['whole_current_width_km'] is result['whole_current_length_km'] is None
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize('offset', [-1, 1])
def test_neighbor_seed_gets_only_sensitivity_section(offset):
    result = diagnostic_case(jet(), 6, offset, 5)
    assert result['status'] == 'seed_sensitivity_section_only'
    assert len(result['stations']) == 1 and result['paths'] == []
    assert not result['all_five_half_peak_spans_resolved']


def test_short_domain_retains_partial_path_failure():
    field = jet()
    take = (field.y >= -9.2) & (field.y <= -8.8)
    short = Field(field.x, field.y[take], field.u[take], field.v[take])
    result = diagnostic_case(short, 6, 0, 5)
    assert result['status'] == 'candidate_diagnostic_unresolved'
    assert len(result['stations']) == 1
    assert len(result['paths']) == 2
    assert all(row['status'] != 'target_station_reached' for row in result['paths'])


def test_missing_months_and_failed_months_are_all_retained():
    weak = jet()
    weak.v[:, :] = 0
    results = diagnose_months({6: weak})
    assert len(results) == 72 and len({row['id'] for row in results}) == 72
    assert sum(row['status'] == 'missing_month_field' for row in results) == 66
    assert sum(row['status'] == 'weak_or_non_northward_seed' for row in results) == 6
    assert not any(row['all_five_half_peak_spans_resolved'] for row in results)


@pytest.mark.parametrize('month,offset,step', [(0, 0, 5), (13, 0, 5), (True, 0, 5),
                                           (1, 2, 5), (1, True, 5), (1, 0, 1), (1, 0, True)])
def test_invalid_case_definitions_cannot_change_method_silently(month, offset, step):
    with pytest.raises(ValueError):
        diagnostic_case(None, month, offset, step)


@pytest.mark.parametrize('months', [{0: None}, {13: None}, {'6': None}, {True: None}])
def test_unexpected_month_keys_fail(months):
    with pytest.raises(ValueError):
        diagnose_months(months)


def test_year_summary_preserves_all_unsupported_comparisons_without_numeric_zeros():
    report = diagnose_year({})
    assert report['case_count'] == 72 and len(report['months']) == 12
    assert len(report['normal_step_comparisons']) == 84
    assert len(report['native_seed_comparisons']) == 48
    for comparison in report['normal_step_comparisons'] + report['native_seed_comparisons']:
        for threshold in comparison['thresholds']:
            assert threshold['a_status'] == threshold['b_status'] == 'missing_month_field'
            assert threshold['a_resolved_span_km'] is threshold['b_resolved_span_km'] is None
            assert threshold['b_minus_a_km'] is None
    for month in report['months']:
        assert not month['both_five_station_half_peak_diagnostics_supported']
    assert report['annual_physical_minimum_width_km'] is report['annual_physical_maximum_width_km'] is None
    json.dumps(report, allow_nan=False)


def test_year_summary_keeps_step_and_seed_sensitivity_distinct_from_physical_range():
    report = diagnose_year({6: jet()})
    assert report['months'][5]['both_five_station_half_peak_diagnostics_supported']
    assert sum(row['status'] == 'missing_month_field' for row in report['cases']) == 66
    central_step = next(row for row in report['normal_step_comparisons']
                        if row['a_case_id'] == 'm06:offset0:step5' and row['station_arc_parameter_km'] == 0)
    half = central_step['thresholds'][1]
    assert half['b_minus_a_km'] == pytest.approx(half['b_resolved_span_km'] - half['a_resolved_span_km'])
    assert report['measurement_uncertainty_km'] is None
    assert report['source_identity_verified'] is report['current_association_verified'] is False
    assert report['annual_physical_minimum_width_km'] is report['annual_physical_maximum_width_km'] is None
    json.dumps(report, allow_nan=False)
