"""Declared regional dimensions from publisher-identified daily model curves."""
from pathlib import Path
from datetime import date, timedelta
from collections import Counter
from statistics import median
import gzip
import hashlib
import io
import json
import math
import xml.etree.ElementTree as ET
import zipfile

import netCDF4
from pyproj import Geod

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = 'research/source-data/kuroshio-wang-2026-v1/'
SOURCE = DIRECTORY + 'kuroshio_2024.nc.gz'
RECEIPT = DIRECTORY + 'acquisition.json'
METADATA = DIRECTORY + 'provider-metadata.json'
SCRIPT = DIRECTORY + 'read_plot.py'
PROTOCOL = 'plans/kuroshio-wang-2024-dimensions-protocol-v1.md'
OPERATOR = 'analysis/kuroshio_wang_dimensions.py'
FILE = 'research/kuroshio-wang-2024-regional-dimensions.json'
FIGURE = 'figures/kuroshio-wang-2024-monthly-snapshots.svg'
ORIGINAL_SHA = '82375f6da17f83f462fc574ea8fc710f79e11cc8e63f5fd010091ea8d3a6946c'
ARCHIVE_SHA = '7a7d8f818f0364526e1b8de34eeb183fce8b9029182c328b00a7c3e823819688'
LAND = 'research/source-data/natural-earth-land-10m-5.1.1/ne_10m_land.zip'
LEVELS = {1: 0.49, 23: 109.73, 30: 380.21}
SECTIONS = (18.5, 21.5, 24.5, 27.5, 29.5)
GEOD = Geod(ellps='WGS84')


def digest(path):
    with (ROOT / path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':')) + '\n').encode()


def source_bytes():
    if digest(SOURCE) != ARCHIVE_SHA:
        raise ValueError('Changed compressed Kuroshio original')
    with gzip.open(ROOT / SOURCE, 'rb') as stream:
        data = stream.read()
    if len(data) != 130603298 or hashlib.sha256(data).hexdigest() != ORIGINAL_SHA:
        raise ValueError('Changed uncompressed Kuroshio original')
    if hashlib.md5(data).hexdigest() != '945fd3bba891a2d12e640ee0ea582348':
        raise ValueError('Provider original checksum mismatch')
    return data


def distance(a, b):
    return GEOD.inv(*a, *b)[2] / 1000


def valid(point):
    return point is not None and len(point) == 2 and all(math.isfinite(x) for x in point) and -180 <= point[0] <= 180 and -90 <= point[1] <= 90


def crossings(points, latitude):
    """Unique source-coordinate intersections; never bridge a missing vertex."""
    found = []; overlap = False
    for i, (a, b) in enumerate(zip(points, points[1:])):
        if not valid(a) or not valid(b):
            continue
        if a[1] == b[1] == latitude:
            overlap = True
            continue
        if a[1] == b[1] or not min(a[1], b[1]) <= latitude <= max(a[1], b[1]):
            continue
        t = (latitude - a[1]) / (b[1] - a[1])
        point = [a[0] + t * (b[0] - a[0]), latitude]
        position = i + t
        # Shared source vertex appears from each adjacent segment.
        if any(abs(position - row['position']) < 1e-10 for row in found):
            continue
        found.append({'point': point, 'position': position, 'segment_km': distance(a, b)})
    return found, overlap


def axis_length(points):
    start, sa = crossings(points, 18.0); end, ea = crossings(points, 30.0)
    row = {'start_crossings': len(start), 'end_crossings': len(end), 'length_km': None}
    if sa or ea:
        return {**row, 'status': 'gate_overlap'}
    if len(start) != 1 or len(end) != 1:
        return {**row, 'status': 'gate_missing_or_multiple'}
    a, b = start[0], end[0]
    if a['position'] >= b['position']:
        return {**row, 'status': 'reversed_gate_order'}
    inside = points[math.floor(a['position']) + 1:math.ceil(b['position'])]
    if not all(valid(p) for p in inside):
        return {**row, 'status': 'internal_missing_vertex'}
    clipped = [a['point'], *inside, b['point']]
    legs = [distance(x, y) for x, y in zip(clipped, clipped[1:])]
    if max([a['segment_km'], b['segment_km'], *legs]) > 50:
        return {**row, 'status': 'source_segment_exceeds_50km'}
    return {**row, 'status': 'resolved', 'length_km': round(math.fsum(legs), 6),
            'gates_lon_lat': [a['point'], b['point']], 'vertices': len(clipped)}


