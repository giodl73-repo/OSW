"""Synthetic geography and vectors only; no original land/ocean array reads."""
from copy import deepcopy
import hashlib
from html.parser import HTMLParser
import io
import json
import xml.etree.ElementTree as ET
import zipfile

import pytest

import eacc_model_core_figures_v1 as figures
from eacc_hycom_source_compilation_v1 import compile_source
from eacc_model_core_diagnostic_v2 import diagnose_year
from west_australian_regional_streamlines import Field
from test_eacc_hycom_source_compilation_v1 import source


@pytest.fixture(scope='module')
def case(source):
    metadata, plan, responses = source
    fields = compile_source(metadata, plan, responses.keys(), responses.__getitem__)
    diagnostic = diagnose_year({month['month']: Field(fields['longitude_degrees_east'], fields['latitude_degrees_north'], month['eastward_m_s'], month['northward_m_s']) for month in fields['months']})
    land = {'shoreline_segments': [[[39, -12], [39, -6]]],
            'label': 'Synthetic test shoreline; not real cartography',
            'evidence_class': 'synthetic_test_context', 'source_url': 'https://example.org/synthetic',
            'cartographic_land_is_velocity_mask': False}
    return fields, diagnostic, land


def test_all_months_failed_cases_and_source_values_have_semantic_pages(case, tmp_path):
    fields, diagnostic, land = case
    out = tmp_path / 'figures'
    manifest = figures.render_case(fields, diagnostic, out, land_context=land)
    assert manifest['months'] == 12 and manifest['cases'] == 72
    assert len(list(out.glob('*-map.svg'))) == len(list(out.glob('*-profiles.svg'))) == 12
    assert len(list(out.glob('m*.html'))) == 12
    assert manifest['cartographic_context']['evidence_class'] == 'synthetic_test_context'
    assert not manifest['named_current_association_reviewed']
    for name, expected in manifest['files'].items():
        raw = (out / name).read_bytes()
        assert len(raw) == expected['bytes'] and hashlib.sha256(raw).hexdigest() == expected['sha256']
        if name.endswith('.svg'):
            root = ET.fromstring(raw)
            assert root.get('role') == 'img' and root.get('aria-labelledby') == 'title desc'
            assert root.find('{'+figures.NS+'}title') is not None
            assert root.find('{'+figures.NS+'}desc') is not None
    january = (out / 'm01.html').read_text(encoding='utf8')
    assert 'Equivalent source-grid values' in january and 'Equivalent normal-profile sample values' in january
    assert 'U unsupported' in january and 'V unsupported' in january
    assert 'minimum 25 paired calendar days' in january
    assert 'missing_seed_bilinear_corners' in january
    assert 'role="region"' in january and 'tabindex="0"' in january and 'scope="row"' in january
    assert '<script' not in january and 'onmouseover' not in january
    assert 'Frozen method' in january and '../monthly-fields.json' in january
    assert 'All twelve months and 72 attempts' in (out / 'index.html').read_text(encoding='utf8')


def test_region_projection_has_correct_orientation_and_degree_aspect():
    assert figures.project(38, -5) == (100, 150)
    assert figures.project(44, -13) == (580, 790)
    assert figures.project(39, -5)[0] - 100 == figures.project(38, -6)[1] - 150


def test_missing_profile_samples_are_never_joined():
    points = [(-10, .2), (-5, .3), (0, None), (5, .3), (10, .2)]
    result = figures._segments(points, lambda row: row if row[1] is not None else None)
    assert result == [[(-10, .2), (-5, .3)], [(5, .3), (10, .2)]]


def test_velocity_scale_is_signed_clipped_and_distinct_from_missing(case):
    fields, diagnostic, land = case
    assert figures._color(1) == figures._color(.6)
    assert figures._color(-1) == figures._color(-.6)
    assert figures._color(.6) != figures._color(-.6)
    text = figures.map_svg(fields, fields['months'][0], diagnostic['cases'][:6], land)
    assert 'url(#missing)' in text and 'Cream: beyond source grid' in text
    assert 'Arrows: direction only' in text and 'Black: shoreline context' in text
    assert '50 km at 12°S' in text and 'No full-current polygon' in text


