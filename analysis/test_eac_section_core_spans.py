"""Independent known-vector/section cases for the declared exploratory operator."""
import math
import json
import copy
import pytest
import build_eac_section_core_spans as core


def primary(values, distance=None, barriers=None):
    return core.measure(distance or [i*1000 for i in range(len(values))], values,
                        barriers or [None]*len(values))['cases'][1]


def test_wgs84_equator_geometry_has_declared_eastward_orientation():
    geo = core.geometry([0., 1., 2.], [0., 0., 0.])
    expected = 6378137*math.pi/180
    assert geo['distance_m'] == pytest.approx([0, expected, 2*expected], abs=1e-6)
    assert geo['forward_bearing_deg'] == pytest.approx([90]*3)
    with pytest.raises(ValueError): core.geometry([0, 0], [0, 0])
    with pytest.raises(ValueError): core.geometry([0, 1], [0, 91])


def test_known_vector_projection_right_normal_and_algebraic_allowance():
    q, a, along, barriers = core.project([3., 3., 3.], [4., 4., 4.], [.2]*3, [.4]*3,
                                        [0., 90., 45.], [200.]*3)
    assert q == pytest.approx([3, -4, -1/math.sqrt(2)])
    assert along == pytest.approx([4, 3, 7/math.sqrt(2)])
    assert a == pytest.approx([.2, .4, .6/math.sqrt(2)])
    assert barriers == [None]*3


def test_bottom_and_missing_pairs_stay_different_barriers():
    q, a, along, barriers = core.project([0., None, 1.], [0., 1., 1.], [0.]*3, [0.]*3,
                                        [90.]*3, [100., 200., 200.])
    assert barriers == ['source_bottom_at_or_above_level', 'missing_paired_velocity', None]
    assert q[:2] == a[:2] == along[:2] == [None, None]
    with pytest.raises(ValueError): core.project([1.], [1.], [-1.], [0.], [0.], [200.])


def test_triangular_core_known_crossings_and_sampling_cell_support():
    case = primary([0., 1., 2., 1., 0.])
    assert case['section_span_km'] == 2
    assert case['shoreward_edge']['distance_m'] == 1000
    assert case['offshore_edge']['distance_m'] == 3000
    assert case['sampling_support_interval_km'] == [0, 2]
    # Support uses the original adjacent cells, even when equality lands on an endpoint.
    assert case['shoreward_edge']['indices_in_distance_order'] == [1, 2]
    assert case['offshore_edge']['indices_in_distance_order'] == [2, 3]


def test_irregular_spacing_uses_metric_distance_not_cell_count():
    case = primary([0., 2., 0.], [0., 1000., 5000.])
    assert case['section_span_km'] == 2.5
    assert case['shoreward_edge']['distance_m'] == 500
    assert case['offshore_edge']['distance_m'] == 3000
    assert case['rounded_section_span_km'] == 3


def test_disconnected_lobe_cannot_replace_global_peak():
    result = core.measure(list(range(7)), [0, 2, None, 0, 1, 0, 0], [None, None, 'missing_paired_velocity', None, None, None, None])
    assert result['peak_index'] == 1
    case = result['cases'][1]
    assert case['section_span_km'] is None
    assert case['shoreward_edge']['status'] == 'resolved'
    assert case['offshore_edge']['status'] == 'unresolved_missing_paired_velocity'


def test_real_missing_and_bottom_barriers_do_not_become_zero_edges():
    for reason in ['missing_paired_velocity', 'source_bottom_at_or_above_level']:
        case = primary([None, 2, 0], barriers=[reason, None, None])
        assert case['section_span_km'] is None
        assert case['shoreward_edge']['status'] == 'unresolved_'+reason
        assert case['offshore_edge']['status'] == 'resolved'
    case = primary([2, 1, 0])
    assert case['shoreward_edge']['status'] == 'unresolved_section_domain'


def test_exact_ties_choose_first_index_and_threshold_plateaus_stop_immediately():
    result = core.measure(list(range(7)), [0, 1, 2, 2, 1, 1, 0], [None]*7)
    assert result['peak_index'] == 2
    case = result['cases'][1]
    assert case['shoreward_edge']['distance_m'] == 1
    assert case['offshore_edge']['distance_m'] == 4


def test_weak_reversed_and_absent_profiles_never_gain_width():
    for values, status in [([None]*3, 'unresolved_no_eligible_component'),
                           ([-1, -2, -1], 'unresolved_peak_below_0_3_m_s'),
                           ([0, .299, 0], 'unresolved_peak_below_0_3_m_s')]:
        result = core.measure([0, 1, 2], values, [None]*3)
        assert all(c['status'] == status and c['section_span_km'] is None for c in result['cases'])
    assert primary([0, .3, 0])['section_span_km'] is not None


