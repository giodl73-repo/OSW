"""Auditable spans read from a published closed outline, never physical footprints."""
import hashlib
import json
import math
from pathlib import Path


def outline_readout(samples,width,height,roi):
    assert len(samples)==width*height*3
    x0,y0,x1,y1=roi;assert 0<=x0<x1<width and 0<=y0<y1<height
    points=set()
    for y in range(y0,y1+1):
        for x in range(x0,x1+1):
            rgb=samples[(y*width+x)*3:(y*width+x)*3+3]
            if min(rgb)>=180 and max(rgb)-min(rgb)<=75:points.add((x,y))
    components=[]
    while points:
        first=min(points);points.remove(first);todo=[first];component={first}
        while todo:
            x,y=todo.pop()
            for dx in [-1,0,1]:
                for dy in [-1,0,1]:
                    q=(x+dx,y+dy)
                    if q in points:points.remove(q);component.add(q);todo.append(q)
        components.append(component)
    components.sort(key=lambda c:(-len(c),min(c)));assert components
    selected=components[0];assert len(selected)>200
    assert len(components)==1 or len(selected)>3*len(components[1])
    bbox=[min(x for x,y in selected),min(y for x,y in selected),max(x for x,y in selected),max(y for x,y in selected)]
    assert x0<bbox[0]<bbox[2]<x1 and y0<bbox[1]<bbox[3]<y1
    border={(x,y) for x in range(x0,x1+1) for y in [y0,y1]}|{(x,y) for x in [x0,x1] for y in range(y0,y1+1)}
    outside=border-selected;todo=list(outside)
    while todo:
        x,y=todo.pop()
        for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            q=(x+dx,y+dy)
            if x0<=q[0]<=x1 and y0<=q[1]<=y1 and q not in selected and q not in outside:outside.add(q);todo.append(q)
    enclosed=(x1-x0+1)*(y1-y0+1)-len(outside)-len(selected);assert enclosed>300
    canonical=json.dumps(sorted(selected),separators=(',',':')).encode()
    columns=[[x,min(y for xx,y in selected if xx==x),max(y for xx,y in selected if xx==x)] for x in sorted({x for x,y in selected})]
    return {'bbox_xyxy':bbox,'selected_pixels':len(selected),'selected_pixels_sha256':hashlib.sha256(canonical).hexdigest(),
        'column_y_extents':columns,'other_component_sizes':[len(c) for c in components[1:]],'enclosed_background_pixels':enclosed}


def axis_value(pixel,anchors):
    assert len(anchors)>=3 and all(a[0]<b[0] for a,b in zip(anchors,anchors[1:]))
    assert anchors[0][0]<=pixel<=anchors[-1][0]
    for a,b in zip(anchors,anchors[1:]):
        if a[0]<=pixel<=b[0]:return a[1]+(pixel-a[0])*(b[1]-a[1])/(b[0]-a[0])
    raise AssertionError('Uncalibrated map coordinate')


def span_interval(case,component):
    assert component in ['east_west','north_south']
    assert case['earth_radius_km']==6371 and case['reading_allowance_pixels']==6 and case['round_outward_km']==25
    x0,y0,x1,y1=case['outline']['bbox_xyxy'];lon=case['axes']['longitude'];lat=case['axes']['latitude']
    assert all(a[1]<b[1] for a,b in zip(lon,lon[1:])) and all(a[1]>b[1] for a,b in zip(lat,lat[1:]))
    midlat=(axis_value(y0,lat)+axis_value(y1,lat))/2
    assert -80<midlat<80 and x1>x0 and y1>y0
    km_per_degree=case['earth_radius_km']*math.pi/180;pad=case['reading_allowance_pixels'];step=case['round_outward_km']
    if component=='north_south':
        native=(axis_value(y0,lat)-axis_value(y1,lat))*km_per_degree
        lower=max(0,axis_value(y0+pad,lat)-axis_value(y1-pad,lat))*km_per_degree
        upper=(axis_value(y0-pad,lat)-axis_value(y1+pad,lat))*km_per_degree
    else:
        native=(axis_value(x1,lon)-axis_value(x0,lon))*km_per_degree*math.cos(math.radians(midlat))
        # Also cover the latitude calibration/reading allowance in the parallel scale.
        cosine=[math.cos(math.radians((axis_value(y0+a*pad,lat)+axis_value(y1+b*pad,lat))/2)) for a in [-1,1] for b in [-1,1]]
        lower=max(0,axis_value(x1-pad,lon)-axis_value(x0+pad,lon))*km_per_degree*min(cosine)
        upper=(axis_value(x1+pad,lon)-axis_value(x0-pad,lon))*km_per_degree*max(cosine)
    return {'native_span_km':native,'unrounded_reading_interval_km':[lower,upper],
        'range_km':[math.floor(lower/step)*step,math.ceil(upper/step)*step]}


