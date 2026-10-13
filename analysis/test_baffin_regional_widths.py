"""Baffin summary spans cannot become seasonal widths or sampling envelopes."""
import copy,hashlib,json,subprocess
import pytest
from check_baffin_regional_widths import ROOT,AUDIT,validate_row
from test_rust_query_browser import CLI
from test_humboldt_width_descriptions import erased_alias_packet

def records():
    return [r for r in json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())['measurements'] if r['current_id']=='baffin']

def test_two_distinct_regional_supports():
    rows=records();assert len(rows)==2
    assert [(r['approximate_width_km'],r['width_range_km']) for r in rows]==[(25,None),(None,[10,30])]
    for i,row in enumerate(rows):
        validate_row(row);assert row['original_regional_context']['audit_pointer']==f'/measurements/{i}'

@pytest.mark.parametrize('key,value',[
    ('approximate_width_km',20),('width_range_km',[10,60]),('width_range_km',[20,25]),
    ('width_range_km',[6,16]),('approximate_width_km',35),('approximate_width_km',33),
    ('fixed_layer_bounds_m',[4,11]),('fixed_layer_bounds_m',[0,300]),
    ('calendar_months',[7,8]),('observed_period',{'start':'1978-07-01','end':'1979-10-31'}),
    ('uncertainty_km',10),('seasonal_playback_eligible',True),('annual_extrema_eligible',True),
    ('full_width_inference_eligible',True),('width_rank_eligible',True),
    ('original_regional_context',{}),('current_id','portugal')])
def test_scope_promotions_rejected(key,value):
    for row in records():
        bad=copy.deepcopy(row);bad[key]=value
        with pytest.raises(ValueError):validate_row(bad)

@pytest.mark.parametrize('field',[
    'offshore_distance_is_current_width','excursion_widening_is_seasonal_range',
    'factor_applied_to_width_endpoints','winter_current_meters_are_winter_widths',
    'instrument_depth_is_fixed_width_layer','reference_is_level_of_no_motion',
    'speed_agreement_error_is_width_uncertainty','typical_year_applicability_resolved',
    'eddy_diameter_is_current_width','paired_width_boundaries_extracted',
    'existing_route_contains_lancaster_intrusion','route_width_band_eligible','full_article_reviewed'])
def test_context_promotions_rejected(field):
    bad=copy.deepcopy(records()[0]);bad['original_regional_context'][field]=True
    with pytest.raises(ValueError):validate_row(bad)

def coherent_packet(packet,key,value):
    bad=copy.deepcopy(packet);receipt=bad['manifest']['seasons_receipts']['widths'];doc=json.loads(receipt['source_json'])
    for rows in [doc['measurements'],bad['collections']['widths']]:
        next(r for r in rows if r['id']==records()[1]['id'])[key]=value
    receipt['source_json']=json.dumps(doc);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest();bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
    return bad

def check_native_guard(directory):
    packet=json.loads((ROOT/'almanac/query-data.json').read_bytes());target=directory/'baffin-tampered.json'
    mutations=[coherent_packet(packet,k,v) for k,v in [('approximate_width_km',20),('width_range_km',[10,60]),('calendar_months',[7,8]),('original_regional_context',{})]]
    mutations.append(erased_alias_packet(packet,'baffin'))
    for bad in mutations:
        target.write_text(json.dumps(bad),encoding='utf8')
        result=subprocess.run([str(CLI),str(target),'--seasons'],capture_output=True,text=True,encoding='utf8')
        assert result.returncode==2 and 'Original regional width' in result.stderr,result.stderr
    return target

def test_coherent_native_scope_rejection(tmp_path):check_native_guard(tmp_path)
