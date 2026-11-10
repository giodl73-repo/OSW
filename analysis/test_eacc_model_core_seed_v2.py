"""Tiny synthetic fields only: no original model arrays, network or rendering."""
import math
import json
from pathlib import Path

import numpy as np
import pytest

from eacc_model_core_seed_v2 import northward_support, offset_seed, select_anchor
from indian_secc_local_normals import GEOD, Field, peak_audit, profile, spans


def jet():
    x = np.linspace(38, 44, 121)
    y = np.array([-11., -10., -9., -8., -7.])
    # A straight northward Gaussian with sigma=40 km on the 9 S parallel.
    distance = np.array([GEOD.inv(40, -9, float(lon), -9)[2] / 1000 for lon in x])
    v = np.tile(.4 * np.exp(-.5 * (distance / 40) ** 2), (len(y), 1))
    return Field(x, y, np.zeros_like(v), v)


@pytest.mark.parametrize('u,v,status', [
    (0, .1, 'supported_northward_seed'),
    (.1, .1, 'supported_northward_seed'),
    (-.1, .1, 'supported_northward_seed'),
    (.10001, .1, 'seed_direction_exceeds_45degrees'),
    (0, .09999, 'weak_or_non_northward_seed'),
    (.5, 0, 'weak_or_non_northward_seed'),
    (0, -.5, 'weak_or_non_northward_seed'),
    (math.nan, .5, 'missing_paired_velocity'),
    (0, math.inf, 'missing_paired_velocity'),
])
def test_true_east_north_vector_guard(u, v, status):
    assert northward_support(u, v)['status'] == status


def test_gaussian_selects_northward_native_anchor_and_recovers_known_span():
    field = jet()
    anchor = select_anchor(field)
    assert anchor['status'] == 'supported_northward_seed'
    assert anchor['selected_lon_lat'] == [40., -9.]
    assert anchor['current_association_verified'] is False
    data = profile(field, tuple(anchor['selected_lon_lat']), 5)
    peak = peak_audit(data)
    assert peak['status'] == 'supported_local_peak'
    width = spans(field, data, peak)[1]
    expected = 2 * 40 * math.sqrt(2 * math.log(2))
    assert width['status'] == 'paired_sampled_edges'
    # Bound accounts for finite native bilinear sampling and geodesic geometry.
    assert abs(width['span_km'] - expected) < 1
    negative, positive = data['rows'][0], data['rows'][-1]
    assert negative['point'][0] < 40 < positive['point'][0]


def test_larger_eastward_velocity_does_not_replace_largest_northward_vector():
    field = jet()
    field.u[:, :] = 0
    field.u[:, 30] = 2
    assert select_anchor(field)['selected_lon_lat'] == [40., -9.]


def test_failed_winner_direction_does_not_fall_back_to_second_peak():
    field = jet()
    field.u[:, 40] = 1
    anchor = select_anchor(field)
    assert anchor['status'] == 'seed_direction_exceeds_45degrees'
    assert anchor['selected_longitude_index'] == 40


def test_numerical_peak_ties_are_retained_without_arbitrary_winner():
    field = jet()
    field.v[2, 41] = field.v[2, 40] - 5e-11
    anchor = select_anchor(field)
    assert anchor['status'] == 'numerically_tied_northward_peaks'
    assert anchor['tied_longitude_indices'] == [40, 41]
    assert anchor['selected_longitude_index'] is None


def test_missing_zero_weight_corner_prevents_seed_without_fallback():
    field = jet()
    field.u[3, 41] = np.nan
    anchor = select_anchor(field)
    assert anchor['status'] == 'missing_seed_bilinear_corners'
    assert anchor['selected_longitude_index'] == 40


def test_missing_cells_counted_without_treating_them_as_zero():
    field = jet()
    field.u[2, 25] = np.nan
    anchor = select_anchor(field)
    assert anchor['status'] == 'supported_northward_seed'
    assert anchor['missing_paired_candidate_count'] == 1
    assert anchor['paired_candidate_count'] == 40


def test_missing_window_and_outside_latitude_have_explicit_failures():
    field = jet()
    field.v[2, :] = np.nan
    assert select_anchor(field)['status'] == 'missing_seed_window'
    outside = Field([39, 40], [-8, -7], np.zeros((2, 2)), np.ones((2, 2)))
    assert select_anchor(outside)['status'] == 'target_latitude_outside_source'


def test_equidistant_native_rows_record_fixed_southern_primary_rule():
    field = Field([39, 40, 41], [-10, -8], np.zeros((2, 3)), np.array([[.2,.4,.2],[.2,.4,.2]]))
    anchor = select_anchor(field)
    assert anchor['status'] == 'supported_northward_seed'
    assert anchor['nearest_latitude_indices'] == [0, 1]
    assert anchor['selected_lon_lat'] == [40, -10]
    assert anchor['latitude_tie_rule'] == 'southern_row_primary_northern_row_sensitivity'
    assert offset_seed(field, anchor, 1)['origin_lon_lat'] == [40, -8]


def test_neighbor_seed_keeps_primary_longitude_even_when_other_peak_is_stronger():
    field = jet()
    anchor = select_anchor(field)
    field.v[3, 50] = 1
    neighbor = offset_seed(field, anchor, 1)
    assert neighbor['status'] == 'supported_northward_seed'
    assert neighbor['origin_lon_lat'] == [40, -8]


def test_neighbor_cannot_bypass_unsupported_primary():
    field = jet()
    field.v[2, :] = 0
    anchor = select_anchor(field)
    assert anchor['status'] == 'weak_or_non_northward_seed'
    assert offset_seed(field, anchor, 1)['status'] == 'primary_seed_unsupported'


@pytest.mark.parametrize('offset', [-2, 2, .5, True])
def test_invalid_seed_offset_fails(offset):
    field = jet()
    with pytest.raises(ValueError):
        offset_seed(field, select_anchor(field), offset)


def test_actual_provider_coordinates_with_synthetic_flow_keep_both_tied_rows():
    # Only provider coordinate metadata is original; velocities are synthetic.
    root = Path(__file__).resolve().parents[1]
    plan = json.loads((root / 'research/eacc-hycom-2013-source-selection-candidate-v1.json').read_bytes())
    x = np.array(plan['selected_coordinates']['lon'])
    y = np.array(plan['selected_coordinates']['lat'])
    v = np.tile(.4 * np.exp(-.5 * ((x - 40) / .36) ** 2), (len(y), 1))
    field = Field(x, y, np.zeros_like(v), v)
    anchor = select_anchor(field)
    assert anchor['status'] == 'supported_northward_seed'
    assert anchor['nearest_latitude_indices'] == [49, 50]
    assert anchor['selected_latitude_index'] == 49
    assert anchor['selected_lon_lat'][1] == -9.039999961853027
    assert offset_seed(field, anchor, 1)['origin_lon_lat'][1] == -8.960000038146973
