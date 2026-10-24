"""Prospective synthetic-gate tests; never execute the Baffin source-gate pair."""
import copy
import json
import xml.etree.ElementTree as ET

import pytest
import baffin_latitude_gate_bound_v1 as m


@pytest.mark.parametrize('a,b', [(5, 8), (-55, -50), (-2, 2), (81, 85)])
def test_independent_arithmetic_and_all_editorial_scenarios(a, b):
    calc = m.calculate_gates(a, b)
    m.verify_arithmetic(calc)
    assert calc['direct_gate_distance_km'] == pytest.approx(m.independent_meridian(a, b), abs=0.000001)
    assert calc['scenario_count'] == len(calc['scenarios']) == 9
    assert calc['rounded_conditional_geographic_floor_km'] % 100 == 0
    assert calc['rounded_conditional_geographic_floor_km'] <= calc['direct_gate_distance_km']
    assert calc['direct_gate_distance_km'] < calc['rounded_conditional_geographic_floor_km'] + 100


@pytest.mark.parametrize('a,b', [(True,8),(5,float('nan')),(5,float('inf')),
                                  (8,5),(5,5),(5,6),(-90,-80),(80,90)])
def test_invalid_or_crossing_scenarios_reject(a, b):
    with pytest.raises(ValueError):
        m.calculate_gates(a, b)


@pytest.mark.parametrize('mutation', ['distance', 'floor', 'minimum', 'missing', 'duplicate', 'shift'])
def test_changed_arithmetic_or_scenarios_reject(mutation):
    calc = m.calculate_gates(5, 8)
    if mutation == 'distance': calc['scenarios'][0]['geographic_separation_km'] += 1
    if mutation == 'floor': calc['rounded_conditional_geographic_floor_km'] += 100
    if mutation == 'minimum': calc['scenario_min_km'] += 1
    if mutation == 'missing': calc['scenarios'].pop()
    if mutation == 'duplicate': calc['scenarios'][0] = copy.deepcopy(calc['scenarios'][1])
    if mutation == 'shift': calc['scenarios'][0]['nominal_latitudes_degrees_north'][0] += 1
    with pytest.raises(ValueError):
        m.verify_arithmetic(calc)


def test_selected_original_source_scope():
    facts = json.loads((m.ROOT / m.FACTS).read_bytes())
    assert m.source_facts(facts) == facts
    assert 'extends' in facts['naming_scope']
    assert facts['source_reported_length_km'] is None
    assert facts['working_dataset_admitted'] is False


@pytest.mark.parametrize('key,value', [
    ('current_id','other'), ('source_doi','other'),
    ('reported_regional_latitudes_degrees_north',[76,67]),
    ('original_sha256','0'*64), ('original_bytes',1),
    ('selected_pdf_pages_visually_reviewed_for_this_question',[1,2]),
    ('source_reported_length_km',1000), ('exact_gate_occupation_dates',['1978-08-01']),
    ('rank_eligible',True), ('working_dataset_admitted',True),
    ('new_numeric_calculation_performed',True), ('original_redistributed',True)])
def test_changed_source_support_rejects(key, value):
    facts = json.loads((m.ROOT / m.FACTS).read_bytes())
    facts[key] = value
    with pytest.raises(ValueError):
        m.source_facts(facts)


def test_scalar_figure_limits_and_accessibility_with_synthetic_gates():
    root = ET.fromstring(m.figure(m.calculate_gates(5, 8)))
    assert root.get('role') == 'img'
    assert root.get('aria-labelledby') == 'title desc'
    text = ' '.join(root.itertext())
    for phrase in ['Not a mapped current route or whole-current length',
                   'not physical uncertainty or seasonal variability',
                   'Southern latitude: 5°N', 'Northern latitude: 8°N',
                   'author extends the name north', 'exact gate dates',
                   'guaranteed physical minimum']:
        assert phrase in text


def test_unfrozen_actual_source_execution_rejects_before_calculation(monkeypatch):
    def forbidden(*args):
        pytest.fail('Actual gate calculation occurred before the freeze check')
    monkeypatch.setattr(m, 'calculate_gates', forbidden)
    with pytest.raises(ValueError, match='pre-execution Git commit'):
        m.build('not-a-commit')


def test_frozen_input_check_rejects_changed_preflight_without_calculation(tmp_path, monkeypatch):
    monkeypatch.setattr(m, 'ROOT', tmp_path)
    monkeypatch.setattr(m.subprocess, 'run', lambda *a, **k: None)
    path = tmp_path / m.PREFLIGHT
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({'schema':'osw.baffin-latitude-bound-preflight.v1',
                               'phase':'prospective_declaration',
                               'actual_baffin_gate_distance_calculated':True}))
    with pytest.raises(ValueError, match='Changed prospective inputs'):
        m.inspect_frozen_inputs('a' * 40)


def test_git_freeze_rejects_different_committed_bytes(tmp_path, monkeypatch):
    from types import SimpleNamespace
    monkeypatch.setattr(m, 'ROOT', tmp_path)
    monkeypatch.setattr(m, 'INPUTS', ['tiny.txt'])
    (tmp_path / 'tiny.txt').write_text('working')
    path = tmp_path / m.PREFLIGHT
    path.parent.mkdir(parents=True)
    path.write_bytes(m.encoded({'schema':'osw.baffin-latitude-bound-preflight.v1',
                               'phase':'prospective_declaration',
                               'actual_baffin_gate_distance_calculated':False,
                               'input_sha256':m.input_pins()}))
    monkeypatch.setattr(m.subprocess, 'run', lambda *a, **k: SimpleNamespace(stdout=b'committed'))
    with pytest.raises(ValueError, match='differs from pre-execution freeze'):
        m.inspect_frozen_inputs('a' * 40)


def test_different_original_rejects_without_network(tmp_path):
    path = tmp_path / 'different.pdf'
    path.write_bytes(b'different original')
    with pytest.raises(ValueError, match='Changed institutional original'):
        m.verify_original(path)
