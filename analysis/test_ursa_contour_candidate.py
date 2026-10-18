"""Dated image proxy, failed cases and scientific scope must survive every view."""
import copy
import hashlib
import json
import subprocess
from pathlib import Path
import pytest
from build_ursa_contour_candidate import ROOT, PATH, validate
from test_rust_query_browser import CLI

OWNER = 'eddy:published:ursa-2021'
ID = 'footprint_candidate:ursa:2021-03-07'

def document():
    return json.loads((ROOT / PATH).read_bytes())

def test_original_trace_calibration_and_failures():
    d = validate(document())
    assert d['scenario_polygon_count'] == 68 and d['scenario_attempt_count'] == 102
    assert len(d['rejected_segmentation_cases']) == 2
    assert all(r['geometry'] is None and r['source_pixel_ring'] for r in d['rejected_segmentation_cases'])
    assert d['source_panel_axes_pixels'] == [1121,1383,674,894]
    assert d['axis_values_lon_lat'] == [-89,-85,28,25]
    # Independent calibration of the source vertices, including latitude tick below 28.
    for pixel, geographic in zip(d['source_pixel_ring'],d['nominal_geometry']['coordinates'][0]):
        assert geographic == [round(-89+(pixel[0]-1121)*4/262,7),round(28-(pixel[1]-674)*3/220,7)]
    assert {a['state_id'] for a in d['state_assessments']} == {'state:CAMR','state:CARB'}
    assert not d['physical_boundary_admitted'] and d['whole_eddy_state_relations'] == []

@pytest.mark.parametrize('key,value',[
    ('observation_date','2021-03-08'),('physical_boundary_admitted',True),
    ('annual_extrema_eligible',True),('seasonal_playback_eligible',True),
    ('rejected_segmentation_cases',[]),('scenario_polygon_count',102),
])
def test_source_audit_mutations_rejected(key,value):
    d=document();d[key]=value
    with pytest.raises(ValueError,match='Ursa contour'): validate(d)

def fixtures(directory,retain=True):
    source=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    targets=[]
    for kind in ['date','owner','geometry','physical','annual','unit','failures','missing_proof','missing_candidate','image','state']:
        b=copy.deepcopy(source);r=b['manifest']['atlas_receipts'][PATH]
        candidate=next(x for x in b['collections']['named_eddy_footprint_candidates'] if x['id']==ID)
        if kind=='date':candidate['observation_date']='2021-03-08'
        elif kind=='owner':candidate['entity_id']='eddy:loop:ursa'
        elif kind=='geometry':next(x for x in b['collections']['geometries'] if x['id']==candidate['geometry_id'])['geometry']['coordinates'][0][0][0]+=0.01
        elif kind=='physical':candidate['physical_boundary_admitted']=True
        elif kind=='annual':candidate['seasonal_playback_eligible']=True
        elif kind=='missing_proof':del b['manifest']['atlas_receipts'][PATH]
        elif kind=='missing_candidate':b['collections']['named_eddy_footprint_candidates'].remove(candidate)
        elif kind=='image':b['manifest']['input_sha256'][document()['source_image_file']]='0'*64
        elif kind=='state':next(x for x in b['collections']['named_eddy_state_assessments'] if x.get('footprint_candidate_id')==ID)['physical_relation']='contained'
        else:
            doc=json.loads(r['source_json'])
            if kind=='unit':doc['contour_definition']['normalized_contour_value_m']=0.65
            else:doc['rejected_segmentation_cases']=[]
            raw=json.dumps(doc);sha=hashlib.sha256(raw.encode()).hexdigest()
            r.update(source_json=raw,source_sha256=sha);b['manifest']['input_sha256'][PATH]=sha
        path=directory/('ursa-contour-'+kind+'.json');path.write_bytes(json.dumps(b).encode())
        result=subprocess.run([str(CLI),str(path)],capture_output=True,text=True,encoding='utf8')
        assert result.returncode==2 and ('Thor/Ursa panels: changed original figure dependency' if kind=='image' else 'Ursa contour') in result.stderr,(kind,result.stderr)
        targets.append(path)
        if not retain:path.unlink()
    return targets

def test_native_proof_and_atlas_object_parity(tmp_path):
    fixtures(tmp_path,retain=False)
    atlas=json.loads(subprocess.check_output([str(CLI),str(ROOT/'almanac/query-data.json'),'--atlas'],encoding='utf8'))
    obj=json.loads(subprocess.check_output([str(CLI),str(ROOT/'almanac/query-data.json'),'--object-view',OWNER],encoding='utf8'))
    assert obj['footprint_plots'][ID]==atlas['footprint_views'][OWNER]['plot_scene']
    overlay=obj['footprint_plots'][ID]['source_panel_overlay']
    assert overlay['view_box']==[1120,642,264,288]
    assert overlay['polygon_d'].startswith('M') and overlay['polygon_d'].endswith('Z')
    assert all(r['temporal_alignment_status']=='year_in_range_event_alignment_unresolved' and r['event_identity_status']=='not_established' for r in atlas['footprint_views'][OWNER]['movie_contexts'])
