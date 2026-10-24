"""Tiny synthetic vectors only; no original arrays, network or map rendering."""
import math
import numpy as np
import pytest

import west_greenland_core_width_math_v1 as method


def test_hour_alignment_preserves_small_signed_source_offsets():
    hours, offsets = method.align_hours(np.array([0, 1 / 24, 2 / 24]) + np.array([0, -1, 1.5]) / 86400)
    assert hours.tolist() == [0, 1, 2]
    assert offsets.tolist() == pytest.approx([0, -1, 1.5], abs=1e-9)


@pytest.mark.parametrize('values', [[0, 0], [1 / 24, 0], [0, 3 / 86400], [np.nan], [-1], [90001], [[0]], []])
def test_bad_time_vectors_cannot_be_silently_aligned(values):
    with pytest.raises(ValueError):method.align_hours(values)


def test_hour_grid_gaps_are_not_removed_by_alignment():
    indices, _ = method.align_hours([0, 1 / 24, 3 / 24])
    assert indices.tolist() == [0, 1, 3]


def test_rotation_has_independent_compass_sign_and_orthogonality():
    bearing = math.radians(method.BEARING_DEGREES_TRUE)
    along, cross = method.rotate(math.sin(bearing), math.cos(bearing))
    assert along == pytest.approx(1) and cross == pytest.approx(0, abs=1e-15)
    along, cross = method.rotate(math.sin(bearing - math.pi / 2), math.cos(bearing - math.pi / 2))
    assert along == pytest.approx(0, abs=1e-15) and cross == pytest.approx(1)
    a, c = method.rotate(3, 4)
    assert a * a + c * c == pytest.approx(25)


def test_layer_average_matches_analytic_linear_profile_with_moving_depth():
    depth = np.array([[40, 60, 80, 110], [45, 70, 95, 120]])
    east = depth / 100
    north = 2 * depth / 100
    a, c, reasons = method.layer_velocity(east, north, depth)
    expected = method.rotate(.75, 1.5)
    assert a.tolist() == pytest.approx([expected[0]] * 2)
    assert c.tolist() == pytest.approx([expected[1]] * 2)
    assert reasons == ['available_layer'] * 2


@pytest.mark.parametrize('depth,reason', [([60, 80, 100, 120], 'layer_not_bracketed'),
                                         ([20, 40, 80, 100], 'vertical_gap_exceeds_limit'),
                                         ([40, 60, 60, 110], 'duplicate_supplied_depth')])
def test_unsupported_layers_are_not_extrapolated(depth, reason):
    a, c, reasons = method.layer_velocity([[1] * 4], [[2] * 4], [depth])
    assert np.isnan(a[0]) and np.isnan(c[0]) and reasons == [reason]


def test_masked_velocity_does_not_supply_a_depth_bracket():
    u = np.ma.array([[1, 1, 1, 1]], mask=[[1, 1, 0, 0]])
    a, _, reasons = method.layer_velocity(u, [[2] * 4], [[40, 60, 80, 100]])
    assert np.isnan(a[0]) and reasons == ['insufficient_paired_depth_cells']


def test_filter_preserves_a_constant_and_never_crosses_a_gap():
    source = np.r_[np.ones(300) * .3, np.nan, np.ones(300) * .8]
    filtered, segments = method.filter_segments(source)
    assert len(segments) == 2
    assert all(s['retained_hours'] == 84 for s in segments)
    assert np.isnan(filtered[:108]).all() and np.isnan(filtered[192:409]).all()
    assert filtered[108:192] == pytest.approx([.3] * 84)
    assert filtered[409:493] == pytest.approx([.8] * 84)


def test_short_filter_segments_are_explicitly_rejected():
    output, segments = method.filter_segments(np.ones(239))
    assert np.isnan(output).all() and segments[0]['status'] == 'short_segment'


def test_filter_reduces_a_twelve_hour_signal_without_claiming_detiding():
    t = np.arange(1000)
    signal = .3 + np.sin(2 * np.pi * t / 12)
    filtered, _ = method.filter_segments(signal)
    interior = filtered[np.isfinite(filtered)]
    assert abs(interior.mean() - .3) < .001
    assert np.ptp(interior) < .03


def month_grid(start='2017-01-01', end='2017-02-01'):
    return np.arange(np.datetime64(start, 'h'), np.datetime64(end, 'h'), np.timedelta64(1, 'h'))


def test_monthly_all_station_means_use_identical_hours():
    hours = month_grid()
    velocity = np.tile(np.arange(len(hours), dtype=float)[:, None], (1, 8))
    velocity[:100, 0] = np.nan
    result = method.monthly_profiles(hours, velocity)[0]
    assert result['calendar_hours'] == 744
    assert result['common_available_hours'] == 644 and result['eligible_for_core_span']
    assert result['conditional_mean_along_m_s'] == pytest.approx([421.5] * 8)
    assert result['station_available_hours'] == [644] + [744] * 7


