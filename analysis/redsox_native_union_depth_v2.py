"""Piecewise native-source predicate tracing without hiding finer hydrographic knots."""
import bisect,math
from build_redsox_lower_nc_section import interpolate_complete


def finite(v):return type(v) in (int,float) and math.isfinite(v)


def validate_axis(z,values,limit,value_limit):
    if not 2<=len(z)<=limit or len(z)!=len(values) or not all(finite(v) and v>=0 for v in z) or any(b<=a for a,b in zip(z,z[1:])):raise ValueError('Complete bounded increasing original depth axis required')
    if any(v is not None and (not finite(v) or not value_limit(v)) for v in values):raise ValueError('Finite or explicit missing original source values required')


def at_depth(z,values,target,gap):
    j=bisect.bisect_left(z,target)
    if j<len(z) and z[j]==target:return values[j],[j,j],'exact_missing' if values[j] is None else 'exact'
    if j==0 or j==len(z):return None,None,'outside'
    indices=[j-1,j]
    if z[j]-z[j-1]>gap:return None,indices,'gap'
    if values[j-1] is None or values[j] is None:return None,indices,'missing'
    return float(interpolate_complete(z,values,[target],max_gap=gap)[0]),indices,'interpolated'


def source_segment(z,values,a,b,gap):
    if not a<b:raise ValueError('Positive union segment required')
    i=bisect.bisect_right(z,a)-1
    if i<0 or i+1>=len(z) or b>z[-1]:return None,'outside'
    if b>z[i+1]:raise ValueError('Union grid omitted a native source knot')
    indices=[i,i+1]
    if z[i+1]-z[i]>gap:return indices,'gap'
    if values[i] is None or values[i+1] is None:return indices,'missing'
    return indices,'ok'


def union_grid(vz,q,hz,s,source_core):
    validate_axis(vz,q,300,lambda v:abs(v)<=10);validate_axis(hz,s,2000,lambda v:0<=v<=50)
    if type(source_core)!=int or not 0<=source_core<len(vz):raise ValueError('Frozen native velocity core required')
    z=sorted(set(vz)|{v for v in hz if vz[0]<=v<=vz[-1]})
    if len(z)>6000:raise ValueError('Fixed per-case node cap exceeded')
    qmap=[at_depth(vz,q,v,20) for v in z];smap=[at_depth(hz,s,v,5) for v in z]
    qedges=[source_segment(vz,q,a,b,20) for a,b in zip(z,z[1:])];sedges=[source_segment(hz,s,a,b,5) for a,b in zip(z,z[1:])]
    return {'depth_m':z,'component_m_s':[v[0] for v in qmap],'salinity_psu':[v[0] for v in smap],'velocity_node_source_indices':[v[1] for v in qmap],'salinity_node_source_indices':[v[1] for v in smap],'velocity_node_mapping_status':[v[2] for v in qmap],'salinity_node_mapping_status':[v[2] for v in smap],'velocity_segment_source_indices':[v[0] for v in qedges],'salinity_segment_source_indices':[v[0] for v in sedges],'velocity_segment_support':[v[1] for v in qedges],'salinity_segment_support':[v[1] for v in sedges],'source_velocity_core_index':source_core,'seed_union_index':z.index(vz[source_core]),'source_velocity_node_count':len(vz),'source_hydrographic_node_count':len(hz),'union_node_count':len(z),'new_independent_samples':0,'interpolated_velocity_is_new_observation':False,'union_spacing_is_native_velocity_resolution':False}


def diagnose(grid):
    z=grid['depth_m'];q=grid['component_m_s'];s=grid['salinity_psu'];core=grid['seed_union_index']
    if not 2<=len(z)<=6000 or len(q)!=len(z) or len(s)!=len(z) or any(len(grid[k])!=len(z)-1 for k in ['velocity_segment_source_indices','salinity_segment_source_indices','velocity_segment_support','salinity_segment_support']):raise ValueError('Exact union-grid nodes and segments required')
    validate_axis(z,q,6000,lambda v:abs(v)<=10);validate_axis(z,s,6000,lambda v:0<=v<=50)
    if type(core)!=int or not 0<=core<len(z) or type(grid['source_velocity_core_index'])!=int or not 0<=grid['source_velocity_core_index']<grid['source_velocity_node_count']:raise ValueError('Original native and union core indices required')
    if any(v not in ['ok','outside','gap','missing'] for k in ['velocity_segment_support','salinity_segment_support'] for v in grid[k]):raise ValueError('Explicit native source segment support required')
    result={'source_velocity_core_index':grid['source_velocity_core_index'],'seed_union_index':core,'original_core_depth_m':z[core],'velocity_threshold_m_s':.2,'practical_salinity_inclusive_lower_threshold':38,'core_reselected':False,'all_native_hydrographic_knots_within_velocity_domain_retained':True,'physical_current_bottom_established':False,'physical_layer_thickness_m':None,'volume_eligible':False,'annual_extrema_established':False}
    if q[core] is None or s[core] is None:return {**result,'status':'original_core_missing_input','upper':None,'lower':None,'joint_support_span_m':None}
    if q[core]<=.2:return {**result,'status':'original_core_not_above_velocity_threshold','upper':None,'lower':None,'joint_support_span_m':None}
    if s[core]<38:return {**result,'status':'original_velocity_core_not_in_declared_saline_class','upper':None,'lower':None,'joint_support_span_m':None}
    def boundary(step):
        i=core
        while True:
            j=i+step
            base={'last_connected_union_index':i,'last_connected_depth_m':z[i],'boundary_depth_m':None,'fine_union_bracket_m':None,'limiting_criteria':[]}
            if not 0<=j<len(z):return {**base,'status':'censored_at_native_velocity_sampling_end'}
            edge=min(i,j);base.update(next_union_index=j,source_velocity_segment_indices=grid['velocity_segment_source_indices'][edge],source_hydrographic_segment_indices=grid['salinity_segment_source_indices'][edge],velocity_segment_support=grid['velocity_segment_support'][edge],salinity_segment_support=grid['salinity_segment_support'][edge])
            if grid['velocity_segment_support'][edge]!='ok' or grid['salinity_segment_support'][edge]!='ok':return {**base,'status':'censored_before_incomplete_native_source_segment'}
            if q[j] is None or s[j] is None:return {**base,'status':'censored_before_missing_union_input'}
            if q[j]>.2 and s[j]>=38:i=j;continue
            crossings=[]
            if q[j]<=.2:crossings.append(('velocity',z[i]+(.2-q[i])*(z[j]-z[i])/(q[j]-q[i])))
            if s[j]<38:crossings.append(('salinity',z[i]+(38-s[i])*(z[j]-z[i])/(s[j]-s[i])))
            value=(min if step>0 else max)(d for name,d in crossings)
            return {**base,'status':'first_adjacent_union_joint_predicate_crossing','boundary_depth_m':value,'fine_union_bracket_m':sorted([z[i],z[j]]),'candidate_crossings_m':dict(crossings),'limiting_criteria':[name for name,d in crossings if d==value]}
    upper,lower=boundary(-1),boundary(1);a,b=upper['boundary_depth_m'],lower['boundary_depth_m']
    return {**result,'status':'conditional_saline_component_core_supported','upper':upper,'lower':lower,'joint_support_span_m':b-a if a is not None and b is not None else None}
