"""Frozen prospective Figure2a vector reading, never a geographic centerline."""
import argparse
import copy
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPERATOR = 'analysis/ke_qiu_plot_pathlength_v1.py'
TESTS = 'analysis/test_ke_qiu_plot_pathlength_v1.py'
PROTOCOL = 'plans/kuroshio-extension-plot-pathlength-protocol-v1.md'
FACTS = 'research/kuroshio-extension-qiu-2023-pathlength-source.json'
PREFLIGHT = 'research/ke-qiu-plot-pathlength-preflight-v1.json'
TRACE = 'research/source-data/ke-qiu-2023/figure2a-vector-trace-v1.json'
REPORT = 'research/ke-qiu-regional-plot-pathlength-v1.json'
FIGURE = 'figures/ke-qiu-regional-plot-pathlength-v1.svg'
INPUTS = [OPERATOR, TESTS, PROTOCOL, FACTS]
PARSER_VERSION = '1.28.2'
ORIGINAL_SHA = '39a9f92f539ff164a6782915518bda2617b65c4fa0ba99e41bb41051bb9caa8d'
FRAME_TOLERANCE = .02
JOIN_TOLERANCE = .0001


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode('utf8')


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def facts():
    result = json.loads((ROOT / FACTS).read_text(encoding='utf8'))
    if (result['original_sha256'] != ORIGINAL_SHA
            or result['original_bytes'] != 5373944 or result['original_pages'] != 9
            or result['doi'] != '10.1029/2023GL103548'
            or result['current_id'] != 'kuroshio-extension'
            or result['regional_longitude_gates_degrees_east'] != [141, 153]
            or result['selected_pdf_pages_visually_reviewed'] != [1, 3, 4]):
        raise ValueError('Changed reviewed original or regional support')
    return result


def input_pins():
    return {p: digest(p) for p in INPUTS}


def verify_declaration():
    declaration = json.loads((ROOT / PREFLIGHT).read_text(encoding='utf8'))
    if declaration['input_sha256'] != input_pins() or declaration['actual_series_extracted'] is not False:
        raise ValueError('Frozen input/declaration mismatch; retain failure and use a new version')
    return declaration


def finite_point(point):
    if (not isinstance(point, (list, tuple)) or len(point) != 2
            or any(type(v) not in (int, float) or not math.isfinite(v) for v in point)):
        raise ValueError('Finite two-coordinate PDF point required')
    return [round(float(v), 6) for v in point]


def in_frame(point, frame):
    x, y = point
    left, top, right, bottom = frame
    return (left - FRAME_TOLERANCE <= x <= right + FRAME_TOLERANCE
            and top - FRAME_TOLERANCE <= y <= bottom + FRAME_TOLERANCE)


def select_runs(drawings, frame):
    runs = []
    for ordinal, drawing in enumerate(drawings):
        color = drawing.get('color')
        if (not color or len(color) != 3 or any(not math.isfinite(v) for v in color)
                or any(abs(v - wanted) > 1e-6 for v, wanted in zip(color, (1, 0, 0)))):
            continue
        box = list(drawing['rect'])
        if (box[2] < frame[0] or box[0] > frame[2] or box[3] < frame[1] or box[1] > frame[3]):
            continue
        if (drawing.get('fill') is not None or drawing.get('closePath', False)
                or not in_frame(box[:2], frame) or not in_frame(box[2:], frame)):
            raise ValueError('Red path crosses frame or is filled/closed')
        points = []
        run_number = 0

        def retain():
            if points:
                runs.append({'drawing_index': ordinal, 'drawing_run_index': run_number,
                             'stroke_width_pt': drawing.get('width'), 'points_pt': copy.deepcopy(points)})

        for item in drawing['items']:
            if item[0] != 'l':
                raise ValueError('Unsupported PDF trace operator')
            a, b = finite_point(list(item[1])), finite_point(list(item[2]))
            if not in_frame(a, frame) or not in_frame(b, frame):
                raise ValueError('Out-of-frame trace vertex')
            if points and math.dist(points[-1], a) > JOIN_TOLERANCE:
                retain()
                points = []
                run_number += 1
            if not points:
                points.append(a)
            points.append(b)
        retain()
    runs.sort(key=lambda r: r['points_pt'][0][0])
    validate_runs(runs, frame)
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
        if type(width) not in (int, float) or not math.isfinite(width) or not 0 < width <= .5:
            raise ValueError('Finite positive source stroke no wider than0.5pt required')
        points = run['points_pt']
        if len(points) < 2:
            raise ValueError('Run must contain a line segment')
        for point in points:
            point = finite_point(point)
            if not in_frame(point, frame):
                raise ValueError('Out-of-frame trace vertex')
            if previous_x is not None and point[0] < previous_x:
                raise ValueError('Reversed or overlapping trace runs')
            previous_x = point[0]


