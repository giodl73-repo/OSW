"""Scientific edge cases for native property support and cross-depth cohorts."""
import copy

import numpy as np
import pytest

from south_indian_front_property_windows import masks, supports, comparisons, selected_times
from south_indian_paired_profiles_v2 import positive_maxima


def test_inclusive_bounds_and_joint_membership():
    m = masks([10, 12, 11, 9.99], [34.6, 35, 34.59, 34.8], [12, 16, 16.01, 11.99],
              [True]*4, [True]*4)
    assert m['stf_theta100'] == [True, True, True, False]
    assert m['stf_sp100'] == [True, True, False, True]
    assert m['stf_joint100'] == [True, True, False, False]
    assert m['arf_theta200'] == [True, True, False, False]


def test_missing_and_ineligible_are_unknown_not_outside():
    m = masks([11, np.nan, 11], [34.8]*3, [14]*3, [False, True, True], [True, False, True])
    assert m['stf_theta100'] == [None, None, True]
    assert m['stf_sp100'] == [None, True, True]
    assert m['stf_joint100'] == [None, None, True]
    assert m['arf_theta200'] == [True, None, True]


@pytest.mark.parametrize('values', [[np.inf], [-np.inf]])
def test_infinite_properties_rejected(values):
    with pytest.raises(ValueError):
        masks(values, [34.8], [14], [True], [True])


def test_integer_eligibility_cannot_silently_cast_to_boolean():
    with pytest.raises(ValueError):
        masks([11], [34.8], [14], [1], [True])


def test_isolated_missing_and_domain_supports_are_retained():
    r = supports([True, False, True, None, True], [-40, -39, -38, -37, -36], 'case')
    assert [a['native_indices'] for a in r] == [[0], [2], [4]]
    assert r[0]['south_flank']['status'] == 'domain_end'
    assert r[1]['north_flank']['status'] == 'unsupported_property'
    assert r[2]['north_flank']['status'] == 'domain_end'
    assert all(a['physical_width_km'] is None and a['physical_edges'] is None for a in r)


def test_contiguous_support_is_not_split_or_interpolated():
    r = supports([False, True, True, False], [-40, -39.5, -39, -38], 'case')
    assert len(r) == 1
    assert r[0]['native_indices'] == [1, 2]
    assert r[0]['latitude_support_degrees_north'] == [-39.5, -39]
    assert r[0]['south_flank']['latitude_degrees_north'] == -40


def test_plateaus_and_all_pairings_not_just_strongest_or_nearest():
    lat = [-40, -39, -38, -37, -36, -35]
    peaks = positive_maxima([0, 1, 1, 0, 2, 0])
    for i, p in enumerate(peaks):
        p['id'] = str(i)
    runs = supports([False, True, False, False, True, False], lat, 'c')
    result = comparisons(peaks, runs, lat, [28]*6, [28]*6, 28)
    assert len(result) == 4
    assert [p['start_index'] for p in peaks] == [1, 4]
    assert peaks[0]['end_index'] == 2
    assert sum(r['native_supports_overlap'] for r in result) == 2
    assert all(r['support_separation_km'] >= 0 for r in result)
    assert all(r['front_identification_verified'] is False and r['current_association_verified'] is False for r in result)


def test_equal_incomplete_counts_do_not_prove_same_days():
    peaks = [{'id': 'p', 'start_index': 0, 'end_index': 0}]
    runs = supports([True, True], [-40, -39], 'c')
    r = comparisons(peaks, runs, [-40, -39], [27, 28], [27, 28], 28)[0]
    assert r['comparison_status'] == 'incomplete_daily_support_not_proven_identical'
    assert r['support_separation_km'] is None and r['native_supports_overlap'] is None


def test_native_int16_counts_keep_complete_cohort():
    peaks = [{'id': 'p', 'start_index': 0, 'end_index': 0}]
    runs = supports([True, False], [-40, -39], 'c')
    counts = np.array([28, 28], dtype=np.int16)
    r = comparisons(peaks, runs, [-40, -39], counts, counts, 28)[0]
    assert r['identical_complete_daily_support'] and r['support_separation_km'] == 0


def test_incomplete_run_interior_cannot_hide_behind_complete_endpoints():
    peaks = [{'id': 'p', 'start_index': 1, 'end_index': 1}]
    runs = supports([True]*3, [-40, -39, -38], 'c')
    r = comparisons(peaks, runs, [-40, -39, -38], [28]*3, [28, 27, 28], 28)[0]
    assert not r['identical_complete_daily_support']


def test_empty_masks_and_no_positive_flow_preserve_no_match():
    assert supports([False, None], [-40, -39], 'c') == []
    assert positive_maxima([-1, 0]) == []
    assert comparisons([], [], [-40, -39], [28]*2, [28]*2, 28) == []


def test_reordered_or_duplicate_time_indices_rejected():
    s = {'requests': [{'month': 1, 'time_indices': [0, 8]}, {'month': 1, 'time_indices': [16]}]}
    assert selected_times(s, 1) == [0, 8, 16]
    bad = copy.deepcopy(s); bad['requests'][1]['time_indices'] = [8]
    with pytest.raises(ValueError):
        selected_times(bad, 1)
    bad = copy.deepcopy(s); bad['requests'].reverse()
    with pytest.raises(ValueError):
        selected_times(bad, 1)


def test_invalid_counts_and_native_axis_rejected():
    with pytest.raises(ValueError):
        comparisons([], [], [-40], [29], [28], 28)
    with pytest.raises(ValueError):
        comparisons([], [], [-40], [28.0], [28], 28)
    with pytest.raises(ValueError):
        supports([True, True], [-39, -40], 'c')
