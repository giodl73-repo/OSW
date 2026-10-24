"""Prospective cubic tests, with analytic curves and no actual series values."""
import copy
import json
import math

import pytest

import ke_qiu_plot_pathlength_v1 as v1
import ke_qiu_plot_pathlength_v2 as v2

GEOMETRY = {'frame': [0, 0, 30, 50], 'year_major_ticks': [[0, 2000], [10, 2005], [20, 2010]],
            'length_labelled_ticks': [[50, 0], [30, 2000], [10, 4000]]}


def drawing(items=None, **updates):
    result = {'color': [1, 0, 0], 'rect': [1, 0, 20, 40], 'fill': None, 'closePath': False,
              'width': .25, 'items': items or [('l', [1, 40], [10, 20]), ('l', [10, 20], [20, 10])]}
    result.update(updates)
    return result


def test_analytic_cubic_midpoint_and_stationary_minimum():
    points = [[1, 10], [2, 0], [3, 0], [4, 10]]
    assert v2.cubic_point(points, .5) == pytest.approx([2.5, 2.5])
    assert v2.cubic_point(points, .25) == pytest.approx([1.75, 4.375])
    values = v2.cubic_mesh(points)
    stationary = [value for value in values if value[2] == 'cubic_stationary_graph_reading']
    assert len(stationary) == 1
    assert stationary[0][0] == pytest.approx(.5)
    assert stationary[0][1] == pytest.approx([2.5, 2.5])
    assert min(point[1] for _, point, _ in values) == pytest.approx(2.5)
    assert values[-1] == (1, [4, 10], 'original_graph_knot')


def test_two_analytic_internal_extrema_and_degenerate_derivatives():
    assert v2.internal_roots(18, -18, 3) == pytest.approx([.5-math.sqrt(3)/6, .5+math.sqrt(3)/6])
    assert v2.internal_roots(0, 2, -1) == [.5]
    assert v2.internal_roots(0, 0, 0) == []
    assert v2.internal_roots(1, 0, 1) == []
    assert v2.internal_roots(0, 1, 0) == []


def test_nonmonotone_cubic_x_rejects():
    with pytest.raises(ValueError, match='Nonmonotone'):
        v2.cubic_mesh([[0, 0], [2, 1], [-1, 1], [1, 0]])


def test_adaptive_mesh_obeys_independent_midpoint_error_check():
    # y(t)=3000*t*(1-t)*(1-2*t); x(t)=3*t. No source data.
    points = [[0, 0], [1, 1000], [2, -1000], [3, 0]]
    readings = [(0, [0, 0], 'start'), *v2.cubic_mesh(points)]
    assert len(readings) > 100
    for (ta, pa, _), (tb, pb, _) in zip(readings, readings[1:]):
        t = (ta+tb)/2
        exact_y = 3000*t*(1-t)*(1-2*t)
        assert abs(exact_y-(pa[1]+pb[1])/2) <= .01


def test_mesh_resource_limit_rejects_unbounded_complexity():
    with pytest.raises(ValueError, match='1024'):
        v2.cubic_mesh([[0, 0], [1, 1e10], [2, -1e10], [3, 0]])


def test_line_only_readings_agree_with_frozen_v1():
    raw = [drawing()]
    old = v1.select_runs(raw, GEOMETRY['frame'])
    new = v2.normalise(v2.select_commands(raw, GEOMETRY['frame']), GEOMETRY['frame'])
    assert new[0]['points_pt'] == old[0]['points_pt']
    assert all(row['kind'] == 'original_graph_knot' for row in new[0]['readings'])


def test_raw_cubic_controls_are_retained_but_not_labelled_observations():
    points = [[1, 10], [2, 0], [3, 0], [4, 10]]
    runs = v2.select_commands([drawing([('c', *points)])], GEOMETRY['frame'])
    assert runs[0]['commands'][0]['points_pt'] == points
    normal = v2.normalise(runs, GEOMETRY['frame'])[0]
    assert normal['points_pt'][0] == [1, 10]
    assert normal['points_pt'][-1] == [4, 10]
    assert [2, 0] not in normal['points_pt'] and [3, 0] not in normal['points_pt']
    assert sum(r['kind'] == 'original_graph_knot' for r in normal['readings']) == 2
    # max|B''|=60:16 intervals exceed0.01pt,32 satisfy it, plus initial knot.
    assert len(normal['readings']) == 33


