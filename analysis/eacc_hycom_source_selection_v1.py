"""Prospective EACC source selection and packed monthly means; no network IO.

Source coordinates are metadata. Original velocity acquisition requires a
separate committed source-request/dependency preflight and cloud-only runner.
"""
import calendar
from datetime import datetime, timedelta, timezone
import hashlib
import math
import re
import struct
from urllib.parse import quote

import numpy as np


BASE = 'https://tds.hycom.org/thredds/dodsC/GLBv0.08/expt_53.X/data/2013'
DIMENSIONS = {'time': 2884, 'depth': 40, 'lat': 3251, 'lon': 4500}
MISSING = -30000
SCALE = struct.unpack('<f', struct.pack('<f', .001))[0]
MAX_DAYS_PER_REQUEST = 6
RESPONSE_CAP_BYTES = 8 * 1024 * 1024


def validate_metadata(dds, das):
    prefix = dds.split('Grid {', 1)[0]
    if not dds.startswith('Dataset {') or not das.startswith('Attributes {'):
        raise ValueError('Expected DDS/DAS metadata')
    for name, size in DIMENSIONS.items():
        if prefix.count(f'Float64 {name}[{name} = {size}];') != 1:
            raise ValueError('Unexpected native dimension: ' + name)
    for name, direction in [('water_u', 'eastward'), ('water_v', 'northward')]:
        declaration = f'Int16 {name}[time = 2884][depth = 40][lat = 3251][lon = 4500];'
        if dds.count(declaration) != 1:
            raise ValueError('Unexpected packed array declaration: ' + name)
        blocks = re.findall(r'\b' + name + r' \{(.*?)\n    \}', das, re.S)
        required = [f'String standard_name "{direction}_sea_water_velocity";',
                    'String units "m/s";', 'Int16 _FillValue -30000;',
                    'Int16 missing_value -30000;', 'Float32 scale_factor 0.001;',
                    'Float32 add_offset 0.0;']
        if len(blocks) != 1 or any(blocks[0].count(token) != 1 for token in required):
            raise ValueError('Unverified velocity frame/packing: ' + name)
    required_coordinates = {
        'depth': ['String units "m";', 'String positive "down";'],
        'lat': ['String units "degrees_north";'],
        'lon': ['String units "degrees_east";'],
        'time': ['String units "hours since 2000-01-01 00:00:00";', 'String calendar "gregorian";'],
    }
    for name, tokens in required_coordinates.items():
        blocks = re.findall(r'\b' + name + r' \{(.*?)\n    \}', das, re.S)
        if len(blocks) != 1 or any(blocks[0].count(token) != 1 for token in tokens):
            raise ValueError('Unverified coordinate convention: ' + name)
    if 'String distribution_statement "Approved for public release. Distribution unlimited.";' not in das:
        raise ValueError('Unverified provider distribution statement')


def parse_coordinates(text):
    headers = list(re.finditer(r'(?m)^(time|depth|lat|lon)\[(\d+)\][\r ]*$', text))
    if not text.startswith('Dataset {') or len(headers) != 4 or {h[1] for h in headers} != set(DIMENSIONS):
        raise ValueError('Incomplete coordinate-only response')
    declaration = text[:headers[0].start()]
    result = {}
    for i, header in enumerate(headers):
        name, size = header[1], int(header[2])
        if declaration.count(f'Float64 {name}[{name} = {size}];') != 1:
            raise ValueError('Coordinate declaration mismatch: ' + name)
        body = text[header.end():headers[i + 1].start() if i + 1 < len(headers) else len(text)].strip()
        try:
            values = [float(token.strip()) for token in body.split(',')]
        except ValueError as error:
            raise ValueError('Malformed coordinate values: ' + name) from error
        if len(values) != size or not values or not all(math.isfinite(value) for value in values):
            raise ValueError('Invalid coordinate support: ' + name)
        if any(b <= a for a, b in zip(values, values[1:])):
            raise ValueError('Coordinates must strictly increase: ' + name)
        result[name] = values
    return result


def _runs(indices):
    """Exact arithmetic-index runs, at most six daily samples per request."""
    runs = []
    start = 0
    while start < len(indices):
        end = start + 1
        if end < len(indices):
            stride = indices[end] - indices[start]
            while end + 1 < len(indices) and end + 1 - start < MAX_DAYS_PER_REQUEST and indices[end + 1] - indices[end] == stride:
                end += 1
        else:
            end = start
        runs.append(indices[start:end + 1])
        start = end + 1
    return runs


