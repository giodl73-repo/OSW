"""Inventory retained diagnostic terminal support; no new current edges."""
import argparse
from collections import Counter
from decimal import Decimal
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = 'research/indian-secc-hycom-source-boundary-preflight-v1.json'
REPORT = 'research/indian-secc-hycom-source-boundary-audit.json'
SOURCE = 'research/indian-secc-hycom-2013-local-normal-spans.json'
ARRAYS = 'research/source-data/hycom-indian-secc-2013/monthly.npz'
QUALITY = 'research/source-data/hycom-indian-secc-2013/quality.json'
SELECTION = 'research/source-data/hycom-indian-secc-2013/selection.json'
COLUMNS = ['normal_offset_km', 'longitude_degrees_east',
           'latitude_degrees_north', 'eastward_m_s', 'northward_m_s',
           'projected_tangent_m_s', 'ascending_latitude_cell_index',
           'longitude_cell_index', 'status']


def pin(path):
    raw = (ROOT / path).read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def outside_sides(row, bounds):
    if row is None:
        return []
    lon, lat = row[1:3]
    return [side for side, value in [('west', lon < bounds['west']),
                                    ('east', lon > bounds['east']),
                                    ('south', lat < bounds['south']),
                                    ('north', lat > bounds['north'])] if value]


def threshold_relation(row, threshold):
    if row is None or row[5] is None or threshold is None:
        return 'unavailable'
    value, limit = Decimal(str(row[5])), Decimal(str(threshold))
    return 'above' if value > limit else 'equal' if value == limit else 'below'


