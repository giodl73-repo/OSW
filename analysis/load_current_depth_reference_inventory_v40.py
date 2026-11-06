"""Keep Leeuwin mean-profile censor support separate from finite monthly boundaries."""
import copy,csv,io,json
import load_current_depth_reference_inventory_v39 as previous
import compiled_depth_catalog_view_v1 as compiled
from load_current_depth_reference_inventory_v1 import checked_piece,reference_csv_bytes,cell
SOURCE='research/leeuwin-monthly-depth-descriptors-v1.json'
SOURCE_SHA='f9fc887bfc2c6888c345f80ce0cc3f712d48592895981d914b51538f760bd310'
REVIEW='research/leeuwin-depth-sensitivity-source-review-v1.json'
REVIEW_SHA='d0952a305ccb5df7f9842d9d9f64136e03b8afcfb177b45fb391a0be59d2652d'
METHOD='research/leeuwin-seasonal-depth-operator-v1.json'
METHOD_SHA='4a523bc949228d584ffccc5e65ceb7593c0d1f60c440b80003329975defc7a12'
PRODUCT_SHA='240680c821d330836c5de4352021bb1c3d0d630f0c34d676c884940798da576a'
CONTEXT='leeuwin-watr50-processed-monthly-mean-censor-support'
SCHEMA='osw.current-depth-leeuwin-mean-censor-support-addendum.v1'
ADDENDUM_ID='leeuwin-watr50-reviewed-monthly-censor-support-v1'
CENSORED=(3,8,11)
SUPPORT_DEPTH_M=475
NULLS=previous.NULLS
FALSES=previous.FALSES

def qualify(source,review,method,before):
    if source['schema']!='osw.leeuwin-monthly-depth-descriptors.v1' or source['status']!='NINE_LOCAL_CALCULATED_ZERO_DESCRIPTORS_THREE_UNKNOWN' or source['entity_id']!='current:leeuwin' or source['site_id']!='WATR50' or source['source_product_sha256']!=PRODUCT_SHA:raise ValueError('Exact reviewed monthly index and product required')
    if review['status']!='PASS_METHOD_SENSITIVITY_SEPARATE_FROM_PUBLISHED_BOUNDARIES' or review['exact_paper_reproduction_established'] is not False:raise ValueError('Reviewed calculation remains separate from published boundaries')
    statement=review['scientific_review'][3]
    if 'March,August,November have no strict sign crossing' not in statement or '475m deepest level' not in statement:raise ValueError('Exact reviewed censor-support statement required')
    if method['entity_id']!='current:leeuwin' or method['site_id']!='WATR50' or method['source_sha256']!=PRODUCT_SHA or method['local_along_mean_bearing_degrees_true']!=348 or method['positive_velocity_direction']!='equatorward' or method['accepted_component_flags']!=[1,2,3,4] or method['core_search_depth_interval_m']!=[0,200]:raise ValueError('Original mean operator, source flags and sign convention required')
    months=source['months']
    if [r['month'] for r in months]!=list(range(1,13)) or source['annual_depth_range_m'] is not None or source['seasonal_interpolation_performed'] is not False:raise ValueError('All twelve original months without annual interpolation')
    by_id={e['id']:e for e in before['evidence']};resolved={}
    for r in months:
        m=r['month']
        if m in CENSORED:
            if r['depth_reference_id'] is not None or r['display_depth_m'] is not None or r['status']!='unknown_no_strict_crossing' or r['diagnostic_status']!='censored_at_deepest_level' or r['sampling_limit_is_boundary'] is not False:raise ValueError('Three original boundary gaps must stay unknown')
        else:
            e=by_id.get(r['depth_reference_id'])
            if e is None or e['entity_id']!='current:leeuwin' or e['metric']!='derived_mean_velocity_zero_crossing_depth' or e['calendar_months']!=[m] or e['approximate_value_m']!=r['display_depth_m'] or e['source_product_sha256']!=PRODUCT_SHA or e['local_along_mean_bearing_degrees_true']!=348 or e['source_accepted_quality_flags']!=[1,2,3,4]:raise ValueError('Every existing finite monthly reference must reconcile')
            resolved[m]=e
    exemplar=resolved[1]
    for e in resolved.values():
        if any(e[k]!=exemplar[k] for k in ['source_record_period','mooring_lon_lat','source_case_id']):raise ValueError('One unchanged local processed cohort required')
    return resolved,exemplar

