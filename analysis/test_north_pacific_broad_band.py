"""Reject unsupported dimensions and definition transfers from textbook prose."""
import copy,hashlib,json,subprocess
import pytest
from check_north_pacific_broad_band import ROOT,validate_row
from check_current_width_inventory import validate
from test_rust_query_browser import CLI
def records():return [r for r in json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())['measurements'] if r['current_id']=='north-pacific']
def test_qualifier_combined_definition_and_page_version():
    row=records()[0];validate_row(row)
    assert len(records())==1 and row['approximate_width_km'] is None and row['width_range_km'] is None
    assert row['reported_width_constraint']['source_notation']=='more than 2000 km'
    c=row['original_regional_context'];assert c['page_version']=='1.1 March 2005'
    assert c['preface_history_version']=='1.2 September 2002'
    assert c['naming_context']['canonical_subarctic_current_id']=='aleutian'
    assert c['adjacent_stream_context']['identity']=='alaskan-stream'
@pytest.mark.parametrize('key,value',[
    ('approximate_width_km',2000),('width_range_km',[150,200]),('width_range_km',[2000,3000]),
    ('fixed_layer_bounds_m',[0,1000]),('calendar_months',[6,7,8]),
    ('observed_period',{'start':'2005-03-01','end':'2005-03-31'}),
    ('uncertainty_km',100),('seasonal_playback_eligible',True),('annual_extrema_eligible',True),
    ('full_width_inference_eligible',True),('width_rank_eligible',True),
    ('original_regional_context',{}),('current_id','aleutian'),('current_id','alaska')])
def test_scope_promotions_rejected(key,value):
    bad=copy.deepcopy(records()[0]);bad[key]=value
    with pytest.raises(ValueError):validate_row(bad)
@pytest.mark.parametrize('field',[
    'full_book_reviewed','publication_version_is_observation_date',
    'more_than_scale_is_representative_width','more_than_scale_is_rigorous_bound',
    'paired_width_boundaries_extracted','source_band_is_flow_normal_transect',
    'adjacent_stream_transport_layer_is_width_layer','adjacent_stream_span_is_north_pacific_width',
    'alternative_43N_split_is_velocity_boundary','front_latitudes_are_width_edges',
    'nearby_SST_image_date_is_width_date','schematic_map_digitized',
    'schematic_projection_is_measurement_support','seasonal_calendar_extracted',
    'map_buffer_eligible','cross_current_width_inheritance_eligible'])
def test_context_support_cannot_be_invented(field):
    bad=copy.deepcopy(records()[0]);bad['original_regional_context'][field]=True
    with pytest.raises(ValueError):validate_row(bad)
def test_owner_guard_survives_erasure_and_qualifier_change():
    doc=json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
    row=next(r for r in doc['measurements'] if r['current_id']=='north-pacific');del row['original_regional_context']
    with pytest.raises(ValueError):validate(doc,json.loads((ROOT/'research/ocean-current-almanac.json').read_bytes()))
    bad=copy.deepcopy(records()[0]);bad['reported_width_constraint']['source_notation']='2000 km'
    with pytest.raises(ValueError):validate_row(bad)
def coherent_packet(packet,changes):
    bad=copy.deepcopy(packet);receipt=bad['manifest']['seasons_receipts']['widths'];doc=json.loads(receipt['source_json'])
    for rows in [doc['measurements'],bad['collections']['widths']]:next(r for r in rows if r['id']==records()[0]['id']).update(changes)
    receipt['source_json']=json.dumps(doc);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest();bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256'];return bad
def check_native_guard(directory):
    packet=json.loads((ROOT/'almanac/query-data.json').read_bytes());target=directory/'north-pacific-band-tampered.json'
    mutations=[coherent_packet(packet,changes) for changes in [{'approximate_width_km':2000},{'width_range_km':[150,200]},{'fixed_layer_bounds_m':[0,1000]},{'calendar_months':[6,7,8]},{'original_regional_context':{},'current_id':'aleutian'},{'original_regional_context':{},'current_id':'alaska'}]]
    for bad in mutations:
        target.write_text(json.dumps(bad),encoding='utf8');result=subprocess.run([str(CLI),str(target),'--seasons'],capture_output=True,text=True,encoding='utf8')
        assert result.returncode==2 and 'Original regional' in result.stderr,result.stderr
    return target
def test_coherent_native_scope_rejection(tmp_path):check_native_guard(tmp_path)
