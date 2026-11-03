"""Append original-observation Tsushima depth scenarios without physical promotion."""
import copy,hashlib,json
from pathlib import Path
import load_current_depth_reference_inventory_v4 as prior
from load_current_depth_reference_inventory_v5 import assemble,load_inventory,reference_csv_bytes,CONTEXT
from derive_tsushima_observed_pair_depth_v1 import audit_and_derive

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-reference-inventory-operator-v5.json'
GENERATOR='analysis/build_current_depth_reference_inventory_v5.py'
INVENTORY='research/current-depth-reference-inventory-v5.json'
ADDENDUM='research/current-depth-reference-addenda/tsushima-observed-pair-direction-change-v1.json'
CSV='research/current-depth-reference-addenda/tsushima-observed-pair-direction-change-v1.csv'
REPORT='research/tsushima-observed-pair-direction-change-source-report-v1.json'


def references(report,report_sha,facts):
    refs=[]
    for i,r in enumerate(report['records']):
        if not r['eligible']:continue
        s=r['source_row']['station']
        refs.append({'id':'tsushima-matsuyama1980-station-'+s.lower()+'-two-level-mean-direction-change-scenario','entity_id':'current:tsushima','metric':'derived_two_level_mean_direction_change_depth_scenario','approximate_value_m':r['linear_scenario_depth_m'],'range_m':None,'range_interpretation':None,'lower_bound_m':None,'lower_bound_operator':None,'lower_bound_exclusive':False,'upper_bound_m':None,'upper_bound_exclusive':False,'unit':'m','vertical_datum':'local_sea_surface_positive_down','upper_boundary_m':None,'lower_boundary_m':None,'thickness_m':None,'uncertainty_m':None,'annual_range_m':None,'phase_label':'1980-07-26 to 1980-08-14 common campaign mean','calendar_months':None,'geographic_scope':facts['geographic_scope']+' Station'+s+'.','temporal_scope':'Finite common19day Table1 means; not full31day A/B records,seasonal climatology or annual extrema.','observed_period':copy.deepcopy(r['table_mean_period']),'source_definition':'Conditional linear interpolation to zero signed mean alongshore flow between two original current-meter depths. Original open bracket retained; actual profile shape,number of crossings and physical current bottom unverified.','evidence_kind':'observed_campaign_mean_pair_with_explicit_linear_direction_change_depth_scenario','source_url':facts['source_url'],'source_citation':facts['citation'],'source_locator':facts['source_locator']+' Station'+s+'.','qualification':'Approximate scenario from two observed campaign means. Not a measured exact zero contour,physical current depth,layer thickness,full-route profile or volume. No interpolation among stations or unsampled surface/bottom.','source_context_id':CONTEXT,'source_statistic':facts['statistic'],'source_interpolation_assumption':'linear_between_two_reported_campaign_means','source_observed_pair':copy.deepcopy(r['source_row']),'source_open_direction_change_bracket_m':copy.deepcopy(r['open_depth_bracket_m']),'source_bracket_endpoints_excluded':True,'source_zero_crossing_uniqueness_established':False,'source_raw_profile_reconstructed':False,'physical_current_bottom_established':False,'source_sampled_lon_lat':None,'source_facts_file':r['source_facts_file'],'source_facts_pointer':r['source_pointer'],'source_facts_sha256':r['source_facts_sha256'],'source_file':REPORT,'source_pointer':'/records/'+str(i),'source_sha256':report_sha,'same_source_width_reference_id':None,'independent_observation_count_claimed':False,'whole_current_representative':False,'volume_eligible':False,'physical_state_join_eligible':False,'seasonal_playback_eligible':False,'annual_extrema_eligible':False,'reference_route_projection_eligible':False})
    return refs


def build(root=ROOT):
    reader=lambda f:(root/f).read_bytes();read=lambda f:json.loads(reader(f));op=read(OPERATOR)
    if any(op['eligibility'].values()):raise ValueError('No physical boundary,annual or volume promotion')
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(f)).hexdigest()!=pin:raise ValueError('Frozen observed-pair input changed: '+f)
    previous=read(op['previous_inventory_file']);before=prior.load_inventory(previous,reader);parts=prior.read_parts(previous,reader);facts=read(op['source_facts_file']);report=audit_and_derive(root,op);report.update(operator_file=OPERATOR,operator_sha256=hashlib.sha256(reader(OPERATOR)).hexdigest(),input_sha256=op['input_sha256'])
    encode=lambda value:(json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode();piece=lambda f,raw:{'file':f,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)};report_raw=encode(report)
    context={'entity_id':'current:tsushima','table_mean_period':facts['table_mean_period'],'geographic_scope':facts['geographic_scope'],'source_document_sha256':facts['source_document_sha256'],'source_method_family':'two_level_observed_campaign_mean_linear_direction_change_scenario','physical_current_bottom_established':False}
    addendum={'schema':'osw.current-depth-two-level-direction-change-addendum.v1','id':'tsushima-observed-pair-direction-change-v1','base_snapshot_sha256':previous['base']['json']['sha256'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256(reader(OPERATOR)).hexdigest(),'input_sha256':op['input_sha256'],'derived_source_report':piece(REPORT,report_raw),'source_contexts':{CONTEXT:context},'evidence':references(report,hashlib.sha256(report_raw).hexdigest(),facts),'runtime_changed':False,'full_goal_complete':False}
    assembled=assemble(*parts,[(addendum,report)]);add_raw=encode(addendum);csv_raw=reference_csv_bytes(addendum['evidence']);inventory=copy.deepcopy(previous);inventory.update(schema='osw.current-depth-reference-inventory.v5',status='PINNED_REFERENCES_WITH_OBSERVED_PAIR_CONDITIONAL_DEPTH_SCENARIOS',counts=assembled['counts'],metric_counts=assembled['metric_counts']);inventory['addenda'].append({'id':addendum['id'],'json':piece(ADDENDUM,add_raw),'csv':piece(CSV,csv_raw)});inventory['view_metadata'].update(schema='osw.current-depth-reference-view.v5',status=inventory['status'],generator_file=GENERATOR,generator_sha256=hashlib.sha256(reader(GENERATOR)).hexdigest(),interpretation=op['interpretation'])
    pieces={INVENTORY:encode(inventory),ADDENDUM:add_raw,CSV:csv_raw,REPORT:report_raw}
    if any(len(raw)>=2500000 for raw in pieces.values()) or sum(map(len,pieces.values()))>=3000000:raise ValueError('Fixed publication caps exceeded')
    view=load_inventory(inventory,lambda f:pieces[f] if f in pieces else reader(f))
    if view['evidence'][:len(before['evidence'])]!=before['evidence']:raise ValueError('Every previous reference must remain unchanged')
    return inventory,addendum,report,pieces,view


def main():
    inventory,addendum,report,pieces,view=build();out=Path('current-depth-reference-inventory-v5');out.mkdir(exist_ok=True)
    for f,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv'),(REPORT,'source-report.json')]: (out/name).write_bytes(pieces[f])
    print(json.dumps({'counts':view['counts'],'new_conditional_scenarios':[{'station':r['source_observed_pair']['station'],'linear_depth_m':r['approximate_value_m'],'open_observed_pair_bracket_m':r['source_open_direction_change_bracket_m']} for r in addendum['evidence']],'retained_original_station_pairs':len(report['records']),'new_ocean_field_requests':0,'physical_current_bottom_established':False}))


if __name__=='__main__':main()
