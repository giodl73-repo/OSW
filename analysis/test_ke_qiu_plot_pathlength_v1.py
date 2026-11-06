"""Prospective synthetic trace/calibration tests; no actual Figure2a readings."""
import copy
import json

import pytest

import ke_qiu_plot_pathlength_v1 as method


GEOMETRY = {'frame': [0, 0, 30, 50],
            'year_major_ticks': [[0, 2000], [10, 2005], [20, 2010]],
            'length_labelled_ticks': [[50, 0], [30, 2000], [10, 4000]]}


def stroke(items=None, **changes):
    result = {'color': [1, 0, 0], 'rect': [1, 10, 20, 40],
              'fill': None, 'closePath': False, 'width': .25,
              'items': items or [('l', [1, 40], [10, 20]), ('l', [10, 20], [20, 10])]}
    result.update(changes)
    return result


@pytest.mark.parametrize('x,y,expected', [(0, 50, (2000, 0)),
                                         (10, 30, (2005, 2000)),
                                         (20, 10, (2010, 4000)),
                                         (5, 40, (2002.5, 1000)),
                                         (25, 20, (2012.5, 3000))])
def test_independent_linear_calibration(x, y, expected):
    assert method.calibrate(x, y, GEOMETRY) == pytest.approx(expected)


def test_piecewise_tick_calibration_does_not_force_uniform_spacing():
    geometry = copy.deepcopy(GEOMETRY)
    geometry['year_major_ticks'][2][0] = 25
    assert method.calibrate(17.5, 30, geometry) == pytest.approx((2007.5, 2000))


@pytest.mark.parametrize('value,expected', [(0, 0), (1004.999, 1000), (1005, 1010), (1015, 1020)])
def test_positive_half_up_ties(value, expected):
    assert method.rounded_length(value) == expected


@pytest.mark.parametrize('value', [-1, float('nan'), float('inf')])
def test_invalid_lengths_reject(value):
    with pytest.raises(ValueError):
        method.rounded_length(value)


def test_all_segments_and_equal_x_vertices_retained():
    drawing = stroke([('l', [1, 40], [10, 20]), ('l', [10, 20], [10, 30]),
                      ('l', [10, 30], [20, 10])])
    runs = method.select_runs([drawing], GEOMETRY['frame'])
    assert len(runs) == 1
    assert runs[0]['points_pt'] == [[1, 40], [10, 20], [10, 30], [20, 10]]


def test_discontinuous_segments_keep_explicit_breaks():
    drawing = stroke([('l', [1, 40], [5, 30]), ('l', [10, 20], [20, 10])])
    runs = method.select_runs([drawing], GEOMETRY['frame'])
    assert [r['drawing_run_index'] for r in runs] == [0, 1]
    assert [len(r['points_pt']) for r in runs] == [2, 2]


def test_other_panels_and_colors_excluded():
    runs = method.select_runs([stroke(color=[0, 0, 1]), stroke(rect=[50, 60, 70, 80]), stroke()], GEOMETRY['frame'])
    assert len(runs) == 1 and runs[0]['drawing_index'] == 2


@pytest.mark.parametrize('drawing', [stroke(fill=[1, 0, 0]), stroke(closePath=True),
                                    stroke(rect=[-5, 10, 20, 40]),
                                    stroke([('c', [1, 40], [10, 20])]),
                                    stroke([('l', [10, 20], [1, 10])]),
                                    stroke([('l', [1, 20], [2, float('nan')])]),
                                    stroke(width=0), stroke(width=.51)])
def test_unsupported_or_invalid_trace_rejects(drawing):
    with pytest.raises(ValueError):
        method.select_runs([drawing], GEOMETRY['frame'])


def test_empty_and_overlapping_runs_reject():
    with pytest.raises(ValueError):
        method.select_runs([], GEOMETRY['frame'])
    with pytest.raises(ValueError):
        method.select_runs([stroke(), stroke()], GEOMETRY['frame'])


def test_invalid_or_inconsistent_axis_calibration_rejects():
    geometry = copy.deepcopy(GEOMETRY)
    geometry['length_labelled_ticks'][1][0] = 31
    with pytest.raises(ValueError):
        method.calibrate(10, 30, geometry)
    geometry = copy.deepcopy(GEOMETRY)
    geometry['year_major_ticks'].reverse()
    with pytest.raises(ValueError):
        method.calibrate(10, 30, geometry)
    with pytest.raises(ValueError):
        method.calibrate(-2, 30, GEOMETRY)


def test_complete_synthetic_report_retains_scope_and_equal_time_vertices(tmp_path, monkeypatch):
    document = {'plot_geometry': GEOMETRY}
    trace = {'schema': 'osw.ke-figure2a-vector-trace.v1', 'original_sha256': method.ORIGINAL_SHA,
             'source_facts_sha256': 'synthetic', 'parser': {'name': 'PyMuPDF', 'version': method.PARSER_VERSION},
             'pdf_page_index': 3,
             'runs': method.select_runs([stroke([('l', [1, 40], [10, 20]), ('l', [10, 20], [10, 30])])], GEOMETRY['frame'])}
    path = tmp_path / method.TRACE
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(trace), encoding='utf8')
    monkeypatch.setattr(method, 'ROOT', tmp_path)
    monkeypatch.setattr(method, 'verify_declaration', lambda: None)
    monkeypatch.setattr(method, 'facts', lambda: document)
    monkeypatch.setattr(method, 'input_pins', lambda: {})
    monkeypatch.setattr(method, 'digest', lambda p: 'synthetic')
    report = method.build()
    assert report['plot_vertex_count'] == 3
    assert report['source_line_segment_count'] == 2
    assert [r['approximate_fractional_year'] for r in report['samples']] == [2000.5, 2005, 2005]
    assert [r['approximate_length_km'] for r in report['samples']] == [1000, 3000, 2000]
    assert report['plotted_vertex_reading_range_km'] == [1000, 3000]
    assert report['whole_current_length_km'] is None
    assert report['physical_width_km'] is None
    assert report['geographic_centerline'] is None
    assert report['annual_extrema_eligible'] is False
    assert report['seasonal_playback_eligible'] is False
    assert report['whole_current_rank_eligible'] is False
    assert all(r['exact_observation_time'] is None and not r['rank_eligible'] and not r['seasonal_playback_eligible']
               and r['length_reading_allowance_km'] == 50 and r['fractional_year_reading_allowance'] == .1
               for r in report['samples'])


def test_failed_write_never_overwrites_an_existing_product(tmp_path, monkeypatch):
    monkeypatch.setattr(method, 'ROOT', tmp_path)
    method.write_new('retained.json', b'first')
    with pytest.raises(FileExistsError):
        method.write_new('retained.json', b'replacement')
    assert (tmp_path / 'retained.json').read_bytes() == b'first'


def test_reviewed_facts_do_not_claim_recovered_daily_cadence_or_calendar_support():
    source = method.facts()
    assert source['plot_geometry']['red_trace_numerically_calibrated'] is False
    assert source['underlying_ssh_context']['is_recovered_plot_sampling_schedule'] is False
    assert source['whole_current_length_admitted'] is False
    assert source['seasonal_or_annual_dimension_range_admitted'] is False
