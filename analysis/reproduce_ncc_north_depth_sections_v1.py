"""Reproduce retained joint native fields without reopening ocean datasets."""
import copy,hashlib,json,math
from collections import Counter
import numpy as np
import acquire_ncc_north_joint_sections_v1 as source
import coastal_fresh_depth_curtains_v1 as spatial
from sample_eac_hycom_route_depth_v1 import along_velocity,clean,canonical_hash,GEOD
from sample_atlantic_current_depth_v1 import wrapped_longitude

DIRECTORY='research/source-data/ncc-north-joint-sections-v1/'
OPERATOR='research/ncc-north-joint-sections-operator-v1.json'
REPORT=DIRECTORY+'source-report.json'


def read_bundle(reader):
    raw=reader(OPERATOR);op=json.loads(raw);source.validate_operator(op)
    for file,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(file)).hexdigest()!=pin:raise ValueError('Frozen native source input changed: '+file)
    report=json.loads(reader(REPORT));ledger_raw=reader(DIRECTORY+'transport-ledger.json');ledger=json.loads(ledger_raw)
    if report['operator_file']!=OPERATOR or report['operator_sha256']!=hashlib.sha256(raw).hexdigest() or report['input_sha256']!=op['input_sha256'] or report['transport_ledger_sha256']!=hashlib.sha256(ledger_raw).hexdigest():raise ValueError('Exact original operator/report/ledger links required')
    sections={};pieces={}
    for piece in report['profiles']:
        name=piece['file']
        if '/' in name or '\\' in name:raise ValueError('Direct native source filename required')
        file=DIRECTORY+name;data=reader(file)
        if file in sections or hashlib.sha256(data).hexdigest()!=piece['sha256'] or len(data)!=piece['bytes']:raise ValueError('Unique exact native section bytes required')
        sections[file]=json.loads(data);pieces[file]={**piece,'file':file}
    return {'operator':op,'report':report,'ledger':ledger,'sections':sections,'pieces':pieces}


