"""Prospective cloud-only regional core diagnostic; no data admission."""
import argparse
import collections
import hashlib
import html
import io
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile

import audit_osnap_wg_sample_support_v1 as support
import west_greenland_core_width_math_v1 as method

source = support.source
ROOT = Path(__file__).resolve().parents[1]
OPERATOR = 'analysis/build_west_greenland_core_width_v1.py'
TESTS = 'analysis/test_west_greenland_core_width_operator_v1.py'
PROTOCOL = 'plans/west-greenland-monthly-core-width-execution-protocol-v1.md'
MATH = 'analysis/west_greenland_core_width_math_v1.py'
MATH_TESTS = 'analysis/test_west_greenland_core_width_math_v1.py'
MATH_PROTOCOL = 'plans/west-greenland-monthly-core-width-protocol-v1.md'
PREFLIGHT = 'research/west-greenland-core-width-preflight-v1.json'
WORKFLOW = '.github/workflows/west-greenland-core-width-v1.yml'
ROLE_REVIEW = 'signals/roles/check/west-greenland-core-width-v1-roles-check-2026-10-24.md'
PAPER_REVIEWS = ['research/west-greenland-pacini-2020-processing-visual-review-v1.json',
                 'research/west-greenland-pacini-2020-core-identity-visual-review-v1.json']
SUPPORT_REVIEW = 'research/osnap-wg-2016-2018-sample-support-execution-review-v1.json'
SUPPORT_REPORT = 'research/osnap-wg-2016-2018-sample-support-v1.json'
VIEW_REVIEW = 'research/osnap-observation-support-view-delivery-review-v1.json'
INPUT = ROOT / '.pytest_cache/osnap-core-restored-source'
OUTPUT = ROOT / '.pytest_cache/west-greenland-core-width-v1'
STATIONS = [f'LS{i}' for i in range(1, 9)]


def required_inputs():
    inherited = json.loads((ROOT / support.PREFLIGHT).read_bytes())['input_sha256']
    return set(inherited) | {support.PREFLIGHT, OPERATOR, TESTS, PROTOCOL, MATH, MATH_TESTS,
                             MATH_PROTOCOL, WORKFLOW, ROLE_REVIEW, SUPPORT_REVIEW, SUPPORT_REPORT, VIEW_REVIEW,
                             *PAPER_REVIEWS}


def verify_preflight():
    git = ['git', '-c', 'core.fsmonitor=false']
    raw = subprocess.check_output([*git, 'show', 'HEAD:' + PREFLIGHT], cwd=ROOT)
    if raw != (ROOT / PREFLIGHT).read_bytes():
        raise ValueError('Regional-core preflight must be committed before original calculation')
    plan = json.loads(raw)
    if (plan.get('schema') != 'osw.west-greenland-core-width-preflight.v1'
            or plan.get('phase') != 'prospective_declaration'
            or not required_inputs() <= plan.get('input_sha256', {}).keys()):
        raise ValueError('Incomplete transitive regional-core freeze')
    for name, pin in plan['input_sha256'].items():
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT) or source.digest(path) != pin:
            raise ValueError('Frozen regional-core input changed: ' + name)
        if subprocess.check_output([*git, 'show', 'HEAD:' + name], cwd=ROOT) != path.read_bytes():
            raise ValueError('Regional-core input differs from committed bytes: ' + name)
    return hashlib.sha256(raw).hexdigest()


def selected_adcp_headers(headers):
    selected = {}
    for row in headers['instrument_headers']:
        variables = row['header']['variables']
        if 'BINDEPTH' not in variables or 'UCUR' not in variables:
            continue
        station = row['member'].split('/')[0]
        if station not in STATIONS or station in selected:
            raise ValueError('Ambiguous ADCP station inventory')
        selected[station] = row
    if set(selected) != set(STATIONS):
        raise ValueError('Exactly one ADCP is required at each of eight stations')
    return selected


