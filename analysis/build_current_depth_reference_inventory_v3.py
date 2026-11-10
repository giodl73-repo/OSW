"""Admit audited Florida native primary-penetration lower bounds."""
import copy,hashlib,json
from pathlib import Path
import load_current_depth_reference_inventory_v2 as prior
from load_current_depth_reference_inventory_v3 import assemble,load_inventory,reference_csv_bytes
from derive_florida_primary_penetration_bounds_v1 import audit_and_derive

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-reference-inventory-operator-v3.json'
GENERATOR='analysis/build_current_depth_reference_inventory_v3.py'
INVENTORY='research/current-depth-reference-inventory-v3.json'
ADDENDUM='research/current-depth-reference-addenda/florida-primary-censored-penetration-v1.json'
CSV='research/current-depth-reference-addenda/florida-primary-censored-penetration-v1.csv'
REPORT='research/florida-primary-censored-penetration-source-report-v1.json'
CONTEXT='florida-hycom2022-original-primary-censored-supported-reach'


def references(report,report_sha):
    refs=[]
    for i,r in enumerate(report['records']):
        if not r['reach_eligible']:continue
        refs.append({'id':'florida-hycom2022-'+r['snapshot_time_utc'][:10]+'-'+r['section_id']+'-primary-supported-reach-lower-bound','entity_id':'current:florida','metric':'derived_supported_component_penetration_lower_bound','approximate_value_m':None,'range_m':None,'lower_bound_m':r['lower_bound_m'],'lower_bound_operator':'>=','lower_bound_exclusive':False,'upper_bound_m':None,'upper_bound_exclusive':False,'range_interpretation':None,'unit':'m','vertical_datum':'local_sea_surface_positive_down','upper_boundary_m':None,'lower_boundary_m':None,'thickness_m':None,'uncertainty_m':None,'annual_range_m':None,'phase_label':r['snapshot_time_utc']+' instantaneous model supported reach','calendar_months':None,'geographic_scope':'Original selected northward-component model node in Florida Straits '+r['section_id']+'; partial25.5-27.5N regional context,not full current.','temporal_scope':'Two retained January15/July15,2022T00Z instantaneous model snapshots; no monthly mean or seasonal envelope.','observed_period':None,'source_definition':'Deepest contiguous native level with northward component strictly above the frozen primary0.1m/s threshold,connected to the selected0-200m core and surface; the following native signed-component value is missing. Inclusive minimum sampled penetration,not a detected lower boundary.','evidence_kind':'derived_instantaneous_model_supported_penetration_lower_bound','source_url':'https://www.hycom.org/dataserver/gofs-3pt1/analysis','source_citation':'HYCOM Consortium/NRL/COAPS-FSU,GOFS3.1GLBy0.08expt93.0uv3z2022;retained original regional section fields.','source_locator':'Original source section/profile/primary-layer references retained on this row.','qualification':'Censored native model support bound only. Missing/dry is not a bed or zero flow; source node/current identity unvalidated. Existing primary lower-boundary gaps remain unchanged. No interpolation,physical layer span,annual range or volume.','source_context_id':CONTEXT,'source_statistic':'native_surface_connected_primary_component_supported_reach','source_snapshot_time_utc':r['snapshot_time_utc'],'source_section_id':r['section_id'],'source_raw_profile_ref':r['source_profile_ref'],'source_raw_section_sha256':r['source_section_sha256'],'source_connected_layer_ref':r['source_connected_layer_ref'],'source_sampled_lon_lat':r['sampled_lon_lat'],'source_selected_column_index':r['selected_column_index'],'source_horizontal_selection_status':r['horizontal_selection_status'],'source_primary_threshold_m_s':r['primary_threshold_m_s'],'source_surface_component_gate_m_s':r['surface_component_gate_m_s'],'source_component_bearing_degrees_true':r['component_bearing_degrees_true'],'source_core_search_depth_interval_m':r['core_search_depth_interval_m'],'source_primary_lower_status':r['primary_layer']['lower_status'],'source_last_connected_native_index':r['last_connected_native_index'],'source_last_connected_velocity_m_s':r['last_connected_velocity_m_s'],'source_next_native_depth_m':r['next_native_depth_m'],'source_next_signed_component_m_s':None,'source_missing_values_interpreted_as_bed':False,'source_bathymetry_used':False,'source_current_axis_independently_validated':False,'source_file':REPORT,'source_pointer':'/records/'+str(i),'source_sha256':report_sha,'same_source_width_reference_id':None,'independent_observation_count_claimed':False,'whole_current_representative':False,'volume_eligible':False,'physical_state_join_eligible':False,'seasonal_playback_eligible':False,'annual_extrema_eligible':False,'reference_route_projection_eligible':False})
    return refs


