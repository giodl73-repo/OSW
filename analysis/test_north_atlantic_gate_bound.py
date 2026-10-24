"""Independent meridional arithmetic and honest working-admission scope."""
import copy
import json
import math
import xml.etree.ElementTree as ET

import pytest
from north_atlantic_gate_bound import ROOT, BASE, ENTITY, build, calculation, append, verify_inputs


def meridional_integral(a, b):
    # Composite Simpson integration of WGS84 meridional curvature, independent
    # of PROJ's inverse-geodesic implementation.
    eccentricity_squared = 0.0066943799901413165
    n = 10000
    lo, hi = math.radians(a), math.radians(b)
    h = (hi - lo) / n
    def radius(phi):
        return 6378137 * (1 - eccentricity_squared) / (1 - eccentricity_squared * math.sin(phi)**2)**1.5
    total = radius(lo) + radius(hi)
    total += sum((4 if i % 2 else 2) * radius(lo + i * h) for i in range(1, n))
    return total * h / 3 / 1000


def test_original_and_independent_nine_scenarios():
    doc, pins = verify_inputs()
    assert len(pins) >= 9
    calc = doc['calculation']
    assert calc['direct_gate_distance_km'] == pytest.approx(meridional_integral(47, 58), abs=0.000001)
    assert calc['rounded_conditional_geographic_floor_km'] == 1200
    assert len(calc['scenarios']) == len({(s['start_shift_degrees'], s['end_shift_degrees']) for s in calc['scenarios']}) == 9
    for scenario in calc['scenarios']:
        assert scenario['geographic_separation_km'] == pytest.approx(meridional_integral(*scenario['nominal_latitudes_degrees_north']), abs=0.000001)
    assert calc['scenario_min_km'] < 1200 < calc['scenario_max_km']


def test_floor_is_conditional_and_never_a_whole_length():
    doc = build()
    row = doc['length_assessment']
    assert row['evidence_status'] == 'derived_lower_bound'
    assert row['published_length_km'] is row['published_rank'] is None
    assert row['rank_eligible'] is False
    m = doc['measurement']
    assert m['guaranteed_physical_minimum'] is m['whole_current_representative'] is False
    for key in ['observation_time', 'uncertainty_km', 'fixed_layer_bounds_m', 'endpoint_coordinates_lon_lat', 'annual_length_range_km']:
        assert m[key] is None
    assert 'nominal' in row['scope'] and '53°N' in row['scope']
    assert doc['physical_state_join_eligible'] is False


def test_working_admission_preserves_other_assessments_and_frozen_source():
    path = ROOT / (BASE + 'length_assessments.json')
    before = path.read_bytes()
    rows = json.loads(before)
    collections = {'length_assessments': copy.deepcopy(rows), 'sources': [], 'claims': [], 'measurements': []}
    append(collections, build())
    assert [r for r in collections['length_assessments'] if r['entity_id'] != ENTITY] == [r for r in rows if r['entity_id'] != ENTITY]
    assert len(collections['length_assessments']) == len(rows)
    assert path.read_bytes() == before
    with pytest.raises(ValueError, match='prior-assessment'):
        append(collections, build())


def test_scalar_figure_accessible_and_not_a_route():
    doc, _ = verify_inputs()
    root = ET.parse(ROOT / doc['figure_file']).getroot()
    assert root.attrib['role'] == 'img'
    assert root.attrib['aria-labelledby'] == 'title desc'
    text = ''.join(root.itertext())
    for phrase in ['conditional', 'unranked', 'not measured uncertainty', 'Section positions, layers and cruises differ']:
        assert phrase in text
    assert not root.findall('.//{http://www.w3.org/2000/svg}polyline')


@pytest.mark.parametrize('a,b', [(58, 47), (-91, 58), (47, 91), (47, 47)])
def test_rejects_invalid_gate_latitudes(a, b):
    with pytest.raises(ValueError):
        calculation(a, b)
