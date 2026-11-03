"""Cloud-only provenance join; no raw ocean-field reads or depth calculations."""
import hashlib,json
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-coverage-audit-operator-v1.json'
INTERIOR='interior_section_integral_maximum_with_finite_neighbors_not_independently_validated_axis'
RESOLVED='REGIONAL_SEED_CONNECTED_VELOCITY_THRESHOLD_CURTAIN'


def sha(raw):return hashlib.sha256(raw).hexdigest()
def encode(value):return (json.dumps(value,separators=(',',':'),allow_nan=False)+'\n').encode()
def key(row):return row['source_file'],row['source_sha256']


def source_row(row,spec,source_operator=None):
    adapter=spec.get('facts_schema_adapter','ORIGINAL_COMMON_FIELDS')
    if adapter=='ORIGINAL_COMMON_FIELDS':return row
    if adapter!='LEGACY_NORTH_BRAZIL_EXPLICIT_10CMS_FIELDS' or spec['facts']!='research/north-brazil-depth-sections-source-facts-v1.json':raise ValueError('Unknown facts schema adapter')
    if source_operator is None or source_operator['primary_threshold_m_s']!=.1 or source_operator['entity_id']!=row['entity_id']:raise ValueError('Original North Brazil 10cm/s operator required')
    layers=[layer for layer in row['selected_column_threshold_layers'] if layer['threshold_m_s']==.1]
    if row['selected_column_index'] is None:
        if layers or row['primary10cms_lower_status'] is not None:raise ValueError('Unselected legacy source must remain unresolved')
    elif len(layers)!=1 or layers[0]['lower_status']!=row['primary10cms_lower_status']:raise ValueError('Legacy primary lower status must match original 10cm/s layer')
    return {**row,'primary_threshold_m_s':.1,'primary_lower_status':row['primary10cms_lower_status']}


def merge_source(index,row,facts_file):
    """Identical source bytes represent one case, even if several facts cite it."""
    fields=['entity_id','section_id','snapshot_time_utc','horizontal_selection_status','selected_column_index','primary_threshold_m_s','primary_lower_status']
    value={name:row[name] for name in fields};value.update(source_file=row['source_file'],source_sha256=row['source_sha256'])
    if any(k[0]==row['source_file'] and k[1]!=row['source_sha256'] for k in index):raise ValueError('Conflicting hashes for one source path')
    k=key(row)
    if k in index:
        if {name:index[k][name] for name in fields}!= {name:row[name] for name in fields}:raise ValueError('Conflicting source-case descriptions')
        index[k]['facts_files'].add(facts_file)
    else:index[k]={**value,'facts_files':{facts_file}}


def attach_curtain(index,derived,case,dataset,alternate=None,threshold_policy='SOURCE_PRIMARY_ONLY'):
    k=key(case)
    if k not in index:raise ValueError('Curtain has no registered source case')
    source=index[k]
    pairs={'entity_id':'entity_id','section_id':'section_id','snapshot_time_utc':'snapshot_time_utc','original_horizontal_selection_status':'horizontal_selection_status','original_selected_column_index':'selected_column_index','velocity_threshold_m_s':'primary_threshold_m_s'}
    mismatches={a:{'curtain':case[a],'source_facts':source[b]} for a,b in pairs.items() if case[a]!=source[b]}
    legacy_policy='LEGACY_MEDITERRANEAN_0P1_VARIANT_NOT_SOURCE_PRIMARY'
    if threshold_policy not in ['SOURCE_PRIMARY_ONLY',legacy_policy] or (threshold_policy==legacy_policy and dataset!='research/mediterranean-regional-velocity-depth-curtains-v1.json'):raise ValueError('Unknown or misplaced threshold policy')
    is_alternate=threshold_policy==legacy_policy and set(mismatches)=={'velocity_threshold_m_s'} and source['entity_id']=='current:balearic' and source['primary_threshold_m_s']==.05 and case['velocity_threshold_m_s']==.1
    if is_alternate:
        if alternate is None:raise ValueError('Separate alternate-threshold destination required')
        mismatches={}
    if mismatches:raise ValueError('Curtain/source metadata mismatch '+json.dumps({'dataset':dataset,'source_file':case['source_file'],'fields':mismatches},sort_keys=True))
    if case['core_reselected'] or case['physical_current_bottom_established'] or case['volume_m3'] is not None:raise ValueError('No reselection or physical promotion in proxy audit')
    if case['status']==RESOLVED and source['horizontal_selection_status']!=INTERIOR:raise ValueError('Unresolved original selection cannot become resolved')
    runs=[run for column in case['columns'] for run in column['connected_depth_runs']]
    value={'status':case['status'],'velocity_threshold_m_s':case['velocity_threshold_m_s'],'source_primary_threshold_m_s':source['primary_threshold_m_s'],'seed_connected_profile_date_columns':sum(bool(c['connected_depth_runs']) for c in case['columns']),'vertical_runs':len(runs),'lower_boundary_status_counts':dict(Counter(r['threshold_layer']['lower_status'] for r in runs)),'lateral_gate_censored':case.get('lateral_gate_censored',False)}
    destination=alternate if is_alternate else derived
    if k in destination:
        if {name:destination[k][name] for name in value}!=value:raise ValueError('Conflicting duplicate curtain results')
        destination[k]['datasets'].add(dataset)
    else:destination[k]={**value,'datasets':{dataset}}


