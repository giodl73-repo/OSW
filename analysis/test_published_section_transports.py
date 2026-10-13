"""Preserve unequal statistical, depth, identity and sampling support."""
import copy,json,subprocess
from pathlib import Path
from published_section_transports import document,build,SOURCE
from test_rust_query_browser import ROOT,CLI,native

def test_original_table_support():
    d=document();rows=build(d);m=rows['section_transports'];v=rows['transport_validations']
    assert len(m)==35 and len(v)==6
    assert sum(r['current_id'] is None for r in m)==15
    assert all(r['standard_error_sv'] is None and r['geometry'] is None for r in m)
    assert next(r for r in m if r['section_id']=='H-1')['fixed_layer_bounds_m']==[0,2000]
    assert all(r['fixed_layer_bounds_m'] is None for r in m if r['section_id'].startswith('W-'))
    assert v[0]['simulation']['direction']=='S' and v[0]['source_direction_discrepancy']
    assert v[5]['source_month_count']==18 and v[5]['period_count_discrepancy']
    assert all(not r['exact_matched_month_mask_supplied'] for r in v)

def test_native_scene_and_owner_scope():
    for c,n in [('section_transports',35),('transport_validations',6)]:
        result=native({'collection':c,'limit':1})
        assert result['ok'] and result['total']==n
        assert len(result['chart_scene']['model_records' if c=='section_transports' else 'validation_records'])==n
    r=native({'collection':'section_transports','filters':[{'field':'current_id','op':'eq','value':'hiri-current'}]})
    s=r['chart_scene'];assert s['points'][0]['record']['value_sv']==6.9
    assert s['geographic_view']['role']=='partial_coordinate_context_not_section_geometry'
    owner=native({'collection':'objects','filters':[{'field':'id','op':'eq','value':'current:hiri-current'}]})['rows'][0]
    assert owner['capabilities']['section_transport']==1
    assert owner['capabilities']['scoped_width']==0 and owner['capabilities']['time_samples']==0

def guard_fixtures(directory):
    packet=json.loads((ROOT/'almanac/query-data.json').read_bytes());targets=[]
    for case in ['mean','spread','layer','direction','months','identity','missing','dependency','capability','proof']:
        bad=copy.deepcopy(packet);m=bad['collections']['section_transports'];v=bad['collections']['transport_validations']
        h=next(r for r in m if r['current_id']=='hiri-current')
        if case=='mean':h['value_sv']=7
        elif case=='spread':h['standard_error_sv']=4.9
        elif case=='layer':h['fixed_layer_bounds_m']=[0,300]
        elif case=='direction':v[0]['simulation']['direction']='W'
        elif case=='months':v[5]['source_month_count']=17
        elif case=='identity':next(r for r in m if r['source_current_label']=='Holloway Current').update(current_id='leeuwin',entity_id='current:leeuwin')
        elif case=='missing':del bad['collections']['section_transports']
        elif case=='dependency':bad['manifest']['input_sha256'][document()['protocol_file']]='0'*64
        elif case=='proof':
            del bad['manifest']['input_sha256'][SOURCE]
            del bad['collections']['section_transports']
            del bad['collections']['transport_validations']
        else:next(r for r in bad['collections']['objects'] if r['id']=='current:hiri-current')['capabilities']['section_transport']=0
        target=directory/f'transport-{case}.json';target.write_text(json.dumps(bad,ensure_ascii=False),encoding='utf8')
        p=subprocess.run([str(CLI),str(target),'--seasons'],capture_output=True,text=True,encoding='utf8')
        assert p.returncode==2 and 'Published section transport' in p.stderr,(case,p.stderr)
        targets.append(target)
    return targets

def test_native_scope_guards(tmp_path):guard_fixtures(tmp_path)