def calibrate(x, y, geometry):
    if not in_frame(finite_point([x, y]), geometry['frame']):
        raise ValueError('Point outside reviewed frame')
    ticks = geometry['year_major_ticks']
    if (len(ticks) < 2 or any(b[0] <= a[0] or b[1] <= a[1] for a, b in zip(ticks, ticks[1:]))):
        raise ValueError('Ordered year calibration ticks required')
    first, last = ticks[:2] if x < ticks[0][0] else ticks[-2:]
    for a, b in zip(ticks, ticks[1:]):
        if a[0] <= x <= b[0]:
            first, last = a, b
            break
    year = first[1] + (x - first[0]) * (last[1] - first[1]) / (last[0] - first[0])
    lengths = geometry['length_labelled_ticks']
    (y0, v0), (ym, vm), (y1, v1) = lengths
    if y0 <= ym or ym <= y1 or v0 != 0 or vm != 2000 or v1 != 4000:
        raise ValueError('Reviewed zero/2000/4000km tick order required')
    slope = (v1 - v0) / (y1 - y0)
    if abs((ym - y0) * slope + v0 - vm) > 1:
        raise ValueError('Intermediate length calibration exceeds1km')
    return year, (y - y0) * slope + v0


def rounded_length(value):
    if not math.isfinite(value) or value < 0:
        raise ValueError('Finite nonnegative length required')
    return int((Decimal(str(value)) / 10).quantize(Decimal('1'), rounding=ROUND_HALF_UP) * 10)


def original_trace(path):
    verify_declaration()
    import pymupdf
    if pymupdf.VersionBind != PARSER_VERSION:
        raise ValueError('Original extraction requires pinned PyMuPDF version')
    document = facts()
    raw = Path(path).read_bytes()
    if len(raw) != document['original_bytes'] or hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA:
        raise ValueError('Original byte custody mismatch')
    with pymupdf.open(stream=raw, filetype='pdf') as pdf:
        if len(pdf) != document['original_pages']:
            raise ValueError('Original page count mismatch')
        page = pdf[document['plot_geometry']['pdf_page_index']]
        runs = select_runs(page.get_drawings(), document['plot_geometry']['frame'])
    return {'schema': 'osw.ke-figure2a-vector-trace.v1',
            'original_sha256': ORIGINAL_SHA, 'source_facts_sha256': digest(FACTS),
            'parser': {'name': 'PyMuPDF', 'version': PARSER_VERSION},
            'pdf_page_index': 3, 'coordinates': 'PDF points, top-left origin; six decimals',
            'runs': runs}


def build():
    verify_declaration()
    source = facts()
    trace = json.loads((ROOT / TRACE).read_text(encoding='utf8'))
    if (trace['schema'] != 'osw.ke-figure2a-vector-trace.v1'
            or trace['original_sha256'] != ORIGINAL_SHA or trace['source_facts_sha256'] != digest(FACTS)
            or trace['parser'] != {'name': 'PyMuPDF', 'version': PARSER_VERSION}
            or trace['pdf_page_index'] != 3):
        raise ValueError('Changed trace custody')
    validate_runs(trace['runs'], source['plot_geometry']['frame'])
    rows = []
    for run_index, run in enumerate(trace['runs']):
        for vertex_index, (x, y) in enumerate(run['points_pt']):
            year, length = calibrate(x, y, source['plot_geometry'])
            rows.append({'id': f'ke-qiu-plot-v1:{run_index}:{vertex_index}',
                         'current_id': 'kuroshio-extension', 'run_index': run_index,
                         'plot_vertex_index': vertex_index, 'pdf_point': [x, y],
                         'approximate_fractional_year': round(year, 6),
                         'fractional_year_reading_allowance': .1,
                         'unrounded_length_km': round(length, 6),
                         'approximate_length_km': rounded_length(length),
                         'length_reading_allowance_km': 50,
                         'exact_observation_time': None, 'rank_eligible': False,
                         'seasonal_playback_eligible': False})
    pins = input_pins()
    pins.update({PREFLIGHT: digest(PREFLIGHT), TRACE: digest(TRACE)})
    return {'schema': 'osw.ke-regional-plot-pathlength.v1',
            'id': 'current_length_series:kuroshio-extension:qiu-2023-figure2a',
            'entity_id': 'current:kuroshio-extension', 'input_sha256': pins,
            'source': source, 'quantity': 'author_plotted_regional_pathlength',
            'geographic_gates_degrees_east': [141, 153], 'unit': 'km',
            'evidence_kind': 'editorial_vector_plot_reading',
            'time_support': 'Approximate fractional years read from a plotted axis; no recovered exact calendar dates or verified sample cadence.',
            'allowance_kind': 'Editorial graph-reading allowances, not physical errors or confidence intervals.',
            'whole_current_length_km': None, 'whole_current_rank_eligible': False,
            'physical_width_km': None, 'geographic_centerline': None,
            'annual_extrema_eligible': False, 'seasonal_playback_eligible': False,
            'run_count': len(trace['runs']), 'plot_vertex_count': len(rows),
            'source_line_segment_count': sum(len(r['points_pt']) - 1 for r in trace['runs']),
            'plotted_vertex_reading_range_km': [min(r['approximate_length_km'] for r in rows),
                                              max(r['approximate_length_km'] for r in rows)],
            'range_scope': 'Retained plotted vertices only, not all underlying observations or physical annual extrema.',
            'samples': rows}


