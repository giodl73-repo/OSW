"""An occupied meander band cannot become a jet width, annual range or footprint."""
import copy,hashlib,json,subprocess
import pytest
from check_tasman_front_band import ROOT,validate_row
from test_rust_query_browser import CLI


def records():
    return [r for r in json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())['measurements'] if r['current_id']=='tasman-front']


def test_occupied_band_definition():
    rows=records();assert len(rows)==1 and rows[0]['approximate_width_km']==600
    assert rows[0]['width_metric']=='author_reported_meander_occupied_band_breadth'
    assert rows[0]['original_regional_context']['individual_jet_width_eligible'] is False
    validate_row(rows[0])


@pytest.mark.parametrize('index',[0])
@pytest.mark.parametrize('key,value',[
    ('width_range_km',[600,700]),('fixed_layer_bounds_m',[0,1300]),
    ('calendar_months',[9]),('observed_period',{'start':'1978-09-04','end':'1978-09-11'}),
    ('uncertainty_km',4),('seasonal_playback_eligible',True),('width_rank_eligible',True),
    ('original_regional_context',{}),('current_id','antarctic-slope'),
    ('approximate_width_km',30),('width_metric','author_reported_current_width')])
def test_promoted_support_rejected(index,key,value):
    row=copy.deepcopy(records()[index]);row[key]=value
    with pytest.raises(ValueError):validate_row(row)


def check_native_guard(directory):
    packet=json.loads((ROOT/'almanac/query-data.json').read_bytes());targets=[]
    changes=[{'width_range_km':[600,700]},{'fixed_layer_bounds_m':[0,1300]},
             {'calendar_months':[9]},{'uncertainty_km':4},
             {'observed_period':{'start':'1978-09-04','end':'1978-09-11'}},
             {'original_regional_context':{},'current_id':'antarctic-slope'},
             {'approximate_width_km':30},{'width_metric':'author_reported_current_width'}]
    for i,change in enumerate(changes):
        bad=copy.deepcopy(packet);receipt=bad['manifest']['seasons_receipts']['widths'];source=json.loads(receipt['source_json'])
        for rows in [source['measurements'],bad['collections']['widths']]:
            next(r for r in rows if r['id']==records()[0]['id']).update(change)
        receipt['source_json']=json.dumps(source,ensure_ascii=False)
        receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest()
        bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
        target=directory/f'tasman-tampered-{i}.json';target.write_text(json.dumps(bad,ensure_ascii=False),encoding='utf8')
        result=subprocess.run([str(CLI),str(target),'--seasons'],capture_output=True,text=True,encoding='utf8')
        assert result.returncode==2 and 'Original regional width' in result.stderr,result.stderr
        targets.append(target)
    return targets


def test_coherent_native_scope_rejection(tmp_path):check_native_guard(tmp_path)
