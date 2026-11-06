"""Qualified local observed component-depth proxies; no physical-bottom promotion."""
import copy,csv,io,json,math
from collections import Counter
import load_current_depth_reference_inventory_v27 as prior
import load_current_depth_reference_inventory_v1 as base
import load_current_depth_reference_inventory_v8 as defaults

SCHEMA='osw.current-depth-a20-local-component-addendum.v1'
FACTS='research/a20-local-component-depth-reference-facts-v1.json'
CONTEXT='gulf-stream-a20-2021-local-fixed96m-direction-cutoffs'
METRIC='derived_local_fixed_reference_direction_component_isotach_depth'
SOURCE='research/a20-gulf-stream-core-direction-depths-v2.json'
SOURCE_SHA='34a5f48c859d5ad272bc6c39a28ff60609ec7d6e754c0b9c9bd5e753516b21cd'
checked_piece=prior.checked_piece
reference_csv_bytes=prior.reference_csv_bytes
FALSE_GATES=['global_first_native_crossing_verified','continuous_core_connection_verified',
             'physical_current_bottom_established','seasonal_extrema_established','volume_eligible',
             'independent_axis_verified','native_bracket_is_uncertainty_interval','runtime_changed','full_goal_complete']


def finite(v):return type(v) in (int,float) and math.isfinite(v)


def validate_facts(f):
    if f['schema']!='osw.a20-local-component-depth-reference-facts.v1' or f['source_file']!=SOURCE or f['source_sha256']!=SOURCE_SHA:
        raise ValueError('Exact frozen observed scalar source required')
    if any(f[k] is not False for k in FALSE_GATES) or f['source_cast_profiles']!=3 or f['independent_observation_count_claimed']:
        raise ValueError('Three casts, not nine independent observations or physical bottoms')
    if f['metric']!=METRIC or len(f['records'])!=9 or f['source_uncertainty_semantics']!='provider_velocity_uncertainty_estimate_not_SE_or_depth_CI':
        raise ValueError('Nine distinct local signed-component definitions required')
    seen=set()
    for r in f['records']:
        key=(r['station'],r['threshold_m_s'])
        if key in seen or key[0] not in ['014','015','016'] or key[1] not in [.05,.1,.2] or r['entity_id']!='current:gulf-stream':
            raise ValueError('Fixed owner and full distinct3by3matrix')
        seen.add(key)
        lo,hi=r['native_depth_bracket_m'];a,b=r['refined_native_indices'];ca,cb=r['original_coarse_bracket_indices']
        if not all(finite(v) for v in [lo,hi,r['computed_depth_m']]) or not 0<=lo<=r['computed_depth_m']<=hi or not lo<hi or type(a)!=int or type(b)!=int or b-a!=1 or not ca<=a<b<=cb:
            raise ValueError('Local adjacent-native bracket inside original coarse candidate required')
        frame=r['fixed_reference_frame']
        if not frame['qualified'] or frame['reference_depth_m']!=96 or frame['reference_direction_is_independently_validated_current_axis']:
            raise ValueError('Original fixed96m reference, not a validated axis')
        if len(frame['east_north_unit_vector'])!=2 or not all(finite(v) for v in frame['east_north_unit_vector']):
            raise ValueError('Original finite signed projection frame required')
        if not r['cast_datetime_utc'].startswith('2021-03-23' if r['station'] in ['014','015'] else '2021-03-24') or r['source_case_pointer']!='/profiles/'+str(['014','015','016'].index(r['station']))+'/threshold_cases/'+str([.05,.1,.2].index(r['threshold_m_s'])):
            raise ValueError('Actual cast date and exact source case pointer, not seasonal phase')
        if r['raw_native_file']!='research/source-data/a20-gulf-stream-native-casts-v1/'+r['station']+'.nc' or len(r['raw_native_sha256'])!=64:
            raise ValueError('Original instrument byte provenance required')
        if r['current_membership_basis']!='primary_cruise_QC_stations14_to21_candidate_not_independent_axis_validation':
            raise ValueError('Do not silently upgrade current identity')
    if len(seen)!=9:raise ValueError('Complete fixed cutoff matrix required')