def test_supplied_magnitude_scenarios_can_change_peak_and_success():
    central = [0, 1, .8, 0]; a = [0, .5, .05, 0]
    result = [core.measure([0, 1, 2, 3], [v+sign*e for v, e in zip(central, a)], [None]*4)
              for _, sign in core.SCENARIOS]
    assert [r['peak_index'] for r in result] == [1, 2, 1]
    # Missing supplied uncertainty cannot borrow the central field's valid crossing.
    q, a, _, barriers = core.project([0., 0., 0.], [0., -1., 0.], [0., None, 0.],
                                     [0.]*3, [90.]*3, [200.]*3)
    assert primary(q)['section_span_km'] is not None
    assert a[1] is None and barriers[1] is None


@pytest.mark.parametrize('distance,values,barriers', [
    ([0, 0, 1], [0, 1, 0], [None]*3),
    ([0, 1, math.inf], [0, 1, 0], [None]*3),
    ([0, 1, 2], [0, math.nan, 0], [None]*3),
    ([0, 1, 2], [0, 1, 0], [None, 'bottom', None]),
])
def test_invalid_support_cannot_enter_diagnostic(distance, values, barriers):
    with pytest.raises(ValueError): core.measure(distance, values, barriers)


@pytest.fixture(scope='module')
def actual():
    return core.build()


def test_all_original_dates_masks_and_scenario_denominators(actual):
    assert actual['counts'] == {'source_dates': 3770, 'scenarios_per_date': 9, 'attempts': 33930, 'months': 124}
    rows = actual['profiles']
    assert [r['source_time_index'] for r in rows] == list(range(3770))
    assert all(v is None for r in rows[513:1142] for v in r['section_normal_velocity_m_s'])
    assert sum(any(v is not None for v in r['section_normal_velocity_m_s']) for r in rows) == 3141
    assert all(all(v is None for v in r['section_normal_velocity_m_s'][:13]) for r in rows)
    assert all(sum(o['status_counts'].values()) == 3770 and o['attempted_dates'] == 3770 for o in actual['overall_outcomes'])
    assert sum(len(m['source_time_indices']) for m in actual['monthly_summaries']) == 3770


def test_scope_flags_and_all_boundary_cells_obey_protocol(actual):
    assert actual['physical_width_admitted'] is False
    assert actual['annual_width_range_km'] is None and actual['geographic_current_edges'] is None
    assert actual['source_timestamps_independent_observations'] is False
    assert actual['supplied_magnitudes_are_statistical_confidence'] is False
    for row in actual['profiles']:
        for scenario in row['scenarios'].values():
            for case in scenario['cases']:
                for side in [case['shoreward_edge'], case['offshore_edge']]:
                    if side and side['status'] == 'resolved':
                        assert all(i >= 13 for i in side['indices_in_distance_order'])
                        assert min(side['distance_bracket_m']) <= side['distance_m'] <= max(side['distance_bracket_m'])


def test_summaries_include_failures_and_do_not_relabel_conditional_spread(actual):
    for summary in actual['overall_outcomes']:
        assert summary['conditioned_on_successful_bracketing_not_annual_extrema'] is True
        assert sum(summary['status_counts'].values()) == summary['attempted_dates']
        assert summary['resolved_dates']+summary['status_counts'].get('unresolved_no_eligible_component', 0) <= 3770


def test_retained_report_reconstructs_and_admission_change_rejects(actual):
    assert core.verify() == actual
    altered = copy.deepcopy(actual); altered['physical_width_admitted'] = True
    with pytest.raises(ValueError, match='frozen source reconstruction'):
        core.verify(altered)


def test_figure_keeps_all_dates_fixed_examples_and_scope():
    receipt = json.loads((core.ROOT/'research/eac-csiro-100m-section-core-spans-figure.json').read_bytes())
    assert receipt['source_sha256'] == core.sha(core.ROOT/core.REPORT)
    assert receipt['primary_resolved']+receipt['primary_unresolved'] == receipt['all_dates_included'] == 3770
    assert receipt['fixed_source_indices'] == [0, 1885, 3769]
    assert receipt['physical_width_admitted'] is False and receipt['annual_range_admitted'] is False
    assert receipt['provider_uncertainty_assigned_confidence_convention'] is False
    for file, pin in receipt['input_sha256'].items(): assert core.sha(core.ROOT/file) == pin
    for asset in receipt['figures'].values(): assert core.sha(core.ROOT/asset['file']) == asset['sha256']
    assert 'eac-core-description' in (core.ROOT/receipt['figures']['.svg']['file']).read_text(encoding='utf8')


def test_compact_summary_binds_full_corpus_without_embedding_profiles():
    import eac_core_spans as summary
    doc,pins=summary.verify_inputs()
    assert 'profiles' not in doc and doc['counts']['source_dates']==3770
    assert doc['raw_profile_sha256']==core.sha(core.ROOT/core.REPORT)
    assert pins[summary.FILE]==core.sha(core.ROOT/summary.FILE)
    assert len(doc['scenario_names'])==3 and doc['fractions']==[.4,.5,.6]
    assert doc['physical_width_admitted'] is False
    assert len(doc['months'])==124
