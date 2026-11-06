"""Frozen default-source audit plus strict non-additive Atlantic SECC context inventory."""
import hashlib,json
from collections import Counter
from pathlib import Path
import audit_current_depth_coverage_v1 as frozen

ROOT=frozen.ROOT
OPERATOR='research/current-depth-coverage-audit-operator-v14.json'
OWNER='current:atlantic-south-equatorial-countercurrent'
SOURCE_OPERATOR='research/atlantic-secc-multi-context-depth-sections-operator-v1.json'
CONTEXTS=('shallow','deep')


def validate_context_case(case,source,config,context):
    if context not in CONTEXTS or source['schema']!='osw.multi-context-interval-depth-section.v1' or source['entity_id']!=OWNER or source['source_section_geometry']!='longitude' or source['source_returned_timestamp_utc']!=source['snapshot_time_utc'] or source['default_diagnostic_context_id']!='shallow' or source['vertical_contexts_are_additive'] is not False or source['contexts_are_independent_observations'] is not False:raise ValueError('Exact source context semantics required')
    windows={'shallow':[0,100],'deep':[150,350]};definition=config['diagnostic_contexts'][context];entry=source['context_diagnoses'][context];d=entry['diagnosis']
    if set(source['context_diagnoses'])!=set(CONTEXTS) or source['diagnosis']!=source['context_diagnoses']['shallow']['diagnosis'] or config['entity_id']!=OWNER or config['component_bearing_degrees_true']!=90 or config['surface_component_gate_m_s'] is not None or config['temperature_gate'] is not None or config['default_diagnostic_context_id']!='shallow':raise ValueError('Original owner/frame/default/null gates required')
    for value in [definition,entry]:
        if value['selection_depth_interval_m']!=windows[context] or value['core_search_depth_interval_m']!=windows[context] or value['primary_threshold_m_s']!=.1:raise ValueError('Original context window and primary required')
    primary=d['selected_column_threshold_layers'][config['thresholds_m_s'].index(.1)] if d['selected_column_index'] is not None else None
    expected={'entity_id':OWNER,'section_id':source['section_definition']['id'],'snapshot_time_utc':source['snapshot_time_utc'],'source_operator':SOURCE_OPERATOR,'source_geometry':'longitude','component_bearing_degrees_true':90,'diagnostic_context_id':context,'source_default_diagnostic_context_id':'shallow','selection_depth_interval_m':windows[context],'core_search_depth_interval_m':windows[context],'original_horizontal_selection_status':d['horizontal_selection_status'],'original_selected_column_index':d['selected_column_index'],'original_primary_layer':primary,'velocity_threshold_m_s':.1,'vertical_contexts_are_additive':False,'contexts_are_independent_observations':False,'source_arrays_changed':False,'diagnostic_view_changes_source_bytes':False,'source_context_diagnosis_sha256':frozen.sha(frozen.encode(d))}
    if any(case[k]!=v for k,v in expected.items()):raise ValueError('Context case must match its OWN original diagnosis exactly')
    resolved=d['horizontal_selection_status']==frozen.INTERIOR
    if case['status']!=(frozen.RESOLVED if resolved else 'ORIGINAL_AXIS_UNRESOLVED_NO_CURTAIN') or (not resolved and case['columns']):raise ValueError('Original context outcome cannot be replaced')
    for key in ['core_reselected','physical_current_bottom_established','named_current_axis_independently_validated','annual_extrema_established','water_mass_classification_performed']:
        if case[key] is not False:raise ValueError('No reselection or physical/annual promotion')
    for key in ['physical_thickness_m','width_m','cross_section_area_m2','volume_m3']:
        if case[key] is not None:raise ValueError('Context diagnostic is not physical geometry or volume')
    return {'entity_id':OWNER,'source_file':case['source_file'],'source_sha256':case['source_sha256'],'section_id':case['section_id'],'snapshot_time_utc':case['snapshot_time_utc'],'diagnostic_context_id':context,'original_selected_column_index':case['original_selected_column_index'],'original_horizontal_selection_status':case['original_horizontal_selection_status'],'status':case['status'],'selection_depth_interval_m':windows[context],'primary_threshold_m_s':.1,'source_context_diagnosis_sha256':case['source_context_diagnosis_sha256']}