def build(root=ROOT):
    reader=lambda f:(root/f).read_bytes();read=lambda f:json.loads(reader(f));op=read(OPERATOR)
    if any(op['eligibility'].values()):raise ValueError('No resolved-boundary/physical/annual/volume promotion')
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(f)).hexdigest()!=pin:raise ValueError('Frozen bound/reference input changed: '+f)
    previous=read(op['previous_inventory_file']);before=prior.load_inventory(previous,reader);base,statistical,regional=prior.read_parts(previous,reader)
    report=audit_and_derive(root,op);report.update(operator_file=OPERATOR,operator_sha256=hashlib.sha256(reader(OPERATOR)).hexdigest(),input_sha256=op['input_sha256'])
    encode=lambda value:(json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode();report_raw=encode(report);piece=lambda f,raw:{'file':f,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    context={'source_operator_file':op['source_operator_file'],'source_manifest_file':op['source_manifest_file'],'source_audit':report['source_audit'],'primary_threshold_m_s':.1,'core_search_depth_interval_m':[0,200],'component_bearing_degrees_true':0,'surface_component_gate_m_s':.05,'physical_current_bottom_established':False,'source_missing_values_interpreted_as_bed':False,'source_snapshot_time_basis':'HYCOM instantaneous2022January/July15T00Z,not monthly means or seasonal envelope.'}
    addendum={'schema':'osw.current-depth-supported-penetration-addendum.v1','id':'florida-primary-censored-penetration-v1','base_snapshot_sha256':previous['base']['json']['sha256'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256(reader(OPERATOR)).hexdigest(),'input_sha256':op['input_sha256'],'derived_source_report':piece(REPORT,report_raw),'source_contexts':{CONTEXT:context},'evidence':references(report,hashlib.sha256(report_raw).hexdigest()),'runtime_changed':False,'full_goal_complete':False}
    assembled=assemble(base,statistical,regional,[(addendum,report)]);add_raw=encode(addendum);csv_raw=reference_csv_bytes(addendum['evidence']);inventory=copy.deepcopy(previous);inventory.update(schema='osw.current-depth-reference-inventory.v3',status='PINNED_REFERENCES_WITH_EXPLICIT_CENSORED_PRIMARY_SUPPORTED_REACH_BOUNDS',counts=assembled['counts'],metric_counts=assembled['metric_counts']);inventory['addenda'].append({'id':addendum['id'],'json':piece(ADDENDUM,add_raw),'csv':piece(CSV,csv_raw)});inventory['view_metadata'].update(schema='osw.current-depth-reference-view.v3',status='SCOPED_REFERENCES_AND_AUDITED_PRIMARY_PENETRATION_LOWER_BOUNDS',generator_file=GENERATOR,generator_sha256=hashlib.sha256(reader(GENERATOR)).hexdigest(),interpretation=op['interpretation'])
    pieces={INVENTORY:encode(inventory),ADDENDUM:add_raw,CSV:csv_raw,REPORT:report_raw}
    if any(len(raw)>=2500000 for raw in pieces.values()) or sum(map(len,pieces.values()))>=3000000:raise ValueError('Fixed publication caps exceeded')
    view=load_inventory(inventory,lambda f:pieces[f] if f in pieces else reader(f))
    if view['evidence'][:len(before['evidence'])]!=before['evidence']:raise ValueError('All prior references must remain unchanged')
    return inventory,addendum,report,pieces,view


def main():
    inventory,addendum,report,pieces,view=build();out=Path('current-depth-reference-inventory-v3');out.mkdir(exist_ok=True)
    for f,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv'),(REPORT,'source-report.json')]: (out/name).write_bytes(pieces[f])
    print(json.dumps({'counts':view['counts'],'new_reach_bounds':len(addendum['evidence']),'source_audit':report['source_audit'],'bounds':[{'snapshot':r['source_snapshot_time_utc'],'section':r['source_section_id'],'lower_bound_m':r['lower_bound_m']} for r in addendum['evidence']],'new_field_requests':0}))


if __name__=='__main__':main()