@pytest.mark.parametrize('change', ['missing_month', 'duplicate_case', 'wrong_depth', 'shape', 'nan', 'coordinate_order'])
def test_invalid_or_incomplete_evidence_is_rejected_before_output(case, tmp_path, change):
    fields, diagnostic, land = deepcopy(case)
    if change == 'missing_month': fields['months'].pop()
    if change == 'duplicate_case': diagnostic['cases'][-1] = diagnostic['cases'][0]
    if change == 'wrong_depth': fields['provider_depth_m'] = 100
    if change == 'shape': fields['months'][0]['eastward_m_s'][0].pop()
    if change == 'nan': fields['months'][0]['eastward_m_s'][0][0] = float('nan')
    if change == 'coordinate_order': fields['latitude_degrees_north'].reverse()
    with pytest.raises(ValueError):
        figures.render_case(fields, diagnostic, tmp_path / 'invalid', land_context=land)
    assert not (tmp_path / 'invalid').exists()


def write_land_fixture(tmp_path, monkeypatch, ring):
    import shapefile
    buffers = {name: io.BytesIO() for name in ('shp', 'shx', 'dbf')}
    with shapefile.Writer(**buffers, shapeType=shapefile.POLYGON) as writer:
        writer.field('name', 'C'); writer.poly([ring]); writer.record('synthetic')
    members = {'ne_10m_land.' + name: buffer.getvalue() for name, buffer in buffers.items()}
    members.update({'ne_10m_land.VERSION.txt': b'5.1.1\n', 'ne_10m_land.prj': b'GCS_WGS_1984'})
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, 'w') as stream:
        for name, raw in members.items(): stream.writestr(name, raw)
    raw = archive.getvalue(); sha = hashlib.sha256(raw).hexdigest()
    monkeypatch.setattr(figures, 'LAND_SHA', sha)
    target = tmp_path / figures.LAND_ARCHIVE
    target.parent.mkdir(parents=True)
    target.write_bytes(raw)
    receipt = {'sha256': sha, 'bytes': len(raw), 'package_version': '5.1.1',
               'members': {name: {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()} for name, data in members.items()},
               'product_url': 'https://example.org/synthetic'}
    (tmp_path / figures.LAND_RECEIPT).write_text(json.dumps(receipt), encoding='utf8')


def test_shoreline_clipping_does_not_invent_viewport_boundaries(tmp_path, monkeypatch):
    write_land_fixture(tmp_path, monkeypatch, [[37,-14],[37,-4],[40,-4],[40,-14],[37,-14]])
    context = figures.load_land_context(tmp_path)
    assert context['shoreline_segments']
    # The true shoreline here is only x=40; a clipped polygon's boundary would
    # invent x=38 and horizontal viewport-edge coastlines.
    assert all(point[0] == 40 for line in context['shoreline_segments'] for point in line)
    assert not context['cartographic_land_is_velocity_mask']


def test_invalid_original_cartographic_polygon_is_not_silently_repaired(tmp_path, monkeypatch):
    write_land_fixture(tmp_path, monkeypatch, [[38,-12],[42,-6],[38,-6],[42,-12],[38,-12]])
    with pytest.raises(ValueError, match='Invalid source land'):
        figures.load_land_context(tmp_path)


def test_positive_northward_profiles_have_curves_thresholds_and_sample_tables():
    from eacc_model_core_diagnostic_v2 import diagnostic_case
    from test_eacc_model_core_diagnostic_v2 import jet
    case = diagnostic_case(jet(), 6, 0, 5)
    assert case['all_five_half_peak_spans_resolved']
    svg = figures.profiles_svg(6, [case])
    root = ET.fromstring(svg)
    assert len(root.findall('{'+figures.NS+'}polyline')) == 5
    assert len(root.findall('{'+figures.NS+'}circle')) == 30  # two edges x three fractions x five stations
    assert '40%' in svg and '60%' in svg and 'm/s' in svg and 'km' in svg
    table = figures._profile_table([case])
    assert table.count('<tr><th scope="row">') == sum(len(station['samples']) for station in case['stations'])
    assert 'unsupported' in table and 'outside source' in table


def test_geometry_collection_keeps_lines_and_drops_isolated_touch_points():
    from shapely.geometry import GeometryCollection, LineString, Point
    collection = GeometryCollection([LineString([(39, -10), (39, -9)]), Point(38, -13)])
    assert figures._line_parts(collection) == [[(39., -10.), (39., -9.)]]


def test_static_png_export_has_correct_dimensions_without_a_browser():
    import struct
    png = figures.raster_png('<svg xmlns="http://www.w3.org/2000/svg" width="40" height="30"><rect width="40" height="30" fill="blue"/></svg>')
    assert png.startswith(b'\x89PNG\r\n\x1a\n')
    assert struct.unpack('>II', png[16:24]) == (40, 30)
