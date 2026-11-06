"""Reproduce complete coastal cohorts and reuse identical prior depth references."""
import copy,csv,hashlib,io,json,math
from collections import Counter
import load_current_depth_reference_inventory_v1 as base_loader
import load_current_depth_reference_inventory_v8 as defaults
import load_current_depth_reference_inventory_v11 as prior
import coastal_full_section_salinity_v1 as source

checked_piece=prior.checked_piece
reference_csv_bytes=prior.reference_csv_bytes
METRIC='derived_conditional_fresh_component_lower_boundary_depth'
SCHEMA='osw.current-depth-full-coastal-fresh-component-addendum.v1'
DIRECTORY='research/source-data/coastal-full-section-salinity-v1/'


def context_id(entity):return 'full-coastal-'+entity.split(':',1)[1]+'-hycom2022-original-core'
def context(entity):
    bearing,salt=source.RULES[entity]
    return {'entity_id':entity,'component_bearing_degrees_true':bearing,'velocity_threshold_m_s':.1,'practical_salinity_exclusive_upper_threshold':salt,'support_start':'original_velocity_core_no_reselection','time_operator':'original_quarterly_instantaneous_snapshots_not_annual_envelope','full_polar_temperature_density_classification_performed':False,'published_coastal_front_foot_definition_reproduced':False,'independently_validated_axis':False,'physical_current_bottom_established':False}


def read_bundle(a,reader):
    op=json.loads(checked_piece(a['source_operator'],reader));report=json.loads(checked_piece(a['derived_source_report'],reader));original=json.loads(checked_piece(a['original_velocity_audit_report'],reader))
    for file,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(file)).hexdigest()!=pin:raise ValueError('Original cohort source input changed: '+file)
    if report['operator_sha256']!=a['source_operator']['sha256'] or report['input_sha256']!=op['input_sha256']:raise ValueError('Exact frozen source operator and inputs required')
    expected=[];configs={};sections={};originals={r['source_section_file']:r for s in original['studies'] for r in s['records'] if r['entity_id'] in source.RULES}
    for study in op['studies']:
        manifest=json.loads(reader(study['manifest_file']));sop=json.loads(reader(study['source_operator_file']));configs[study['entity_id']]={**sop,**sop['currents'][study['entity_id']]}
        for piece in manifest['sections']:
            if piece['entity_id']!=study['entity_id']:continue
            file=study['source_directory']+piece['file'];raw=reader(file)
            if hashlib.sha256(raw).hexdigest()!=piece['sha256'] or len(raw)!=piece['bytes']:raise ValueError('Exact original velocity section required')
            expected.append(file);sections[file]=json.loads(raw)
    profiles=[]
    for piece in report['profiles']:
        if '/' in piece['file'] or '\\' in piece['file']:raise ValueError('Direct original source filenames required')
        profiles.append(json.loads(checked_piece({**piece,'file':DIRECTORY+piece['file']},reader)))
    ledger_raw=reader(DIRECTORY+'transport-ledger.json')
    if hashlib.sha256(ledger_raw).hexdigest()!=report['transport_ledger_sha256']:raise ValueError('Original transport ledger hash required')
    ledger=json.loads(ledger_raw)
    controls=[(file,json.loads(reader(file))) for file in op['retained_control_files']]
    return {'report':report,'operator':op,'expected_files':expected,'sections':sections,'originals':originals,'configs':configs,'profiles':profiles,'ledger':ledger,'controls':controls}


