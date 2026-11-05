"""Retain frozen observed cores; refine their support on both native source axes."""
import copy,json,zipfile
from pathlib import Path
from collections import Counter
import derive_redsox_observed_depth_sections_v1 as original
import redsox_native_union_depth_v2 as fine

ROOT=original.ROOT
OPERATOR='research/redsox-observed-depth-sections-operator-v2.json'
PREVIOUS='research/redsox-observed-depth-sections-v1.json'
SECTIONS=original.SECTIONS


def refine_case(case,rows,header,sequence,crows):
    result=copy.deepcopy(case);before=copy.deepcopy(case['joint_diagnosis'])
    reproduced=original.profile_depth(rows,header,sequence,crows,case['section_bearing_degrees_true'])
    if any(case[k]!=v for k,v in reproduced.items()):raise ValueError('Every frozen core, selection, axis, remapping and coarse diagnosis must reproduce')
    hz,hs,method=original.hydro_depths(header,sequence,crows)
    grid=fine.union_grid(case['native_velocity_depth_m'],case['native_component_m_s'],hz,hs,case['core_index']);seed=grid['seed_union_index']
    if grid['depth_m'][seed]!=case['core_depth_m'] or grid['component_m_s'][seed]!=case['core_component_m_s'] or grid['salinity_psu'][seed]!=case['core_remapped_salinity_psu']:raise ValueError('Exact frozen native velocity core and same-core hydrographic screen required')
    result.update(previous_velocity_grid_joint_diagnosis=before,joint_diagnosis=fine.diagnose(grid),fine_source_union_grid=grid,native_hydrographic_depth_m=hz,native_hydrographic_salinity_psu=hs,depth_grid_kind='union_of_original_velocity_and_hydrographic_depth_knots',frozen_velocity_core_and_point_salinity_reproduced_exactly=True,hydrographic_depth_operator=method)
    return result


def build(root=ROOT,section=None):
    if section not in SECTIONS:raise ValueError('Explicit original section batch required')
    read=lambda p:json.loads((root/p).read_bytes());op=read(OPERATOR)
    if op['sections']!=SECTIONS or op['previous_observed_report']!=PREVIOUS or op['maximum_union_nodes_per_case']!=6000 or op['maximum_native_scalar_values']!=250000 or op['maximum_decoded_bytes']!=7000000 or any(op['eligibility'].values()):raise ValueError('Exact original scope, unchanged caps and non-promotion required')
    for file,pin in op['input_sha256'].items():
        if original.digest((root/file).read_bytes())!=pin:raise ValueError('Pinned source, method or frozen core changed: '+file)
    prior=read(PREVIOUS);expected=[(name,station) for name,stations in SECTIONS.items() for station in stations]
    if [(c['section_id'],c['station']) for c in prior['cases']]!=expected or len(expected)!=17:raise ValueError('All original seventeen cases exactly once required')
    old={c['station']:c for c in prior['cases']};lv=read('research/redsox-ladcp-source-inventory.json');cv=read('research/redsox-ctd-companion-inventory.json');lb={p['station']:p for p in lv['profiles'] if p['campaign']=='RSX1'};cb={p['filename_station']:p for p in cv['profiles'] if p['campaign']=='RSX1'}
    planned=prior['counts']['planned_native_scalar_values']
    if planned!=sum(lb[s]['samples']*4+(cb[s]['samples']*len(cb[s]['sequence']) if s in cb else 0) for name,s in expected) or planned>250000 or 8*(planned+2*6000*17)>7000000:raise ValueError('All-source and maximum derived-grid reservation before decode required')
    result=[];actual=0
    with zipfile.ZipFile(root/original.LZIP) as vz,zipfile.ZipFile(root/original.CZIP) as hz:
        for station in SECTIONS[section]:
            case=old[station];p=copy.deepcopy(case);p['previous_velocity_grid_joint_diagnosis']=copy.deepcopy(p['joint_diagnosis']);p['fine_source_union_grid']=None
            if 'native_velocity_depth_m' in case:
                l=lb[station];c=cb[station];a=vz.read(l['source_file']);b=hz.read(c['source_file'])
                if original.digest(a)!=l['source_sha256'] or original.digest(b)!=c['source_sha256'] or l['source_sha256']!=case['source_velocity_member_sha256'] or c['source_sha256']!=case['source_hydrography_member_sha256']:raise ValueError('Exact original archive member hashes required')
                h,rows,issues=original.parse_gpl(a);ch,sequence,crows=original.parse_ctd(b)
                if len(rows)!=l['samples'] or len(crows)!=c['samples'] or sequence!=c['sequence']:raise ValueError('Exact source shapes required')
                actual+=4*len(rows)+len(sequence)*len(crows)
                if actual>planned:raise ValueError('Joint native decode reservation exceeded')
                p=refine_case(case,rows,ch,sequence,crows)
            result.append(p)
    report={'schema':'osw.redsox-observed-depth-sections.v2','operator_file':OPERATOR,'operator_sha256':original.digest((root/OPERATOR).read_bytes()),'input_sha256':op['input_sha256'],'section_id':section,'source_plan_case_count':17,'batch_case_count':len(result),'cases':result,'counts':{'profile_cases':len(result),'status_counts':dict(Counter(c['status'] for c in result)),'joint_status_counts':dict(Counter(c['joint_diagnosis']['status'] if c['joint_diagnosis'] else 'not_diagnosed' for c in result)),'fine_upper_boundary_status_counts':dict(Counter(c['joint_diagnosis']['upper']['status'] for c in result if c['joint_diagnosis'] and c['joint_diagnosis']['status']=='conditional_saline_component_core_supported')),'fine_lower_boundary_status_counts':dict(Counter(c['joint_diagnosis']['lower']['status'] for c in result if c['joint_diagnosis'] and c['joint_diagnosis']['status']=='conditional_saline_component_core_supported')),'whole_cohort_native_scalar_reservation':planned,'decoded_native_scalar_values_in_batch':actual,'maximum_conservative_input_and_derived_grid_bytes':8*(planned+2*6000*17),'union_grid_cases':sum(c['fine_source_union_grid'] is not None for c in result),'union_nodes':sum(c['fine_source_union_grid']['union_node_count'] for c in result if c['fine_source_union_grid'])},'interpretation':op['interpretation'],'new_ocean_field_requests':0,'new_reference_inventory_rows':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0,'runtime_changed':False,'full_goal_complete':False}
    raw=original.encode(report)
    if len(raw)>=2400000:raise ValueError('Fixed per-section2.4MB output cap exceeded')
    return report,raw


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--section',required=True,choices=list(SECTIONS));args=parser.parse_args();report,raw=build(section=args.section);out=Path('redsox-observed-depth-sections-v2')/args.section;out.mkdir(parents=True,exist_ok=True);(out/'depths.json').write_bytes(raw);print(json.dumps({'section':args.section,'bytes':len(raw),'counts':report['counts']}),flush=True)
