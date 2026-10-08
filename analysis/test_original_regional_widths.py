"""Background width cannot acquire the dates/layer of a different campaign."""
import copy,hashlib,json,subprocess
import pytest
from check_original_regional_widths import ROOT,AUDIT,ALASKA_AUDIT,validate_row
from test_rust_query_browser import CLI

def test_original_span_is_not_campaign_series():
    row=next(r for r in json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())['measurements'] if r['current_id']=='algerian');validate_row(row)
    for key,value in [('approximate_width_km',40),('calendar_months',[9,10,11,12]),('fixed_layer_bounds_m',[0,975]),('annual_extrema_eligible',True),('seasonal_playback_eligible',True),('observed_period',{'start':'2014-09-01','end':'2016-12-31'})]:
        bad=copy.deepcopy(row);bad[key]=value
        with pytest.raises(ValueError):validate_row(bad)
    a=json.loads((ROOT/AUDIT).read_bytes());a['measurement']['width_range_km']=[20,50]
    with pytest.raises(ValueError):validate_row(row,a)

def test_alaska_point_is_not_neighbor_or_forcing_range():
    row=next(r for r in json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())['measurements'] if r['current_id']=='alaska');validate_row(row)
    for key,value in [('approximate_width_km',100),('width_range_km',[100,300]),('calendar_months',list(range(1,13))),('fixed_layer_bounds_m',[0,40]),('annual_extrema_eligible',True),('seasonal_playback_eligible',True),('width_rank_eligible',True),('observed_period',{'start':'1946-01-01','end':'2000-12-31'}),('uncertainty_km',100),('current_id','alaska-coastal-gulf')]:
        bad=copy.deepcopy(row);bad[key]=value
        with pytest.raises(ValueError):validate_row(bad)
    for key in ['survey_years_are_width_occupations','drifter_depth_is_width_layer','forcing_climatologies_are_width_climatology','year_round_persistence_is_monthly_width_series','alaskan_stream_width_is_range_endpoint','coastal_confinement_is_alaska_width','shelf_breadth_is_current_width','boundary_coordinates_extracted']:
        bad=copy.deepcopy(row);bad['original_regional_context'][key]=True
        with pytest.raises(ValueError):validate_row(bad)
    audit=json.loads((ROOT/ALASKA_AUDIT).read_bytes());audit['measurement']['width_range_km']=[100,400]
    with pytest.raises(ValueError):validate_row(row,audit)

def check_compiled_original_scope(tmp_path):
    path=ROOT/'almanac/query-data.json';packet=json.loads(path.read_bytes())
    plan=json.loads(subprocess.check_output([str(CLI),str(path),'--seasons'],encoding='utf8'))['phase_plans']['algerian']
    assert len(plan['phases'])==1 and plan['can_play'] is False and plan['eligible_indices']==[]
    assert plan['phases'][0]['playback_step_eligible'] is False
    for key,value in [('approximate_width_km',40),('width_range_km',[30,120]),('calendar_months',[9,10,11,12]),('fixed_layer_bounds_m',[0,975]),('seasonal_playback_eligible',True)]:
        bad=copy.deepcopy(packet);receipt=bad['manifest']['seasons_receipts']['widths'];doc=json.loads(receipt['source_json'])
        next(r for r in doc['measurements'] if r['current_id']=='algerian')[key]=value
        next(r for r in bad['collections']['widths'] if r['current_id']=='algerian')[key]=value
        receipt['source_json']=json.dumps(doc);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest();bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
        target=tmp_path/'algerian-tampered.json';target.write_text(json.dumps(bad),encoding='utf8')
        result=subprocess.run([str(CLI),str(target),'--seasons'],capture_output=True,text=True,encoding='utf8')
        assert result.returncode==2 and 'Original regional width' in result.stderr,result.stderr
    plan=json.loads(subprocess.check_output([str(CLI),str(path),'--seasons'],encoding='utf8'))['phase_plans']['alaska']
    assert len(plan['phases'])==1 and plan['can_play'] is False and plan['eligible_indices']==[]
    for key,value in [('approximate_width_km',100),('width_range_km',[100,300]),('calendar_months',list(range(1,13))),('fixed_layer_bounds_m',[0,40]),('seasonal_playback_eligible',True),('original_regional_context',{})]:
        bad=copy.deepcopy(packet);receipt=bad['manifest']['seasons_receipts']['widths'];doc=json.loads(receipt['source_json'])
        next(r for r in doc['measurements'] if r['current_id']=='alaska')[key]=value
        next(r for r in bad['collections']['widths'] if r['current_id']=='alaska')[key]=value
        receipt['source_json']=json.dumps(doc);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest();bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
        target=tmp_path/'alaska-tampered.json';target.write_text(json.dumps(bad),encoding='utf8')
        result=subprocess.run([str(CLI),str(target),'--seasons'],capture_output=True,text=True,encoding='utf8')
        assert result.returncode==2 and 'Original regional width' in result.stderr,result.stderr
