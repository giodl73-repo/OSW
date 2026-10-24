"""Verify retained EACC profiles and adapt them for a separately defined extent case.

No source IO, acquisition, compiler, diagnose_year or original figure producer.
Readonly Field/geodesic primitives verify the retained records; calculated
extents use the stored, rounded q values with explicit representation guards.
Original-data invocation belongs exclusively in a separately gated cloud runner.
"""
from copy import deepcopy
import math

from coastal_reference_extent_v1 import FRAME,COORDINATE,analyse_cases,finite
from indian_secc_local_normals import normal_point
from west_australian_regional_streamlines import Field,GEOD


Q_BOUND = 5.000001e-9
OFFSET_BOUND_KM = 5.000001e-7
COORDINATE_BOUND_DEGREES = 5.000001e-9
SOURCE_SCHEMA = 'osw.eacc-regional-model-core.numerical-diagnostic.v2'
FIELDS_SCHEMA = 'osw.eacc-hycom.monthly-vector-fields.v1'


class NativeGeometry:
    """All cells in the sampler's conservative segment bounding rectangle."""
    def __init__(self,field):
        self.field=field;self.cache={}

    def cell_scale(self,yi,xi):
        key=(yi,xi)
        if key not in self.cache:
            west,east=map(float,self.field.x[xi:xi+2])
            south,north=map(float,self.field.y[yi:yi+2])
            edges=((west,south,east,south),(west,north,east,north),
                   (west,south,west,north),(east,south,east,north))
            self.cache[key]=max(GEOD.inv(*edge)[2]/1000 for edge in edges)
        return self.cache[key]

    def segment_scale(self,start,end):
        left=self.field.cell(min(start[0],end[0]),min(start[1],end[1]))
        right=self.field.cell(max(start[0],end[0]),max(start[1],end[1]))
        if left is None or right is None:return None
        return max(self.cell_scale(yi,xi) for yi in range(left[0],right[0]+1)
                   for xi in range(left[1],right[1]+1))


def near(actual,expected,bound):
    return finite(actual) and finite(expected) and abs(actual-expected)<=bound+math.ulp(actual)+math.ulp(expected)


def verify_retained_profile(case,field):
    """Reconstruct frame/support only; never replace stored samples or choose a peak."""
    initial=case.get('initial_refinement')
    if initial is None:return None,{'status':'no_original_initial_refinement'}
    samples=initial['samples'];step=case['normal_sample_step_km']
    if not samples:return None,{'status':'empty_original_initial_profile'}
    if any(len(row)!=9 for row in samples) or any(a[0]>=b[0] for a,b in zip(samples,samples[1:])):
        raise ValueError('Malformed original packed profile inventory')
    if any(not near(b[0]-a[0],step,2*OFFSET_BOUND_KM) for a,b in zip(samples,samples[1:])):
        raise ValueError('Original profile sampling step changed')
    seed=case.get('seed') or {}
    if seed.get('status')!='supported_northward_seed':
        raise ValueError('Initial profile exists without its supported original seed')
    origin=seed['origin_lon_lat']
    velocity=field.sample(*origin)
    if velocity is None:raise ValueError('Original seed lost source-field support')
    bearing=math.degrees(math.atan2(velocity[0],velocity[1]))%360
    computed=[]
    for row in samples:
        if not finite(row[0]) or not finite(row[1]) or not finite(row[2]) or not isinstance(row[-1],str):
            raise ValueError('Nonfinite original profile coordinate or status')
        point,tangent=normal_point(tuple(origin),bearing,row[0])
        if not near(row[1],point[0],COORDINATE_BOUND_DEGREES) or not near(row[2],point[1],COORDINATE_BOUND_DEGREES):
            raise ValueError('Retained point disagrees with original WGS84 normal')
        cell=field.cell(*point);uv=field.sample(*point) if cell is not None else None
        status='outside_source' if cell is None else 'missing_paired_corner' if uv is None else 'ok'
        if list(cell or (None,None))!=row[6:8]:
            raise ValueError('Retained native cell indices changed')
        computed.append({'point':point,'tangent':tangent,'cell':cell,'velocity':uv,'base_status':status})
    centers=[i for i,row in enumerate(samples) if row[0]==0]
    if len(centers)!=1:raise ValueError('One retained zero-offset seed is required')
    center=centers[0]
    for i,(row,check) in enumerate(zip(samples,computed)):
        expected=check['base_status']
        if i!=center and expected=='ok':
            closer=i+1 if i<center else i-1
            if not field.supported_rectangle(computed[closer]['point'],check['point']):
                expected='unsupported_rectangle'
        if row[-1]!=expected:raise ValueError('Retained sample support disagrees with original field/mask')
        if row[-1]=='ok':
            u,v=check['velocity'];angle=math.radians(check['tangent'])
            q=u*math.sin(angle)+v*math.cos(angle)
            if not all(near(value,truth,Q_BOUND) for value,truth in zip(row[3:6],(u,v,q))):
                raise ValueError('Retained Earth components or projected q disagree with the source')
        elif any(value is not None for value in row[3:6]):
            raise ValueError('Unsupported original velocities were filled or changed')
    # Each original side stops at its first unsupported sample.
    for indices in (range(center-1,-1,-1),range(center+1,len(samples))):
        stopped=False
        for i in indices:
            if stopped:raise ValueError('Original profile continues beyond its first unsupported sample')
            stopped=samples[i][-1]!='ok'
    peak=initial['peak']
    if (peak.get('usable_for_thresholds') is not True or len(peak.get('tie_offsets_km',[]))!=1
            or type(peak.get('index')) is not int):
        return None,{'status':'original_initial_peak_not_usable','original_peak_status':peak.get('status'),
            'frame_and_support_verified':True,'sample_count':len(samples),'seed_bearing_degrees_true':bearing}
    at=peak['index']
    if not 0<at<len(samples)-1 or samples[at][0]!=peak['peak_offset_km']:
        raise ValueError('Retained original peak index/offset changed')
    if not near(samples[at][5],peak['peak_projected_m_s'],2*Q_BOUND):
        raise ValueError('Retained peak component changed')
    geometry=NativeGeometry(field)
    segments=[]
    for i in range(len(samples)-1):
        a,b=computed[i]['point'],computed[i+1]['point']
        supported=samples[i][-1]==samples[i+1][-1]=='ok' and field.supported_rectangle(a,b)
        segments.append({'supported':bool(supported),'native_cell_scale_km':geometry.segment_scale(a,b)})
    audit={'status':'retained_frame_support_and_peak_verified','frame_and_support_verified':True,
        'sample_count':len(samples),'seed_bearing_degrees_true':bearing,
        'positive_normal_is_eastward':math.cos(math.radians(bearing))>0,
        'positive_normal_is_verified_offshore':False,
        'original_peak_status':peak['status'],'native_scale_cells_touched':len(geometry.cache),
        'primitive_verification_only':True,'anchor_or_peak_reselected':False}
    return {'rows':samples,'segments':segments,'peak':peak},audit