def section_span(curves, latitude):
    values = [crossings(curves[k], latitude) for k in ['axis', 'left', 'right']]
    row = {'latitude': latitude, 'span_km': None,
           'crossing_counts': [len(v[0]) for v in values]}
    if any(v[1] for v in values):
        return {**row, 'status': 'section_overlap'}
    if any(len(v[0]) != 1 for v in values):
        return {**row, 'status': 'section_missing_or_multiple'}
    axis, left, right = [v[0][0] for v in values]
    if max(v['segment_km'] for v in [axis, left, right]) > 50:
        return {**row, 'status': 'source_segment_exceeds_50km'}
    if not min(left['point'][0], right['point'][0]) <= axis['point'][0] <= max(left['point'][0], right['point'][0]):
        return {**row, 'status': 'axis_not_between_edges'}
    return {**row, 'status': 'resolved', 'span_km': round(distance(left['point'], right['point']), 6),
            'section_lon_lat': [left['point'], axis['point'], right['point']]}


def summary(values):
    return {'valid_count': len(values), 'minimum_km': min(values) if values else None,
            'median_km': round(median(values), 6) if values else None,
            'maximum_km': max(values) if values else None}


def read_curves(group):
    result = {}
    for kind, prefix in [('axis', 'main_axis'), ('left', 'left_bdy'), ('right', 'right_bdy')]:
        lon = group.variables[prefix + '_lon']; lat = group.variables[prefix + '_lat']
        if lon.dimensions != ('point',) or lat.dimensions != ('point',) or lon.shape != lat.shape:
            raise ValueError('Unexpected source coordinate dimensions')
        if lon.units != 'degrees_east' or lat.units != 'degrees_north':
            raise ValueError('Changed source angular units')
        # Each curve independently preserves its own missing vertices. No index pairing.
        result[kind] = [[float(x), float(y)] if math.isfinite(float(x)) and math.isfinite(float(y)) else None
                        for x, y in zip(lon[:].filled(float('nan')), lat[:].filled(float('nan')))]
        if any(p is not None and not valid(p) for p in result[kind]):
            raise ValueError('Source coordinate out of bounds')
    return result


def build():
    receipt = json.loads((ROOT / RECEIPT).read_bytes())
    metadata = json.loads((ROOT / METADATA).read_bytes())
    if metadata['doi'] != '10.6084/m9.figshare.30267070.v1' or metadata['license']['name'] != 'CC BY 4.0':
        raise ValueError('Changed dataset edition or licence')
    if receipt['provider_doi'] != metadata['doi'] or receipt['license'] != metadata['license']:
        raise ValueError('Custody and provider source disagree')
    original = next(f for f in metadata['files'] if f['name'] == 'kuroshio_2024.nc')
    if original['id'] != 63345796 or original['size'] != 130603298 or original['computed_md5'] != '945fd3bba891a2d12e640ee0ea582348':
        raise ValueError('Changed2024 provider file identity')
    compressed = receipt['compressed_original']
    if compressed['sha256'] != ARCHIVE_SHA or compressed['uncompressed_sha256'] != ORIGINAL_SHA or compressed['bytes'] != (ROOT/SOURCE).stat().st_size:
        raise ValueError('Compressed original custody mismatch')
    for item in receipt['files']:
        if item['file'] != 'kuroshio_2024.nc' and digest(DIRECTORY + item['file']) != item['sha256']:
            raise ValueError('Changed retained provider companion')
    rows = []; frames = []
    with netCDF4.Dataset('publisher-original', memory=source_bytes()) as dataset:
        if set(dataset.groups) != {f'day{i:03}' for i in range(1, 367)}:
            raise ValueError('Incomplete2024 leap-year day inventory')
        for day in range(1, 367):
            group = dataset.groups[f'day{day:03}']
            if set(group.groups) != {f'depth{i:02}' for i in range(1, 31)}:
                raise ValueError('Incomplete source depth inventory')
            when = date(2024, 1, 1) + timedelta(days=day - 1)
            for level, depth in LEVELS.items():
                curves = read_curves(group.groups[f'depth{level:02}'])
                row = {'date': when.isoformat(), 'source_day': day, 'source_level': level,
                       'nominal_depth_m': depth, 'axis': axis_length(curves['axis']),
                       'sections': [section_span(curves, lat) for lat in SECTIONS]}
                rows.append(row)
                if when.day == 1:
                    # Display-only rounding, after all numerical admission decisions.
                    display = {k: [None if p is None else [round(p[0], 6), round(p[1], 6)] for p in v]
                               for k, v in curves.items()}
                    frames.append({'date': when.isoformat(), 'source_level': level,
                                   'nominal_depth_m': depth, 'curves_lon_lat': display})
    summaries = []
    for level, depth in LEVELS.items():
        for month in [None, *range(1, 13)]:
            selected = [r for r in rows if r['source_level'] == level and (month is None or int(r['date'][5:7]) == month)]
            summaries.append({'source_level': level, 'nominal_depth_m': depth, 'month': month,
                              'expected_days': len(selected), 'axis_length': summary([r['axis']['length_km'] for r in selected if r['axis']['status'] == 'resolved']),
                              'sections': [{'latitude': lat, **summary([r['sections'][i]['span_km'] for r in selected if r['sections'][i]['status'] == 'resolved'])} for i, lat in enumerate(SECTIONS)]})
    files = [SOURCE, RECEIPT, METADATA, SCRIPT, PROTOCOL, OPERATOR, LAND, 'requirements-test.txt']
    return {'schema': 'osw.kuroshio-publisher-regional-dimensions.v1',
            'current_id': 'kuroshio', 'entity_id': 'current:kuroshio',
            'status': 'reproducible_model_regional_dimensions_not_inventory_admission',
            'source': {'doi': metadata['doi'], 'paper_doi': '10.1038/s41597-026-07275-3',
                       'attribution': 'Wang, J., Chen, X., Mao, K. and Zhang, C. (2026). Kuroshio axis and boundary dataset, v1. CC BY4.0.',
                       'license_url': metadata['license']['url'], 'original_sha256': ORIGINAL_SHA,
                       'basis': 'Publisher-identified GLORYS12V1 reanalysis; not direct daily observations'},
            'input_sha256': {p: digest(p) for p in files},
            'conventions': {'year': 2024, 'levels': LEVELS, 'axis_gates_latitude': [18, 30],
                            'section_latitudes': SECTIONS, 'maximum_source_segment_km': 50,
                            'range_kind': 'empirical_model_sample_extrema_within2024_not_error_or_climatology',
                            'span_kind': 'fixed_latitude_smoothed_boundary_geodesic_separation_not_flow_normal_width',
                            'boundary_threshold_fraction': 0.3, 'fallback_occurrence': 'not encoded; search truncation possible',
                            'source_smoothing_km': 110, 'section_interpolation': 'piecewise linear lon_lat; no missing-point bridging'},
            'counts': {'source_days': 366, 'source_depth_levels': 30, 'extracted_depth_levels': 3,
                       'daily_depth_cases': len(rows), 'section_cases': len(rows) * len(SECTIONS),
                       'display_frames': len(frames)},
            'axis_status_counts': dict(Counter(r['axis']['status'] for r in rows)),
            'section_status_counts': dict(Counter(s['status'] for r in rows for s in r['sections'])),
            'daily': rows, 'summaries': summaries, 'display_frames': frames,
            'rank_eligible': False, 'scoped_width_inventory_admitted': False,
            'whole_current_width_km': None, 'whole_current_length_km': None,
            'annual_physical_width_range_km': None, 'physical_state_passage_admitted': False,
            'figure': FIGURE}


