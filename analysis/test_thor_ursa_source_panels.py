"""Protect dated event context against geometry and climatology promotion."""
import copy,hashlib,json,subprocess
from pathlib import Path
import pytest
from build_thor_ursa_source_panels import ROOT,PATH,validate
from test_rust_query_browser import CLI

def document():
    return json.loads((ROOT/PATH).read_bytes())

def test_original_panels_keep_event_dates_and_unknown_geometry():
    d=validate(document())
    assert [e['panel_count'] for e in d['events']]==[25,25]
    assert d['new_closed_footprint_count']==0
    assert [e['panels'][-1]['observation_date'] for e in d['events']]==['2020-06-29','2021-05-01']
    for e in d['events']:
        for p in e['panels']:
            assert p['geometry_lon_lat'] is None and p['physical_state_relations']==[]
            assert p['center_lon_lat'] is None and not p['seasonal_playback_eligible']

@pytest.mark.parametrize('key,value',[
    ('observation_date','2021-03-08'),('geometry_lon_lat',{'type':'Polygon','coordinates':[]}),
    ('physical_state_relations',['CAMR']),('annual_extrema_eligible',True),
    ('seasonal_playback_eligible',True),('ring_identity_from_panel_alone',True),
])
def test_source_scope_cannot_be_promoted(key,value):
    d=document();d['events'][1]['panels'][13][key]=value
    with pytest.raises(ValueError,match='Thor/Ursa'):validate(d)

def fixtures(directory):
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes());targets=[]
    for kind in ['date','owner','crop','geometry','unit','annual','missing_proof','xml','figure']:
        bad=copy.deepcopy(bundle);receipt=bad['manifest']['atlas_receipts'][PATH]
        d=json.loads(receipt['source_json'])
        if kind=='missing_proof':del bad['manifest']['atlas_receipts'][PATH]
        elif kind in ['xml','figure']:
            file=d['source_document_file'] if kind=='xml' else d['events'][0]['source_image_file']
            bad['manifest']['input_sha256'][file]='0'*64
        else:
            p=d['events'][1]['panels'][13]
            if kind=='date':p['observation_date']='2021-03-08'
            elif kind=='owner':d['events'][1]['entity_id']='eddy:loop:ursa'
            elif kind=='crop':p['crop_pixels_xywh'][0]=0
            elif kind=='geometry':p['geometry_lon_lat']={'type':'Polygon','coordinates':[[[0,0],[1,1],[1,0],[0,0]]]}
            elif kind=='unit':d['contour_definition']['normalized_contour_value_m']=0.65
            elif kind=='annual':p['seasonal_playback_eligible']=True
            raw=json.dumps(d);sha=hashlib.sha256(raw.encode()).hexdigest()
            receipt.update(source_json=raw,source_sha256=sha);bad['manifest']['input_sha256'][PATH]=sha
        file=directory/('eddy-panels-'+kind+'.json');file.write_bytes(json.dumps(bad).encode())
        r=subprocess.run([str(CLI),str(file)],capture_output=True,text=True,encoding='utf8')
        assert r.returncode==2 and 'Thor/Ursa panels' in r.stderr,(kind,r.stderr)
        targets.append(file)
    return targets

def test_native_guard_and_shared_views(tmp_path):
    fixtures(tmp_path)
    atlas=json.loads(subprocess.check_output([str(CLI),str(ROOT/'almanac/query-data.json'),'--atlas'],encoding='utf8'))
    for event in document()['events']:
        obj=json.loads(subprocess.check_output([str(CLI),str(ROOT/'almanac/query-data.json'),'--object-view',event['entity_id']],encoding='utf8'))
        assert obj['source_panel_scene']==atlas['eddy_source_panel_scenes'][event['entity_id']]
        assert obj['source_panel_scene']['panels']==event['panels']
    assert len(atlas['eddy_source_panel_scenes'])==2
