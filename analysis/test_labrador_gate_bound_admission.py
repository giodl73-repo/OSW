"""Actual arithmetic and lossless, atomic working-query admission."""
import copy
import json
import pytest
from labrador_latitude_gate_bound_v1 import ROOT, BASE, ENTITY, verify_inputs
from labrador_gate_bound_query import append, records
from test_labrador_latitude_gate_bound_v1 import independent_meridian


def test_actual_nine_scenarios_independent_and_scope_complete():
    doc, pins = verify_inputs()
    assert len(pins) == 11
    calc = doc['calculation']
    assert calc['direct_gate_distance_km'] == pytest.approx(independent_meridian(43,60),abs=0.000001)
    for row in calc['scenarios']:
        assert row['geographic_separation_km'] == pytest.approx(independent_meridian(*row['nominal_latitudes_degrees_north']),abs=0.000001)
    assert calc['rounded_conditional_geographic_floor_km'] == 1800
    assert calc['scenario_min_km'] < 1800 < calc['scenario_max_km']
    m = doc['measurement']
    assert m['rank_eligible'] is m['guaranteed_physical_minimum'] is m['whole_current_representative'] is False
    assert all(m[key] is None for key in ['observation_time','uncertainty_km','fixed_layer_bounds_m','endpoint_coordinates_lon_lat','annual_length_range_km','geometry_id'])
    assert doc['whole_current_length_km'] is None and doc['physical_state_join_eligible'] is False
    assert doc['length_assessment']['published_length_km'] is doc['length_assessment']['published_rank'] is None


def fixture():
    rows = json.loads((ROOT / BASE).read_bytes())['length_assessments']
    return {'length_assessments':copy.deepcopy(rows),'measurements':[], 'claims':[], 'sources':[],
            'current_length_bound_admissions':[{'id':'existing-north-atlantic','payload':{'untouched':True}}]}


def test_admission_preserves_other_assessments_existing_nac_and_frozen_export():
    before_bytes = (ROOT / BASE).read_bytes()
    before = fixture(); result = copy.deepcopy(before); doc,_ = verify_inputs()
    append(result,doc)
    assert [r for r in result['length_assessments'] if r['entity_id'] != ENTITY] == [r for r in before['length_assessments'] if r['entity_id'] != ENTITY]
    assert len(result['length_assessments']) == len(before['length_assessments'])
    assert result['current_length_bound_admissions'][0] == before['current_length_bound_admissions'][0]
    assert result['current_length_bound_admissions'][1] == doc
    assert len(result['sources']) == 2
    assert (ROOT / BASE).read_bytes() == before_bytes


@pytest.mark.parametrize('duplicate_collection', ['current_length_bound_admissions','measurements','claims','sources'])
def test_duplicate_admission_rejects_before_any_mutation(duplicate_collection):
    collections = fixture(); doc,_ = verify_inputs()
    row = next(row for name,row in records(doc) if name == duplicate_collection)
    collections[duplicate_collection].append(copy.deepcopy(row)); before = copy.deepcopy(collections)
    with pytest.raises(ValueError,match='Duplicate'):append(collections,doc)
    assert collections == before


def test_prior_assessment_changes_reject_without_partial_admission():
    collections = fixture(); doc,_ = verify_inputs()
    next(r for r in collections['length_assessments'] if r['entity_id'] == ENTITY)['scope'] = 'changed'
    before = copy.deepcopy(collections)
    with pytest.raises(ValueError,match='prior Labrador'):append(collections,doc)
    assert collections == before
