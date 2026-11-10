"""Native velocity-depth support conditional on a separately remapped salinity screen."""
import math


def finite(v):return type(v) in (int,float) and math.isfinite(v)


def diagnose(z,q,s,core):
    if len(z)!=len(q) or len(z)!=len(s) or not 2<=len(z)<=300 or not all(finite(x) and x>=0 for x in z) or any(b<=a for a,b in zip(z,z[1:])) or type(core)!=int or not 0<=core<len(z):raise ValueError('Bounded increasing native velocity depths and original core required')
    if any(v is not None and (not finite(v) or abs(v)>10) for v in q) or any(v is not None and (not finite(v) or not 0<=v<=50) for v in s):raise ValueError('Finite native component and finite-or-missing practical salinity required')
    result={'original_core_index':core,'original_core_depth_m':z[core],'velocity_threshold_m_s':.2,'practical_salinity_inclusive_lower_threshold':38,'maximum_native_velocity_depth_gap_m':20,'core_reselected':False,'physical_current_bottom_established':False,'physical_layer_thickness_m':None,'volume_eligible':False,'annual_extrema_established':False}
    if q[core] is None or s[core] is None:return {**result,'status':'original_core_missing_input','upper':None,'lower':None,'joint_support_span_m':None}
    if q[core]<=.2:return {**result,'status':'original_core_not_above_velocity_threshold','upper':None,'lower':None,'joint_support_span_m':None}
    if s[core]<38:return {**result,'status':'original_velocity_core_not_in_declared_saline_class','upper':None,'lower':None,'joint_support_span_m':None}
    def boundary(step):
        i=core
        while True:
            j=i+step
            if not 0<=j<len(z):return {'status':'censored_at_native_sampling_end','last_connected_native_index':i,'last_connected_depth_m':z[i],'boundary_depth_m':None,'bracket_m':None,'limiting_criteria':[]}
            if abs(z[j]-z[i])>20:return {'status':'censored_before_native_depth_gap','last_connected_native_index':i,'last_connected_depth_m':z[i],'next_native_index':j,'boundary_depth_m':None,'bracket_m':None,'limiting_criteria':[]}
            if q[j] is None or s[j] is None:return {'status':'censored_before_missing_input','last_connected_native_index':i,'last_connected_depth_m':z[i],'next_native_index':j,'boundary_depth_m':None,'bracket_m':None,'missing_inputs':[name for name,values in [('velocity',q),('remapped_salinity',s)] if values[j] is None],'limiting_criteria':[]}
            if q[j]>.2 and s[j]>=38:i=j;continue
            crossings=[]
            if q[j]<=.2:crossings.append(('velocity',z[i]+(.2-q[i])*(z[j]-z[i])/(q[j]-q[i])))
            if s[j]<38:crossings.append(('salinity',z[i]+(38-s[i])*(z[j]-z[i])/(s[j]-s[i])))
            value=(min if step>0 else max)(depth for name,depth in crossings)
            return {'status':'adjacent_native_velocity_depth_joint_crossing','last_connected_native_index':i,'next_native_index':j,'last_connected_depth_m':z[i],'boundary_depth_m':value,'bracket_m':sorted([z[i],z[j]]),'candidate_crossings_m':dict(crossings),'limiting_criteria':[name for name,depth in crossings if depth==value]}
    upper,lower=boundary(-1),boundary(1);a,b=upper['boundary_depth_m'],lower['boundary_depth_m']
    return {**result,'status':'conditional_saline_component_core_supported','upper':upper,'lower':lower,'joint_support_span_m':b-a if a is not None and b is not None else None}
