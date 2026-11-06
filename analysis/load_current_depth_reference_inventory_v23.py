"""Admit audited daily observed lower-isotach estimates, preserving physical qualifiers."""
import copy
import csv
import hashlib
import io
import json
import re
from collections import Counter
import load_current_depth_reference_inventory_v1 as base
import load_current_depth_reference_inventory_v8 as defaults
import load_current_depth_reference_inventory_v22 as prior

SCHEMA='osw.current-depth-tao-euc-observed-daily-lower-addendum.v1'
FACTS='research/tao-pacific-euc-observed-lower-depth-reference-source-facts-v1.json'
CONTEXT='tao-pacific-euc-2005-observed-daily-u0p1-lower-depths'
OWNER='current:pacific-equatorial-undercurrent'
METRIC='derived_observed_daily_mean_component_lower_isotach_depth'
checked_piece=prior.checked_piece
reference_csv_bytes=prior.reference_csv_bytes
PIECES={'candidate_piece':'research/tao-pacific-euc-lower-threshold-reference-candidates-v1.json',
        'profile_piece':'research/source-data/tao-pacific-euc-direct-source-v2/profiles.json',
        'audit_piece':'research/tao-pacific-euc-retained-depth-audit-v1.json',
        'journal_piece':'research/source-data/tao-pacific-euc-direct-source-v2/journal.json',
        'source_review_piece':'research/current-depth-tao-pacific-euc-retained-depth-audit-source-review-v1.json',
        'all_case_csv_piece':'research/tao-pacific-euc-daily-depth-profiles-v1.csv',
        'all_case_geojson_piece':'research/tao-pacific-euc-daily-depth-points-v1.geojson'}


def read_facts(f,reader):
    result=copy.deepcopy(f);result['_bytes']={}
    for key,file in PIECES.items():
        if result[key]['file']!=file:raise ValueError('Exact independently reviewed source piece required')
        result['_bytes'][key]=checked_piece(result[key],reader)
    for key in ['candidate','profile','audit','journal','source_review']:
        result['_'+key]=json.loads(result['_bytes'][key+'_piece'])
    result['records']=copy.deepcopy(result['_candidate']['records'])
    validate_facts(result)
    return result


