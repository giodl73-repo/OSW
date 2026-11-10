"""Audit the published inventory statistic without replacing its rounded value."""
import copy,hashlib,json
from decimal import Decimal,ROUND_HALF_UP


def audit_and_derive(root,op):
    read=lambda f:json.loads((root/f).read_bytes());facts=read(op['source_facts_file']);custody=read(facts['acquisition_file'])
    if facts['schema']!='osw.jutland-salinity-selected-area-mean-depth-source-facts.v1' or facts['entity_id']!='current:jutland' or facts['primary_table_and_scope_visually_verified'] is not True:raise ValueError('Known owner and visually verified original table required')
    if custody['primary_PDF_retained'] is not True or custody['http_status']!=200 or custody['body_sha256']!=facts['source_document_sha256'] or custody['body_bytes']!=facts['source_document_bytes'] or custody['source_url']!=facts['source_url'] or custody['attempts']!=1:raise ValueError('Exact successful primary PDF custody required')
    if facts['selection']!={'source_label':'JCW(S<34.0)','salinity_comparator':'<','salinity_threshold_source_value':34.0,'salinity_scale':'source_not_explicitly_standardized'} or facts['source_average_depth_definition']!='Ha=Vtot/Atot' or facts['reported_table_precision_decimal_places']!=0 or facts['reported_average_water_depth_Ha_m']!=22 or facts['reported_average_freshwater_depth_Hf_m']!=.55:raise ValueError('Original Ha statistic,selection,precision and separate Hf required')
    if facts['source_cruise_window']!={'start_date':'1989-11-27','end_date':'1989-12-06'} or facts['exact_inventory_occupation_dates_resolved'] is not False:raise ValueError('Cruise window is not exact inventory occupation dates')
    volume=facts['reported_total_water_volume'];area=facts['reported_total_area']
    if volume!={'table_coefficient':350000,'table_multiplier_power_of_ten':6,'unit':'m3'} or area!={'coefficient':1.59,'multiplier_power_of_ten':10,'unit':'m2'}:raise ValueError('Exact source-reported volume/area units and coefficients required')
    quotient=Decimal(str(volume['table_coefficient']))*Decimal(10)**volume['table_multiplier_power_of_ten']/(Decimal(str(area['coefficient']))*Decimal(10)**area['multiplier_power_of_ten'])
    rounded=int(quotient.quantize(Decimal('1'),rounding=ROUND_HALF_UP))
    if rounded!=facts['reported_average_water_depth_Ha_m']:raise ValueError('Source ratio inconsistent at reported precision')
    return {'schema':'osw.jutland-area-mean-depth-source-report.v1','entity_id':facts['entity_id'],'reported_value_m':facts['reported_average_water_depth_Ha_m'],'source_statistic':'source_reported_Ha_Vtot_divided_by_Atot','source_selection':copy.deepcopy(facts['selection']),'geographic_scope':facts['geographic_scope'],'source_cruise_window':copy.deepcopy(facts['source_cruise_window']),'reported_total_water_volume':copy.deepcopy(volume),'reported_total_area':copy.deepcopy(area),'arithmetic_check':{'dimension':'m3/m2=m','computed_quotient_m_for_consistency_only':str(quotient),'rounded_at_source_precision_m':rounded,'reported_value_replaced':False,'rounding_is_uncertainty':False},'source_facts_file':op['source_facts_file'],'source_facts_sha256':hashlib.sha256((root/op['source_facts_file']).read_bytes()).hexdigest(),'physical_current_bottom_established':False,'new_OSW_volume_estimate':False,'new_ocean_field_requests':0,'runtime_changed':False,'full_goal_complete':False}