def make_selection(metadata):
    if set(metadata) != {'metadata.dds', 'metadata.das', 'coordinates.ascii'} or any(type(raw) is not bytes for raw in metadata.values()):
        raise ValueError('Require exact metadata byte inventory')
    validate_metadata(metadata['metadata.dds'].decode('utf8'), metadata['metadata.das'].decode('utf8'))
    coordinates = parse_coordinates(metadata['coordinates.ascii'].decode('utf8'))
    if any(len(coordinates[name]) != size for name, size in DIMENSIONS.items()):
        raise ValueError('Native metadata/coordinate sizes differ')
    depth = [i for i, value in enumerate(coordinates['depth']) if value == 15]
    if len(depth) != 1:
        raise ValueError('Missing unique exact 15m depth')
    selected = {'depth': depth}
    for name, low, high in [('lat', -13, -5), ('lon', 38, 44)]:
        values = coordinates[name]
        if values[0] > low or values[-1] < high:
            raise ValueError('Source does not cover investigation window: ' + name)
        indices = [i for i, value in enumerate(values) if low - 1e-5 <= value <= high + 1e-5]
        if len(indices) < 2 or indices != list(range(indices[0], indices[-1] + 1)):
            raise ValueError('Invalid regional native selection')
        selected[name] = indices
    origin = datetime(2000, 1, 1, tzinfo=timezone.utc)
    actual = {}
    for i, hours in enumerate(coordinates['time']):
        if not hours.is_integer():
            raise ValueError('Nonintegral source clock hours')
        stamp = origin + timedelta(hours=hours)
        if stamp.year != 2013:
            raise ValueError('Source time outside Gregorian 2013')
        actual[stamp] = i
    daily = [datetime(2013, 1, 1, tzinfo=timezone.utc) + timedelta(days=i) for i in range(365)]
    requests = []
    for month in range(1, 13):
        indices = [actual[stamp] for stamp in daily if stamp.month == month and stamp in actual]
        for number, run in enumerate(_runs(indices)):
            stride = run[1] - run[0] if len(run) > 1 else 1
            section = f'[{run[0]}:{stride}:{run[-1]}][{depth[0]}]'
            section += ''.join(f'[{selected[name][0]}:1:{selected[name][-1]}]' for name in ('lat', 'lon'))
            expression = ','.join(variable + section for variable in ('water_u', 'water_v'))
            requests.append({'file': f'm{month:02d}-r{number:02d}.ascii', 'month': month,
                             'time_indices': run, 'url': BASE + '.ascii?' + quote(expression, safe='')})
    return {'schema': 'osw.eacc-hycom.source-selection.v1', 'dataset_url': BASE,
            'source_model_year': 2013, 'provider_depth_m': 15,
            'metadata': {name: {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()} for name, raw in sorted(metadata.items())},
            'selection': selected, 'requests': requests,
            'selected_coordinates': {name: [coordinates[name][i] for i in indices] for name, indices in selected.items()},
            'source_time_hours_since_2000_01_01': coordinates['time'],
            'missing_daily_00z': [stamp.isoformat() for stamp in daily if stamp not in actual],
            'calendar_days': [calendar.monthrange(2013, month)[1] for month in range(1, 13)],
            'minimum_pairs': [(4 * calendar.monthrange(2013, month)[1] + 4) // 5 for month in range(1, 13)],
            'packing_scale_float64_hex': SCALE.hex(), 'response_cap_bytes': RESPONSE_CAP_BYTES,
            'max_concurrent_requests': 1, 'maximum_daily_samples_per_request': MAX_DAYS_PER_REQUEST,
            'source_request_preflight_frozen': False, 'velocity_acquisition_allowed': False,
            'current_association_verified': False, 'width_measurement_admitted': False,
            'annual_physical_range_admitted': False}


def paired_month(u, v, month, source_hours):
    """Paired packed-int sums before exact binary32 scaling; no gap filling."""
    if type(month) is not int or month not in range(1, 13):
        raise ValueError('Invalid Gregorian month')
    if np.ma.isMaskedArray(u) or np.ma.isMaskedArray(v):
        raise ValueError('Use retained packed fill values, not an external mask')
    u, v = np.asarray(u), np.asarray(v)
    if u.shape != v.shape or u.ndim != 3 or u.shape[1] < 1 or u.shape[2] < 1:
        raise ValueError('Expected paired time/latitude/longitude cubes')
    if any(array.dtype.kind != 'i' or array.dtype.itemsize != 2 for array in (u, v)):
        raise ValueError('Packed source must be Int16')
    if len(source_hours) != u.shape[0] or any(not math.isfinite(float(hours)) or not float(hours).is_integer() for hours in source_hours):
        raise ValueError('Invalid source sample clock')
    stamps = [datetime(2000, 1, 1, tzinfo=timezone.utc) + timedelta(hours=float(hours)) for hours in source_hours]
    if any(stamp.year != 2013 or stamp.month != month or stamp.hour != 0 for stamp in stamps):
        raise ValueError('Samples must be daily 00Z in the declared month')
    if any(b <= a for a, b in zip(stamps, stamps[1:])):
        raise ValueError('Duplicate or reordered sample dates')
    days = calendar.monthrange(2013, month)[1]
    minimum = (4 * days + 4) // 5
    valid = (u != MISSING) & (v != MISSING)
    counts = valid.sum(axis=0).astype('<i2')
    means = []
    for array in (u, v):
        result = np.full(counts.shape, np.nan, dtype='<f8')
        total = np.where(valid, array, 0).sum(axis=0, dtype=np.int64)
        np.divide(total * SCALE, counts, out=result, where=counts >= minimum)
        means.append(result)
    return {'month': month, 'calendar_days': days, 'minimum_pairs': minimum,
            'sample_days': len(stamps), 'pair_count': counts,
            'eastward_m_s': means[0], 'northward_m_s': means[1]}