def figure_bytes(doc):
    """Native SVG scientific panels; source gaps remain visible."""
    import shapefile
    from shapely.geometry import shape, box
    ns = 'http://www.w3.org/2000/svg'; ET.register_namespace('', ns)
    def node(parent, tag, attrs=None, text=None):
        e = ET.SubElement(parent, '{' + ns + '}' + tag, {k: str(v) for k, v in (attrs or {}).items()})
        e.text = text; return e
    svg = ET.Element('{' + ns + '}svg', {'viewBox': '0 0 1200 1390', 'width': '1200', 'height': '1390', 'role': 'img'})
    node(svg, 'title', text='Kuroshio 2024: twelve dated regional model snapshots at 0.49 m')
    node(svg, 'desc', text='East China Sea and Luzon Strait. Separate axis and left/right smoothed model boundaries. First day of each month, not monthly means. Length uses18–30N gates. Fixed24.5N span is oblique, not a flow-normal width. Missing source vertices break lines.')
    node(svg, 'rect', {'width': 1200, 'height': 1390, 'fill': '#f8fafb'})
    node(svg, 'text', {'x': 28, 'y': 37, 'font-size': 26, 'font-family': 'sans-serif', 'fill': '#12374a'}, 'Kuroshio · twelve dated 2024 model snapshots · 0.49 m')
    for i, text in enumerate(['GLORYS12V1 curves: solid navy axis · dashed purple left · dotted teal right.',
                              'Length: 18–30°N regional axis. Span: fixed 24.5°N section; not a flow-normal width.',
                              'First day of month, not monthly mean. Fallback edge censoring is unknown.']):
        node(svg, 'text', {'x': 28, 'y': 65 + i*25, 'font-size': 17, 'font-family': 'sans-serif'}, text)
    land = []
    if digest(LAND) != 'e547d749445eaa0964aba76738090ec88f5e63c4585122170f98c67a7ea922dc':
        raise ValueError('Changed map-context land source')
    with zipfile.ZipFile(ROOT / LAND) as archive:
        with shapefile.Reader(**{s: io.BytesIO(archive.read('ne_10m_land.' + s)) for s in ['shp', 'shx', 'dbf']}) as reader:
            for item in reader.iterShapes(bbox=(118, 15, 132, 32)):
                g = shape(item.__geo_interface__).intersection(box(118, 15, 132, 32))
                parts = [g] if g.geom_type == 'Polygon' else list(g.geoms) if g.geom_type == 'MultiPolygon' else []
                land.extend(parts)
    defs = node(svg, 'defs'); cp = node(defs, 'clipPath', {'id': 'panel'}); node(cp, 'rect', {'x': 0, 'y': 0, 'width': 260, 'height': 300})
    def xy(p): return (260*(p[0]-118)/14, 300*(32-p[1])/17)
    def path(points):
        commands = []; pen = False
        for p in points:
            if p is None: pen = False; continue
            x, y = xy(p); commands.append(('L' if pen else 'M') + f'{x:.3f},{y:.3f}'); pen = True
        return ' '.join(commands)
    surface = [r for r in doc['display_frames'] if r['source_level'] == 1]
    for i, frame in enumerate(surface):
        x, y = 28+(i%4)*297, 170+(i//4)*390
        node(svg, 'text', {'x': x, 'y': y-13, 'font-size': 18, 'font-family': 'sans-serif'}, frame['date'])
        g = node(svg, 'g', {'transform': f'translate({x},{y})'})
        clip = node(g, 'g', {'clip-path': 'url(#panel)'})
        node(clip, 'rect', {'width': 260, 'height': 300, 'fill': '#e4f1f5'})
        for polygon in land:
            d = path(list(polygon.exterior.coords))+'Z'
            for ring in polygon.interiors: d += ' '+path(list(ring.coords))+'Z'
            node(clip, 'path', {'d': d, 'fill': '#d9d6c8', 'fill-rule': 'evenodd'})
        for lat in [18, 24.5, 30]:
            yy = xy([118, lat])[1]
            node(clip, 'path', {'d': f'M0,{yy}H260', 'stroke': '#718691', 'stroke-width': '.6', 'stroke-dasharray': '3 3', 'fill': 'none'})
            node(clip, 'text', {'x': 3, 'y': yy-3, 'font-size': 11, 'font-family': 'sans-serif'}, f'{lat}°N')
        for lon in [120, 125, 130]:
            node(clip, 'text', {'x': xy([lon, 15])[0]-13, 'y': 295, 'font-size': 10, 'font-family': 'sans-serif'}, f'{lon}°E')
        for key, color, dash in [('left', '#a03e9d', '6 2'), ('right', '#008278', '2 2'), ('axis', '#153e75', None)]:
            attrs = {'d': path(frame['curves_lon_lat'][key]), 'fill': 'none', 'stroke': color, 'stroke-width': 1.7}
            if dash: attrs['stroke-dasharray'] = dash
            node(clip, 'path', attrs)
        row = next(r for r in doc['daily'] if r['date'] == frame['date'] and r['source_level'] == 1)
        length, span = row['axis']['length_km'], row['sections'][2]['span_km']
        for j, label in enumerate([f'18–30°N: ≈{round(length/10)*10} km' if length is not None else '18–30°N length unresolved', f'24.5°N: ≈{round(span/10)*10} km span' if span is not None else '24.5°N span unresolved']):
            node(g, 'text', {'x': 0, 'y': 323+j*21, 'font-size': 14, 'font-family': 'sans-serif'}, label)
    for i, text in enumerate(['Wang, Chen, Mao & Zhang (2026), doi:10.1038/s41597-026-07275-3; data doi:10.6084/m9.figshare.30267070.v1, CC BY4.0.',
                              'OSW derived dimensions; equirectangular display. Natural Earth land1:10 million v5.1.1, public domain; map scale is not positional accuracy.',
                              'No whole-current measurement, physical annual extrema, uncertainty interval, NASA association or occupied-area polygon inferred.']):
        node(svg, 'text', {'x': 28, 'y': 1350+i*17, 'font-size': 11, 'font-family': 'sans-serif'}, text)
    return ET.tostring(svg, encoding='utf-8', xml_declaration=True)


def verify_inputs():
    doc = json.loads((ROOT / FILE).read_bytes())
    for p, sha in doc['input_sha256'].items():
        if digest(p) != sha: raise ValueError('Changed Kuroshio dimension input: '+p)
    if (ROOT / FIGURE).read_bytes() != figure_bytes(doc):
        raise ValueError('Changed Kuroshio snapshot figure')
    return doc


if __name__ == '__main__':
    result = build()
    (ROOT / FILE).write_bytes(encoded(result))
    (ROOT / FIGURE).write_bytes(figure_bytes(result))
    print(json.dumps({'counts': result['counts'], 'axis': result['axis_status_counts'], 'sections': result['section_status_counts']}))
