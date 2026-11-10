"""Admit context-owned Malvinas/EACC native primary penetration bounds."""
import copy,hashlib,json
from pathlib import Path
import load_current_depth_reference_inventory_v3 as prior
from load_current_depth_reference_inventory_v4 import assemble,load_inventory,reference_csv_bytes
from derive_native_primary_penetration_bounds_v2 import audit_and_derive

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-reference-inventory-operator-v4.json'
GENERATOR='analysis/build_current_depth_reference_inventory_v4.py'
INVENTORY='research/current-depth-reference-inventory-v4.json'
ADDENDUM='research/current-depth-reference-addenda/malvinas-eacc-primary-censored-penetration-v1.json'
CSV='research/current-depth-reference-addenda/malvinas-eacc-primary-censored-penetration-v1.csv'
REPORT='research/malvinas-eacc-primary-censored-penetration-source-report-v1.json'


def context_id(entity):return entity.split(':')[1]+'-hycom2022-original-primary-censored-supported-reach'


def references(report,report_sha):
    refs=[]
    for i,r in enumerate(report['records']):
        if not r['reach_eligible']:continue
        domain=r['censoring_kind']=='native_vertical_domain_limit'
        refs.append({'id':r['entity_id'].split(':')[1]+'-hycom2022-'+r['snapshot_time_utc'][:10]+'-'+r['section_id']+'-primary-supported-reach-lower-bound','entity_id':r['entity_id'],'metric':'derived_supported_component_penetration_lower_bound','approximate_value_m':None,'range_m':None,'lower_bound_m':r['lower_bound_m'],'lower_bound_operator':'>=','lower_bound_exclusive':False,'upper_bound_m':None,'upper_bound_exclusive':False,'range_interpretation':None,'unit':'m','vertical_datum':'local_sea_surface_positive_down','upper_boundary_m':None,'lower_boundary_m':None,'thickness_m':None,'uncertainty_m':None,'annual_range_m':None,'phase_label':r['snapshot_time_utc']+' instantaneous model supported reach','calendar_months':None,'geographic_scope':r['branch_scope'],'temporal_scope':'Two retained January15/July15,2022T00Z instantaneous model snapshots; not monthly means or seasonal envelopes.','observed_period':None,'source_definition':'Deepest contiguous native level above the original selected primary signed-component threshold,connected to the sampled0-200m core and surface. The native vertical domain ends at that level.' if domain else 'Deepest contiguous native level above the original selected primary signed-component threshold,connected to the sampled0-200m core and surface; the next native signed component is missing.','evidence_kind':'derived_instantaneous_model_supported_penetration_lower_bound','source_url':'https://www.hycom.org/dataserver/gofs-3pt1/analysis','source_citation':'HYCOM Consortium/NRL/COAPS-FSU,GOFS3.1GLBy0.08expt93.0uv3z2022;retained original regional sections.','source_locator':'Exact original section/profile/primary-layer references and derived audit record retained on this row.','qualification':'Native model lower bound only; no independently validated current axis,detected lower contour,physical bottom,layer span or annual range. Missing-level and domain-limit censoring remain distinct. Original projection gaps are unchanged.','source_context_id':context_id(r['entity_id']),'source_statistic':'native_surface_connected_primary_component_supported_reach','source_snapshot_time_utc':r['snapshot_time_utc'],'source_section_id':r['section_id'],'source_raw_profile_ref':r['source_profile_ref'],'source_raw_section_sha256':r['source_section_sha256'],'source_connected_layer_ref':r['source_connected_layer_ref'],'source_sampled_lon_lat':r['sampled_lon_lat'],'source_selected_column_index':r['selected_column_index'],'source_horizontal_selection_status':r['horizontal_selection_status'],'source_primary_threshold_m_s':r['primary_threshold_m_s'],'source_surface_component_gate_m_s':r['surface_component_gate_m_s'],'source_component_bearing_degrees_true':r['component_bearing_degrees_true'],'source_core_search_depth_interval_m':r['core_search_depth_interval_m'],'source_primary_lower_status':r['primary_layer']['lower_status'],'source_censoring_kind':r['censoring_kind'],'source_last_connected_native_index':r['last_connected_native_index'],'source_last_connected_velocity_m_s':r['last_connected_velocity_m_s'],'source_next_native_index':r['next_native_index'],'source_next_native_depth_m':r['next_native_depth_m'],'source_next_signed_component_m_s':None,'source_next_native_level_exists':not domain,'source_native_domain_deep_limit_m':r['native_domain_deep_limit_m'],'source_native_level_count':r['native_level_count'],'source_native_endpoint_is_current_bottom':False,'source_missing_values_interpreted_as_bed':False,'source_bathymetry_used':False,'source_current_axis_independently_validated':False,'source_file':REPORT,'source_pointer':'/records/'+str(i),'source_sha256':report_sha,'same_source_width_reference_id':None,'independent_observation_count_claimed':False,'whole_current_representative':False,'volume_eligible':False,'physical_state_join_eligible':False,'seasonal_playback_eligible':False,'annual_extrema_eligible':False,'reference_route_projection_eligible':False})
    return refs


