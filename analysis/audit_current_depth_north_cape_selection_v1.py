"""Explain the frozen North Cape diagnostic; do not select alternative profiles."""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
from mixed_interval_section_geometry_v1 import validate_retained

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-north-cape-selection-audit-operator-v1.json'


def support(z,column,window):
    indices=[i for i,depth in enumerate(z) if window[0]<=depth<=window[1]]
    if len(indices)<2 or z[indices[0]]!=window[0] or z[indices[-1]]!=window[1]:raise ValueError('Audit windows require native endpoints')
    return all(column[i] is not None and math.isfinite(column[i]) for i in indices)


def classify(z,column,score,config,windows):
    complete=support(z,column,config['selection_depth_interval_m'])
    if complete!=score['complete_selection_interval_support']:raise ValueError('Source interval support differs from audit')
    if not complete:peak=None;category='incomplete_original_selection_interval'
    else:
        peak=max(v for depth,v in zip(z,column) if config['selection_depth_interval_m'][0]<=depth<=config['selection_depth_interval_m'][1])
        core=peak>config['primary_threshold_m_s'];positive=score['signed_selection_interval_integral_m2_s']>0
        if core and positive:category='eligible_original_diagnostic'
        elif core:category='qualifying_core_but_nonpositive_integral'
        elif positive:category='positive_integral_but_subthreshold_core'
        else:category='subthreshold_core_and_nonpositive_integral'
    if (category=='eligible_original_diagnostic')!=score['eligible']:raise ValueError('Original eligibility differs from audit category')
    return {'category':category,'original_core_peak_component_m_s':peak,
        'original_signed_selection_interval_integral_m2_s':score['signed_selection_interval_integral_m2_s'],
        'native_support_by_window':{str(a)+'_'+str(b):support(z,column,[a,b]) for a,b in windows}}


def build(reader=None):
    read=reader or (lambda f:(ROOT/f).read_bytes());op=json.loads(read(OPERATOR))
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256(read(f)).hexdigest()!=pin:raise ValueError('Pinned audit input changed: '+f)
    source_op=json.loads(read(op['source_operator_file']));facts=json.loads(read(op['source_facts_file']))
    entity='current:north-cape';config={**source_op,**source_op['currents'][entity]}
    addendum=json.loads(read(op['projection_addendum_file']));cases=addendum['projections']+addendum['unresolved_reference_cases']
    anchors={(c['entity_id'],c['snapshot_time_utc'],a['source_section_id']):(c,a) for c in cases for a in c['anchors']}
    expected={(stamp,s['id']) for stamp in source_op['snapshot_times_utc'] for s in source_op['sections'] if s['entity_id']==entity}
    rows=[(i,r) for i,r in enumerate(facts['descriptors']) if r['entity_id']==entity]
    if len(rows)!=len(expected) or {(r['snapshot_time_utc'],r['section_id']) for i,r in rows}!=expected:raise ValueError('Every original North Cape case required')
    categories=Counter();support_counts=Counter();sections=[];profiles=[]
    for index,row in rows:
        packet=json.loads(read(row['source_file']));validate_retained(packet,config)
        diagnosis=packet['diagnosis'];z=packet['depth_levels_m'];scores=diagnosis['candidate_scores']
        if packet['operator_file']!=op['source_operator_file'] or packet['operator_sha256']!=op['input_sha256'][op['source_operator_file']] or diagnosis['selected_column_index']!=row['selected_column_index']:raise ValueError('Original source identity/selection changed')
        local=Counter();local_support=Counter()
        for j,(column,score) in enumerate(zip(packet['columns'],scores)):
            result=classify(z,column['signed_reference_component_m_s'],score,config,op['support_windows_m'])
            categories[result['category']]+=1;local[result['category']]+=1
            for key,value in result['native_support_by_window'].items():support_counts[key]+=int(value);local_support[key]+=int(value)
            profiles.append({'source_file':row['source_file'],'source_profile_pointer':'/columns/'+str(j),
                'source_score_pointer':'/diagnosis/candidate_scores/'+str(j),'snapshot_time_utc':row['snapshot_time_utc'],'section_id':row['section_id'],**result})
        case,anchor=anchors[entity,row['snapshot_time_utc'],row['section_id']]
        if anchor['source_profile_refs']!=[op['source_facts_file']+'#/descriptors/'+str(index)] or anchor['source_horizontal_selection_status']!=diagnosis['horizontal_selection_status'] or anchor['model_lower_depth_m']!=row['primary_lower_depth_m']:raise ValueError('Published reference source pointer/value differs')
        sections.append({'source_file':row['source_file'],'source_sha256':row['source_sha256'],'source_descriptor_index':index,
            'snapshot_time_utc':row['snapshot_time_utc'],'section_id':row['section_id'],'original_horizontal_selection_status':diagnosis['horizontal_selection_status'],
            'original_selected_column_index':row['selected_column_index'],'original_primary_lower_status':row['primary_lower_status'],
            'original_projection_block_reasons':anchor['projection_block_reasons'],'original_lower_projection_eligible':anchor['lower_projection_eligible'],
            'published_case_id':case['id'],'published_case_status':case['status'],'column_category_counts':dict(local),'native_support_counts_by_window':dict(local_support)})
    return {'schema':'osw.current-depth-selection-coverage-audit.v1','status':'FROZEN_DIAGNOSTIC_COVERAGE_AUDIT_NOT_ALTERNATIVE_SELECTION',
        'entity_id':entity,'operator_file':OPERATOR,'operator_sha256':hashlib.sha256(read(OPERATOR)).hexdigest(),'input_sha256':op['input_sha256'],
        'counts':{'section_date_cases':len(sections),'native_velocity_profiles':len(profiles),'category_counts':dict(categories),'native_support_counts_by_window':dict(support_counts),
            'original_selected_profiles':sum(s['original_selected_column_index'] is not None for s in sections),
            'original_lower_projectable_nodes':sum(s['original_lower_projection_eligible'] for s in sections)},
        'sections':sections,'profile_classifications':profiles,
        'interpretation':'Counts explain the frozen50-350m/10cm/s eastward diagnostic. Support-window counts describe native data completeness only;they do not select alternate candidates,derive other contours,establish current absence or identify bathymetric causes of missing values.',
        'alternative_selection_evaluated':False,'new_projected_depths':0,'new_field_retrieval_performed':False,'seabed_inferred_from_missing_support':False,
        'current_absence_established':False,'physical_or_annual_promotion_performed':False,'runtime_changed':False,'full_goal_complete':False}


if __name__=='__main__':
    output=Path('north-cape-selection-audit-v1');output.mkdir(exist_ok=True)
    report=build();(output/'audit.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print(json.dumps(report['counts']))