def context_inventory(root,op):
    read=lambda p:json.loads((root/p).read_bytes())
    if op['context_source_operator']!=SOURCE_OPERATOR:raise ValueError('Exact original context source operator required')
    original=read(SOURCE_OPERATOR);config={**original,**original['currents'][OWNER]};files=op['context_source_files'];specs=op['non_additive_context_datasets']
    if len(files)!=16 or len(set(files))!=16 or len(specs)!=2 or {s['context'] for s in specs}!=set(CONTEXTS):raise ValueError('Both contexts on exactly sixteen shared cases required')
    if set(original['currents'])!={OWNER} or any(original['eligibility'].values()):raise ValueError('One original owner and no physical promotion required')
    shallow=next(s for s in specs if s['context']=='shallow');deep=next(s for s in specs if s['context']=='deep');main={s['data'] for s in op['curtain_datasets']}
    if shallow['data'] not in main or deep['data'] in main:raise ValueError('Only declared shallow default enters frozen source-case join')
    definitions={s['id']:s for s in original['sections']};source={}
    for file in files:
        raw=(root/file).read_bytes();value=json.loads(raw)
        if frozen.sha(raw)!=op['input_sha256'][file] or value['operator_file']!=SOURCE_OPERATOR or value['operator_sha256']!=frozen.sha((root/SOURCE_OPERATOR).read_bytes()) or value['section_definition']!=definitions[value['section_definition']['id']]:raise ValueError('Exact source hash/operator/definition required')
        source[file]=(value,frozen.sha(raw))
    expected={(s['entity_id'],s['id'],t) for s in original['sections'] for t in original['snapshot_times_utc']}
    if {(v['entity_id'],v['section_definition']['id'],v['snapshot_time_utc']) for v,h in source.values()}!=expected:raise ValueError('Complete original sixteen-case matrix required')
    rows=[];summary={};sets=[]
    for spec in specs:
        context=spec['context'];raw=(root/spec['data']).read_bytes();report=json.loads(raw);review=read(spec['review']);pins=review['input_sha256']
        if pins.get(spec['data'])!=frozen.sha(raw) or report['diagnostic_context_id']!=context or review['diagnostic_context_id']!=context or report['entity_id']!=OWNER or report['source_plan_case_count']!=16 or report['source_context_case_count']!=16 or report['counts']['cases']!=16 or len(report['cases'])!=16 or report['vertical_contexts_are_additive'] is not False or report['contexts_are_independent_observations'] is not False:raise ValueError('Pinned context report/count/semantics required')
        entries=[];seen=set()
        for case in report['cases']:
            file=case['source_file']
            if file not in source or file in seen or case['source_sha256']!=source[file][1] or pins.get(file)!=source[file][1]:raise ValueError('Exactly one pinned source occurrence per context required')
            seen.add(file);entries.append(validate_context_case(case,source[file][0],config,context))
        if seen!=set(files) or dict(Counter(c['status'] for c in entries))!=report['counts']['status_counts']:raise ValueError('Complete context matrix/outcome counts required')
        sets.append(seen);rows.extend(entries);summary[context]={'diagnostic_cases':16,'status_counts':dict(Counter(c['status'] for c in entries)),'data_file':spec['data'],'review_file':spec['review']}
    if sets[0]!=sets[1] or len({(r['source_file'],r['source_sha256'],r['diagnostic_context_id']) for r in rows})!=32:raise ValueError('Same sixteen source cases, thirty-two unique context diagnostics required')
    return {'entity_id':OWNER,'unique_shared_source_cases':16,'diagnostic_context_cases':32,'context_datasets':2,'contexts':summary,'cases':rows,'default_context_in_source_case_totals':'shallow','deep_context_added_to_source_case_totals':False,'vertical_contexts_are_additive':False,'contexts_are_independent_observations':False,'additional_current_identities':0,'new_independent_observations':0,'source_metadata_only_no_velocity_calculation':True}


def build(root=ROOT):
    op=json.loads((root/OPERATOR).read_bytes());previous=frozen.OPERATOR
    try:
        frozen.OPERATOR=OPERATOR;report,unused=frozen.build(root)
    finally:frozen.OPERATOR=previous
    inventory=context_inventory(root,op)
    report['schema']='osw.current-depth-coverage-audit.v14';report['previous_coverage_snapshot']=op['previous_coverage_snapshot'];report['snapshot_reason']=op['snapshot_reason'];report['non_additive_diagnostic_context_coverage']=inventory
    report['context_inventory_scope']='Both Atlantic SECC contexts checked against own original source diagnosis. Same sixteen inputs; deep context excluded from frozen default-source totals. No raw velocity calculations or physical/annual/whole-route promotion.'
    raw=frozen.encode(report)
    if len(raw)>=2400000:raise ValueError('Fixed audit output cap exceeded')
    return report,raw


if __name__=='__main__':
    report,raw=build();out=Path('current-depth-coverage-audit-v14');out.mkdir(exist_ok=True);(out/'coverage.json').write_bytes(raw);print(json.dumps({'counts':report['counts'],'model_totals':report['registered_model_totals'],'context_summary':{k:v for k,v in report['non_additive_diagnostic_context_coverage'].items() if k!='cases'}}),flush=True)