def references(f,piece):
    validate_facts(f);rows=[]
    for i,r in enumerate(f['records']):
        row={k:None for k in defaults.NULL_FIELDS};row.update({k:False for k in defaults.FALSE_FIELDS})
        row.update(id='gulf-stream-a20-2021-cast-'+r['station']+'-local-frame-'+str(int(round(100*r['threshold_m_s'])))+'cms',
            entity_id='current:gulf-stream',metric=METRIC,unit='m',approximate_value_m=10*round(r['computed_depth_m']/10),
            source_computed_depth_before_display_rounding_m=r['computed_depth_m'],
            vertical_datum='source_native_LADCP_depth_metres_exact_surface_datum_unverified',
            phase_label='observed_cast_'+r['cast_datetime_utc'],geographic_scope='IndividualA20GulfStreamcrossing cast'+r['station']+'; primary-QC candidate current membership, no independently validated axis.',
            temporal_scope='Single cast '+r['cast_datetime_utc']+'; not mean,seasonal phase or annual range.',
            source_definition='Adjacent-native signed-component cutoff crossing located inside the first descending coarse bracket, using direction fixed at the native96m reference. Global-first crossing and continuous core connection unverified.',
            evidence_kind='derived_observed_LADCP_local_component_crossing',
            source_url='https://currents.soest.hawaii.edu/go-ship/ladcp/downloads/2021_A20/'+r['station']+'.nc',
            source_citation='US GO-SHIP A20(2021),LADCP processed by A.M.Thurnherr,LDEO IX14; primary2022-03-04post-cruiseQC report.',
            source_locator=r['raw_native_file']+' plus '+SOURCE+'#'+r['source_case_pointer'],
            qualification='Sparse coarse scan can miss earlier reversals/gaps. Native endpoint bracket is sampling support,not uncertainty. This local proxy is not a physical current bottom,whole-route thickness,seasonal extreme or volume.',
            source_context_id=CONTEXT,source_file=piece['file'],source_sha256=piece['sha256'],source_pointer='/records/'+str(i),
            source_metric_file=SOURCE,source_metric_sha256=SOURCE_SHA,source_metric_pointer=r['source_case_pointer'],
            source_cast_profile_id='a20-2021-cast-'+r['station'],source_cast_datetime_utc=r['cast_datetime_utc'],
            source_sampled_lon_lat=copy.deepcopy(r['source_lon_lat']),
            source_velocity_threshold_m_s=r['threshold_m_s'],source_native_bracketing_depths_m=copy.deepcopy(r['native_depth_bracket_m']),
            source_refined_native_indices=copy.deepcopy(r['refined_native_indices']),source_original_coarse_bracket_indices=copy.deepcopy(r['original_coarse_bracket_indices']),
            source_fixed_reference_frame=copy.deepcopy(r['fixed_reference_frame']),
            source_native_file=r['raw_native_file'],source_native_sha256=r['raw_native_sha256'],
            source_current_membership_basis=r['current_membership_basis'],
            source_uncertainty_semantics=f['source_uncertainty_semantics'],
            global_first_native_crossing_verified=False,continuous_core_connection_verified=False,
            source_bracket_is_uncertainty_interval=False,depth_confidence_interval_m=None,
            direct_physical_current_depth_measurement=False,physical_depth_ranking_eligible=False,
            fitted_mean_direction_metric_equivalent=False,metric_frame_is_instantaneous_sample_not_climatology=True,
            source_upper_to_lower_pair_is_physical_thickness=False)
        rows.append(row)
    return rows


def validate_addendum(a,f):
    expected=references(f,a['reviewed_source_facts'])
    if a['evidence']!=expected or a['source_contexts']!={CONTEXT:f}:
        raise ValueError('Exact native local proxy references and no promotions')
    return expected


def assemble(*parts):
    result=prior.assemble(*parts[:-1])
    if len(parts[-1])!=1:raise ValueError('Exactly one local-component source addendum')
    a,f=parts[-1][0];expected=validate_addendum(a,f)
    if CONTEXT in result['source_contexts']:raise ValueError('Duplicate local source context')
    old={r['id'] for r in result['evidence']}
    if len({r['id'] for r in expected})!=9 or any(r['id'] in old for r in expected):raise ValueError('No duplicate cast/cutoff reference')
    result['evidence'].extend(copy.deepcopy(expected));result['source_contexts'][CONTEXT]=copy.deepcopy(f)
    for r in result['records']:r['depth_reference_ids']=[e['id'] for e in result['evidence'] if e['entity_id']==r['entity_id']]
    result['counts']=base.counts_for(result['records'],result['evidence'])
    result['metric_counts']=dict(sorted(Counter(r['metric'] for r in result['evidence']).items()))
    result['coordinate_unit_counts']=dict(sorted(Counter(r['unit'] for r in result['evidence']).items()))
    return result


def read_parts(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v28':raise ValueError('Inventoryv28 required')
    old=[];new=[];seen=set()
    for part in manifest['addenda']:
        if part['id'] in seen:raise ValueError('Duplicate addendum')
        seen.add(part['id']);a=json.loads(checked_piece(part['json'],reader))
        if a['schema']!=SCHEMA:
            if new:raise ValueError('Previous source classes precede new class')
            old.append(part);continue
        if a['id']!=part['id'] or a['base_snapshot_sha256']!=manifest['base']['json']['sha256'] or a['runtime_changed'] or a['full_goal_complete'] or a['reviewed_source_facts']['file']!=FACTS:
            raise ValueError('Exact base/source and no runtime promotion')
        facts=json.loads(checked_piece(a['reviewed_source_facts'],reader))
        incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode()));rows=list(incoming);fields=list(incoming.fieldnames)
        if len(rows)!=9 or set(fields)!={k for r in a['evidence'] for k in r} or any(row!={k:base.cell(raw.get(k)) for k in fields} for raw,row in zip(a['evidence'],rows)):
            raise ValueError('Typed JSON/CSV cell disagreement')
        new.append((a,facts))
    if len(new)!=1:raise ValueError('Exactly one new source addendum')
    return (*prior.read_parts({'schema':'osw.current-depth-reference-inventory.v27','base':manifest['base'],'addenda':old},reader),new)


def load_inventory(manifest,reader):
    result=assemble(*read_parts(manifest,reader))
    for k in ['counts','metric_counts','coordinate_unit_counts']:
        if result[k]!=manifest[k]:raise ValueError('Every inventory count must reproduce')
    if any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):
        raise ValueError('No runtime/completion promotion')
    result.update(copy.deepcopy(manifest['view_metadata']))
    result['inventory_base_file']=manifest['base']['json']['file'];result['inventory_addendum_files']=[p['json']['file'] for p in manifest['addenda']]
    result['member_depth_index_scope']='base_only_not_updated_for_addenda'
    return result