def build():
    declared = json.loads((ROOT / PREFLIGHT).read_bytes())
    for path, expected in declared['dependencies'].items():
        if pin(path) != expected:
            raise ValueError('Changed frozen boundary-audit dependency: ' + path)
    source = json.loads((ROOT / SOURCE).read_bytes())
    quality = json.loads((ROOT / QUALITY).read_bytes())
    if quality['monthly_arrays'] != pin(ARRAYS) or quality['selection'] != pin(SELECTION):
        raise ValueError('Changed native array binding')
    if (source['source_quality'] != pin(QUALITY) or source['selection'] != pin(SELECTION)
            or source['sample_columns'] != COLUMNS):
        raise ValueError('Changed diagnostic source or sample columns')
    cases = source['cases']
    if len(cases) != 144 or len({c['id'] for c in cases}) != 144:
        raise ValueError('Incomplete attempt matrix')
    sections = {c['section_id'] for c in cases}
    expected = {(m, section, offset, step) for m in range(1, 13)
                for section in sections for offset in [-1, 0, 1] for step in [5, 10]}
    actual = {(c['month'], c['section_id'], c['native_latitude_offset'], c['normal_sample_step_km']) for c in cases}
    if len(sections) != 2 or actual != expected:
        raise ValueError('Changed seed/offset/step matrix')
    with np.load(ROOT / ARRAYS, allow_pickle=False) as data:
        x, y = data['lon'], data['lat']
        if (not np.isfinite(x).all() or not np.isfinite(y).all()
                or not (np.diff(x) > 0).all() or not (np.diff(y) > 0).all()
                or data['month'].tolist() != list(range(1, 13))
                or data['depth'].tolist() != [15]
                or any(data[k].shape != (12, len(y), len(x)) for k in ['u_m_s', 'v_m_s'])):
            raise ValueError('Changed native coordinate/field support')
        bounds = dict(west=float(x[0]), east=float(x[-1]),
                      south=float(y[0]), north=float(y[-1]))
        grid_shape = [len(y), len(x)]
    rows = []
    for c in cases:
        for station in c['stations']:
            samples = station['samples']
            if any(a[0] >= b[0] for a, b in zip(samples, samples[1:])):
                raise ValueError('Unordered retained profile')
            if [t['fraction'] for t in station['threshold_cases']] != [0.4, 0.5, 0.6]:
                raise ValueError('Changed threshold matrix')
            for direction, terminal, inward in [
                    ('negative_normal', samples[0] if samples else None, samples[1] if len(samples) > 1 else None),
                    ('positive_normal', samples[-1] if samples else None, samples[-2] if len(samples) > 1 else None)]:
                sides = outside_sides(terminal, bounds)
                if terminal is not None and (terminal[8] == 'outside_source') != bool(sides):
                    raise ValueError('Terminal status/domain mismatch')
                thresholds = []
                for t in station['threshold_cases']:
                    edge = t['edges'].get(direction)
                    stored = None if edge is None else edge.get('threshold_projected_m_s')
                    peak = station['peak']['peak_projected_m_s']
                    threshold = (None if peak is None else
                                 str(Decimal(str(peak)) * Decimal(str(t['fraction']))))
                    thresholds.append({
                        'fraction': t['fraction'], 'pair_status': t['status'],
                        'direction_edge': edge,
                        'source_censored_before_crossing': edge is not None and edge['status'] == 'outside_source_before_crossing',
                        'serialized_peak_threshold_m_s': threshold,
                        'stored_crossing_threshold_m_s': stored,
                        'inward_sample_relation_to_serialized_threshold': threshold_relation(inward, threshold)})
                rows.append({'case_id': c['id'], 'month': c['month'],
                             'section_id': c['section_id'],
                             'native_latitude_offset': c['native_latitude_offset'],
                             'normal_sample_step_km': c['normal_sample_step_km'],
                             'all_five_local_axis_checks_pass': c['all_five_local_axis_checks_pass'],
                             'station_arc_parameter_km': station['station_arc_parameter_km'],
                             'station_axis_check_pass': station['local_candidate_axis_check'],
                             'direction': direction, 'terminal_sample': terminal,
                             'immediate_inward_sample': inward, 'outside_sides': sides,
                             'thresholds': thresholds})
    months = []
    for month in range(1, 13):
        group = [r for r in rows if r['month'] == month]
        months.append({'month': month, 'attempts': sum(c['month'] == month for c in cases),
                       'terminal_rows': len(group),
                       'outside_source_terminals': sum(bool(r['outside_sides']) for r in group),
                       'half_peak_source_censored_edges': sum(r['thresholds'][1]['source_censored_before_crossing'] for r in group),
                       'axis_passing_half_peak_source_censored_edges': sum(r['all_five_local_axis_checks_pass'] and r['thresholds'][1]['source_censored_before_crossing'] for r in group)})
    if any(m['attempts'] != 12 for m in months):
        raise ValueError('Incomplete monthly attempt matrix')
    return {'schema': 'osw.indian-secc-source-boundary-audit.v1',
            'current_id': source['current_id'],
            'status': 'retained_serialized_support_audit_not_current_edges',
            'dependencies': declared['dependencies'], 'sample_columns': COLUMNS,
            'native_bounds': bounds, 'native_grid_shape_lat_lon': grid_shape,
            'attempt_inventory': [{'case_id': c['id'], 'month': c['month'],
                                   'status': c['status'], 'available_stations': len(c['stations'])}
                                  for c in cases],
            'monthly_summary': months, 'terminal_rows': rows,
            'terminal_status_counts': dict(sorted(Counter('missing_profile' if r['terminal_sample'] is None else r['terminal_sample'][8] for r in rows).items())),
            'physical_width_admitted': False, 'physical_axis_admitted': False,
            'physical_length_admitted': False, 'annual_width_range_admitted': False,
            'limitation': 'Serialized-value comparisons do not resolve the unsampled terminal interval, prove a missing crossing, or establish named-current association.'}


def encoded():
    return (json.dumps(build(), ensure_ascii=True, indent=2, allow_nan=False) + '\n').encode()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['build', 'check'])
    args = parser.parse_args()
    result = encoded()
    path = ROOT / REPORT
    if args.action == 'check':
        if path.read_bytes() != result:
            raise ValueError('Boundary audit differs from exact offline rebuild')
        print('PASS boundary audit byte exact')
    else:
        if path.exists():
            raise ValueError('Refusing to overwrite a calculated report')
        path.write_bytes(result)
        print('Wrote', REPORT, len(result), 'bytes')
