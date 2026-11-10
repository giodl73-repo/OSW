"""Small admission fixtures; no packet loads, native builds or browser sessions."""
import copy
import json

import pytest
import baffin_bound_admission as a


def fixture(doc):
    return {
        'entities': [copy.deepcopy(doc['accepted_entity']), {'id':'current:other'}],
        'length_assessments': [copy.deepcopy(doc['prior_length_assessment']),
                               {'id':'length_assessment:other','entity_id':'current:other','published_rank':1}],
        'measurements': [{'id':'old:measurement','entity_id':'current:other'}],
        'claims': [{'id':'old:claim','subject_id':'current:other'}],
        'sources': [{'id':'source:existing'}],
        'widths': [{'id':'baffin:width:one','current_id':'baffin','approximate_width_km':25},
                   {'id':'baffin:width:two','current_id':'baffin','width_range_km':[10,30]}],
        'width_samples': [], 'geometries': [{'id':'old:route'}],
        'objects': [{'id':'current:baffin','latest_observation_date':'1979-08-01',
                     'capabilities':{'reported_length':0,'scoped_width':2}}],
    }


@pytest.fixture(scope='module')
def contract():
    document = json.loads(a.read(a.FILE))
    assert a.encoded(document) == a.encoded(a.build_contract())
    return document


def test_frozen_report_values_do_not_become_physical_or_seasonal_lengths(contract):
    row = contract['measurement']
    assert row['value'] == 1000
    assert row['direct_gate_distance_km'] == 1004.206947
    for key in ['rank_eligible','guaranteed_physical_minimum','whole_current_representative','historical_release_admitted']:
        assert row[key] is False
    for key in ['observation_time','uncertainty_km','fixed_layer_bounds_m','endpoint_coordinates_lon_lat',
                'annual_length_range_km','geometry_id']:
        assert row[key] is None
    assert contract['admission']['study_years'] == [1978,1979]
    assert 'extends' in contract['admission']['naming_scope']
    assert contract['claim']['review_fingerprint'] == a.review_fingerprint(contract['claim'])
    assert contract['working_delivery_verified'] is False


def test_all_nine_scenarios_are_separately_queryable_editorial_cases(contract):
    rows = contract['scenario_records']
    assert [r['scenario_index'] for r in rows] == list(range(1,10))
    assert len({r['id'] for r in rows}) == 9
    assert len({(r['start_shift_degrees'],r['end_shift_degrees']) for r in rows}) == 9
    for row in rows:
        assert row['entity_id'] == a.ENTITY and row['measurement_id'] == a.MEASUREMENT
        assert row['scenario_kind'] == 'editorial_latitude_sensitivity'
        assert row['is_observation'] is row['annual_extrema_eligible'] is row['seasonal_playback_eligible'] is False
        assert row['observation_time'] is None


def test_atomic_record_preparation_preserves_all_prior_other_rows(contract):
    parent = fixture(contract)
    original = copy.deepcopy(parent)
    staged, receipt = a.prepare_records(parent, contract)
    assert parent == original
    for name, rows in original.items():
        if name == 'length_assessments':
            assert staged[name][0] == contract['length_assessment']
            assert staged[name][1:] == rows[1:]
        else:
            assert staged[name][:len(rows)] == rows
    assert sum(len(staged.get(name,[]))-len(parent.get(name,[])) for name in staged) == 14
    assert receipt['owner_projection_verified'] is receipt['working_delivery_verified'] is False
    assert receipt['physical_samples_added'] == 0
    assert staged['objects'] == original['objects']
    for key in ['published_rank','published_length_km','illustration_source_id','illustration_ledger_source_id']:
        assert staged['length_assessments'][0][key] == original['length_assessments'][0][key]


@pytest.mark.parametrize('collection', ['measurements','claims','sources','current_length_bound_admissions','current_length_bound_scenarios'])
def test_record_collisions_reject_without_mutating_parent(contract, collection):
    parent = fixture(contract)
    row = next(row for name, row in a.records(contract) if name == collection)
    parent.setdefault(collection,[]).append(copy.deepcopy(row))
    before = copy.deepcopy(parent)
    with pytest.raises(ValueError, match='identity collision'):
        a.prepare_records(parent, contract)
    assert parent == before


@pytest.mark.parametrize('change', ['assessment','duplicate-assessment','entity','missing','shape','duplicate-source'])
def test_changed_or_incomplete_parent_rejects_atomically(contract, change):
    parent = fixture(contract)
    if change == 'assessment': parent['length_assessments'][0]['scope'] = 'changed'
    if change == 'duplicate-assessment': parent['length_assessments'].append(copy.deepcopy(parent['length_assessments'][0]))
    if change == 'entity': parent['entities'][0]['type'] = 'unresolved'
    if change == 'missing': del parent['length_assessments']
    if change == 'shape': parent['geometries'] = 'not rows'
    if change == 'duplicate-source': parent['sources'].append(copy.deepcopy(parent['sources'][0]))
    before = copy.deepcopy(parent)
    with pytest.raises(ValueError): a.prepare_records(parent, contract)
    assert parent == before


@pytest.mark.parametrize('section,key,value', [
    ('measurement','value',1100), ('measurement','rank_eligible',True),
    ('measurement','annual_length_range_km',[893,1116]),
    ('measurement','source_id','source:other'), ('measurement','entity_id','current:other'),
    ('admission','study_season','winter'), ('claim','observation_time','1979-08-01')])
def test_contract_changes_reject(contract, section, key, value):
    changed = copy.deepcopy(contract)
    changed[section][key] = value
    parent = fixture(contract)
    before = copy.deepcopy(parent)
    with pytest.raises(ValueError, match='unverified Baffin admission contract'):
        a.prepare_records(parent, changed)
    assert parent == before


def test_query_links_include_the_nine_scenarios_without_provider_requests(contract):
    from urllib.parse import unquote
    links = contract['card_links']
    scenarios = next(r for r in links if 'nine' in r['label'])
    query = json.loads(unquote(scenarios['url'].split('?q=')[1]))
    assert query['collection'] == 'current_length_bound_scenarios'
    assert query['limit'] == 9
    assert query['filters'][0]['value'] == a.ENTITY
    assert all(not r['url'].startswith('http') for r in links)
