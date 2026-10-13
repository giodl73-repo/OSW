"""Keep model means, theoretical scales and real calendar occupations separate."""
import copy
import hashlib
import json
import subprocess
import pytest
from check_guinea_model_width import ROOT, AUDIT, validate_row
from test_rust_query_browser import CLI

def test_model_scope_and_theoretical_exclusions():
    row = next(r for r in json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())['measurements'] if r['current_id']=='guinea')
    validate_row(row)
    for key, value in [('approximate_width_km',210), ('width_range_km',[200,210]), ('calendar_months',[7,8,9]), ('observed_period',{'start':'2005-01-01','end':'2010-12-31'}), ('fixed_layer_bounds_m',[0,40]), ('seasonal_playback_eligible',True)]:
        bad = copy.deepcopy(row); bad[key] = value
        with pytest.raises(ValueError): validate_row(bad)
    audit = json.loads((ROOT/AUDIT).read_bytes())
    audit['measurement']['model_regional_context']['model']['analysis_model_years']=[2005,2006,2007,2008,2009,2010]
    with pytest.raises(ValueError): validate_row(row,audit)

def check_compiled_model_scope(tmp_path):
    path=ROOT/'almanac/query-data.json'
    packet=json.loads(path.read_bytes())
    plans=json.loads(subprocess.check_output([str(CLI),str(path),'--seasons'],encoding='utf8'))['phase_plans']
    plan=plans['guinea']
    assert len(plan['phases'])==1 and plan['can_play'] is False and plan['eligible_indices']==[]
    assert plan['phases'][0]['playback_step_eligible'] is False
    for key,value in [('approximate_width_km',210),('width_range_km',[200,210]),('calendar_months',[7,8,9]),('fixed_layer_bounds_m',[0,40]),('seasonal_playback_eligible',True)]:
        bad=copy.deepcopy(packet)
        receipt=bad['manifest']['seasons_receipts']['widths'];doc=json.loads(receipt['source_json'])
        next(r for r in doc['measurements'] if r['current_id']=='guinea')[key]=value
        next(r for r in bad['collections']['widths'] if r['current_id']=='guinea')[key]=value
        receipt['source_json']=json.dumps(doc);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest()
        bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
        target=tmp_path/'guinea-tampered.json';target.write_text(json.dumps(bad),encoding='utf8')
        result=subprocess.run([str(CLI),str(target),'--seasons'],capture_output=True,text=True,encoding='utf8')
        assert result.returncode==2 and 'Guinea model width' in result.stderr,result.stderr