def read_adcp(dataset):
    variables = dataset.variables
    for name, standard in [('UCUR', 'eastward_sea_water_velocity'), ('VCUR', 'northward_sea_water_velocity')]:
        variable = variables[name]
        if (variable.dimensions != ('TIME', 'BINDEPTH') or variable.units != 'meter/second'
                or variable.standard_name != standard):
            raise ValueError('Unreviewed ADCP velocity identity')
    if (variables['DEPTH'].dimensions != ('TIME', 'BINDEPTH') or variables['DEPTH'].units != 'meters'
            or variables['TIME'].dimensions != ('TIME',) or variables['TIME'].units != support.EPOCH_UNITS
            or getattr(variables['TIME'], 'calendar', 'standard') not in ('standard', 'gregorian')):
        raise ValueError('Unreviewed ADCP depth or time coordinates')
    positions = support.coordinates(dataset)
    if not positions['station_position_available']:
        raise ValueError('Station requires singleton finite surveyed coordinates')
    for name in ['LATITUDE', 'LONGITUDE']:
        if positions[name]['attributes'].get('reference') != 'WGS84':
            raise ValueError('Station coordinate reference must be declared WGS84')
    indices, offsets = method.align_hours(support.read_array(variables['TIME']))
    along, cross, reasons = method.layer_velocity(support.read_array(variables['UCUR']),
                                                  support.read_array(variables['VCUR']),
                                                  support.read_array(variables['DEPTH']))
    if len(indices) != len(along):
        raise ValueError('Time and moving-layer profiles do not align')
    return {'hour_indices': indices, 'alignment_offsets_seconds': offsets,
            'along_m_s': along, 'cross_m_s': cross, 'layer_reasons': reasons,
            'coordinates': positions}


def section_coordinates(instruments):
    from pyproj import Geod
    origin = instruments['LS4']['coordinates']
    lon0 = origin['LONGITUDE']['values'][0]
    lat0 = origin['LATITUDE']['values'][0]
    geod = Geod(ellps='WGS84')
    result = []
    for name in STATIONS:
        point = instruments[name]['coordinates']
        lon = point['LONGITUDE']['values'][0]
        lat = point['LATITUDE']['values'][0]
        azimuth, _, metres = geod.inv(lon0, lat0, lon, lat)
        cross = metres / 1000 * math.cos(math.radians(azimuth - (method.BEARING_DEGREES_TRUE - 90)))
        along = metres / 1000 * math.cos(math.radians(azimuth - method.BEARING_DEGREES_TRUE))
        result.append({'station': name, 'longitude': lon, 'latitude': lat,
                       'transverse_km': cross, 'along_reference_offset_km': along,
                       'distance_from_ls4_km': metres / 1000, 'azimuth_from_ls4_degrees_true': azimuth,
                       'coordinate_attributes': {key: point[key]['attributes'] for key in ['LATITUDE', 'LONGITUDE']}})
    if any(b['transverse_km'] <= a['transverse_km'] for a, b in zip(result, result[1:])):
        raise ValueError('Surveyed station order does not increase offshore')
    return result


def build_diagnostic(instruments):
    import numpy as np
    if set(instruments) != set(STATIONS):
        raise ValueError('All eight original ADCP stations are required')
    coordinates = section_coordinates(instruments)
    start = min(int(instruments[name]['hour_indices'][0]) for name in STATIONS)
    stop = max(int(instruments[name]['hour_indices'][-1]) for name in STATIONS) + 1
    if not 0 < stop - start <= 20000:
        raise ValueError('Hourly trace exceeds the declared deployment budget')
    hours = np.arange(start, stop, dtype='int64')
    utc = np.datetime64('1950-01-01T00', 'h') + hours.astype('timedelta64[h]')
    unfiltered = np.full((len(hours), 8), np.nan)
    filtered = unfiltered.copy()
    traces = {'hour_indices_since_1950': hours}
    stations = []
    for column, name in enumerate(STATIONS):
        row = instruments[name]
        slots = np.asarray(row['hour_indices'], dtype='int64') - start
        if len(np.unique(slots)) != len(slots):
            raise ValueError('Duplicate aligned trace hours')
        unfiltered[slots, column] = row['along_m_s']
        filtered[:, column], segments = method.filter_segments(unfiltered[:, column])
        prefix = name.lower() + '_'
        traces[prefix + 'original_hour_indices'] = row['hour_indices']
        traces[prefix + 'signed_alignment_offset_seconds'] = row['alignment_offsets_seconds']
        traces[prefix + 'layer_cross_m_s'] = row['cross_m_s']
        traces[prefix + 'layer_reason_codes'] = np.asarray(row['layer_reasons'], dtype='U40')
        stations.append({'station': name, 'source_member': row.get('member'), 'source_sha256': row.get('sha256'),
                         'time_rows': len(slots), 'layer_profile_counts': dict(collections.Counter(row['layer_reasons'])),
                         'alignment_offset_seconds_min': float(np.min(row['alignment_offsets_seconds'])),
                         'alignment_offset_seconds_max': float(np.max(row['alignment_offsets_seconds'])),
                         'filter_segments': segments, 'filtered_available_hours': int(np.isfinite(filtered[:, column]).sum())})
    traces['unfiltered_layer_along_m_s'] = unfiltered
    traces['filtered_layer_along_m_s'] = filtered
    traces['joint_available_hours'] = np.isfinite(filtered).all(axis=1)
    monthly = method.monthly_profiles(utc, filtered)
    x = [row['transverse_km'] for row in coordinates]
    for row in monthly:
        results = []
        for fraction in method.THRESHOLD_FRACTIONS:
            if row['eligible_for_core_span']:
                value = method.core_span(x, row['conditional_mean_along_m_s'], STATIONS, fraction)
                for key in ['left_bracket', 'right_bracket']:
                    bracket = value.get(key)
                    value[key + '_stations'] = [STATIONS[i] for i in bracket] if bracket is not None else None
            else:
                value = {'fraction_of_peak': fraction, 'status': 'monthly_support_insufficient', 'span_km': None}
            results.append(value)
        row['threshold_results'] = results
    return {'coordinates': coordinates, 'stations': stations, 'months': monthly,
            'hour_grid_rows': len(hours), 'station_order': STATIONS}, traces


