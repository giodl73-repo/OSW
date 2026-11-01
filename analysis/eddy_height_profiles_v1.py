"""Reproduce selected source-plot ink readings, never whole-eddy boundaries."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import statistics
from eddy_map_spans_v1 import axis_value


def ink(samples,width,height,window,gate):
    assert len(samples)==width*height*3 and gate in [75,100]
    x0,y0,x1,y1=window;assert 0<=x0<x1<width and 0<=y0<y1<height
    return [(x,y) for y in range(y0,y1+1) for x in range(x0,x1+1) if max(samples[(y*width+x)*3:(y*width+x)*3+3])<=gate]


def span(c):
    anchors=sorted([[t['coordinate'],t['value']] for t in c['ticks'] if t['axis']=='latitude'])
    assert [a[1] for a in anchors]==[23,24,25,26,27,28]
    km_per_degree=6371*math.pi/180;pad=6;intervals=[]
    for row in c['crossings']:
        s,n=[row['crossings'][side]['x_range'] for side in ['south','north']]
        for shifts in itertools.product([-2,2],repeat=6):
            a=[[x+shift,value] for (x,value),shift in zip(anchors,shifts)]
            intervals.append([(axis_value(n[0]-pad,a)-axis_value(s[1]+pad,a))*km_per_degree,
                              (axis_value(n[1]+pad,a)-axis_value(s[0]-pad,a))*km_per_degree])
    nominal=next(r for r in c['crossings'] if r['height_m']==.3 and r['maximum_rgb_channel']==100)
    s,n=[statistics.mean(nominal['crossings'][side]['x_range']) for side in ['south','north']]
    lo,hi=min(r[0] for r in intervals),max(r[1] for r in intervals)
    assert 0<lo<hi
    return {'audit_span_km':round((axis_value(n,anchors)-axis_value(s,anchors))*km_per_degree,6),
            'audit_reading_interval_km':[round(lo,6),round(hi,6)],'range_km':[math.floor(lo/25)*25,math.ceil(hi/25)*25],
            'axis_scenarios_per_level_gate':64,'level_gate_cases':6,'total_scenarios':len(intervals),'height_levels_m':[.25,.3,.35]}


def peak(c):
    zero=next(t['coordinate'] for t in c['ticks'] if t['axis']=='height' and t['value']==0)
    half=next(t['coordinate'] for t in c['ticks'] if t['axis']=='height' and t['value']==.5)
    intervals=[]
    for p in c['peaks']:
        for dz,dh in itertools.product([-2,2],repeat=2):
            z,h=zero+dz,half+dh
            intervals.append([.5*(z-(p['minimum_y_pixel']+6))/(z-h),.5*(z-(p['minimum_y_pixel']-6))/(z-h)])
    lo,hi=min(r[0] for r in intervals),max(r[1] for r in intervals)
    nominal=next(p['minimum_y_pixel'] for p in c['peaks'] if p['maximum_rgb_channel']==100)
    return {'audit_height_m':round(.5*(zero-nominal)/(zero-half),6),'audit_reading_interval_m':[round(lo,6),round(hi,6)],
            'range_m':[round(math.floor(lo/.05)*.05,6),round(math.ceil(hi/.05)*.05,6)],'total_scenarios':len(intervals)}


def validate_case(c):
    assert c['method']=='source_height_profile_readings_v1'
    assert c['owner_id']=='eddy:horizon:loop-10-primary' and c['source_name']=='Murphy' and c['date']=='1988-06-20'
    assert c['pdf_page']==4 and c['figure']==4 and c['dynamic_topography_unit']=='m' and c['horizontal_coordinate']=='north_latitude_degrees'
    assert c['earth_radius_km']==6371 and c['reading_allowance_pixels']==6 and c['axis_sensitivity_pixels']==2
    assert c['round_span_outward_km']==25 and c['round_height_outward_m']==.05
    assert c['diagnostic_level_m']==.3 and c['level_choice_by_osw'] is True and c['sensitivity_levels_m']==[.25,.3,.35]
    assert all(c[k] is False for k in ['author_eddy_boundary','along_track_distance_inferred','diameter_inferred','physical_state_join_eligible','association_is_verified','seasonal_playback_eligible','rights_screened_release_eligible','missing_ink_reconstructed'])
    assert c['curve']=='Altimeter' and c['axbt_trace_combined'] is False
    ref=c['source_raster'];assert (ref['xref'],ref['width'],ref['height'],ref['components'])==(119,3234,4403,3)
    assert ref['samples_sha256']=='19dd097f0900b67600f916ec01c74aa9350c518c14766040dd143fe445c8b5d6'
    assert len(c['ticks'])==9
    assert sorted(t['value'] for t in c['ticks'] if t['axis']=='height')==[0,.5,1]
    zero=next(t['coordinate'] for t in c['ticks'] if t['axis']=='height' and t['value']==0)
    half=next(t['coordinate'] for t in c['ticks'] if t['axis']=='height' and t['value']==.5)
    assert {(r['height_m'],r['maximum_rgb_channel']) for r in c['crossings']}==set(itertools.product([.25,.3,.35],[75,100])) and len(c['crossings'])==6
    for r in c['crossings']:
        assert r['row_pixel']==round(zero-r['height_m']*(zero-half)/.5)
        for side,limits in [('south',[2035,2075]),('north',[2380,2425])]:
            v=r['crossings'][side];assert v['window_xyxy']==[limits[0],r['row_pixel']-1,limits[1],r['row_pixel']+1]
            assert limits[0]<v['x_range'][0]<=v['x_range'][1]<limits[1] and v['ink_pixels']>=6
            assert v['distinct_columns']==list(range(v['x_range'][0],v['x_range'][1]+1))
    assert len(c['peaks'])==2 and {p['maximum_rgb_channel'] for p in c['peaks']}=={75,100}
    for p in c['peaks']:
        assert p['window_xyxy']==[2035,500,2425,730] and 500<p['minimum_y_pixel']<730 and p['ink_pixels']>1000
    span(c);peak(c)


def verify_source(pdf,batch_path):
    from verify_eddy_plot_source_v1 import constrain
    constrain()
    import pymupdf
    b=json.loads(batch_path.read_bytes());c=b['height_profile_cases'][0];validate_case(c);original=b['sources']['calman-1989']['original']
    raw=pdf.read_bytes();assert len(raw)==original['bytes']==5107472 and hashlib.sha256(raw).hexdigest()==original['sha256']
    with pymupdf.open(stream=raw,filetype='pdf') as doc:
        assert len(doc)==original['pages']==6 and 119 in [r[0] for r in doc[3].get_images(full=True)]
        pix=pymupdf.Pixmap(doc,119);assert (pix.width,pix.height,pix.n)==(3234,4403,3);samples=pix.samples
        assert hashlib.sha256(samples).hexdigest()==c['source_raster']['samples_sha256']
        for t in c['ticks']:
            pts=ink(samples,pix.width,pix.height,t['window_xyxy'],100);assert len(pts)==t['ink_pixels']
            coord=statistics.median(p[0 if t['axis']=='latitude' else 1] for p in pts)
            assert coord==t['coordinate'] and t['bbox_xyxy']==[min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)]
        for r in c['crossings']:
            for v in r['crossings'].values():
                pts=ink(samples,pix.width,pix.height,v['window_xyxy'],r['maximum_rgb_channel']);xs=sorted({p[0] for p in pts})
                assert len(pts)==v['ink_pixels'] and xs==v['distinct_columns'] and [min(xs),max(xs)]==v['x_range']
        for p in c['peaks']:
            pts=ink(samples,pix.width,pix.height,p['window_xyxy'],p['maximum_rgb_channel']);y=min(v[1] for v in pts);xs=[v[0] for v in pts if v[1]==y]
            assert len(pts)==p['ink_pixels'] and y==p['minimum_y_pixel'] and [min(xs),max(xs)]==p['minimum_row_x_range']
    return {'schema':'osw.eddy-height-profile-source-verification.v1','status':'PASS','original_pdf_sha256':original['sha256'],
            'batch_sha256':hashlib.sha256(batch_path.read_bytes()).hexdigest(),'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'axis_math_sha256':hashlib.sha256((Path(__file__).parent/'eddy_map_spans_v1.py').read_bytes()).hexdigest(),
            'source_pixels_verified':True,'tick_windows_verified':9,'level_gate_cases_verified':6,'crossing_windows_verified':12,'peak_windows_verified':2,
            'manual_curve_selection_required':True,'missing_ink_reconstructed':False,'physical_boundary_admitted':False,'meridional_span':span(c),'peak_height':peak(c),'runtime_changed':False}


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--pdf',type=Path,required=True);parser.add_argument('--batch',type=Path,required=True);parser.add_argument('--result',type=Path,required=True)
    a=parser.parse_args();result=verify_source(a.pdf,a.batch);a.result.write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps(result))
