"""Reconstruct retained observations and independently verify every threshold crossing."""
import csv
import hashlib
import io
import json
import math
import urllib.request
from pathlib import Path
import collect_tao_pacific_euc_direct_source_v2 as source

ROOT=Path(__file__).resolve().parents[1]
OP='research/tao-pacific-euc-retained-depth-audit-operator-v1.json'
DATA='research/source-data/tao-pacific-euc-direct-source-v2'


def independent(z,u,threshold):
    candidates=[i for i in range(len(z)) if 50<=z[i]<=250 and u[i] is not None and u[i]>threshold]
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
    if len(z)>40 or len(u)!=len(z) or len(p['source_u_cm_s'])!=len(z) or len(p['source_u_quality'])!=len(z):
        raise ValueError('Original source profile shapes and forty-level cap required')
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
    check=independent(z,u,.1);eligible=check['core'] is not None and z[check['core']] not in [50,250]
    if p['primary_core_window_interior']!=eligible:raise ValueError('No source-window-edge promotion')
    equal_number(p['primary_lower_isotach_depth_m'],check['lower'] if eligible else None)
    equal_number(p['primary_threshold_layer_span_m'],check['span'] if eligible else None)
    for key in ['physical_current_thickness_m','annual_range_m','volume_m3']:
        if p[key] is not None:raise ValueError('Velocity proxy cannot become physical depth/range/volume')
    if p['physical_current_identity_independently_verified'] or p['daily_underlying_sample_coverage_verified'] or p['mean_field_depth_is_mean_instantaneous_depth']:
        raise ValueError('No identity/coverage/temporal-operator promotion')


def no_network(*args,**kwargs):raise RuntimeError('Retained-byte audit forbids every provider request')


