"""Append Indian Ocean seasonal sections while separating simulation and calendar time."""
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v10 as previous

ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v11.json'
RULES='research/current-depth-rules-v11.json'
OUTPUT='research/current-depth-register-v11.json'
CSV='research/current-depth-register-v11.csv'
validate_reference=previous.validate_reference


def validate_context(row):
    if row.get('same_source_width_reference_id') is not None or row.get('independent_observation_count_claimed') is not False:
        raise ValueError('No width join or independent repeat established')
    case=row['source_case_id'];entity=row['entity_id']
    if '-sen-2022-' in case:
        basis={'kind':'repeating_climatological_forcing','simulation_duration_years':8,'analysis_window':'last_three_simulation_years','calendar_years':None}
        if row.get('model_time_basis')!=basis or row.get('model_product')!='Sen2022_ROMS_NIO' or row['evidence_kind']!='published_model_seasonal_climatology':
            raise ValueError('Retain climatological simulation time basis')
        if row.get('climatology_years') is not None or row.get('section_sampling_month') is not None or row.get('campaign_window') is not None:
            raise ValueError('No calendar observation years assigned to climatological run')
    if case=='eacc-zheng-2024-ofes-mean':
        if entity!='current:east-african-coastal' or row.get('model_product')!='OFES' or row.get('climatology_years')!=[1993,2017] or row['evidence_kind']!='published_model_climatology':
            raise ValueError('EACC mean belongs to OFES1993–2017')
        if row.get('section_latitude_band_degrees_north')!=[-11,0] or row.get('spatial_averaging')!='coast_to_source_eastern_boundary_and_0_to_11S' or row['calendar_months'] is not None:
            raise ValueError('Regional vertical mean is not a June-only main-axis depth')
        if row['id'].endswith('-core'):
            if row['metric']!='core_depth' or row['range_m']!=[20,80] or row.get('core_definition')!={'kind':'maximum_regional_mean_meridional_velocity'}:raise ValueError('Retain regional velocity-core band')
        elif row['id'].endswith('-concentrated-reach'):
            if row['metric']!='reported_vertical_extent' or row['approximate_value_m']!=300:raise ValueError('Concentrated layer is not a hard bottom')
        else:raise ValueError('Unknown EACC reference')
    elif case in ['eicc-sen-2022-northward','eicc-sen-2022-southward']:
        expected={
            'north-a-core':('core_depth',150,None,'A',19.3,[85.3,87.4]),
            'north-b-reach':('reported_vertical_extent',20,None,'B',16,[82.1,84.2]),
            'north-c-core-band':('core_depth',None,[0,100],'C',12,[80,82.1]),
            'south-regional-reach':('reported_vertical_extent',200,None,None,None,None),
            'south-b-core':('core_depth',150,None,'B',16,[82.1,84.2]),
            'south-c-core':('core_depth',100,None,'C',12,[80,82.1])}
        tag=row['id'].removeprefix('eicc-sen-2022-')
        values=(row['metric'],row['approximate_value_m'],row['range_m'],row.get('section_name'),row.get('section_latitude_degrees_north'),row.get('section_longitude_band_degrees_east'))
        if entity!='current:east-india-coastal' or tag not in expected or values!=expected[tag]:raise ValueError('EICC section geometry and metric cannot be interchanged')
        direction='northward' if tag.startswith('north-') else 'southward';months=[2,3,4] if direction=='northward' else [10,11,12]
        if case!='eicc-sen-2022-'+direction or row.get('flow_direction')!=direction or row['calendar_months']!=months:raise ValueError('Retain EICC seasonal direction')
        if row['metric']=='core_depth' and row.get('core_definition')!={'kind':'maximum_directional_meridional_velocity'}:raise ValueError('Velocity core is not a property core')
    elif case.startswith('wicc-sen-2022-'):
        expected={'north-seasonal-reach':('reported_vertical_extent',100,[10,11,12,1,2],'northward','reported_seasonal_reach'),'south-june-reversal':('lower_flow_boundary_depth',60,[6],'southward','reported_direction_reversal'),'south-july-august-reversal':('lower_flow_boundary_depth',30,[7,8],'southward','reported_direction_reversal')}
        tag=case.removeprefix('wicc-sen-2022-');values=(row['metric'],row['approximate_value_m'],row['calendar_months'],row.get('flow_direction'),row.get('boundary_definition'))
        if entity!='current:west-india-coastal' or tag not in expected or values!=expected[tag]:raise ValueError('Summer reversal cannot be replaced by100m transport cutoff')
    elif case.startswith('somali-sen-2022-'):
        expected={'northeast-a-c-reach':(800,[5,6,7,8,9,10],'northeastward',None,None,None),'southwest-b-reach':(500,[11,12,1,2],'southwestward','B',6,[49,51.5]),'southwest-c-reach':(600,[11,12,1,2],'southwestward','C',3,[46.7,49.2])}
        tag=case.removeprefix('somali-sen-2022-');values=(row['approximate_value_m'],row['calendar_months'],row.get('flow_direction'),row.get('section_name'),row.get('section_latitude_degrees_north'),row.get('section_longitude_band_degrees_east'))
        if entity!='current:somali' or row['metric']!='reported_vertical_extent' or tag not in expected or values!=expected[tag]:raise ValueError('Somali directional section reach changed')
        if tag=='northeast-a-c-reach' and (row.get('section_names')!=['A','C'] or row.get('source_longitude_bands_degrees_east')!=[[50.5,53],[46.7,49.2]]):raise ValueError('Do not infer sectionB reach from transport integration')
    elif case=='semc-nauw-2008-april2001':
        if entity!='current:southern-east-madagascar' or row['evidence_kind']!='published_observed_section_summary' or row.get('section_sampling_month')!='2001-04' or row.get('velocity_reconstruction')!='LADCP_inverse_solution':raise ValueError('Observed poleward current is distinct from undercurrent')
        if row.get('campaign_window')!={'start':'2001-03-05','end':'2001-04-16'} or row.get('window_role')!='whole_campaign_not_exact_section_occupation':raise ValueError('Retain April section timing separately from entire campaign')
        if row['id'].endswith('-jet-reach'):
            if row['metric']!='reported_vertical_extent' or row['approximate_value_m']!=1000 or row.get('section_names')!=['T5','T6','T7','T8']:raise ValueError('Jet reach is not isotherm or sampling depth')
        elif row['id'].endswith('-t6-t8-core-band'):
            if row['metric']!='core_depth' or row['range_m']!=[100,160] or row.get('section_names')!=['T6','T7','T8'] or row.get('core_definition')!={'kind':'maximum_poleward_LADCP_velocity'}:raise ValueError('T5 near-surface core is not included in T6–T8 band')
        else:raise ValueError('Unknown SEMC reference')
    else:raise ValueError('Unreviewed source case')


