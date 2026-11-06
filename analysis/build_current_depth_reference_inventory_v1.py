"""Add source-reported REDSOX plume-layer statistics without expanding the base."""
import hashlib,json
from pathlib import Path
from load_current_depth_reference_inventory_v1 import assemble,load_inventory,reference_csv_bytes

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-reference-inventory-operator-v1.json'
GENERATOR='analysis/build_current_depth_reference_inventory_v1.py'
INVENTORY='research/current-depth-reference-inventory-v1.json'
ADDENDUM='research/current-depth-reference-addenda/redsox-published-plume-thickness-v1.json'
CSV='research/current-depth-reference-addenda/redsox-published-plume-thickness-v1.csv'
CONTEXT='peters-redsox-2005-table2-active-channel-axis-layers'


def references(facts):
    if facts['schema']!='osw.redsox-published-plume-thickness-source-facts.v1' or not facts['original_page_visually_reviewed'] or len(facts['data'])!=12:raise ValueError('Reviewed original twelve-row statistical table required')
    rows=[];seen=set()
    for i,fact in enumerate(facts['data']):
        channel=fact['channel'];layer=fact['layer'];cruise=fact['cruise'];key=(channel,layer,cruise)
        if key in seen or channel not in ['northern','southern'] or layer not in ['bottom','interfacial','whole_plume'] or cruise not in ['REDSOX-1','REDSOX-2']:raise ValueError('Unique channel/layer/cruise required')
        seen.add(key);rule=facts['boundary_rules'][cruise];season='winter' if cruise=='REDSOX-1' else 'summer'
        rows.append({'id':'redsox-peters-2005-'+channel+'-'+cruise.lower()+'-'+layer.replace('_','-')+'-mean-thickness','entity_id':'current:red-sea-saline-overflow','metric':'reported_vertical_thickness','approximate_value_m':fact['mean_thickness_m'],'range_m':[fact['minimum_sampled_thickness_m'],fact['maximum_sampled_thickness_m']],'range_kind':'minimum_and_maximum_among_source_selected_casts','range_interpretation':'Minimum and maximum among source-selected active channel-axis casts; spatial and occupation variability, not a confidence interval or annual extrema.','unit':'m','vertical_datum':'not_applicable_thickness_distance','upper_boundary_m':None,'lower_boundary_m':None,'thickness_m':None,'uncertainty_m':None,'annual_range_m':None,'phase_label':cruise+' '+season+' campaign; active '+channel+'-channel '+layer.replace('_',' ')+' layer','calendar_months':None,'geographic_scope':'REDSOX '+channel.title()+' Channel axis in the western Gulf of Aden; no per-cast locations reconstructed.','temporal_scope':cruise+' campaign in 2001, conditional on significant active plume flow; not an exact common occupation period or annual climatology.','observed_period':None,'source_definition':'Author-reported mean thickness of the '+layer.replace('_',' ')+' layer, with source cast minimum/maximum and count. Plume top uses cruise-specific speed/direction/salinity criteria.','evidence_kind':'published_observational_channel_axis_layer_thickness_statistics','source_url':facts['source_url'],'source_citation':'Peters, Johns, Bower and Fratantoni (2005), J. Phys. Oceanogr. 35, 569-583, doi:10.1175/JPO2679.1.','source_locator':'Table 2 and Section 5a, printed p577 / PDF p9.','qualification':'Conditional active-cast layer statistic; layers share casts. Winter and summer boundary thresholds differ. No whole-current, matched width, annual range, or stored-volume inference.','source_context_id':CONTEXT,'source_channel':channel,'source_layer_component':layer,'source_cruise':cruise,'source_season_label':season,'source_statistic':'source_reported_mean_over_selected_active_channel_axis_casts','source_cast_count':fact['ctd_ladcp_casts'],'source_reported_mean_thickness_m':fact['mean_thickness_m'],'source_reported_minimum_thickness_m':fact['minimum_sampled_thickness_m'],'source_reported_maximum_thickness_m':fact['maximum_sampled_thickness_m'],'source_top_boundary_speed_threshold_m_s':rule['speed_threshold_m_s'],'source_top_boundary_salinity_threshold_psu':rule['salinity_threshold_psu'],'source_top_boundary_direction_departure_degrees':45,'source_top_boundary_operator':'any_of_speed_less_than_cutoff_OR_direction_departure_greater_than45_OR_salinity_less_than_cutoff','source_bottom_layer_top':'velocity_maximum_above_seafloor','source_interfacial_layer_extent':'between_bottom_layer_top_and_plume_top','source_bottom_layer_detection_limit_approximately_m':15,'source_active_flow_cast_selection':True,'source_layer_cast_sets_overlap':True,'source_pdf_sha256':facts['source_pdf_sha256'],'source_file':'research/redsox-published-plume-thickness-source-facts-v1.json','source_pointer':'/data/'+str(i),'same_source_width_reference_id':None,'range_is_confidence_interval':False,'seasonal_common_operator_comparison_eligible':False,'independent_observation_count_claimed':False,'whole_current_representative':False,'volume_eligible':False,'physical_state_join_eligible':False,'seasonal_playback_eligible':False,'annual_extrema_eligible':False,'reference_route_projection_eligible':False})
    return rows


