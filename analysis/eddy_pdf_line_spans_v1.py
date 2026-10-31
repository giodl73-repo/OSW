"""Source-native PDF line spans; no ocean field, physical footprint or date inference."""
import hashlib
import json
from pathlib import Path
from eddy_map_spans_v1 import span_interval


def validate_case(c):
    assert c['method']=='source_native_pdf_frontal_line_spans_v1'
    assert c['owner_id']=='eddy:horizon:loop-77-primary' and c['source_name']=='Berek'
    assert c['background_ssh_date']=='2023-12-21' and c['contour_observation_date'] is None
    assert c['source_legend_speed_knots']==1.5
    assert c['coordinate_system']=='PDF points, equivalent to pixels in a 72 dpi rendering'
    assert c['reading_allowance_pixels']==c['reading_allowance_pdf_points']==6
    assert c['earth_radius_km']==6371 and c['round_outward_km']==25
    assert all(c[k] is False for k in ['association_is_verified','physical_state_join_eligible','physical_footprint_admitted','rights_screened_release_eligible','missing_segments_reconstructed','background_date_is_contour_date'])
    p=c['native_path'];assert (p['pdf_page'],p['drawing_index'],p['sequence_number'])==(1,217,254)
    assert p['stroke_rgb']==[0,0,0] and p['stroke_width_pdf_points']==8 and p['fill'] is None
    assert p['segments']==3500 and p['segment_types']==['l'] and p['chain_breaks']==0
    assert p['explicit_endpoint_closure_verified'] is True and p['pdf_close_path_flag'] is False
    assert p['original_pdf_sha256']=='66f70c2f3ef2da78affa0d737b950a4a1e2dfcddfda09921a6dd369d103ed1e1'
    assert p['points_sha256']=='bd9209b10d48f8f4b7aa93302bde1767aa852dcde738d802945fef3a08f0b730'
    extrema=p['directional_extrema'];assert set(extrema)=={'west','east','north','south'}
    assert c['outline']['bbox_xyxy']==[extrema['west']['point'][0],extrema['north']['point'][1],extrema['east']['point'][0],extrema['south']['point'][1]]
    for v in extrema.values():assert 0<=v['index']<=3500 and len(v['point'])==2
    assert c['axis_method']=='Piecewise linear interpolation between published tick-label centers; no projection or source-field accuracy inferred.'
    assert len(c['axis_label_boxes'])==10
    for dimension,ending,axis_index in [('longitude','W',0),('latitude','N',1)]:
        rows=[r for r in c['axis_label_boxes'] if r['text'].endswith(ending)]
        anchors=sorted([[(r['bbox'][axis_index]+r['bbox'][axis_index+2])/2,(-1 if ending=='W' else 1)*int(r['text'].split('°')[0])] for r in rows])
        assert c['axes'][dimension]==anchors
    for component in ['east_west','north_south']:span_interval(c,component)


def verify_source(pdf,batch_path):
    # Modest source-document parsing only; never ocean-field or runtime processing.
    from verify_eddy_plot_source_v1 import constrain
    constrain()
    import pymupdf
    b=json.loads(batch_path.read_bytes());c=b['pdf_line_cases'][0];validate_case(c)
    original=b['sources']['bower-2024']['original'];raw=pdf.read_bytes()
    assert len(raw)==original['bytes']==16648659 and hashlib.sha256(raw).hexdigest()==original['sha256']
    with pymupdf.open(stream=raw,filetype='pdf') as doc:
        assert len(doc)==original['pages']==1
        page=doc[0];d=page.get_drawings()[c['native_path']['drawing_index']];items=d['items']
        assert d['seqno']==254 and len(items)==3500 and all(i[0]=='l' for i in items)
        assert d['color']==(0,0,0) and d['width']==8 and d['fill'] is None and d['closePath'] is False
        assert all(items[n-1][2]==items[n][1] for n in range(1,len(items)))
        points=[list(items[0][1])]+[list(i[2]) for i in items];assert points[0]==points[-1]
        assert hashlib.sha256(json.dumps(points,separators=(',',':')).encode()).hexdigest()==c['native_path']['points_sha256']
        for direction,axis,sign in [('west',0,1),('east',0,-1),('north',1,1),('south',1,-1)]:
            index=min(range(len(points)),key=lambda i:sign*points[i][axis])
            assert c['native_path']['directional_extrema'][direction]=={'index':index,'point':points[index]}
        assert list(d['rect'])==c['outline']['bbox_xyxy']
        words=[{'bbox':list(w[:4]),'text':w[4]} for w in page.get_text('words') if any(s in w[4] for s in ['96°W','92°W','88°W','84°W','80°W','30°N','27°N','24°N','21°N','18°N']) and 630<w[0]<3200 and 400<w[1]<2300]
        assert words==c['axis_label_boxes']
        text=page.get_text();assert 'Eddy Berek' in text and '21 December 2023' in text and '1.5-knot' in text
    return {'schema':'osw.eddy-pdf-line-source-verification.v1','status':'PASS','original_pdf_sha256':original['sha256'],'batch_sha256':hashlib.sha256(batch_path.read_bytes()).hexdigest(),'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'span_math_sha256':hashlib.sha256((Path(__file__).parent/'eddy_map_spans_v1.py').read_bytes()).hexdigest(),'source_native_path_verified':True,'source_axis_labels_verified':True,'explicit_endpoint_closure_verified':True,'chain_breaks':0,'missing_segments_reconstructed':False,'physical_footprint_admitted':False,'contour_observation_date':None,'original_assets_republished':False,'spans':{component:span_interval(c,component) for component in ['east_west','north_south']},'runtime_changed':False}


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--pdf',type=Path,required=True);parser.add_argument('--batch',type=Path,required=True);parser.add_argument('--result',type=Path,required=True)
    args=parser.parse_args();result=verify_source(args.pdf,args.batch);args.result.write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps(result))
