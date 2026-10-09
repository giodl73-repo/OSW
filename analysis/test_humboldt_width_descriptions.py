"""Regional source descriptions cannot become ranges or seasonal samples."""
import copy,hashlib,json,subprocess
import pytest
from check_humboldt_width_descriptions import ROOT,AUDIT,validate_row
from check_current_width_inventory import validate
from test_rust_query_browser import CLI

def records():
    return [r for r in json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())['measurements'] if r['current_id']=='peru-humboldt']

def test_three_descriptions_keep_distinct_support():
    rows=records();assert [r['approximate_width_km'] for r in rows]==[250,350,800]
    assert [r['original_regional_context']['audit_pointer'] for r in rows]==['/measurements/0','/measurements/1','/measurements/2']
    for row in rows:validate_row(row)

@pytest.mark.parametrize('key,value',[('approximate_width_km',300),('width_range_km',[250,350]),('width_range_km',[250,800]),('calendar_months',[1,2,3]),('fixed_layer_bounds_m',[0,1500]),('observed_period',{'start':'1993-01-01','end':'2005-12-31'}),('uncertainty_km',50),('seasonal_playback_eligible',True),('annual_extrema_eligible',True),('width_rank_eligible',True),('original_regional_context',{}),('current_id','peru-chile-undercurrent')])
def test_source_scopes_cannot_be_promoted(key,value):
    for row in records():
        bad=copy.deepcopy(row);bad[key]=value
        with pytest.raises(ValueError):validate_row(bad)

def test_inventory_context_erasure_cannot_bypass_guard():
    document=json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes());ledger=json.loads((ROOT/'research/ocean-current-almanac.json').read_bytes())
    next(r for r in document['measurements'] if r['current_id']=='peru-humboldt').pop('original_regional_context')
    with pytest.raises(ValueError):validate(document,ledger)

@pytest.mark.parametrize('field',['core_jet_relationship_resolved','reference_pressure_is_fixed_width_layer','qualitative_seasonality_is_numeric_width_series','three_descriptions_are_annual_range','original_pdf_acquired','figures_visually_inspected'])
def test_unresolved_source_support_cannot_be_claimed(field):
    bad=copy.deepcopy(records()[0]);bad['original_regional_context'][field]=True
    with pytest.raises(ValueError):validate_row(bad)

def coherent_packet(packet,key,value):
    bad=copy.deepcopy(packet);receipt=bad['manifest']['seasons_receipts']['widths'];doc=json.loads(receipt['source_json'])
    next(r for r in doc['measurements'] if r['current_id']=='peru-humboldt')[key]=value
    next(r for r in bad['collections']['widths'] if r['current_id']=='peru-humboldt')[key]=value
    receipt['source_json']=json.dumps(doc);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest();bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
    return bad

def erased_alias_packet(packet,owner='peru-humboldt'):
    bad=copy.deepcopy(packet);receipt=bad['manifest']['seasons_receipts']['widths'];doc=json.loads(receipt['source_json'])
    identity=next(r['id'] for r in doc['measurements'] if r['current_id']==owner and r.get('original_regional_context'))
    for rows in [doc['measurements'],bad['collections']['widths']]:
        row=next(r for r in rows if r['id']==identity);row.pop('original_regional_context');row['current_id']='portugal'
    receipt['source_json']=json.dumps(doc);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest();bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
    return bad

@pytest.mark.parametrize('owner',['jutland','western-adriatic','baffin','peru-humboldt','west-australian','zeehan','kuroshio-extension','new-guinea-coastal-undercurrent','algerian','alaska','atlantic-equatorial-undercurrent','pacific-equatorial-undercurrent'])
def test_context_deletion_and_alias_transfer_rejected(tmp_path,owner):
    packet=json.loads((ROOT/'almanac/query-data.json').read_bytes());bad=erased_alias_packet(packet,owner)
    ledger=json.loads((ROOT/'research/ocean-current-almanac.json').read_bytes())
    with pytest.raises(ValueError):validate(json.loads(bad['manifest']['seasons_receipts']['widths']['source_json']),ledger)
    target=tmp_path/'alias.json';target.write_text(json.dumps(bad),encoding='utf8')
    result=subprocess.run([str(CLI),str(target),'--seasons'],capture_output=True,text=True,encoding='utf8')
    assert result.returncode==2 and 'Original regional width' in result.stderr,result.stderr

def check_native_guard(directory):
    packet=json.loads((ROOT/'almanac/query-data.json').read_bytes());target=directory/'humboldt-tampered.json'
    for key,value in [('approximate_width_km',300),('width_range_km',[250,350]),('calendar_months',[1,2,3]),('original_regional_context',{})]:
        target.write_text(json.dumps(coherent_packet(packet,key,value)),encoding='utf8')
        result=subprocess.run([str(CLI),str(target),'--seasons'],capture_output=True,text=True,encoding='utf8')
        assert result.returncode==2 and 'Original regional width' in result.stderr,result.stderr
    target.write_text(json.dumps(erased_alias_packet(packet)),encoding='utf8')
    result=subprocess.run([str(CLI),str(target),'--seasons'],capture_output=True,text=True,encoding='utf8')
    assert result.returncode==2 and 'Original regional width' in result.stderr,result.stderr
    return target
