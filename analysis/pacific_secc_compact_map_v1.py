"""Exact-vector mobile crop and a presentation-only verified-engine overlay."""
import argparse
import copy
import json
import re
import xml.etree.ElementTree as ET

import pacific_secc_reference_delivery_v2 as presentation
import pacific_secc_publication_admission_v1 as admission

ROOT = admission.ROOT
MODULE = 'analysis/pacific_secc_compact_map_v1.py'
PROTOCOL = 'plans/pacific-secc-compact-map-presentation-v1.md'
FIGURE = 'figures/pacific-secc-western-reference-compact-v1.svg'
SOURCE = admission.query.FIGURE
SOURCE_SHA = 'b1813b4dcbe4e245e007f5139495a71a7b778800103a491b8ab71da7cf5d254e'
PAGE = admission.query.PAGE
UI = 'almanac/reference-routes.js'
UI_ARCHIVE = 'research/pacific-secc-reference-presentation-history-v1/reference-routes-executed-v1.js.source'
UI_SHA = '4249b2a86cb1e272d67681ad7f4356fe90b8926a91cf9b80f3adec25c9669035'
BASE_PAGE_SHA = '115fcab970ba2e144432ea3484efc0985bfa4f1514cdfc0a3e51b39cc948d3fc'
BASE_ENGINE_SHA = 'a3e26e385d44d8c06606e49e478b5c041fcaf7f5e1728538e281e0ebc283aa2b'
LOGICAL = 'f0e046651b75c84da488c4e81204e410b18f37256e102c26a0ab2f70b5f69184'
WASM_SHA = '569b082b354b1e376ad07bcf644a4c6e0cfc27982acaafc334396f02a3940318'
KEY = 'pacific_secc_compact_map_presentation_v1'
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)


def tag(name): return '{' + NS + '}' + name
def sha(raw): return admission.runtime.sha(raw)


def compact_svg():
    raw = (ROOT / SOURCE).read_bytes()
    if sha(raw) != SOURCE_SHA: raise ValueError('Exact reviewed detailed map required')
    source = ET.fromstring(raw)
    kinds = ['path', 'polyline', 'circle', 'line']
    shapes = [child for child in source if child.tag in {tag(k) for k in kinds}]
    if {k: sum(child.tag == tag(k) for child in shapes) for k in kinds} != {'path': 3, 'polyline': 28, 'circle': 2, 'line': 1}:
        raise ValueError('Exact retained land/scenario/nominal/end-gate/dateline inventory required')
    root = ET.Element(tag('svg'), {'viewBox': '0 0 320 190', 'width': '320', 'height': '190',
        'role': 'img', 'aria-labelledby': 'title description'})
    ET.SubElement(root, tag('title'), {'id': 'title'}).text = 'Pacific SECC western editorial reference: approximately 1,800 km'
    ET.SubElement(root, tag('desc'), {'id': 'description'}).text = ('Same retained map vectors, cropped for phones. '
        'Reference longitude gates164E and180E;27 editorial drawings. No observed axis, seasonal range or whole-current length.')
    ET.SubElement(root, tag('rect'), {'width': '320', 'height': '190', 'rx': '4', 'fill': '#e7f2f7'})
    font = {'font-family': 'system-ui,sans-serif', 'fill': '#123c4b'}
    ET.SubElement(root, tag('text'), {**font, 'x': '12', 'y': '23', 'font-size': '18', 'font-weight': '700'}).text = 'Western Pacific SECC'
    ET.SubElement(root, tag('text'), {**font, 'x': '12', 'y': '42', 'font-size': '13'}).text = 'Reference gates · 27 drawings'
    viewport = ET.SubElement(root, tag('svg'), {'x': '10', 'y': '48', 'width': '300', 'height': '105',
        'viewBox': '1440 486 110 38.5', 'overflow': 'hidden', 'preserveAspectRatio': 'xMidYMid meet'})
    for child in shapes: viewport.append(copy.deepcopy(child))
    # Label positions follow the saved endpoint-circle x coordinates; geometry is untouched.
    circles = [child for child in source if child.tag == tag('circle')]
    for child, label in zip(circles, ['164°E', '180°E']):
        x = 10 + (float(child.attrib['cx']) - 1440) * 300 / 110
        ET.SubElement(root, tag('text'), {**font, 'x': f'{x:.3f}', 'y': '145',
            'text-anchor': 'middle', 'font-size': '16', 'font-weight': '700'}).text = label
    ET.SubElement(root, tag('text'), {**font, 'x': '12', 'y': '177', 'font-size': '16'}).text = '≈ 1,800 km · editorial reach'
    return ET.tostring(root, encoding='utf-8', xml_declaration=True) + b'\n'


