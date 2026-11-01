"""Dated source-chart isoline spans, never physical polygons or principal widths."""
import hashlib
import itertools
import json
import math

from eddy_map_spans_v1 import span_interval

AXES = {'longitude': [[271, -98], [899, -90], [1526, -82]],
        'latitude': [[388, 30], [702, 26], [1016, 22]]}
SOURCES = {
    '2022-12-29': {'sha256': '501b64286d74b58f8e7a2a3e3c79761078f03f62aeed71558b01644634fc9154', 'bytes': 1038075, 'height': 1697},
    '2023-01-13': {'sha256': 'a5cca5b4fb42ba2e07602635eff537bc9c5151a514cd32228a0f503cf97b755c', 'bytes': 926977, 'height': 1698},
}


def read_outline(samples, width, height, roi, gate):
    """Select a dominant closed neutral-ink component without repairing any gaps."""
    assert len(samples) == width * height * 3 and gate in [150, 175]
    x0, y0, x1, y1 = roi
    assert 0 <= x0 < x1 < width and 0 <= y0 < y1 < height
    points = set()
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            rgb = samples[(y * width + x) * 3:(y * width + x) * 3 + 3]
            if max(rgb) <= gate and max(rgb) - min(rgb) <= 40:
                points.add((x, y))
    parts = []
    while points:
        first = min(points); points.remove(first); todo = [first]; part = {first}
        while todo:
            x, y = todo.pop()
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    q = x + dx, y + dy
                    if q in points:
                        points.remove(q); part.add(q); todo.append(q)
        parts.append(part)
    parts.sort(key=lambda p: (-len(p), min(p)))
    assert parts and len(parts[0]) > 200
    selected = parts[0]
    assert len(parts) == 1 or len(selected) > 3 * len(parts[1]), 'Ambiguous line selection'
    bbox = [min(x for x, y in selected), min(y for x, y in selected),
            max(x for x, y in selected), max(y for x, y in selected)]
    assert x0 < bbox[0] < bbox[2] < x1 and y0 < bbox[1] < bbox[3] < y1, 'Clipped line'
    border = {(x, y) for x in range(x0, x1 + 1) for y in [y0, y1]} | {(x, y) for x in [x0, x1] for y in range(y0, y1 + 1)}
    outside = border - selected; todo = list(outside)
    while todo:
        x, y = todo.pop()
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            q = x + dx, y + dy
            if x0 <= q[0] <= x1 and y0 <= q[1] <= y1 and q not in selected and q not in outside:
                outside.add(q); todo.append(q)
    enclosed = (x1 - x0 + 1) * (y1 - y0 + 1) - len(outside) - len(selected)
    assert enclosed > 300, 'Source ink does not enclose a region'
    return {'maximum_rgb_channel': gate, 'maximum_rgb_spread': 40, 'bbox_xyxy': bbox,
            'selected_pixels': len(selected), 'selected_pixels_sha256': hashlib.sha256(json.dumps(sorted(selected), separators=(',', ':')).encode()).hexdigest(),
            'other_component_sizes': [len(p) for p in parts[1:]], 'enclosed_background_pixels': enclosed}


def validate_case(c):
    assert c['method'] == 'source_bold_ssh_isoline_spans_v1'
    assert c['owner_id'] == 'eddy:horizon:loop-75-primary' and c['source_name'] == 'Zodiac'
    source = SOURCES[c['date']]
    assert c['source_raster']['sha256'] == source['sha256'] and c['source_raster']['bytes'] == source['bytes']
    assert (c['source_raster']['width'], c['source_raster']['height']) == (2308, source['height'])
    assert len(c['source_raster']['rgb_samples_sha256']) == 64
    assert c['axes'] == AXES and c['roi_xyxy_inclusive'] == [950, 430, 1370, 880]
    assert c['earth_radius_km'] == 6371 and c['reading_allowance_pixels'] == 6 and c['axis_sensitivity_pixels'] == 2 and c['round_outward_km'] == 25
    assert c['source_ssh_contour_cm'] == 17 and c['source_ssh_reference'] == 'unspecified in reviewed source'
    assert c['source_contour_provider'] == 'Robert Leben / CCAR'
    assert c['source_date_is_map_label'] is True
    assert all(c[k] is False for k in ['association_is_verified', 'missing_ink_reconstructed', 'physical_footprint_admitted', 'physical_state_join_eligible', 'rights_screened_release_eligible', 'whole_eddy_dimensions_inferred', 'annual_extrema_inferred', 'source_operator_equated_to_osw'])
    assert len(c['readings']) == 2 and {r['maximum_rgb_channel'] for r in c['readings']} == {150, 175}
    for r in c['readings']:
        x0, y0, x1, y1 = r['bbox_xyxy']
        assert 950 < x0 < x1 < 1370 and 430 < y0 < y1 < 880
        assert r['maximum_rgb_spread'] == 40 and r['selected_pixels'] > 200 and r['enclosed_background_pixels'] > 300
        assert not r['other_component_sizes'] or r['selected_pixels'] > 3 * max(r['other_component_sizes'])
        assert len(r['selected_pixels_sha256']) == 64
    return c


def spans(c, component):
    validate_case(c)
    assert component in ['east_west', 'north_south']
    intervals = []
    for reading in c['readings']:
        for shifts in itertools.product([-2, 2], repeat=6):
            axes = {key: [[p + delta, v] for (p, v), delta in zip(c['axes'][key], changes)]
                    for key, changes in [('longitude', shifts[:3]), ('latitude', shifts[3:])]}
            value = span_interval({**c, 'axes': axes, 'outline': reading}, component)
            intervals.append(value['audit_reading_interval_km'])
    nominal = span_interval({**c, 'outline': c['readings'][1]}, component)
    lo, hi = min(r[0] for r in intervals), max(r[1] for r in intervals)
    return {'audit_visible_isoline_span_km': nominal['audit_span_km'], 'audit_reading_interval_km': [lo, hi],
            'range_km': [math.floor(lo / 25) * 25, math.ceil(hi / 25) * 25], 'total_scenarios': len(intervals),
            'pixel_and_axis_sensitivity_only': True, 'whole_eddy_dimensions_inferred': False}
