"""Retain composite Antarctic coastal depths with checked same-section width joins."""
import csv, hashlib, io, json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v22 as previous
ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v23.json'
RULES='research/current-depth-rules-v23.json'
OUTPUT='research/current-depth-register-v23.json'
CSV='research/current-depth-register-v23.csv'
WIDTHS='research/ocean-current-width-inventory.json'
AUDIT='research/antarctic-coastal-schubert-2021-composite-width-scope-audit.json'
validate_reference=previous.validate_reference

def validate_context(row,root=ROOT):
    n=row.get('hydrographic_section_number')
    if type(n) is not int or not 1<=n<=7:raise ValueError('Require reviewed composite section')
    width_doc=json.loads((root/WIDTHS).read_bytes());audit_doc=json.loads((root/AUDIT).read_bytes())
    wid='antarctic-coastal-schubert-2021-section-'+str(n).zfill(2)
    indexed=[(i,r) for i,r in enumerate(width_doc['measurements']) if r['id']==wid]
    if len(indexed)!=1:raise ValueError('Width identity must resolve uniquely')
    i,width=indexed[0];audit=audit_doc['measurements'][n-1]
    c=width['original_regional_context'];ac=audit['original_regional_context'];v=c['source_properties']
    if width['id']!=audit['id'] or width['current_id']!='antarctic-coastal' or width['approximate_width_km']!=audit['approximate_width_km'] or c['section_number']!=n:raise ValueError('Width/audit identity mismatch')
    for key in ['source_properties','temporal_operator','geostrophic_reference_depth_m','integration_base_salinity_psu','integration_base_is_fixed_depth','offshore_edge_fraction_of_center_integrated_velocity','profile_period_descriptions','sampling_dominant_season','sampling_prose_discrepancy']:
        if c[key]!=ac[key]:raise ValueError('Width/audit operator mismatch: '+key)
    required={'id':wid+'-mean-depth','entity_id':'current:antarctic-coastal','metric':'transport_selected_depth_extent','evidence_kind':'published_composite_hydrographic_section','source_case_id':'antarctic-coastal-schubert-2021-composite-section-'+str(n).zfill(2),
        'approximate_value_m':v['source_mean_depth_m'],'same_source_width_reference_id':wid,'source_width_reference_file':WIDTHS,'source_width_reference_pointer':'/measurements/'+str(i),'source_width_reference_sha256':hashlib.sha256((root/WIDTHS).read_bytes()).hexdigest(),
        'source_audit_file':AUDIT,'source_audit_pointer':'/measurements/'+str(n-1),'source_audit_sha256':hashlib.sha256((root/AUDIT).read_bytes()).hexdigest(),
        'section_depth_statistic':'source_reported_section_mean','source_spatial_depth_range_m':v['source_depth_range_m'],'depth_basis':'source_salinity_selected_composite_layer_mean','integration_base_salinity_psu':34.4,'integration_base_is_fixed_depth':False,
        'geostrophic_reference_depth_m':400,'reference_is_flow_boundary':False,'offshore_edge_fraction_of_center_integrated_velocity':0.15,'center_selection':'maximum_gradient_of_net_transport','shoreward_boundary':'coastline_or_ice_shelf_face',
        'temporal_operator':'all_available_profiles_moving_median_composite','source_profile_counts':{k:v[k] for k in ['winter_profiles','summer_profiles','total_profiles']},'source_profile_period_descriptions':c['profile_period_descriptions'],'sampling_dominant_season':c['sampling_dominant_season'],'sampling_prose_discrepancy':c['sampling_prose_discrepancy'],
        'independent_observation_count_claimed':False,'mean_depth_weighting_independently_recovered':False,'cross_section_area_eligible':False,'rectangle_cross_section_inferred':False,'exact_boundary_coordinates_available':False,'branch_section_scope':'regional_WAP_Bellingshausen_coastal_composite','source_access_scope':'retained_original_pdf_prose_and_page_pixels'}
    if not row.get('source_spatial_depth_range_interpretation'):raise ValueError('Spatial range requires interpretation')
    if not v['source_depth_range_m'][0]<=row['approximate_value_m']<=v['source_depth_range_m'][1]:raise ValueError('Mean outside reported spatial support')
    for k in ['section_sampling_month','calendar_months','phase_label','climatology_years']:
        if row.get(k) is not None:raise ValueError('Composite cannot become a dated or seasonal section')
    for k,v in required.items():
        if row.get(k)!=v:raise ValueError('Source/width context changed: '+k)

def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v22.py',RULES,SOURCE,WIDTHS,AUDIT]:
        pins[p]=hashlib.sha256((root/p).read_bytes()).hexdigest()
    source=json.loads((root/SOURCE).read_bytes());rules=json.loads((root/RULES).read_bytes())
    if source['previous_register_sha256']!=pins[previous.OUTPUT]:raise ValueError('Prior pin mismatch')
    for p,digest in source['source_input_sha256'].items():
        if pins[p]!=digest:raise ValueError('Retained source XML changed')
    evidence=list(prior['evidence']);seen={r['id'] for r in evidence};identities={r['entity_id'] for r in prior['records']}
    for i,row in enumerate(source['references']):
        validate_reference(row,identities,rules['metric_types']);validate_context(row,root)
        if row['id'] in seen:raise ValueError('Duplicate source reference')
        seen.add(row['id']);evidence.append(dict(row,source_file=SOURCE,source_pointer=f'/references/{i}',source_sha256=pins[SOURCE]))
    records=[]
    for raw in prior['records']:
        row=dict(raw);row['depth_reference_ids']=[r['id'] for r in evidence if r['entity_id']==row['entity_id']]
        row['status']='scoped_depth_reference' if row['depth_reference_ids'] else 'not_yet_assessed';records.append(row)
    owners=sum(bool(r['depth_reference_ids']) for r in records)
    return {'schema':'osw.current-depth-register.v23','status':'ANTARCTIC_COASTAL_COMPOSITE_DEPTHS_WITH_EXACT_WIDTH_JOINS',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v23.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v23.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Antarctic coastal composite means retain section-specific spatial depth ranges and exact matching width rows, salinity integration base, geostrophic reference and sampling counts. Shared source support does not establish mean-depth weighting, area, seasonal extrema or an instantaneous along-route profile.',
            'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns += [p for p in ['source_width_reference_file','source_width_reference_pointer','source_width_reference_sha256','source_audit_file','source_audit_pointer','source_audit_sha256','section_depth_statistic','source_spatial_depth_range_m','source_spatial_depth_range_interpretation','integration_base_salinity_psu','integration_base_is_fixed_depth','offshore_edge_fraction_of_center_integrated_velocity','center_selection','shoreward_boundary','temporal_operator','source_profile_counts','source_profile_period_descriptions','sampling_dominant_season','sampling_prose_discrepancy','mean_depth_weighting_independently_recovered'] if p not in columns]
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for raw in document['evidence']:
        row=dict(raw)
        if row.get('section_sampling_window'):
            row['section_window_start']=row['section_sampling_window']['start'];row['section_window_end']=row['section_sampling_window']['end']
        for key,value in list(row.items()):
            if isinstance(value,(dict,list)):row[key]=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        writer.writerow(row)
    return out.getvalue().encode('utf8')
