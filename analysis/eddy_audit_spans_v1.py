"""Coarse arc spans of retained figure-contour candidates, never physical sizes."""
import hashlib
import itertools
import json
import math
from pathlib import Path

AUDIT='research/ursa-2021-0307-figure-contour-audit.json'


def digest(value):
    return hashlib.sha256(json.dumps(value,separators=(',',':')).encode()).hexdigest()


def bbox(ring):
    assert len(ring)>20 and ring[0]==ring[-1]
    assert all(len(p)==2 and all(type(v) is int for v in p) for p in ring)
    return [min(p[0] for p in ring),min(p[1] for p in ring),max(p[0] for p in ring),max(p[1] for p in ring)]


def case_from_audit(audit,audit_sha):
    return {'method':'retained_contour_audit_span_v1','source_name':'Ursa','owner_id':audit['entity_id'],'date':audit['observation_date'],
        'figure':3,'panel':'row 3 column 4, temporary-detachment candidate',
        'audit_file':AUDIT,'audit_sha256':audit_sha,
        'source_image_file':audit['source_image_file'],'source_image_sha256':audit['source_image_sha256'],
        'source_axes_pixels':audit['source_panel_axes_pixels'],'axis_values_lon_lat':audit['axis_values_lon_lat'],
        'roi_xyxy':audit['source_pixel_search_box_xyxy'],
        'outline_cases':[{'threshold':r['dark_rgb_max_exclusive'],'edge':r['stroke_edge'],'bbox_xyxy':bbox(r['source_pixel_ring']),
                          'pixel_ring_sha256':digest(r['source_pixel_ring'])} for r in audit['segmentation_sensitivity_cases']],
        'nominal_case_index':audit['nominal_segmentation_case_index'],'axis_sensitivity_pixels':3,
        'calibration_scenarios_per_outline':17,'rejected_segmentation_cases':len(audit['rejected_segmentation_cases']),
        'earth_radius_km':6371,'reading_allowance_pixels':6,'round_outward_km':25,
        'association_is_verified':False,'physical_state_join_eligible':False,
        'boundary_description':'Editorial source-figure contour candidate; physical ring attribution pending. Source literal SSH contour 0.65 cm has unresolved unit. No numeric SSH field reconstructed.'}


def validate_case(case,audit,audit_sha):
    assert case==case_from_audit(audit,audit_sha)
    assert audit['entity_id']=='eddy:published:ursa-2021' and audit['observation_date']=='2021-03-07'
    assert audit['closed_pixel_loop_verified'] and not audit['physical_boundary_admitted']
    assert audit['contour_definition']['normalized_contour_value_m'] is None
    assert len(case['outline_cases'])==4 and case['rejected_segmentation_cases']==2
    assert [(r['threshold'],r['edge']) for r in case['outline_cases']]==[(t,e) for t in [40,70] for e in ['outer_stroke_edge','inner_stroke_edge']]
    x0,y0,x1,y1=case['roi_xyxy']
    for row in case['outline_cases']:
        a,b,c,d=row['bbox_xyxy'];assert x0<a<c<x1 and y0<b<d<y1
    assert case['source_axes_pixels']==[1121,1383,674,894] and case['axis_values_lon_lat']==[-89,-85,28,25]


