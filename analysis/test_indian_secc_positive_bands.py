"""Independent grid flood fill and historical-domain checks protect interpretation."""
import copy
import json
from collections import deque
import pytest
from indian_secc_positive_bands import (ROOT, SOURCE, REPORT, positive_runs, maxima,
                                        column_nodes, connect, verify, encoded,
                                        distance_readback, compare_cases)


def profile(values, column=0):
    return [{'coordinate': i-3, 'latitude': i-3, 'longitude': 50+column/3,
             'component_m_s': v, 'eastward_m_s': v, 'northward_m_s': 0 if v is not None else None,
             'paired_source_samples': 6 if v is not None else 0} for i, v in enumerate(values)]


def nodes(values, column=0):
    return column_nodes(profile(values, column), 50+column/3, column)


def test_zero_missing_and_negative_never_bridge():
    assert positive_runs([1, 0, 1, None, 1, -1, 1, float('nan'), 1]) == [(0,0),(2,2),(4,4),(6,6),(8,8)]
    assert positive_runs([]) == []


def test_plateaus_and_secondary_peaks_are_retained():
    assert maxima([1, 2, 2, 1, 3, 1, 3], 0, 6) == [
        {'first_row':1, 'last_row':2, 'eastward_m_s':2},
        {'first_row':4, 'last_row':4, 'eastward_m_s':3},
        {'first_row':6, 'last_row':6, 'eastward_m_s':3}]
    n = nodes([-1,1,2,1,2,1,-1])[0]
    assert n['equal_global_peak_rows'] == [2,4] and n['peak_latitude'] == -1
    assert len(n['local_maximum_plateaus']) == 2


def test_zero_edges_and_interpolated_edges_are_distinct():
    n = nodes([-1,0,1,2,1,-1,-1])[0]
    assert n['south_zero_edge']['status'] == 'exact_native_zero'
    assert n['south_zero_edge']['latitude'] == -2
    assert n['north_zero_edge']['status'] == 'linear_zero_crossing'
    assert n['north_zero_edge']['latitude'] == 1.5


@pytest.mark.parametrize('values,status', [([1,1,1,-1,-1,-1,-1],'source_boundary_without_crossing'),
                                         ([None,1,1,-1,-1,-1,-1],'missing_before_crossing')])
def test_censored_edges_do_not_close(values, status):
    assert nodes(values)[0]['south_zero_edge']['status'] == status


def test_weak_run_is_retained_with_null_measurement():
    n = nodes([-1,-1,.001,.01,.001,-1,-1])[0]
    assert n['peak_eastward_m_s'] == .01
    assert all(c['status'] == 'weak_or_no_eligible_peak' and c['span_km'] is None for c in n['threshold_cases'])


def test_diagonal_native_cells_are_not_connected():
    all_nodes, components = connect([nodes([1,-1,-1,-1,-1,-1,-1],0),nodes([-1,1,-1,-1,-1,-1,-1],1)])
    assert len(components) == 2 and all(not n['east_neighbors'] and not n['west_neighbors'] for n in all_nodes)


def test_split_merge_retains_both_branches():
    _, components = connect([nodes([-1,1,1,1,-1,-1,-1],0),
                             nodes([-1,1,-1,1,-1,-1,-1],1),
                             nodes([-1,1,1,1,-1,-1,-1],2)])
    assert len(components) == 1
    assert components[0]['nodes'] == 4
    assert components[0]['eastward_splits'] == components[0]['eastward_merges'] == 1


def test_distance_readback_never_changes_original_brackets():
    original = nodes([-1,1,2,3,2,1,-1])[0]['threshold_cases'][1]
    case = copy.deepcopy(original);case['span_km'] = 123.456789123456
    case['grid_bracket_span_km'] = [-0.0,234.567890123456]
    before = copy.deepcopy(case);rounded = distance_readback(case)
    assert case == before
    assert rounded['span_km'] == 123.456789
    assert rounded['grid_bracket_span_km'] == [0.0,234.56789]
    assert rounded['boundaries'] == case['boundaries']


def test_platform_distance_drift_does_not_create_a_domain_extension():
    previous = nodes([-1,1,2,3,2,1,-1])[0]['threshold_cases'][1]
    previous['span_km'] = 273.7451967643802
    current = copy.deepcopy(previous);current['span_km'] += 5.684341886080802e-14
    result = compare_cases(previous,current)
    assert result['historical']['span_km'] == previous['span_km']
    assert result['boundary_coordinates_and_status_exact'] and result['span_readback_matches']
    assert result['comparison_kind'] == 'same_boundaries_and_status'
    assert not result['northern_crossing_recovered'] and result['span_readback_difference_km'] == 0