def references(source,review,method,before):
    _,base=qualify(source,review,method,before);rows=[]
    for month in CENSORED:
        r={k:None for k in NULLS};r.update({k:False for k in FALSES})
        r.update(id=f'leeuwin-osw-tr50-month-{month:02d}-mean-sign-censored-support',entity_id='current:leeuwin',metric='derived_censored_mean_flow_reach',unit='m',
            lower_bound_m=SUPPORT_DEPTH_M,lower_bound_exclusive=False,calendar_months=[month],phase_label=f'calendar_month_{month}',
            vertical_datum=base['vertical_datum'],geographic_scope=base['geographic_scope'],temporal_scope=base['temporal_scope'],
            evidence_kind='reviewed_derived_processed_monthly_mean_sign_support_summary',
            source_definition='Inclusive sampled poleward-sign reach of the processed calendar-month mean profile; strict reversal boundary remains unknown.',
            source_url=method['source_url'],source_citation=method['source_citation'],source_file=SOURCE,source_sha256=SOURCE_SHA,source_pointer='/months/'+str(month-1),source_context_id=CONTEXT,
            source_locator=REVIEW+'#/scientific_review/3; '+SOURCE+'#/months/'+str(month-1),
            support_summary_file=REVIEW,support_summary_sha256=REVIEW_SHA,support_summary_pointer='/scientific_review/3',
            source_product_sha256=PRODUCT_SHA,source_record_period=copy.deepcopy(base['source_record_period']),source_case_id=base['source_case_id'],
            source_site_id='WATR50',mooring_lon_lat=copy.deepcopy(base['mooring_lon_lat']),local_along_mean_bearing_degrees_true=348,
            processed_product_flag_definitions=copy.deepcopy(method['source_flags']),accepted_processed_product_flags=[1,2,3,4],
            temporal_operator='sampled_sign_support_of_calendar_month_pooled_daily_mean_not_mean_individual_boundaries',
            computed_zero_crossing_depth_m=None,interpolation_bracket_m=None,source_selected_daily_records=None,
            source_acknowledgement=method['source_acknowledgement'],source_license='CC-BY-4.0',
            qualification='Censored strict-sign support of a processed monthly mean, including observed, extrapolated and SOM-filled velocities; not evidence of strong or statistically significant flow at475m. The sign-reversal boundary, physical current bottom/thickness and uncertainty remain unknown. No exact paper reproduction, annual extrema, missing-month interpolation, independent observation, width join or volume.')
        rows.append(r)
    return rows

def context(method):
    return {'entity_id':'current:leeuwin','source_file':SOURCE,'source_sha256':SOURCE_SHA,'support_summary_file':REVIEW,'support_summary_sha256':REVIEW_SHA,
        'quantity':'censored_sampled_sign_support_of_processed_monthly_mean_not_boundary','months':list(CENSORED),'inclusive_support_depth_m':SUPPORT_DEPTH_M,
        'boundary_gaps_filled':0,'new_independent_observing_cases':0,'processed_product_flag_definitions':copy.deepcopy(method['source_flags']),
        'historical_native_budget_compliance_reestablished':False,'physical_current_depth_established':False}

def assemble(before,a,source,review,method):
    expected=references(source,review,method,before)
    if a['schema']!=SCHEMA or a['id']!=ADDENDUM_ID or a['evidence']!=expected or a['source_contexts']!={CONTEXT:context(method)} or any(a.get(k) is not False for k in ['runtime_changed','full_goal_complete']):raise ValueError('Exact three support references without boundary promotion')
    out=copy.deepcopy(before);old={e['id'] for e in out['evidence']}
    if CONTEXT in out['source_contexts'] or any(e['id'] in old for e in expected):raise ValueError('Duplicate support reference/context')
    out['evidence'].extend(expected);out['source_contexts'][CONTEXT]=context(method);compiled.refresh(out);return out