def figure(report):
    paths = []
    for run in range(report['run_count']):
        rows = [r for r in report['samples'] if r['run_index'] == run]
        points = ' '.join(f"{80 + (r['approximate_fractional_year'] - 1993) * 28:.3f},{320 - r['unrounded_length_km'] * .045:.3f}" for r in rows)
        paths.append(f'<polyline points="{points}" fill="none" stroke="#55d5da" stroke-width="1.2"/>')
    ticks = []
    for year in (1995, 2000, 2005, 2010, 2015, 2020):
        x = 80 + (year - 1993) * 28
        ticks.append(f'<text x="{x}" y="346" text-anchor="middle">{year}</text>')
    for value in (0, 2000, 4000):
        y = 320 - value * .045
        ticks.append(f'<path d="M80 {y} H920" stroke="#355563"/><text x="68" y="{y + 5}" text-anchor="end">{value}</text>')
    return ('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 510" role="img" aria-labelledby="title desc">
<title id="title">Kuroshio Extension regional plotted pathlength,141E to153E</title>
<desc id="desc">Complete retained vector-plot readings with explicit breaks. Approximate year positions plus or minus0.1 year and lengths plus or minus50km are editorial reading allowances. Not whole-current length, physical annual extrema, seasonal playback or a geographic path. Complete numerical samples accompany this chart.</desc>
<rect width="980" height="510" rx="12" fill="#102733"/>
<g font-family="system-ui,sans-serif" fill="#e8f4f5" font-size="16">
<text x="32" y="40" font-size="25">Kuroshio Extension · upstream plotted pathlength</text>
<text x="32" y="70">Regional gates141°E–153°E · Figure2a · Qiu, Chen and Oka (2023)</text>
<text x="32" y="102">km</text>
''' + ''.join(ticks) + ''.join(paths) + f'''
<text x="500" y="371" text-anchor="middle">Approximate year</text>
<text x="32" y="396">{report['plot_vertex_count']:,} plotted vertices · {report['run_count']} explicit runs · no smoothing</text>
<text x="32" y="416">Reading allowances: ±50km and ±0.1 year; precise observation dates unavailable.</text>
<text x="32" y="446">Regional plot readings; no whole-current rank, annual extrema or seasonal envelope.</text>
<text x="32" y="476">doi:10.1029/2023GL103548 · complete sample table accompanies the chart.</text>
</g></svg>''').encode('utf8')


def write_new(path, data):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as stream:
        stream.write(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['declare', 'extract', 'build', 'check', 'original'])
    parser.add_argument('--original-path')
    args = parser.parse_args()
    if args.command == 'declare':
        if any((ROOT / p).exists() for p in (PREFLIGHT, TRACE, REPORT, FIGURE)):
            raise ValueError('Retain existing declaration/products; use a new version')
        facts()
        write_new(PREFLIGHT, encoded({'schema': 'osw.ke-plot-pathlength-preflight.v1',
                                    'input_sha256': input_pins(), 'actual_series_extracted': False,
                                    'original_sha256': ORIGINAL_SHA, 'parser_version': PARSER_VERSION,
                                    'source_layout_and_black_axis_ticks_previously_inspected': True}))
    elif args.command in ('extract', 'original'):
        if not args.original_path:
            parser.error('--original-path is required')
        trace = encoded(original_trace(args.original_path))
        if args.command == 'extract':
            write_new(TRACE, trace)
        elif trace != (ROOT / TRACE).read_bytes():
            raise ValueError('Original trace replay differs')
    else:
        report = build()
        if args.command == 'build':
            if any((ROOT / p).exists() for p in (REPORT, FIGURE)):
                raise ValueError('Retain existing products; use a new version')
            write_new(REPORT, encoded(report))
            write_new(FIGURE, figure(report))
        elif encoded(report) != (ROOT / REPORT).read_bytes() or figure(report) != (ROOT / FIGURE).read_bytes():
            raise ValueError('Scientific product replay differs')
    print(args.command + ': PASS')


if __name__ == '__main__':
    main()
