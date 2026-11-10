"""Source illustration extent-circle readings; no physical eddy boundary fitted."""
import hashlib
import itertools
import json
from pathlib import Path
from eddy_map_spans_v1 import span_interval

WINDOWS = {'west': [161, 280, 173, 296], 'east': [288, 279, 301, 296],
           'north': [224, 218, 240, 231], 'south': [224, 344, 240, 359]}
AXES = {'longitude': [[138, 13], [210, 14], [282, 15], [354, 16]],
        'latitude': [[115, -35], [223, -36], [332, -37], [441, -38]]}


def read_extremum(samples, width, height, direction, gate):
    assert len(samples) == width*height and direction in WINDOWS and gate in [150, 190]
    x0, y0, x1, y1 = WINDOWS[direction]
    assert 0 <= x0 < x1 < width and 0 <= y0 < y1 < height
    points = [[x, y] for y in range(y0, y1+1) for x in range(x0, x1+1)
              if samples[y*width+x] <= gate]
    assert len(points) >= 10
    axis = 0 if direction in ['west', 'east'] else 1
    value = (min if direction in ['west', 'north'] else max)(p[axis] for p in points)
    assert (x0 if axis == 0 else y0) < value < (x1 if axis == 0 else y1)
    return {'direction': direction, 'window_xyxy_inclusive': WINDOWS[direction],
            'axis_coordinate_pixel': value, 'selected_ink_pixels': len(points),
            'selected_ink_pixels_sha256': hashlib.sha256(json.dumps(points, separators=(',', ':')).encode()).hexdigest()}


def spans(case, component):
    assert component in ['east_west', 'north_south']
    rows = []
    for stroke in case['stroke_cases']:
        for shifts in itertools.product([-2, 2], repeat=8):
            axes = {key: [[p+s, v] for (p, v), s in zip(AXES[key], shifts[offset:offset+4])]
                    for key, offset in [('longitude', 0), ('latitude', 4)]}
            rows.append(span_interval({**case, 'axes': axes, 'outline': {'bbox_xyxy': stroke['bbox_xyxy']}}, component))
    nominal = span_interval({**case, 'outline': {'bbox_xyxy': case['stroke_cases'][0]['bbox_xyxy']}}, component)
    return {'audit_span_km': nominal['audit_span_km'], 'audit_decimal_places': 6,
            'audit_reading_interval_km': [min(r['audit_reading_interval_km'][0] for r in rows),
                                        max(r['audit_reading_interval_km'][1] for r in rows)],
            'range_km': [min(r['range_km'][0] for r in rows), max(r['range_km'][1] for r in rows)],
            'total_scenarios': len(rows), 'ink_maximum_gray_sensitivity': [150, 190]}


def validate_case(case):
    assert case['method'] == 'source_cartographic_extent_circle_spans_v1'
    assert case['source_name'] == 'Laura' and case['owner_id'] == 'eddy:geography:laura-1999'
    assert (case['pdf_page'], case['figure']) == (6, 3) and case['source_raster']['xref'] == 62
    assert (case['source_raster']['width'], case['source_raster']['height'], case['source_raster']['channels']) == (794, 600, 1)
    assert len(case['source_raster']['samples_sha256']) == 64
    assert case['axes'] == AXES and case['date'] is None
    assert case['source_month_label'] == 'Mar 00' and case['month_context'] == '2000-03'
    assert case['earth_radius_km'] == 6371 and case['reading_allowance_pixels'] == 6
    assert case['axis_sensitivity_pixels'] == 2 and case['round_outward_km'] == 25
    assert case['boundary_operator'] is None and case['source_uncertainty_km'] is None
    for key in ['circle_is_physical_boundary', 'geodesic_circle_assumed', 'circle_fit_performed',
                'physical_crosswalk_verified', 'physical_state_join_eligible', 'area_derived',
                'diameter_inferred', 'exact_survey_instant_known', 'annual_extrema_inferred']:
        assert case[key] is False
    assert [s['ink_maximum_gray'] for s in case['stroke_cases']] == [150, 190]
    for stroke in case['stroke_cases']:
        readings = stroke['extremum_readings']
        assert [r['direction'] for r in readings] == list(WINDOWS)
        for r in readings:
            assert r['window_xyxy_inclusive'] == WINDOWS[r['direction']]
            assert r['selected_ink_pixels'] >= 10 and len(r['selected_ink_pixels_sha256']) == 64
            x0, y0, x1, y1 = WINDOWS[r['direction']];a, b = (x0, x1) if r['direction'] in ['west', 'east'] else (y0, y1)
            assert a < r['axis_coordinate_pixel'] < b
        assert stroke['bbox_xyxy'] == [readings[i]['axis_coordinate_pixel'] for i in [0, 2, 1, 3]]
    for component in ['east_west', 'north_south']: spans(case, component)


