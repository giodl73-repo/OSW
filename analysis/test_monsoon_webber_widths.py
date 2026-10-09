"""Distinct flow/origin definitions cannot become a temporal range or footprint."""
import copy,hashlib,json,subprocess
import pytest
from check_monsoon_webber_widths import ROOT,validate_row
from test_rust_query_browser import CLI


def records():
    return [r for r in json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())['measurements'] if r['current_id']=='monsoon']


def test_distinct_feature_definitions():
    rows=records();assert [r['approximate_width_km'] for r in rows]==[300,150]
    assert len({r['width_metric'] for r in rows})==2
    assert rows[1]['original_regional_context']['description_kind']=='conditional_salinity_origin_component'
    for row in rows:validate_row(row)


@pytest.mark.parametrize('index',[0,1])
@pytest.mark.parametrize('key,value',[
    ('width_range_km',[150,300]),('fixed_layer_bounds_m',[110,110]),
    ('calendar_months',[7]),('observed_period',{'start':'2016-07-05','end':'2016-07-15'}),
    ('uncertainty_km',4),('seasonal_playback_eligible',True),('width_rank_eligible',True),
    ('original_regional_context',{}),('current_id','antarctic-slope')])
def test_promoted_support_rejected(index,key,value):
    row=copy.deepcopy(records()[index]);row[key]=value
    with pytest.raises(ValueError):validate_row(row)


def check_native_guard(directory):
    packet=json.loads((ROOT/'almanac/query-data.json').read_bytes());targets=[]
    changes=[{'width_range_km':[150,300]},{'fixed_layer_bounds_m':[110,110]},
             {'calendar_months':[7]},{'uncertainty_km':4},
             {'observed_period':{'start':'2016-07-05','end':'2016-07-15'}},
             {'original_regional_context':{},'current_id':'antarctic-slope'}]
    for i,change in enumerate(changes):
        bad=copy.deepcopy(packet);receipt=bad['manifest']['seasons_receipts']['widths'];source=json.loads(receipt['source_json'])
        for rows in [source['measurements'],bad['collections']['widths']]:
            next(r for r in rows if r['id']==records()[1]['id']).update(change)
        receipt['source_json']=json.dumps(source,ensure_ascii=False)
        receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest()
        bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
        target=directory/f'monsoon-tampered-{i}.json';target.write_text(json.dumps(bad,ensure_ascii=False),encoding='utf8')
        result=subprocess.run([str(CLI),str(target),'--seasons'],capture_output=True,text=True,encoding='utf8')
        assert result.returncode==2 and 'Original regional width' in result.stderr,result.stderr
        targets.append(target)
    return targets


def test_coherent_native_scope_rejection(tmp_path):check_native_guard(tmp_path)