def diagnostic_svg(diagnostic):
    """Static support and conditional-span figure, not current geometry."""
    months = diagnostic['months']
    lines = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 1020" role="img">',
             '<title>West Greenland regional core diagnostic and sampling support</title>',
             '<rect width="1100" height="1020" fill="#fff"/>',
             '<g font-family="sans-serif" fill="#173c4c">',
             '<text x="30" y="35" font-size="24">50–100 m regional upper-slope core diagnostic</text>',
             '<text x="30" y="65" font-size="15">Fixed 318.1° true reference; filtered section projection, not whole-current width.</text>',
             '<text x="30" y="90" font-size="14">Bars show joint available hours / calendar hours. Gray labels mark failed support.</text>']
    for index, row in enumerate(months):
        y = 125 + index * 26
        colour = '#176d84' if row['eligible_for_core_span'] else '#777'
        lines.append(f'<text x="30" y="{y}" font-size="13">{html.escape(row["month"])}</text>')
        lines.append(f'<rect x="120" y="{y-13}" width="{row["common_fraction"]*300:.2f}" height="16" fill="{colour}"/>')
        label = f'{row["common_available_hours"]}/{row["calendar_hours"]} h'
        for value in row['threshold_results']:
            number = value.get('span_km')
            short = {'monthly_support_insufficient': 'support fail', 'censored': 'censored',
                     'merged_secondary_core': 'merged core', 'ambiguous_peak': 'peak tie',
                     'peak_outside_upper_slope_anchors': 'off-anchor',
                     'peak_below_diagnostic_floor': 'weak peak',
                     'missing_station_no_interpolation': 'missing station'}
            text = f'{number:.2f} km' if number is not None else short.get(value['status'], 'unresolved')
            label += f' | {value["fraction_of_peak"]:.1f}: {text}'
        lines.append(f'<text x="440" y="{y}" font-size="11">{html.escape(label)}</text>')
    lines.extend(['<text x="30" y="865" font-size="14">All 0.4 / 0.5 / 0.6 thresholds retained; unresolved outcomes are not zero widths.</text>',
                  '<text x="30" y="895" font-size="14">Threshold sensitivity is not measurement error. Conditional monthly means are not an unbiased climatology.</text>',
                  '<text x="30" y="925" font-size="14">Source: Pickart (2020), DOI 10.35090/fz80-6c32; original archive and first custody retained.</text>',
                  '<text x="30" y="955" font-size="14">OSW prospective method v1; source traces and edge brackets accompany every result. No data admission.</text>',
                  '<text x="30" y="985" font-size="14">Digits show calculation precision; physical uncertainty and annual current ranges are not established.</text>',
                  '</g></svg>'])
    return ('\n'.join(lines) + '\n').encode()


