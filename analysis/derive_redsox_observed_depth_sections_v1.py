"""Dated REDSOX depth contexts from existing original archives; no retrieval."""
import hashlib,json,math,zipfile
from collections import Counter
from pathlib import Path
import gsw
import numpy as np
from build_redsox_ladcp_source_inventory import parse_gpl
from build_redsox_ctd_companion_inventory import parse_ctd
from build_redsox_lower_nc_section import velocity_layer,interpolate_complete
from build_redsox_section3_spans import geometry as section_geometry,component,STATIONS
from redsox_saline_component_depth_v1 import diagnose

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/redsox-observed-depth-sections-operator-v1.json'
LZIP='research/source-data/ncei-redsox-2001/ladcp-ascii-originals.zip'
CZIP='research/source-data/ncei-redsox-2001/ctd-ascii-originals.zip'
SECTIONS={'lower-northern-channel':[7,8,9,10,11],'winter-section3':STATIONS}


def digest(raw):return hashlib.sha256(raw).hexdigest()
def encode(v):return (json.dumps(v,separators=(',',':'),allow_nan=False)+'\n').encode()


def hydro_depths(header,sequence,rows):
    if header.get('_p_data_units')!='dbar' or header.get('_S_data_units')!='psu':raise ValueError('Original pressure dbar and practical salinity units required')
    if 'z' in sequence and header.get('_z_data_units',header.get('_z_dat_units'))!='m':raise ValueError('Explicit source depth metres or documented unit-key typo required')
    if not 2<=len(rows)<=2000 or len(sequence) not in [6,7,8]:raise ValueError('Bounded original hydrography required')
    if 'z' in sequence:
        z=[r[sequence.index('z')] for r in rows];method='source_explicit_depth_m_with_previously_documented_header_typo'
    else:
        p=[r[sequence.index('p')] for r in rows]
        if any(v is None or not math.isfinite(v) or v<0 for v in p):raise ValueError('Complete native pressure axis required')
        z=(-gsw.z_from_p(np.asarray(p),float(header['lat']))).tolist();method='minus_gsw.z_from_p_dbar_source_latitude_default_zero_dynamic_height_and_surface_geopotential'
    if any(v is None or not math.isfinite(v) or v<0 for v in z) or any(b<=a for a,b in zip(z,z[1:])):raise ValueError('Original increasing hydrographic depth axis required')
    return z,[r[sequence.index('S')] for r in rows],method


def remap_salinity(z,s,targets):
    values=[];receipts=[]
    for target in targets:
        j=int(np.searchsorted(z,target));receipt={'target_velocity_depth_m':target,'hydrographic_indices':None,'status':'outside_observed_hydrographic_support','salinity_psu':None}
        if j<len(z) and z[j]==target:
            value=s[j];receipt.update(hydrographic_indices=[j,j],status='exact_original_hydrographic_sample' if value is not None else 'missing_exact_original_hydrographic_sample',salinity_psu=value)
        elif j==0 or j==len(z):value=None
        else:
            receipt['hydrographic_indices']=[j-1,j];receipt['hydrographic_depth_bracket_m']=[z[j-1],z[j]]
            try:
                value=float(interpolate_complete(z,s,[target],max_gap=5)[0]);receipt.update(status='complete_adjacent_hydrographic_bracket_interpolation',salinity_psu=value)
            except ValueError:
                value=None;receipt['status']='missing_or_over5m_hydrographic_bracket'
        values.append(value);receipts.append(receipt)
    return values,receipts


def profile_depth(rows,header,sequence,crows,bearing):
    # Retain the original 20-200m-above-bed interval even if a weaker interval works.
    mean=velocity_layer(rows,[20,200])
    data=[list(r) for r in rows]
    if not 2<=len(data)<=300 or any(r[0] is None or r[1] is None for r in data):raise ValueError('Complete bounded native height/depth coordinates required')
    if all(a[1]>b[1] for a,b in zip(data,data[1:])):data.reverse()
    if any(b[1]<=a[1] for a,b in zip(data,data[1:])) or any(b[0]>=a[0] for a,b in zip(data,data[1:])):raise ValueError('Monotonic native depth and opposing height axes required')
    q=[None if r[2] is None or r[3] is None else (-r[3] if bearing is None else component(r[2],r[3],bearing)) for r in data]
    meanq=-mean['v_m_s'] if bearing is None else component(mean['u_m_s'],mean['v_m_s'],bearing)
    candidates=[i for i,r in enumerate(data) if 20<=r[0]<=200 and q[i] is not None]
    if not candidates or meanq<=0:return {'status':'original_height_interval_not_positive_or_no_native_core','joint_diagnosis':None,'core_reselected':False}
    core=max(candidates,key=lambda i:q[i]);z=[r[1] for r in data];hz,hs,method=hydro_depths(header,sequence,crows);s,receipt=remap_salinity(hz,hs,z)
    return {'status':'original_velocity_core_retained_for_joint_screen','core_index':core,'core_depth_m':z[core],'core_height_above_bottom_m':data[core][0],'core_component_m_s':q[core],'core_remapped_salinity_psu':s[core],'selection_height_above_bottom_interval_m':[20,200],'selection_interval_mean_component_m_s':meanq,'hydrographic_depth_operator':method,'pressure_equals_depth':False,'source_rows_reversed_for_increasing_depth':data!=rows,'native_velocity_depth_m':z,'native_height_above_bottom_m':[r[0] for r in data],'native_component_m_s':q,'remapped_salinity_psu':s,'salinity_remapping':receipt,'joint_diagnosis':diagnose(z,q,s,core),'core_reselected':False}