def source_counts(keys,index,derived,alternate=None):
    keys=set(keys);processed=keys & set(derived);backlog=keys-set(derived)
    return {'registered_source_cases':len(keys),'source_interior_selections':sum(index[k]['horizontal_selection_status']==INTERIOR for k in keys),'source_unresolved_selections':sum(index[k]['horizontal_selection_status']!=INTERIOR for k in keys),'source_primary_adjacent_lower_crossings':sum(index[k]['primary_lower_status']=='adjacent_isotach_crossing' for k in keys),'cases_with_contour_processing':len(processed),'resolved_contours':sum(derived[k]['status']==RESOLVED for k in processed),'processed_unresolved_cases':sum(derived[k]['status']!=RESOLVED for k in processed),'cases_with_declared_alternate_threshold_contours':len(keys & set(alternate or {})),'unprocessed_source_cases':len(backlog),'unprocessed_interior_cases':sum(index[k]['horizontal_selection_status']==INTERIOR for k in backlog),'unprocessed_unresolved_cases':sum(index[k]['horizontal_selection_status']!=INTERIOR for k in backlog),'seed_connected_profile_date_columns':sum(derived[k]['seed_connected_profile_date_columns'] for k in processed),'vertical_runs':sum(derived[k]['vertical_runs'] for k in processed),'lateral_gate_censored_contours':sum(derived[k]['lateral_gate_censored'] for k in processed)}