def build(root=ROOT):
    reader=lambda f:(root/f).read_bytes();read=lambda f:json.loads(reader(f));op=read(OPERATOR)
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(f)).hexdigest()!=pin:raise ValueError('Frozen source/reference input changed: '+f)
    facts=read(op['source_facts_file']);acquisition=read(op['source_acquisition_file'])
    if facts['source_pdf_sha256']!=acquisition['sha256'] or facts['source_url']!=acquisition['source_url'] or facts['source_pdf_bytes']!=acquisition['bytes']:raise ValueError('Original source custody metadata changed')
    base=read(op['base_register_file']);refs=references(facts)
    for ref in refs:ref['source_sha256']=hashlib.sha256(reader(op['source_facts_file'])).hexdigest()
    context={k:facts[k] for k in ['source_url','doi','source_pdf_sha256','source_pdf_bytes','source_locator','boundary_rules','qualifications','source_mean_weighting_reconstructed']}
    context.update(original_pdf_redistributed=False,new_field_requests=0,casts_are_independent_across_layers=False,source_active_cast_count_is_whole_cruise_cast_count=False)
    addendum={'schema':'osw.current-depth-statistical-thickness-addendum.v1','id':'redsox-published-plume-thickness-v1','base_snapshot_sha256':hashlib.sha256(reader(op['base_register_file'])).hexdigest(),'operator_file':OPERATOR,'operator_sha256':hashlib.sha256(reader(OPERATOR)).hexdigest(),'input_sha256':op['input_sha256'],'source_contexts':{CONTEXT:context},'evidence':refs,'runtime_changed':False,'full_goal_complete':False}
    encode=lambda value:(json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode('utf8')
    add_raw=encode(addendum);csv_raw=reference_csv_bytes(refs);piece=lambda f,raw:{'file':f,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    assembled=assemble(base,[addendum]);inventory={'schema':'osw.current-depth-reference-inventory.v1','status':'PINNED_FROZEN_REGISTER_AND_SCOPED_STATISTICAL_THICKNESS_ADDENDA','base':{'json':piece(op['base_register_file'],reader(op['base_register_file'])),'csv':piece(op['base_csv_file'],reader(op['base_csv_file']))},'addenda':[{'id':addendum['id'],'json':piece(ADDENDUM,add_raw),'csv':piece(CSV,csv_raw)}],'counts':assembled['counts'],'metric_counts':assembled['metric_counts'],'view_metadata':{'schema':'osw.current-depth-reference-view.v1','status':'FROZEN_REFERENCE_REGISTER_WITH_SCOPED_PUBLISHED_LAYER_STATISTICS','generator_file':GENERATOR,'generator_sha256':hashlib.sha256(reader(GENERATOR)).hexdigest(),'interpretation':op['interpretation'],'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False},'publication_policy':'Immutable base bytes remain unchanged. Query loader combines small pinned addenda in memory; no expanded register or combined CSV is published.','runtime_changed':False,'full_goal_complete':False}
    pieces={INVENTORY:encode(inventory),ADDENDUM:add_raw,CSV:csv_raw}
    if any(len(raw)>=2500000 for raw in pieces.values()) or sum(len(raw) for raw in pieces.values())>=3000000:raise ValueError('Fixed publication caps exceeded')
    view=load_inventory(inventory,lambda f:pieces[f] if f in pieces else reader(f));return inventory,addendum,pieces,view


def main():
    inventory,addendum,pieces,view=build();out=Path('current-depth-reference-inventory-v1');out.mkdir(exist_ok=True)
    for f,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv')]: (out/name).write_bytes(pieces[f])
    print(json.dumps({'counts':view['counts'],'new_reference_count':len(addendum['evidence']),'new_field_requests':0,'new_measurements_collected':0,'runtime_changed':False}))


if __name__=='__main__':main()
