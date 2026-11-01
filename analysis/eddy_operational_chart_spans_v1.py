"""Low-resolution operational frontal-line references; never occupied polygons."""
import hashlib
import itertools
import json
import math
from pathlib import Path

from eddy_map_spans_v1 import span_interval

CONFIG = {
 'Galileo': {'owner_id':'eddy:horizon:loop-56-primary','date':'2011-06-21','xref':28,
             'windows':{side:[80,65,125,118] for side in ['west','east','north','south']}},
 'Hadal': {'owner_id':'eddy:horizon:loop-57-primary','date':'2011-08-01','xref':30,
           'windows':{'north':[130,55,180,74],'west':[105,60,123,83],
                      'east':[181,69,196,99],'south':[137,122,183,142]}},
}


def read_pixels(samples, width, height, windows):
    assert len(samples)==width*height*3
    readings=[]
    for gate in [150,175]:
        extrema={}
        for side, roi in windows.items():
            x0,y0,x1,y1=roi
            assert 0<=x0<x1<width and 0<=y0<y1<height
            points=set()
            for y in range(y0,y1+1):
                for x in range(x0,x1+1):
                    rgb=samples[(y*width+x)*3:(y*width+x)*3+3]
                    if max(rgb)<=gate and max(rgb)-min(rgb)<=40:points.add((x,y))
            parts=[]
            while points:
                first=min(points);points.remove(first);todo=[first];part={first}
                while todo:
                    x,y=todo.pop()
                    for dx in [-1,0,1]:
                        for dy in [-1,0,1]:
                            p=(x+dx,y+dy)
                            if p in points:points.remove(p);todo.append(p);part.add(p)
                parts.append(part)
            parts.sort(key=lambda part:(-len(part),min(part)));assert parts
            selected=parts[0];assert len(selected)>=20
            assert len(parts)==1 or len(selected)>2*len(parts[1]), 'Manual segment window is ambiguous'
            axis=0 if side in ['west','east'] else 1
            choose=min if side in ['west','north'] else max
            value=choose(p[axis] for p in selected)
            assert roi[axis]<value<roi[axis+2], 'Extremum touches selection window edge'
            extrema[side]={'window_xyxy':roi,'coordinate':value,'selected_pixels':len(selected),
              'selected_pixels_sha256':hashlib.sha256(json.dumps(sorted(selected),separators=(',',':')).encode()).hexdigest(),
              'other_component_sizes':[len(p) for p in parts[1:]]}
        readings.append({'maximum_rgb_channel':gate,'maximum_rgb_spread':40,'extrema':extrema})
    return readings


def validate_case(c):
    config=CONFIG[c['source_name']]
    assert c['method']=='source_operational_chart_visible_line_spans_v1'
    assert c['owner_id']==config['owner_id'] and c['date']==config['date']
    assert c['pdf_page']==8 and c['figure']==5 and c['source_raster']['xref']==config['xref']
    assert c['source_raster']['width']==303 and c['source_raster']['height']==240
    assert c['axes']=={'longitude':[[78,-94],[140,-90],[202,-86]],'latitude':[[44,29],[95,26],[145,23]]}
    assert c['earth_radius_km']==6371 and c['reading_allowance_pixels']==6 and c['axis_sensitivity_pixels']==2 and c['round_outward_km']==25
    assert all(c[k] is False for k in ['front_threshold_known','physical_footprint_admitted','physical_state_join_eligible','association_is_verified','rights_screened_release_eligible','missing_ink_reconstructed','whole_eddy_dimensions_inferred'])
    assert len(c['readings'])==2 and {r['maximum_rgb_channel'] for r in c['readings']}=={150,175}
    for row in c['readings']:
        assert row['maximum_rgb_spread']==40
        for side, v in row['extrema'].items():
            assert v['window_xyxy']==config['windows'][side] and v['selected_pixels']>=20
            assert not v['other_component_sizes'] or v['selected_pixels']>2*max(v['other_component_sizes'])
            axis=0 if side in ['west','east'] else 1
            assert v['window_xyxy'][axis]<v['coordinate']<v['window_xyxy'][axis+2]
    return c


def spans(c, component):
    validate_case(c);assert component in ['east_west','north_south']
    intervals=[]
    for reading in c['readings']:
        e=reading['extrema'];bbox=[e[k]['coordinate'] for k in ['west','north','east','south']]
        for shifts in itertools.product([-2,2],repeat=6):
            axes={}
            for name, changes in [('longitude',shifts[:3]),('latitude',shifts[3:])]:
                axes[name]=[[pixel+delta,value] for (pixel,value),delta in zip(c['axes'][name],changes)]
            interval=span_interval({**c,'outline':{'bbox_xyxy':bbox},'axes':axes},component)
            intervals.append(interval['audit_reading_interval_km'])
    e=c['readings'][1]['extrema'];bbox=[e[k]['coordinate'] for k in ['west','north','east','south']]
    nominal=span_interval({**c,'outline':{'bbox_xyxy':bbox}},component)
    lo,hi=min(v[0] for v in intervals),max(v[1] for v in intervals)
    return {'audit_visible_line_span_km':nominal['audit_span_km'],'audit_reading_interval_km':[lo,hi],
            'range_km':[math.floor(lo/25)*25,math.ceil(hi/25)*25],'total_scenarios':len(intervals),
            'pixel_and_axis_sensitivity_only':True,'whole_eddy_dimensions_inferred':False}


def verify_source(pdf,batch_path):
    from verify_eddy_plot_source_v1 import constrain
    constrain()
    import pymupdf
    b=json.loads(batch_path.read_bytes());original=b['sources']['brickley-2012']['original'];raw=pdf.read_bytes()
    assert len(raw)==original['bytes']==1077794 and hashlib.sha256(raw).hexdigest()==original['sha256']
    results=[]
    with pymupdf.open(stream=raw,filetype='pdf') as doc:
        assert len(doc)==12
        for c in b['operational_chart_cases']:
            validate_case(c);ref=c['source_raster'];assert ref['xref'] in [v[0] for v in doc[7].get_images(full=True)]
            pix=pymupdf.Pixmap(pymupdf.csRGB,pymupdf.Pixmap(doc,ref['xref']));samples=pix.samples
            assert (pix.width,pix.height,pix.n)==(303,240,3)
            assert hashlib.sha256(samples).hexdigest()==ref['samples_sha256']
            assert read_pixels(samples,pix.width,pix.height,CONFIG[c['source_name']]['windows'])==c['readings']
            results.append({'name':c['source_name'],'date':c['date'],'source_pixels_verified':True,
                            'spans':{k:spans(c,k) for k in ['east_west','north_south']}})
    return {'schema':'osw.eddy-operational-chart-line-verification.v1','status':'PASS',
            'original_pdf_sha256':original['sha256'],'batch_sha256':hashlib.sha256(batch_path.read_bytes()).hexdigest(),
            'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'axis_math_sha256':hashlib.sha256((Path(__file__).parent/'eddy_map_spans_v1.py').read_bytes()).hexdigest(),
            'source_pixels_verified':True,'manual_name_date_axis_and_segment_selection_required':True,
            'missing_ink_reconstructed':False,'whole_eddy_dimensions_inferred':False,'physical_footprint_admitted':False,
            'records':results,'runtime_changed':False}
