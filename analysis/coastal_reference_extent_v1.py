"""Prospective local extent brackets; pure scalar profiles, no source IO or admission."""
from copy import deepcopy
import math


FRACTIONS = (.4,.5,.6)
FRAME = 'earth_velocity_projected_on_local_geodesic_tangent'
COORDINATE = 'signed_WGS84_geodesic_normal_km'
RISE_FRACTION = .01
MINIMUM_CELL_SCALES = 4
QUANTITIES = ('core_to_positive_normal_threshold_extent','local_two_sided_threshold_span',
    'finite_paired_support_to_positive_threshold_extent','shore_reference_to_positive_threshold_extent')


def finite(value):
    return type(value) in (int,float) and math.isfinite(value)


def interval(value):
    return isinstance(value,list) and len(value)==2 and all(finite(x) for x in value) and value[0]<=value[1]


def validate(profile):
    if profile.get('frame')!=FRAME or profile.get('coordinate')!=COORDINATE:
        raise ValueError('Unknown distance/projection frame')
    if (not isinstance(profile.get('case_id'),str) or not profile['case_id']
            or not isinstance(profile.get('source'),dict) or not profile['source']
            or not isinstance(profile.get('legacy_regional_gate'),dict)):
        raise ValueError('Case, source and unchanged legacy gate required')
    for key in ('q_representation_bound_m_s','offset_representation_bound_km'):
        if not finite(profile.get(key)) or profile[key]<0:
            raise ValueError('Explicit nonnegative representation bounds required')
    rows=profile['rows']
    if len(rows)<3 or any(not finite(row.get('s_km')) or not isinstance(row.get('status'),str) or not row['status'] for row in rows):
        raise ValueError('At least three ordered finite offsets required')
    if any(a['s_km']>=b['s_km'] for a,b in zip(rows,rows[1:])):
        raise ValueError('Duplicate or reversed offsets')
    step=profile.get('normal_sample_step_km')
    if step is not None and (not finite(step) or step<=0 or any(
            abs(b['s_km']-a['s_km']-step)>2*profile['offset_representation_bound_km']+1e-12
            for a,b in zip(rows,rows[1:]))):
        raise ValueError('Declared sampling step disagrees with retained offsets')
    if any(row.get('status')=='ok' and not finite(row.get('q_m_s')) for row in rows):
        raise ValueError('Supported rows need finite projected velocities')
    segments=profile['segments']
    if len(segments)!=len(rows)-1 or any(type(s.get('supported')) is not bool for s in segments):
        raise ValueError('Explicit support for every intervening segment required')
    if any('native_cell_scale_km' not in s for s in segments):
        raise ValueError('Declare native scale or explicit unknown for every segment')
    if any(s.get('native_cell_scale_km') is not None and
           (not finite(s['native_cell_scale_km']) or s['native_cell_scale_km']<=0) for s in segments):
        raise ValueError('Native scales must be positive finite values or explicit unknown')
    peak=profile['peak']
    kind=peak.get('support_kind','interior_unique_candidate')
    if kind not in ('interior_unique_candidate','one_sided_boundary_candidate'):
        raise ValueError('Unknown retained peak support kind')
    if (type(peak.get('index')) is not int or not 0<=peak['index']<len(rows)-1
            or kind=='interior_unique_candidate' and peak['index']==0):
        raise ValueError('Retained peak index with declared side support required')
    if (peak.get('unique_verified') is not True or peak.get('local_support_verified') is not True
            or not isinstance(peak.get('source_fingerprint'),str) or not peak['source_fingerprint']):
        raise ValueError('Retained peak support and provenance required')
    at=rows[peak['index']]
    if at['status']!='ok' or at['q_m_s']<=profile['q_representation_bound_m_s']:
        raise ValueError('Positive supported peak required')
    adjacent=(peak['index']-1,peak['index']) if kind=='interior_unique_candidate' else (peak['index'],)
    for i in adjacent:
        if not segments[i]['supported'] or rows[i]['status']!='ok' or rows[i+1]['status']!='ok':
            raise ValueError('Retained peak neighbors lack connected support')
    neighbor_indices=(peak['index']-1,peak['index']+1) if kind=='interior_unique_candidate' else (peak['index']+1,)
    if any(rows[i]['q_m_s']>at['q_m_s']+2*profile['q_representation_bound_m_s'] for i in neighbor_indices):
        raise ValueError('A retained peak cannot lie below an adjacent sample')
    return rows,segments,peak['index']


