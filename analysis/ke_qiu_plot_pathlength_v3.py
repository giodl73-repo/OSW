"""Explicit source-stroke correction; prior methods and failures stay frozen."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path

import ke_qiu_plot_pathlength_v1 as v1

ROOT = v1.ROOT
OPERATOR = 'analysis/ke_qiu_plot_pathlength_v3.py'
TESTS = 'analysis/test_ke_qiu_plot_pathlength_v3.py'
PROTOCOL = 'plans/kuroshio-extension-plot-pathlength-protocol-v3.md'
PREFLIGHT = 'research/ke-qiu-plot-pathlength-preflight-v3.json'
TRACE = 'research/source-data/ke-qiu-2023/figure2a-vector-trace-v3.json'
REPORT = 'research/ke-qiu-regional-plot-pathlength-v3.json'
FIGURE = 'figures/ke-qiu-regional-plot-pathlength-v3.svg'
INPUTS = [OPERATOR, TESTS, PROTOCOL, *v1.INPUTS, v1.PREFLIGHT,
          'research/ke-qiu-v1-pdf-operator-diagnostic.json',
          'analysis/ke_qiu_plot_pathlength_v2.py', 'analysis/test_ke_qiu_plot_pathlength_v2.py',
          'plans/kuroshio-extension-plot-pathlength-protocol-v2.md',
          'research/ke-qiu-plot-pathlength-preflight-v2.json',
          'research/ke-qiu-v2-stroke-diagnostic.json']
encoded = v1.encoded


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def pins():
    return {p: digest(p) for p in INPUTS}


def verify():
    p = json.loads((ROOT / PREFLIGHT).read_text(encoding='utf8'))
    if p['input_sha256'] != pins() or p['actual_series_calibrated'] is not False:
        raise ValueError('Changed frozen v3 inputs or declaration')


def derivative_coefficients(values):
    p0, p1, p2, p3 = values
    return 3 * (-p0 + 3*p1 - 3*p2 + p3), 6 * (p0 - 2*p1 + p2), 3 * (p1-p0)


def internal_roots(a, b, c):
    if abs(a) < 1e-12:
        candidates = [] if abs(b) < 1e-12 else [-c/b]
    else:
        discriminant = b*b - 4*a*c
        candidates = [] if discriminant < 0 else [(-b-math.sqrt(discriminant))/(2*a), (-b+math.sqrt(discriminant))/(2*a)]
    return sorted({t for t in candidates if 1e-12 < t < 1-1e-12})


def cubic_point(points, t):
    return [sum(((1-t)**3, 3*(1-t)**2*t, 3*(1-t)*t*t, t**3)[i] * points[i][axis]
                for i in range(4)) for axis in range(2)]


def cubic_mesh(points):
    a, b, c = derivative_coefficients([p[0] for p in points])
    checks = [c, a+b+c]
    if a > 0 and 0 < -b/(2*a) < 1:
        t = -b/(2*a)
        checks.append(a*t*t+b*t+c)
    if min(checks) < -1e-9:
        raise ValueError('Nonmonotone cubic time coordinate')
    second = [math.hypot(*(6*(points[i+2][axis]-2*points[i+1][axis]+points[i][axis])
                           for axis in range(2))) for i in (0, 1)]
    count = 16
    while max(second) / (8*count*count) > .01:
        count *= 2
        if count > 1024:
            raise ValueError('Cubic mesh exceeds declared1024-interval limit')
    stationary = internal_roots(*derivative_coefficients([p[1] for p in points]))
    parameters = sorted(set([i/count for i in range(1, count+1)] + stationary))
    return [(t, cubic_point(points, t), 'original_graph_knot' if t == 1 else
             ('cubic_stationary_graph_reading' if t in stationary else 'cubic_interpolated_graph_reading'))
            for t in parameters]


def select_commands(drawings, frame):
    runs = []
    for drawing_index, drawing in enumerate(drawings):
        color = drawing.get('color')
        if (not color or len(color) != 3 or any(not math.isfinite(v) for v in color)
                or any(abs(v-w) > 1e-6 for v, w in zip(color, (1, 0, 0)))):
            continue
        box = list(drawing['rect'])
        if box[2] < frame[0] or box[0] > frame[2] or box[3] < frame[1] or box[1] > frame[3]:
            continue
        if (drawing.get('fill') is not None or drawing.get('closePath', False)
                or not v1.in_frame(box[:2], frame) or not v1.in_frame(box[2:], frame)):
            raise ValueError('Filled/closed or out-of-frame red path')
        commands = []
        previous = None
        run_index = 0

        def retain():
            if commands:
                runs.append({'drawing_index': drawing_index, 'drawing_run_index': run_index,
                             'stroke_width_pt': drawing.get('width'), 'commands': copy.deepcopy(commands)})

        for item in drawing['items']:
            if item[0] not in ('l', 'c') or len(item) != (3 if item[0] == 'l' else 5):
                raise ValueError('Unsupported PDF command')
            points = [v1.finite_point(list(point)) for point in item[1:]]
            if any(not v1.in_frame(p, frame) for p in points):
                raise ValueError('Out-of-frame control or endpoint')
            if previous is not None and math.dist(previous, points[0]) > v1.JOIN_TOLERANCE:
                retain()
                commands = []
                run_index += 1
            commands.append({'operator': item[0], 'points_pt': points})
            previous = points[-1]
        retain()
    runs.sort(key=lambda run: run['commands'][0]['points_pt'][0][0])
    normalise(runs, frame)
    return runs


def validate_runs(runs, frame):
    if not runs:
        raise ValueError('No red trace runs found')
    previous_x = None
    owners = set()
    for run in runs:
        owner = (run['drawing_index'], run['drawing_run_index'])
        if owner in owners:
            raise ValueError('Duplicate drawing/run owner')
        owners.add(owner)
        width = run['stroke_width_pt']
        if type(width) not in (int, float) or not math.isfinite(width) or not 0 < width <= .75:
            raise ValueError('Finite positive source stroke no wider than0.75pt required')
        points = run['points_pt']
        if len(points) < 2:
            raise ValueError('Run must contain a line segment')
        for point in points:
            point = v1.finite_point(point)
            if not v1.in_frame(point, frame):
                raise ValueError('Out-of-frame trace vertex')
            if previous_x is not None and point[0] < previous_x:
                raise ValueError('Reversed or overlapping trace runs')
            previous_x = point[0]


def normalise(runs, frame):
    result = []
    for run in runs:
        readings = []
        for index, command in enumerate(run['commands']):
            op, points = command['operator'], command['points_pt']
            if op not in ('l', 'c') or len(points) != (2 if op == 'l' else 4):
                raise ValueError('Unsupported retained command')
            points = [v1.finite_point(p) for p in points]
            if any(not v1.in_frame(p, frame) for p in points):
                raise ValueError('Out-of-frame retained control or endpoint')
            if not readings:
                readings.append({'point': points[0], 'source_segment_index': index,
                                 'parameter': 0, 'kind': 'original_graph_knot'})
            elif math.dist(readings[-1]['point'], points[0]) > v1.JOIN_TOLERANCE:
                raise ValueError('Undeclared gap inside retained run')
            extra = [(1, points[-1], 'original_graph_knot')] if op == 'l' else cubic_mesh(points)
            for t, point, kind in extra:
                readings.append({'point': v1.finite_point(point), 'source_segment_index': index,
                                 'parameter': round(t, 12), 'kind': kind})
        result.append({'drawing_index': run['drawing_index'], 'drawing_run_index': run['drawing_run_index'],
                       'stroke_width_pt': run['stroke_width_pt'],
                       'points_pt': [r['point'] for r in readings], 'readings': readings})
    validate_runs(result, frame)
    return result


def original_trace(path):
    verify()
    import pymupdf
    if pymupdf.VersionBind != v1.PARSER_VERSION:
        raise ValueError('Pinned PyMuPDF version required')
    source = v1.facts()
    raw = Path(path).read_bytes()
    if len(raw) != source['original_bytes'] or hashlib.sha256(raw).hexdigest() != v1.ORIGINAL_SHA:
        raise ValueError('Original checksum/byte count mismatch')
    with pymupdf.open(stream=raw, filetype='pdf') as pdf:
        if len(pdf) != source['original_pages']:
            raise ValueError('Original page count mismatch')
        runs = select_commands(pdf[3].get_drawings(), source['plot_geometry']['frame'])
    return {'schema': 'osw.ke-figure2a-vector-trace.v3', 'original_sha256': v1.ORIGINAL_SHA,
            'source_facts_sha256': digest(v1.FACTS), 'parser_version': v1.PARSER_VERSION,
            'pdf_page_index': 3, 'runs': runs}


def build():
    verify()
    source = v1.facts()
    trace = json.loads((ROOT / TRACE).read_text(encoding='utf8'))
    if (trace['schema'] != 'osw.ke-figure2a-vector-trace.v3'
            or trace['original_sha256'] != v1.ORIGINAL_SHA or trace['source_facts_sha256'] != digest(v1.FACTS)
            or trace['parser_version'] != v1.PARSER_VERSION or trace['pdf_page_index'] != 3):
        raise ValueError('Trace source/version custody mismatch')
    runs = normalise(trace['runs'], source['plot_geometry']['frame'])
    rows = []
    for run_index, run in enumerate(runs):
        for index, reading in enumerate(run['readings']):
            x, y = reading['point']
            year, length = v1.calibrate(x, y, source['plot_geometry'])
            rows.append({'id': f'ke-qiu-plot-v3:{run_index}:{index}',
                         'entity_id': 'current:kuroshio-extension', 'run_index': run_index,
                         'reading_index': index, 'source_segment_index': reading['source_segment_index'],
                         'segment_parameter': reading['parameter'], 'reading_kind': reading['kind'],
                         'pdf_point': [x, y], 'approximate_fractional_year': round(year, 6),
                         'fractional_year_reading_allowance': .1, 'unrounded_length_km': round(length, 6),
                         'approximate_length_km': v1.rounded_length(length), 'length_reading_allowance_km': 50,
                         'exact_observation_time': None, 'rank_eligible': False, 'seasonal_playback_eligible': False})
    counts = {op: sum(command['operator'] == op for run in trace['runs'] for command in run['commands'])
              for op in ('l', 'c')}
    input_pins = pins()
    input_pins.update({PREFLIGHT: digest(PREFLIGHT), TRACE: digest(TRACE)})
    return {'schema': 'osw.ke-regional-plot-pathlength.v3',
            'id': 'current_length_series:kuroshio-extension:qiu-2023-figure2a:v3',
            'entity_id': 'current:kuroshio-extension', 'input_sha256': input_pins, 'source': source,
            'quantity': 'author_plotted_regional_pathlength', 'geographic_gates_degrees_east': [141, 153],
            'unit': 'km', 'evidence_kind': 'editorial_vector_graph_reading',
            'time_support': 'Approximate graph-year positions only; no recovered calendar dates or verified observed sample cadence.',
            'allowance_kind': 'Editorial graph-reading allowances, not physical errors or confidence intervals.',
            'whole_current_length_km': None, 'whole_current_rank_eligible': False,
            'physical_width_km': None, 'geographic_centerline': None,
            'annual_extrema_eligible': False, 'seasonal_playback_eligible': False,
            'run_count': len(runs), 'original_line_commands': counts['l'], 'original_cubic_commands': counts['c'],
            'original_graph_knot_count': counts['l'] + counts['c'] + len(runs),
            'graph_reading_count': len(rows), 'recovered_observed_sample_count': None,
            'plotted_graph_reading_range_km': [min(r['approximate_length_km'] for r in rows), max(r['approximate_length_km'] for r in rows)],
            'range_scope': 'Published graphic only, including cubic stationary points; not all source observations or physical annual extrema.',
            'samples': rows}


def figure(report):
    parts = []
    for run in range(report['run_count']):
        points = ' '.join(f"{80+(r['approximate_fractional_year']-1993)*28:.3f},{320-r['unrounded_length_km']*.045:.3f}"
                          for r in report['samples'] if r['run_index'] == run)
        parts.append(f'<polyline points="{points}" fill="none" stroke="#55d5da" stroke-width="1.2"/>')
    ticks = []
    for year in (1995, 2000, 2005, 2010, 2015, 2020):
        ticks.append(f'<text x="{80+(year-1993)*28}" y="346" text-anchor="middle">{year}</text>')
    for value in (0, 2000, 4000):
        y = 320-value*.045
        ticks.append(f'<path d="M80 {y} H920" stroke="#355563"/><text x="68" y="{y+5}" text-anchor="end">{value}</text>')
    low, high = report['plotted_graph_reading_range_km']
    return (f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 540" role="img" aria-labelledby="title desc">
<title id="title">Kuroshio Extension regional plotted pathlength,141E–153E</title>
<desc id="desc">The published graphic's approximate readings span{low:,} to{high:,}km. All original commands and explicit run breaks are retained; extra cubic graph readings are not observations. Reading allowances are plus or minus50km and0.1year. Not whole-current length, physical annual extrema or seasonal playback. A complete numeric table accompanies this chart.</desc>
<rect width="980" height="540" rx="12" fill="#102733"/>
<g font-family="system-ui,sans-serif" fill="#e8f4f5" font-size="16">
<text x="32" y="40" font-size="25">Kuroshio Extension · upstream plotted pathlength</text>
<text x="32" y="70">Regional gates141°E–153°E · Qiu, Chen and Oka (2023), Figure2a</text>
<text x="32" y="102">km</text>
''' + ''.join(ticks)+''.join(parts)+f'''
<text x="500" y="371" text-anchor="middle">Approximate year</text>
<text x="32" y="401">Plotted readings: {low:,}–{high:,}km · {report['original_graph_knot_count']:,} original graph knots</text>
<text x="32" y="431">Cubic readings preserve graphic shape; they are not additional observations.</text>
<text x="32" y="461">Reading allowances: ±50km and ±0.1year; exact observation dates unavailable.</text>
<text x="32" y="491">Regional graphic range; no whole-current rank or physical annual extrema.</text>
<text x="32" y="521">doi:10.1029/2023GL103548 · complete numeric table accompanies this chart.</text>
</g></svg>''').encode('utf8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['declare', 'extract', 'build', 'check', 'original'])
    parser.add_argument('--original-path')
    args = parser.parse_args()
    if args.command == 'declare':
        if any((ROOT / p).exists() for p in (PREFLIGHT, TRACE, REPORT, FIGURE)):
            raise ValueError('Existing v3 products/declaration must be retained')
        v1.facts()
        v1.write_new(PREFLIGHT, encoded({'schema': 'osw.ke-plot-pathlength-preflight.v3',
                                      'input_sha256': pins(), 'actual_series_calibrated': False,
                                      'original_sha256': v1.ORIGINAL_SHA,
                                      'prior_v1_operator_and_v2_stroke_failures_retained': True,
                                      'raw_operator_and_stroke_diagnostics_previously_inspected': True}))
    elif args.command in ('extract', 'original'):
        if not args.original_path:
            parser.error('--original-path required')
        trace = encoded(original_trace(args.original_path))
        if args.command == 'extract':
            v1.write_new(TRACE, trace)
        elif trace != (ROOT / TRACE).read_bytes():
            raise ValueError('Original trace replay differs')
    else:
        report = build()
        if args.command == 'build':
            if any((ROOT / p).exists() for p in (REPORT, FIGURE)):
                raise ValueError('Retain scientific products; use a new version')
            v1.write_new(REPORT, encoded(report))
            v1.write_new(FIGURE, figure(report))
        elif encoded(report) != (ROOT / REPORT).read_bytes() or figure(report) != (ROOT / FIGURE).read_bytes():
            raise ValueError('Scientific replay differs')
    print(args.command+': PASS')


if __name__ == '__main__':
    main()
