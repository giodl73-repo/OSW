"""Append explicit publisher-selected non-core water-mass lower extents."""
import copy,hashlib,json
from pathlib import Path
import load_current_depth_reference_inventory_v6 as prior
from load_current_depth_reference_inventory_v7 import assemble,load_inventory,reference_csv_bytes,CONTEXT
from derive_nwasc_selected_noncore_depths_v1 import audit_and_derive

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-reference-inventory-operator-v7.json'
GENERATOR='analysis/build_current_depth_reference_inventory_v7.py'
INVENTORY='research/current-depth-reference-inventory-v7.json'
ADDENDUM='research/current-depth-reference-addenda/nwasc-baumann-selected-noncore-depth-v1.json'
CSV='research/current-depth-reference-addenda/nwasc-baumann-selected-noncore-depth-v1.csv'
REPORT='research/nwasc-selected-noncore-depth-source-report-v1.json'


def references(report,report_sha,source):
    refs=[]
    for i,r in enumerate(report['records']):
        refs.append({'id':'nwasc-baumann2026-'+r['section_id']+'-selected-noncore-lower-extent','entity_id':r['entity_id'],'metric':'reported_selected_noncore_water_mass_lower_extent','approximate_value_m':r['reported_noncore_lower_extent_m'],'range_m':None,'range_interpretation':None,'lower_bound_m':None,'lower_bound_operator':None,'lower_bound_exclusive':False,'upper_bound_m':None,'upper_bound_exclusive':False,'unit':'m','vertical_datum':'local_sea_surface_positive_down','upper_boundary_m':None,'lower_boundary_m':None,'thickness_m':None,'uncertainty_m':None,'annual_range_m':None,'phase_label':'1993-2022static mean-defined non-core AW selection','calendar_months':None,'geographic_scope':r['section_id']+' selected non-core Atlantic Water domain associated with the Norwegian Atlantic Slope Current;not whole current or broader Norwegian Current.','temporal_scope':'Static1993-2022mean-defined spatial selection,not per-transect depths,annual extrema or seasonal samples.','observed_period':None,'source_definition':'Source-reported lower extent of the selected NON-CORE AW population outside the source50percent mean-transport core. Not physical current bottom or the core lower extent.','evidence_kind':'published_original_static_mean_selected_noncore_water_mass_extent','source_url':source['source_url'],'source_citation':source['citation'],'source_locator':source['source_locator'],'qualification':'Source population extent only. Original upper50m and shoreward isobath selection gates are analysis choices,not physical current edges. No uniform layer thickness,profile interpolation,annual range or volume.','source_context_id':CONTEXT,'source_statistic':'source_reported_static_mean_selected_noncore_lower_extent','source_population_role':r['source_population_role'],'source_section_id':r['section_id'],'source_figure_panel':r['source_figure_panel'],'source_existing_core_reference_id':r['existing_core_reference_id'],'source_core_lower_extent_m':r['source_core_lower_extent_m'],'source_core_comparison_is_error_bar':False,'source_shoreward_isobath_gate_m':r['shoreward_isobath_gate_m'],'source_selection':copy.deepcopy(r['source_selection']),'source_mean_definition_years':r['source_mean_definition_years'],'source_xml_file':r['source_xml_file'],'source_xml_paragraph_index':r['source_xml_paragraph_index'],'source_xml_normalized_paragraph_sha256':r['source_xml_normalized_paragraph_sha256'],'physical_current_bottom_established':False,'source_sampled_lon_lat':None,'source_file':REPORT,'source_pointer':'/records/'+str(i),'source_sha256':report_sha,'same_source_width_reference_id':None,'independent_observation_count_claimed':False,'whole_current_representative':False,'volume_eligible':False,'physical_state_join_eligible':False,'seasonal_playback_eligible':False,'annual_extrema_eligible':False,'reference_route_projection_eligible':False})
    return refs


def build(root=ROOT):
    reader=lambda f:(root/f).read_bytes();read=lambda f:json.loads(reader(f));op=read(OPERATOR)
    if any(op['eligibility'].values()):raise ValueError('No physical boundary,identity,annual or volume promotion')
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(f)).hexdigest()!=pin:raise ValueError('Frozen non-core source input changed: '+f)
    previous=read(op['previous_inventory_file']);before=prior.load_inventory(previous,reader);parts=prior.read_parts(previous,reader);source=read(op['source_context_file']);report=audit_and_derive(root,op);report.update(operator_file=OPERATOR,operator_sha256=hashlib.sha256(reader(OPERATOR)).hexdigest(),input_sha256=op['input_sha256'])
    encode=lambda value:(json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode();piece=lambda f,raw:{'file':f,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)};report_raw=encode(report)
    context={'entity_id':source['entity_id'],'source_population_role':source['source_population_role'],'source_selection':copy.deepcopy(source['selection']),'source_mean_definition_years':source['source_mean_definition_years'],'excluded_owner_ids':source['excluded_owner_ids'],'physical_current_bottom_established':False}
    addendum={'schema':'osw.current-depth-selected-noncore-extent-addendum.v1','id':'nwasc-baumann-selected-noncore-depth-v1','base_snapshot_sha256':previous['base']['json']['sha256'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256(reader(OPERATOR)).hexdigest(),'input_sha256':op['input_sha256'],'derived_source_report':piece(REPORT,report_raw),'source_contexts':{CONTEXT:context},'evidence':references(report,hashlib.sha256(report_raw).hexdigest(),source),'runtime_changed':False,'full_goal_complete':False}
    assembled=assemble(*parts,[(addendum,report)]);add_raw=encode(addendum);csv_raw=reference_csv_bytes(addendum['evidence']);inventory=copy.deepcopy(previous);inventory.update(schema='osw.current-depth-reference-inventory.v7',status='PINNED_REFERENCES_WITH_SELECTED_NONCORE_WATER_MASS_EXTENTS',counts=assembled['counts'],metric_counts=assembled['metric_counts']);inventory['addenda'].append({'id':addendum['id'],'json':piece(ADDENDUM,add_raw),'csv':piece(CSV,csv_raw)});inventory['view_metadata'].update(schema='osw.current-depth-reference-view.v7',status=inventory['status'],generator_file=GENERATOR,generator_sha256=hashlib.sha256(reader(GENERATOR)).hexdigest(),interpretation=op['interpretation'])
    pieces={INVENTORY:encode(inventory),ADDENDUM:add_raw,CSV:csv_raw,REPORT:report_raw}
    if any(len(raw)>=2500000 for raw in pieces.values()) or sum(map(len,pieces.values()))>=3000000:raise ValueError('Fixed publication caps exceeded')
    view=load_inventory(inventory,lambda f:pieces[f] if f in pieces else reader(f))
    if view['evidence'][:len(before['evidence'])]!=before['evidence']:raise ValueError('Every prior reference must remain unchanged')
    return inventory,addendum,report,pieces,view


def main():
    inventory,addendum,report,pieces,view=build();out=Path('current-depth-reference-inventory-v7');out.mkdir(exist_ok=True)
    for f,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv'),(REPORT,'source-report.json')]: (out/name).write_bytes(pieces[f])
    print(json.dumps({'counts':view['counts'],'new_noncore_extents':[{'section':r['section_id'],'reported_noncore_extent_m':r['reported_noncore_lower_extent_m'],'existing_core_extent_m':r['source_core_lower_extent_m']} for r in report['records']],'curated_transects_obtained':False,'new_ocean_field_requests':0,'physical_current_bottom_established':False}))


if __name__=='__main__':main()