def reproduce(bundle):
    report=bundle['report'];records=report['records'];profiles=bundle['profiles'];expected=bundle['expected_files'];ledger=bundle['ledger']
    if report['schema']!='osw.coastal-full-section-salinity-source-report.v1' or report['status']!='ALL32SECTIONS_RETRIEVED_AND_CONTROLS_MATCH' or report['all_targets_preflighted_before_field_reads'] is not True or report['original_velocity_diagnoses_reproduced']!=32 or report['all_five_retained_controls_match'] is not True or any(report[k] for k in ['new_reference_inventory_rows_admitted','reference_inventory_updated','model_projection_inventory_updated','physical_current_bottom_established','runtime_changed','full_goal_complete']):raise ValueError('Complete original source cohort and historical source-stage limits required')
    if report['source_global_attributes'].get('field_type')!='instantaneous' or report['source_variable_attributes'].get('units') not in ['psu','PSU'] or report['source_variable_attributes'].get('standard_name')!='sea_water_salinity':raise ValueError('Original instantaneous practical salinity required')
    if len(expected)!=32 or len(set(expected))!=32 or len(records)!=32 or len(profiles)!=32 or [r['original_velocity_source_file'] for r in records]!=expected:raise ValueError('All and only32original cases in frozen order required')
    targets=[];results=[];planned=0
    for i,(record,p,file) in enumerate(zip(records,profiles,expected)):
        s=bundle['sections'][file];r=bundle['originals'][file];columns=s['columns'];n=len(columns);original=s['diagnosis'];slab=s['retrieved_hyperslab'];entity=s['entity_id'];bearing,salt=source.RULES[entity];z=s['depth_levels_m']
        if source.original_diagnose(z,[c['signed_reference_component_m_s'] for c in columns],bundle['configs'][entity])!=original:raise ValueError('Original velocity selection must reproduce unchanged')
        if p['schema']!='osw.coastal-full-section-native-salinity.v1' or p['original_velocity_source_file']!=file or p['original_velocity_source_sha256']!=r['source_section_sha256'] or record['original_velocity_source_sha256']!=r['source_section_sha256'] or record['profile']!=report['profiles'][i] or report['profiles'][i]['file']!=file.rsplit('/',1)[-1]:raise ValueError('Exact profile,report and original source audit links required')
        if p['entity_id']!=entity or record['entity_id']!=entity or r['entity_id']!=entity or p['original_selected_column_index']!=original['selected_column_index'] or record['original_selected_column_index']!=original['selected_column_index'] or r['selected_column_index']!=original['selected_column_index'] or p['original_horizontal_selection_status']!=original['horizontal_selection_status'] or record['original_horizontal_selection_status']!=original['horizontal_selection_status'] or record['status']!='FULL_NATIVE_SALINITY_SECTION_RETRIEVED':raise ValueError('Original owner,axis and selected column required')
        layer=original['selected_column_threshold_layers'][1] if original['selected_column_threshold_layers'] else None
        if p['original_primary_layer']!=layer or p['component_bearing_degrees_true']!=bearing or p['practical_salinity_exclusive_upper_threshold']!=salt or p['velocity_threshold_m_s']!=.1 or p['published_coastal_front_foot_definition_reproduced'] is not False or p['physical_current_bottom_established'] is not False:raise ValueError('Exact source-specific classifier and non-promotion required')
        if len(z)!=40 or p['depth_levels_m']!=z or not 3<=n<=150 or len(p['practical_salinity_columns'])!=n or any(len(c)!=40 or any(v is not None and (type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=50) for v in c) for c in p['practical_salinity_columns']):raise ValueError('Exact full finite/missing native salinity support required')
        if p['native_latitude_index']!=slab['latitude_index'] or p['native_longitude_indices_inclusive']!=slab['longitude_indices_inclusive'] or p['native_latitude_degrees_north']!=s['actual_source_latitude_degrees_north'] or p['native_longitudes_degrees_east']!=[c['native_source_longitude_degrees_east'] for c in columns]:raise ValueError('Every original native source column coordinate required')
        if p['opendap_dataset']!=source.DATASET or p['source_time_index']!=s['source_time_index'] or p['source_returned_timestamp_utc']!=s['snapshot_time_utc'] or record['snapshot_time_utc']!=s['snapshot_time_utc'] or r['snapshot_time_utc']!=s['snapshot_time_utc'] or record['section_id']!=s['section_definition']['id']:raise ValueError('Exact original snapshot and section required')
        classification=source.classify(s,p['practical_salinity_columns'])
        if classification!=p['classification'] or classification!=record['classification']:raise ValueError('Frozen native-field classification must reproduce exactly')
        planned+=40*n;targets.append({'file':file});results.append({'record':record,'profile':p,'profile_piece':{**report['profiles'][i],'file':DIRECTORY+report['profiles'][i]['file']},'original':r,'classification':classification,'source_index':i})
    passed,controls=source.check_controls(targets,{i:p for i,p in enumerate(profiles)},bundle['controls'])
    if not passed or controls!=report['retained_controls']:raise ValueError('All five retained controls must still match exactly')
    if ledger!=report['transport'] or ledger['retained_velocity_cell_pairs_audited']!=planned or ledger['planned_first_attempt_salinity_scalars']!=planned or ledger['successful_returned_salinity_scalars']!=planned or sum(r['requested_scalar_values'] for r in ledger['requests'])!=ledger['actual_requested_salinity_scalars']:raise ValueError('Exact original source ledger and returned/requested counts required')
    if ledger['joint_retained_pairs_plus_reserved_salinity_scalars']!=2*planned+ledger['additional_retry_scalars_reserved'] or ledger['conservative_retained_velocity_and_reserved_salinity_bytes']!=24*planned+8*ledger['additional_retry_scalars_reserved'] or ledger['maximum_joint_native_cell_units']!=250000 or ledger['maximum_decoded_bytes']!=7000000:raise ValueError('Exact joint reservation units and frozen caps required')
    if 2*planned+ledger['additional_retry_scalars_reserved']>250000 or 24*planned+8*ledger['additional_retry_scalars_reserved']>7000000:raise ValueError('Original joint native/decoded caps required')
    if dict(Counter(r['classification']['status'] for r in records))!=report['classification_status_counts']:raise ValueError('All original class outcomes required')
    return results


