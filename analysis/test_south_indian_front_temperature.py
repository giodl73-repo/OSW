"""Derived monthly source must preserve actual daily support and raw means."""
import copy

import numpy as np
import pytest

from acquire_south_indian_front_levels import common_means, FIELDS
from build_south_indian_front_temperature import converted_month, nullable, THETA


def fixture():
    scale = float(np.float32(.001))
    offsets = {'water_u': 0., 'water_v': 0., 'water_temp': 20., 'salinity': 20.}
    fields = {n: np.zeros((5, 2, 2, 1), dtype='<i2') for n in FIELDS}
    fields['salinity'][:] = 15000
    fields['water_temp'][:, 0, :, :] = np.arange(5)[:, None, None]*1000-10000
    fields['water_temp'][:, 1, :, :] = np.arange(5)[:, None, None]*2000-15000
    fields['water_u'][:2, 0, 0, 0] = -30000
    counts, means = common_means(fields, 4, scale, offsets)
    raw = {'month': 1, 'sample_days': 5, 'minimum_common_samples': 4,
           'common_samples': counts.tolist(), 'fields': {n: nullable(a) for n, a in means.items()}}
    times = np.arange(5, dtype=float)*24
    grids = [{**{n: a[:3] for n, a in fields.items()}, 'time': times[:3]},
             {**{n: a[3:] for n, a in fields.items()}, 'time': times[3:]}]
    return grids, times, raw, scale, offsets


def run(grids, times, raw, scale, offsets):
    return converted_month(grids, times, raw, [100, 200], [-45, -35], [80], scale, offsets)


def test_month_retains_raw_counts_nulls_and_distinct_temperature():
    args = fixture(); result = run(*args)
    assert np.array_equal(result['common_samples'], args[2]['common_samples'])
    assert result['common_samples'][0, 0, 0] == 3
    assert np.isnan(result[THETA][0, 0, 0])
    assert np.isfinite(result[THETA][1]).all()
    source_t = np.asarray(args[2]['fields']['water_temp'], dtype=float)
    assert np.all(result[THETA][1] < source_t[1])
    assert np.all(result['absolute_salinity_g_kg'][1] > 35)
    assert np.all(result['sea_pressure_dbar'][1] > 200)
    assert nullable(result[THETA])[0][0][0] is None


@pytest.mark.parametrize('change', ['empty', 'reorder', 'missing', 'duplicate', 'sample_days', 'count', 'mean'])
def test_derived_source_does_not_repair_or_hide_invalid_raw_support(change):
    grids, times, raw, scale, offsets = fixture()
    if change == 'empty': grids = []
    if change == 'reorder': grids.reverse()
    if change == 'missing': grids.pop()
    if change == 'duplicate': grids.append(copy.deepcopy(grids[-1]))
    if change == 'sample_days': raw['sample_days'] -= 1
    if change == 'count': raw['common_samples'][1][1][0] -= 1
    if change == 'mean': raw['fields']['water_temp'][1][1][0] += 1e-9
    with pytest.raises(ValueError): run(grids, times, raw, scale, offsets)
