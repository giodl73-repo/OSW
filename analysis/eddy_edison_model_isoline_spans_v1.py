"""Reading sensitivity for the preprint's control-model 0.4 m SSH isoline."""
import itertools
import math

from eddy_map_spans_v1 import span_interval

METHOD = 'source_manual_edison_control_0p4m_isoline_spans_v1'


def summarize(report, component):
    assert report['schema'] == 'osw.eddy-edison-control-isoline-source-review.v1'
    c = report['case']
    assert c['owner_id'] == 'eddy:horizon:loop-80-primary'
    assert c['source_name'] == 'Edison' and c['source_map_date'] == '2024-10-10'
    assert c['experiment'] == 'Control' and c['source_is_preprint'] is True
    assert c['source_ssh_contour_cm'] == 40
    assert c['source_ssh_reference'] == 'relative to source background level; datum unspecified in reviewed methods'
    assert c['outline']['bbox_xyxy'] == [218, 123, 262, 188]
    assert c['manual_extrema_xy_approx'] == {'west': [218, 151], 'north': [246, 123], 'east': [262, 144], 'south': [238, 188]}
    assert c['axes'] == {'longitude': [[126, -92], [212, -88], [300, -84]], 'latitude': [[57, 30], [144, 26], [230, 22]]}
    assert c['reading_allowance_pixels'] == 6 and c['axis_sensitivity_pixels'] == 2
    assert c['round_outward_km'] == 25 and c['earth_radius_km'] == 6371
    assert c['native_raster'] == {'xref': 439, 'width': 1431, 'height': 1852, 'components': 3,
                                  'decoded_samples_sha256': '2f9839c85b7549cb2491935fb8c4c4fe22d26c3efd7bc84480898fb5a2ea4cd1'}
    assert report['original']['sha256'] == '0539dbe7f34a7391a7f291489891f097fb7895ea056eb0ba85e06ab2ef3c2413'
    assert all(c[k] is False for k in ['observation_inferred', 'closed_boundary_topology_verified',
        'missing_segments_reconstructed', 'whole_physical_eddy_extent_inferred', 'physical_crosswalk_verified',
        'physical_footprint_admitted', 'physical_state_join_eligible', 'rights_screened_release_eligible',
        'annual_extrema_inferred', 'principal_width_inferred', 'diameter_inferred',
        'source_operator_equated_to_osw_speed_core', 'counterfactual_experiment_values_inherited',
        'red_speed_contour_used_as_ssh_boundary'])
    assert all(report['source_verification'][k] is True for k in ['complete_pdf_eof_and_parser_verified',
        'native_raster_samples_verified', 'actual_source_pixels_reviewed', 'named_model_case_and_contour_legend_reviewed'])
    intervals = []
    for shifts in itertools.product([-2, 2], repeat=6):
        axes = {key: [[p + delta, v] for (p, v), delta in zip(c['axes'][key], changes)]
                for key, changes in [('longitude', shifts[:3]), ('latitude', shifts[3:])]}
        intervals.append(span_interval({**c, 'axes': axes}, component)['audit_reading_interval_km'])
    nominal = span_interval(c, component)
    lo, hi = min(v[0] for v in intervals), max(v[1] for v in intervals)
    return {'method': METHOD, 'component': component, 'source_case_name': 'Edison',
        'source_map_date': c['source_map_date'], 'observation_date': None, 'source_experiment': 'Control',
        'source_is_preprint': True, 'source_ssh_contour_cm': 40, 'source_ssh_reference': c['source_ssh_reference'],
        'audit_visible_isoline_span_km': nominal['audit_span_km'], 'audit_reading_interval_km': [lo, hi],
        'range_km': [math.floor(lo / 25) * 25, math.ceil(hi / 25) * 25],
        'reading_allowance_native_pixels': 6, 'axis_allowance_native_pixels': 2,
        'axis_shift_scenarios': len(intervals), 'round_outward_km': 25,
        'manual_reading_only': True, 'physical_uncertainty_quantified': False,
        'closed_boundary_inferred': False, 'whole_physical_eddy_extent_inferred': False,
        'source_operator_equated_to_osw_speed_core': False}
