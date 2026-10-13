"""A seasonal prose span cannot become a monthly observation series."""
import copy,hashlib,json,subprocess
import pytest
from check_somali_seasonal_width import ROOT,AUDIT,validate_row
from test_rust_query_browser import CLI

def test_source_calendar_and_no_inference():
    row=next(r for r in json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())['measurements'] if r['current_id']=='somali');validate_row(row)
    for key,value in [('calendar_months',[6,7,8]),('approximate_width_km',75),('fixed_layer_bounds_m',[0,500]),('annual_extrema_eligible',True),('seasonal_playback_eligible',True),('observed_period',{'start':'2001-03-01','end':'2001-05-31'})]:
        bad=copy.deepcopy(row);bad[key]=value
        with pytest.raises(ValueError):validate_row(bad)
    audit=json.loads((ROOT/AUDIT).read_bytes());audit['measurement']['width_range_km']=[50,150]
    with pytest.raises(ValueError):validate_row(row,audit)

def check_compiled_scope_and_independent_route_playback(tmp_path):
    path=ROOT/'almanac/query-data.json';bundle=json.loads(path.read_bytes())
    plans=json.loads(subprocess.check_output([str(CLI),str(path),'--seasons'],encoding='utf8'))['phase_plans']
    plan=plans['somali'];assert len(plan['phases'])==3 and plan['can_play'] is True and plan['eligible_indices']==[1,2]
    assert plan['phases'][0]['playback_step_eligible'] is False
    assert plans['northern-mediterranean']['can_play'] is True
    for key,value in [('calendar_months',[6,7,8]),('approximate_width_km',75),('seasonal_playback_eligible',True)]:
        bad=copy.deepcopy(bundle);receipt=bad['manifest']['seasons_receipts']['widths'];doc=json.loads(receipt['source_json'])
        next(r for r in doc['measurements'] if r['current_id']=='somali')[key]=value
        next(r for r in bad['collections']['widths'] if r['current_id']=='somali')[key]=value
        receipt['source_json']=json.dumps(doc);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest();bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
        target=tmp_path/'changed.json';target.write_text(json.dumps(bad),encoding='utf8')
        result=subprocess.run([str(CLI),str(target),'--seasons'],capture_output=True,text=True,encoding='utf8')
        assert result.returncode==2 and 'Somali seasonal width' in result.stderr,result.stderr