def validate_facts(f):
    if f['schema']!='osw.tao-pacific-euc-observed-lower-depth-reference-source-facts.v1' or f['entity_id']!=OWNER or f['metric']!=METRIC or f['source_dataset']!='pmelTaoDyAdcp':
        raise ValueError('One exact observed-field source and lower-threshold metric required')
    if f['source_url']!='https://coastwatch.pfeg.noaa.gov/erddap/info/pmelTaoDyAdcp/index.html':raise ValueError('Exact reviewed primary dataset required')
    fixed={'component_bearing_degrees_true':90,'primary_threshold_m_s':.1,'core_search_depth_interval_m':[50,250],
           'quality_flags_accepted':[1,2],'source_sampling':'original_rows_near10m_not_full_original5m_structure',
           'interpolation_assumption':'piecewise_linear_between_retained_rows_no_unobserved_reversals',
           'source_coordinate_role':'nominal_station_not_actual_deployment_or_current_axis',
           'source_temporal_operator':'provider_daily_mean_00UTC_to24UTC_label12UTC',
           'independent_threshold_contexts_verified':144,'all_source_profiles_retained':48,
           'admitted_finite_primary_lower_estimates':18,'new_raw_measurements':0,'new_ocean_field_requests':0}
    if any(f[k]!=v for k,v in fixed.items()):raise ValueError('No frame/threshold/QC/sampling/position/period/count substitution')
    for key in ['source_daily_underlying_sample_coverage_verified','source_mean_field_depth_is_mean_instantaneous_depth',
                'physical_current_bottom_established','physical_thickness_or_volume_promoted','runtime_changed','full_goal_complete']:
        if f[key] is not False:raise ValueError('No physical or temporal coverage promotion')
    for key,file in PIECES.items():
        raw=f['_bytes'][key]
        if f[key]['file']!=file or len(raw)!=f[key]['bytes'] or hashlib.sha256(raw).hexdigest()!=f[key]['sha256']:
            raise ValueError('Exact reviewed piece bytes must remain bound')
    for key in ['candidate','profile','audit','journal','source_review']:
        if f['_'+key]!=json.loads(f['_bytes'][key+'_piece']):raise ValueError('Structured source cannot diverge from its retained bytes')
    if f['records']!=f['_candidate']['records'] or f['_candidate']['reference_inventory_admission_performed'] is not False:
        raise ValueError('Immutable candidate-stage records required')
    audit=f['_audit'];review=f['_source_review'];profiles=f['_profile']['profiles'];journal=f['_journal']
    if audit['status']!='PASS_EXACT_RECONSTRUCTION_AND_INDEPENDENT_BOUNDARY_CHECKS' or audit['source_profile_count']!=48 or audit['finite_primary_lower_threshold_depths']!=18 or audit['finite_primary_threshold_layer_spans']!=15 or audit['independent_threshold_contexts_verified']!=144 or audit['provider_requests']!=0:
        raise ValueError('All48outcomes and144independent checks required')
    if review['source_run']!=41975675102 or review['tests_passed']!=5 or len(profiles)!=48 or len(journal['requests'])!=18:
        raise ValueError('Exact successful cloud audit and original aggregate custody required')
    for key in PIECES:
        if key!='source_review_piece' and review['input_sha256'].get(f[key]['file'])!=f[key]['sha256']:
            raise ValueError('Every candidate/profile/audit/all-case piece must match independent source review')
    receipts={r['raw_file']:r for r in journal['requests'][2:]}
    expected_indices={i for i,p in enumerate(profiles) if p['primary_lower_isotach_depth_m'] is not None}
    admitted=set();ids=set()
    for r in f['records']:
        match=re.fullmatch(r'/profiles/(0|[1-9][0-9]*)',r['source_profile_pointer'])
        if not match:raise ValueError('Exact source profile pointer required')
        index=int(match[1])
        if index not in expected_indices or index in admitted or r['id'] in ids:raise ValueError('Every eligible source profile admitted exactly once')
        p=profiles[index];primary=p['threshold_contexts'][1];station=p['nominal_station']
        if r['entity_id']!=OWNER or r['metric']!=METRIC or r['unit']!='m' or r['source_profile_file']!=PIECES['profile_piece'] or r['approximate_value_m']!=p['primary_lower_isotach_depth_m']:
            raise ValueError('Exact source lower depth and metric required')
        if r['source_station']!=station or station['latitude']!=0 or station['longitude'] not in [165,190,220,250] or r['source_daily_average_date']!=p['time_center_utc'][:10]:
            raise ValueError('No date/station/nominal location substitution')
        if r['component_bearing_degrees_true']!=90 or r['threshold_m_s']!=.1 or primary['threshold_m_s']!=.1 or not p['primary_core_window_interior'] or primary['lower_status']!='adjacent_isotach_crossing':
            raise ValueError('Original interior core and primary finite lower contour required')
        if r['source_lower_interpolation_bracket_m']!=primary['lower_bracket_m'] or r['source_upper_threshold_depth_m']!=primary['upper_depth_m'] or r['source_threshold_layer_span_m']!=p['primary_threshold_layer_span_m']:
            raise ValueError('Source proxy boundaries/span and resolution bracket required')
        if r['source_sampling']!=f['source_sampling'] or r['interpolation_assumption']!=f['interpolation_assumption']:
            raise ValueError('Original retained-sample interpolation assumption required')
        prefix='research/source-data/tao-pacific-euc-direct-source-v2/'
        if not r['source_raw_file'].startswith(prefix):raise ValueError('Original source response path required')
        receipt=receipts.get(r['source_raw_file'][len(prefix):])
        if receipt is None or receipt['sha256']!=r['source_raw_sha256'] or receipt['status']!='received_archived_before_derivation' or receipt['derivation_status']!='parsed_and_diagnosed':
            raise ValueError('Exact successful raw response custody required')
        for key in ['thickness_m','uncertainty_m','annual_range_m','volume_m3']:
            if r[key] is not None:raise ValueError('No physical thickness/range/uncertainty/volume substitution')
        for key in ['physical_current_bottom_established','independent_observation_count_claimed','reference_route_projection_eligible','volume_eligible','seasonal_playback_eligible']:
            if r[key] is not False:raise ValueError('No physical/spatial/seasonal promotion')
        admitted.add(index);ids.add(r['id'])
    if admitted!=expected_indices or len(admitted)!=18:raise ValueError('All and only eighteen verified finite lower values required')


