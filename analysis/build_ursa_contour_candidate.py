"""Trace a dated closed source-image loop; physical named-ring identity stays pending."""
import hashlib,itertools,json
from pathlib import Path
import cv2
import numpy as np
import shapely
from PIL import Image
from shapely.geometry import Polygon
from build_published_kraken_figure_state_join import state_shapes
from build_kraken_footprint_candidate import geometry_digest
from build_thor_ursa_source_panels import PINS,PATH as PANELS,SOURCE,ACQUISITION,URL

ROOT=Path(__file__).resolve().parents[1]
PATH='research/ursa-2021-0307-figure-contour-audit.json'
IMAGE='figures/exley-loop-2022-source-figure-3.webp'
MAP='figures/osw-province-atlas-interactive.svg'
PROTOCOL='plans/ursa-dated-contour-digitization-protocol-v1.md'
OWNER='eddy:published:ursa-2021'
AXES=[1121,1383,674,894]
ROI=[1122,678,1380,925]

def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def coordinates(pixels,axes):
    a,b,c,d=axes
    return [[round(-89+(x-a)*4/(b-a),7),round(28-(y-c)*3/(d-c),7)] for x,y in pixels]
def display(points):return Polygon([[60+(x+180)/360*1480,90+(90-y)/180*740] for x,y in points])

