"""Validate original hourly Norkyst DAP arrays, without current-width inference."""
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'research/source-data/norkyst-ingoy-months-2024'
PREFLIGHT_SHA256 = '64e2513c69d554e30d2cda61ccb4c26f47711163d12dcefbe98c720c3b2ee42d'
VARIABLES = ('salinity', 'u_eastward', 'v_northward')
Y = tuple(range(576, 765, 4))
X = tuple(range(2420, 2617, 4))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def preflight():
    path = ROOT / SOURCE / 'preflight.json'
    if sha(path.read_bytes()) != PREFLIGHT_SHA256:
        raise ValueError('Changed frozen temporal-support preflight')
    doc = json.loads(path.read_bytes())
    for source, pin in doc['input_sha256'].items():
        if sha((ROOT / source).read_bytes()) != pin:
            raise ValueError('Changed declared Norkyst input: ' + source)
    if doc['target_year_hours'] != 8784 or doc['halo_hours_each_side'] != 36 or doc['fully_blinded']:
        raise ValueError('Changed temporal-support declaration')
    return doc


def month_window(month):
    if type(month) is not int or not 1 <= month <= 12:
        raise ValueError('Month must be an integer from 1 to 12')
    start = datetime(2024, month, 1, tzinfo=timezone.utc)
    end = datetime(2025, 1, 1, tzinfo=timezone.utc) if month == 12 else datetime(2024, month + 1, 1, tzinfo=timezone.utc)
    return start, end, start - timedelta(hours=36), end + timedelta(hours=36)


def daily_requests(months):
    """Merge requested hours by archive day; keep the exact month halo support."""
    hours = {}
    for month in months:
        _, _, start, end = month_window(month)
        while start < end:
            hours.setdefault(start.date().isoformat(), set()).add(start.hour)
            start += timedelta(hours=1)
    result = []
    for day, values in sorted(hours.items()):
        first, last = min(values), max(values)
        if values != set(range(first, last + 1)):
            raise ValueError('Discontinuous requested day')
        result.append((day, first, last))
    return result


def block(text, name):
    matches = re.findall(r'(?m)^    ' + re.escape(name) + r' \{(.*?)^    \}', text, re.S)
    if len(matches) != 1:
        raise ValueError('Missing or duplicate metadata block: ' + name)
    return matches[0]


def attribute(text, name):
    matches = re.findall(r'(?m)^\s+\w+ ' + re.escape(name) + r' (.*?);\s*$', text)
    if len(matches) != 1:
        raise ValueError('Missing or duplicate metadata attribute: ' + name)
    value = matches[0]
    return json.loads(value) if value.startswith('"') else float(value)


def metadata(raw, day):
    text = raw.decode('utf8')
    for name, expected in [('project', 'Norkyst_v3'), ('time_coverage_start', day + 'T00:00:00'),
                           ('time_coverage_end', day + 'T23:00:00')]:
        if attribute(text, name) != expected:
            raise ValueError('Unexpected source ' + name)
    if 'CC-BY-4.0' not in attribute(text, 'license'):
        raise ValueError('Unexpected source license')
    projection = block(text, 'projection_stere')
    for name, expected in [('grid_mapping_name','polar_stereographic'), ('straight_vertical_longitude_from_pole',70),
                           ('latitude_of_projection_origin',90), ('standard_parallel',60),
                           ('false_easting',3369600), ('false_northing',1844800),
                           ('semi_major_axis',6378137), ('semi_minor_axis',6356752.3142)]:
        if attribute(projection, name) != expected:
            raise ValueError('Changed source projection: ' + name)
    time = block(text, 'time')
    if attribute(time, 'units') != 'seconds since 1970-01-01 00:00:00' or attribute(time, 'calendar') != 'gregorian':
        raise ValueError('Changed time convention')
    depth = block(text, 'depth')
    if attribute(depth, 'units') != 'meter' or attribute(depth, 'positive') != 'down':
        raise ValueError('Changed depth convention')
    packing = {}
    for name in VARIABLES:
        source = block(text, name)
        expected_name = {'salinity':'sea_water_salinity', 'u_eastward':'eastward_sea_water_velocity', 'v_northward':'northward_sea_water_velocity'}[name]
        expected = {'scale_factor':0.001, 'add_offset':30 if name == 'salinity' else 0,
                    '_FillValue':-32767, 'units':'1' if name == 'salinity' else 'meter second-1',
                    'standard_name':expected_name, 'grid_mapping':'projection_stere'}
        if any(attribute(source, key) != value for key, value in expected.items()):
            raise ValueError('Changed daily field packing/identity: ' + name)
        packing[name] = expected
    mask = block(text, 'sea_mask')
    if attribute(mask,'flag_values') != '0, 1' or attribute(mask,'standard_name') != 'sea_binary_mask':
        raise ValueError('Changed sea-mask semantics')
    return packing