def reproduce(bundle):
    op=bundle['operator'];source.validate_operator(op);report=bundle['report'];ledger=bundle['ledger'];source_rows=report['records']
    expected=[(stamp,definition) for stamp in source.STAMPS for definition in source.SECTIONS]
    if report['schema']!='osw.ncc-north-joint-source-report.v1' or report['status']!='ALL8JOINT_NATIVE_SECTIONS_RETRIEVED' or report['all_targets_preflighted_before_fields'] is not True or len(source_rows)!=8 or len(report['profiles'])!=8 or len(bundle['sections'])!=8 or any(report[k] for k in ['new_reference_inventory_rows_admitted','physical_current_bottom_established','runtime_changed','full_goal_complete']):raise ValueError('Complete original source cohort and non-promotion required')
    cases=[];requests=[];planned=0;time_indices={};reference_z=None
    finite=lambda x:type(x) in (int,float) and math.isfinite(x)
    for index,((stamp,definition),record) in enumerate(zip(expected,source_rows)):
        file=DIRECTORY+stamp[:10]+'-'+definition['id']+'.json';s=bundle['sections'][file];piece=bundle['pieces'][file];columns=s['columns'];salt=s['practical_salinity_columns'];z=s['depth_levels_m'];n=len(columns);iy=s['native_latitude_index'];x0,x1=s['native_longitude_indices_inclusive'];it=s['source_time_index']
        if s['schema']!='osw.ncc-north-joint-native-section.v1' or s['entity_id']!=source.OWNER or s['operator_file']!=OPERATOR or s['operator_sha256']!=report['operator_sha256'] or s['section_definition']!=definition or s['snapshot_time_utc']!=stamp or s['source_returned_timestamp_utc']!=stamp or record['section_id']!=definition['id'] or record['snapshot_time_utc']!=stamp or record['profile']!=report['profiles'][index] or record['profile']['file']!=file.rsplit('/',1)[-1]:raise ValueError('Exact declared section/date/owner/source links required')
        if s['velocity_dataset']!=source.UV or s['salinity_dataset']!=source.TS or s['native_coordinates_exactly_paired'] is not True or any(s[k] for k in ['core_reselected_after_salinity','physical_current_bottom_established','annual_extrema_established','full_goal_complete','wire_hash_claimed']) or s['physical_thickness_m'] is not None or s['volume_m3'] is not None:raise ValueError('Original paired native provenance and limits required')
        if len(z)!=40 or z[0]!=0 or z[-1]!=5000 or 100 not in z or not all(finite(v) for v in z) or any(b<=a for a,b in zip(z,z[1:])) or (reference_z is not None and z!=reference_z):raise ValueError('Same original increasing40native depths required')
        reference_z=z
        if not 3<=n<=150 or n*40>20000 or len(salt)!=n or any(len(c)!=40 or any(v is not None and (not finite(v) or not 0<=v<=50) for v in c) for c in salt):raise ValueError('Complete bounded native salinity columns required')
        if any(type(v)!=int or v<0 for v in [iy,x0,x1,it]) or x1-x0+1!=n or (stamp in time_indices and it!=time_indices[stamp]):raise ValueError('Exact nonnegative native indices and per-date time correspondence required')
        time_indices[stamp]=it
        lat=s['native_latitude_degrees_north'];distance=GEOD.inv(0,definition['latitude_degrees_north'],0,lat)[2]/1000
        if not finite(lat) or distance!=s['nearest_latitude_distance_km'] or distance>5:raise ValueError('Original native latitude and tolerance required')
        west,east=definition['longitude_gate_degrees_east'];previous_lon=None
        for j,c in enumerate(columns):
            lon=c['native_source_longitude_degrees_east']
            if c['global_longitude_index']!=x0+j or c['global_latitude_index']!=iy or c['native_source_latitude_degrees_north']!=lat or not finite(lon) or not west<=lon<=east or (previous_lon is not None and lon<=previous_lon) or c['sampled_lon_lat']!=[wrapped_longitude(lon),lat]:raise ValueError('Every original ordered native column coordinate required')
            previous_lon=lon
            for name in ['eastward_velocity_m_s','northward_velocity_m_s','signed_reference_component_m_s']:
                if len(c[name])!=40 or any(v is not None and (not finite(v) or abs(v)>10) for v in c[name]):raise ValueError('Finite/missing original native component profiles required')
            u=np.asarray([np.nan if v is None else v for v in c['eastward_velocity_m_s']]);v=np.asarray([np.nan if v is None else v for v in c['northward_velocity_m_s']]);component=along_velocity(u,v,0);component=np.where(np.isfinite(u)&np.isfinite(v),component,np.nan)
            if clean(component)!=c['signed_reference_component_m_s']:raise ValueError('Signed native component must reproduce from both source components')
        if canonical_hash(columns)!=s['decoded_columns_sha256'] or canonical_hash(salt)!=s['decoded_salinity_sha256']:raise ValueError('Canonical native arrays must match source hashes')
        metadata=s['source_metadata']
        if metadata['velocity_global'].get('field_type')!='instantaneous' or metadata['salinity_global'].get('field_type')!='instantaneous' or any(metadata['variables'][name].get('units')!=unit or metadata['variables'][name].get('standard_name')!=standard for name,(unit,standard) in source.FIELDS.items()):raise ValueError('Original instantaneous component/salinity metadata required')
        diagnosis=source.diagnose(z,[c['signed_reference_component_m_s'] for c in columns],op)
        if diagnosis!=s['diagnosis'] or record['horizontal_selection_status']!=diagnosis['horizontal_selection_status']:raise ValueError('Original complete interval velocity selection must reproduce unchanged')
        classification=source.classify(z,columns,salt,diagnosis)
        if classification!=s['fresh_component_classification'] or classification!=record['fresh_component_classification']:raise ValueError('Original conditional fresh boundaries must reproduce exactly')
        selected=diagnosis['selected_column_index'];audit={'schema':'osw.ncc-north-retained-section-reproduction-case.v1','source_section_file':file,'source_section_sha256':piece['sha256'],'entity_id':source.OWNER,'snapshot_time_utc':stamp,'section_id':definition['id'],'branch_scope':op['branch_scope'],'sampled_lon_lat':copy.deepcopy(columns[selected]['sampled_lon_lat']) if selected is not None else None,'selected_column_index':selected,'horizontal_selection_status':diagnosis['horizontal_selection_status']}
        cases.append({'original':audit,'classification':classification,'profile':s,'profile_piece':piece,'source_index':index})
        planned+=40*n
        requests.extend((name,it,iy,x0,x1,40*n) for name in source.FIELDS)
    if len(set(time_indices.values()))!=4 or ledger!=report['transport'] or ledger['schema']!='osw.ncc-joint-three-field-read-ledger.v1':raise ValueError('All four distinct snapshots and exact original ledger required')
    actual=[];extra=0;requested=0;returned=0;pending=None;attempt=0
    for r in ledger['requests']:
        key=(r['variable'],r['time_index'],r['latitude_index'],*r['longitude_indices_inclusive'],r['requested_scalar_values'])
        if pending is None:
            if len(actual)>=len(requests) or key!=requests[len(actual)] or r['attempt']!=1:raise ValueError('All-and-only ordered original first reads required')
            pending=key;attempt=1
        else:
            attempt+=1
            if key!=pending or r['attempt']!=attempt or attempt>3:raise ValueError('Only identical bounded retries required')
            extra+=key[-1]
        if r['depth_indices_inclusive']!=[0,39]:raise ValueError('Full original40levels required')
        requested+=key[-1]
        if r['status']=='success':
            if not 0<r['decoded_array_bytes']<=8*key[-1]:raise ValueError('Conservative source decoded bound required')
            actual.append(key);returned+=key[-1];pending=None
        elif r['status']!='provider_io_failure' or attempt==3:raise ValueError('Only literal provider IO retry followed by success required')
    if pending is not None or actual!=requests or ledger['planned_velocity_cell_pairs']!=planned or ledger['planned_salinity_scalars']!=planned or ledger['planned_first_attempt_scalar_values']!=3*planned or ledger['additional_retry_scalar_values_reserved']!=extra or ledger['joint_reserved_native_cell_units']!=2*planned+extra or ledger['conservative_joint_decoded_bytes']!=24*planned+8*extra or ledger['actual_requested_scalar_values']!=requested or ledger['successful_returned_scalar_values']!=returned or returned!=3*planned or ledger['maximum_joint_native_cell_units']!=250000 or ledger['maximum_decoded_bytes']!=7000000 or ledger['maximum_attempts_per_target']!=3 or ledger['wire_hash_claimed'] is not False or 2*planned+extra>250000 or 24*planned+8*extra>7000000:raise ValueError('Exact complete shared reservation/return arithmetic and frozen caps required')
    if report['counts']!={'new_sections':8,'native_velocity_profiles':planned//40,'classification_status_counts':dict(Counter(c['classification']['status'] for c in cases))}:raise ValueError('All original outcome counts required')
    return cases


def curtains(cases,bundle):return [spatial.curtain(c,bundle) for c in cases]
