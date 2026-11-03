"""Append one published regional Jutland inventory mean without gap repair."""
import copy,hashlib,json
from pathlib import Path
import load_current_depth_reference_inventory_v5 as prior
from load_current_depth_reference_inventory_v6 import assemble,load_inventory,reference_csv_bytes,CONTEXT
from derive_jutland_area_mean_depth_reference_v1 import audit_and_derive

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-reference-inventory-operator-v6.json'
GENERATOR='analysis/build_current_depth_reference_inventory_v6.py'
INVENTORY='research/current-depth-reference-inventory-v6.json'
ADDENDUM='research/current-depth-reference-addenda/jutland-aure1989-area-mean-depth-v1.json'
CSV='research/current-depth-reference-addenda/jutland-aure1989-area-mean-depth-v1.csv'
REPORT='research/jutland-aure1989-area-mean-depth-source-report-v1.json'


def reference(report,report_sha,facts):
    return {'id':'jutland-aure1989-salinity-selected-area-mean-water-depth','entity_id':'current:jutland','metric':'reported_salinity_selected_area_mean_water_depth','approximate_value_m':report['reported_value_m'],'range_m':None,'range_interpretation':None,'lower_bound_m':None,'lower_bound_operator':None,'lower_bound_exclusive':False,'upper_bound_m':None,'upper_bound_exclusive':False,'unit':'m','vertical_datum':'not_applicable_volume_area_ratio_distance','upper_boundary_m':None,'lower_boundary_m':None,'thickness_m':None,'uncertainty_m':None,'annual_range_m':None,'phase_label':'lateautumn1989source coastal-water inventory','calendar_months':None,'geographic_scope':report['geographic_scope'],'temporal_scope':'Finite lateautumn survey; source cruiseNovember27-December6,1989. Exact inventory occupation dates unresolved; no seasonal climatology or annual extrema.','observed_period':None,'source_cruise_window':copy.deepcopy(report['source_cruise_window']),'source_definition':'Published Table2 average water depth Ha=Vtot/Atot for source salinity-selected JCW regional inventory; retain rounded reported22m,not a velocity-current bottom.','evidence_kind':'published_source_reported_regional_salinity_selected_inventory_mean_depth','source_url':facts['source_url'],'source_citation':facts['citation'],'source_locator':facts['source_locator'],'qualification':'Regional area mean only. No uniform whole-current depth,velocity-isotach boundary,layer thickness,annual range or compatible OSW volume estimate is established. Source Hf is a separate freshwater-equivalent metric.','source_context_id':CONTEXT,'source_statistic':report['source_statistic'],'source_selection':copy.deepcopy(report['source_selection']),'source_reported_total_water_volume':copy.deepcopy(report['reported_total_water_volume']),'source_reported_total_area':copy.deepcopy(report['reported_total_area']),'source_value_replaced_by_computed_quotient':False,'source_rounding_is_uncertainty':False,'physical_current_bottom_established':False,'source_sampled_lon_lat':None,'source_facts_file':report['source_facts_file'],'source_facts_pointer':'/reported_average_water_depth_Ha_m','source_facts_sha256':report['source_facts_sha256'],'source_file':REPORT,'source_pointer':'/reported_value_m','source_sha256':report_sha,'same_source_width_reference_id':None,'independent_observation_count_claimed':False,'whole_current_representative':False,'volume_eligible':False,'physical_state_join_eligible':False,'seasonal_playback_eligible':False,'annual_extrema_eligible':False,'reference_route_projection_eligible':False}


def build(root=ROOT):
    reader=lambda f:(root/f).read_bytes();read=lambda f:json.loads(reader(f));op=read(OPERATOR)
    if any(op['eligibility'].values()):raise ValueError('No physical boundary,annual or volume promotion')
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(f)).hexdigest()!=pin:raise ValueError('Frozen regional source input changed: '+f)
    previous=read(op['previous_inventory_file']);before=prior.load_inventory(previous,reader);parts=prior.read_parts(previous,reader);facts=read(op['source_facts_file']);report=audit_and_derive(root,op);report.update(operator_file=OPERATOR,operator_sha256=hashlib.sha256(reader(OPERATOR)).hexdigest(),input_sha256=op['input_sha256'])
    encode=lambda value:(json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode();piece=lambda f,raw:{'file':f,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)};report_raw=encode(report)
    context={'entity_id':'current:jutland','source_average_depth_definition':'Ha=Vtot/Atot','source_selection':copy.deepcopy(report['source_selection']),'source_document_sha256':facts['source_document_sha256'],'source_cruise_window':facts['source_cruise_window'],'geographic_scope':facts['geographic_scope'],'source_survey_condition':facts['source_survey_condition'],'physical_current_bottom_established':False}
    addendum={'schema':'osw.current-depth-salinity-selected-area-mean-addendum.v1','id':'jutland-aure1989-area-mean-depth-v1','base_snapshot_sha256':previous['base']['json']['sha256'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256(reader(OPERATOR)).hexdigest(),'input_sha256':op['input_sha256'],'derived_source_report':piece(REPORT,report_raw),'source_contexts':{CONTEXT:context},'evidence':[reference(report,hashlib.sha256(report_raw).hexdigest(),facts)],'runtime_changed':False,'full_goal_complete':False}
    assembled=assemble(*parts,[(addendum,report)]);add_raw=encode(addendum);csv_raw=reference_csv_bytes(addendum['evidence']);inventory=copy.deepcopy(previous);inventory.update(schema='osw.current-depth-reference-inventory.v6',status='PINNED_REFERENCES_WITH_SOURCE_REPORTED_REGIONAL_WATER_INVENTORY_MEAN',counts=assembled['counts'],metric_counts=assembled['metric_counts']);inventory['addenda'].append({'id':addendum['id'],'json':piece(ADDENDUM,add_raw),'csv':piece(CSV,csv_raw)});inventory['view_metadata'].update(schema='osw.current-depth-reference-view.v6',status=inventory['status'],generator_file=GENERATOR,generator_sha256=hashlib.sha256(reader(GENERATOR)).hexdigest(),interpretation=op['interpretation'])
    pieces={INVENTORY:encode(inventory),ADDENDUM:add_raw,CSV:csv_raw,REPORT:report_raw}
    if any(len(raw)>=2500000 for raw in pieces.values()) or sum(map(len,pieces.values()))>=3000000:raise ValueError('Fixed publication caps exceeded')
    view=load_inventory(inventory,lambda f:pieces[f] if f in pieces else reader(f))
    if view['evidence'][:len(before['evidence'])]!=before['evidence']:raise ValueError('Every prior reference must remain unchanged')
    return inventory,addendum,report,pieces,view


def main():
    inventory,addendum,report,pieces,view=build();out=Path('current-depth-reference-inventory-v6');out.mkdir(exist_ok=True)
    for f,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv'),(REPORT,'source-report.json')]: (out/name).write_bytes(pieces[f])
    print(json.dumps({'counts':view['counts'],'new_source_reported_mean_m':report['reported_value_m'],'source_statistic':report['source_statistic'],'arithmetic_check':report['arithmetic_check'],'new_ocean_field_requests':0,'physical_current_bottom_established':False}))


if __name__=='__main__':main()
