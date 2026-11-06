"""Explicit linear scenarios from original campaign paired mean currents."""
import copy,hashlib,json,math


def derive_pair(row):
    keys=['shallow_depth_m','deep_depth_m','shallow_mean_U_cm_s','deep_mean_U_cm_s']
    if any(type(row[k]) not in [int,float] or not math.isfinite(row[k]) for k in keys):raise ValueError('Finite reported depths and signed means required')
    za,zb,ua,ub=[row[k] for k in keys]
    if not 0<za<zb:raise ValueError('Ordered positive source sampling depths required')
    if not ua>0>ub:return {'eligible':False,'reason':'original_pair_does_not_bracket_positive_to_negative_mean_flow','open_depth_bracket_m':None,'linear_scenario_depth_m':None}
    value=za+ua/(ua-ub)*(zb-za)
    if not za<value<zb:raise ValueError('Linear zero must be strictly inside original observation bracket')
    return {'eligible':True,'reason':'opposite_signed_campaign_means_with_explicit_linear_vertical_assumption','open_depth_bracket_m':[za,zb],'linear_scenario_depth_m':value}


def audit_and_derive(root,op):
    read=lambda f:json.loads((root/f).read_bytes());facts=read(op['source_facts_file']);custody=read(facts['acquisition_file'])
    if facts['schema']!='osw.tsushima-campaign-two-level-mean-current-source-facts.v1' or facts['entity_id']!='current:tsushima' or facts['source_document_sha256']!=custody['sha256'] or facts['source_document_bytes']!=custody['bytes'] or facts['source_url']!=custody['source_url'] or facts['primary_table_visually_verified'] is not True:raise ValueError('Original visually reviewed primary table custody required')
    if facts['table_mean_period']!={'start_date':'1980-07-26','end_date':'1980-08-14','source_reported_common_days':19} or facts['velocity_unit']!='cm/s' or facts['depth_unit']!='m' or facts['vertical_datum']!='local_sea_surface_positive_down' or facts['statistic']!='source_reported_common_period_mean_signed_alongshore_component_U':raise ValueError('Original Table1 common period,units and statistic required')
    if [r['station'] for r in facts['rows']]!=['A','C','B','D','E']:raise ValueError('All original Table1 station pairs and source order required')
    records=[]
    for i,r in enumerate(facts['rows']):
        if r['positive_alongshore_bearing_degrees_true']!=(75 if r['station']=='E' else 90):raise ValueError('Original station-specific signed frame changed')
        records.append({'entity_id':facts['entity_id'],'source_row':copy.deepcopy(r),'source_pointer':'/rows/'+str(i),'source_facts_file':op['source_facts_file'],'source_facts_sha256':hashlib.sha256((root/op['source_facts_file']).read_bytes()).hexdigest(),'table_mean_period':copy.deepcopy(facts['table_mean_period']),**derive_pair(r)})
    return {'schema':'osw.tsushima-two-level-mean-direction-change-source-report.v1','records':records,'eligible_scenario_count':sum(r['eligible'] for r in records),'physical_current_bottom_established':False,'zero_crossing_uniqueness_established':False,'raw_profile_reconstructed':False,'station_geometry_invented':False,'new_ocean_field_requests':0,'runtime_changed':False,'full_goal_complete':False}
