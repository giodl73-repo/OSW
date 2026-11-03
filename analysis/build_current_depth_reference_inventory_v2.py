"""Append source-reported Persian Gulf Water regional core thicknesses."""
import copy,hashlib,json
from pathlib import Path
import load_current_depth_reference_inventory_v1 as prior
from load_current_depth_reference_inventory_v2 import assemble,load_inventory,reference_csv_bytes

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-reference-inventory-operator-v2.json'
GENERATOR='analysis/build_current_depth_reference_inventory_v2.py'
INVENTORY='research/current-depth-reference-inventory-v2.json'
ADDENDUM='research/current-depth-reference-addenda/pgw-pous-2004-regional-core-thickness-v1.json'
CSV='research/current-depth-reference-addenda/pgw-pous-2004-regional-core-thickness-v1.csv'
CONTEXT='pous-2004-gogp99-half-salinity-core-regional-thickness'


def references(facts):
    if facts['schema']!='osw.pgw-pous-regional-core-thickness-source-facts.v1' or not facts['original_pages_visually_reviewed'] or len(facts['data'])!=2 or facts['boundary_equation']!='(S_max+S_env)/2':raise ValueError('Reviewed regional hydrographic source descriptions required')
    rows=[];seen=set()
    for i,fact in enumerate(facts['data']):
        if fact['id'] in seen:raise ValueError('Duplicate regional source description')
        seen.add(fact['id'])
        rows.append({'id':fact['id'],'entity_id':'current:persian-gulf-saline-overflow','metric':'reported_vertical_thickness','approximate_value_m':fact['approximate_thickness_m'],'range_m':fact['approximate_thickness_range_m'],'range_kind':'author_approximate_regional_span' if fact['approximate_thickness_range_m'] is not None else None,'range_interpretation':'Author approximate regional thickness description, not sampled cast extrema, uncertainty or annual range.' if fact['approximate_thickness_range_m'] is not None else None,'unit':'m','vertical_datum':'not_applicable_thickness_distance','upper_boundary_m':None,'lower_boundary_m':None,'thickness_m':None,'uncertainty_m':None,'annual_range_m':None,'phase_label':'GOGP99 regional core description: '+fact['geographic_role'],'calendar_months':None,'geographic_scope':fact['geographic_scope'],'temporal_scope':'October-November 1999 GOGP99 campaign context; a regional narrative summary, not an exact common section occupation period.','observed_period':None,'source_definition':'Published approximate thickness of the Persian Gulf Water core bounded by half the salinity contrast between local core maximum and environmental water.','evidence_kind':'published_regional_hydrographic_core_thickness_description','source_url':facts['source_url'],'source_citation':'Pous, Carton and Lazure (2004), Hydrology and circulation in the Strait of Hormuz and the Gulf of Oman, part 2, doi:10.1029/2003JC002146.','source_locator':facts['source_locator'],'qualification':'Approximate regional hydrographic-core description; no cast mean/count, velocity boundary, paired geographic edges, uniform current thickness, annual extrema or volume inference.','source_context_id':CONTEXT,'source_statistic':'source_approximate_regional_description','source_cast_count':None,'source_value_qualifier':fact['value_qualifier'],'source_section_ids':fact['section_ids'],'source_geographic_role':fact['geographic_role'],'source_section_positions_reconstructed':False,'source_layer_identity':'half_salinity_contrast_PGW_core','source_core_boundary_equation':facts['boundary_equation'],'source_velocity_boundary_m_s':None,'source_width_thickness_boundary_definition_shared':True,'source_reported_mean_thickness_m':None,'source_reported_minimum_thickness_m':None,'source_reported_maximum_thickness_m':None,'source_pdf_sha256':facts['source_pdf_sha256'],'source_file':'research/pgw-pous-2004-regional-core-thickness-source-facts-v1.json','source_pointer':'/data/'+str(i),'same_source_width_reference_id':None,'range_is_confidence_interval':False,'seasonal_common_operator_comparison_eligible':False,'independent_observation_count_claimed':False,'whole_current_representative':False,'volume_eligible':False,'physical_state_join_eligible':False,'seasonal_playback_eligible':False,'annual_extrema_eligible':False,'reference_route_projection_eligible':False})
    return rows


