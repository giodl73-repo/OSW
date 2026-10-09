"""Local radar means retain sampling, layer and velocity/width distinctions."""
import copy,hashlib,json,subprocess
import pytest
from check_western_adriatic_mean_widths import ROOT,AUDIT,validate_row
from test_rust_query_browser import CLI
from test_humboldt_width_descriptions import erased_alias_packet

def records():
    return [r for r in json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())['measurements'] if r['current_id']=='western-adriatic']

def test_two_local_mean_profiles():
    rows=records();assert len(rows)==2
    assert [(r['approximate_width_km'],r['width_range_km']) for r in rows]==[(40,None),(50,None)]
    for i,row in enumerate(rows):
        validate_row(row);assert row['original_regional_context']['audit_pointer']==f'/measurements/{i}'
        assert row['original_regional_context']['deployment_period_months']==['2002-10','2004-10']
        assert row['original_regional_context']['source_sign_conventions']=={'figure_14_southeastward':'positive','figure_15_southeastward':'negative','merged_or_repaired':False}

@pytest.mark.parametrize('key,value',[
    ('approximate_width_km',20),('width_range_km',[40,50]),('width_range_km',[10,20]),
    ('approximate_width_km',6),('approximate_width_km',12),
    ('fixed_layer_bounds_m',[0,1]),('fixed_layer_bounds_m',[0,30]),
    ('calendar_months',[1,2,3]),('observed_period',{'start':'2002-10-01','end':'2004-10-31'}),
    ('uncertainty_km',5),('uncertainty_km',1.5),('seasonal_playback_eligible',True),
    ('annual_extrema_eligible',True),('full_width_inference_eligible',True),('width_rank_eligible',True),
    ('original_regional_context',{}),('current_id','east-adriatic')])
def test_scope_promotions_rejected(key,value):
    for row in records():
        bad=copy.deepcopy(row);bad[key]=value
        with pytest.raises(ValueError):validate_row(bad)

@pytest.mark.parametrize('field',[
    'study_period_is_exact_width_occupation','identical_valid_times_between_sections',
    'averaging_weights_resolved','effective_depth_is_fixed_layer','width_is_tidal_model_prediction',
    'grid_spacing_is_width_uncertainty','radar_range_is_current_width','site_coordinates_are_width_edges',
    'paired_width_boundaries_extracted','velocity_confidence_ellipses_are_width_intervals',
    'tidal_discrepancy_is_current_width','peak_speed_is_width_cutoff','peak_position_is_width',
    'widths_at_two_sites_are_seasonal_range','seasonal_velocity_changes_are_width_series',
    'running_medians_are_width_filter','full_article_reviewed'])
def test_context_promotions_rejected(field):
    bad=copy.deepcopy(records()[0]);bad['original_regional_context'][field]=True
    with pytest.raises(ValueError):validate_row(bad)

def test_source_array_pointer_cannot_select_other_section():
    bad=copy.deepcopy(records()[0]);bad['original_regional_context']['audit_pointer']='/measurements/1'
    with pytest.raises(ValueError):validate_row(bad)

def coherent_packet(packet,key,value):
    bad=copy.deepcopy(packet);receipt=bad['manifest']['seasons_receipts']['widths'];doc=json.loads(receipt['source_json'])
    for rows in [doc['measurements'],bad['collections']['widths']]:
        next(r for r in rows if r['id']==records()[0]['id'])[key]=value
    receipt['source_json']=json.dumps(doc);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest();bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
    return bad

def check_native_guard(directory):
    packet=json.loads((ROOT/'almanac/query-data.json').read_bytes());target=directory/'western-adriatic-tampered.json'
    mutations=[coherent_packet(packet,k,v) for k,v in [('approximate_width_km',20),('width_range_km',[40,50]),('fixed_layer_bounds_m',[0,1]),('calendar_months',[1,2,3]),('original_regional_context',{})]]
    mutations.append(erased_alias_packet(packet,'western-adriatic'))
    for bad in mutations:
        target.write_text(json.dumps(bad),encoding='utf8')
        result=subprocess.run([str(CLI),str(target),'--seasons'],capture_output=True,text=True,encoding='utf8')
        assert result.returncode==2 and 'Original regional width' in result.stderr,result.stderr
    return target

def test_coherent_native_scope_rejection(tmp_path):check_native_guard(tmp_path)