def validate_record(case, row):
    validate_case(case)
    assert row['entity_id'] == case['owner_id'] and row['category'] == 'size' and row['unit'] == 'km'
    assert row['value'] is None and row['evidence_role'] == 'source_illustration_extent_reference'
    assert row['period_start'] is None and row['period_end'] is None
    assert row['period_precision'] == 'source_month_label_no_exact_survey_instant'
    assert row['metric'] == 'source_cartographic_circle_'+row['map_span_component']+'_bounding_arc_span'
    assert row['range_value'] == spans(case, row['map_span_component'])['range_km']
    assert row['range_kind'] == 'source_illustration_ink_calibration_and_reading_interval'
    assert row['rights_screened_release_eligible'] is False


def validate_ssh_record(row):
    c = row['profile_context']
    assert c['method'] == 'source_reported_laura_survey_ssh_anomaly'
    assert row['entity_id'] == 'eddy:geography:laura-1999'
    assert (row['category'], row['metric'], row['value'], row['unit']) == ('structure', 'author_reported_approximate_maximum_ssh_anomaly', 40, 'cm')
    assert row['period_start'] is None and row['period_end'] is None and row['period_precision'] == 'source_cruise_month'
    assert row['evidence_role'] == 'qualified_published_named_case_reference' and row['rights_screened_release_eligible'] is False
    assert c['survey_month'] == '2000-03' and c['source_qualifier'] == 'about'
    assert c['quantity'] == 'positive_sea_surface_height_anomaly_maximum' and c['anomaly_reference'] is None
    assert row.get('depth_m') is None and row.get('range_value') is None
    assert all(c[k] is False for k in ['is_eddy_vertical_extent', 'hydrographic_and_ssh_centers_assumed_equal',
                                      'full_lifetime_maximum_inferred', 'annual_extrema_inferred', 'raw_altimeter_fields_acquired'])


def verify_source(pdf, batch_path):
    from verify_eddy_plot_source_v1 import constrain
    constrain()
    import pymupdf
    batch = json.loads(batch_path.read_bytes()); source = batch['sources']['van-aken-2003-laura']
    assert pdf.stat().st_size == source['original']['bytes'] < 2000000
    assert hashlib.sha256(pdf.read_bytes()).hexdigest() == source['original']['sha256']
    case = batch['cartographic_circle_cases'][0]; validate_case(case)
    with pymupdf.open(pdf) as d:
        assert len(d) == 29 and 62 in [r[0] for r in d[5].get_images(full=True)]
        pix = pymupdf.Pixmap(d, 62); raw = pix.samples
        assert (pix.width, pix.height, pix.n) == (794, 600, 1)
        assert hashlib.sha256(raw).hexdigest() == case['source_raster']['samples_sha256']
        for stroke in case['stroke_cases']:
            assert [read_extremum(raw, 794, 600, direction, stroke['ink_maximum_gray'])
                    for direction in WINDOWS] == stroke['extremum_readings']
        # The source font's positive sign extracts as thorn; actual page pixels
        # were reviewed to verify the printed +40 cm, without OCR correction.
        text = d[5].get_text(); assert 'Laura' in text and 'about \u00fe40 cm' in text and 'circles indicate the extension' in text
        assert 'not surveyed completely' in d[7].get_text()
    return {'schema': 'osw.eddy-cartographic-circle-source-verification.v1', 'status': 'PASS',
            'batch_sha256': hashlib.sha256(batch_path.read_bytes()).hexdigest(),
            'original_pdf_sha256': source['original']['sha256'],
            'verifier_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'span_math_sha256': hashlib.sha256((Path(__file__).parent/'eddy_map_spans_v1.py').read_bytes()).hexdigest(),
            'source_pixels_verified': True, 'source_caption_and_ssh_text_verified': True,
            'stroke_cases': case['stroke_cases'],
            'spans': {c: spans(case, c) for c in ['east_west', 'north_south']},
            'physical_boundary_admitted': False, 'runtime_changed': False}
