"""Source definitions, complete spatial context and coherent native guards."""
import copy,hashlib,json,subprocess
import pytest
from check_antarctic_coastal_composites import ROOT,validate_row
from test_rust_query_browser import CLI,native

def records():
    return [r for r in json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())['measurements'] if r['current_id']=='antarctic-coastal']

def test_source_properties_and_scope():
    rows=records()
    assert [r['approximate_width_km'] for r in rows]==[28.4,23.8,75.1,60.9,89.8,160.9,111.9]
    assert [(r['original_regional_context']['source_properties']['winter_profiles'],r['original_regional_context']['source_properties']['summer_profiles']) for r in rows]==[(183,221),(494,67),(1040,145),(753,243),(348,168),(117,150),(147,59)]
    for row in rows:
        validate_row(row)
        c=row['original_regional_context'];p=c['source_properties']
        assert c['offshore_edge_fraction_of_center_integrated_velocity']==.15
        assert c['geostrophic_reference_depth_m']==400 and c['integration_base_salinity_psu']==34.4
        assert p['total_profiles']==p['winter_profiles']+p['summer_profiles']
        assert row['calendar_months'] is None and row['fixed_layer_bounds_m'] is None
    assert rows[5]['original_regional_context']['sampling_prose_discrepancy'] is True

CHANGES=[{'width_range_km':[23.8,160.9]},{'fixed_layer_bounds_m':[0,400]},
         {'calendar_months':[4,5,6,7,8,9]},{'uncertainty_km':4},
         {'observed_period':{'start':'2005-01-01','end':'2015-06-30'}},
         {'seasonal_playback_eligible':True},{'width_rank_eligible':True},
         {'original_regional_context':{},'current_id':'antarctic-slope'}]

@pytest.mark.parametrize('change',CHANGES)
def test_promoted_support_rejected(change):
    row=copy.deepcopy(records()[5]);row.update(change)
    with pytest.raises(ValueError):validate_row(row)

@pytest.mark.parametrize('key,value',[('offshore_edge_fraction_of_center_integrated_velocity',.1),('integration_base_is_fixed_depth',True),('sampling_prose_discrepancy',False)])
def test_context_relabeling_rejected(key,value):
    row=copy.deepcopy(records()[5]);row['original_regional_context'][key]=value
    with pytest.raises(ValueError):validate_row(row)

def check_native_guard(directory):
    packet=json.loads((ROOT/'almanac/query-data.json').read_bytes());targets=[]
    for i,change in enumerate(CHANGES+[None]):
        bad=copy.deepcopy(packet);receipt=bad['manifest']['seasons_receipts']['widths'];source=json.loads(receipt['source_json'])
        for rows in [source['measurements'],bad['collections']['widths']]:
            target=next(r for r in rows if r['id']==records()[5]['id'])
            if change is None:rows.remove(target)
            else:target.update(change)
        if change is None:
            missing=records()[5]['id']
            # Remove all dependent joins and refresh their source receipts too.
            for row in bad['collections']['objects']:
                if missing in row.get('width_ids',[]):row['width_ids'].remove(missing)
            dashboard=bad['manifest']['dashboard_receipt'];doc=json.loads(dashboard['source_json'])
            for row in doc['entries']:
                if missing in row.get('width_ids',[]):row['width_ids'].remove(missing)
            dashboard['source_json']=json.dumps(doc,ensure_ascii=False)
            dashboard['source_sha256']=hashlib.sha256(dashboard['source_json'].encode()).hexdigest()
            bad['manifest']['input_sha256'][dashboard['source_file']]=dashboard['source_sha256']
            for row in source['current_decisions']:
                if missing in row.get('measurement_ids',[]):row['measurement_ids'].remove(missing)
        receipt['source_json']=json.dumps(source,ensure_ascii=False)
        receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest()
        bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
        target=directory/f'coastal-tampered-{i}.json';target.write_text(json.dumps(bad,ensure_ascii=False),encoding='utf8')
        result=subprocess.run([str(CLI),str(target),'--seasons'],capture_output=True,text=True,encoding='utf8')
        expected='Coastal composite seven-section' if change is None else 'Original regional width'
        assert result.returncode==2 and expected in result.stderr,result.stderr
        targets.append(target)
    return targets

def test_coherent_native_scope_rejection(tmp_path):check_native_guard(tmp_path)

def test_filtered_scene_retains_source_context():
    result=native({'collection':'widths','filters':[{'field':'id','op':'eq','value':records()[5]['id']}],'limit':1})
    assert result['ok'] and result['total']==1
    scene=result['chart_scene'];assert len(scene['bars'])==7 and scene['axis_max_km']==175
    assert [b['section_number'] for b in scene['bars'] if b['matching']]==[6]
    assert scene['source_image']['pixel_dimensions']==[1474,912]