def reference(case,a):
    r=case['original'];c=case['classification'];lower=c['lower'];piece=case['profile_piece'];row={k:None for k in defaults.NULL_FIELDS};row.update({k:False for k in defaults.FALSE_FIELDS})
    row.update(id='full-coastal-fresh-'+r['entity_id'].split(':',1)[1]+'-'+r['snapshot_time_utc'][:10]+'-'+r['section_id'],entity_id=r['entity_id'],metric=METRIC,approximate_value_m=lower['boundary_depth_m'],lower_bound_m=None,lower_bound_operator=None,unit='m',vertical_datum='local_sea_surface_positive_down',phase_label=r['snapshot_time_utc'],geographic_scope=r['branch_scope'],temporal_scope='Single original2022quarterly instantaneous model snapshot;not a seasonal mean or annual envelope.',source_definition='First finite adjacent native lower exit from original-core-connected fresh salinity/component predicate;conditional regional descriptor,not physical current bottom or coastal front-foot scale.',evidence_kind='reproduced_full_native_coastal_section_conditional_fresh_component_crossing',source_url='https://www.hycom.org/dataserver/gofs-3pt1/analysis',source_citation='GOFS3.1expt93.0ts3z2022practicalsalinity with frozen uv3z2022original component/axis/core;source-specific declared conditionalfreshclass.',source_locator=piece['file']+'#/classification/lower',qualification='Native bracket is resolution support,not uncertainty or annual range. Original geographic velocity core and salinity class do not independently validate coastal identity. No full-current thickness,route/width pairing or volume.',source_context_id=context_id(r['entity_id']),source_file=piece['file'],source_sha256=piece['sha256'],source_pointer='/classification/lower',source_report_file=a['derived_source_report']['file'],source_report_sha256=a['derived_source_report']['sha256'],source_report_pointer='/records/'+str(case['source_index']),source_native_bracket_m=copy.deepcopy(lower['bracket_m']),source_native_bracket_is_confidence_interval=False,source_native_bracket_is_annual_range=False,source_original_audit_record=copy.deepcopy(r),source_classification=copy.deepcopy(c),source_contiguous_support_start='original_velocity_core',source_sampled_lon_lat=copy.deepcopy(r['sampled_lon_lat']),source_surface_sample_support=c['upper']['status']=='surface_sample_supported',published_coastal_front_foot_definition_reproduced=False)
    return row


def admission(before,bundle,a):
    cases=reproduce(bundle);existing={};new=[];reused=[];outcomes=[];used=set()
    for row in before['evidence']:
        if row['metric']!=METRIC or row['entity_id'] not in source.RULES:continue
        file=row['source_original_audit_record']['source_section_file']
        if file in existing:raise ValueError('Unique prior reference per original case required')
        existing[file]=row
    for case in cases:
        c=case['classification'];r=case['original'];file=r['source_section_file'];lower=c.get('lower') or {};eligible=c['status']=='conditional_fresh_component_core_supported' and lower.get('status')=='adjacent_native_joint_predicate_crossing' and lower.get('boundary_depth_m') is not None
        outcome={'original_velocity_source_file':file,'source_index':case['source_index'],'entity_id':r['entity_id'],'snapshot_time_utc':r['snapshot_time_utc'],'section_id':r['section_id'],'classification':copy.deepcopy(c),'reference_id':None,'admission_status':'UNRESOLVED_OR_UNCLASSIFIED_NO_REFERENCE'}
        if eligible and file in existing:
            old=existing[file]
            if old['source_original_audit_record']!=r or old['source_classification']!=c or old['approximate_value_m']!=lower['boundary_depth_m'] or old['source_native_bracket_m']!=lower['bracket_m'] or old['phase_label']!=r['snapshot_time_utc'] or old['entity_id']!=r['entity_id']:raise ValueError('Previously admitted descriptor must reproduce identically before reuse')
            used.add(file);reused.append(old['id']);outcome.update(reference_id=old['id'],admission_status='EXACT_EXISTING_REFERENCE_REUSED_UNCHANGED')
        elif eligible:
            row=reference(case,a);new.append(row);outcome.update(reference_id=row['id'],admission_status='NEW_CONDITIONAL_DESCRIPTOR_ADMITTED')
        outcomes.append(outcome)
    if used!=set(existing):raise ValueError('No prior reference may disappear or become unclassified')
    audit={'schema':'osw.coastal-fresh-depth-reference-admission-report.v1','operator_file':a['operator_file'],'operator_sha256':a['operator_sha256'],'input_sha256':a['input_sha256'],'source_report':copy.deepcopy(a['derived_source_report']),'original_cases_reproduced':len(cases),'retained_controls_matched':5,'new_reference_count':len(new),'reused_reference_ids':reused,'cases':outcomes,'new_ocean_field_requests':0,'physical_current_bottom_established':False,'runtime_changed':False,'full_goal_complete':False}
    return new,audit


