"""Dated author-image SSH colour-patch spans, never whole-eddy dimensions.

Only rendered source images are processed. No ocean fields or runtime are read.
"""
import hashlib
import itertools
import json
import math
from pathlib import Path

METHOD = 'source_author_animation_ssh_patch_v1'
LEVELS = [0.70, 0.75, 0.80]


def palette_readout(samples, width, height):
    assert (width, height) == (2255, 950) and len(samples) == width*height*3
    # Actual legend endpoints: top coloured pixel 71, bottom coloured pixel 844.
    # Duplicate RGB chips collapse to their lowest level, preserving the
    # deterministic minimum-level tie rule used by nearest-colour matching.
    levels = {}
    for y in range(71, 845):
        rgb = samples[(y*width+1737)*3:(y*width+1737)*3+3]
        levels[rgb] = round((844-y)/773, 9)
    return [{'level_m': levels[rgb], 'rgb': list(rgb)} for rgb in sorted(levels)]


def patch_readouts(samples, width, height, roi, palette):
    assert len(samples) == width*height*3 and len(palette) == 134
    x0, y0, x1, y1 = roi
    assert 0 <= x0 < x1 < width and 0 <= y0 < y1 < height
    # GIF palette has few colours: classify each unique RGB once, deterministically.
    colours = {samples[(y*width+x)*3:(y*width+x)*3+3]
               for y in range(y0, y1+1) for x in range(x0, x1+1)}
    lookup = {c: min((sum((a-b)**2 for a, b in zip(c, p['rgb'])), p['level_m'])
                     for p in palette) for c in sorted(colours)}
    result = []
    for level in LEVELS:
        points = {(x, y) for y in range(y0, y1+1) for x in range(x0, x1+1)
                  if lookup[samples[(y*width+x)*3:(y*width+x)*3+3]][0] <= 900
                  and lookup[samples[(y*width+x)*3:(y*width+x)*3+3]][1] >= level}
        components = []
        while points:
            first = min(points); points.remove(first); todo = [first]; selected = {first}
            while todo:
                x, y = todo.pop()
                for dx, dy in itertools.product([-1, 0, 1], repeat=2):
                    q = (x+dx, y+dy)
                    if q in points:
                        points.remove(q); todo.append(q); selected.add(q)
            components.append(selected)
        components.sort(key=lambda c: (-len(c), min(c)))
        assert components and len(components[0]) > 1000
        selected = components[0]
        assert len(components) == 1 or len(selected) > 10*len(components[1])
        bbox = [min(x for x, y in selected), min(y for x, y in selected),
                max(x for x, y in selected), max(y for x, y in selected)]
        assert x0+6 < bbox[0] < bbox[2] < x1-6 and y0+6 < bbox[1] < bbox[3] < y1-6
        result.append({'level_m': level, 'bbox_xyxy': bbox, 'selected_pixels': len(selected),
                       'selected_pixels_sha256': hashlib.sha256(json.dumps(sorted(selected), separators=(',', ':')).encode()).hexdigest(),
                       'other_component_sizes': [len(c) for c in components[1:]]})
    return result


def axis_value(pixel, anchors, mercator=False):
    assert anchors[0][0] <= pixel <= anchors[-1][0]
    for (p, a), (q, b) in zip(anchors, anchors[1:]):
        if p <= pixel <= q:
            t = (pixel-p)/(q-p)
            if mercator:
                a, b = [math.asinh(math.tan(math.radians(v))) for v in [a, b]]
                return math.degrees(math.atan(math.sinh(a+t*(b-a))))
            return a+t*(b-a)
    raise AssertionError('Uncalibrated coordinate')


def spans(case, component):
    assert component in ['east_west', 'north_south']
    rows = []; nominal = None; km = 6371*math.pi/180
    for index, patch in enumerate(case['patch_cases']):
        x0, y0, x1, y1 = patch['bbox_xyxy']
        for shifts in itertools.product([-2, 2], repeat=6):
            lon = [[p+s, v] for (p, v), s in zip(case['axes']['longitude'], shifts[:3])]
            lat = [[p+s, v] for (p, v), s in zip(case['axes']['latitude'], shifts[3:])]
            for mercator in [False, True]:
                av = lambda y: axis_value(y, lat, mercator)
                if component == 'north_south':
                    lo = max(0, av(y0+6)-av(y1-6))*km
                    hi = (av(y0-6)-av(y1+6))*km
                else:
                    cosines = [math.cos(math.radians((av(y0+a)+av(y1+b))/2))
                               for a, b in itertools.product([-6, 6], repeat=2)]
                    lo = max(0, axis_value(x1-6, lon)-axis_value(x0+6, lon))*km*min(cosines)
                    hi = (axis_value(x1+6, lon)-axis_value(x0-6, lon))*km*max(cosines)
                rows.append([lo, hi])
        if index == 1:
            lon, lat = case['axes']['longitude'], case['axes']['latitude']
            nominal = ((axis_value(y0, lat)-axis_value(y1, lat))*km if component == 'north_south'
                       else (axis_value(x1, lon)-axis_value(x0, lon))*km*
                       math.cos(math.radians((axis_value(y0, lat)+axis_value(y1, lat))/2)))
    lo, hi = min(r[0] for r in rows), max(r[1] for r in rows)
    return {'audit_span_km': round(nominal, 6), 'audit_reading_interval_km': [round(lo, 6), round(hi, 6)],
            'audit_decimal_places': 6, 'range_km': [math.floor(lo/25)*25, math.ceil(hi/25)*25],
            'plot_level_sensitivity_m': LEVELS, 'total_scenarios': len(rows),
            'latitude_interpolations': ['piecewise_linear_degrees', 'piecewise_linear_mercator']}


