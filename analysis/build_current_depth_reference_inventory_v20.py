"""Admit linked core/reach references from audited native-source REDSOX depth reports."""
import copy,hashlib,json
from pathlib import Path
import load_current_depth_reference_inventory_v19 as prior
import load_current_depth_reference_inventory_v20 as loader

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-reference-inventory-operator-v20.json'
GENERATOR='analysis/build_current_depth_reference_inventory_v20.py'
INVENTORY='research/current-depth-reference-inventory-v20.json'
ADDENDUM='research/current-depth-reference-addenda/redsox-rsx1-observed-core-and-censored-reach-v1.json'
CSV='research/current-depth-reference-addenda/redsox-rsx1-observed-core-and-censored-reach-v1.csv'
SOURCE_REVIEW='research/current-depth-redsox-observed-depth-sections-source-review-v2.json'


def sha(raw):return hashlib.sha256(raw).hexdigest()
def encode(v):return (json.dumps(v,separators=(',',':'),allow_nan=False)+'\n').encode()


def admit_case(case,file,file_sha,index):
    if case['entity_id']!=loader.OWNER or case['campaign']!='RSX1' or case['exclusion_reasons'] or case['provider_station_assessment']['status']!='consistent_provider_station_records':raise ValueError('Original unexcluded provider-consistent winter source case required')
    d=case['joint_diagnosis'];g=case['fine_source_union_grid']
    if d is None or d['status']!='conditional_saline_component_core_supported' or g is None or case['frozen_velocity_core_and_point_salinity_reproduced_exactly'] is not True or d['core_reselected'] is not False:raise ValueError('Audited unchanged velocity core with complete fine-source diagnostic required')
    source_core=case['core_index'];seed=g['seed_union_index'];last=len(g['depth_m'])-1
    if d['source_velocity_core_index']!=source_core or g['source_velocity_core_index']!=source_core or d['seed_union_index']!=seed or g['depth_m'][seed]!=case['core_depth_m'] or case['native_velocity_depth_m'][source_core]!=case['core_depth_m'] or g['component_m_s'][seed]!=case['core_component_m_s'] or g['salinity_psu'][seed]!=case['core_remapped_salinity_psu']:raise ValueError('Exact core depth, component and same-core salinity required')
    if case['selection_height_above_bottom_interval_m']!=[20,200] or not case['selection_interval_mean_component_m_s']>0 or not 20<=case['core_height_above_bottom_m']<=200 or d['velocity_threshold_m_s']!=.2 or d['practical_salinity_inclusive_lower_threshold']!=38:raise ValueError('Original positive interval selection and joint cutoffs required')
    if g['depth_m']!=sorted(set(case['native_velocity_depth_m'])|{z for z in case['native_hydrographic_depth_m'] if case['native_velocity_depth_m'][0]<=z<=case['native_velocity_depth_m'][-1]}) or d['all_native_hydrographic_knots_within_velocity_domain_retained'] is not True:raise ValueError('Every fine native hydrographic knot required')
    lower=d['lower']
    if lower['status']!='censored_at_native_velocity_sampling_end' or lower['boundary_depth_m'] is not None or lower['last_connected_union_index']!=last or lower['last_connected_depth_m']!=g['depth_m'][last] or g['depth_m'][last]!=case['native_velocity_depth_m'][-1]:raise ValueError('Deepest supported native sample remains a sampling censor, not physical bottom')
    if len(g['component_m_s'])!=len(g['depth_m']) or len(g['salinity_psu'])!=len(g['depth_m']) or len(g['velocity_segment_support'])!=last or len(g['salinity_segment_support'])!=last:raise ValueError('Complete fine-grid node and segment arrays required')
    if any(q is None or not q>.2 or s is None or not s>=38 for q,s in zip(g['component_m_s'][seed:],g['salinity_psu'][seed:])) or any(g[key][i]!='ok' for key in ['velocity_segment_support','salinity_segment_support'] for i in range(seed,last)):raise ValueError('Every node and BOTH source supports from frozen core to last sample must remain connected')
    for key in ['physical_cast_identity_independently_verified','sample_level_synchronization_verified','physical_current_bottom_established','annual_extrema_established','tidal_correction_applied']:
        if case[key] is not False:raise ValueError('No identity, synchronization, physical, annual or tidal promotion')
    if case['physical_layer_thickness_m'] is not None or case['volume_m3'] is not None or d['joint_support_span_m'] is not None:raise ValueError('Censored support does not establish thickness or volume')
    section=case['section_id'];station=case['station']
    return {'entity_id':loader.OWNER,'campaign':'RSX1','station':station,'section_id':section,'source_case_id':'redsox-rsx1-'+section+'-'+str(station),'source_report_file':file,'source_report_sha256':file_sha,'source_case_pointer':'/cases/'+str(index),'core_depth_m':case['core_depth_m'],'core_component_m_s':case['core_component_m_s'],'core_salinity_psu':case['core_remapped_salinity_psu'],'source_velocity_core_index':source_core,'source_depth_basis':'provider_reported_LADCP_zz_metres_not_independent_pressure_sensor','supported_penetration_lower_bound_m':lower['last_connected_depth_m'],'supported_penetration_lower_bound_exclusive':False,'support_start_depth_m':case['core_depth_m'],'surface_connection_established':False,'lower_status':lower['status'],'lower_boundary_depth_m':None,'upper_crossing_context':copy.deepcopy(d['upper']),'native_union_path_from_core_to_sampling_end_verified':True,'all_native_hydrographic_knots_retained':True,'position_lon_lat':copy.deepcopy(case['position_lon_lat']),'source_velocity_header_time_utc':case['source_velocity_time_utc'],'source_ctd_start_time_utc':case['source_ctd_start_time_utc'],'component_reference':case['component_reference'],'section_bearing_degrees_true':case['section_bearing_degrees_true'],'source_hydrographic_depth_operator':case['hydrographic_depth_operator'],'comparison_group':'redsox-rsx1-'+section+'-q0p2-s38-height20-200-native-union-v2','selection_height_above_bottom_interval_m':[20,200],'velocity_threshold_m_s':.2,'salinity_inclusive_lower_threshold_psu':38,'source_velocity_archive_member':case['source_velocity_file'],'source_velocity_archive_member_sha256':case['source_velocity_member_sha256'],'source_hydrography_archive_member':case['source_hydrography_file'],'source_hydrography_archive_member_sha256':case['source_hydrography_member_sha256'],'provider_station_assessment':copy.deepcopy(case['provider_station_assessment']),'physical_cast_identity_independently_verified':False,'sample_level_synchronization_verified':False,'source_reference_quality_independently_verified':False,'tidal_correction_applied':False,'independent_observation_count_claimed':False,'physical_current_bottom_established':False,'physical_layer_thickness_m':None,'uncertainty_m':None,'annual_range_m':None,'volume_m3':None,'paired_width_reference_id':None,'observed_period':None,'calendar_months':None,'volume_eligible':False,'annual_extrema_established':False,'reference_route_projection_eligible':False}


