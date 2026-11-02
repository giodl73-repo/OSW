"""Join reviewed local velocity layers without promoting them to whole-current geometry."""
import csv, hashlib, io, json
from collections import Counter
from pathlib import Path
import build_current_depth_register_v14 as previous
ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-source-facts-v15.json'
RULES='research/current-depth-rules-v15.json'
OUTPUT='research/current-depth-register-v15.json'
CSV='research/current-depth-register-v15.csv'
SERIES='research/caribbean-current-depth-measurements-v1.json'
OPERATOR='research/caribbean-current-depth-operator-v1.json'
REVIEW='research/caribbean-current-depth-measurement-review-v1.json'
validate_reference=previous.validate_reference

def validate_context(row, root=ROOT):
    if row.get('same_source_width_reference_id') is not None or row.get('independent_observation_count_claimed') is not False:raise ValueError('No width join or independent repeat established')
    case=row['source_case_id']
    if case=='caribbean-ru29-2024-local-westward-layers':
        data=json.loads((root/SERIES).read_bytes())
        if data['status']!='ACCEPTED_SOURCE_SPECIFIC_DIRECTIONAL_LAYER_DIAGNOSTICS':raise ValueError('Unreviewed layers')
        index={m['id']:(i,m) for i,m in enumerate(data['records'])}
        if row.get('measurement_id') not in index:raise ValueError('Unknown profile measurement')
        i,m=index[row['measurement_id']]; lower=m['velocity_defined_layer']['lower']
        required={'entity_id':'current:caribbean','metric':'velocity_layer_lower_boundary_depth','evidence_kind':'osw_derived_threshold_profile','approximate_value_m':lower['linear_crossing_m'],'id':m['id']+'-lower-crossing','measurement_file':SERIES,'measurement_pointer':f'/records/{i}','operator_file':OPERATOR,'operator_sha256':hashlib.sha256((root/OPERATOR).read_bytes()).hexdigest(),'discretization_bracket_m':lower['bracket_m'],'discretization_bracket_is_confidence_interval':False,'threshold_m_s':0.1,'minimum_support_bins':3,'depth_basis':'local_contiguous_westward_velocity_threshold_crossing','dataset_url':'https://doi.org/10.5281/zenodo.18332586'}
        required.update({k:m[k] for k in ['source_profile_index','latitude','longitude','transect_id','sampling_interval','source_reported_time','derived_representative_time']})
        if lower['status']!='bracketed' or m['central_threshold_m_s']!=0.1 or m['velocity_defined_layer']['support_bins']<3:raise ValueError('Unsupported lower crossing')
        for k,v in required.items():
            if row.get(k)!=v:raise ValueError('Derived profile join changed: '+k)
    elif case=='baffin-carroll-2018-arctic-water-band':
        required={'entity_id':'current:baffin','metric':'reported_flow_depth_band','evidence_kind':'published_literature_synthesis','range_m':[100,300],'water_mass_component':'Arctic_water','branch_section_scope':'partial_water_mass_component','depth_basis':'source_reported_water_mass_flow_band','section_sampling_month':None}
        for k,v in required.items():
            if row.get(k)!=v:raise ValueError('Baffin component band changed: '+k)
    else:raise ValueError('Unreviewed source case')

def build(root=ROOT):
    prior=previous.build(root)
    if prior!=json.loads((root/previous.OUTPUT).read_bytes()):raise ValueError('Prior register no longer reproduces')
    pins=dict(prior['input_sha256'])
    for p in [previous.OUTPUT,previous.CSV,'analysis/build_current_depth_register_v14.py',RULES,SOURCE,SERIES,OPERATOR,REVIEW]:
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
    return {'schema':'osw.current-depth-register.v15','status':'LOCAL_DERIVED_LAYERS_AND_COMPONENT_DEPTH_BAND',
            'rules_file':RULES,'generator_file':'analysis/build_current_depth_register_v15.py',
            'generator_sha256':hashlib.sha256((root/'analysis/build_current_depth_register_v15.py').read_bytes()).hexdigest(),
            'input_sha256':pins,'previous_evidence_preserved':evidence[:len(prior['evidence'])]==prior['evidence'],
            'counts':{'identities':111,'depth_references':len(evidence),'identities_with_scoped_depth_reference':owners,
                      'identities_not_yet_assessed':111-owners,'whole_route_depth_profiles':0,'volume_estimates':0},
            'metric_counts':dict(sorted(Counter(r['metric'] for r in evidence).items())),
            'coverage_interpretation':prior['coverage_interpretation']+' Local directional-layer crossings retain profile coordinates, sampling interval and pinned operator; they are not unique physical named-current boundaries. Component depth bands retain their water mass.',
            'records':records,'evidence':evidence,'runtime_changed':False,'full_goal_complete':False}


def csv_bytes(document):
    columns=next(csv.reader(io.StringIO(previous.csv_bytes(document).decode('utf8'))))
    columns += [p for p in ['measurement_id','measurement_file','measurement_pointer','operator_file','operator_sha256','source_profile_index','latitude','longitude','transect_id','sampling_interval','source_reported_time','derived_representative_time','threshold_m_s','minimum_support_bins','discretization_bracket_m','discretization_bracket_is_confidence_interval','water_mass_component','dataset_url'] if p not in columns]
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n',extrasaction='ignore');writer.writeheader()
    for raw in document['evidence']:
        row=dict(raw)
        if row.get('section_sampling_window'):
            row['section_window_start']=row['section_sampling_window']['start'];row['section_window_end']=row['section_sampling_window']['end']
        for key,value in list(row.items()):
            if isinstance(value,(dict,list)):row[key]=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        writer.writerow(row)
    return out.getvalue().encode('utf8')
