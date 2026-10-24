"""Independent crossing examples and actual source reconstruction."""
import copy
import json
import math
from pathlib import Path
import pytest
import build_asca_component_spans as operator


def primary(values, distances=None, u=None):
    return operator.measure(distances or list(range(0, 1000*len(values), 1000)), values, u or [None]*len(values))


def test_linear_crossing_and_bracket_meaning():
    result = primary([0, -1, -2, -1, 0])
    case = result['cases'][1]
    assert result['peak_index'] == 2
    assert case['span_km'] == 2
    assert case['smaller_distance_edge']['distance_m'] == 1000
    assert case['larger_distance_edge']['distance_m'] == 3000
    assert case['grid_bracket_separation_interval_km'] == [0, 2]
    assert result['peak_alignment_indicator_deg'] is None
    # Unequal interpolation: q=.5 occurs at .5km and 2.25km.
    case = primary([0, -1, -.6, -.2])['cases'][1]
    assert case['span_km'] == pytest.approx(1.75)
    assert case['smaller_distance_edge']['fraction_inside_to_outside'] == .5
    assert case['larger_distance_edge']['fraction_inside_to_outside'] == pytest.approx(.25)


def test_readback_changes_only_computed_alignment_not_measurements():
    report=operator.build()
    source=json.loads((operator.ROOT/operator.RAW).read_bytes())
    assert report['alignment_indicator_readback_decimal_places']==6
    assert report['calculation_readback_protocol']==operator.READBACK
    for observed,stored in zip(source['profiles'],report['profiles']):
        full=operator.measure(source['coordinates']['distance_m'],observed['fields']['v'],observed['fields']['U'])
        for key,value in full.items():
            if key!='peak_alignment_indicator_deg':assert stored[key]==value
        angle=full['peak_alignment_indicator_deg']
        assert stored['peak_alignment_indicator_deg']==(None if angle is None else round(angle,6))
        if angle is not None:assert abs(stored['peak_alignment_indicator_deg']-angle)<=5.000001e-7


def test_missing_barriers_are_not_zero_or_an_edge():
    case = primary([0, None, -2, -1, 0])['cases'][1]
    assert case['status'] == 'unresolved_paired_boundaries'
    assert case['span_km'] is None
    assert case['smaller_distance_edge']['status'] == 'unresolved_missing_barrier'
    assert case['larger_distance_edge']['status'] == 'resolved'
    assert case['larger_distance_edge']['distance_m'] == 3000
    # A separated lobe beyond a null cannot provide a replacement core/edge.
    result = primary([0, -1, 0, None, -2, None, 0])
    assert result['peak_index'] == 4
    assert all(c['span_km'] is None for c in result['cases'])


def test_peak_ties_lobes_and_no_convenient_reselection():
    result = primary([0, -2, 0, -2, 0])
    assert result['peak_index'] == 1
    assert result['cases'][1]['span_km'] == 1
    result = primary([-2, 0, -1, 0])
    assert result['peak_index'] == 0
    assert result['cases'][1]['span_km'] is None
    assert result['cases'][1]['smaller_distance_edge']['status'] == 'unresolved_domain_truncation'


def test_absent_weak_flow_and_threshold_gate():
    assert all(c['status'] == 'unresolved_no_finite_v' for c in primary([None]*4)['cases'])
    assert all(c['status'] == 'unresolved_peak_below_0_3_m_s' for c in primary([0, -.29999, 0])['cases'])
    assert primary([0, -.3, 0])['cases'][1]['span_km'] == 1
    assert all(c['span_km'] is None for c in primary([.1, .2, 0])['cases'])


def test_equal_threshold_plateau_stops_at_first_cell():
    case = primary([0, -1, -1, -2, -1, -1, 0])['cases'][1]
    assert case['smaller_distance_edge']['distance_m'] == 2000
    assert case['larger_distance_edge']['distance_m'] == 4000
    assert case['span_km'] == 2


def test_alignment_is_local_context_not_a_rotation():
    result = primary([0, -1, -2, -1, 0], u=[None, None, 2, None, None])
    assert result['peak_alignment_indicator_deg'] == 45
    assert result['cases'][1]['span_km'] == 2
    assert operator.rounded(2.5) == 3
    assert operator.rounded(2.4999) == 2


@pytest.mark.parametrize('distances,values,u', [([0, 2, 1], [0, -1, 0], [None]*3),
    ([0, 0, 1], [0, -1, 0], [None]*3), ([0, math.inf, 2], [0, -1, 0], [None]*3),
    ([0, 1, 2], [0, math.nan, 0], [None]*3), ([0, 1, 2], [0, -1, 0], [0, math.inf, 0]),
    ([0, 1, 2], [0, -1], [None]*3)])
