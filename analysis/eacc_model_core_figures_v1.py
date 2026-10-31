"""Regional source maps, all retained normal profiles and semantic evidence.

Original arrays are rendered only inside the frozen cloud case. Cartographic
land context is independent of the velocity mask and never defines an edge.
"""
import calendar
import hashlib
import html
import io
import json
import math
from pathlib import Path
import zipfile

from pyproj import Geod


ROOT = Path(__file__).resolve().parents[1]
LAND_ARCHIVE = 'research/source-data/natural-earth-land-10m-5.1.1/ne_10m_land.zip'
LAND_RECEIPT = 'research/source-data/natural-earth-land-10m-5.1.1/acquisition.json'
LAND_SHA = 'e547d749445eaa0964aba76738090ec88f5e63c4585122170f98c67a7ea922dc'
GEOD = Geod(ellps='WGS84')
REGION = (38., -13., 44., -5.)
V_LIMIT = .6
NS = 'http://www.w3.org/2000/svg'


def esc(value):
    return html.escape(str(value), quote=True)


def fmt(value, digits=3):
    return 'unsupported' if value is None else f'{value:.{digits}f}'


def project(lon, lat):
    return 100 + (lon - 38) * 80, 150 + (-5 - lat) * 80


def _line_parts(geometry):
    if geometry.geom_type == 'LineString':
        return [] if geometry.is_empty else [list(geometry.coords)]
    if geometry.geom_type in ('MultiLineString', 'GeometryCollection'):
        return [line for part in geometry.geoms for line in _line_parts(part)]
    return []


def load_land_context(root=ROOT):
    import shapefile
    from shapely.geometry import box, shape
    root = Path(root)
    raw = (root / LAND_ARCHIVE).read_bytes()
    receipt = json.loads((root / LAND_RECEIPT).read_bytes())
    if hashlib.sha256(raw).hexdigest() != LAND_SHA or receipt['sha256'] != LAND_SHA or receipt['bytes'] != len(raw) or receipt['package_version'] != '5.1.1':
        raise ValueError('Changed cartographic land archive/receipt')
    if shapefile.__version__ != '2.3.1':
        raise ValueError('Use the frozen PyShp reader')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = {name for name in archive.namelist() if not name.endswith('/')}
        if names != set(receipt['members']):
            raise ValueError('Changed land member inventory')
        for name, expected in receipt['members'].items():
            item = archive.getinfo(name)
            if item.file_size != expected['bytes'] or item.file_size > 8 * 1024 * 1024:
                raise ValueError('Changed land member size')
            if hashlib.sha256(archive.read(name)).hexdigest() != expected['sha256']:
                raise ValueError('Changed land member bytes')
        if archive.read('ne_10m_land.VERSION.txt').decode().strip() != '5.1.1' or 'GCS_WGS_1984' not in archive.read('ne_10m_land.prj').decode():
            raise ValueError('Changed land edition or coordinate frame')
        options = {suffix: io.BytesIO(archive.read('ne_10m_land.' + suffix)) for suffix in ('shp', 'shx', 'dbf')}
    region = box(*REGION)
    segments = []
    with shapefile.Reader(**options) as reader:
        for item in reader.iterShapes(bbox=REGION):
            geometry = shape(item.__geo_interface__)
            if not geometry.is_valid:
                raise ValueError('Invalid source land; do not silently repair')
            # Clip the original boundary, not a clipped polygon's boundary:
            # the latter would invent shorelines along the viewport edges.
            clipped = geometry.boundary.intersection(region)
            segments.extend(_line_parts(clipped))
    if not segments:
        raise ValueError('No regional land context')
    return {'shoreline_segments': segments, 'evidence_class': 'natural_earth_cartographic_context',
            'source_url': receipt['product_url'], 'source_sha256': LAND_SHA,
            'label': 'Natural Earth 5.1.1 land, 1:10 million, public domain',
            'cartographic_land_is_velocity_mask': False}


def _svg(width, height, title, description):
    return [f'<svg xmlns="{NS}" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{esc(title)}</title><desc id="desc">{esc(description)}</desc>',
            '<rect width="100%" height="100%" fill="#fff"/>']


def _text(x, y, value, size=14, **attributes):
    attrs = ' '.join(f'{key.replace("_", "-")}="{esc(value)}"' for key, value in attributes.items())
    return f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="{size}" fill="#152c39" {attrs}>{esc(value)}</text>'


