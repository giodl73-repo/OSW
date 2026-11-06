"""Source-figure colour-band patch spans; no physical eddy boundary inferred."""
import hashlib
import json
import statistics
from pathlib import Path
from eddy_map_spans_v1 import span_interval


def palette_readout(samples,width,height,spec):
    assert len(samples)==width*height*3
    assert spec=={'x_pixels':[1923,1943],'positive_15_line_y':703,'pixels_per_level':15.2,'half_patch_height':2,'extension_15_y':688}
    result=[]
    for level in range(-15,16):
        y=688 if level==15 else round(703+(14.5-level)*15.2)
        rgb=[samples[(yy*width+x)*3:(yy*width+x)*3+3] for x in range(1923,1944) for yy in range(y-2,y+3)]
        result.append({'level_lower_edge':level,'sample_center_y':y,'rgb_median':[round(statistics.median(c[k] for c in rgb)) for k in range(3)]})
    return result


def patch_readout(samples,width,height,roi,palette,level):
    assert len(samples)==width*height*3 and level in [9,10,11]
    x0,y0,x1,y1=roi;assert 0<=x0<x1<width and 0<=y0<y1<height
    points=set()
    for y in range(y0,y1+1):
        for x in range(x0,x1+1):
            rgb=samples[(y*width+x)*3:(y*width+x)*3+3]
            distance,band=min((sum((a-b)**2 for a,b in zip(rgb,p['rgb_median'])),p['level_lower_edge']) for p in palette)
            if distance<=900 and band>=level:points.add((x,y))
    components=[]
    while points:
        first=min(points);points.remove(first);todo=[first];selected={first}
        while todo:
            x,y=todo.pop()
            for dx in [-1,0,1]:
                for dy in [-1,0,1]:
                    q=(x+dx,y+dy)
                    if q in points:points.remove(q);todo.append(q);selected.add(q)
        components.append(selected)
    components.sort(key=lambda c:(-len(c),min(c)));assert components
    selected=components[0];assert len(selected)>1000
    assert len(components)==1 or len(selected)>10*len(components[1])
    box=[min(x for x,y in selected),min(y for x,y in selected),max(x for x,y in selected),max(y for x,y in selected)]
    assert x0+6<box[0]<box[2]<x1-6 and y0+6<box[1]<box[3]<y1-6
    return {'level_lower_edge':level,'bbox_xyxy':box,'selected_pixels':len(selected),
        'selected_pixels_sha256':hashlib.sha256(json.dumps(sorted(selected),separators=(',',':')).encode()).hexdigest(),
        'other_component_sizes':[len(c) for c in components[1:]]}


def validate_case(case):
    assert case['method']=='source_palette_level_patch_v1'
    assert case['owner_id']=='eddy:geography:lilian-2006' and case['date']=='2006-07-05'
    assert case['source_name']=='Lilian' and case['figure']==3 and case['panel']=='b, 05-Jul-2006'
    assert case['source_level']==10 and case['source_level_unit'] is None and case['physical_level_m'] is None
    assert case['full_ring_boundary_admitted'] is False and case['physical_state_join_eligible'] is False
    assert case['rgb_distance_squared_max']==900 and case['nominal_patch_index']==1
    assert case['roi_xyxy_inclusive']==[970,270,1160,410]
    assert case['axes']=={'longitude':[[720,-45],[853,-43],[987,-41],[1120,-39],[1254,-37]],'latitude':[[133,-22],[280,-24],[427,-26],[574,-28]]}
    assert [p['level_lower_edge'] for p in case['patch_cases']]==[9,10,11]
    assert [p['level_lower_edge'] for p in case['palette']]==list(range(-15,16))
    x0,y0,x1,y1=case['roi_xyxy_inclusive']
    for patch in case['patch_cases']:
        a,b,c,d=patch['bbox_xyxy'];assert x0+6<a<c<x1-6 and y0+6<b<d<y1-6
        assert patch['selected_pixels']>1000 and len(patch['selected_pixels_sha256'])==64
        assert not patch['other_component_sizes'] or patch['selected_pixels']>10*max(patch['other_component_sizes'])
    for component in ['east_west','north_south']:spans(case,component)


def spans(case,component):
    assert component in ['east_west','north_south']
    rows=[span_interval({**case,'outline':{'bbox_xyxy':p['bbox_xyxy']}},component) for p in case['patch_cases']]
    return {'audit_span_km':rows[case['nominal_patch_index']]['audit_span_km'],
        'audit_reading_interval_km':[min(r['audit_reading_interval_km'][0] for r in rows),max(r['audit_reading_interval_km'][1] for r in rows)],
        'audit_decimal_places':6,'plot_level_sensitivity':[9,10,11],
        'range_km':[min(r['range_km'][0] for r in rows),max(r['range_km'][1] for r in rows)]}


def verify_source(pdf,batch_path):
    from verify_eddy_plot_source_v1 import constrain
    constrain()
    import pymupdf
    batch=json.loads(batch_path.read_bytes());original=batch['sources']['guerra-2018']['original']
    assert pdf.stat().st_size==original['bytes']<15000000
    assert hashlib.sha256(pdf.read_bytes()).hexdigest()==original['sha256']
    case=batch['colour_span_cases'][0];validate_case(case);ref=case['source_raster']
    with pymupdf.open(pdf) as document:
        assert len(document)==10 and ref['xref'] in [r[0] for r in document[5].get_images(full=True)]
        pix=pymupdf.Pixmap(document,ref['xref']);assert pix.n==3
        assert (pix.width,pix.height)==(ref['width'],ref['height'])==(2000,1865)
        assert hashlib.sha256(pix.samples).hexdigest()==ref['samples_sha256']
        palette=palette_readout(pix.samples,pix.width,pix.height,case['palette_calibration']);assert palette==case['palette']
        patches=[patch_readout(pix.samples,pix.width,pix.height,case['roi_xyxy_inclusive'],palette,level) for level in [9,10,11]]
        assert patches==case['patch_cases']
    return {'schema':'osw.eddy-colour-span-source-verification.v1','status':'PASS',
        'original_pdf_sha256':original['sha256'],'batch_sha256':hashlib.sha256(batch_path.read_bytes()).hexdigest(),
        'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'span_math_sha256':hashlib.sha256((Path(__file__).parent/'eddy_map_spans_v1.py').read_bytes()).hexdigest(),
        'source_pixels_verified':True,'source_palette_verified':True,'patches':patches,
        'spans':{c:spans(case,c) for c in ['east_west','north_south']},
        'source_level_unit':None,'full_ring_boundary_admitted':False,'runtime_changed':False}


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--pdf',type=Path,required=True);parser.add_argument('--batch',type=Path,required=True);parser.add_argument('--result',type=Path,required=True)
    args=parser.parse_args();result=verify_source(args.pdf,args.batch);args.result.write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps(result['spans']))