def facts_from_sources(root,op):
    read=lambda p:json.loads((root/p).read_bytes());review=read(SOURCE_REVIEW);records=[];pins={};all_cases=0
    if op['observed_source_review']!=SOURCE_REVIEW or review['tests_passed']!=35 or review['source_run']!=41952843629:raise ValueError('Exact validated fine-grid source review required')
    expected_files=['research/redsox-observed-depth-sections-'+name+'-v2.json' for name in ['lower-northern-channel','winter-section3']]
    if op['observed_reports']!=expected_files:raise ValueError('Both original section reports in source order required')
    for file in op['observed_reports']:
        raw=(root/file).read_bytes();report=json.loads(raw);pins[file]=sha(raw)
        if review['input_sha256'].get(file)!=pins[file] or report['schema']!='osw.redsox-observed-depth-sections.v2' or report['source_plan_case_count']!=17 or report['counts']['profile_cases']!=len(report['cases']):raise ValueError('Pinned source report and complete case counts required')
        all_cases+=len(report['cases'])
        for index,case in enumerate(report['cases']):
            if case['joint_diagnosis'] and case['joint_diagnosis']['status']=='conditional_saline_component_core_supported':records.append(admit_case(case,file,pins[file],index))
    if all_cases!=17 or [r['station'] for r in records]!=[8,9,73,62]:raise ValueError('Every original case reviewed and exactly four unchanged supported cores required')
    facts={'schema':'osw.redsox-observed-depth-reference-source-facts.v1','entity_id':loader.OWNER,'source_url':'https://www.ncei.noaa.gov/archive/accession/0146147','source_citation':'Peters, Bower and Johns (2017), REDSOX2001 CTD/SADCP/LADCP collection, NCEI Accession0146147 version1.2; OSW conditional native-source union-grid depth derivation v2.','source_review_file':SOURCE_REVIEW,'source_review_sha256':sha((root/SOURCE_REVIEW).read_bytes()),'source_review_tests_passed':35,'source_report_pins':pins,'original_selected_profile_cases':17,'source_profile_cases':4,'reference_rows':8,'records':records,'method_scope':'Two dated non-synoptic winter source sections. Greatest native signed component in positive20-200m-above-bed interval, q>.2/S>=38 at SAMEcore; complete fine-native-source support to deepest velocity sample. Component frames and profile clock roles remain distinct. Source-reported LADCPzz is not an independently sensed depth or physical current boundary.','qualifications':['Four original processed source profiles provide two linked metrics each, not eight independent observations or whole-current depths.','Each core depth and inclusive supported penetration bound shares a source_case_id, source report hash/pointer, position and distinct velocity-header/CTD-start timestamps. Neither timestamp supplies a verified common instantaneous cast time or survey mean.','Reach support begins at the unchanged core, not at surface0. Sampling-end censor remains unknown below last sample; no seabed closure, physical thickness, symmetric layer, paired width, area or volume.','Fine native hydrographic knots/source gaps checked; reconstructed velocity between native samples is not increased measurement resolution, uncertainty or an annual range.','Provider station association/reference/current identity/sample synchronization are not independently verified; original source exclusions, signs, q/S predicates and all limits remain.','Preserve all810priorrefs, native units and historical snapshots; no raw field requests or new independent raw observations.'],'new_ocean_field_requests':0,'new_raw_observations':0,'independent_observation_count_claimed':False,'physical_current_bottom_established':False,'runtime_changed':False,'full_goal_complete':False}
    loader.validate_facts(facts);return facts


