"""Nominal drifting depths, overlapping subsets and distinct error support."""
import copy,hashlib,json,subprocess
import pytest
from check_dwbc_float_composite import ROOT,validate_row
from test_rust_query_browser import CLI,native

def record():
    return next(r for r in json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())['measurements'] if r['current_id']=='deep-western-boundary')

def test_source_definitions_and_auxiliary_subsets():
    r=record();validate_row(r);c=r['original_regional_context'];table=c['source_table_rows']
    assert r['approximate_width_km']==100 and r['width_range_km'] is None
    assert [t['observations_in_current'] for t in table]==[500,124,188,177]
    assert sum(t['observations_in_current'] for t in table[1:])==489
    assert [t['maximum_bin_average_velocity_cm_s'] for t in table]==[26,39,30,19]
    assert [t['transport_per_unit_depth_10_3_m2_s'] for t in table]==[14,23,16,8]
    assert all(t['current_width_km']==100 for t in table)
    assert all(t['total_volume_transport_sv'] is None for t in table[1:])
    assert r['fixed_layer_bounds_m'] is None and c['source_estimated_float_sinking_m']==230
    assert c['geographic_view_role']=='figure_viewport_context_only'
    assert c['independent_subset_width_edges_extracted'] is False

CHANGES=[{'uncertainty_km':5},{'width_range_km':[90,130]},
         {'fixed_layer_bounds_m':[1800,1800]},{'fixed_layer_bounds_m':[900,2800]},
         {'calendar_months':[1,2,3,4,5,6,7,8,9,10]},
         {'observed_period':{'start':'1989-01-01','end':'1990-10-31'}},
         {'seasonal_playback_eligible':True},{'width_rank_eligible':True},
         {'current_id':'equatorial-undercurrent','original_regional_context':{}}]

@pytest.mark.parametrize('change',CHANGES)
def test_promoted_support_rejected(change):
    r=copy.deepcopy(record());r.update(change)
    with pytest.raises(ValueError):validate_row(r)

@pytest.mark.parametrize('key,value',[('nominal_depth_is_fixed_layer',True),('geographic_view_role','observed_current_footprint'),('subset_counts_additive',True),('gap_means_current_absent',True)])
def test_context_scope_rejected(key,value):
    r=copy.deepcopy(record());r['original_regional_context'][key]=value
    with pytest.raises(ValueError):validate_row(r)

def check_native_guard(directory):
    packet=json.loads((ROOT/'almanac/query-data.json').read_bytes());targets=[]
    for i,change in enumerate(CHANGES+[None]):
        bad=copy.deepcopy(packet);receipt=bad['manifest']['seasons_receipts']['widths'];source=json.loads(receipt['source_json'])
        for rows in [source['measurements'],bad['collections']['widths']]:
            r=next(r for r in rows if r['id']==record()['id'])
            if change is None:rows.remove(r)
            else:r.update(change)
        if change is None:
            missing=record()['id']
            for r in bad['collections']['objects']:
                if missing in r.get('width_ids',[]):r['width_ids'].remove(missing)
            dashboard=bad['manifest']['dashboard_receipt'];doc=json.loads(dashboard['source_json'])
            for r in doc['entries']:
                if missing in r.get('width_ids',[]):r['width_ids'].remove(missing)
            dashboard['source_json']=json.dumps(doc,ensure_ascii=False)
            dashboard['source_sha256']=hashlib.sha256(dashboard['source_json'].encode()).hexdigest()
            bad['manifest']['input_sha256'][dashboard['source_file']]=dashboard['source_sha256']
            for r in source['current_decisions']:
                if missing in r.get('measurement_ids',[]):r['measurement_ids'].remove(missing)
        receipt['source_json']=json.dumps(source,ensure_ascii=False)
        receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest()
        bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
        target=directory/f'dwbc-tampered-{i}.json';target.write_text(json.dumps(bad,ensure_ascii=False),encoding='utf8')
        result=subprocess.run([str(CLI),str(target),'--seasons'],capture_output=True,text=True,encoding='utf8')
        error='DWBC float composite inventory' if change is None else 'Original regional width'
        assert result.returncode==2 and error in result.stderr,result.stderr
        targets.append(target)
    return targets

def test_coherent_native_scope_rejection(tmp_path):check_native_guard(tmp_path)

def test_native_source_scene_and_combined_comparisons():
    query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'deep-western-boundary'}]}
    r=native(query);assert r['ok'] and r['total']==1
    scene=r['chart_scene'];assert scene['kind']=='dwbc_float_composite'
    assert scene['geographic_view']['extent_lon_lat']==[-55,-5,-10,15]
    assert scene['geographic_view']['role']=='figure_viewport_context_only'
    assert len(scene['panels'])==2 and len(scene['table'])==4
    assert scene['panels'][0]['points'][1]['standard_error']==5
    all_widths=native({'collection':'widths','limit':1})
    assert all_widths['chart_scene']['kind']=='scoped_width_comparisons'
    assert [s['kind'] for s in all_widths['chart_scene']['scenes']]==['coastal_composite_widths','dwbc_float_composite','pacific_neuc_isopycnal_breadths']