def build():
    for path,(digest,size) in PINS.items():
        if sha(path)!=digest or (ROOT/path).stat().st_size!=size:raise ValueError('Changed original Ursa source: '+path)
    panels=json.loads((ROOT/PANELS).read_bytes())
    if panels['events'][1]['panels'][13]['observation_date']!='2021-03-07':raise ValueError('Wrong original Ursa panel date')
    with Image.open(ROOT/IMAGE) as image:array=np.array(image.convert('RGB'))
    left,top,right,bottom=ROI
    region=array[top:bottom,left:right].max(axis=2)
    states=state_shapes();cases=[];failures=[]
    for threshold in [40,70,100]:
        contours,hierarchy=cv2.findContours((region<threshold).astype('uint8'),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        outer=[i for i,c in enumerate(contours) if cv2.contourArea(c)>20000 and hierarchy[0,i,3]==-1]
        if len(outer)!=1:raise ValueError('Ursa source must contain one dominant closed hollow loop')
        index=outer[0];child=int(hierarchy[0,index,2])
        if child<0 or cv2.contourArea(contours[child])<20000 or hierarchy[0,child,3]!=index:
            raise ValueError('Ursa loop has no comparable direct hole child')
        for edge,idx in [('outer_stroke_edge',index),('inner_stroke_edge',child)]:
            c=contours[idx][:,0,:]
            if np.any(c[:,0]<=0) or np.any(c[:,0]>=right-left-1) or np.any(c[:,1]<=0) or np.any(c[:,1]>=bottom-top-1):
                raise ValueError('Ursa contour touches the search box; never close a clipped line')
            ring=[[int(x+left),int(y+top)] for x,y in c];ring.append(ring[0])
            pixel_polygon=Polygon(ring)
            if not pixel_polygon.is_valid:
                failures.append({'dark_rgb_max_exclusive':threshold,'stroke_edge':edge,
                    'source_pixel_ring':ring,'status':'rejected_non_simple_pixel_ring',
                    'reason':shapely.is_valid_reason(pixel_polygon),'geometry':None,
                    'interpretation':'Dark-field or instrument-dot contact creates a non-simple pixel ring. No repair or physical inference.'})
                continue
            vertices=coordinates(ring,AXES)
            nominal=display(vertices)
            if not nominal.is_valid or nominal.area<=0:raise ValueError('Invalid Ursa contour polygon')
            calibrations=[]
            for shifts in [(0,0,0,0),*itertools.product((-3,3),repeat=4)]:
                axes=[a+b for a,b in zip(AXES,shifts)]
                poly=display(coordinates(ring,axes))
                if not poly.is_valid or poly.area<=0:raise ValueError('Invalid perturbed Ursa contour')
                fractions={code:round(poly.intersection(shape).area/poly.area,8) for code,shape in states.items() if poly.intersects(shape)}
                calibrations.append({'axis_shifts_pixels':list(shifts),'display_area_fraction_by_state':fractions})
            cases.append({'dark_rgb_max_exclusive':threshold,'stroke_edge':edge,'source_pixel_ring':ring,
                'geometry':{'type':'Polygon','coordinates':[vertices]},'calibrations':calibrations})
    nominal=cases[2];geometry=nominal['geometry']
    codes=sorted(set().union(*(set(c['display_area_fraction_by_state']) for row in cases for c in row['calibrations'])))
    assessments=[]
    for code in codes:
        vals=[c['display_area_fraction_by_state'].get(code,0) for row in cases for c in row['calibrations']]
        assessments.append({'state_id':'state:'+code,
            'intersection_assessment':'robust_across_tested_calibrations' if min(vals)>0 else 'calibration_sensitive_candidate',
            'containment_assessment':'unresolved',
            'nominal_display_area_fraction':nominal['calibrations'][0]['display_area_fraction_by_state'].get(code,0),
            'display_area_fraction_range':[min(vals),max(vals)]})
    return {'schema':'osw.named-eddy-figure-contour-audit.v1','status':'editorial_figure_digitization_scientific_review_pending',
        'entity_id':OWNER,'observation_date':'2021-03-07','source_url':URL,'source_doi':'10.3389/fmars.2022.1049645',
        'source_locator':'Figure 3, 2021-03-07 (row 3 column 4); Section 2 final paragraph; Section 3.2 temporary-detachment narrative',
        'source_document_file':SOURCE,'source_document_sha256':sha(SOURCE),'source_image_file':IMAGE,'source_image_sha256':sha(IMAGE),
        'source_panel_audit_file':PANELS,'source_panel_audit_sha256':sha(PANELS),
        'acquisition_file':ACQUISITION,'acquisition_sha256':sha(ACQUISITION),
        'state_geometry_file':MAP,'state_geometry_sha256':sha(MAP),'protocol_file':PROTOCOL,'protocol_sha256':sha(PROTOCOL),
        'method':'Threshold maximum RGB channel below 40/70/100 within the pinned interior ROI; require one dominant closed hollow loop; trace outer and inner stroke edges using CHAIN_APPROX_SIMPLE (exact collinear source-pixel compression), without morphological repair; preserve rejected non-simple threshold-100 rings; transfer common figure tick calibration; test nominal plus sixteen independent +/-3-pixel anchor shifts per accepted edge/threshold; intersect approximate coast-masked OSW display polygons.',
        'physical_limit':'Dated instantaneous figure-derived SSH contour proxy during the Ursa shedding event. Attribution to the detached named ring is an editorial interpretation requiring scientific review. Source prints 0.65 cm with unresolved unit; no numerical SSH contour was reconstructed. Not a verified whole-ring physical footprint, material coherent core, 3-D volume, lifetime extent or NASA individual identity. Tested scenarios omit source field error, unknown datum/projection, instrument-dot artifacts and OSW boundary uncertainty; no statistical confidence or physical uncertainty bound follows.',
        'coordinate_reference_system':'figure_axis_lon_lat_degrees_unspecified_datum',
        'coordinate_reference_status':'Longitude/latitude inferred by linear calibration of source figure axes. Source datum/projection are unspecified; seven-decimal output is display precision only.',
        'identity_status':'publication_scoped_event_contour_attribution_unverified',
        'contour_definition':panels['contour_definition'],'source_pixel_search_box_xyxy':ROI,
        'source_panel_axes_pixels':AXES,'axis_values_lon_lat':[-89,-85,28,25],
        'axis_calibration_sensitivity_pixels':3,'segmentation_sensitivity_cases':cases,
        'rejected_segmentation_cases':failures,'scenario_attempt_count':102,
        'nominal_segmentation_case_index':2,'scenario_polygon_count':len(cases)*17,
        'nominal_geometry':geometry,'geometry_sha256':geometry_digest(geometry),
        'source_pixel_ring':nominal['source_pixel_ring'],'state_assessments':assessments,
        'closed_pixel_loop_verified':True,'physical_boundary_admitted':False,
        'whole_eddy_state_relations':[],'center_lon_lat':None,'radius_km':None,'area_km2':None,
        'annual_extrema_eligible':False,'seasonal_playback_eligible':False,'nasa_individual_identity_claim':False,
        'source_license':'CC BY 4.0','source_license_url':'https://creativecommons.org/licenses/by/4.0/',
        'source_credit':'Adapted by OSW from Johnson Exley, Donohue, Watts, Tracey and Kennelly (2022), Figure 3; original authors retain copyright. Threshold tracing and figure-axis georeferencing are OSW transformations. Original complete source figure is available.',
        'runtime':{'opencv':cv2.__version__,'shapely':shapely.__version__,'numpy':np.__version__}}

def validate(doc):
    if doc!=build():raise ValueError('Ursa contour source, digitization, calibration or state evidence changed')
    return doc

def records(doc,geometry_id,source_id,snapshot_id):
    ident='footprint_candidate:ursa:2021-03-07'
    shared={'entity_id':OWNER,'observation_date':doc['observation_date'],'source_id':source_id,
        'source_snapshot_id':snapshot_id,'source_locator':doc['source_locator'],'method':doc['method']}
    geometry={**shared,'id':geometry_id,'role':'dated_figure_ssh_contour_proxy','geometry':doc['nominal_geometry'],
        'geometry_sha256':doc['geometry_sha256'],'candidate_id':ident,
        'coordinate_reference_system':doc['coordinate_reference_system'],'coordinate_reference_status':doc['coordinate_reference_status'],
        'positional_uncertainty':'Source-image threshold/stroke/axis scenarios; no physical uncertainty bound or survey accuracy established.',
        'source_pixel_ring':doc['source_pixel_ring'],'source_panel_axes_pixels':doc['source_panel_axes_pixels']}
    candidate={**shared,'id':ident,'geometry_id':geometry_id,'geometry_sha256':doc['geometry_sha256'],
        'boundary_type':'figure_digitized_instantaneous_ssh_contour_proxy','review_status':'not_individually_reviewed',
        'physical_limit':doc['physical_limit'],'source_audit_file':PATH,
        **{key:doc[key] for key in ['identity_status','state_assessments','source_document_sha256','source_image_sha256',
            'source_image_file','state_geometry_sha256','source_panel_axes_pixels','coordinate_reference_status',
            'segmentation_sensitivity_cases','rejected_segmentation_cases','scenario_polygon_count','scenario_attempt_count',
            'physical_boundary_admitted','annual_extrema_eligible','seasonal_playback_eligible',
            'source_credit','source_license_url']}}
    return geometry,candidate

if __name__=='__main__':
    doc=build();(ROOT/PATH).write_bytes((json.dumps(doc,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print('Ursa contour candidate:',doc['scenario_polygon_count'],'tested polygons;',doc['state_assessments'])