def build(root=ROOT):
    reader=lambda f:(root/f).read_bytes();read=lambda f:json.loads(reader(f));op=read(OPERATOR)
    if any(op['eligibility'].values()):raise ValueError('No physical, annual, volume or runtime promotion')
    for file,pin in op['input_sha256'].items():
        if sha(reader(file))!=pin:raise ValueError('Frozen reference/source input changed: '+file)
    previous=read(op['previous_inventory_file']);before=prior.load_inventory(previous,reader);parts=prior.read_parts(previous,reader);facts=facts_from_sources(root,op);factraw=encode(facts);piece=lambda file,raw:{'file':file,'sha256':sha(raw),'bytes':len(raw)};source=piece(loader.FACTS,factraw)
    addendum={'schema':loader.SCHEMA,'id':'redsox-rsx1-observed-core-and-censored-reach-v1','base_snapshot_sha256':previous['base']['json']['sha256'],'operator_file':OPERATOR,'operator_sha256':sha(reader(OPERATOR)),'input_sha256':op['input_sha256'],'reviewed_source_facts':source,'source_contexts':{loader.CONTEXT:loader.source_context(facts,loader.OWNER)},'evidence':[loader.reference(facts,r,i,source,metric) for i,r in enumerate(facts['records']) for metric in loader.METRICS],'runtime_changed':False,'full_goal_complete':False}
    assembled=loader.assemble(*parts,[(addendum,facts)]);addraw=encode(addendum);csvraw=loader.reference_csv_bytes(addendum['evidence']);inventory=copy.deepcopy(previous);inventory.update(schema='osw.current-depth-reference-inventory.v20',status='PINNED_REFERENCES_WITH_CONDITIONAL_OBSERVED_REDSOX_CORES_AND_CENSORED_REACHES',counts=assembled['counts'],metric_counts=assembled['metric_counts'],coordinate_unit_counts=assembled['coordinate_unit_counts']);inventory['addenda'].append({'id':addendum['id'],'json':piece(ADDENDUM,addraw),'csv':piece(CSV,csvraw)});inventory['view_metadata'].update(schema='osw.current-depth-reference-view.v20',status=inventory['status'],generator_file=GENERATOR,generator_sha256=sha(reader(GENERATOR)),interpretation=op['interpretation']);pieces={INVENTORY:encode(inventory),ADDENDUM:addraw,CSV:csvraw,loader.FACTS:factraw}
    if any(len(raw)>=2500000 for raw in pieces.values()) or sum(map(len,pieces.values()))>=2400000:raise ValueError('Fixed file and scientific output caps exceeded')
    view=loader.load_inventory(inventory,lambda f:pieces[f] if f in pieces else reader(f))
    if view['evidence'][:len(before['evidence'])]!=before['evidence']:raise ValueError('Every prior evidence row unchanged required')
    return inventory,addendum,facts,pieces,view


if __name__=='__main__':
    inventory,addendum,facts,pieces,view=build();out=Path('current-depth-reference-inventory-v20');out.mkdir(exist_ok=True)
    for file,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv'),(loader.FACTS,'facts.json')]:(out/name).write_bytes(pieces[file])
    print(json.dumps({'counts':view['counts'],'native_units':view['coordinate_unit_counts'],'new_reference_rows':len(addendum['evidence']),'source_profile_cases':facts['source_profile_cases'],'independent_observation_count_claimed':False,'new_ocean_field_requests':0}),flush=True)