def context_id(owner):
    if owner!=OWNER:raise ValueError('One exact named-current geographic context required')
    return CONTEXT


def source_context(f,owner):
    context_id(owner)
    keys=[k for k in f if not k.startswith('_') and k!='records']
    return {**{k:copy.deepcopy(f[k]) for k in keys},'reference_admission_policy':'finite_verified_lower_threshold_only_all48outcomes_remain_linked'}


def reference(f,r,index,piece):
    p=f['_profile']['profiles'][int(r['source_profile_pointer'].split('/')[-1])]
    rawname=r['source_raw_file'].split('/')[-1]
    receipt=next(v for v in f['_journal']['requests'][2:] if v['raw_file']==rawname)
    row={k:None for k in defaults.NULL_FIELDS};row.update({k:False for k in defaults.FALSE_FIELDS})
    date=r['source_daily_average_date'];station=r['source_station'];lon=station['longitude']
    row.update(id=r['id'],entity_id=OWNER,metric=METRIC,unit='m',approximate_value_m=r['approximate_value_m'],
        vertical_datum=r['vertical_datum'],phase_label=date+' provider_daily_mean',
        geographic_scope='Pacific equator; nominal mooring'+station['station']+'. Nominal coordinates only; actual deployment and current axis unresolved.',
        temporal_scope='Provider daily00-24UTC average, labelled12UTC on'+date+'; underlying numeric sample coverage unverified. Not a noon snapshot, seasonal mean or annual range.',
        source_definition='Lower eastward0.1m/s crossing connected to the original50-250m selected core in the provider daily-mean observed field; piecewise-linear between retained original rows near10m spacing.',
        evidence_kind='independently_audited_observed_daily_ADCP_component_lower_threshold_depth',
        source_url=f['source_url'],source_data_url=receipt['url'],source_citation=f['source_citation'],
        source_locator=r['source_profile_file']+'#'+r['source_profile_pointer'],
        qualification='Derived daily-mean-field velocity proxy. Not independently validated physical current bottom, actual axis, full original5m structure, complete within-day coverage, depth uncertainty or physical thickness. Correlated daily observations; no inter-station/date interpolation or volume eligibility.',
        source_context_id=CONTEXT,source_file=f['candidate_piece']['file'],source_sha256=f['candidate_piece']['sha256'],source_pointer='/records/'+str(index),
        source_facts_file=piece['file'],source_facts_sha256=piece['sha256'],source_facts_pointer='/candidate_piece',
        source_audit_record=copy.deepcopy(r),source_station=copy.deepcopy(station),source_nominal_lon_lat=[lon if lon<=180 else lon-360,0],
        source_sampled_lon_lat=None,source_position_role=f['source_coordinate_role'],
        source_daily_average_interval_utc=copy.deepcopy(p['provider_averaging_interval_utc']),source_time_label_utc=p['time_center_utc'],
        source_snapshot_time_utc=None,source_statistic='lower_contour_of_provider_daily_mean_eastward_velocity_component',
        source_component_bearing_degrees_true=90,source_primary_threshold_m_s=.1,source_quality_flags_accepted=[1,2],
        source_core_search_depth_interval_m=[50,250],source_sampling=f['source_sampling'],source_interpolation_assumption=f['interpolation_assumption'],
        source_lower_interpolation_bracket_m=copy.deepcopy(r['source_lower_interpolation_bracket_m']),
        source_upper_threshold_depth_m=r['source_upper_threshold_depth_m'],source_threshold_layer_span_m=r['source_threshold_layer_span_m'],
        source_raw_file=r['source_raw_file'],source_raw_sha256=r['source_raw_sha256'],
        source_profile_file=r['source_profile_file'],source_profile_pointer=r['source_profile_pointer'],
        source_daily_underlying_sample_coverage_verified=False,source_mean_field_depth_is_mean_instantaneous_depth=False,
        direct_velocity_profile_observation=True,direct_current_depth_measurement=False,physical_depth_ranking_eligible=False,
        current_identity_independently_verified=False,source_all_original_adcp_bins_retained=False,
        source_all48_case_outcomes_csv=copy.deepcopy(f['all_case_csv_piece']),source_all48_nominal_points_geojson=copy.deepcopy(f['all_case_geojson_piece']))
    return row