def ascii_sections(raw):
    parts = raw.decode('utf8').split('---------------------------------------------')
    if len(parts) != 2:
        raise ValueError('Invalid DAP ASCII envelope')
    return parts[1]


def grid_array(body, name, expected_shape, packed=True):
    matches = list(re.finditer(r'(?m)^' + re.escape(name + '.' + name) + r'((?:\[\d+\])+)[\r\n]+', body))
    if len(matches) != 1:
        raise ValueError('Missing or duplicate source array: ' + name)
    match = matches[0]
    shape = tuple(int(n) for n in re.findall(r'\[(\d+)\]', match[1]))
    if shape != tuple(expected_shape):
        raise ValueError('Wrong source shape: ' + name)
    rows = []
    count = int(np.prod(shape[:-1]))
    for line in body[match.end():].splitlines():
        if not line.strip():
            break
        prefix, values = line.split(',', 1)
        index = tuple(int(n) for n in re.findall(r'\[(\d+)\]', prefix))
        if len(rows) >= count or index != np.unravel_index(len(rows), shape[:-1]):
            raise ValueError('Nonsequential source rows: ' + name)
        row = [float(x) for x in values.split(',')]
        if len(row) != shape[-1] or not np.isfinite(row).all():
            raise ValueError('Invalid source row: ' + name)
        rows.append(row)
    if len(rows) != count:
        raise ValueError('Incomplete source array: ' + name)
    result = np.asarray(rows, dtype=np.float64).reshape(shape)
    if packed and (np.any(result != np.trunc(result)) or np.any(result < -32768) or np.any(result > 32767)):
        raise ValueError('Invalid packed integer array: ' + name)
    return result.astype(np.int16) if packed else result


def axis(body, name, key, expected):
    match = re.findall(r'(?m)^' + re.escape(name + '.' + key) + r'\[(\d+)\][\r\n]+([^\r\n]+)', body)
    if len(match) != 1:
        raise ValueError('Missing source axis: ' + name + '.' + key)
    length, values = match[0]
    values = [float(v) for v in values.split(',')]
    if int(length) != len(expected) or values != list(expected):
        raise ValueError('Wrong source axis: ' + name + '.' + key)


def parse_fields(raw, day, first, last):
    body = ascii_sections(raw)
    nt = last - first + 1
    midnight = datetime.fromisoformat(day).replace(tzinfo=timezone.utc).timestamp()
    times = [int(midnight + hour * 3600) for hour in range(first, last + 1)]
    values = {}
    for name in VARIABLES:
        values[name] = grid_array(body, name, (nt, 1, len(Y), len(X)))[:, 0]
        axis(body,name,'time',times); axis(body,name,'depth',[10])
        axis(body,name,'Y',[y * 800 for y in Y]); axis(body,name,'X',[x * 800 for x in X])
    values['sea_mask'] = grid_array(body, 'sea_mask', (len(Y), len(X)))
    axis(body,'sea_mask','Y',[y * 800 for y in Y]); axis(body,'sea_mask','X',[x * 800 for x in X])
    if not np.isin(values['sea_mask'], [0,1,-127,129]).all():
        raise ValueError('Unexpected sea-mask code')
    return times, values
