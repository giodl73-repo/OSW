"""Cloud-only independent Indian60-160m checks and exact retained-pilot reconstruction."""
import math,hashlib,json
def independent(z,u,threshold):
    candidates=[i for i in range(len(z)) if 60<=z[i]<=160 and u[i] is not None and u[i]>threshold]
    if not candidates:return {'core':None,'upper':None,'lower':None,'span':None}
    core=max(candidates,key=lambda i:u[i])
    edges=[]
    for direction in [-1,1]:
        i=core;crossing=None
        while 0<=i+direction<len(z):
            j=i+direction
            if abs(z[j]-z[i])>15 or u[j] is None:break
            if u[j]<=threshold:
                # Distinct weighted-endpoint expression from the frozen kernel.
                crossing=(z[i]*(u[j]-threshold)+z[j]*(threshold-u[i]))/(u[j]-u[i])
                break
            i=j
        edges.append(crossing)
    upper,lower=edges
    return {'core':core,'upper':upper,'lower':lower,'span':lower-upper if upper is not None and lower is not None else None}


def equal_number(actual,expected):
    if (actual is None)!=(expected is None) or (actual is not None and not math.isclose(actual,expected,rel_tol=1e-12,abs_tol=1e-10)):
        raise ValueError('Independent retained-sample boundary calculation disagrees')


def verify_profile(p):
    z=p['source_depths_m'];u=p['accepted_eastward_velocity_m_s']
    if len(z)>30 or len(u)!=len(z) or len(p['source_u_cm_s'])!=len(z) or len(p['source_u_quality'])!=len(z):
        raise ValueError('Original source profile shapes and thirty-level cap required')
    for raw,quality,accepted in zip(p['source_u_cm_s'],p['source_u_quality'],u):
        wanted=raw/100 if raw is not None and quality in [1,2] else None
        equal_number(accepted,wanted)
    if len(z)<2:
        if p['threshold_contexts'] or p['primary_lower_isotach_depth_m'] is not None:raise ValueError('No fabricated boundaries for absent profile')
        return
    if len(p['threshold_contexts'])!=3:raise ValueError('All three declared threshold contexts required')
    for threshold,layer in zip([.05,.1,.2],p['threshold_contexts']):
        check=independent(z,u,threshold)
        if layer['threshold_m_s']!=threshold or layer.get('core_index')!=check['core']:raise ValueError('Original locked core must reproduce independently')
        for key,expected in [('upper_depth_m',check['upper']),('lower_depth_m',check['lower']),('layer_thickness_m',check['span'])]:
            equal_number(layer[key],expected)
    check=independent(z,u,.1);eligible=check['core'] is not None and z[check['core']] not in [60,160]
    if p['primary_core_window_interior']!=eligible:raise ValueError('No source-window-edge promotion')
    equal_number(p['primary_lower_isotach_depth_m'],check['lower'] if eligible else None)
    equal_number(p['primary_threshold_layer_span_m'],check['span'] if eligible else None)
    for key in ['physical_current_thickness_m','annual_range_m','volume_m3']:
        if p[key] is not None:raise ValueError('Velocity proxy cannot become physical depth/range/volume')
    if p['physical_current_identity_independently_verified'] or p['daily_underlying_sample_coverage_verified'] or p['mean_field_depth_is_mean_instantaneous_depth']:
        raise ValueError('No identity/coverage/temporal-operator promotion')


def verify_indian_profile(p):
    verify_profile(p)
    z=p['source_depths_m'];u=p['accepted_eastward_velocity_m_s']
    primary=independent(z,u,.1) if len(z)>=2 else {'core':None}
    interior=primary['core'] is not None and z[primary['core']] not in [60,160]
    upper=dict(zip(z,u));values=[upper.get(d) for d in [40,50]]
    reference=max(values) if all(v is not None for v in values) else None
    contrast=u[primary['core']]-reference if interior and reference is not None else None
    candidate=bool(contrast is not None and (contrast>=.1 or math.isclose(contrast,.1,rel_tol=0,abs_tol=1e-12)))
    equal_number(p['observed_upper_reference_max_m_s'],reference)
    equal_number(p['operational_core_upper_reference_contrast_m_s'],contrast)
    if p['operational_daily_context_candidate']!=candidate:raise ValueError('Independent upper-reference context mismatch')
    for key in ['true_surface_comparison_verified','thermocline_membership_independently_verified']:
        if p[key]:raise ValueError('Unobserved surface/thermocline context cannot be promoted')


def reconstruct_2005(root):
    import collect_indian_euc_rama_2005_depth_v1 as prior
    folder=root/'research/source-data/indian-euc-rama-2005-depth-v1'
    plan=json.loads((folder/'field-plan.json').read_bytes())
    journal=json.loads((folder/'journal.json').read_bytes())
    original=json.loads((folder/'profiles.json').read_bytes())
    if plan!=prior.plan() or len(journal['requests'])!=8:raise ValueError('Exact closed pilot scope required')
    rebuilt=[];decoded=0;checked=0
    for target,receipt in zip(plan,journal['requests']):
        if receipt['url']!=target['url'] or receipt['target_id']!=target['target_id'] or receipt['attempts']!=1:
            raise ValueError('Exact one-attempt prior custody required')
        if target['nominal_longitude']==90:
            if receipt.get('source_http_status')!=503 or receipt['bytes_received']!=0:raise ValueError('Original503 source failure required')
            values=[prior.profile(t,target) for t in target['times_utc']]
            for p in values:p['source_status']='attempted_transport_failure_no_retry'
        else:
            raw=(folder/receipt['raw_file']).read_bytes()
            if hashlib.sha256(raw).hexdigest()!=receipt['sha256'] or len(raw)!=receipt['bytes_received']:raise ValueError('Exact retained raw bytes required')
            values,n=prior.parse_patch(raw,target);decoded+=n
            for p in values:verify_indian_profile(p);checked+=len(p['threshold_contexts'])
        rebuilt.extend(values)
    runs=prior.mark_persistence(rebuilt)
    if rebuilt!=original['profiles'] or runs!=original['operational_persistence_runs'] or decoded!=1944 or checked!=36:
        raise ValueError('Exact132 prior outcomes and36 independent threshold contexts required')
    return {'status':'PASS_EXACT132_OUTCOMES_AND36_INDEPENDENT_CONTEXTS','provider_requests':0,
            'source_profiles':12,'planned_outcomes':132,'field_scalars_decoded':decoded,
            'independent_threshold_contexts':checked,'failed_90E_persistence':'unassessable_source_HTTP503',
            'sparse_80p5E_persistence':'unassessed_by_design','current_absence_inferred':False,
            'new_named_current_references':0}