def _segments(rows, point):
    segments, current = [], []
    for row in rows:
        value = point(row)
        if value is None:
            if current: segments.append(current)
            current = []
        else:
            current.append(value)
    if current: segments.append(current)
    return segments


def _polyline(points, color, dashed=False, width=1.5):
    if len(points) < 2: return ''
    coords = ' '.join(f'{x:.3f},{y:.3f}' for x, y in points)
    return f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="{width}"' + (' stroke-dasharray="5 4"' if dashed else '') + '/>'


def _color(v):
    t = min(1., abs(v) / V_LIMIT)
    end = (188, 73, 25) if v >= 0 else (31, 107, 169)
    rgb = [round(246 + t * (channel - 246)) for channel in end]
    return '#' + ''.join(f'{channel:02x}' for channel in rgb)


def _edges(axis):
    return [axis[0] - (axis[1] - axis[0]) / 2] + [(a + b) / 2 for a, b in zip(axis, axis[1:])] + [axis[-1] + (axis[-1] - axis[-2]) / 2]


def _month_cases(diagnostic, month):
    return [case for case in diagnostic['cases'] if case['month'] == month]


def map_svg(fields, month, cases, land):
    number = month['month']
    out = _svg(820, 920, f'2013-{number:02d} EACC candidate: regional model diagnostic',
               'Equirectangular source map, 38–44E and 13–5S, at 15 m standard output depth. Northward velocity colors are clipped at plus/minus 0.6 m/s. Arrows show direction only. Black shoreline context is independent of the missing-velocity hatch. Lines and edge markers are diagnostic candidates, not a named-current footprint. See equivalent source-grid and threshold tables.')
    out += [_text(35, 35, f'{calendar.month_name[number]} 2013 · EACC candidate core', 22),
            _text(35, 65, 'HYCOM daily-00Z sample means · standard output depth 15 m', 16),
            _text(35, 90, 'Regional model diagnostic; current association and physical ranges unreviewed.', 14),
            '<defs><clipPath id="map"><rect x="100" y="150" width="480" height="640"/></clipPath>',
            '<pattern id="missing" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" fill="#e9edf0"/><path d="M0 6L6 0" stroke="#79858c" stroke-width="1"/></pattern>',
            '</defs>',
            '<g clip-path="url(#map)"><rect x="100" y="150" width="480" height="640" fill="#fff5d5"/>']
    lon, lat = fields['longitude_degrees_east'], fields['latitude_degrees_north']
    xe, ye = _edges(lon), _edges(lat)
    for yi in range(len(lat)):
        for xi in range(len(lon)):
            u, v = month['eastward_m_s'][yi][xi], month['northward_m_s'][yi][xi]
            x, y = project(xe[xi], ye[yi + 1])
            right, bottom = project(xe[xi + 1], ye[yi])
            color = 'url(#missing)' if u is None or v is None else _color(v)
            out.append(f'<rect x="{x:.3f}" y="{y:.3f}" width="{right-x:.3f}" height="{bottom-y:.3f}" fill="{color}"/>')
    for line in land['shoreline_segments']:
        out.append(_polyline([project(*point[:2]) for point in line], '#101e27', width=1.2))
    stride = max(1, round(max(len(lat), len(lon)) / 18))
    for yi in range(0, len(lat), stride):
        for xi in range(0, len(lon), stride):
            u, v = month['eastward_m_s'][yi][xi], month['northward_m_s'][yi][xi]
            if u is None or v is None or math.hypot(u, v) == 0: continue
            end = GEOD.fwd(lon[xi], lat[yi], math.degrees(math.atan2(u, v)), 12000)[:2]
            x, y = project(lon[xi], lat[yi]); x2, y2 = project(*end)
            out.append(f'<line x1="{x:.3f}" y1="{y:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="#fff" stroke-width="3"/>')
            out.append(f'<line x1="{x:.3f}" y1="{y:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="#172d3a" stroke-width="1"/>')
            length = math.hypot(x2 - x, y2 - y)
            dx, dy = (x2 - x) / length, (y2 - y) / length
            head = [(x2, y2), (x2 - 4 * dx + 2 * dy, y2 - 4 * dy - 2 * dx),
                    (x2 - 4 * dx - 2 * dy, y2 - 4 * dy + 2 * dx)]
            out.append(f'<polygon points="{" ".join(f"{a:.3f},{b:.3f}" for a,b in head)}" fill="#172d3a" stroke="white" stroke-width="0.4"/>')
    for case in cases:
        if case['native_latitude_offset'] != 0: continue
        dashed = case['normal_sample_step_km'] == 10
        color = '#6b187d' if dashed else '#143f30'
        for path in case['paths']:
            out.append(_polyline([project(*point) for point in path['vertices_lon_lat']], color, dashed, 2))
        for station in case['stations']:
            segments = _segments(station['samples'], lambda row: project(row[1], row[2]) if row[-1] == 'ok' and row[5] is not None else None)
            for segment in segments: out.append(_polyline(segment, '#74818a', dashed, .8))
            for threshold in station['threshold_cases']:
                for edge in threshold['edges'].values():
                    if edge.get('point_lon_lat') is None: continue
                    x, y = project(*edge['point_lon_lat'])
                    out.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="2.5" fill="white" stroke="{color}"/>')
    out.append('</g><rect x="100" y="150" width="480" height="640" fill="none" stroke="#172d3a"/>')
    for longitude in range(38, 45):
        x, _ = project(longitude, -13)
        out.append(_text(x, 815, f'{longitude}°E', text_anchor='middle'))
    for latitude in range(-13, -4):
        _, y = project(38, latitude)
        out.append(_text(90, y + 4, f'{abs(latitude)}°S', text_anchor='end'))
    legend = ['Northward V (m/s)', '+0.6 or more: orange', '0: pale gray', '−0.6 or less: blue', 'Hatch: missing pair', 'Cream: beyond source grid', 'Black: shoreline context', 'Arrows: direction only', 'Gray: normal profiles', 'Green: 5 km candidate path', 'Purple dashed: 10 km path', 'Circles: 40/50/60% edges', 'No full-current polygon']
    for i, line in enumerate(legend): out.append(_text(600, 165 + 26 * i, line, 12))
    x, y = project(38.5, -12)
    endpoint = GEOD.fwd(38.5, -12, 90, 50000)[:2]
    x2, y2 = project(*endpoint)
    out += [f'<line x1="{x:.3f}" y1="{y:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="#111" stroke-width="3"/>',
            _text(x, y + 20, '50 km at 12°S', 12),
            _text(35, 850, 'Equirectangular longitude/latitude · WGS84 geodesic diagnostics', 14),
            _text(35, 875, land['label'], 13),
            _text(35, 897, 'Land map scale is not positional accuracy; this is not a navigation chart.', 13), '</svg>']
    return ''.join(out)