def test_equal_x_curve_readings_remain_distinct():
    runs = v2.select_commands([drawing([('c', [1, 10], [1, 0], [1, 0], [1, 10])])], GEOMETRY['frame'])
    normal = v2.normalise(runs, GEOMETRY['frame'])[0]
    assert len(normal['readings']) == 33
    assert set(p[0] for p in normal['points_pt']) == {1}


def test_source_run_breaks_and_other_panels_remain_separate():
    raw = [drawing(color=[0, 0, 1]), drawing(rect=[50, 60, 70, 80]),
           drawing([('l', [1, 40], [5, 30]), ('l', [10, 20], [20, 10])])]
    runs = v2.select_commands(raw, GEOMETRY['frame'])
    assert [(r['drawing_index'], r['drawing_run_index']) for r in runs] == [(2, 0), (2, 1)]
    assert [len(r['commands']) for r in runs] == [1, 1]


@pytest.mark.parametrize('raw', [drawing(fill=[1, 0, 0]), drawing(closePath=True),
                               drawing(width=.51), drawing([('re', [1, 10], [2, 20])]),
                               drawing([('c', [1, 10], [-2, 0], [3, 0], [4, 10])]),
                               drawing([('c', [1, 10], [2, float('nan')], [3, 0], [4, 10])]),
                               drawing([('l', [20, 10], [1, 40])])])
def test_invalid_source_commands_reject(raw):
    with pytest.raises(ValueError):
        v2.select_commands([raw], GEOMETRY['frame'])


def test_undeclared_gaps_and_overlapping_runs_reject():
    runs = v2.select_commands([drawing()], GEOMETRY['frame'])
    broken = copy.deepcopy(runs)
    broken[0]['commands'][1]['points_pt'][0][0] = 11
    with pytest.raises(ValueError, match='Undeclared gap'):
        v2.normalise(broken, GEOMETRY['frame'])
    with pytest.raises(ValueError):
        v2.select_commands([drawing(), drawing()], GEOMETRY['frame'])


def test_synthetic_report_counts_and_scope(tmp_path, monkeypatch):
    source = {'plot_geometry': GEOMETRY}
    runs = v2.select_commands([drawing([('c', [1, 10], [2, 0], [3, 0], [4, 10])])], GEOMETRY['frame'])
    trace = {'schema': 'osw.ke-figure2a-vector-trace.v2', 'original_sha256': v1.ORIGINAL_SHA,
             'source_facts_sha256': 'synthetic', 'parser_version': v1.PARSER_VERSION,
             'pdf_page_index': 3, 'runs': runs}
    path = tmp_path / v2.TRACE
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(trace), encoding='utf8')
    monkeypatch.setattr(v2, 'ROOT', tmp_path)
    monkeypatch.setattr(v2, 'verify', lambda: None)
    monkeypatch.setattr(v2, 'pins', lambda: {})
    monkeypatch.setattr(v2, 'digest', lambda p: 'synthetic')
    monkeypatch.setattr(v1, 'facts', lambda: source)
    report = v2.build()
    assert report['original_line_commands'] == 0
    assert report['original_cubic_commands'] == 1
    assert report['original_graph_knot_count'] == 2
    assert report['graph_reading_count'] == 33
    assert report['plotted_graph_reading_range_km'] == [4000, 4750]
    assert report['recovered_observed_sample_count'] is None
    assert report['whole_current_length_km'] is None
    assert report['geographic_centerline'] is None
    assert report['physical_width_km'] is None
    assert not report['whole_current_rank_eligible'] and not report['annual_extrema_eligible']
    assert not report['seasonal_playback_eligible']
    assert all(r['exact_observation_time'] is None and not r['rank_eligible'] and not r['seasonal_playback_eligible']
               for r in report['samples'])
    assert len({r['id'] for r in report['samples']}) == 33
    assert all(r['length_reading_allowance_km'] == 50 and r['fractional_year_reading_allowance'] == .1
               for r in report['samples'])
