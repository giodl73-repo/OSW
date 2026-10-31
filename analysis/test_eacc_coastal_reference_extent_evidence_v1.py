"""Synthetic frames and tiny profiles only; no original model/map inputs."""
from copy import deepcopy
import hashlib
import xml.etree.ElementTree as ET

import pytest

import eacc_coastal_reference_extent_evidence_v1 as evidence
from eacc_coastal_reference_extent_adapter_v1 import adapt_cases
from coastal_reference_extent_v1 import analyse_cases
from test_eacc_coastal_reference_extent_adapter_v1 import source_fixture,SOURCE


def map_fixture(month=1):
    return (f'<svg xmlns="{evidence.NS}" width="820" height="920" viewBox="0 0 820 920">'
        f'<title>Synthetic map frame{month}</title><desc>No ocean data.</desc>'
        '<rect width="100%" height="100%" fill="white"/>'
        '<defs><clipPath id="map"><rect x="100" y="150" width="480" height="640"/></clipPath>'
        '<pattern id="missing" width="6" height="6" patternUnits="userSpaceOnUse"><path d="M0 6L6 0" stroke="#87949c"/></pattern></defs>'
        '<text x="110" y="180">SYNTHETIC FRAME; no original ocean map</text>'
        '<g clip-path="url(#map)"><rect x="100" y="190" width="40" height="40" fill="url(#missing)"/>'
        '<rect x="200" y="300" width="40" height="40" fill="#123456"/>'
        '<polyline points="110,200 120,210 130,205" fill="none" stroke="#101e27"/></g></svg>').encode()


@pytest.fixture(scope='module')
def cases():
    diagnostic,fields,_=source_fixture()
    adapted=adapt_cases(diagnostic,fields,SOURCE)
    return adapted,analyse_cases(adapted)


def test_hatch_expansion_changes_display_only_and_preserves_context_geometry():
    raw=map_fixture();before=bytes(raw)
    body,count=evidence.explicit_missing_hatching(raw)
    assert count==1 and raw==before
    assert 'fill="url(#missing)"' not in body and '#eef1f3' in body
    assert '#123456' in body and '110,200 120,210 130,205' in body
    parsed=ET.fromstring(f'<svg xmlns="{evidence.NS}">{body}</svg>')
    assert list(parsed.iter(f'{{{evidence.NS}}}line'))
    assert any(node.get('clip-path')=='url(#map)' for node in parsed.iter())


@pytest.mark.parametrize('change',['projection','size','geometry'])
def test_unknown_source_svg_frame_or_cell_geometry_is_refused(change):
    raw=map_fixture()
    if change=='projection':raw=raw.replace(b'0 0 820 920',b'0 0 800 800')
    if change=='size':raw=b' '*(2*1024*1024+1)
    if change=='geometry':raw=raw.replace(b'width="40" height="40" fill="url',b'width="-40" height="40" fill="url')
    with pytest.raises(ValueError):evidence.explicit_missing_hatching(raw)


def test_map_overlay_has_correct_frame_and_retained_seed_marker(cases):
    adapted,report=cases
    a=next(c for c in adapted if c['id']=='m01:offset0:step5')
    c=next(c for c in report['cases'] if c['case_id']==a['id'])
    svg,count=evidence.map_layer_svg(1,map_fixture(),a,c)
    root=ET.fromstring(svg)
    assert root.get('viewBox')=='0 0 1080 1100' and count==1
    assert evidence.project(38,-5)==(100,150) and evidence.project(44,-13)==(580,790)
    peak=next(node for node in root.iter(f'{{{evidence.NS}}}circle') if node.get('fill')=='#164e80')
    assert float(peak.get('cx'))==260 and float(peak.get('cy'))==470
    assert 'translate(0 80)' in svg and 'No whole-current width admitted' in svg


def test_all_months_profiles_outcomes_and_alternatives_are_written(cases,tmp_path):
    adapted,report=cases;before=(deepcopy(adapted),deepcopy(report))
    maps={month:map_fixture(month) for month in range(1,13)}
    manifest={'region_lon_lat':evidence.REGION,'projection':'equirectangular longitude/latitude',
        'files':{f'm{m:02d}-map.svg':{'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()} for m,raw in maps.items()}}
    result=evidence.render_evidence(adapted,report,maps,manifest,tmp_path/'figures')
    assert (adapted,report)==before
    assert result['months']==12 and result['cases']==72 and len(result['files'])==37
    assert result['original_map_inputs_unchanged'] and not result['old_figure_producer_rerun']
    assert not result['current_association_verified'] and result['new_current_measurements_admitted']==0
    assert set(result['display_only_missing_hatch_expansion_count_by_month'].values())=={1}
    page=(tmp_path/'figures/m01.html').read_text(encoding='utf8')
    for case in adapted[:6]:assert case['id'] in page
    for quantity in evidence.QUANTITY_LABELS.values():assert quantity in page
    assert 'Every retained signed-offset' in page and 'Primary map-marker geometry' in page
    assert 'scope="col"' in page and 'scope="row"' in page and 'tabindex="0"' in page
    assert 'outward to 0.1 km' in page and 'not confidence intervals' in page
    assert '<script' not in page and 'animation' in (tmp_path/'figures/index.html').read_text()


def test_tampered_source_map_fingerprint_is_rejected(cases,tmp_path):
    adapted,report=cases
    maps={month:map_fixture(month) for month in range(1,13)}
    manifest={'region_lon_lat':evidence.REGION,'projection':'equirectangular longitude/latitude',
        'files':{f'm{m:02d}-map.svg':{'bytes':len(raw),'sha256':'0'*64} for m,raw in maps.items()}}
    with pytest.raises(ValueError,match='fingerprint'):evidence.render_evidence(adapted,report,maps,manifest,tmp_path/'bad')


def test_display_rounding_encloses_unrounded_brackets():
    assert evidence.span([29.999999,40.000001])=='29.9 to 40.1 km'
    assert evidence.span(None)=='unresolved'


def test_source_text_is_escaped_in_semantic_output(cases):
    adapted,report=deepcopy(cases)
    group=[c for c in adapted if c['month']==1];calculated=[c for c in report['cases'] if c['case_id'].startswith('m01:')]
    calculated[0]['source_status']='<script>alert(1)</script>'
    page=evidence.monthly_html(1,group,calculated)
    assert '<script>' not in page and '&lt;script&gt;' in page