def profiles_svg(month, cases):
    panels = [(case, station) for case in cases for station in (case['stations'] or [None])]
    out = _svg(920, 100 + 230 * len(panels), f'2013-{month:02d} retained normal profiles',
               'Every retained case/station, including failed seeds. Horizontal axes are signed normal distance in km; vertical axes are projected tangent velocity in m/s. Gaps are not connected. Threshold lines are core definitions, not uncertainty limits. Equivalent threshold tables are in the monthly HTML.')
    out.append(_text(30, 35, f'{calendar.month_name[month]} 2013 · retained normal profiles', 23))
    out.append(_text(30, 65, 'Projected tangent velocity q (m/s); signed geodesic normal offset (km). No physical range admitted.', 14))
    for index, (case, station) in enumerate(panels):
        top = 100 + index * 230
        label = case['id'] + (' · no supported station' if station is None else f" · station {station['station_arc_parameter_km']:+g} km")
        out.append(_text(30, top, label, 15))
        status = case['status'] if station is None else ', '.join(station['failed_axis_checks']) or 'local numerical axis checks pass'
        out.append(_text(30, top + 20, status, 12))
        rows = [] if station is None else station['samples']
        valid = [row for row in rows if row[-1] == 'ok' and row[5] is not None]
        if not valid:
            out.append(_text(50, top + 80, 'Unsupported: no retained finite paired profile; no zero-width inference.', 14))
            continue
        low = min(0., *(row[5] for row in valid)); high = max(.1, *(row[5] for row in valid))
        margin = .08 * (high - low); low -= margin; high += margin
        left = min(-5, *(row[0] for row in rows)); right = max(5, *(row[0] for row in rows))
        point = lambda row: (85 + (row[0] - left) / (right - left) * 770, top + 175 - (row[5] - low) / (high - low) * 125)
        out.append(f'<rect x="85" y="{top+50}" width="770" height="125" fill="#f3f5f6" stroke="#485a65"/>')
        zero_x = 85 + (0 - left) / (right - left) * 770
        zero_y = top + 175 - (0 - low) / (high - low) * 125
        out += [f'<line x1="{zero_x:.3f}" y1="{top+50}" x2="{zero_x:.3f}" y2="{top+175}" stroke="#8b979f" stroke-dasharray="2 3"/>',
                f'<line x1="85" y1="{zero_y:.3f}" x2="855" y2="{zero_y:.3f}" stroke="#c2c9ce"/>',
                _text(zero_x, top + 195, '0 km', 12, text_anchor='middle')]
        for segment in _segments(rows, lambda row: point(row) if row[-1] == 'ok' and row[5] is not None else None):
            out.append(_polyline(segment, '#183e59', case['normal_sample_step_km'] == 10, 2))
        peak = station['peak']['peak_projected_m_s']
        if peak is not None:
            for fraction in (.4, .5, .6):
                y = top + 175 - (peak * fraction - low) / (high - low) * 125
                out += [f'<line x1="85" y1="{y:.3f}" x2="855" y2="{y:.3f}" stroke="#976523" stroke-dasharray="3 4"/>', _text(860, y + 4, f'{fraction:.0%}', 11)]
        for threshold in station['threshold_cases']:
            for edge in threshold['edges'].values():
                if edge.get('offset_km') is None: continue
                x = 85 + (edge['offset_km'] - left) / (right - left) * 770
                y = top + 175 - (edge['threshold_projected_m_s'] - low) / (high - low) * 125
                out.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="3" fill="#fff" stroke="#172d3a"/>')
        out += [_text(78, top + 60, fmt(high, 2), 11, text_anchor='end'), _text(78, top + 175, fmt(low, 2), 11, text_anchor='end'),
                _text(85, top + 195, f'{left:g} km', 12), _text(855, top + 195, f'{right:g} km', 12, text_anchor='end')]
    return ''.join(out + ['</svg>'])


