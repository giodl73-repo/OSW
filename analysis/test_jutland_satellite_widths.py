"""Distinct sites and source operators cannot become seasonal dimensions."""
import copy,hashlib,json,subprocess
import pytest
from check_jutland_satellite_widths import ROOT,AUDIT,validate_row
from check_current_width_inventory import validate
from test_rust_query_browser import CLI

def records():
    return [r for r in json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())['measurements'] if r['id'].startswith('jutland-nielsen-2000-')]

def test_three_separate_site_estimates():
    rows=records();assert [(r['approximate_width_km'],r['width_range_km']) for r in rows]==[(40,None),(25,None),(None,[20,25])]
    for i,row in enumerate(rows):
        validate_row(row);assert row['original_regional_context']['audit_pointer']==f'/measurements/{i}'
        assert row['original_regional_context']['qualitative_widening_context']['calendar_months_assigned'] is None

@pytest.mark.parametrize('key,value',[
    ('approximate_width_km',22.5),('width_range_km',[10,40]),('width_range_km',[20,40]),
    ('fixed_layer_bounds_m',[0,30]),('fixed_layer_bounds_m',[0,10]),
    ('calendar_months',[7,8]),('observed_period',{'start':'1994-01-01','end':'1994-12-31'}),
    ('uncertainty_km',5),('seasonal_playback_eligible',True),('annual_extrema_eligible',True),
    ('full_width_inference_eligible',True),('width_rank_eligible',True),
    ('original_regional_context',{}),('current_id','norwegian-coastal')])
def test_scope_promotions_rejected(key,value):
    for row in records():
        bad=copy.deepcopy(row);bad[key]=value
        with pytest.raises(ValueError):validate_row(bad)

@pytest.mark.parametrize('field',[
    'underlying_width_methods_reviewed','original_satellite_images_acquired',
    'satellite_sensor_resolved','image_dates_resolved','image_threshold_resolved',
    'paired_width_boundaries_extracted','image_resolution_is_width_uncertainty',
    'freshwater_definition_is_image_threshold','mixed_water_description_is_fixed_depth_slab',
    'publication_year_is_width_occupation','hydrographic_years_are_image_dates',
    'sites_form_annual_range','cross_source_span_is_annual_range','full_report_reviewed'])
def test_context_support_cannot_be_claimed(field):
    bad=copy.deepcopy(records()[0]);bad['original_regional_context'][field]=True
    with pytest.raises(ValueError):validate_row(bad)

def test_same_owner_other_audit_and_site_pointer_rejected():
    row=copy.deepcopy(records()[0]);doc=json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
    earlier=next(r for r in doc['measurements'] if r['id']=='jutland-skov-2019-coastal-water-mass-breadth')
    for context in [earlier['original_regional_context'],dict(row['original_regional_context'],audit_pointer='/measurements/2')]:
        bad=copy.deepcopy(row);bad['original_regional_context']=context
        with pytest.raises(ValueError):validate_row(bad)

def coherent_packet(packet,key,value):
    bad=copy.deepcopy(packet);receipt=bad['manifest']['seasons_receipts']['widths'];doc=json.loads(receipt['source_json'])
    for rows in [doc['measurements'],bad['collections']['widths']]:
        next(r for r in rows if r['id']==records()[0]['id'])[key]=value
    receipt['source_json']=json.dumps(doc);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest();bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
    return bad

def check_native_guard(directory):
    packet=json.loads((ROOT/'almanac/query-data.json').read_bytes());target=directory/'jutland-satellite-tampered.json'
    old=next(r for r in packet['collections']['widths'] if r['id']=='jutland-skov-2019-coastal-water-mass-breadth')
    mutations=[coherent_packet(packet,k,v) for k,v in [('width_range_km',[10,40]),('fixed_layer_bounds_m',[0,30]),('calendar_months',[7,8]),('original_regional_context',old['original_regional_context'])]]
    alias=coherent_packet(packet,'original_regional_context',{});receipt=alias['manifest']['seasons_receipts']['widths'];doc=json.loads(receipt['source_json'])
    for rows in [doc['measurements'],alias['collections']['widths']]:next(r for r in rows if r['id']==records()[0]['id'])['current_id']='portugal'
    receipt['source_json']=json.dumps(doc);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest();alias['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256'];mutations.append(alias)
    for bad in mutations:
        target.write_text(json.dumps(bad),encoding='utf8')
        result=subprocess.run([str(CLI),str(target),'--seasons'],capture_output=True,text=True,encoding='utf8')
        assert result.returncode==2 and 'Original regional' in result.stderr,result.stderr
    return target

def test_coherent_native_scope_rejection(tmp_path):check_native_guard(tmp_path)
