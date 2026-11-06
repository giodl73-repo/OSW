"""Independent actual-source readback, added after the frozen v4 extraction."""
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
REPORT = 'research/ke-qiu-regional-plot-pathlength-v4.json'
TRACE = 'research/source-data/ke-qiu-2023/figure2a-vector-trace-v4.json'
FIGURE = 'figures/ke-qiu-regional-plot-pathlength-v4.svg'


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf8'))


def dec(value):
    return Decimal(str(value))


def test_all_frozen_inputs_and_selected_original_custody():
    report = load(REPORT)
    for path, wanted in report['input_sha256'].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == wanted, path
    source = report['source']
    assert source['original_sha256'] == '39a9f92f539ff164a6782915518bda2617b65c4fa0ba99e41bb41051bb9caa8d'
    assert source['original_bytes'] == 5373944 and source['original_pages'] == 9
    assert source['selected_pdf_pages_visually_reviewed'] == [1, 3, 4]
    assert source['original_redistributed'] is False


def test_all_original_commands_and_knot_instances_accounted_for():
    trace, report = load(TRACE), load(REPORT)
    runs = trace['runs']
    assert len(runs) == report['run_count'] == 16
    counts = {op: sum(c['operator'] == op for r in runs for c in r['commands']) for op in ('l', 'c')}
    # Counts come from the pre-calibration raw PDF operator diagnostic.
    assert counts == {'l': 1532, 'c': 4}
    assert report['original_line_commands'] == counts['l']
    assert report['original_cubic_commands'] == counts['c']
    assert report['original_graph_knot_count'] == sum(len(r['commands']) + 1 for r in runs) == 1552
    rows = report['samples']
    assert len(rows) == report['graph_reading_count'] == 1612
    assert len({r['id'] for r in rows}) == len(rows)
    assert sum(r['reading_kind'] == 'original_graph_knot' for r in rows) == 1552
    assert sum(r['reading_kind'] == 'cubic_interpolated_graph_reading' for r in rows) == 60
    for i, run in enumerate(runs):
        actual = [r['pdf_point'] for r in rows if r['run_index'] == i and r['reading_kind'] == 'original_graph_knot']
        expected = [run['commands'][0]['points_pt'][0], *[c['points_pt'][-1] for c in run['commands']]]
        assert actual == expected
        assert abs(run['stroke_width_pt'] - .6) < 1e-6


def test_independent_decimal_length_year_and_rounding_for_every_reading():
    report = load(REPORT)
    geometry = report['source']['plot_geometry']
    year_ticks = [[dec(v) for v in p] for p in geometry['year_major_ticks']]
    (y0, zero), (_, _), (y4, four) = [[dec(v) for v in p] for p in geometry['length_labelled_ticks']]
    assert zero == 0 and four == 4000
    expected_values = []
    for row in report['samples']:
        x, y = [dec(v) for v in row['pdf_point']]
        # Direct dimensional ratio using independent Decimal arithmetic.
        length = (y0-y) * Decimal(4000) / (y0-y4)
        assert abs(length-dec(row['unrounded_length_km'])) <= Decimal('.000001')
        rounded = int((length/10).quantize(Decimal('1'), rounding=ROUND_HALF_UP)*10)
        assert row['approximate_length_km'] == rounded
        expected_values.append(rounded)
        intervals = list(zip(year_ticks, year_ticks[1:]))
        pair = next(((a, b) for a, b in intervals if a[0] <= x <= b[0]),
                    intervals[0] if x < year_ticks[0][0] else intervals[-1])
        a, b = pair
        year = a[1] + (x-a[0])*(b[1]-a[1])/(b[0]-a[0])
        assert abs(year-dec(row['approximate_fractional_year'])) <= Decimal('.000001')
    assert report['plotted_graph_reading_range_km'] == [min(expected_values), max(expected_values)] == [1120, 4660]


def test_derived_cubic_readings_match_retained_source_commands_independently():
    trace, report = load(TRACE), load(REPORT)
    for row in report['samples']:
        command = trace['runs'][row['run_index']]['commands'][row['source_segment_index']]
        if row['reading_kind'] == 'original_graph_knot':
            continue
        assert command['operator'] == 'c'
        t = dec(row['segment_parameter'])
        assert 0 < t < 1
        weights = [(1-t)**3, 3*(1-t)**2*t, 3*(1-t)*t*t, t**3]
        expected = [sum(weights[i]*dec(command['points_pt'][i][axis]) for i in range(4)) for axis in (0, 1)]
        assert all(abs(v-dec(row['pdf_point'][axis])) <= Decimal('.000001') for axis, v in enumerate(expected))


def test_source_breaks_and_small_overlaps_are_explicit_and_unrepaired():
    trace, report = load(TRACE), load(REPORT)
    rows = report['samples']
    expected = []
    for i, run in enumerate(trace['runs']):
        selected = [r for r in rows if r['run_index'] == i]
        assert selected[0]['pdf_point'] == run['commands'][0]['points_pt'][0]
        assert selected[-1]['pdf_point'] == run['commands'][-1]['points_pt'][-1]
        assert all(b['pdf_point'][0] >= a['pdf_point'][0] for a, b in zip(selected, selected[1:]))
        if i:
            previous = trace['runs'][i-1]['commands'][-1]['points_pt'][-1][0]
            first = run['commands'][0]['points_pt'][0][0]
            if previous > first:
                expected.append({'previous_run_index': i-1, 'next_run_index': i, 'overlap_pt': round(previous-first, 6)})
    assert report['run_boundary_overlaps'] == expected and len(expected) == 2
    assert all(0 < p['overlap_pt'] <= .02 for p in expected)
    assert report['graph_knot_count_includes_shared_run_endpoint_instances'] is True


def test_numeric_series_does_not_create_unobserved_dimensions_or_times():
    report = load(REPORT)
    assert report['entity_id'] == 'current:kuroshio-extension'
    assert report['geographic_gates_degrees_east'] == [141, 153]
    assert report['quantity'] == 'author_plotted_regional_pathlength'
    assert report['recovered_observed_sample_count'] is None
    assert report['whole_current_length_km'] is None
    assert report['physical_width_km'] is None and report['geographic_centerline'] is None
    assert report['whole_current_rank_eligible'] is False
    assert report['annual_extrema_eligible'] is False and report['seasonal_playback_eligible'] is False
    assert all(r['exact_observation_time'] is None and not r['rank_eligible'] and not r['seasonal_playback_eligible']
               and r['length_reading_allowance_km'] == 50 and r['fractional_year_reading_allowance'] == .1
               for r in report['samples'])


def test_chart_retains_all_graph_readings_runs_and_textual_scope():
    report = load(REPORT)
    root = ET.fromstring((ROOT / FIGURE).read_bytes())
    polylines = root.findall('.//{http://www.w3.org/2000/svg}polyline')
    assert len(polylines) == report['run_count']
    assert sum(len(p.attrib['points'].split()) for p in polylines) == report['graph_reading_count']
    words = ''.join(root.itertext())
    assert '1,120' in words and '4,660' in words
    assert '±50km' in words and '±0.1year' in words
    assert 'Approximate year' in words and 'not additional observations' in words
    assert root.attrib['aria-labelledby'] == 'title desc'
