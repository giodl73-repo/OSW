"""Reject conflation of climatological contour breadths and other supports."""
import copy, hashlib, json, subprocess
import pytest
from check_acc_udintsev_breadths import ROOT,validate_row
from check_current_width_inventory import validate
from test_rust_query_browser import CLI

def records():
    return [r for r in json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())['measurements'] if r['current_id']=='acc']

def test_distinct_original_metrics():
    rows=records()
    assert len(rows)==2
    assert [r['approximate_width_km'] for r in rows]==[170,500]
    assert len({r['width_metric'] for r in rows})==2
    assert [r['original_regional_context']['boundary_labels'] for r in rows]==[['SAF','SACCF'],['NB','SB']]
    for row in rows: validate_row(row)

@pytest.mark.parametrize('index',[0,1])
@pytest.mark.parametrize('key,value',[
    ('width_range_km',[170,500]),('fixed_layer_bounds_m',[100,250]),
    ('calendar_months',[2,12]),('observed_period',{'start':'2016-02-01','end':'2017-12-31'}),
    ('uncertainty_km',14),('width_rank_eligible',True),('seasonal_playback_eligible',True),
    ('full_width_inference_eligible',True),('original_regional_context',{}),('current_id','antarctic-slope')])
def test_promoted_support_rejected(index,key,value):
    row=copy.deepcopy(records()[index]); row[key]=value
    with pytest.raises(ValueError): validate_row(row)

@pytest.mark.parametrize('key,value',[
    ('boundary_labels',['NB','SB']),('boundary_mdt_m',[0.3,-1.11]),
    ('reference_period_years',[2016,2017]),('other_quantity_is_range_endpoint',True),
    ('hydrographic_front_agreement_is_width_uncertainty',True),('argo_temperature_depths_are_width_layer',True),
    ('cruise_months_are_width_occupations',True),('jet_speed_association_is_edge_cutoff',True),
    ('map_buffer_eligible',True),('meridional_distance_is_flow_normal_width',True)])
def test_method_and_support_identity_rejected(key,value):
    row=copy.deepcopy(records()[0]);row['original_regional_context'][key]=value
    with pytest.raises(ValueError): validate_row(row)

def test_owner_guard_with_erased_context():
    document=json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
    row=next(r for r in document['measurements'] if r['current_id']=='acc')
    del row['original_regional_context']
    with pytest.raises(ValueError): validate(document,json.loads((ROOT/'research/ocean-current-almanac.json').read_bytes()))

@pytest.mark.parametrize('owner',['antarctic-slope','algerian'])
def test_inventory_identity_guard_survives_context_erasure_and_transfer(owner):
    document=json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
    row=next(r for r in document['measurements'] if r['current_id']=='acc')
    row['current_id']=owner
    del row['original_regional_context']
    with pytest.raises(ValueError,match='ACC quantities pooled, support promoted or source identity changed'):
        validate(document,json.loads((ROOT/'research/ocean-current-almanac.json').read_bytes()))

def check_native_guard(directory):
    packet=json.loads((ROOT/'almanac/query-data.json').read_bytes()); targets=[]
    changes_list=[{'width_range_km':[170,500]}, {'fixed_layer_bounds_m':[100,250]},
                  {'calendar_months':[2,12]}, {'uncertainty_km':14},
                  {'original_regional_context':{},'current_id':'antarctic-slope'},
                  {'original_regional_context':{},'current_id':'algerian'},
                  {'width_metric':records()[1]['width_metric'],'approximate_width_km':500}]
    for i,changes in enumerate(changes_list):
        bad=copy.deepcopy(packet);receipt=bad['manifest']['seasons_receipts']['widths']
        document=json.loads(receipt['source_json'])
        for rows in [document['measurements'],bad['collections']['widths']]:
            next(r for r in rows if r['id']==records()[0]['id']).update(changes)
        receipt['source_json']=json.dumps(document)
        receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest()
        bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
        target=directory/f'acc-breadth-tampered-{i}.json';target.write_text(json.dumps(bad),encoding='utf8')
        result=subprocess.run([str(CLI),str(target),'--seasons'],capture_output=True,text=True,encoding='utf8')
        assert result.returncode==2 and 'Original regional' in result.stderr,result.stderr
        targets.append(target)
    return targets

def test_coherent_native_scope_rejection(tmp_path): check_native_guard(tmp_path)