STYLE = 'body{font:16px/1.5 system-ui,sans-serif;color:#172d3a;max-width:70rem;margin:auto;padding:1rem}a{color:#13558a}a:focus-visible,summary:focus-visible{outline:3px solid #964600;outline-offset:3px}img{display:block;width:100%;height:auto}table{border-collapse:collapse}th,td{padding:.35rem;border:1px solid #abb7bf;text-align:left;vertical-align:top}caption{text-align:left;font-weight:600} .scroll{overflow:auto;max-width:100%}h1{font-size:clamp(1.5rem,5vw,2.2rem)}code{overflow-wrap:anywhere}summary{padding:.6rem;cursor:pointer}nav a{display:inline-block;padding:.5rem}td{min-width:6rem}'


def _page(title, body):
    return f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><style>{STYLE}</style><body><main><h1>{esc(title)}</h1>{body}</main></body></html>'


STATUS_GUIDE = '<section aria-labelledby="status-guide"><h2 id="status-guide">Reading the outcomes</h2><ul><li>Missing support: one or more paired samples/corners are unavailable. This does not mean zero flow or current absence.</li><li>Tied seed: more than one location shares the strongest northward component under the numerical tie rule.</li><li>Unresolved edges: a gap, domain limit or competing rise prevents a supported edge pair. One edge is never doubled.</li><li>Insufficient resolution: the span is narrower than four of the largest source-cell scales it crosses.</li><li>Resolved regional diagnostic: the numerical gates passed; current identity and measurement admission still require review.</li></ul></section>'


def raster_png(svg):
    """Static raster evidence, no browser; originals use this only in cloud."""
    import pymupdf
    with pymupdf.open(stream=svg.encode('utf8'), filetype='svg') as document:
        return document[0].get_pixmap().tobytes('png')


def _threshold_table(cases):
    out = ['<div class="scroll" tabindex="0" role="region" aria-label="Retained case and threshold data"><table><caption>All cases, stations and threshold outcomes. Unsupported spans are not zero.</caption><thead><tr>']
    out += [f'<th scope="col">{title}</th>' for title in ('Case / status', 'Station (km)', 'Core fraction', 'Edge support', 'Diagnostic span (km)', 'Resolved span (km)', 'Native scale (km)')]
    out.append('</tr></thead><tbody>')
    for case in cases:
        if not case['stations']:
            out.append(f'<tr><th scope="row"><code>{esc(case["id"])}</code></th><td colspan="6">{esc(case["status"])}; unsupported, no span inferred</td></tr>')
        for station in case['stations']:
            for threshold in station['threshold_cases']:
                edges = '; '.join(name + ': ' + edge['status'] for name, edge in threshold['edges'].items()) or threshold['status']
                values = [station['station_arc_parameter_km'], f'{threshold["fraction"]:.0%}', edges,
                          fmt(threshold['diagnostic_span_km']), fmt(threshold['resolved_span_km']), fmt(threshold['native_cell_scale_km'])]
                out.append(f'<tr><th scope="row"><code>{esc(case["id"])}</code><br>{esc(case["status"])}<br>{esc(threshold["status"])}</th>' + ''.join(f'<td>{esc(value)}</td>' for value in values) + '</tr>')
    return ''.join(out + ['</tbody></table></div>'])


