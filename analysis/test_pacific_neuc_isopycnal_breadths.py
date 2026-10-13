"""Keep distinct components, isopycnals and climatologies separate."""
import copy,hashlib,json,subprocess
import pytest
from check_pacific_neuc_isopycnal_breadths import document,records,validate_row,AUDIT
from test_rust_query_browser import ROOT,CLI,native

def test_source_breadths_and_density_support():
    rows=records();assert [r['approximate_width_km'] for r in rows]==[330,110]
    assert [r['original_regional_context']['source_reported_latitude_span_degrees'] for r in rows]==[3,1]
    assert document()['middle_component']['width_km'] is None
    for r in rows:
        validate_row(r);assert r['fixed_layer_bounds_m'] is None and r['width_range_km'] is None
        assert r['original_regional_context']['source_mean_years']==[2004,2014]
        assert r['original_regional_context']['sigma_theta_anomaly_kg_m3']==27.0

CHANGES=[{'width_range_km':[110,330]},{'uncertainty_km':10},{'fixed_layer_bounds_m':[300,600]},
         {'calendar_months':[1,2,3,4]},{'seasonal_playback_eligible':True},{'width_rank_eligible':True},
         {'current_id':'north-equatorial-undercurrent','original_regional_context':{}}]
@pytest.mark.parametrize('change',CHANGES)
def test_dimension_or_identity_promotions_rejected(change):
    r=records()[0];r.update(change)
    with pytest.raises(ValueError):validate_row(r)

def fixtures(directory):
    packet=json.loads((ROOT/'almanac/query-data.json').read_bytes());targets=[]
    cases=CHANGES+[{'original_regional_context':{}},{'original_regional_context':{**records()[0]['original_regional_context'],'sigma_theta_anomaly_kg_m3':26.8}},None,'proof']
    for i,change in enumerate(cases):
        bad=copy.deepcopy(packet);receipt=bad['manifest']['seasons_receipts']['widths'];doc=json.loads(receipt['source_json'])
        for rows in [doc['measurements'],bad['collections']['widths']]:
            r=next(r for r in rows if r['id']==records()[0]['id'])
            if change is None or change=='proof':rows.remove(r)
            else:r.update(change)
        if change=='proof':
            for rows in [doc['measurements'],bad['collections']['widths']]:rows[:]=[r for r in rows if r['id']!=records()[1]['id']]
            del bad['manifest']['input_sha256'][AUDIT]
        receipt['source_json']=json.dumps(doc,ensure_ascii=False);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest();bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
        target=directory/f'neuc-breadth-{i}.json';target.write_text(json.dumps(bad,ensure_ascii=False),encoding='utf8')
        result=subprocess.run([str(CLI),str(target),'--seasons'],capture_output=True,text=True,encoding='utf8')
        assert result.returncode==2 and 'Pacific NEUC breadth' in result.stderr,result.stderr
        targets.append(target)
    return targets

def test_native_scope_rejections(tmp_path):fixtures(tmp_path)

def test_native_complete_context_for_filtered_component():
    result=native({'collection':'widths','filters':[{'field':'id','op':'eq','value':records()[1]['id']}]})
    assert result['total']==1
    scene=result['chart_scene'];assert scene['kind']=='pacific_neuc_isopycnal_breadths'
    assert len(scene['records'])==2 and scene['matching_ids']==[records()[1]['id']]
    assert scene['geometry_role']=='abstract_component_comparison_no_edges_or_footprint'
    for owner in ['north-equatorial-undercurrent','pacific-north-equatorial-undercurrent']:
        r=native({'collection':'objects','filters':[{'field':'id','op':'eq','value':'current:'+owner}]})['rows'][0]
        assert r['capabilities']['scoped_width']==(2 if owner.startswith('pacific-') else 0)
        assert r['capabilities']['time_samples']==0 and r['capabilities']['observed_velocity']==0