def row_bounds(profile,row):
    error=profile['q_representation_bound_m_s']
    return row['q_m_s']-error,row['q_m_s']+error


def offset_bounds(profile,row):
    error=profile['offset_representation_bound_km']
    return [row['s_km']-error,row['s_km']+error]


def level_bounds(profile,fraction):
    return [fraction*x for x in row_bounds(profile,profile['rows'][profile['peak']['index']])]


def crossing(profile,fraction,direction):
    rows,segments,peak=validate(profile)
    if fraction not in FRACTIONS or type(direction) is not int or direction not in (-1,1):
        raise ValueError('Use declared fractions and signed sides')
    level=level_bounds(profile,fraction)
    peak_low=row_bounds(profile,rows[peak])[0]
    minimum=peak_low; above=peak; previous=peak; used=[]; ambiguous=[]
    base={'status':'sample_limit_without_crossing','offset_bracket_km':None,
          'threshold_component_interval_m_s':level,'above_index':None,'below_index':None,
          'segment_indices':used,'ambiguous_sample_indices':ambiguous}
    for i in range(peak+direction,len(rows) if direction>0 else -1,direction):
        segment=min(previous,i);used.append(segment)
        if rows[i]['status']!='ok':
            return base|{'status':rows[i]['status']+'_before_crossing','stop_index':i}
        if not segments[segment]['supported']:
            return base|{'status':'unsupported_segment_before_crossing','stop_index':i}
        low,high=row_bounds(profile,rows[i])
        if high<=level[0]:
            a,b=offset_bounds(profile,rows[above]),offset_bounds(profile,rows[i])
            return base|{'status':'connected_sampled_crossing_bracket',
                'offset_bracket_km':[min(a[0],b[0]),max(a[1],b[1])],
                'above_index':above,'below_index':i}
        if high-minimum>RISE_FRACTION*peak_low:
            return base|{'status':'possible_competing_rise_before_crossing','stop_index':i}
        minimum=min(minimum,low)
        if low>level[1]:above=i
        else:ambiguous.append(i)
        previous=i
    return base


def support_reference(profile):
    """First negative supported-domain transition, never a physical shoreline."""
    rows,segments,peak=validate(profile)
    for i in range(peak-1,-1,-1):
        segment=i
        if rows[i]['status']=='ok' and segments[segment]['supported']:
            continue
        if rows[i]['status']=='outside_source':
            return {'status':'source_crop_is_not_inshore_reference','kind':'finite_paired_support_transition'}
        a,b=offset_bounds(profile,rows[i]),offset_bounds(profile,rows[i+1])
        return {'status':'sampled_support_transition','kind':'finite_paired_support_transition',
            'offset_bracket_km':[a[0],b[1]],'unsupported_index':i,'supported_index':i+1,
            'transition_segment_index':segment,'original_support_status':rows[i]['status'],
            'segment_supported':segments[segment]['supported'],
            'is_physical_shoreline':False,'inshore_flow_connectivity_verified':False}
    return {'status':'no_inshore_support_transition_retained','kind':'finite_paired_support_transition'}


def path_connection(profile,start,peak,fraction):
    level=level_bounds(profile,fraction)
    for i in range(start,peak+1):
        row=profile['rows'][i]
        if row['status']!='ok':return 'missing_reference_to_peak_support'
        if i<peak and not profile['segments'][i]['supported']:return 'unsupported_reference_to_peak_segment'
        if i==peak:continue  # The threshold shares this same positive reference amplitude.
        low,high=row_bounds(profile,row)
        if high<=level[0]:return 'reference_not_connected_to_sampled_threshold_core'
        if low<=level[1]:return 'reference_connection_ambiguous_at_stored_precision'
    return 'sampled_reference_to_peak_connection'


def unresolved_metric(kind,status,reference=None,edge=None):
    return {'quantity':kind,'status':status,'extent_bracket_km':None,
        'bracket_kind':'sampled_position_and_numeric_representation_bounds_not_physical_uncertainty',
        'reference':reference,'positive_edge':edge,'maximum_native_cell_scale_km':None,
        'minimum_span_in_native_cell_scales':None,'source_scale_gate_passed':False,
        'resolution_status':'not_evaluated','supported_path_lower_bound_km':None,
        'inshore_connection_verified':None if reference is None else reference.get('inshore_flow_connectivity_verified'),
        'conditional_on_inshore_flow_assumption':reference is not None and reference.get('kind')=='geographic_shoreline' and (
            reference.get('inshore_flow_connectivity_verified') is not True
            or reference.get('model_support_reaches_entire_shore_interval') is not True),
        'source_scale_gate_applies_to':'known_supported_model_path_only',
        'effective_resolution_verified':False,'is_confidence_interval':False,
        'whole_current_width_km':None,'width_rank_eligible':False,'physical_state_join_eligible':False,
        'physical_annual_range_eligible':False,'physical_uncertainty_km':None}


