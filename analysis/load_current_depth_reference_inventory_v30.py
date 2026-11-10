"""Add conditional native-U/V cast references to the corrected v29 catalog."""
import copy,csv,io,json,math
from collections import Counter
import current_depth_cast_time_view_v29 as previous
import load_current_depth_reference_inventory_v1 as base
import load_current_depth_reference_inventory_v8 as defaults

SOURCE='research/i06s-agulhas-native-frame-depths-v2.json'
SOURCE_SHA='160260d77a701fb1e987f553c83185a9cd578dd22aa498016580bf32875633df'
CONTEXT='agulhas-i06s-2019-native-uv-local-cutoffs'
METRIC='derived_native_uv_fixed_frame_component_isotach_depth'
SCHEMA='osw.current-depth-i06s-native-uv-addendum.v1'
FALSE_GATES=['exact_solver_equivalence_verified','source_final_QC_verified','current_axis_verified',
    'global_first_crossing_verified','physical_current_bottom_established',
    'whole_route_physical_depth_profile_established','runtime_changed','full_goal_complete']
checked_piece=base.checked_piece
reference_csv_bytes=base.reference_csv_bytes

def finite(v):return type(v) in (int,float) and math.isfinite(v)

def references(source):
    if source['schema']!='osw.i06s-native-frame-depths.v2' or any(source[k] is not False for k in FALSE_GATES):
        raise ValueError('Conditional frozen source, never verified physical bottom or axis')
    profiles=source['profiles']
    if [p['station'] for p in profiles]!=['046','047','048'] or source['counts']['source_cast_profiles']!=3:
        raise ValueError('Exactly three original source casts')
    rows=[]
    for i,p in enumerate(profiles):
        if p['entity_context']!='current:agulhas' or not p['cast_datetime_utc'].startswith('2019-05-09T'):
            raise ValueError('Regional owner and original cast date required')
        if p['source_processing_software']!='LDEO LADCP software: Version IX_14beta2' or p['exact_solver_equivalence_verified'] is not False or p['independent_geographic_component_orientation_verified'] is not False:
            raise ValueError('Preserve declared beta version and orientation qualification')
        if p['volume_eligible'] is not False or p['physical_state_join_eligible'] is not False or p['physical_thickness_m'] is not None or p['seasonal_range_m'] is not None:
            raise ValueError('No geometric, seasonal or physical promotion')
        if not 1<=p['selected_native_levels']<=40 or p['current_membership_basis']!='regional_Agulhas_candidate_not_independently_validated_current_axis':
            raise ValueError('Original bounded selection and provisional current membership')
        if p['source_file']!='research/source-data/i06s-agulhas-native-casts-v1/'+p['station']+'.nc' or len(p['source_sha256'])!=64:
            raise ValueError('Native byte provenance required')
        frame=p['native_component_frame'];direction=frame['native_uv_unit_vector']
        if not frame['qualified'] or frame['independent_geographic_direction_or_current_axis_verified'] is not False or len(direction)!=2 or not all(finite(v) for v in direction) or not math.isclose(math.hypot(*direction),1.,abs_tol=1e-12):
            raise ValueError('Qualified native basis frame, not independently verified east/north')
        if [c['threshold_m_s'] for c in p['threshold_cases']]!=[.05,.1,.2]:raise ValueError('Exact three-cutoff source matrix')
        for j,c in enumerate(p['threshold_cases']):
            lo,hi=c['lower_depth_native_bracket_m'];a,b=c['refined_bracket_indices'];ca,cb=c['coarse_bracket_indices']
            value=c['lower_depth_m']
            if c['status']!='ADJACENT_NATIVE_CROSSING_WITHIN_FIRST_COARSE_DESCENDING_BRACKET' or not all(finite(v) for v in [lo,hi,value]) or not 0<=lo<=value<=hi or not lo<hi or b-a!=1 or not ca<=a<b<=cb:
                raise ValueError('Finite local adjacent bracket within coarse source candidate')
            for k in ['first_native_downcrossing_below_core_verified','continuous_connection_from_core_verified','physical_current_bottom_established','volume_eligible','local_crossing_is_first_crossing_of_entire_native_profile']:
                if c[k] is not False:raise ValueError('Local bracket cannot establish entire flow boundary')
            row={k:None for k in defaults.NULL_FIELDS};row.update({k:False for k in defaults.FALSE_FIELDS})
            row.update(id='agulhas-i06s-2019-cast-'+p['station']+'-native-uv-frame-'+str(int(round(100*c['threshold_m_s'])))+'cms',
                entity_id='current:agulhas',metric=METRIC,unit='m',approximate_value_m=10*round(value/10),
                source_computed_depth_before_display_rounding_m=value,
                vertical_datum='source_native_LADCP_depth_metres_exact_surface_datum_unverified',
                phase_label='observed_cast_'+p['cast_datetime_utc'],
                geographic_scope='Individual northern I06S2019cast'+p['station']+'; regional Agulhas candidate, current-axis membership unverified.',
                temporal_scope='Processed finite LADCP cast '+p['cast_datetime_utc']+'; nominal profile label, not a per-depth instant, climatology or seasonal range.',
                source_definition='Adjacent-native signed-component cutoff crossing inside the first descending coarse bracket; fixed nearest100m vector in provider-declared native U/V basis.',
                evidence_kind='conditional_derived_observed_LADCP_native_uv_local_crossing',
                source_url='https://currents.soest.hawaii.edu/go-ship/ladcp/downloads/2019_I06S/'+p['station']+'.nc',
                source_citation='US GO-SHIP I06S2019,TN366; provider-processed LDEO IX_14beta2 cast. Final source QC and exact solver equivalence unverified.',
                source_locator=p['source_file']+' plus '+SOURCE+'#/profiles/'+str(i)+'/threshold_cases/'+str(j),
                qualification='Conditional archived-field proxy. Coarse skipping can hide earlier reversals. Native bracket is sampling support, not uncertainty or accuracy. Cast046 terminal-edge proximity and cast047 tilt warning remain relevant. No physical-bottom, thickness, seasonal, route/state or volume claim.',
                source_context_id=CONTEXT,source_file=SOURCE,source_sha256=SOURCE_SHA,
                source_pointer='/profiles/'+str(i)+'/threshold_cases/'+str(j),
                source_metric_file=SOURCE,source_metric_sha256=SOURCE_SHA,
                source_metric_pointer='/profiles/'+str(i)+'/threshold_cases/'+str(j),
                source_cast_profile_id='i06s-2019-cast-'+p['station'],source_cast_datetime_utc=p['cast_datetime_utc'],
                source_sampled_lon_lat=copy.deepcopy(p['source_lon_lat']),source_velocity_threshold_m_s=c['threshold_m_s'],
                source_native_bracketing_depths_m=copy.deepcopy(c['lower_depth_native_bracket_m']),
                source_refined_native_indices=copy.deepcopy(c['refined_bracket_indices']),
                source_original_coarse_bracket_indices=copy.deepcopy(c['coarse_bracket_indices']),
                source_fixed_native_uv_frame=copy.deepcopy(frame),source_native_file=p['source_file'],
                source_native_sha256=p['source_sha256'],source_processing_software=p['source_processing_software'],
                source_processing_warnings=p['source_processing_warnings'],source_QC_status=p['source_QC_status'],
                source_current_membership_basis=p['current_membership_basis'],
                source_uncertainty_semantics='provider_velocity_diagnostic_not_SE_or_depth_CI',
                source_timestamp_role=p['source_timestamp_role'],metric_frame_is_cast_specific_not_climatology=True,
                source_frame_is_mathematical_instant=False,source_actual_cast_duration_resolved=False,
                global_first_native_crossing_verified=False,continuous_core_connection_verified=False,
                source_bracket_is_uncertainty_interval=False,depth_confidence_interval_m=None,
                exact_solver_equivalence_verified=False,source_final_QC_verified=False,
                independent_geographic_component_orientation_verified=False,
                direct_physical_current_depth_measurement=False,physical_depth_ranking_eligible=False,
                source_upper_to_lower_pair_is_physical_thickness=False)
            rows.append(row)
    return rows