def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v10.py',RULES,SOURCE]:
        pins[p]=hashlib.sha256((root/p).read_bytes()).hexdigest()
    source=json.loads((root/SOURCE).read_bytes());rules=json.loads((root/RULES).read_bytes())
    if source['previous_register_sha256']!=pins[previous.OUTPUT]:raise ValueError('Prior pin mismatch')
    for p,digest in source['source_input_sha256'].items():
        if pins[p]!=digest:raise ValueError('Retained source XML changed')
    evidence=list(prior['evidence']);seen={r['id'] for r in evidence};identities={r['entity_id'] for r in prior['records']}
    for i,row in enumerate(source['references']):
        validate_reference(row,identities,rules['metric_types']);validate_context(row)
        if row['id'] in seen:raise ValueError('Duplicate source reference')
        seen.add(row['id']);evidence.append(dict(row,source_file=SOURCE,source_pointer=f'/references/{i}',source_sha256=pins[SOURCE]))
    records=[]
    for raw in prior['records']:
        row=dict(raw);row['depth_reference_ids']=[r['id'] for r in evidence if r['entity_id']==row['entity_id']]
        row['status']='scoped_depth_reference' if row['depth_reference_ids'] else 'not_yet_assessed';records.append(row)
    owners=sum(bool(r['depth_reference_ids']) for r in records)
    return {'schema':'osw.current-depth-register.v11','status':'SCOPED_INDIAN_OCEAN_SEASONAL_SECTION_REFERENCES',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v11.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v11.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Seasonal model directions retain their separate sections and simulation time basis. Direction reversal is distinct from transport integration limits; regional mean core bands and observed section bands are not temporal extrema.',
            'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns+=['model_time_basis','flow_direction','boundary_definition','spatial_averaging','section_names','source_longitude_bands_degrees_east']
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for raw in document['evidence']:
        row=dict(raw)
        if row.get('section_sampling_window'):
            row['section_window_start']=row['section_sampling_window']['start'];row['section_window_end']=row['section_sampling_window']['end']
        for key,value in list(row.items()):
            if isinstance(value,(dict,list)):row[key]=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        writer.writerow(row)
    return out.getvalue().encode('utf8')