def support_page():
    raw = presentation.support_page()
    if sha(raw) != BASE_PAGE_SHA: raise ValueError('Exact passed full-delivery support page required')
    text = raw.decode()
    pattern = r'(<a href="\.\./' + re.escape(SOURCE) + r'">)(<img\b[\s\S]*?>)(</a>)'
    def replace(match):
        return (match[1] + '<picture><source media="(max-width:480px)" srcset="../' + FIGURE + '">'
                + match[2] + '</picture>' + match[3])
    text, count = re.subn(pattern, replace, text)
    if count != 1: raise ValueError('Exactly one map image anchor must gain responsive picture/source markup')
    return text.encode()


def atlas_ui():
    raw = (ROOT / UI_ARCHIVE).read_bytes()
    if sha(raw) != UI_SHA: raise ValueError('Exact reviewed atlas UI source required')
    text = raw.decode()
    marker = "      if(report.rendering_role==='derived_inline_source_reference_card_not_additional_observation')node('p','The comparison figure"
    if text.count(marker) != 1: raise ValueError('Unique route-card image insertion point required')
    added = ("      if(row.figure==='" + SOURCE + "'){\n"
             "        const responsive=document.createElement('picture'),mobile=document.createElement('source');\n"
             "        mobile.media='(max-width:480px)';mobile.srcset='../" + FIGURE + "';\n"
             "        image.replaceWith(responsive);responsive.append(mobile,image);\n"
             "      }\n")
    return text.replace(marker, added + marker).encode()


def overlay(parent, *, parent_manifest_sha, control_commit):
    if (parent_manifest_sha != BASE_ENGINE_SHA or KEY in parent
            or not re.fullmatch('[0-9a-f]{40}', control_commit)
            or parent['sha256'].get(PAGE) != BASE_PAGE_SHA
            or parent['sha256'].get(UI) != UI_SHA
            or parent['sha256'].get('almanac/query-engine.wasm') != WASM_SHA
            or parent['pacific_secc_reference_engine_delivery_v1']['logical_sha256'] != LOGICAL
            or not isinstance(parent.get('eacc_regional_connection_presentation_v4'), dict)):
        raise ValueError('Exact passed full candidate and fresh presentation overlay required')
    outputs = {PAGE: support_page(), UI: atlas_ui(), FIGURE: compact_svg(), MODULE: (ROOT / MODULE).read_bytes(),
               PROTOCOL: (ROOT / PROTOCOL).read_bytes()}
    if any(path in parent['sha256'] for path in [FIGURE, MODULE, PROTOCOL]):
        raise ValueError('Presentation additions already exist in the parent engine')
    result = copy.deepcopy(parent)
    result['sha256'].update({path: sha(raw) for path, raw in outputs.items()})
    result[KEY] = {'parent_candidate_engine_manifest_sha256': parent_manifest_sha,
        'control_commit': control_commit, 'changed_paths': [PAGE, UI], 'added_paths': [FIGURE, MODULE, PROTOCOL],
        'detailed_map_source_sha256': SOURCE_SHA, 'logical_sha256': LOGICAL, 'wasm_sha256': WASM_SHA,
        'native_wasm_rebuilt': False, 'new_scientific_records': 0}
    if any(result[key] != value for key, value in parent.items() if key != 'sha256'):
        raise ValueError('Parent engine metadata changed')
    if any(result['sha256'][path] != value for path, value in parent['sha256'].items() if path not in {PAGE, UI}):
        raise ValueError('Unrelated parent engine pin changed')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'check'])
    args = parser.parse_args()
    raw = compact_svg()
    if args.action == 'build': (ROOT / FIGURE).write_bytes(raw)
    elif (ROOT / FIGURE).read_bytes() != raw: raise ValueError('Saved compact map differs')
    print(json.dumps({'status': 'PASS', 'new_scientific_records': 0, 'svg_sha256': sha(raw),
                      'support_page_sha256': sha(support_page())}))