def context():
    return {'source_file':SOURCE,'source_sha256':SOURCE_SHA,'metric':METRIC,'source_cast_profiles':3,
        'threshold_contexts':9,'independent_observation_count_claimed':False,
        'native_uv_basis_is_independently_verified_geographic_orientation':False,
        'exact_solver_equivalence_verified':False,'source_final_QC_verified':False,
        'physical_current_bottom_established':False,'volume_eligible':False}

def assemble(before,addendum,source):
    expected=references(source)
    if addendum['schema']!=SCHEMA or addendum['id']!='i06s-agulhas-native-uv-depths-v1' or addendum['evidence']!=expected or addendum['source_contexts']!={CONTEXT:context()}:
        raise ValueError('Exact conditional references and context, no promotion or warning loss')
    out=copy.deepcopy(before);old={r['id'] for r in out['evidence']}
    if CONTEXT in out['source_contexts'] or any(r['id'] in old for r in expected):raise ValueError('No duplicate references/context')
    if 'current:agulhas' not in {r['entity_id'] for r in out['records']}:raise ValueError('Existing current owner required')
    out['evidence'].extend(copy.deepcopy(expected));out['source_contexts'][CONTEXT]=context()
    for r in out['records']:r['depth_reference_ids']=[e['id'] for e in out['evidence'] if e['entity_id']==r['entity_id']]
    out['counts']=base.counts_for(out['records'],out['evidence'])
    out['metric_counts']=dict(sorted(Counter(r['metric'] for r in out['evidence']).items()))
    out['coordinate_unit_counts']=dict(sorted(Counter(r['unit'] for r in out['evidence']).items()))
    return out

def load_inventory(manifest,reader):
    if manifest['schema']!='osw.current-depth-reference-inventory.v30':raise ValueError('Inventoryv30 required')
    before=previous.load_inventory(json.loads(checked_piece(manifest['previous_inventory'],reader)),reader)
    part=manifest['reference_addendum'];addendum=json.loads(checked_piece(part['json'],reader))
    if addendum['source_result']['file']!=SOURCE or addendum['source_result']['sha256']!=SOURCE_SHA:raise ValueError('Frozen diagnostic source required')
    source=json.loads(checked_piece(addendum['source_result'],reader));out=assemble(before,addendum,source)
    incoming=csv.DictReader(io.StringIO(checked_piece(part['csv'],reader).decode('utf8')));rows=list(incoming);fields=list(incoming.fieldnames)
    if len(rows)!=9 or set(fields)!={k for r in addendum['evidence'] for k in r} or any(row!={k:base.cell(raw.get(k)) for k in fields} for raw,row in zip(addendum['evidence'],rows)):
        raise ValueError('All typed JSON/CSV fields and values must agree')
    for k in ['counts','metric_counts','coordinate_unit_counts']:
        if out[k]!=manifest[k]:raise ValueError('Every catalog count must reproduce')
    if any(manifest['view_metadata'].get(k,False) is not False for k in ['runtime_changed','query_ui_integration_performed','full_goal_complete']):raise ValueError('No runtime/completion promotion')
    out.update(copy.deepcopy(manifest['view_metadata']));return out