def assemble(*parts):
    result=prior.assemble(*parts[:-1]);known={r['entity_id'] for r in result['records']};seen={r['id'] for r in result['evidence']}
    for a,bundle in parts[-1]:
        expected,audit=admission(result,bundle,a);contexts={context_id(row['entity_id']):context(row['entity_id']) for row in expected}
        if a['evidence']!=expected or a['source_contexts']!=contexts or set(contexts)&set(result['source_contexts']) or bundle['admission_report']!=audit:raise ValueError('Exact all-and-only new references,reuse audit and source contexts required')
        for row in expected:
            if row['id'] in seen or row['entity_id'] not in known:raise ValueError('Unique known direct owner required')
            seen.add(row['id'])
        result['source_contexts'].update(copy.deepcopy(contexts));result['evidence'].extend(copy.deepcopy(expected))
    for r in result['records']:r['depth_reference_ids']=[e['id'] for e in result['evidence'] if e['entity_id']==r['entity_id']]
    result['counts']=base_loader.counts_for(result['records'],result['evidence']);result['metric_counts']=dict(sorted(Counter(r['metric'] for r in result['evidence']).items()));return result


def read_parts(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v12':raise ValueError('Known reference inventory v12 required')
    old=[];cohorts=[];seen=set()
    for part in manifest['addenda']:
        if part['id'] in seen:raise ValueError('Duplicate addendum identity')
        seen.add(part['id']);a=json.loads(checked_piece(part['json'],reader))
        if a['schema']!=SCHEMA:
            if cohorts:raise ValueError('Prior source classes must precede complete coastal cohort')
            old.append(part);continue
        if a['id']!=part['id'] or a['base_snapshot_sha256']!=manifest['base']['json']['sha256'] or a['runtime_changed'] or a['full_goal_complete']:raise ValueError('Original base and non-promotion required')
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));rows=list(incoming);fields=list(incoming.fieldnames)
        if len(rows)!=len(a['evidence']) or set(fields)!={k for r in a['evidence'] for k in r} or any(row!={k:base_loader.cell(raw.get(k)) for k in fields} for raw,row in zip(a['evidence'],rows)):raise ValueError('Every exact typed source JSON/CSVcell required')
        bundle=read_bundle(a,reader);bundle['admission_report']=json.loads(checked_piece(a['reference_admission_report'],reader));cohorts.append((a,bundle))
    return (*prior.read_parts({'schema':'osw.current-depth-reference-inventory.v11','base':manifest['base'],'addenda':old},reader),cohorts)


def load_inventory(manifest,reader):
    result=assemble(*read_parts(manifest,reader))
    if result['counts']!=manifest['counts'] or result['metric_counts']!=manifest['metric_counts']:raise ValueError('Reference counts do not reproduce')
    allowed={'schema','status','generator_file','generator_sha256','interpretation','runtime_changed','query_ui_integration_performed','full_goal_complete'}
    if not set(manifest['view_metadata'])<=allowed or any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('No runtime or completion promotion')
    result.update(copy.deepcopy(manifest['view_metadata']));result['inventory_base_file']=manifest['base']['json']['file'];result['inventory_addendum_files']=[p['json']['file'] for p in manifest['addenda']];result['member_depth_index_scope']='base_only_not_updated_for_addenda';return result


def combined_csv_bytes(manifest,reader):
    load_inventory(manifest,reader);first=csv.DictReader(io.StringIO(checked_piece(manifest['base']['csv'],reader).decode()));columns=list(first.fieldnames);rows=list(first)
    for part in manifest['addenda']:
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));columns.extend(k for k in incoming.fieldnames if k not in columns);rows.extend(list(incoming))
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows);return out.getvalue().encode()