def validate_map_case(case):
    assert case['color_gate']=={'minimum_rgb_channel':180,'maximum_rgb_spread':75}
    assert case['association_is_verified'] is False and case['physical_state_join_eligible'] is False
    ref=case['source_raster'];outline=case['outline'];roi=case['roi_xyxy_inclusive'];bbox=outline['bbox_xyxy'];columns=outline['column_y_extents']
    assert ref['width']>500 and ref['height']>500 and len(ref['samples_sha256'])==64
    assert 0<=roi[0]<bbox[0]<bbox[2]<roi[2]<ref['width'] and 0<=roi[1]<bbox[1]<bbox[3]<roi[3]<ref['height']
    assert [c[0] for c in columns]==list(range(bbox[0],bbox[2]+1))
    assert all(bbox[1]<=lo<=hi<=bbox[3] for x,lo,hi in columns)
    assert min(c[1] for c in columns)==bbox[1] and max(c[2] for c in columns)==bbox[3]
    assert outline['selected_pixels']>200 and outline['enclosed_background_pixels']>300
    assert not outline['other_component_sizes'] or outline['selected_pixels']>3*max(outline['other_component_sizes'])
    assert len(outline['selected_pixels_sha256'])==64
    for component in ['east_west','north_south']:span_interval(case,component)


def verify_source(pdf,batch_path):
    # Source-PDF analysis only. No ocean-field, engine, browser or runtime access.
    from verify_eddy_plot_source_v1 import constrain
    constrain()
    import pymupdf
    batch=json.loads(batch_path.read_bytes());original=batch['sources']['trott-2024']['original']
    assert pdf.stat().st_size==original['bytes']<15000000
    assert hashlib.sha256(pdf.read_bytes()).hexdigest()==original['sha256']
    results=[]
    with pymupdf.open(pdf) as document:
        assert len(document)==original['pages']
        for case in batch['map_cases']:
            validate_map_case(case);ref=case['source_raster']
            assert ref['xref'] in [r[0] for r in document[case['pdf_page']-1].get_images(full=True)]
            pix=pymupdf.Pixmap(document,ref['xref']);assert pix.n==3
            assert (pix.width,pix.height)==(ref['width'],ref['height'])
            assert hashlib.sha256(pix.samples).hexdigest()==ref['samples_sha256']
            if case.get('axis_reference_raster'):
                axis=case['axis_reference_raster']
                assert axis['xref'] in [r[0] for r in document[case['pdf_page']-1].get_images(full=True)]
                ap=pymupdf.Pixmap(document,axis['xref'])
                assert (ap.width,ap.height)==(axis['width'],axis['height'])
                assert hashlib.sha256(ap.samples).hexdigest()==axis['samples_sha256']
            actual=outline_readout(pix.samples,pix.width,pix.height,case['roi_xyxy_inclusive'])
            assert actual==case['outline']
            results.append({'name':case['source_name'],'date':case['date'],'source_pixels_verified':True,
                'selected_pixels':actual['selected_pixels'],'spans':{c:span_interval(case,c)['range_km'] for c in ['east_west','north_south']}})
        a,b=batch['excluded_duplicate_figure_images']['pdf_pages'];x,y=batch['excluded_duplicate_figure_images']['xrefs']
        assert x in [r[0] for r in document[a-1].get_images(full=True)] and y in [r[0] for r in document[b-1].get_images(full=True)]
        p,q=pymupdf.Pixmap(document,x),pymupdf.Pixmap(document,y)
        assert (p.width,p.height,p.samples)==(q.width,q.height,q.samples)
    return {'schema':'osw.eddy-map-span-source-verification.v1','status':'PASS','original_pdf_sha256':original['sha256'],
        'batch_sha256':hashlib.sha256(batch_path.read_bytes()).hexdigest(),'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'records':results,'duplicate_figure_images_verified':True,
        'source_pixels_verified':True,'runtime_changed':False}


if __name__=='__main__':
    import argparse
    from pathlib import Path
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--pdf',type=Path,required=True);parser.add_argument('--batch',type=Path,required=True);parser.add_argument('--result',type=Path)
    args=parser.parse_args();result=verify_source(args.pdf,args.batch)
    if args.result:args.result.write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print(json.dumps(result))