def build(root=ROOT):
    read=lambda file:json.loads((root/file).read_bytes())
    op=read(OPERATOR)
    for file,pin in op['input_sha256'].items():
        if sha((root/file).read_bytes())!=pin:raise ValueError('Pinned audit input changed: '+file)
    inventory=read(op['reference_inventory']);base=read(inventory['base']['json']['file'])
    evidence=list(base['evidence'])
    if sha((root/inventory['base']['json']['file']).read_bytes())!=inventory['base']['json']['sha256']:raise ValueError('Reference base hash mismatch')
    for addendum in inventory['addenda']:
        file=addendum['json']['file']
        if sha((root/file).read_bytes())!=addendum['json']['sha256']:raise ValueError('Reference addendum hash mismatch')
        evidence.extend(read(file)['evidence'])
    if len(evidence)!=inventory['counts']['depth_references'] or len({e['id'] for e in evidence})!=len(evidence):raise ValueError('Exact unique reference inventory required')
    if dict(Counter(e['metric'] for e in evidence))!=inventory['metric_counts'] or dict(Counter(e['unit'] for e in evidence))!=inventory['coordinate_unit_counts']:raise ValueError('Reference metrics/native units mismatch')
    identities={r['entity_id']:r for r in base['records']}
    if len(identities)!=inventory['counts']['identities']:raise ValueError('Exact original identity register required')
    references=defaultdict(list)
    for e in evidence:references[e['entity_id']].append(e)
    index={};cohorts={};source_mentions=0
    for spec in op['model_section_facts']:
        facts=read(spec['facts']);pins=read(spec['review'])['input_sha256'];descriptors=facts['descriptors']
        if len(descriptors)!=facts['counts']['section_date_cases']:raise ValueError('Facts case count mismatch')
        original=None
        if spec.get('facts_schema_adapter')=='LEGACY_NORTH_BRAZIL_EXPLICIT_10CMS_FIELDS':
            file=spec['source_operator']
            if facts['operator_file']!=file or facts['operator_sha256']!=sha((root/file).read_bytes()):raise ValueError('Legacy facts/operator pin mismatch')
            original=read(file)
        keys=[]
        for row in descriptors:
            if pins.get(row['source_file'])!=row['source_sha256']:raise ValueError('Source descriptor lacks matching retained review pin')
            row=source_row(row,spec,original)
            merge_source(index,row,spec['facts']);keys.append(key(row));source_mentions+=1
        if len(keys)!=len(set(keys)):raise ValueError('Duplicate case inside a source cohort')
        cohorts[spec['facts']]=set(keys)
    derived={};alternate={};curtain_mentions=0
    for spec in op['curtain_datasets']:
        report=read(spec['data']);pins=read(spec['review'])['input_sha256']
        if pins.get(spec['data'])!=sha((root/spec['data']).read_bytes()) or len(report['cases'])!=report['counts']['cases']:raise ValueError('Retained curtain review/count mismatch')
        for case in report['cases']:
            if pins.get(case['source_file'])!=case['source_sha256']:raise ValueError('Curtain source lacks retained review pin')
            attach_curtain(index,derived,case,spec['data'],alternate,spec.get('threshold_policy','SOURCE_PRIMARY_ONLY'));curtain_mentions+=1
    fitted={};fitted_by_owner=defaultdict(list)
    for spec in op['fitted_sensitivity_datasets']:
        report=read(spec['data']);pins=read(spec['review'])['input_sha256']
        if pins.get(spec['data'])!=sha((root/spec['data']).read_bytes()):raise ValueError('Fitted report pin mismatch')
        for case in report['cases']:
            if pins.get(case['source_file'])!=case['source_sha256'] or case['timestamp_is_instantaneous_observation_date'] or case['whole_route_representative']:raise ValueError('Fitted provenance/interpretation mismatch')
            sensitivity=case['sensitivity']
            if sensitivity['confidence_interval_established'] or sensitivity['physical_current_bottom_established'] or sensitivity['volume_eligible']:raise ValueError('Fitted sensitivity cannot be promoted')
            k=(case['source_file'],case['source_sha256'],case['source_pointer'])
            value={'entity_id':case['entity_id'],'product_kind':case['source_product_kind'],'finite_fixed_cutoff_sensitivity':sensitivity['lower_depth_sensitivity_range_m'] is not None,'dataset':spec['data']}
            if k in fitted and fitted[k]!=value:raise ValueError('Conflicting fitted source pointer')
            fitted[k]=value
    for value in fitted.values():fitted_by_owner[value['entity_id']].append(value)
    owners=set(identities)|set(references)|{r['entity_id'] for r in index.values()}|set(fitted_by_owner)
    rows=[]
    for owner in sorted(owners):
        registered=identities.get(owner);keys={k for k,v in index.items() if v['entity_id']==owner};counts=source_counts(keys,index,derived,alternate);refs=references[owner];fits=fitted_by_owner[owner]
        actions=[]
        if counts['unprocessed_interior_cases']:actions.append('TRACE_RETAINED_INTERIOR_SECTION_CASES')
        if counts['source_unresolved_selections']:actions.append('REVIEW_UNRESOLVED_SOURCE_SELECTIONS_WITHOUT_RETUNING')
        if not keys:actions.append('NO_CASES_IN_REGISTERED_MODEL_SECTION_SCOPE_REVIEW_OTHER_SOURCES')
        if not refs:actions.append('NO_DIRECT_REFERENCE_ROWS_DO_NOT_INHERIT_FROM_RELATED_IDENTITIES')
        rows.append({'entity_id':owner,'name':registered['name'] if registered else None,'identity_level':registered['identity_level'] if registered else None,'in_reference_identity_register':registered is not None,'direct_reference_rows':len(refs),'reference_metric_counts':dict(sorted(Counter(e['metric'] for e in refs).items())),'reference_unit_counts':dict(sorted(Counter(e['unit'] for e in refs).items())),'reference_evidence_kind_counts':dict(sorted(Counter(e['evidence_kind'] for e in refs).items())),'registered_model_sections':counts,'source_facts_files':sorted({f for k in keys for f in index[k]['facts_files']}),'curtain_datasets':sorted({f for k in keys for container in [derived,alternate] if k in container for f in container[k]['datasets']}),'fitted_profile_sensitivity_cases':len(fits),'fitted_finite_sensitivity_cases':sum(v['finite_fixed_cutoff_sensitivity'] for v in fits),'fitted_dataset_files':sorted({v['dataset'] for v in fits}),'next_actions':actions,'whole_route_physical_depth_established':False,'annual_depth_extrema_established':False,'volume_estimate_established':False})
    cohort_rows=[]
    for file,keys in sorted(cohorts.items()):cohort_rows.append({'facts_file':file,'owners':sorted({index[k]['entity_id'] for k in keys}),**source_counts(keys,index,derived,alternate)})
    cohort_rows.sort(key=lambda r:(-r['unprocessed_interior_cases'],-r['unprocessed_source_cases'],r['facts_file']))
    report={'schema':'osw.current-depth-coverage-audit.v1','status':'SCOPED_PROVENANCE_COVERAGE_NOT_PHYSICAL_DEPTH_COMPLETION','operator_file':OPERATOR,'operator_sha256':sha((root/OPERATOR).read_bytes()),'input_sha256':op['input_sha256'],'counts':{'reference_identities':len(identities),'reference_rows':len(evidence),'identity_rows_including_any_extra_direct_owners':len(rows),'reference_identities_with_direct_rows':sum(bool(references[k]) for k in identities),'registered_model_fact_files':len(op['model_section_facts']),'curtain_dataset_files':len(op['curtain_datasets']),'source_descriptor_mentions':source_mentions,'unique_registered_model_source_cases':len(index),'duplicate_source_mentions_removed':source_mentions-len(index),'curtain_case_mentions':curtain_mentions,'unique_cases_with_contour_processing':len(derived),'unique_alternate_threshold_source_cases':len(alternate),'unique_source_cases_with_any_threshold_contours':len(set(derived)|set(alternate)),'duplicate_curtain_mentions_removed':curtain_mentions-len(derived)-len(alternate),'fitted_profile_sensitivity_cases':len(fitted),'fitted_finite_sensitivity_cases':sum(v['finite_fixed_cutoff_sensitivity'] for v in fitted.values()),'whole_route_physical_depth_profiles':0,'volume_estimates':0,'new_ocean_field_requests':0,'new_depth_references':0},'registered_model_totals':source_counts(index,index,derived,alternate),'alternate_threshold_cases':[{'source_file':k[0],'source_sha256':k[1],'entity_id':index[k]['entity_id'],'section_id':index[k]['section_id'],'snapshot_time_utc':index[k]['snapshot_time_utc'],**{name:value for name,value in v.items() if name!='datasets'},'datasets':sorted(v['datasets'])} for k,v in sorted(alternate.items())],'reference_unit_counts':dict(Counter(e['unit'] for e in evidence)),'source_cohort_backlog':cohort_rows,'currents':rows,'scope':op['scope'],'interpretation':op['interpretation'],'raw_ocean_field_data_reaudited':False,'runtime_changed':False,'full_goal_complete':False}
    raw=encode(report)
    if len(raw)>=2400000:raise ValueError('Audit output exceeds fixed bound')
    return report,raw


if __name__=='__main__':
    report,raw=build();out=Path('current-depth-coverage-audit-v1');out.mkdir(exist_ok=True);(out/'coverage.json').write_bytes(raw);print(json.dumps({'counts':report['counts'],'model_totals':report['registered_model_totals'],'top_backlog':report['source_cohort_backlog'][:8]}),flush=True)