def dimension(profile,kind,reference,edge,segments,connection='sampled_reference_to_peak_connection'):
    result=unresolved_metric(kind,connection,reference,edge)
    if connection!='sampled_reference_to_peak_connection':return result
    if edge['status']!='connected_sampled_crossing_bracket':return result|{'status':edge['status']}
    if reference.get('status') not in ('sampled_support_transition','declared_shore_reference','retained_core_origin','connected_negative_crossing'):
        return result|{'status':reference['status']}
    low=edge['offset_bracket_km'][0]-reference['offset_bracket_km'][1]
    high=edge['offset_bracket_km'][1]-reference['offset_bracket_km'][0]
    if low<=0 or high<low:return result|{'status':'overlapping_or_reversed_boundary_brackets'}
    result['extent_bracket_km']=[low,high]
    scales=[profile['segments'][i]['native_cell_scale_km'] for i in sorted(set(segments))]
    if not scales or any(value is None for value in scales):
        return result|{'status':'unknown_native_scale','resolution_status':'unknown_native_scale'}
    start=reference.get('supported_start_index')
    supported_low=low if start is None else min(low,edge['offset_bracket_km'][0]-offset_bounds(profile,profile['rows'][start])[1])
    scale=max(scales);ratio=supported_low/scale
    result.update(maximum_native_cell_scale_km=scale,minimum_span_in_native_cell_scales=ratio,
        supported_path_lower_bound_km=supported_low,
        resolution_status='source_scale_supported' if ratio>=MINIMUM_CELL_SCALES else 'insufficient_native_scale_support',
        source_scale_gate_passed=ratio>=MINIMUM_CELL_SCALES,
        status='source_scale_supported_local_extent' if ratio>=MINIMUM_CELL_SCALES else 'insufficient_native_scale_support')
    if reference.get('kind')=='geographic_shoreline' and (
            reference['inshore_flow_connectivity_verified'] is not True
            or reference['model_support_reaches_entire_shore_interval'] is not True):
        result['status']='conditional_shore_to_edge_extent_with_unresolved_inshore_strip'
    return result