def assemble(*parts):
    result=prior.assemble(*parts[:-1]);seen={r['id'] for r in result['evidence']}
    for a,f in parts[-1]:
        validate_facts(f);expected=[reference(f,r,i,a['reviewed_source_facts']) for i,r in enumerate(f['records'])]
        contexts={CONTEXT:source_context(f,OWNER)}
        if a['evidence']!=expected or a['source_contexts']!=contexts or CONTEXT in result['source_contexts'] or any(r['id'] in seen for r in expected):
            raise ValueError('Exact source rows/context and unique reference identities required')
        seen.update(r['id'] for r in expected);result['evidence'].extend(copy.deepcopy(expected));result['source_contexts'].update(copy.deepcopy(contexts))
    for r in result['records']:r['depth_reference_ids']=[e['id'] for e in result['evidence'] if e['entity_id']==r['entity_id']]
    result['counts']=base.counts_for(result['records'],result['evidence'])
    result['metric_counts']=dict(sorted(Counter(r['metric'] for r in result['evidence']).items()))
    result['coordinate_unit_counts']=dict(sorted(Counter(r['unit'] for r in result['evidence']).items()))
    return result


def read_parts(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v23':raise ValueError('Reference inventoryv23 required')
    old=[];new=[];seen=set()
    for part in manifest['addenda']:
        if part['id'] in seen:raise ValueError('Duplicate addendum identity')
        seen.add(part['id']);a=json.loads(checked_piece(part['json'],reader))
        if a['schema']!=SCHEMA:
            if new:raise ValueError('Prior source classes must precede observed daily lower source')
            old.append(part);continue
        if a['id']!=part['id'] or a['base_snapshot_sha256']!=manifest['base']['json']['sha256'] or a['runtime_changed'] or a['full_goal_complete'] or a['reviewed_source_facts']['file']!=FACTS:
            raise ValueError('Exact base/source and no completion/runtime promotion required')
        facts=read_facts(json.loads(checked_piece(a['reviewed_source_facts'],reader)),reader)
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));rows=list(incoming);fields=list(incoming.fieldnames)
        if len(rows)!=len(a['evidence']) or set(fields)!={k for r in a['evidence'] for k in r} or any(row!={k:base.cell(raw.get(k)) for k in fields} for raw,row in zip(a['evidence'],rows)):
            raise ValueError('Every typed JSON/CSV cell must match exactly')
        new.append((a,facts))
    if len(new)!=1:raise ValueError('Exactly one observed daily lower addendum required')
    return (*prior.read_parts({'schema':'osw.current-depth-reference-inventory.v22','base':manifest['base'],'addenda':old},reader),new)


def load_inventory(manifest,reader):
    result=assemble(*read_parts(manifest,reader))
    if any(result[k]!=manifest[k] for k in ['counts','metric_counts','coordinate_unit_counts']):raise ValueError('Every reference count must reproduce')
    allowed={'schema','status','generator_file','generator_sha256','interpretation','runtime_changed','query_ui_integration_performed','full_goal_complete'}
    if not set(manifest['view_metadata'])<=allowed or any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):
        raise ValueError('No runtime/completion promotion')
    result.update(copy.deepcopy(manifest['view_metadata']));result['inventory_base_file']=manifest['base']['json']['file']
    result['inventory_addendum_files']=[p['json']['file'] for p in manifest['addenda']]
    result['member_depth_index_scope']='base_only_not_updated_for_addenda'
    return result


def combined_csv_bytes(manifest,reader):
    load_inventory(manifest,reader)
    first=csv.DictReader(io.StringIO(checked_piece(manifest['base']['csv'],reader).decode()));columns=list(first.fieldnames);rows=list(first)
    for part in manifest['addenda']:
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));columns.extend(k for k in incoming.fieldnames if k not in columns);rows.extend(list(incoming))
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows)
    return out.getvalue().encode()