def main(argv=None):
    args = argv if argv is not None else __import__('sys').argv[1:]
    source.require_cloud('--cloud-core-width' in args, os.environ)
    parser = argparse.ArgumentParser()
    parser.add_argument('--cloud-core-width', action='store_true', required=True)
    parser.parse_args(args)
    preflight_sha = verify_preflight()
    os.sched_setaffinity(0, {min(os.sched_getaffinity(0))});os.nice(5)
    if source.shutil.disk_usage(ROOT).free < 2 * 1024**3 or source.available_memory_bytes() < 2 * 1024**3:
        raise ValueError('Insufficient cloud disk or memory')
    headers = json.loads((ROOT / support.HEADERS).read_bytes())
    custody = json.loads((ROOT / support.CUSTODY).read_bytes())
    inventory = json.loads((ROOT / source.INVENTORY).read_bytes())
    original = support.verify_restored_source(INPUT, headers, custody, inventory)
    selected = selected_adcp_headers(headers)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    from netCDF4 import Dataset
    instruments = {}
    with zipfile.ZipFile(original) as archive:
        source.checked_members(archive, inventory['instrument_candidates'])
        for name in STATIONS:
            expected = selected[name]
            if expected['bytes'] > 64 * 1024**2:
                raise ValueError('Original ADCP exceeds the memory budget')
            raw = archive.read(expected['member'])
            if (len(raw) != expected['bytes'] or hashlib.sha256(raw).hexdigest() != expected['sha256']
                    or source.header_metadata(raw, OUTPUT) != expected['header']):
                raise ValueError('Original ADCP member or header changed: ' + name)
            with tempfile.NamedTemporaryFile(dir=OUTPUT, prefix='core-', suffix='.nc', delete=False) as stream:
                temporary = Path(stream.name);stream.write(raw)
            del raw
            try:
                with Dataset(str(temporary), 'r') as dataset:row = read_adcp(dataset)
            finally:
                temporary.unlink()
            instruments[name] = {**row, 'member': expected['member'], 'sha256': expected['sha256']}
            print('PASS ORIGINAL ADCP LAYER ' + name, flush=True)
    diagnostic, traces = build_diagnostic(instruments)
    import numpy as np
    buffer = io.BytesIO();np.savez_compressed(buffer, **traces);trace = buffer.getvalue()
    if len(trace) > 64 * 1024**2:
        raise ValueError('Hourly trace exceeds artifact budget')
    source.write_once(OUTPUT / 'hourly-traces.npz', trace)
    figure = diagnostic_svg(diagnostic);source.write_once(OUTPUT / 'diagnostic.svg', figure)
    report = {'schema': 'osw.west-greenland-regional-core-diagnostic.v1',
              'status': 'CALCULATED_UNADMITTED_REGIONAL_CORE_DIAGNOSTIC',
              'execution_commit': subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
              'preflight_sha256': preflight_sha, 'custody': custody, 'source_artifact_id': 12558929959,
              'source_header_report_sha256': source.digest(ROOT / support.HEADERS),
              'trace': {'name': 'hourly-traces.npz', 'bytes': len(trace), 'sha256': hashlib.sha256(trace).hexdigest()},
              'figure': {'name': 'diagnostic.svg', 'bytes': len(figure), 'sha256': hashlib.sha256(figure).hexdigest()},
              'layer_m': list(method.LAYER_M), 'flow_reference_bearing_degrees_true': method.BEARING_DEGREES_TRUE,
              'metric': 'regional_filtered_layer_core_transverse_projection',
              'resolved_threshold_samples': sum(v.get('span_km') is not None for r in diagnostic['months'] for v in r['threshold_results']),
              'full_current_widths_derived': 0, 'annual_physical_ranges_derived': 0,
              'working_dataset_admitted': False, 'new_current_geometry_or_state_joins': 0,
              'scientific_release_published': False, 'fresh_provider_download': False, **diagnostic}
    encoded = source.encoded(report)
    if len(encoded) > 8 * 1024**2:
        raise ValueError('Regional diagnostic report exceeds budget')
    source.write_once(OUTPUT / 'result.json', encoded)
    print(json.dumps({'status': report['status'], 'months': len(diagnostic['months']),
                      'resolved_threshold_samples': report['resolved_threshold_samples']}))


if __name__ == '__main__':
    main()
