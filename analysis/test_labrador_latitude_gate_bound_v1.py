"""Prospective arithmetic/source tests using synthetic gates only."""
import copy
import json
import math
import xml.etree.ElementTree as ET

import pytest
from labrador_latitude_gate_bound_v1 import (
    ROOT, FACTS, calculate_gates, source_facts, figure,
)


def independent_meridian(a, b):
    eccentricity_squared = 0.0066943799901413165
    lo, hi = math.radians(a), math.radians(b)
    n = 2000
    h = (hi - lo) / n
    def radius(phi):
        return 6378137 * (1 - eccentricity_squared) / (1 - eccentricity_squared * math.sin(phi)**2)**1.5
    total = radius(lo) + radius(hi)
    total += sum((4 if i % 2 else 2) * radius(lo + i * h) for i in range(1, n))
    return total * h / 3 / 1000


@pytest.mark.parametrize('a,b', [(5,8),(-55,-50),(-2,2)])
def test_synthetic_nine_scenarios_and_independent_wgs84_arithmetic(a, b):
    calc = calculate_gates(a, b)
    assert calc['direct_gate_distance_km'] == pytest.approx(independent_meridian(a,b),abs=0.000001)
    assert calc['scenario_count'] == len(calc['scenarios']) == 9
    assert len({(r['start_shift_degrees'],r['end_shift_degrees']) for r in calc['scenarios']}) == 9
    for row in calc['scenarios']:
        x,y = row['nominal_latitudes_degrees_north']
        assert row['geographic_separation_km'] == pytest.approx(independent_meridian(x,y),abs=0.000001)
    floor = calc['rounded_conditional_geographic_floor_km']
    assert floor % 100 == 0
    assert floor <= calc['direct_gate_distance_km'] < floor + 100
    distances = [r['geographic_separation_km'] for r in calc['scenarios']]
    assert calc['scenario_min_km'] == min(distances)
    assert calc['scenario_max_km'] == max(distances)


@pytest.mark.parametrize('a,b', [(True,8),(5,float('nan')),(5,float('inf')),
                                  (8,5),(5,5),(5,6),(-90,-80),(80,90)])
def test_invalid_or_crossing_synthetic_scenarios_reject(a,b):
    with pytest.raises(ValueError):calculate_gates(a,b)


def test_selected_original_facts_and_no_numeric_admission():
    facts = json.loads((ROOT/FACTS).read_bytes())
    assert source_facts(facts) == facts
    assert facts['new_along_current_length_km'] is None
    assert facts['new_geographic_bound_km'] is None
    assert facts['new_width_measurement_admitted'] is False
    assert facts['full_article_review_claimed'] is False


@pytest.mark.parametrize('key,value', [
    ('current_id','other'),('source_doi','other'),
    ('reported_regional_latitudes_degrees_north',[60,43]),
    ('original_sha256','0'*64),('original_bytes',1),
    ('selected_pdf_pages_visually_reviewed',[1,2]),
    ('original_redistributed',True),('new_numeric_calculation_performed',True)])
def test_changed_source_facts_reject(key,value):
    facts = copy.deepcopy(json.loads((ROOT/FACTS).read_bytes()))
    facts[key] = value
    with pytest.raises(ValueError):source_facts(facts)


def test_scalar_figure_describes_its_limits_with_synthetic_numbers():
    raw = figure(calculate_gates(5,8))
    root = ET.fromstring(raw)
    assert root.get('role') == 'img'
    text = ' '.join(root.itertext())
    assert 'Not a mapped current route or whole-current length' in text
    assert 'not physical uncertainty or seasonal variability' in text
    assert 'Southern gate 5°N' in text and 'Northern gate 8°N' in text
    assert 'guaranteed physical minimum' in text