def test_invalid_source_rejected_without_reordering(distances, values, u):
    with pytest.raises(ValueError):
        operator.measure(distances, values, u)


def test_summary_denominator_does_not_drop_failures():
    rows = [primary([0, -2, 0]), primary([None, -2, None])]
    summary = operator.summarize(rows)[1]
    assert summary['attempted_profiles'] == 2 and summary['resolved_profiles'] == 1
    assert summary['resolved_span_min_km'] == summary['resolved_span_median_km'] == summary['resolved_span_max_km'] == 1
    assert summary['unresolved_side_reason_counts'] == {'unresolved_missing_barrier': 2}


@pytest.fixture(scope='module')
def reconstructed():
    return operator.verify()


def test_actual_source_preserves_every_time_and_case(reconstructed):
    raw = json.loads((operator.ROOT/operator.RAW).read_bytes())
    assert reconstructed['counts'] == {'profiles': 931, 'threshold_cases': 2793, 'calendar_bins': 27}
    for source, row in zip(raw['profiles'], reconstructed['profiles'], strict=True):
        for key in ['observed_at', 'source_epoch_seconds', 'source_time_index', 'year', 'month']:
            assert row[key] == source[key]
        assert row['source_pointer'] == '/profiles/'+str(source['source_time_index'])
        assert [c['fraction'] for c in row['cases']] == [.4, .5, .6]
        resolved = [c['span_km'] for c in row['cases'] if c['span_km'] is not None]
        assert resolved == sorted(resolved, reverse=True)
        for case in row['cases']:
            if case['span_km'] is not None:
                lo, hi = case['grid_bracket_separation_interval_km']
                assert lo <= case['span_km'] <= hi
    assert [x['resolved_profiles'] for x in reconstructed['overall_outcomes']] == [271, 330, 406]
    assert sum(m['outcomes'][1]['resolved_profiles'] for m in reconstructed['monthly_summaries']) == 330
    assert [m['year']*100+m['month'] for m in reconstructed['monthly_summaries']] == sorted({p['year']*100+p['month'] for p in raw['profiles']})
    assert sum(m['complete_calendar_time_support'] for m in reconstructed['monthly_summaries']) == 25


def test_derived_values_are_not_physical_admission(reconstructed):
    assert reconstructed['whole_current_width_km'] is None
    assert reconstructed['annual_width_range_km'] is None
    assert reconstructed['geographic_edges'] is None
    for key in ['width_rank_eligible', 'width_measurement_admitted', 'seasonal_playback_eligible']:
        assert reconstructed[key] is False
    assert reconstructed['source_method']['full_2022_corrigenda_reviewed'] is False
    assert reconstructed['source_method']['source_timestamps_modified'] is False
    assert reconstructed['operator']['axis_rotation_applied'] is False


def test_modified_outcomes_or_admission_are_rejected(reconstructed, monkeypatch):
    monkeypatch.setattr(operator, 'build', lambda: reconstructed)
    for change in ['width_measurement_admitted', 'profiles', 'monthly_summaries']:
        document = copy.deepcopy(reconstructed)
        if change == 'width_measurement_admitted': document[change] = True
        else: document[change].pop()
        with pytest.raises(ValueError): operator.verify(document)


def test_changed_frozen_input_fails_before_processing(monkeypatch):
    monkeypatch.setattr(operator, 'digest', lambda _: '0'*64)
    with pytest.raises(ValueError, match='Changed frozen'):
        operator.build()


def test_figure_and_query_projection_are_pinned(reconstructed):
    from asca_component_spans import verify_inputs, record, ID, FIGURE
    document, figure, inputs = verify_inputs()
    assert document == reconstructed
    assert figure['all_primary_outcomes_rendered'] == 931
    assert figure['prespecified_profile_indices'] == [0, 465, 930]
    assert figure['physical_edges_rendered'] is False
    assert FIGURE in inputs and operator.REPORT in inputs
    assert all(operator.digest(path) == pin for path, pin in inputs.items())
    projection = record(document)
    assert projection['id'] == ID
    assert projection['rank_eligible'] is False
    assert projection['source_file_sha256'] == operator.digest(operator.REPORT)
    assert json.loads(projection['source_json']) == document
    svg = (operator.ROOT/figure['figures']['.svg']['file']).read_text(encoding='utf8')
    assert 'role="img"' in svg and 'asca-description' in svg
    assert '601remain unresolved' in svg
