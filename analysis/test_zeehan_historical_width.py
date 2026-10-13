import copy,json,pytest
from check_zeehan_historical_width import ROOT,AUDIT,validate_row
def row():return next(r for r in json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())['measurements'] if r['current_id']=='zeehan')
def test_attributed_width():
    r=validate_row(row());assert r['approximate_width_km']==40
    assert r['original_regional_context']['section_comparison']['records'][1]['observed_month']=='1997-12'
@pytest.mark.parametrize('key,value',[('width_range_km',[20,40]),('observed_period',{'start':'1997-03-19','end':'1997-12-09'}),('calendar_months',[3,12]),('fixed_layer_bounds_m',[0,300]),('annual_extrema_eligible',True),('seasonal_playback_eligible',True),('original_regional_context',{})])
def test_false_historical_support(key,value):
    r=copy.deepcopy(row());r[key]=value
    with pytest.raises((ValueError,KeyError)):validate_row(r)
@pytest.mark.parametrize('key,value',[('numerical_width_ratio',0.5),('annual_range_eligible',True),('width_relation','December half as wide')])
def test_coherent_comparison_promotion(key,value):
    doc=json.loads((ROOT/AUDIT).read_bytes());doc['measurement']['original_regional_context']['section_comparison'][key]=value
    with pytest.raises(ValueError):validate_row(row(),doc)
def test_coherent_section_width_and_date_promotion():
    for key,value in [('width_km',40),('width_range_km',[20,40]),('observed_month','1997-12-01')]:
        doc=json.loads((ROOT/AUDIT).read_bytes());doc['measurement']['original_regional_context']['section_comparison']['records'][1][key]=value
        with pytest.raises(ValueError):validate_row(row(),doc)