def calendar_series(view,source,review,method):
    resolved,base=qualify(source,review,method,view);support={r['calendar_months'][0]:r for r in view['evidence'] if r.get('source_context_id')==CONTEXT};rows=[]
    if set(support)!=set(CENSORED):raise ValueError('All three canonical support IDs required')
    for month in range(1,13):
        e=resolved.get(month);s=support.get(month)
        rows.append({'month':month,'boundary_reference_id':e['id'] if e else None,'support_reference_id':s['id'] if s else None,
            'status':'calculated_local_mean_velocity_crossing' if e else 'boundary_unknown_censored_processed_mean_sign_support',
            'display_boundary_depth_m':e['approximate_value_m'] if e else None,'computed_zero_crossing_depth_m':e['computed_zero_crossing_depth_m'] if e else None,
            'interpolation_bracket_m':copy.deepcopy(e['interpolation_bracket_m']) if e else None,'support_lower_bound_m':SUPPORT_DEPTH_M if s else None,
            'support_lower_bound_exclusive':False if s else None,'sampling_limit_is_boundary':False,'physical_uncertainty_m':None})
    return {'schema':'osw.leeuwin-monthly-depth-support-series.v2','entity_id':'current:leeuwin','site_id':'WATR50',
        'time_operator':'calendar_month_pooled_daily_processed_mean_profiles_not_instantaneous_boundaries','source_record_period':copy.deepcopy(base['source_record_period']),
        'mooring_lon_lat':copy.deepcopy(base['mooring_lon_lat']),'months':rows,'counts':{'calendar_months':12,'finite_boundary_descriptors':9,'censored_support_months':3,'unknown_boundary_months':3},
        'processed_product_flags':copy.deepcopy(method['source_flags']),'annual_depth_range_m':None,'seasonal_interpolation_performed':False,
        'physical_current_bottom_established':False,'physical_thickness_m':None,'volume_m3':None,'source_acknowledgement':method['source_acknowledgement'],
        'interpretation':'Finite crossings and475m censor-support markers are different quantities. Never draw a boundary through censored months or use475m as an annual maximum. Rounding and5m computational brackets are not physical uncertainty. All values are local processed-mean descriptors, not independent observations or whole-current depths.',
        'runtime_changed':False,'full_goal_complete':False}

def check_csv(raw,rows):
    incoming=list(csv.DictReader(io.StringIO(raw.decode('utf8'))));fields=list(incoming[0])
    if len(incoming)!=len(rows) or set(fields)!={k for r in rows for k in r} or any(row!={k:cell(e.get(k)) for k in fields} for e,row in zip(rows,incoming)):raise ValueError('Complete JSON/CSV cell parity required')

def load_inventory(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v40':raise ValueError('Inventoryv40 required')
    before=previous.load_inventory(json.loads(checked_piece(manifest['previous_inventory'],reader)),reader)
    part=manifest['reference_addendum'];a=json.loads(checked_piece(part['json'],reader))
    for key,p,h in [('source_result',SOURCE,SOURCE_SHA),('support_review',REVIEW,REVIEW_SHA),('mean_operator',METHOD,METHOD_SHA)]:
        if a[key]['file']!=p or a[key]['sha256']!=h:raise ValueError('Exact reviewed descriptor pieces required')
    source=json.loads(checked_piece(a['source_result'],reader));review=json.loads(checked_piece(a['support_review'],reader));method=json.loads(checked_piece(a['mean_operator'],reader))
    out=assemble(before,a,source,review,method);check_csv(checked_piece(part['csv'],reader),a['evidence']);compiled.check_counts(out,manifest)
    series=calendar_series(out,source,review,method);pieces=manifest['calendar_series']
    if json.loads(checked_piece(pieces['json'],reader))!=series:raise ValueError('Exact twelve-month series must reconcile with canonical references')
    check_csv(checked_piece(pieces['csv'],reader),series['months'])
    out['calendar_depth_series']=copy.deepcopy(before.get('calendar_depth_series',[]))+[series]
    allowed={'schema','status','interpretation','runtime_changed','query_ui_integration_performed','full_goal_complete'}
    if not set(manifest['view_metadata'])<=allowed or any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('View metadata cannot overwrite data or promote completion')
    out.update(copy.deepcopy(manifest['view_metadata']));return out
