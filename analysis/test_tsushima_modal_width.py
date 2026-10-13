import copy
import json
import pytest
from check_tsushima_modal_width import ROOT, AUDIT, validate_row

def row():
    return next(r for r in json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())['measurements'] if r['current_id']=='tsushima')

def test_original_modal_estimate_and_operators():
    r=validate_row(row());c=r['modal_decay_context']
    assert r['approximate_width_km']==22 and c['recalculated_width_km']==pytest.approx(23.0769230769)
    assert c['common_current_mean_period']['end']=='1980-08-14'
    assert c['hydrographic_profile_support']['date']=='1980-08-08'
    assert c['arithmetic_discrepancy_unresolved'] is True

@pytest.mark.parametrize('key,value',[('approximate_width_km',23.076923),('width_range_km',[20,22]),('observed_period',{'start':'1980-07-26','end':'1980-08-25'}),('calendar_months',[7,8]),('fixed_layer_bounds_m',[10,110]),('seasonal_playback_eligible',True),('width_rank_eligible',True),('modal_decay_context',{})])
def test_false_admissions_and_erased_context(key,value):
    r=copy.deepcopy(row());r[key]=value
    with pytest.raises(ValueError):validate_row(r)

@pytest.mark.parametrize('key,value',[('arithmetic_discrepancy_unresolved',False),('recalculated_width_km',22),('summary_is_independent_measurement',True),('coefficient_method','Offshore velocity regression')])
def test_coherent_audit_changes_fail(key,value):
    audit=json.loads((ROOT/AUDIT).read_bytes());audit['measurement']['modal_decay_context'][key]=value
    with pytest.raises(ValueError):validate_row(row(),audit)

def test_climatology_and_campaign_support_cannot_be_pooled():
    audit=json.loads((ROOT/AUDIT).read_bytes())
    audit['measurement']['modal_decay_context']['separate_hydrographic_climatology']['is_1980_width_support']=True
    with pytest.raises(ValueError):validate_row(row(),audit)

def test_differential_equation_conflict_is_preserved():
    r=validate_row(row());c=r['modal_decay_context']['offshore_equation_consistency']
    assert c['printed_equation']=='d2Y_n/dy2+gamma_n^2*Y_n=0'
    assert c['inconsistent_for_real_positive_gamma'] is True
    assert c['sign_resolution'] is None and c['diagram_validates_printed_differential_equation'] is False
    audit=json.loads((ROOT/AUDIT).read_bytes())
    audit['measurement']['modal_decay_context']['offshore_equation_consistency']['sign_resolution']='minus'
    with pytest.raises(ValueError):validate_row(row(),audit)