def _profile_table(cases):
    out = ['<details><summary>Equivalent normal-profile sample values</summary><p>Signed normal offset in km; coordinates in geographic degrees; U, V and projected tangent q in m/s. Display rounding is not measurement uncertainty.</p><div class="scroll" tabindex="0" role="region" aria-label="Normal-profile samples"><table><caption>Every retained profile sample, including the first unsupported sample.</caption><thead><tr>']
    out += [f'<th scope="col">{label}</th>' for label in ('Case / station', 'Offset (km)', 'Longitude', 'Latitude', 'U', 'V', 'q', 'Support')]
    out.append('</tr></thead><tbody>')
    for case in cases:
        for station in case['stations']:
            for row in station['samples']:
                values = [fmt(row[0]), fmt(row[1], 6), fmt(row[2], 6), fmt(row[3]), fmt(row[4]), fmt(row[5]), row[-1].replace('_', ' ')]
                out.append(f'<tr><th scope="row">{esc(case["id"])} / {station["station_arc_parameter_km"]:+g} km</th>' + ''.join(f'<td>{esc(value)}</td>' for value in values) + '</tr>')
    return ''.join(out + ['</tbody></table></div></details>'])


def _grid_table(fields, month):
    out = ['<details><summary>Equivalent source-grid values: U, V and paired counts</summary><p>Output-cell centers; velocities in m/s, displayed to 0.001 m/s. Readback precision is not uncertainty. Missing means remain unsupported. Original unrounded values are in the linked source JSON.</p><div class="scroll" tabindex="0" role="region" aria-label="Source-grid vector data"><table><caption>Latitude rows and longitude columns; every source position.</caption><thead><tr><th scope="col">Latitude / longitude (degrees)</th>']
    out += [f'<th scope="col">{lon:.6f}°E</th>' for lon in fields['longitude_degrees_east']]
    out.append('</tr></thead><tbody>')
    for yi in reversed(range(len(fields['latitude_degrees_north']))):
        out.append(f'<tr><th scope="row">{fields["latitude_degrees_north"][yi]:.6f}°N</th>')
        for xi in range(len(fields['longitude_degrees_east'])):
            u, v = month['eastward_m_s'][yi][xi], month['northward_m_s'][yi][xi]
            out.append(f'<td>U {fmt(u)}<br>V {fmt(v)}<br>pairs {month["paired_samples"][yi][xi]}</td>')
        out.append('</tr>')
    return ''.join(out + ['</tbody></table></div></details>'])


def _validate(fields, diagnostic):
    if fields.get('schema') != 'osw.eacc-hycom.monthly-vector-fields.v1' or diagnostic.get('schema') != 'osw.eacc-regional-model-core.numerical-diagnostic.v2':
        raise ValueError('Unexpected source/diagnostic schema')
    if [month['month'] for month in fields['months']] != list(range(1, 13)) or len(diagnostic['cases']) != 72:
        raise ValueError('All twelve months and 72 attempts must be retained')
    expected = {(month, offset, step) for month in range(1, 13) for offset in (-1, 0, 1) for step in (5, 10)}
    actual = {(case['month'], case['native_latitude_offset'], case['normal_sample_step_km']) for case in diagnostic['cases']}
    if actual != expected or len({case['id'] for case in diagnostic['cases']}) != 72:
        raise ValueError('Duplicate or missing case identity')
    if fields['source_model_year'] != 2013 or fields['provider_depth_m'] != 15:
        raise ValueError('Unexpected source year or output depth')
    lat, lon = fields['latitude_degrees_north'], fields['longitude_degrees_east']
    for axis in (lat, lon):
        if len(axis) < 2 or not all(math.isfinite(value) for value in axis) or any(b <= a for a, b in zip(axis, axis[1:])):
            raise ValueError('Invalid source coordinate order')
    for month in fields['months']:
        for name in ('eastward_m_s', 'northward_m_s', 'paired_samples'):
            matrix = month[name]
            if len(matrix) != len(lat) or any(len(row) != len(lon) for row in matrix):
                raise ValueError('Source vector/count shape differs from coordinates')
        if any(value is not None and not math.isfinite(value) for name in ('eastward_m_s', 'northward_m_s') for row in month[name] for value in row):
            raise ValueError('Nonfinite source display values')