def build(root=ROOT):
    urllib.request.urlopen=no_network;urllib.request.build_opener=no_network
    op=json.loads((root/OP).read_bytes())
    for f,h in op['input_sha256'].items():
        if hashlib.sha256((root/f).read_bytes()).hexdigest()!=h:raise ValueError('Pinned retained-source input changed:'+f)
    journal=json.loads((root/DATA/'journal.json').read_bytes())
    original=json.loads((root/DATA/'profiles.json').read_bytes())
    plan=json.loads((root/DATA/'field-plan.json').read_bytes())
    before,metadata=source.imported(root)
    if plan!=source.plan() or journal['requests'][:2]!=before['requests'] or len(journal['requests'])!=18:
        raise ValueError('Exact predeclared scope and complete aggregate custody required')
    rebuilt=[];decoded=0;raw_bytes=0;csv_rows=[];features=[];candidates=[]
    if original['metadata']!=metadata:raise ValueError('Exact retained metadata semantics required')
    for target,receipt in zip(plan,journal['requests'][2:]):
        raw=(root/DATA/receipt['raw_file']).read_bytes()
        if receipt['url']!=target['url'] or receipt['target_id']!=target['target_id'] or receipt['attempts']!=1 or receipt['status']!='received_archived_before_derivation' or receipt['derivation_status']!='parsed_and_diagnosed' or hashlib.sha256(raw).hexdigest()!=receipt['sha256'] or len(raw)!=receipt['bytes_received']:
            raise ValueError('Every exact field-response receipt/hash must reproduce')
        values,numeric=source.diagnose(raw,target);decoded+=numeric;raw_bytes+=len(raw)
        for p in values:
            verify_profile(p)
            pointer='/profiles/'+str(len(rebuilt));rebuilt.append(p)
            primary=p['threshold_contexts'][1] if p['threshold_contexts'] else {}
            station=p['nominal_station'];date=p['time_center_utc'][:10]
            identifier=station['station']+'-'+date
            row={'id':identifier,'station':station['station'],'nominal_longitude_degrees_east':station['longitude'],
                 'nominal_latitude_degrees_north':0,'provider_daily_average_date':date,
                 'time_label_utc':p['time_center_utc'],'component_bearing_degrees_true':90,
                 'primary_threshold_m_s':.1,'sampled_core_depth_m':primary.get('core_depth_m'),
                 'primary_lower_threshold_depth_m':p['primary_lower_isotach_depth_m'],
                 'primary_threshold_layer_span_m':p['primary_threshold_layer_span_m'],
                 'upper_status':primary.get('upper_status'),'lower_status':primary.get('lower_status'),
                 'lower_last_connected_depth_m':primary.get('lower_last_connected_depth_m'),
                 'physical_current_thickness_m':None,'annual_range_m':None,'volume_m3':None,
                 'position_role':'nominal_station_not_actual_deployment_or_current_axis',
                 'daily_underlying_sample_coverage_verified':False,'source_raw_file':DATA+'/'+receipt['raw_file'],
                 'source_raw_sha256':receipt['sha256'],'source_profile_file':DATA+'/profiles.json','source_profile_pointer':pointer}
            csv_rows.append(row)
            lon=station['longitude'];features.append({'type':'Feature','id':identifier,
                'geometry':{'type':'Point','coordinates':[lon if lon<=180 else lon-360,0]},'properties':row})
            if p['primary_lower_isotach_depth_m'] is not None:
                candidates.append({'id':'tao-euc-'+identifier+'-daily-u0p1-lower','entity_id':'current:pacific-equatorial-undercurrent',
                    'metric':'derived_observed_daily_mean_component_lower_isotach_depth','unit':'m',
                    'approximate_value_m':p['primary_lower_isotach_depth_m'],
                    'source_upper_threshold_depth_m':primary.get('upper_depth_m'),
                    'source_threshold_layer_span_m':p['primary_threshold_layer_span_m'],
                    'source_lower_interpolation_bracket_m':primary.get('lower_bracket_m'),
                    'source_station':station,'source_daily_average_date':date,'component_bearing_degrees_true':90,
                    'threshold_m_s':.1,'source_raw_file':row['source_raw_file'],'source_raw_sha256':receipt['sha256'],
                    'source_profile_file':row['source_profile_file'],'source_profile_pointer':pointer,
                    'vertical_datum':'provider_depth_m_below_sea_surface_positive_down',
                    'interpolation_assumption':'piecewise_linear_between_retained_rows_no_unobserved_reversals',
                    'source_sampling':'original_rows_near10m_not_full_original5m_structure',
                    'thickness_m':None,'uncertainty_m':None,'annual_range_m':None,'volume_m3':None,
                    'physical_current_bottom_established':False,'independent_observation_count_claimed':False,
                    'reference_route_projection_eligible':False,'volume_eligible':False,'seasonal_playback_eligible':False,
                    'reference_inventory_admission_performed':False})
    if rebuilt!=original['profiles'] or decoded!=journal['field_scalars_decoded'] or before['total_body_bytes']+raw_bytes!=journal['total_body_bytes']:
        raise ValueError('All profiles, decoded cells and aggregate byte custody must match exactly')
    if len(rebuilt)!=48 or len(candidates)!=18 or sum(p['primary_threshold_layer_span_m'] is not None for p in rebuilt)!=15:
        raise ValueError('Exact source scientific outcomes changed')
    audit={'schema':'osw.tao-pacific-euc-retained-depth-audit.v1','status':'PASS_EXACT_RECONSTRUCTION_AND_INDEPENDENT_BOUNDARY_CHECKS',
           'source_run':41974968456,'source_profile_count':48,'source_field_responses_verified':16,
           'finite_primary_lower_threshold_depths':18,'finite_primary_threshold_layer_spans':15,
           'independent_threshold_contexts_verified':144,'aggregate_request_attempts_preserved':18,
           'field_scalars_decoded':decoded,'provider_requests':0,'input_sha256':op['input_sha256'],
           'new_reference_candidates':18,'reference_inventory_admission_performed':False,
           'physical_current_thickness_or_volume_established':False,'runtime_changed':False,'full_goal_complete':False,
           'interpretation':['Derived contours of provider daily means, not mean instantaneous depths or seasonal means.',
                             'No missing/QC rejection/depth gap is treated as zero, seabed or absence of the named current.',
                             'Nominal points and interpolated retained-sample thresholds do not prove actual axes, unsampled5m structure, current membership or physical thickness.',
                             'Interpolation brackets describe sampling resolution, not uncertainty. No pooling into annual ranges or volume.']}
    buffer=io.StringIO();writer=csv.DictWriter(buffer,fieldnames=list(csv_rows[0]),lineterminator='\n');writer.writeheader()
    for row in csv_rows:writer.writerow({k:('' if v is None else json.dumps(v) if isinstance(v,(dict,list,bool)) else v) for k,v in row.items()})
    pieces={'audit.json':source.frozen.encoded(audit),'profiles.csv':buffer.getvalue().encode(),
            'depth-points.geojson':source.frozen.encoded({'type':'FeatureCollection','features':features}),
            'reference-candidates.json':source.frozen.encoded({'schema':'osw.tao-euc-lower-threshold-reference-candidates.v1','records':candidates,'physical_thickness_or_volume_promoted':False,'reference_inventory_admission_performed':False})}
    if sum(map(len,pieces.values()))>=2400000:raise ValueError('Unchanged scientific output cap exceeded')
    return pieces


if __name__=='__main__':
    out=ROOT/'tao-pacific-euc-retained-depth-audit-v1';out.mkdir(exist_ok=True);pieces=build()
    for name,raw in pieces.items():(out/name).write_bytes(raw)
    print(json.dumps(json.loads(pieces['audit.json'])|{'input_sha256':'verified_pins_omitted_from_log'}),flush=True)