def adapt_case(case,field,source):
    legacy={key:case[key] for key in ('status','all_five_local_axis_checks_pass','all_five_half_peak_spans_resolved')}
    source_status=case['status'];verified,audit=verify_retained_profile(case,field)
    output={'id':case['id'],'month':case['month'],'native_latitude_offset':case['native_latitude_offset'],
        'normal_sample_step_km':case['normal_sample_step_km'],'source_status':source_status,
        'legacy_regional_gate':deepcopy(legacy),'profile':None,'adapter_audit':audit}
    if verified is None:return output
    rows,peak=verified['rows'],verified['peak']
    output['profile']={'case_id':case['id'],'source':deepcopy(source)|{
        'original_case_id':case['id'],'original_seed_lon_lat':deepcopy(case['seed']['origin_lon_lat']),
        'source_model_year':2013,'provider_standard_output_depth_m':15,
        'time_support':'daily00Z sample monthly means, not observations/climatology/mean instantaneous width'},
        'legacy_regional_gate':deepcopy(legacy),'frame':FRAME,'coordinate':COORDINATE,
        'normal_sample_step_km':case['normal_sample_step_km'],
        'q_representation_bound_m_s':Q_BOUND,'offset_representation_bound_km':OFFSET_BOUND_KM,
        'positive_normal_is_verified_offshore':False,
        'rows':[{'s_km':row[0],'q_m_s':row[5],'status':row[-1]} for row in rows],
        'segments':verified['segments'],
        'peak':{'index':peak['index'],'unique_verified':True,'local_support_verified':True,
            'support_kind':'interior_unique_candidate',
            'source_fingerprint':source['diagnostic_sha256']+':'+case['id']+':initial_refinement'}}
    return output


def adapt_cases(diagnostic,fields,source):
    if diagnostic.get('schema')!=SOURCE_SCHEMA or fields.get('schema')!=FIELDS_SCHEMA:
        raise ValueError('Unexpected retained source schemas')
    if fields.get('source_model_year')!=2013 or fields.get('provider_depth_m')!=15:
        raise ValueError('Wrong declared original model year/depth')
    if [month['month'] for month in fields['months']]!=list(range(1,13)):
        raise ValueError('All original source months required in calendar order')
    if diagnostic.get('current_association_verified') is not False:
        raise ValueError('Original regional diagnostic association must remain unverified')
    for key in ('longitude_degrees_east','latitude_degrees_north'):
        axis=fields[key]
        if len(axis)<2 or any(not finite(value) for value in axis) or any(a>=b for a,b in zip(axis,axis[1:])):
            raise ValueError('Original native axes must remain finite and ascending')
    cases=diagnostic['cases']
    expected={(m,o,s) for m in range(1,13) for o in (-1,0,1) for s in (5,10)}
    if (len(cases)!=72 or len({case['id'] for case in cases})!=72 or
            any(type(c[key]) is not int for c in cases for key in ('month','native_latitude_offset','normal_sample_step_km')) or
            {(c['month'],c['native_latitude_offset'],c['normal_sample_step_km']) for c in cases}!=expected):
        raise ValueError('Complete original72-case identity set required')
    if any(c['id']!=f"m{c['month']:02d}:offset{c['native_latitude_offset']}:step{c['normal_sample_step_km']}" for c in cases):
        raise ValueError('Original case id disagrees with its source fields')
    grid={month['month']:Field(fields['longitude_degrees_east'],fields['latitude_degrees_north'],
        month['eastward_m_s'],month['northward_m_s']) for month in fields['months']}
    adapted=[adapt_case(case,grid[case['month']],source) for case in cases]
    return adapted


def analyse_saved_case(diagnostic,fields,source):
    """New extent operator only; original case and input dictionaries are unchanged."""
    adapted=adapt_cases(diagnostic,fields,source)
    output=analyse_cases(adapted)
    audits={case['id']:case['adapter_audit'] for case in adapted}
    for case in output['cases']:case['adapter_audit']=audits[case['case_id']]
    output['source']=deepcopy(source)
    output['source_model_year']=2013;output['provider_standard_output_depth_m']=15
    output['time_support']='daily00Z sample monthly means, not observations/climatology/mean instantaneous width'
    output['investigated_current_id']='current:east-african-coastal'
    output['old_producer_rerun']=False;output['new_provider_requests']=0
    output['independent_shore_reference_supplied']=False
    output['scope']='Post2013-failure method development; local sampled extent brackets, not physical whole-current widths.'
    return output