def render_case(fields, diagnostic, directory, land_context=None, rasterize=False):
    _validate(fields, diagnostic)
    land = load_land_context() if land_context is None else land_context
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    links, outputs = [], {}
    for month in fields['months']:
        number = month['month']; cases = _month_cases(diagnostic, number)
        if len(cases) != 6: raise ValueError('Missing monthly diagnostic attempts')
        prefix = f'm{number:02d}'
        files = {prefix + '-map.svg': map_svg(fields, month, cases, land),
                 prefix + '-profiles.svg': profiles_svg(number, cases)}
        body = f'<nav aria-label="Evidence pages"><a href="index.html">All months</a><a href="../monthly-fields.json">Unrounded source fields</a><a href="../diagnostic.json">Complete diagnostic</a><a href="../selection.json">Exact source requests</a><a href="../preflight.json">Frozen method</a></nav><p>Regional model diagnostic at 15 m; current association and physical ranges are unreviewed. Daily 00Z sample means are not observations or climatology. A width of a monthly mean is not mean instantaneous width. Seed/step/threshold differences are method sensitivity, not error bars.</p><p>Source support: {month["sample_days"]} sampled days; minimum {month["minimum_pairs"]} paired calendar days per cell; {month["eligible_cells"]} eligible cells. Unsupported results do not imply current absence.</p>'
        body += f'<figure><img src="{prefix}-map.svg" alt="Regional source map with independent shoreline context, missing support, candidate lines and sampled edges; equivalent grid and threshold data follow."><figcaption>Equirectangular map; arrows show direction only. Source masks are not land. {esc(land["label"])}; <a href="{esc(land["source_url"])}">cartographic source</a>.</figcaption></figure>'
        body += STATUS_GUIDE + _threshold_table(cases)
        body += f'<figure><img src="{prefix}-profiles.svg" loading="lazy" alt="All retained normal-profile panels, including failed cases; threshold outcomes are in the preceding table."><figcaption>Signed projected velocity across each local normal. Missing samples are not joined.</figcaption></figure>'
        body += _profile_table(cases)
        body += _grid_table(fields, month)
        files[prefix + '.html'] = _page(f'{calendar.month_name[number]} 2013: EACC model-core evidence', body)
        for name, content in files.items():
            raw = content.encode('utf8')
            with (directory / name).open('xb') as stream: stream.write(raw)
            outputs[name] = {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
            if rasterize and name.endswith('.svg'):
                png_name = name.removesuffix('.svg') + '.png'
                png = raster_png(content)
                with (directory / png_name).open('xb') as stream: stream.write(png)
                outputs[png_name] = {'bytes': len(png), 'sha256': hashlib.sha256(png).hexdigest()}
        links.append(f'<li><a href="{prefix}.html">{calendar.month_name[number]}: source map, all profiles and data tables</a></li>')
    index = _page('EACC regional model-core evidence · 2013', '<p>Unreviewed regional model diagnostics, not admitted current dimensions. All twelve months and 72 attempts are retained, including unsupported outcomes. No animation is played automatically.</p><ul>' + ''.join(links) + '</ul>')
    (directory / 'index.html').write_text(index, encoding='utf8')
    index_raw = index.encode('utf8')
    outputs['index.html'] = {'bytes': len(index_raw), 'sha256': hashlib.sha256(index_raw).hexdigest()}
    manifest = {'schema': 'osw.eacc-model-core.figures.v1', 'months': 12, 'cases': 72,
                'projection': 'equirectangular longitude/latitude', 'region_lon_lat': list(REGION),
                'velocity_color_clip_m_s': [-V_LIMIT, V_LIMIT], 'arrows_show': 'direction_only',
                'cartographic_context': {key: value for key, value in land.items() if key != 'shoreline_segments'},
                'files': outputs, 'raster_pngs': rasterize, 'named_current_association_reviewed': False,
                'physical_annual_range_admitted': False, 'new_current_widths_admitted': 0}
    (directory / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf8')
    return manifest