def test_real_distance_difference_is_retained_without_inventing_boundary_change():
    previous = nodes([-1,1,2,3,2,1,-1])[0]['threshold_cases'][1]
    current = copy.deepcopy(previous);current['span_km'] += .001
    result = compare_cases(previous,current)
    assert result['boundary_coordinates_and_status_exact'] and not result['span_readback_matches']
    assert abs(result['span_readback_difference_km']-.001)<1e-12
    assert not result['northern_crossing_recovered']


def test_changed_boundary_and_status_cannot_hide_behind_distance_readback():
    previous = nodes([-1,1,2,3,2,1,-1])[0]['threshold_cases'][1]
    current = copy.deepcopy(previous)
    current['boundaries']['high_coordinate']['coordinate'] += 1e-12
    result = compare_cases(previous,current)
    assert not result['boundary_coordinates_and_status_exact']
    assert result['comparison_kind'] == 'other_boundary_or_support_difference'
    current = copy.deepcopy(previous);current['boundaries']['high_coordinate']['status'] = 'domain_edge_without_crossing'
    assert not compare_cases(previous,current)['boundary_coordinates_and_status_exact']


@pytest.fixture(scope='module')
def retained():
    d, _ = verify()
    assert encoded(d) == (ROOT/REPORT).read_bytes()
    return d, json.loads((ROOT/SOURCE).read_bytes())


def test_independent_native_cell_flood_fill(retained):
    d, source = retained
    for month, frame in zip(d['months'], source['months']):
        order = sorted(range(len(source['latitude_degrees_north'])),key=lambda y: source['latitude_degrees_north'][y])
        positive = {(x,y) for y, yi in enumerate(order) for x in range(len(source['longitude_degrees_east']))
                    if frame['eastward_m_s'][yi][x] is not None and frame['northward_m_s'][yi][x] is not None
                    and frame['eastward_m_s'][yi][x] > 0}
        unseen = set(positive); expected = set()
        while unseen:
            start = min(unseen); unseen.remove(start); group = {start}; queue = deque([start])
            while queue:
                x,y = queue.popleft()
                for point in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
                    if point in unseen: unseen.remove(point);group.add(point);queue.append(point)
            expected.add(frozenset(group))
        groups = {}
        covered = set()
        for node in month['bands']:
            cells = {(node['column'],y) for y in range(node['first_row'],node['last_row']+1)}
            assert not covered & cells;covered |= cells
            groups.setdefault(node['component_id'],set()).update(cells)
        assert covered == positive
        assert {frozenset(v) for v in groups.values()} == expected


def test_historical_domain_extensions_do_not_rewrite_old_results(retained):
    d, _ = retained; rows = d['historical_section_comparisons']
    assert len(rows) == 72
    gained = [r for r in rows if not r['boundary_coordinates_and_status_exact']]
    assert len(gained) == 9
    for r in gained:
        a,b = r['historical'],r['surrounding_domain']
        assert a['status'] == 'unresolved_full_span' and b['status'] == 'paired_boundaries'
        assert a['boundaries']['low_coordinate'] == b['boundaries']['low_coordinate']
        assert a['boundaries']['high_coordinate']['status'] == 'domain_edge_without_crossing'
        assert b['boundaries']['high_coordinate']['latitude'] > 0
        assert r['northern_crossing_recovered'] and r['comparison_kind'] == 'northern_domain_extension'
    same = [r for r in rows if r['boundary_coordinates_and_status_exact']]
    assert len(same) == 63 and all(r['span_readback_matches'] for r in same)
    assert sum(r['northern_crossing_recovered'] for r in rows) == 9


def test_connected_anchor_flow_is_not_promoted_to_current_geometry(retained):
    d,_ = retained
    assert d['whole_current_width_km'] is d['whole_current_length_km'] is None
    assert all(d[k] is False for k in ['current_association_verified','physical_current_axis_admitted',
                                      'length_rank_eligible','width_rank_eligible','physical_state_join_eligible'])
    assert len(d['monthly_summary']) == 12
    for r, month in zip(d['monthly_summary'], d['months']):
        assert r['eligible_anchor_count'] == 2 and r['eligible_anchors_same_component']
        assert r['anchor_component_equator_or_north_reach'] and r['anchor_component_source_truncation']
        assert r['physical_axis_or_width_admitted'] is False
        for anchor in month['anchors']:
            key = 'anchor_'+anchor['section_id'].removeprefix('indian-secc-')
            case = anchor['anchor_search_threshold_cases'][1]
            assert r[key+'_half_peak_component_span_km'] == case['span_km']
            assert r[key+'_half_peak_status'] == case['status']
            assert r[key+'_northern_edge_degrees_north'] == case['boundaries'].get('high_coordinate', {}).get('coordinate')