def analyse(profile,shore=None):
    rows,segments,peak=validate(profile)
    if shore is not None:
        if (shore.get('kind')!='geographic_shoreline' or shore.get('status')!='declared_shore_reference'
                or not interval(shore.get('offset_bracket_km')) or not isinstance(shore.get('source_fingerprint'),str)
                or not shore['source_fingerprint']
                or type(shore.get('geometry_reviewed')) is not bool
                or type(shore.get('inshore_flow_connectivity_verified')) is not bool
                or shore['offset_bracket_km'][1]>rows[peak]['s_km']):
            raise ValueError('Explicit source-bound inshore shoreline interval required')
        shore=deepcopy(shore)
        start=peak
        while start>0 and rows[start-1]['status']=='ok' and segments[start-1]['supported']:
            start-=1
        floor=[i for i in range(start,peak+1) if rows[i]['s_km']<=shore['offset_bracket_km'][0]]
        if floor:start=max(floor)
        if 'supported_start_index' in shore and shore['supported_start_index']!=start:
            raise ValueError('Shore support start cannot select a favorable later sample')
        shore['supported_start_index']=start
        low,high=offset_bounds(profile,rows[start])
        shore['inshore_model_gap_bracket_km']=[max(0,low-shore['offset_bracket_km'][1]),
            max(0,high-shore['offset_bracket_km'][0])]
        shore['model_support_reaches_entire_shore_interval']=shore['inshore_model_gap_bracket_km'][1]==0
    reference=support_reference(profile)
    variants=[]
    for fraction in FRACTIONS:
        negative=crossing(profile,fraction,-1);positive=crossing(profile,fraction,1)
        core={'status':'retained_core_origin','kind':'retained_peak',
            'offset_bracket_km':offset_bounds(profile,rows[peak]),'source_fingerprint':profile['peak']['source_fingerprint']}
        metrics=[dimension(profile,'core_to_positive_normal_threshold_extent',core,positive,positive['segment_indices'])]
        neg_reference={'status':'connected_negative_crossing' if negative['status']=='connected_sampled_crossing_bracket' else negative['status'],
            'kind':'negative_threshold_crossing','offset_bracket_km':negative['offset_bracket_km'],'original_edge':negative}
        metrics.append(dimension(profile,'local_two_sided_threshold_span',neg_reference,positive,
            negative['segment_indices']+positive['segment_indices']))
        start=reference.get('supported_index')
        connection=(path_connection(profile,start,peak,fraction) if start is not None else reference['status'])
        path=list(range(start,peak)) if start is not None else []
        if reference.get('transition_segment_index') is not None:path.append(reference['transition_segment_index'])
        metrics.append(dimension(profile,'finite_paired_support_to_positive_threshold_extent',reference,positive,
            path+positive['segment_indices'],connection))
        if shore is not None:
            start=shore['supported_start_index'];connection=path_connection(profile,start,peak,fraction)
            if not shore['geometry_reviewed']:connection='shore_reference_geometry_unreviewed'
            metrics.append(dimension(profile,'shore_reference_to_positive_threshold_extent',shore,positive,
                list(range(start,peak))+positive['segment_indices'],connection))
        else:
            metrics.append(unresolved_metric('shore_reference_to_positive_threshold_extent','no_independent_shore_reference'))
        variants.append({'fraction':fraction,'metrics':metrics})
    return deepcopy({'schema':'osw.coastal-reference-extent.v1','status':'local_method_development_not_measurement_admission',
        'evidence_class':'local_sampled_reference_extent_method_development','current_association_verified':False,
        'width_rank_eligible':False,'physical_state_join_eligible':False,
        'case_id':profile['case_id'],'source':profile['source'],'legacy_regional_gate':profile['legacy_regional_gate'],
        'frame':profile['frame'],'coordinate':profile['coordinate'],
        'normal_sample_step_km':profile.get('normal_sample_step_km'),
        'peak_support_kind':profile['peak'].get('support_kind','interior_unique_candidate'),
        'q_representation_bound_m_s':profile['q_representation_bound_m_s'],
        'offset_representation_bound_km':profile['offset_representation_bound_km'],
        'positive_normal_is_verified_offshore':profile.get('positive_normal_is_verified_offshore',False),
        'variants':variants,'new_current_measurements_admitted':0,'whole_current_width_km':None,
        'physical_annual_minimum_width_km':None,'physical_annual_maximum_width_km':None,
        'physical_uncertainty_km':None})


def analyse_cases(cases):
    """Retain every12x3x2 attempt; a missing input remains a visible outcome."""
    expected={(m,o,s) for m in range(1,13) for o in (-1,0,1) for s in (5,10)}
    if (len(cases)!=72 or any(type(c[key]) is not int for c in cases for key in
            ('month','native_latitude_offset','normal_sample_step_km')) or len({c['id'] for c in cases})!=72
            or {(c['month'],c['native_latitude_offset'],c['normal_sample_step_km']) for c in cases}!=expected):
        raise ValueError('Complete unique twelve-month case set required')
    outputs=[]
    for case in cases:
        identity=f"m{case['month']:02d}:offset{case['native_latitude_offset']}:step{case['normal_sample_step_km']}"
        if case['id']!=identity:raise ValueError('Case id disagrees with month/offset/step')
        profile=case.get('profile')
        if profile is None:
            outputs.append({'case_id':identity,'status':'missing_supported_profile',
                'source_status':case['source_status'],'legacy_regional_gate':deepcopy(case['legacy_regional_gate']),
                'new_current_measurements_admitted':0,'whole_current_width_km':None,
                'variants':[{'fraction':fraction,'metrics':[unresolved_metric(quantity,'missing_supported_profile')
                    for quantity in QUANTITIES]} for fraction in FRACTIONS]})
        else:
            if (profile['case_id']!=identity or profile['legacy_regional_gate']!=case['legacy_regional_gate']
                    or profile.get('normal_sample_step_km')!=case['normal_sample_step_km']):
                raise ValueError('Profile identity or legacy gate changed')
            answer=analyse(profile,case.get('shore'))
            answer['source_status']=case['source_status']
            outputs.append(answer)
    return {'schema':'osw.coastal-reference-extent-cases.v1','case_count':72,'cases':outputs,
        'current_association_verified':False,'width_rank_eligible':False,'physical_state_join_eligible':False,
        'all_months_and_failures_retained':True,'method_development':True,'new_current_measurements_admitted':0,
        'whole_current_width_km':None,'physical_annual_width_range_km':None,'physical_uncertainty_km':None}
