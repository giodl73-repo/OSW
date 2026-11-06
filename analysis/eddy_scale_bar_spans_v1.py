"""Source-image scale-bar equivalents; no geodesic or physical boundary inference."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import statistics


def ink(samples,width,height,roi,gate):
    assert len(samples)==width*height*3 and gate in [75,100]
    x0,y0,x1,y1=roi;assert 0<=x0<x1<width and 0<=y0<y1<height
    return {(x,y) for y in range(y0,y1+1) for x in range(x0,x1+1) if max(samples[(y*width+x)*3:(y*width+x)*3+3])<=gate}


def loop_readout(samples,width,height,roi,gate):
    remaining=ink(samples,width,height,roi,gate);components=[]
    while remaining:
        p=min(remaining);remaining.remove(p);selected={p};todo=[p]
        while todo:
            x,y=todo.pop()
            for dx,dy in itertools.product([-1,0,1],repeat=2):
                q=(x+dx,y+dy)
                if q in remaining:remaining.remove(q);selected.add(q);todo.append(q)
        components.append(selected)
    components.sort(key=lambda c:(-len(c),min(c)));selected=components[0]
    assert len(selected)>800 and (len(components)==1 or len(selected)>3*len(components[1]))
    bbox=[min(x for x,y in selected),min(y for x,y in selected),max(x for x,y in selected),max(y for x,y in selected)]
    x0,y0,x1,y1=roi;assert x0<bbox[0]<bbox[2]<x1 and y0<bbox[1]<bbox[3]<y1
    border={(x,y) for x in range(x0,x1+1) for y in [y0,y1]}|{(x,y) for x in [x0,x1] for y in range(y0,y1+1)}
    outside=border-selected;todo=list(outside)
    while todo:
        x,y=todo.pop()
        for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            q=(x+dx,y+dy)
            if x0<=q[0]<=x1 and y0<=q[1]<=y1 and q not in selected and q not in outside:outside.add(q);todo.append(q)
    enclosed=(x1-x0+1)*(y1-y0+1)-len(outside)-len(selected);assert enclosed>1000
    return {'maximum_rgb_channel':gate,'bbox_xyxy':bbox,'selected_pixels':len(selected),'selected_pixels_sha256':hashlib.sha256(json.dumps(sorted(selected),separators=(',',':')).encode()).hexdigest(),'enclosed_background_pixels':enclosed,'other_component_sizes':[len(c) for c in components[1:]]}


def spans(c,component):
    assert component in ['horizontal','vertical']
    intervals=[];axis=0 if component=='horizontal' else 1
    for r in c['readings']:
        ticks=r['ticks'];assert [t['value_km'] for t in ticks]==[0,100,200,300]
        for d0,d1 in itertools.product([-2,2],repeat=2):
            scale=300/(ticks[-1]['coordinate_x']+d1-ticks[0]['coordinate_x']-d0)
            b=r['outline']['bbox_xyxy'];extent=b[axis+2]-b[axis]
            intervals.append([(extent-12)*scale,(extent+12)*scale])
    lo,hi=min(r[0] for r in intervals),max(r[1] for r in intervals)
    nominal=next(r for r in c['readings'] if r['outline']['maximum_rgb_channel']==100)
    b=nominal['outline']['bbox_xyxy'];ticks=nominal['ticks']
    return {'audit_scale_bar_equivalent_km':round((b[axis+2]-b[axis])*300/(ticks[-1]['coordinate_x']-ticks[0]['coordinate_x']),6),'audit_reading_interval_km':[round(lo,6),round(hi,6)],'range_km':[math.floor(lo/25)*25,math.ceil(hi/25)*25],'total_scenarios':len(intervals),'systematic_projection_error_quantified':False}


def validate_case(c):
    assert c['method']=='source_image_scale_bar_equivalent_spans_v1'
    assert c['owner_id']=='eddy:horizon:loop-71-primary' and c['source_name']=='Verne' and c['date']=='2021-11-23'
    assert c['coordinate_system']=='source_image_pixels_scale_bar_equivalent_not_geodesic'
    assert c['scale_bar_km']==300 and c['reading_allowance_pixels']==6 and c['axis_sensitivity_pixels']==2 and c['round_outward_km']==25
    assert c['roi_xyxy_inclusive']==[85,345,181,429]
    assert all(c[k] is False for k in ['projection_known','contour_threshold_known','geodesic_distance_inferred','physical_footprint_admitted','physical_state_join_eligible','association_is_verified','rights_screened_release_eligible','missing_ink_reconstructed'])
    assert c['source_raster']=={'width':800,'height':640,'components':3,'samples_sha256':'c5e0725e0cd1d0a771a979aaa928544f970ffe2d8026fd8b1b43385adebda941'}
    assert len(c['readings'])==2 and {r['outline']['maximum_rgb_channel'] for r in c['readings']}=={75,100}
    for r in c['readings']:
        assert r['outline']['selected_pixels']>800 and r['outline']['enclosed_background_pixels']>1000
        assert [t['value_km'] for t in r['ticks']]==[0,100,200,300]
        for t in r['ticks']:assert t['window_xyxy'][0]<t['coordinate_x']<t['window_xyxy'][2]
        a,b=r['ticks'][0]['coordinate_x'],r['ticks'][-1]['coordinate_x']
        assert all(abs(t['coordinate_x']-(a+(b-a)*t['value_km']/300))<=1 for t in r['ticks'])
    for component in ['horizontal','vertical']:spans(c,component)


def read_case(samples,width,height):
    rows=[]
    for gate in [75,100]:
        ticks=[]
        for value,roi in [(0,[635,579,645,583]),(100,[674,579,685,583]),(200,[713,579,724,583]),(300,[752,579,763,583])]:
            p=ink(samples,width,height,roi,gate)
            ticks.append({'value_km':value,'window_xyxy':roi,'coordinate_x':statistics.median(x for x,y in p),'ink_pixels':len(p),'pixels_sha256':hashlib.sha256(json.dumps(sorted(p),separators=(',',':')).encode()).hexdigest()})
        rows.append({'outline':loop_readout(samples,width,height,[85,345,181,429],gate),'ticks':ticks})
    return rows


def verify_source(source,batch_path):
    from verify_eddy_plot_source_v1 import constrain
    constrain()
    from PIL import Image
    b=json.loads(batch_path.read_bytes());c=b['scale_bar_cases'][0];validate_case(c);original=b['sources']['cls-2021']['chart']
    raw=source.read_bytes();assert len(raw)==original['bytes']==103919 and hashlib.sha256(raw).hexdigest()==original['sha256']
    with Image.open(source) as im:
        im=im.convert('RGB');samples=im.tobytes();assert list(im.size)==original['dimensions']==[800,640]
        assert hashlib.sha256(samples).hexdigest()==c['source_raster']['samples_sha256'] and read_case(samples,*im.size)==c['readings']
    return {'schema':'osw.eddy-scale-bar-source-verification.v1','status':'PASS','original_chart_sha256':original['sha256'],'batch_sha256':hashlib.sha256(batch_path.read_bytes()).hexdigest(),'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_pixels_verified':True,'manual_name_date_and_curve_selection_required':True,'missing_ink_reconstructed':False,'physical_footprint_admitted':False,'spans':{component:spans(c,component) for component in ['horizontal','vertical']},'runtime_changed':False}