def build(root=ROOT):
    reader=lambda f:(root/f).read_bytes();read=lambda f:json.loads(reader(f));op=read(OPERATOR)
    if any(op['eligibility'].values()):raise ValueError('No physical/annual/volume/resolved-boundary promotion')
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(f)).hexdigest()!=pin:raise ValueError('Frozen native-bound input changed: '+f)
    previous=read(op['previous_inventory_file']);before=prior.load_inventory(previous,reader);base,statistical,regional,old_bounds=prior.read_parts(previous,reader)
    report=audit_and_derive(root,op);report.update(operator_file=OPERATOR,operator_sha256=hashlib.sha256(reader(OPERATOR)).hexdigest(),input_sha256=op['input_sha256'])
    encode=lambda value:(json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode();piece=lambda f,raw:{'file':f,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)};report_raw=encode(report);sop=read(op['source_operator_file']);contexts={}
    for entity in op['target_entities']:
        config=sop['currents'][entity];contexts[context_id(entity)]={'entity_id':entity,'source_method_family':'classic_upper200_surface_connected_integral','primary_threshold_m_s':config['primary_threshold_m_s'],'surface_component_gate_m_s':config['surface_component_gate_m_s'],'component_bearing_degrees_true':config['component_bearing_degrees_true'],'core_search_depth_interval_m':sop['core_search_depth_interval_m'],'snapshot_times_utc':sop['snapshot_times_utc'],'branch_scope':config['branch_scope'],'source_operator_file':op['source_operator_file'],'source_audit':report['source_audit'],'physical_current_bottom_established':False,'source_missing_values_interpreted_as_bed':False}
    addendum={'schema':'osw.current-depth-native-primary-penetration-addendum.v1','id':'malvinas-eacc-primary-censored-penetration-v1','base_snapshot_sha256':previous['base']['json']['sha256'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256(reader(OPERATOR)).hexdigest(),'input_sha256':op['input_sha256'],'derived_source_report':piece(REPORT,report_raw),'source_contexts':contexts,'evidence':references(report,hashlib.sha256(report_raw).hexdigest()),'runtime_changed':False,'full_goal_complete':False}
    assembled=assemble(base,statistical,regional,old_bounds,[(addendum,report)]);add_raw=encode(addendum);csv_raw=reference_csv_bytes(addendum['evidence']);inventory=copy.deepcopy(previous);inventory.update(schema='osw.current-depth-reference-inventory.v4',status='PINNED_REFERENCES_WITH_CONTEXT_OWNED_NATIVE_REACH_CENSORING_CLASSES',counts=assembled['counts'],metric_counts=assembled['metric_counts']);inventory['addenda'].append({'id':addendum['id'],'json':piece(ADDENDUM,add_raw),'csv':piece(CSV,csv_raw)});inventory['view_metadata'].update(schema='osw.current-depth-reference-view.v4',status='SCOPED_REFERENCES_AND_CONTEXT_OWNED_NATIVE_PRIMARY_REACH_BOUNDS',generator_file=GENERATOR,generator_sha256=hashlib.sha256(reader(GENERATOR)).hexdigest(),interpretation=op['interpretation'])
    pieces={INVENTORY:encode(inventory),ADDENDUM:add_raw,CSV:csv_raw,REPORT:report_raw}
    if any(len(raw)>=2500000 for raw in pieces.values()) or sum(map(len,pieces.values()))>=3000000:raise ValueError('Fixed publication caps exceeded')
    view=load_inventory(inventory,lambda f:pieces[f] if f in pieces else reader(f))
    if view['evidence'][:len(before['evidence'])]!=before['evidence']:raise ValueError('Every prior reference must remain unchanged')
    return inventory,addendum,report,pieces,view


def main():
    inventory,addendum,report,pieces,view=build();out=Path('current-depth-reference-inventory-v4');out.mkdir(exist_ok=True)
    for f,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv'),(REPORT,'source-report.json')]: (out/name).write_bytes(pieces[f])
    print(json.dumps({'counts':view['counts'],'source_audit':report['source_audit'],'new_bounds':[{'entity_id':r['entity_id'],'snapshot':r['source_snapshot_time_utc'],'section':r['source_section_id'],'lower_bound_m':r['lower_bound_m'],'censoring_kind':r['source_censoring_kind']} for r in addendum['evidence']],'new_field_requests':0}))


if __name__=='__main__':main()
