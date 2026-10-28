"""Clarify equal-length placement scenarios; preserve prior generated drafts."""
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'research/wicc-winter-regional-reference-route-v3-candidate.json'
REPORT = 'research/wicc-winter-regional-reference-route-v4-candidate.json'
FIGURE = 'figures/wicc-winter-regional-reference-route-v4-candidate.svg'


def prepare():
    raw = (ROOT / SOURCE).read_bytes()
    data = json.loads(raw)
    assert max(s['length_km'] for s in data['scenarios']) - min(s['length_km'] for s in data['scenarios']) < .001
    # A uniform longitude translation on an ellipsoid of revolution preserves
    # every segment length. Outward display rounding is not sensitivity.
    data['reported_rounding_enclosure_km'] = data.pop('reported_scenario_range_km')
    data['reported_scenario_range_km'] = None
    data['scenario_length_interpretation'] = 'All three placements are uniform longitude translations and have equal geodesic length. The 1500-1600 km outward rounding enclosure is not a sensitivity range, uncertainty or seasonal envelope.'
    data['route_placement_sensitivity_established'] = False
    data['length_uncertainty_km'] = None
    data['annual_length_range_km'] = None
    data['previous_prepared_report'] = SOURCE
    data['previous_prepared_report_sha256'] = hashlib.sha256(raw).hexdigest()
    data['presentation_postprocessor_file'] = 'analysis/prepare_wicc_winter_reference_route_v4.py'
    data['presentation_postprocessor_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    svg = ET.parse(ROOT / data['figure'])
    texts = [e for e in svg.getroot().iter() if e.tag.endswith('}text')]
    label = next(e for e in texts if e.text and 'scenario range' in e.text)
    label.text = 'Approx. 1,500 km; three translated placements share this length'
    caution = next(e for e in texts if e.text == 'Not an observed axis or statistical confidence interval')
    caution.text = 'No observed axis, endpoint uncertainty or seasonal range'
    data['figure'] = FIGURE
    assert not (ROOT / REPORT).exists() and not (ROOT / FIGURE).exists()
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    svg.write(ROOT / FIGURE, encoding='utf-8', xml_declaration=True)
    (ROOT / REPORT).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    import pymupdf
    document = pymupdf.open(ROOT / FIGURE)
    document[0].get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5)).save(ROOT / '.pytest_cache/wicc-route-review-v1/candidate-v4.png')
    return data


if __name__ == '__main__':
    data = prepare()
    print(json.dumps({'nominal_reference_path_km': data['nominal_reference_path_km'],
                      'reported_scenario_range_km': data['reported_scenario_range_km'],
                      'length_uncertainty_km': data['length_uncertainty_km']}))
