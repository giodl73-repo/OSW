"""Water-mass breadth preserves source support across Python and Rust."""
import copy,hashlib,json,subprocess
import pytest
from check_jutland_water_mass_breadth import ROOT,AUDIT,validate_row
from test_rust_query_browser import CLI
from test_humboldt_width_descriptions import erased_alias_packet

def records():
    return [r for r in json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())['measurements'] if r['id']=='jutland-skov-2019-coastal-water-mass-breadth']

def test_regional_water_mass_span():
    row,=records();validate_row(row)
    assert row['width_range_km']==[10,20] and row['approximate_width_km'] is None
    c=row['original_regional_context']
    assert c['audit_pointer']=='/measurements/0'
    assert c['quantity_scope']=='surface_water_mass_breadth_not_velocity_core_width'
    assert c['habitat_context']['zone_around_km']==40
    assert c['offshore_context']['traceability_almost_km']==100

@pytest.mark.parametrize('key,value',[
    ('approximate_width_km',15),('approximate_width_km',20),('approximate_width_km',40),
    ('width_range_km',[10,40]),('width_range_km',[40,100]),('width_range_km',[20,20]),
    ('fixed_layer_bounds_m',[15,30]),('calendar_months',[12]),
    ('observed_period',{'start':'2018-12-01','end':'2018-12-31'}),
    ('uncertainty_km',5),('width_rank_eligible',True),('annual_extrema_eligible',True),
    ('seasonal_playback_eligible',True),('full_width_inference_eligible',True),
    ('is_confidence_interval',True),('original_regional_context',{}),('current_id','norwegian-coastal')])
def test_scope_promotions_rejected(key,value):
    bad=copy.deepcopy(records()[0]);bad[key]=value
    with pytest.raises(ValueError):validate_row(bad)

@pytest.mark.parametrize('field',[
    'underlying_width_methods_reviewed','salinity_threshold_extracted',
    'paired_width_boundaries_extracted','surface_label_is_fixed_depth_layer',
    'width_occupation_dates_resolved','publication_year_is_width_occupation',
    'modeled_map_date_is_width_occupation','model_map_is_width_measurement',
    'span_is_annual_range','full_report_reviewed'])
def test_unknown_support_cannot_be_claimed(field):
    bad=copy.deepcopy(records()[0]);bad['original_regional_context'][field]=True
    with pytest.raises(ValueError):validate_row(bad)

@pytest.mark.parametrize('block,field',[
    ('offshore_context','are_paired_width_edges'),('offshore_context','are_range_endpoints'),
    ('habitat_context','is_current_width'),('habitat_context','bathymetry_is_width_layer'),
    ('habitat_context','bird_seasonality_is_width_series'),
    ('alternate_geographic_context','is_preferred_width'),
    ('alternate_geographic_context','is_dated_width_sample'),
    ('alternate_geographic_context','is_independent_measurement'),
    ('naming_context','north_south_aliases_resolved'),('naming_context','canonical_alias_admitted'),
    ('naming_context','norwegian_coastal_width_inheritance_eligible')])
def test_contexts_cannot_be_inherited(block,field):
    bad=copy.deepcopy(records()[0]);bad['original_regional_context'][block][field]=True
    with pytest.raises(ValueError):validate_row(bad)

def coherent_packet(packet,key,value):
    bad=copy.deepcopy(packet);receipt=bad['manifest']['seasons_receipts']['widths'];doc=json.loads(receipt['source_json'])
    for rows in [doc['measurements'],bad['collections']['widths']]:
        next(r for r in rows if r['id']==records()[0]['id'])[key]=value
    receipt['source_json']=json.dumps(doc);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest();bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
    return bad

def check_native_guard(directory):
    packet=json.loads((ROOT/'almanac/query-data.json').read_bytes());target=directory/'jutland-tampered.json'
    mutations=[coherent_packet(packet,k,v) for k,v in [('approximate_width_km',15),('width_range_km',[40,100]),('fixed_layer_bounds_m',[15,30]),('calendar_months',[12]),('original_regional_context',{})]]
    mutations.append(erased_alias_packet(packet,'jutland'))
    for bad in mutations:
        target.write_text(json.dumps(bad),encoding='utf8')
        result=subprocess.run([str(CLI),str(target),'--seasons'],capture_output=True,text=True,encoding='utf8')
        assert result.returncode==2 and 'Original regional width' in result.stderr,result.stderr
    return target

def test_coherent_native_scope_rejection(tmp_path):check_native_guard(tmp_path)