def build(root=ROOT):
    reader=lambda f:(root/f).read_bytes();read=lambda f:json.loads(reader(f));op=read(OPERATOR)
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(f)).hexdigest()!=pin:raise ValueError('Frozen regional/reference input changed: '+f)
    previous=read(op['previous_inventory_file']);before=prior.load_inventory(previous,reader);base,statistical=prior.read_parts(previous,reader)
    facts=read(op['source_facts_file']);acquisition=read(op['source_acquisition_file'])
    if facts['source_pdf_sha256']!=acquisition['sha256'] or facts['source_pdf_bytes']!=acquisition['bytes'] or facts['source_url']!=acquisition['source_url'] or facts['doi']!=acquisition['doi']:raise ValueError('Original regional source custody metadata changed')
    refs=references(facts)
    for ref in refs:ref['source_sha256']=hashlib.sha256(reader(op['source_facts_file'])).hexdigest()
    context={k:facts[k] for k in ['source_url','doi','source_pdf_sha256','source_pdf_bytes','source_locator','boundary_equation','qualifications']};context.update(original_pdf_redistributed=False,new_field_requests=0,source_statistic='source_approximate_regional_description',cast_count_reported_for_these_descriptions=False,source_figure_digitized=False)
    addendum={'schema':'osw.current-depth-regional-description-addendum.v1','id':'pgw-pous-2004-regional-core-thickness-v1','base_snapshot_sha256':previous['base']['json']['sha256'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256(reader(OPERATOR)).hexdigest(),'input_sha256':op['input_sha256'],'source_contexts':{CONTEXT:context},'evidence':refs,'runtime_changed':False,'full_goal_complete':False}
    encode=lambda value:(json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode('utf8');add_raw=encode(addendum);csv_raw=reference_csv_bytes(refs);piece=lambda f,raw:{'file':f,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    assembled=assemble(base,statistical,[addendum]);inventory=copy.deepcopy(previous);inventory.update(schema='osw.current-depth-reference-inventory.v2',status='PINNED_REGISTER_WITH_STATISTICAL_AND_REGIONAL_HYDROGRAPHIC_THICKNESS',counts=assembled['counts'],metric_counts=assembled['metric_counts']);inventory['addenda'].append({'id':addendum['id'],'json':piece(ADDENDUM,add_raw),'csv':piece(CSV,csv_raw)});inventory['view_metadata'].update(schema='osw.current-depth-reference-view.v2',status='SCOPED_PUBLISHED_LAYER_STATISTICS_AND_REGIONAL_CORE_DESCRIPTIONS',generator_file=GENERATOR,generator_sha256=hashlib.sha256(reader(GENERATOR)).hexdigest(),interpretation=op['interpretation'])
    pieces={INVENTORY:encode(inventory),ADDENDUM:add_raw,CSV:csv_raw}
    if any(len(raw)>=2500000 for raw in pieces.values()) or sum(map(len,pieces.values()))>=3000000:raise ValueError('Fixed publication caps exceeded')
    view=load_inventory(inventory,lambda f:pieces[f] if f in pieces else reader(f))
    if view['evidence'][:len(before['evidence'])]!=before['evidence']:raise ValueError('Prior references must remain unchanged')
    return inventory,addendum,pieces,view


def main():
    inventory,addendum,pieces,view=build();out=Path('current-depth-reference-inventory-v2');out.mkdir(exist_ok=True)
    for f,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv')]: (out/name).write_bytes(pieces[f])
    print(json.dumps({'counts':view['counts'],'new_reference_count':len(addendum['evidence']),'new_field_requests':0,'new_measurements_collected':0,'runtime_changed':False}))


if __name__=='__main__':main()
