"""Conditional EGCC fresh/component layer; not the published coastal front foot."""
import math


def finite(x):return type(x) in (int,float) and math.isfinite(x)


def diagnose(z,velocity,salinity,core,velocity_threshold=.1,salinity_threshold=34):
    if velocity_threshold!=.1 or salinity_threshold!=34:raise ValueError('Frozen original component and source salinity thresholds required')
    if len(z)!=len(velocity) or len(z)!=len(salinity) or len(z)<2 or not all(finite(x) and x>=0 for x in z) or any(b<=a for a,b in zip(z,z[1:])) or type(core)!=int or not 0<=core<len(z):raise ValueError('Original increasing native axis and valid core required')
    if any(x is not None and not finite(x) for x in velocity+salinity) or any(x is not None and not 0<=x<=50 for x in salinity):raise ValueError('Finite or explicit missing native inputs required')
    result={'original_core_index':core,'original_core_depth_m':z[core],'velocity_threshold_m_s':velocity_threshold,'practical_salinity_exclusive_upper_threshold':salinity_threshold,'core_reselected':False,'physical_current_bottom_established':False,'physical_layer_thickness_m':None,'volume_eligible':False,'independently_validated_current_axis':False,'annual_extrema_established':False}
    if velocity[core] is None or salinity[core] is None:return {**result,'status':'original_core_missing_input','upper':None,'lower':None}
    if velocity[core]<=velocity_threshold:return {**result,'status':'original_core_not_above_original_velocity_threshold','upper':None,'lower':None}
    if salinity[core]>=salinity_threshold:return {**result,'status':'original_velocity_core_not_in_declared_fresh_class','upper':None,'lower':None}
    def boundary(step):
        i=core
        while True:
            j=i+step
            if not 0<=j<len(z):return {'status':'surface_sample_supported' if step<0 and z[i]==0 else 'censored_at_native_domain_end','last_connected_native_index':i,'last_connected_depth_m':z[i],'boundary_depth_m':None,'bracket_m':None,'limiting_criteria':[]}
            if velocity[j] is None or salinity[j] is None:return {'status':'censored_before_missing_native_input','last_connected_native_index':i,'last_connected_depth_m':z[i],'next_native_index':j,'next_native_depth_m':z[j],'missing_inputs':[name for name,a in [('velocity',velocity),('salinity',salinity)] if a[j] is None],'boundary_depth_m':None,'bracket_m':None,'limiting_criteria':[]}
            if velocity[j]>velocity_threshold and salinity[j]<salinity_threshold:i=j;continue
            crossings=[]
            if velocity[j]<=velocity_threshold:crossings.append(('velocity',z[i]+(velocity_threshold-velocity[i])*(z[j]-z[i])/(velocity[j]-velocity[i])))
            if salinity[j]>=salinity_threshold:crossings.append(('salinity',z[i]+(salinity_threshold-salinity[i])*(z[j]-z[i])/(salinity[j]-salinity[i])))
            depth=(min if step>0 else max)(d for _,d in crossings)
            return {'status':'adjacent_native_joint_predicate_crossing','last_connected_native_index':i,'last_connected_depth_m':z[i],'next_native_index':j,'next_native_depth_m':z[j],'boundary_depth_m':depth,'bracket_m':sorted([z[i],z[j]]),'limiting_criteria':[name for name,d in crossings if d==depth],'candidate_crossings_m':dict(crossings)}
    return {**result,'status':'conditional_fresh_component_core_supported','upper':boundary(-1),'lower':boundary(1)}
