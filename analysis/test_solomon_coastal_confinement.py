"""Reject measured-width, temporal and source-identity promotions."""
import copy,hashlib,json,subprocess
import pytest
from check_solomon_coastal_confinement import ROOT,validate_row
from check_current_width_inventory import validate
from test_rust_query_browser import CLI

OWNERS={'solomon-island-coastal-undercurrent','new-ireland-coastal-undercurrent'}
def records():
    return [r for r in json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())['measurements'] if r['current_id'] in OWNERS]

def test_distinct_model_and_cited_observation_support():
    rows=records();assert len(rows)==2
    assert [r['reported_width_constraint']['reference_scale_km'] for r in rows]==[100,40]
    assert [r['source_evidence_kind'] for r in rows]==['model_coastal_confinement','cited_observational_coastal_confinement']
    for i,row in enumerate(rows):
        validate_row(row)
        assert row['original_regional_context']['audit_pointer']==f'/measurements/{i}'
        assert row['approximate_width_km'] is None and row['width_range_km'] is None
        assert row['original_regional_context']['model_context']['is_observation_period'] is False

@pytest.mark.parametrize('key,value',[
    ('approximate_width_km',40),('width_range_km',[0,100]),('width_range_km',[40,100]),
    ('fixed_layer_bounds_m',[100,400]),('fixed_layer_bounds_m',[200,235]),
    ('calendar_months',[6,7,8]),('observed_period',{'start':'1986-01-01','end':'2004-12-31'}),
    ('uncertainty_km',9),('seasonal_playback_eligible',True),('annual_extrema_eligible',True),
    ('full_width_inference_eligible',True),('width_rank_eligible',True),
    ('original_regional_context',{}),('current_id','new-guinea-coastal-undercurrent')])
def test_scope_promotions_rejected(key,value):
    for row in records():
        bad=copy.deepcopy(row);bad[key]=value
        with pytest.raises(ValueError):validate_row(bad)

@pytest.mark.parametrize('field',[
    'underlying_cited_observation_paper_reviewed','paired_width_boundaries_extracted',
    'coast_distance_is_full_width','confinement_is_rigorous_bound',
    'core_depth_is_fixed_width_layer','core_speed_is_width_threshold',
    'model_grid_spacing_is_width_uncertainty','transport_variability_is_width_variability',
    'transport_calendar_is_width_calendar','model_years_are_observation_dates',
    'integration_gate_is_width_edge','density_layer_is_fixed_depth_slab',
    'map_buffer_eligible','neighboring_current_scale_inheritance_eligible'])
def test_support_claims_rejected(field):
    bad=copy.deepcopy(records()[0]);bad['original_regional_context'][field]=True
    with pytest.raises(ValueError):validate_row(bad)

def test_owner_guard_survives_context_erasure():
    doc=json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
    row=next(r for r in doc['measurements'] if r['current_id'] in OWNERS)
    del row['original_regional_context']
    with pytest.raises(ValueError):validate(doc,json.loads((ROOT/'research/ocean-current-almanac.json').read_bytes()))

def coherent_packet(packet,record_id,changes):
    bad=copy.deepcopy(packet);receipt=bad['manifest']['seasons_receipts']['widths'];doc=json.loads(receipt['source_json'])
    for rows in [doc['measurements'],bad['collections']['widths']]:
        next(r for r in rows if r['id']==record_id).update(changes)
    receipt['source_json']=json.dumps(doc);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest();bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
    return bad

def check_native_guard(directory):
    packet=json.loads((ROOT/'almanac/query-data.json').read_bytes());target=directory/'solomon-confinement-tampered.json';rows=records()
    mutations=[]
    for row in rows:
        other=next(r for r in rows if r['id']!=row['id'])
        for changes in [{'approximate_width_km':row['reported_width_constraint']['reference_scale_km']}, {'fixed_layer_bounds_m':[100,400]}, {'calendar_months':[6,7,8]}, {'original_regional_context':other['original_regional_context']}, {'original_regional_context':{},'current_id':'portugal'}, {'original_regional_context':{},'current_id':other['current_id']}]:
            mutations.append(coherent_packet(packet,row['id'],changes))
    for bad in mutations:
        target.write_text(json.dumps(bad),encoding='utf8')
        result=subprocess.run([str(CLI),str(target),'--seasons'],capture_output=True,text=True,encoding='utf8')
        assert result.returncode==2 and 'Original regional' in result.stderr,result.stderr
    return target

def test_coherent_native_scope_rejection(tmp_path):check_native_guard(tmp_path)