def build(root=ROOT):
    read=lambda p:json.loads((root/p).read_bytes());op=read(OPERATOR)
    if op['sections']!=SECTIONS or op['selection_height_above_bottom_interval_m']!=[20,200] or op['primary_velocity_threshold_m_s']!=.2 or op['salinity_inclusive_lower_threshold_psu']!=38 or any(op['eligibility'].values()):raise ValueError('Exact declared sections, rules and no physical promotion required')
    if op['maximum_native_velocity_gap_m']!=20 or op['maximum_hydrographic_bracket_gap_m']!=5 or op['maximum_native_scalar_values']!=250000 or op['maximum_decoded_bytes']!=7000000 or op['excluded_downcast_treatment_stations']!=[10,63]:raise ValueError('Fixed native support, joint reservation and original exclusion rules required')
    for file,pin in op['input_sha256'].items():
        if digest((root/file).read_bytes())!=pin:raise ValueError('Pinned observed source or method changed: '+file)
    ladcp=read('research/redsox-ladcp-source-inventory.json');ctd=read('research/redsox-ctd-companion-inventory.json');support=read('research/redsox-provider-station-support.json');lb={p['station']:p for p in ladcp['profiles'] if p['campaign']=='RSX1'};cb={p['filename_station']:p for p in ctd['profiles'] if p['campaign']=='RSX1'};sb={p['station']:p for p in support['profiles'] if p['campaign']=='RSX1'}
    stations=[s for values in SECTIONS.values() for s in values];planned=sum(lb[s]['samples']*4+(cb[s]['samples']*len(cb[s]['sequence']) if s in cb else 0) for s in stations)
    if len(stations)!=17 or len(set(stations))!=17 or planned>250000 or 8*planned>7000000:raise ValueError('All selected native values jointly fit unchanged caps before archive decode')
    result=[];actual=0
    with zipfile.ZipFile(root/LZIP) as lv,zipfile.ZipFile(root/CZIP) as cv:
        for section,selected in SECTIONS.items():
            bearings=section_geometry([lb[s]['position_lon_lat'] for s in selected])[1] if section=='winter-section3' else [None]*len(selected)
            for station,bearing in zip(selected,bearings):
                l=lb[station];c=cb.get(station);p={'entity_id':'current:red-sea-saline-overflow','section_id':section,'station':station,'campaign':'RSX1','source_velocity_file':LZIP+'#'+l['source_file'],'source_velocity_member_sha256':l['source_sha256'],'source_hydrography_file':CZIP+'#'+c['source_file'] if c else None,'source_hydrography_member_sha256':c['source_sha256'] if c else None,'position_lon_lat':l['position_lon_lat'],'source_velocity_time_utc':l['time_utc'],'source_ctd_start_time_utc':c['start_time_utc'] if c else None,'component_reference':'fixed_southward_minus_v' if bearing is None else 'right_normal_to_original_bent_section','section_bearing_degrees_true':bearing,'provider_station_assessment':sb[station]['assessment'],'physical_cast_identity_independently_verified':False,'sample_level_synchronization_verified':False,'source_processing_exclusions_cleared':False,'tidal_correction_applied':False,'physical_current_bottom_established':False,'physical_layer_thickness_m':None,'volume_m3':None,'annual_extrema_established':False,'joint_diagnosis':None}
                reasons=[]
                if station in [10,63]:reasons.append('unverified_rejected_downcast_treatment')
                if l['source_reference']=='m':reasons.append('uninterpretable_velocity_reference')
                if c is None:reasons.append('missing_hydrographic_companion')
                if sb[station]['assessment']['status']!='consistent_provider_station_records':reasons.append('provider_station_metadata_not_consistent')
                p['exclusion_reasons']=reasons
                if reasons:p['status']='EXCLUDED_OR_UNRESOLVED_SOURCE_SUPPORT';result.append(p);continue
                a=lv.read(l['source_file']);b=cv.read(c['source_file'])
                if digest(a)!=l['source_sha256'] or digest(b)!=c['source_sha256']:raise ValueError('Exact retained archive members required')
                h,rows,issues=parse_gpl(a);ch,sequence,crows=parse_ctd(b)
                if len(rows)!=l['samples'] or len(crows)!=c['samples'] or sequence!=c['sequence']:raise ValueError('Original source shapes must reproduce')
                actual+=len(rows)*4+len(crows)*len(sequence)
                if actual>planned:raise ValueError('Decoded values exceed joint reservation')
                p['source_header_issues_preserved']=issues
                try:p.update(profile_depth(rows,ch,sequence,crows,bearing))
                except ValueError as error:p.update(status='UNRESOLVED_NATIVE_SUPPORT',support_failure=str(error))
                result.append(p)
    report={'schema':'osw.redsox-observed-depth-sections.v1','operator_file':OPERATOR,'operator_sha256':digest((root/OPERATOR).read_bytes()),'input_sha256':op['input_sha256'],'cases':result,'counts':{'selected_profile_cases':len(result),'status_counts':dict(Counter(p['status'] for p in result)),'joint_status_counts':dict(Counter(p['joint_diagnosis']['status'] if p['joint_diagnosis'] else 'not_diagnosed' for p in result)),'planned_native_scalar_values':planned,'decoded_native_scalar_values':actual,'maximum_conservative_decoded_bytes':8*planned},'interpretation':op['interpretation'],'new_ocean_field_requests':0,'new_reference_inventory_rows':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0,'runtime_changed':False,'full_goal_complete':False}
    raw=encode(report)
    if len(raw)>=2400000:raise ValueError('Fixed 2.4MB output cap exceeded')
    return report,raw


if __name__=='__main__':
    report,raw=build();out=Path('redsox-observed-depth-sections-v1');out.mkdir(exist_ok=True);(out/'depths.json').write_bytes(raw);print(json.dumps(report['counts']),flush=True)
