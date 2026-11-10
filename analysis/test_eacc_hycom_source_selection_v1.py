"""Small synthetic coordinates/packed values; no original velocity arrays."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import math
import json
from urllib.parse import unquote

import numpy as np
import pytest

from eacc_hycom_source_selection_v1 import (
    BASE, DIMENSIONS, MISSING, SCALE, _runs, make_selection, paired_month,
    parse_coordinates, validate_metadata,
)


METADATA = Path(__file__).resolve().parents[1] / 'research/source-data/eacc-hycom-2013-metadata-v1'


def coordinate_text(values):
    return ('Dataset {\n' + ''.join(f'    Float64 {name}[{name} = {len(axis)}];\n' for name, axis in values.items())
            + '} synthetic;\n' + ''.join(f'{name}[{len(axis)}]\n' + ', '.join(map(str, axis)) + '\n' for name, axis in values.items()))


def synthetic_metadata():
    start = (datetime(2013, 1, 1, tzinfo=timezone.utc) - datetime(2000, 1, 1, tzinfo=timezone.utc)).total_seconds() / 3600
    values = {
        'time': [start + 3 * i for i in range(2920) if i not in range(1, 37)],
        'depth': [0, 2, 4, 6, 8, 10, 12, 15] + list(range(20, 84, 2)),
        'lat': np.linspace(-80, 90, DIMENSIONS['lat']).tolist(),
        'lon': [i * .08 for i in range(DIMENSIONS['lon'])],
    }
    metadata = {name: (METADATA / name).read_bytes() for name in ('metadata.dds', 'metadata.das')}
    metadata['coordinates.ascii'] = coordinate_text(values).encode()
    return metadata, values


def hours(month, days):
    origin = datetime(2000, 1, 1, tzinfo=timezone.utc)
    first = datetime(2013, month, 1, tzinfo=timezone.utc)
    return [(first + timedelta(days=day) - origin).total_seconds() / 3600 for day in range(days)]


def test_retained_provider_declarations_pass_without_velocity_payload():
    validate_metadata((METADATA / 'metadata.dds').read_text(), (METADATA / 'metadata.das').read_text())


@pytest.mark.parametrize('old,new', [
    ('eastward_sea_water_velocity', 'northward_sea_water_velocity'),
    ('Float32 scale_factor 0.001;', 'Float64 scale_factor 0.001;'),
    ('String units "m/s";', 'String units "cm/s";'),
    ('Int16 missing_value -30000;', 'Int16 missing_value -32768;'),
    ('String positive "down";', 'String positive "up";'),
    ('String calendar "gregorian";', 'String calendar "360_day";'),
    ('Approved for public release. Distribution unlimited.', 'No distribution statement'),
])
def test_changed_coordinate_frame_packing_or_terms_are_rejected(old, new):
    with pytest.raises(ValueError):
        validate_metadata((METADATA / 'metadata.dds').read_text(), (METADATA / 'metadata.das').read_text().replace(old, new))


def test_selection_uses_exact_depth_and_all_available_daily_00z_indices_once():
    metadata, values = synthetic_metadata()
    result = make_selection(metadata)
    assert result['selection']['depth'] == [7]
    assert result['provider_depth_m'] == 15
    assert result['minimum_pairs'] == [25, 23, 25, 24, 25, 24, 25, 25, 24, 25, 24, 25]
    expected = [i for i, value in enumerate(values['time']) if (value - values['time'][0]) % 24 == 0]
    actual = [i for request in result['requests'] for i in request['time_indices']]
    assert actual == expected and len(actual) == len(set(actual)) == 361
    assert len(result['missing_daily_00z']) == 4
    for request in result['requests']:
        assert len(request['time_indices']) <= 6
        assert request['url'].startswith(BASE + '.ascii?')
        decoded = unquote(request['url'])
        assert 'water_u[' in decoded and ',water_v[' in decoded and '][7][' in decoded
        assert 'water_temp' not in decoded
    assert result['max_concurrent_requests'] == 1
    assert not result['velocity_acquisition_allowed']
    assert not result['source_request_preflight_frozen']


def test_retained_candidate_reconstructs_from_exact_provider_coordinate_metadata():
    root = METADATA.parents[2]
    metadata = {name: (METADATA / name).read_bytes() for name in ('metadata.dds', 'metadata.das')}
    metadata['coordinates.ascii'] = (root / 'research/source-data/eacc-hycom-2013-coordinates-v1/coordinates.ascii').read_bytes()
    result = make_selection(metadata)
    retained = json.loads((root / 'research/eacc-hycom-2013-source-selection-candidate-v1.json').read_bytes())
    assert result == retained
    assert len(result['requests']) == 82
    assert sum(len(row['time_indices']) for row in result['requests']) == 363
    assert result['selection']['depth'] == [7]
    assert result['missing_daily_00z'] == ['2013-08-14T00:00:00+00:00', '2013-12-25T00:00:00+00:00']


@pytest.mark.parametrize('indices', [[], [3], [1, 9, 17, 25, 26, 34], list(range(19))])
def test_index_runs_preserve_irregular_indices_exactly_without_overlap(indices):
    runs = _runs(indices)
    assert [i for run in runs for i in run] == indices
    assert all(1 <= len(run) <= 6 for run in runs)
    for run in runs:
        if len(run) > 2:
            assert len({b - a for a, b in zip(run, run[1:])}) == 1


@pytest.mark.parametrize('axis,mutation', [
    ('depth', lambda a: [x + .01 if x == 15 else x for x in a]),
    ('lat', lambda a: list(reversed(a))),
    ('lon', lambda a: [x + 50 for x in a]),
    ('time', lambda a: a[:-1]),
    ('time', lambda a: [x + .5 for x in a]),
    ('time', lambda a: [x - 9000 for x in a]),
])
def test_source_selection_refuses_altered_or_inadequate_coordinates(axis, mutation):
    metadata, values = synthetic_metadata()
    values[axis] = mutation(values[axis])
    metadata['coordinates.ascii'] = coordinate_text(values).encode()
    with pytest.raises(ValueError):
        make_selection(metadata)


@pytest.mark.parametrize('text', [
    'not a DAP response',
    coordinate_text({'time': [1], 'depth': [15], 'lat': [-9], 'lon': [math.nan]}),
    coordinate_text({'time': [1, 1], 'depth': [15], 'lat': [-9], 'lon': [40]}),
    coordinate_text({'time': [1], 'depth': [15], 'lat': [-9]}),
    coordinate_text({'time': [1], 'depth': [15], 'lat': [-9], 'lon': [40]}).replace('lon[1]', 'lon[2]'),
])
def test_malformed_coordinate_responses_are_not_accepted(text):
    with pytest.raises(ValueError):
        parse_coordinates(text)


def test_monthly_pairing_uses_identical_valid_days_for_both_components():
    u = np.full((31, 1, 2), 1000, dtype='<i2')
    v = np.full_like(u, 2000)
    u[0:6, 0, 0] = MISSING  # 25 paired days, just sufficient in January
    v[6, 0, 1] = MISSING
    u[0:6, 0, 1] = MISSING  # 24 paired days, insufficient for both components
    v[0:6, 0, 0] = 30000  # invalid U days must not contribute to V's mean
    result = paired_month(u, v, 1, hours(1, 31))
    assert result['pair_count'].tolist() == [[25, 24]]
    assert result['eastward_m_s'][0, 0] == 1000 * SCALE
    assert result['northward_m_s'][0, 0] == 2000 * SCALE
    assert np.isnan(result['eastward_m_s'][0, 1]) and np.isnan(result['northward_m_s'][0, 1])


def test_missing_provider_days_do_not_lower_calendar_day_threshold():
    u = np.full((24, 1, 1), 100, dtype='<i2')
    result = paired_month(u, u, 1, hours(1, 24))
    assert result['minimum_pairs'] == 25 and result['sample_days'] == 24
    assert np.isnan(result['eastward_m_s']).all()


def test_packed_integer_sum_precedes_exact_binary32_scaling():
    u = np.array([32767, -32768] * 12 + [123], dtype='<i2').reshape(25, 1, 1)
    result = paired_month(u, -u, 1, hours(1, 25))
    expected = sum(int(value) for value in u[:, 0, 0]) * SCALE / 25
    assert result['eastward_m_s'][0, 0] == expected
    assert SCALE == float(np.float32(.001)) and SCALE != .001


def test_completely_missing_month_has_zero_counts_and_null_means_not_zero_flow():
    empty = np.empty((0, 2, 2), dtype='<i2')
    result = paired_month(empty, empty, 2, [])
    assert result['sample_days'] == 0 and result['minimum_pairs'] == 23
    assert result['pair_count'].tolist() == [[0, 0], [0, 0]]
    assert np.isnan(result['eastward_m_s']).all() and np.isnan(result['northward_m_s']).all()


@pytest.mark.parametrize('sample_hours', [hours(1, 25)[::-1], hours(1, 24) + hours(1, 1),
                                       hours(2, 25), [x + 3 for x in hours(1, 25)],
                                       [x + .01 for x in hours(1, 25)], hours(1, 24)])
def test_duplicate_non_midnight_reordered_or_wrong_month_times_fail(sample_hours):
    u = np.zeros((25, 1, 1), dtype='<i2')
    with pytest.raises(ValueError):
        paired_month(u, u, 1, sample_hours)


@pytest.mark.parametrize('values', [np.zeros((25, 1, 1), dtype=float),
                                  np.zeros((25, 1, 1), dtype=np.int32),
                                  np.zeros((25, 1), dtype=np.int16),
                                  np.ma.array(np.zeros((25, 1, 1), dtype=np.int16), mask=True)])
def test_source_dtype_shape_and_external_masks_cannot_be_silently_coerced(values):
    with pytest.raises(ValueError):
        paired_month(values, values, 1, hours(1, 25))
