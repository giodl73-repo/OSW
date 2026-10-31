"""Tiny complete synthetic year; no original velocity IO or acquisition."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone

import numpy as np
import pytest

from eacc_hycom_source_compilation_v1 import (
    RECEIPT_SCHEMA, compile_source, encoded, pin, validate_receipt, validate_response,
)
from eacc_hycom_source_selection_v1 import MISSING, SCALE, make_selection
from test_eacc_hycom_source_selection_v1 import coordinate_text, synthetic_metadata


def payload(request, plan):
    axes = plan['selected_coordinates']
    times = [plan['source_time_hours_since_2000_01_01'][i] for i in request['time_indices']]
    nt, ny, nx = len(times), len(axes['lat']), len(axes['lon'])
    declarations, bodies = [], []
    for variable, packed in [('water_u', 1000), ('water_v', 2000)]:
        declarations.append(f'Int16 {variable}[time = {nt}][depth = 1][lat = {ny}][lon = {nx}];')
        lines = [f'{variable}.{variable}[{nt}][1][{ny}][{nx}]']
        for ti, hours in enumerate(times):
            stamp = datetime(2000, 1, 1, tzinfo=timezone.utc) + timedelta(hours=hours)
            for yi in range(ny):
                row = [packed] * nx
                if stamp.month == 1 and yi == 0:
                    if stamp.day in (1, 6) and variable == 'water_u':
                        row[0] = MISSING
                    if stamp.day in (1, 6) and variable == 'water_v':
                        row[0] = 30000  # must be excluded with missing paired U
                    if stamp.day in (1, 6, 7) and variable == 'water_v':
                        row[1] = MISSING
                lines.append(f'[{ti}][0][{yi}], ' + ', '.join(map(str, row)))
        for name in ('time', 'depth', 'lat', 'lon'):
            values = times if name == 'time' else axes[name]
            lines.extend([f'{variable}.{name}[{len(values)}]', ', '.join(map(str, values))])
        bodies.append('\n'.join(lines))
    return ('Dataset {\n' + '\n'.join(declarations) + '\n} synthetic;\n' + '\n'.join(bodies) + '\n').encode()


@pytest.fixture(scope='module')
def source():
    metadata, values = synthetic_metadata()
    # Preserve declared full-coordinate sizes but only two cells on each axis
    # inside the editorial viewport: a tiny synthetic payload grid, not HYCOM.
    values['lat'] = np.linspace(-80, -13.1, 1600).tolist() + [-9.1, -8.9] + np.linspace(-4.9, 90, 1649).tolist()
    values['lon'] = np.linspace(0, 37.9, 2000).tolist() + [39.5, 40.5] + np.linspace(44.1, 359.9, 2498).tolist()
    metadata['coordinates.ascii'] = coordinate_text(values).encode()
    plan = make_selection(metadata)
    responses = {}
    selection_sha = pin(encoded(plan))['sha256']
    for i, request in enumerate(plan['requests']):
        raw = payload(request, plan)
        start = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=2 * i)
        receipt = {'schema': RECEIPT_SCHEMA, 'request_file': request['file'],
                   'request_url': request['url'], 'final_url': request['url'],
                   'http_status': 200, 'content_type': 'text/plain; charset=UTF-8',
                   'started_utc': start.isoformat(), 'finished_utc': (start + timedelta(seconds=1)).isoformat(),
                   'response': pin(raw), 'selection_sha256': selection_sha}
        responses[request['file']] = (raw, receipt)
    return metadata, plan, responses


def test_full_synthetic_year_streams_each_bound_response_once_and_keeps_nulls(source):
    metadata, plan, responses = source
    seen = []
    def load(name):
        seen.append(name)
        return responses[name]
    report = compile_source(metadata, plan, responses.keys(), load)
    assert seen == [row['file'] for row in plan['requests']]
    assert len(report['months']) == 12
    assert len(report['original_response_bindings']) == len(responses)
    january = report['months'][0]
    assert january['sample_days'] == 27 and january['minimum_pairs'] == 25
    assert january['paired_samples'] == [[25, 24], [27, 27]]
    assert january['eastward_m_s'][0] == [1000 * SCALE, None]
    assert january['northward_m_s'][0] == [2000 * SCALE, None]
    assert january['eligible_cells'] == 3
    assert report['months'][1]['sample_days'] == 28
    assert report['months'][1]['northward_m_s'] == [[2000 * SCALE] * 2] * 2
    assert report['whole_current_width_km'] is report['whole_current_length_km'] is None
    assert report['current_association_verified'] is report['annual_physical_range_admitted'] is False
    assert report['source_response_binding_verified'] is True
    encoded(report)  # strict JSON; no NaN or platform-dependent NumPy scalars


@pytest.mark.parametrize('mutation', [
    lambda s: s['selection']['depth'].__setitem__(0, 8),
    lambda s: s.__setitem__('response_cap_bytes', 2 ** 30),
    lambda s: s['requests'][0].__setitem__('url', 'https://example.org/'),
    lambda s: s['minimum_pairs'].__setitem__(0, 1),
])
def test_changed_selection_rejected_before_any_payload_load(source, mutation):
    metadata, plan, responses = source
    changed = deepcopy(plan)
    mutation(changed)
    def forbidden(_):
        pytest.fail('Changed selection must fail before loading')
    with pytest.raises(ValueError, match='reproduced'):
        compile_source(metadata, changed, responses.keys(), forbidden)


@pytest.mark.parametrize('mode', ['missing', 'extra', 'duplicate'])
def test_incomplete_extra_or_duplicate_inventory_is_not_a_provider_time_gap(source, mode):
    metadata, plan, responses = source
    names = list(responses)
    if mode == 'missing': names.pop()
    if mode == 'extra': names.append('unplanned.ascii')
    if mode == 'duplicate': names.append(names[0])
    with pytest.raises(ValueError, match='inventory'):
        compile_source(metadata, plan, names, lambda _: pytest.fail('Inventory must fail before load'))


@pytest.mark.parametrize('old,new', [
    (b'Int16 water_u', b'Float32 water_u'),
    (b'[0][0][0],', b'[0][0][1],'),
    (b'1000, 1000', b'1.5, 1000'),
    (b'1000, 1000', b'32768, 1000'),
    (b'water_v.lon[2]', b'water_v.lat[2]'),
    (b'water_u.depth[1]\n15.0', b'water_u.depth[1]\n14.0'),
    (b'water_v.lon[2]\n39.5, 40.5', b'water_v.lon[2]\n39.5, 40.6'),
    (b'water_u.lat[2]\n-9.1, -8.9', b'water_u.lat[2]\n-9.2, -8.9'),
])
def test_response_types_row_identity_masks_and_coordinate_maps_are_not_trusted(source, old, new):
    _, plan, responses = source
    request = plan['requests'][0]
    raw, _ = responses[request['file']]
    assert old in raw
    with pytest.raises(ValueError):
        validate_response(raw.replace(old, new), request, plan)


@pytest.mark.parametrize('key,value', [
    ('schema', 'other'), ('request_file', 'wrong.ascii'), ('http_status', 403),
    ('request_url', 'https://example.org'), ('final_url', 'https://example.org'),
    ('content_type', 'text/html'), ('selection_sha256', '0' * 64),
    ('response', {'bytes': 0, 'sha256': '0' * 64}),
    ('started_utc', '2026-01-01T00:00:00'),
    ('started_utc', '2026-01-01T00:00:00+01:00'),
    ('finished_utc', '2025-01-01T00:00:00+00:00'),
])
def test_wrong_receipt_identity_content_clock_and_hashes_fail(source, key, value):
    _, plan, responses = source
    request = plan['requests'][0]
    raw, receipt = responses[request['file']]
    changed = deepcopy(receipt)
    changed[key] = value
    with pytest.raises(ValueError):
        validate_receipt(raw, changed, request, plan)


def test_payload_byte_corruption_fails_before_compilation(source):
    metadata, plan, responses = source
    first = plan['requests'][0]['file']
    def corrupt(name):
        raw, receipt = responses[name]
        return (raw + b' ', receipt) if name == first else (raw, receipt)
    with pytest.raises(ValueError, match='bytes do not match'):
        compile_source(metadata, plan, responses.keys(), corrupt)


def test_receipts_must_demonstrate_sequential_requests(source):
    metadata, plan, responses = source
    second = plan['requests'][1]['file']
    def overlapping(name):
        raw, receipt = responses[name]
        if name == second:
            receipt = {**receipt, 'started_utc': responses[plan['requests'][0]['file']][1]['started_utc']}
        return raw, receipt
    with pytest.raises(ValueError, match='overlap'):
        compile_source(metadata, plan, responses.keys(), overlapping)


def test_payload_cap_is_checked_before_parsing_or_hashing(source):
    _, plan, responses = source
    request = plan['requests'][0]
    raw, receipt = responses[request['file']]
    tiny_cap = {**plan, 'response_cap_bytes': len(raw) - 1}
    with pytest.raises(ValueError, match='bounded'):
        validate_response(raw, request, tiny_cap)
    with pytest.raises(ValueError, match='bounded'):
        validate_receipt(raw, receipt, request, tiny_cap)


def test_compiled_missing_values_reach_all_diagnostic_cases_without_zero_filling(source):
    from eacc_model_core_diagnostic_v2 import diagnose_year
    from west_australian_regional_streamlines import Field
    metadata, plan, responses = source
    report = compile_source(metadata, plan, responses.keys(), responses.__getitem__)
    fields = {month['month']: Field(report['longitude_degrees_east'], report['latitude_degrees_north'],
                                    month['eastward_m_s'], month['northward_m_s']) for month in report['months']}
    assert np.isnan(fields[1].u[0, 1]) and np.isnan(fields[1].v[0, 1])
    diagnostic = diagnose_year(fields)
    assert diagnostic['case_count'] == 72
    assert sum(case['status'] == 'missing_seed_bilinear_corners' for case in diagnostic['cases']) == 6
    assert sum(case['status'] == 'numerically_tied_northward_peaks' for case in diagnostic['cases']) == 66
    assert not any(month['both_five_station_half_peak_diagnostics_supported'] for month in diagnostic['months'])
    assert diagnostic['source_identity_verified'] is diagnostic['current_association_verified'] is False
    assert diagnostic['annual_physical_minimum_width_km'] is diagnostic['annual_physical_maximum_width_km'] is None
    encoded(diagnostic)
