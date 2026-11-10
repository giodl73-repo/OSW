"""Manual spans of a specified plotted SSH isoline; no physical boundary inference."""
import itertools
import math

from eddy_map_spans_v1 import span_interval

METHOD = 'source_manual_qe2_5cm_isoline_spans_v1'


def summarize(report, component):
    assert report['schema'] == 'osw.eddy-qe2-manual-isoline-source-review.v1'
    c = report['case']
    assert c['owner_id'] == 'eddy:horizon:loop-40-secondary'
    assert c['source_name'] == 'QE2' and c['source_map_date'] == '2002-08-08'
    assert c['source_ssh_contour_cm'] == 5 and c['source_contour_interval_cm'] == 5
    assert c['source_ssh_reference'] == 'unspecified in reviewed source'
    assert c['contour_level_assignment'] == 'intermediate line between labeled 0 and 10 cm contours, checked against the 5 cm color-key intervals'
    assert c['outline']['bbox_xyxy'] == [475, 480, 554, 547]
    assert c['manual_extrema_xy'] == {'west': [475, 500], 'north': [520, 480], 'east': [554, 520], 'south': [530, 547]}
    assert c['axes'] == {'longitude': [[314, -93], [443, -90], [574, -87]], 'latitude': [[357, 27], [500, 24], [641, 21]]}
    assert c['reading_allowance_pixels'] == 6 and c['axis_sensitivity_pixels'] == 2
    assert c['round_outward_km'] == 25 and c['earth_radius_km'] == 6371
    assert c['native_raster']['xref'] == 1202
    assert [c['native_raster']['width'], c['native_raster']['height']] == [971, 950]
    assert report['original']['sha256'] == '87242ed9c88aa27f209c0e3994483af94d48af7ed9253b54ce7020aa29a70286'
    assert all(c[k] is False for k in [
        'source_map_date_is_exact_observation_time', 'closed_boundary_topology_verified',
        'missing_segments_reconstructed', 'whole_physical_eddy_extent_inferred',
        'physical_crosswalk_verified', 'physical_footprint_admitted',
        'physical_state_join_eligible', 'rights_screened_release_eligible',
        'annual_extrema_inferred', 'principal_width_inferred', 'diameter_inferred',
        'source_operator_equated_to_osw_speed_core',
    ])
    assert report['prior_speed_core_rejection_preserved'] is True
    assert report['prior_closed_ink_rejections_preserved'] is True
    assert all(report['source_verification'][k] is True for k in [
        'original_pdf_bytes_and_sha256_verified', 'native_raster_samples_verified',
        'actual_source_pixels_reviewed', 'named_eastern_split_feature_text_reviewed',
    ])
    intervals = []
    for shifts in itertools.product([-2, 2], repeat=6):
        axes = {key: [[p + delta, v] for (p, v), delta in zip(c['axes'][key], changes)]
                for key, changes in [('longitude', shifts[:3]), ('latitude', shifts[3:])]}
        intervals.append(span_interval({**c, 'axes': axes}, component)['audit_reading_interval_km'])
    nominal = span_interval(c, component)
    lo, hi = min(v[0] for v in intervals), max(v[1] for v in intervals)
    return {'method': METHOD, 'component': component, 'source_case_name': 'QE2',
            'source_map_date': c['source_map_date'], 'observation_date': None,
            'source_ssh_contour_cm': 5, 'source_ssh_reference': c['source_ssh_reference'],
            'audit_visible_isoline_span_km': nominal['audit_span_km'],
            'audit_reading_interval_km': [lo, hi],
            'range_km': [math.floor(lo / 25) * 25, math.ceil(hi / 25) * 25],
            'reading_allowance_native_pixels': 6, 'axis_allowance_native_pixels': 2,
            'axis_shift_scenarios': len(intervals), 'round_outward_km': 25,
            'manual_reading_only': True, 'physical_uncertainty_quantified': False,
            'closed_boundary_inferred': False, 'whole_physical_eddy_extent_inferred': False,
            'source_operator_equated_to_osw_speed_core': False}
