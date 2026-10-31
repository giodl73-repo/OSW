"""Correct South Java map framing; preserve every verified geometry attribute."""
import copy
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = 'research/south-java-reference-presentation-history-v1/coarse-map-executed-v1.svg.source'
CANDIDATE = 'research/south-java-java-bali-reference-path-v1-candidate.json'
DETAILED = 'figures/south-java-java-bali-reference-path-v2-candidate.svg'
COMPACT = 'figures/south-java-java-bali-reference-compact-v1.svg'
SHA = '53da64165d87bef63b59dae68d6efb485a75bb52f01620b432e915a2abbe09dc'
NS = '{http://www.w3.org/2000/svg}'
ET.register_namespace('', NS[1:-1])


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def geometry(root):
    return [(node.tag, dict(node.attrib)) for node in root.iter()
            if node.tag in [NS + name for name in ['path', 'polyline', 'circle']]]


def detailed(raw):
    assert digest(raw) == SHA, 'Wrong executed map source'
    original = ET.fromstring(raw)
    root = copy.deepcopy(original)
    assert root.get('viewBox') == '1164 365 65 65'
    root.set('viewBox', '1224 455 65 65')
    rectangles = list(root.iter(NS + 'rect'))
    assert len(rectangles) == 1 and rectangles[0].get('x') == '1164' and rectangles[0].get('y') == '365'
    rectangles[0].set('x', '1224')
    rectangles[0].set('y', '455')
    texts = list(root.iter(NS + 'text'))
    assert len(texts) == 8 and texts[0].text == '105E gate' and texts[1].text == '115E gate'
    circles = list(root.iter(NS + 'circle'))
    assert len(circles) == 2
    for i, (node, circle) in enumerate(zip(texts[:2], circles)):
        node.set('x', str(float(circle.get('cx')) + (0.8 if i == 0 else -0.8)))
        node.set('y', str(float(circle.get('cy')) + (-1 if i == 0 else 2)))
        node.set('text-anchor', 'start' if i == 0 else 'end')
        label_box = ET.Element(NS + 'rect', {
            'x': str(float(node.get('x')) - (0.3 if i == 0 else 6.4)),
            'y': str(float(node.get('y')) - 1.3), 'width': '7', 'height': '1.8',
            'fill': '#e7f2f7'})
        root.insert(list(root).index(node), label_box)
    for node in texts[2:]:
        node.set('x', str(float(node.get('x')) + 60))
        node.set('y', str(float(node.get('y')) + 90))
    panel = ET.Element(NS + 'rect', {'x': '1227', 'y': '460', 'width': '50', 'height': '16',
                                    'fill': '#e7f2f7', 'fill-opacity': '.96'})
    root.insert(list(root).index(texts[2]), panel)
    assert geometry(root) == geometry(original)
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)


def compact(raw):
    source = ET.fromstring(detailed(raw))
    root = ET.Element(NS + 'svg', {'viewBox': '0 0 390 245', 'width': '780', 'height': '490',
        'role': 'img', 'aria-labelledby': 'title description'})
    ET.SubElement(root, NS + 'title', {'id': 'title'}).text = 'South Java editorial reference reach'
    ET.SubElement(root, NS + 'desc', {'id': 'description'}).text = (
        'The same27 verified drawings and coast vectors, cropped for compact display. '
        '105E and115E are editorial gates. About1100km is a reference distance, not a measured current length.')
    ET.SubElement(root, NS + 'rect', {'width': '390', 'height': '245', 'rx': '4', 'fill': '#e7f2f7'})
    def label(x, y, value, size, weight=None, anchor='start'):
        attrs = {'x': str(x), 'y': str(y), 'font-family': 'sans-serif', 'font-size': str(size),
                 'fill': '#153d4d', 'text-anchor': anchor}
        if weight:
            attrs['font-weight'] = weight
        ET.SubElement(root, NS + 'text', attrs).text = value
    defs = ET.SubElement(root, NS + 'defs')
    clip = ET.SubElement(defs, NS + 'clipPath', {'id': 'world-clip', 'clipPathUnits': 'userSpaceOnUse'})
    ET.SubElement(clip, NS + 'rect', {'x': '10', 'y': '60', 'width': '370', 'height': '133.2'})
    clipped = ET.SubElement(root, NS + 'g', {'clip-path': 'url(#world-clip)'})
    world = ET.SubElement(clipped, NS + 'g', {'transform': 'translate(10 60) scale(7.4) translate(-1227 -481)'})
    for node in source:
        if node.tag in [NS + name for name in ['path', 'polyline', 'circle']]:
            world.append(copy.deepcopy(node))
    # Paint heading/footer after the map for SVG readers that ignore clipPath.
    ET.SubElement(root, NS + 'rect', {'width': '390', 'height': '60', 'fill': '#e7f2f7'})
    ET.SubElement(root, NS + 'rect', {'y': '193.2', 'width': '390', 'height': '51.8', 'fill': '#e7f2f7'})
    label(12, 27, 'South Java reference reach', 21, '700')
    label(12, 49, 'Java-Bali context · 27 drawings', 15)
    label(45, 209, '105°E gate', 15, '700', 'middle')
    label(349, 209, '115°E gate', 15, '700', 'middle')
    label(12, 236, '≈ 1,100 km · editorial reach', 19)
    assert geometry(root) == geometry(source)
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)


def main():
    raw = (ROOT / ARCHIVE).read_bytes()
    source = json.loads((ROOT / CANDIDATE).read_bytes())
    preflight = json.loads((ROOT / 'research/south-java-reference-cloud-preflight-v1.json').read_bytes())
    path = 'analysis/build_cartographic_current_state_join.py'
    assert digest((ROOT / path).read_bytes()) == preflight['input_sha256'][path]
    assert source['scenario_count'] == 27 and source['nominal_reference_path_km'] == 1127.329
    outputs = {DETAILED: detailed(raw), COMPACT: compact(raw)}
    for path, content in outputs.items():
        (ROOT / path).write_bytes(content)
    revised = copy.deepcopy(source)
    revised.update(figure=DETAILED, map_view_box=[1224, 455, 65, 65],
        presentation_revision={'role': 'viewport_and_compact_rendering_only', 'source_candidate': CANDIDATE,
            'source_candidate_sha256': digest((ROOT / CANDIDATE).read_bytes()),
            'executed_svg_archive': ARCHIVE, 'executed_svg_sha256': SHA,
            'geometry_attributes_unchanged': True, 'compact_figure': COMPACT,
            'output_sha256': {p: digest(r) for p, r in outputs.items()}})
    assert revised['scenarios'] == source['scenarios']
    path = ROOT / 'research/south-java-java-bali-reference-path-v2-candidate.json'
    path.write_bytes((json.dumps(revised, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode())
    print('Reframed maps preserve all28 route polylines, both gate circles and the exact coastline path.')


if __name__ == '__main__':
    main()