def test_partial_month_never_becomes_a_complete_month():
    hours = month_grid('2017-01-02')
    result = method.monthly_profiles(hours, np.ones((len(hours), 8)))[0]
    assert result['common_fraction'] > .9
    assert not result['full_calendar_month'] and not result['eligible_for_core_span']


def test_monthly_coverage_and_long_gap_are_separate_rejections():
    hours = month_grid()
    source = np.ones((len(hours), 8));source[:169, 0] = np.nan
    result = method.monthly_profiles(hours, source)[0]
    assert result['common_fraction'] > .7 and result['max_unsupported_run_hours'] == 169
    assert not result['eligible_for_core_span']


def test_calendar_includes_leap_day_and_empty_months():
    hours = month_grid('2016-02-01', '2016-04-01')
    source = np.ones((len(hours), 8));source[:696] = np.nan
    result = method.monthly_profiles(hours, source)
    assert result[0]['calendar_hours'] == 696 and result[0]['conditional_mean_along_m_s'] == [None] * 8
    assert result[1]['calendar_hours'] == 744 and result[1]['eligible_for_core_span']


def test_month_grid_gap_is_not_averaged_away():
    hours = month_grid()[::2]
    with pytest.raises(ValueError):method.monthly_profiles(hours, np.ones((len(hours), 8)))


IDS = [f'LS{i}' for i in range(1, 9)]
X = np.arange(8) * 10


def test_analytic_triangle_has_two_observed_exact_edges():
    result = method.core_span(X, [-.1, 0, .5, 1, .5, 0, -.1, -.2], IDS)
    assert result['span_km'] == 20
    assert result['left_bracket'] == [2, 2] and result['right_bracket'] == [4, 4]
    assert result['status'] == 'resolved_regional_core_span' and not result['full_current_width']


def test_linear_edge_interpolation_is_in_kilometres():
    result = method.core_span(X, [0, .1, .2, 1, .8, .3, .1, 0], IDS)
    assert result['left_cross_km'] == pytest.approx(23.75)
    assert result['right_cross_km'] == pytest.approx(46)
    assert result['span_km'] == pytest.approx(22.25)


@pytest.mark.parametrize('profile,status', [([.8, .8, .8, 1, .8, .3, .1, 0], 'censored'),
                                          ([0, .1, .2, 1, 1, .2, .1, 0], 'ambiguous_peak'),
                                          ([0, 1, .2, .8, .6, .2, .1, 0], 'peak_outside_upper_slope_anchors'),
                                          ([0, .01, .02, .08, .06, .02, .01, 0], 'peak_below_diagnostic_floor'),
                                          ([0, .1, np.nan, 1, .8, .3, .1, 0], 'missing_station_no_interpolation'),
                                          ([0, .65, .55, 1, .8, .3, .1, 0], 'merged_secondary_core'),
                                          ([.8, .5, .5, 1, .8, .3, .1, 0], 'censored'),
                                          ([.5, .7, .8, 1, .8, .3, .1, 0], 'censored')])
def test_unresolved_core_cases_keep_null_dimensions(profile, status):
    result = method.core_span(X, profile, IDS)
    assert result['status'] == status and result['span_km'] is None


def test_secondary_flat_core_is_not_missed_by_strict_peak_comparison():
    ids = ['LS0'] + IDS
    result = method.core_span(np.arange(9) * 10, [0, .65, .65, .55, 1, .8, .3, .1, 0], ids)
    assert result['status'] == 'merged_secondary_core'


def test_threshold_touch_without_exit_is_censored():
    result = method.core_span(X, [.3, .6, .5, 1, .8, .3, .1, 0], IDS)
    assert result['status'] == 'censored' and result['left_censoring'] == 'threshold_touch_without_exit'


@pytest.mark.parametrize('coordinates,fraction', [(X[::-1], .5), (X, .3), ([0] * 8, .5)])
def test_undeclared_geometry_or_sensitivity_rejected(coordinates, fraction):
    with pytest.raises(ValueError):method.core_span(coordinates, [0, .1, .2, 1, .8, .3, .1, 0], IDS, fraction)


def test_sensitivity_alternatives_are_preserved_individually():
    profile = [0, .1, .2, 1, .8, .3, .1, 0]
    results = [method.core_span(X, profile, IDS, fraction) for fraction in method.THRESHOLD_FRACTIONS]
    assert [r['fraction_of_peak'] for r in results] == [.4, .5, .6]
    assert results[0]['span_km'] > results[1]['span_km'] > results[2]['span_km']
