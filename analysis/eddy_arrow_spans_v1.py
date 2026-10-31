"""Manual ink-extremum readings of plotted circulation arrows, never footprints."""
import hashlib
import json
from pathlib import Path
from eddy_map_spans_v1 import span_interval,outline_readout


def read_extremum(samples,width,height,window,direction):
    assert len(samples)==width*height*3 and direction in ['west','east','north','south']
    x0,y0,x1,y1=window;assert 0<=x0<x1<width and 0<=y0<y1<height
    points=[]
    for y in range(y0,y1+1):
        for x in range(x0,x1+1):
            if max(samples[(y*width+x)*3:(y*width+x)*3+3])<=75:points.append([x,y])
    assert len(points)>=10
    axis=0 if direction in ['west','east'] else 1
    value=(min if direction in ['west','north'] else max)(p[axis] for p in points)
    assert (x0 if axis==0 else y0)<value<(x1 if axis==0 else y1)
    return {'direction':direction,'window_xyxy_inclusive':window,'axis_coordinate_pixel':value,
        'selected_ink_pixels':len(points),'selected_ink_pixels_sha256':hashlib.sha256(json.dumps(points,separators=(',',':')).encode()).hexdigest(),
        'extreme_ink_pixels':[p for p in points if p[axis]==value]}


def validate_case(case):
    assert case['method']=='manual_ink_arrow_span_v1' and case['source_ink_max_rgb_channel']==75
    assert case['association_is_verified'] is False and case['physical_state_join_eligible'] is False
    assert case['closed_contour_extraction_admitted'] is False and case['footprint_admitted'] is False
    assert case['source_contour_level'] is None and case['source_contour_unit'] is None
    assert case['rights_screened_release_eligible'] is False and case['chart_contains_confidential_stamp'] is True
    readings=case['extremum_readings'];assert [r['direction'] for r in readings]==['west','east','north','south']
    for r in readings:
        x0,y0,x1,y1=r['window_xyxy_inclusive'];axis=0 if r['direction'] in ['west','east'] else 1
        assert (x0 if axis==0 else y0)<r['axis_coordinate_pixel']<(x1 if axis==0 else y1)
        assert r['selected_ink_pixels']>=10 and len(r['selected_ink_pixels_sha256'])==64
        assert r['extreme_ink_pixels'] and all(p[axis]==r['axis_coordinate_pixel'] for p in r['extreme_ink_pixels'])
    assert case['outline']['bbox_xyxy']==[readings[0]['axis_coordinate_pixel'],readings[2]['axis_coordinate_pixel'],readings[1]['axis_coordinate_pixel'],readings[3]['axis_coordinate_pixel']]
    box=case['outline']['bbox_xyxy'];assert box[2]-box[0]>12 and box[3]-box[1]>12
    for component in ['east_west','north_south']:span_interval(case,component)


def verify_source(pdf,batch_path):
    from verify_eddy_plot_source_v1 import constrain
    constrain()
    import pymupdf
    batch=json.loads(batch_path.read_bytes());original=batch['sources']['horizon-aade-2015']['original']
    assert pdf.stat().st_size==original['bytes']<15000000 and hashlib.sha256(pdf.read_bytes()).hexdigest()==original['sha256']
    results=[]
    with pymupdf.open(pdf) as document:
        assert len(document)==60
        for case in batch['arrow_span_cases']:
            validate_case(case);ref=case['source_raster'];assert ref['xref'] in [r[0] for r in document[case['pdf_page']-1].get_images(full=True)]
            pix=pymupdf.Pixmap(document,ref['xref']);samples=pix.samples
            assert pix.n==3 and (pix.width,pix.height)==(ref['width'],ref['height'])
            assert hashlib.sha256(samples).hexdigest()==ref['samples_sha256']
            actual=[read_extremum(samples,pix.width,pix.height,r['window_xyxy_inclusive'],r['direction']) for r in case['extremum_readings']]
            assert actual==case['extremum_readings']
            axis=case['axis_reference_raster'];assert axis['xref'] in [r[0] for r in document[case['pdf_page']-1].get_images(full=True)]
            ap=pymupdf.Pixmap(document,axis['xref']);assert ap.n==3 and (ap.width,ap.height)==(axis['width'],axis['height'])
            assert hashlib.sha256(ap.samples).hexdigest()==axis['samples_sha256']
            _,am=document[case['pdf_page']-1].get_image_rects(ref['xref'],transform=True)[0]
            _,bm=document[case['pdf_page']-1].get_image_rects(axis['xref'],transform=True)[0]
            origin=pymupdf.Point(0,0)*bm*~am;xend=pymupdf.Point(1,0)*bm*~am
            assert abs(origin.x*pix.width)<.2 and abs(origin.y*pix.height-axis['y_offset_pixels'])<.2
            assert abs((xend.x-origin.x)*pix.width-axis['width'])<.2 and abs((xend.y-origin.y)*pix.height)<.2
            rejected=False
            try:outline_readout(bytes(255-v for v in samples),pix.width,pix.height,case['closed_outline_test_roi'])
            except AssertionError:rejected=True
            assert rejected
            results.append({'name':case['source_name'],'source_extrema_pixels_verified':True,'closed_outline_gate_rejected':True,
                'bbox_xyxy':case['outline']['bbox_xyxy'],'spans':{c:span_interval(case,c) for c in ['east_west','north_south']}})
    return {'schema':'osw.eddy-arrow-span-source-verification.v1','status':'PASS','batch_sha256':hashlib.sha256(batch_path.read_bytes()).hexdigest(),
        'original_pdf_sha256':original['sha256'],'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'span_math_sha256':hashlib.sha256((Path(__file__).parent/'eddy_map_spans_v1.py').read_bytes()).hexdigest(),
        'records':results,'source_pixels_verified':True,'no_gap_repair':True,'physical_footprint_admitted':False,'runtime_changed':False}


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--pdf',type=Path,required=True);parser.add_argument('--batch',type=Path,required=True);parser.add_argument('--result',type=Path,required=True)
    args=parser.parse_args();result=verify_source(args.pdf,args.batch);args.result.write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps(result['records']))