def spans(case,component):
    assert component in ['east_west','north_south']
    assert (case['earth_radius_km'],case['reading_allowance_pixels'],case['round_outward_km'],case['axis_sensitivity_pixels'])==(6371,6,25,3)
    shifts=[(0,0,0,0),*itertools.product((-3,3),repeat=4)]
    values=[];lower=[];upper=[];pad=6;scale=6371*math.pi/180
    for outline in case['outline_cases']:
        x0,y0,x1,y1=outline['bbox_xyxy']
        assert x1-x0>2*pad and y1-y0>2*pad
        for shift in shifts:
            a,b,c,d=[v+s for v,s in zip(case['source_axes_pixels'],shift)]
            assert a<b and c<d
            lon=lambda x:-89+(x-a)*4/(b-a)
            lat=lambda y:28-(y-c)*3/(d-c)
            rx0,ry0,rx1,ry1=case['roi_xyxy']
            # Labeled ticks are interior to the source panel, not its frame.
            # Use the retained audit's linear calibration throughout the ROI.
            assert rx0<x0-pad<x1+pad<rx1 and ry0<y0-pad<y1+pad<ry1
            mid=(lat(y0)+lat(y1))/2
            if component=='north_south':
                values.append((lat(y0)-lat(y1))*scale)
                lower.append((lat(y0+pad)-lat(y1-pad))*scale)
                upper.append((lat(y0-pad)-lat(y1+pad))*scale)
            else:
                values.append((lon(x1)-lon(x0))*scale*math.cos(math.radians(mid)))
                cosines=[math.cos(math.radians((lat(y0+i*pad)+lat(y1+j*pad))/2)) for i in [-1,1] for j in [-1,1]]
                lower.append((lon(x1-pad)-lon(x0+pad))*scale*min(cosines))
                upper.append((lon(x1+pad)-lon(x0-pad))*scale*max(cosines))
    assert len(values)==68 and min(lower)>0
    return {'audit_span_km':round(values[case['nominal_case_index']*17],6),
        'audit_outline_and_axis_sensitivity_km':[round(min(values),6),round(max(values),6)],
        'audit_reading_interval_km':[round(min(lower),6),round(max(upper),6)],'audit_decimal_places':6,
        'accepted_scenarios':68,'range_km':[math.floor(min(lower)/25)*25,math.ceil(max(upper)/25)*25]}


def verify_source(root):
    # Explicit source-image analysis only; no state geometries, ocean fields or runtime.
    from verify_eddy_plot_source_v1 import constrain
    constrain()
    import cv2
    import numpy as np
    from PIL import Image
    cv2.setNumThreads(1)
    audit=json.loads((root/AUDIT).read_bytes());pins={AUDIT:hashlib.sha256((root/AUDIT).read_bytes()).hexdigest()}
    for file_key,sha_key in [('source_image_file','source_image_sha256'),('source_document_file','source_document_sha256'),('source_panel_audit_file','source_panel_audit_sha256'),('acquisition_file','acquisition_sha256'),('protocol_file','protocol_sha256')]:
        path=audit[file_key];pins[path]=hashlib.sha256((root/path).read_bytes()).hexdigest();assert pins[path]==audit[sha_key]
    case=case_from_audit(audit,pins[AUDIT]);validate_case(case,audit,pins[AUDIT])
    with Image.open(root/audit['source_image_file']) as image:array=np.array(image.convert('RGB'))
    x0,y0,x1,y1=case['roi_xyxy'];region=array[y0:y1,x0:x1].max(axis=2);verified=[]
    rows=audit['segmentation_sensitivity_cases']+audit['rejected_segmentation_cases']
    for threshold in [40,70,100]:
        contours,hierarchy=cv2.findContours((region<threshold).astype('uint8'),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        outer=[i for i,c in enumerate(contours) if cv2.contourArea(c)>20000 and hierarchy[0,i,3]==-1];assert len(outer)==1
        index=outer[0];child=int(hierarchy[0,index,2]);assert child>=0 and cv2.contourArea(contours[child])>20000
        for edge,idx in [('outer_stroke_edge',index),('inner_stroke_edge',child)]:
            ring=[[int(x+x0),int(y+y0)] for x,y in contours[idx][:,0,:]];ring.append(ring[0])
            row=next(r for r in rows if r['dark_rgb_max_exclusive']==threshold and r['stroke_edge']==edge)
            assert ring==row['source_pixel_ring']
            verified.append({'threshold':threshold,'edge':edge,'vertices':len(ring),'pixel_ring_sha256':digest(ring),'admitted_to_span':threshold<100})
    return {'schema':'osw.eddy-audit-span-source-verification.v1','status':'PASS','input_sha256':pins,
        'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_paths_reproduced':verified,
        'prior_rejected_paths_remain_excluded':True,'source_pixels_verified':True,
        'spans':{c:spans(case,c) for c in ['east_west','north_south']},'opencv':cv2.__version__,'physical_boundary_admitted':False,'runtime_changed':False}


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,required=True);parser.add_argument('--result',type=Path,required=True)
    args=parser.parse_args();result=verify_source(args.root);args.result.write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps(result['spans']))