def validate_case(case):
    assert case['method'] == METHOD and case['source_name'] == 'Atwater'
    assert case['owner_id'] == 'eddy:horizon:loop-76-primary' and case['date'] == '2023-07-30'
    assert case['frame_index_zero_based'] == 0 and case['animation_frames'] == 4
    assert case['legend_label'] == 'SSH (m)' and case['source_level_m'] == 0.75
    assert case['axes'] == {'longitude': [[1021, -92], [1252, -88], [1484, -84]],
                            'latitude': [[338, 28], [467, 26], [595, 24]]}
    assert case['roi_xyxy_inclusive'] == [1040, 350, 1355, 505]
    assert case['earth_radius_km'] == 6371 and case['reading_allowance_pixels'] == 6
    assert case['axis_sensitivity_pixels'] == 2 and case['round_outward_km'] == 25
    assert case['rgb_distance_squared_max'] == 900 and case['palette_sample_x'] == 1737
    assert case['legend_coloured_y_endpoints'] == [71, 844]
    assert [p['level_m'] for p in case['patch_cases']] == LEVELS
    assert len(case['palette']) == 134
    assert case['source_raster']['width'] == 2255 and case['source_raster']['height'] == 950
    assert len(case['source_raster']['samples_sha256']) == 64
    for key in ['physical_crosswalk_verified', 'full_ring_boundary_admitted', 'physical_state_join_eligible',
                'observational_measurement_admitted', 'exact_field_product_verified', 'seasonal_range_inferred']:
        assert case[key] is False
    assert case['field_datum'] is None and case['source_original_pdf_acquired'] is False
    for p in case['patch_cases']:
        x0, y0, x1, y1 = p['bbox_xyxy']
        assert 1046 < x0 < x1 < 1349 and 356 < y0 < y1 < 499
        assert p['selected_pixels'] > 1000 and len(p['selected_pixels_sha256']) == 64
        assert not p['other_component_sizes'] or p['selected_pixels'] > 10*max(p['other_component_sizes'])
    for c in ['east_west', 'north_south']: spans(case, c)


def verify_source(gif, batch_path):
    from verify_eddy_plot_source_v1 import constrain
    constrain()
    from PIL import Image
    batch = json.loads(batch_path.read_bytes()); source = batch['sources']['hu-2026-author-animation']
    assert gif.stat().st_size == source['original']['bytes'] < 2000000
    assert hashlib.sha256(gif.read_bytes()).hexdigest() == source['original']['sha256']
    case = batch['author_animation_patch_cases'][0]; validate_case(case)
    with Image.open(gif) as im:
        assert im.n_frames == 4 and im.size == (2255, 950)
        im.seek(0); raw = im.convert('RGB').tobytes()
    assert hashlib.sha256(raw).hexdigest() == case['source_raster']['samples_sha256']
    palette = palette_readout(raw, 2255, 950); assert palette == case['palette']
    patches = patch_readouts(raw, 2255, 950, case['roi_xyxy_inclusive'], palette)
    assert patches == case['patch_cases']
    return {'schema': 'osw.eddy-author-animation-patch-verification.v1', 'status': 'PASS',
            'source_pixels_verified': True, 'source_palette_verified': True,
            'batch_sha256': hashlib.sha256(batch_path.read_bytes()).hexdigest(),
            'original_gif_sha256': source['original']['sha256'],
            'verifier_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'patches': patches, 'spans': {c: spans(case, c) for c in ['east_west', 'north_south']},
            'physical_footprint_admitted': False, 'runtime_changed': False}


def validate_record(case, row):
    validate_case(case)
    assert row['entity_id'] == case['owner_id'] and row['category'] == 'size' and row['unit'] == 'km'
    assert row['map_span_component'] in ['east_west', 'north_south']
    assert row['metric'] == 'author_image_ssh_patch_'+row['map_span_component']+'_bounding_arc_span'
    assert row['period_start'] == row['period_end'] == case['date']
    assert row['value'] is None and row['evidence_role'] == 'qualified_author_image_patch_reference'
    assert row['rights_screened_release_eligible'] is False
    assert row['range_kind'] == 'source_image_colour_selection_calibration_and_reading_interval'
    assert row['range_value'] == spans(case, row['map_span_component'])['range_km']
