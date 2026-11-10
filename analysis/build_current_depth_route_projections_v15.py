"""North Brazil full-section profiles in a pinned base/addendum inventory."""
import copy
import csv
import hashlib
import io
import json
import math
from pathlib import Path
from build_current_depth_route_projections_v12 import GEOD, paired_anchor, project
from load_current_depth_projection_inventory_v1 import assemble, load_inventory

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-route-projection-operator-v15.json'
GENERATOR='analysis/build_current_depth_route_projections_v15.py'
INVENTORY='research/current-depth-route-projection-inventory-v1.json'
ADDENDUM='research/current-depth-route-projection-addenda/north-brazil-full-sections-hycom2022-v1.json'
SAMPLES_CSV='research/current-depth-route-projection-addenda/north-brazil-full-sections-hycom2022-v1.csv'


def encoded(value):
    return (json.dumps(value,indent=2,allow_nan=False)+'\n').encode('utf8')


def full_section_cases(facts,chunks,op):
    keyed={}
    for index,row in enumerate(facts['descriptors']):
        key=row['snapshot_time_utc'],row['section_id']
        if key in keyed:raise ValueError('Duplicate original source section/date')
        keyed[key]=index,row
    expected={(t,s) for t in op['snapshot_times_utc'] for s in op['section_ids']}
    if set(keyed)!=expected:raise ValueError('All fourteen source section/date cases required')
    cases=[]
    for stamp in op['snapshot_times_utc']:
        anchors=[];distance=0.;previous=None
        for section_id in op['section_ids']:
            index,row=keyed[stamp,section_id];source=chunks[row['source_file']]
            column_index=row['selected_column_index'];profile=source['columns'][column_index];diagnosis=source['diagnosis']
            if (source['entity_id']!='current:north-brazil' or source['snapshot_time_utc']!=stamp
                or source['section_definition']['id']!=section_id or source['component_bearing_degrees_true']!=315
                or row['component_bearing_degrees_true']!=315 or row['source_sha256']!=op['input_sha256'][row['source_file']]
                or row['source_profile_pointer']!='/columns/'+str(column_index) or row['source_diagnosis_pointer']!='/diagnosis'
                or diagnosis['selected_column_index']!=column_index or row['selected_lon_lat']!=profile['sampled_lon_lat']
                or row['section_definition']!=source['section_definition']
                or row['horizontal_selection_status']!=diagnosis['horizontal_selection_status']
                or row['selected_column_threshold_layers']!=diagnosis['selected_column_threshold_layers']):raise ValueError('Source section, frame, selection, pointer or depth changed')
            layers=row['selected_column_threshold_layers'];matches=[r for r in layers if r['threshold_m_s']==.1]
            if len(matches)!=1:raise ValueError('Exactly one source primary10cm/s layer required')
            layer=matches[0]
            if layer['lower_depth_m']!=row['primary10cms_lower_depth_m'] or layer['layer_thickness_m']!=row['primary10cms_layer_thickness_m']:raise ValueError('Source primary lower depth/span changed')
            point=row['selected_lon_lat']
            if previous is not None:
                metres=GEOD.inv(*previous,*point)[2]
                if not math.isfinite(metres) or metres<=0:raise ValueError('Distinct finite original section positions required')
                distance+=metres/1000
            previous=point;reasons=[]
            if row['horizontal_selection_status']!='interior_section_integral_maximum_with_finite_neighbors_not_independently_validated_axis':reasons.append('section_axis_proxy_not_interior_bracketed')
            if layer['lower_depth_m'] is None:reasons.append('primary10cms_lower_boundary_censored_or_unresolved')
            lower=not reasons;thickness=lower and layer['layer_thickness_m'] is not None
            anchors.append(paired_anchor('north-brazil-full-sections-'+stamp[:10]+'-'+section_id,layer,lower,thickness,reasons,
                source_section_id=section_id,distance_km=round(distance,6),reference_lon_lat=point,
                selected_model_node_lon_lat=point,source_native_longitude_degrees_east=profile['native_source_longitude_degrees_east'],
                source_horizontal_selection_status=row['horizontal_selection_status'],source_component_bearing_degrees_true=315,
                source_profile_refs=[op['source_facts_file']+'#/descriptors/'+str(index)],
                source_model_profile_ref=row['source_file']+'#'+row['source_profile_pointer'],
                source_connected_diagnosis_ref=row['source_file']+'#/diagnosis/selected_column_threshold_layers/'+str(layers.index(layer)),
                source_section_definition=row['section_definition'],source_candidate_count=row['candidate_count'],
                source_local_integral_maximum_indices=row['local_integral_maximum_indices']))
        raw={'entity_id':'current:north-brazil','snapshot_time_utc':stamp,'primary_threshold_m_s':.1,'anchors':anchors,
            'geometry_role':'shortest_geodesic_connector_between_full_section_model_axis_proxies_not_observed_current_axis',
            'route_id':'north-brazil-full-section-axis-proxy-'+stamp[:10],'route_file':None,
            'source_time_basis':'HYCOM00Z2022instantaneous full sections;fixed315degree northwest component and complete surface-connected0–200m integral selector. Two snapshots are not an annual cycle or observed monthly means.',
            'projection_gate':'Interior full-section integral maximum with finite neighboring upper-layer support and resolved primary10cm/s lower contour; no independent named-current-axis validation.',
            'source_component_reference_frame':'fixed_geographic_315degree_true_northwest_held_through_depth',
            'earlier_unresolved_pilot_case_id':'north-brazil-hycom-'+stamp[:10]+'-regional-depth-v1',
            'method_frame_differs_from_earlier_corridor_pilot':True}
        case=project(raw,op)
        case['id']='north-brazil-full-sections-'+stamp[:10]+'-nw315-v1'
        if not any(a['lower_projection_eligible'] for a in anchors):raise ValueError('No supported regional projection; retain source as unresolved instead')
        cases.append(case)
    return cases


def sample_csv_bytes(projections,base_csv):
    reader=csv.DictReader(io.StringIO(base_csv.decode('utf8')));columns=list(reader.fieldnames);rows=[]
    for p in projections:
        for sample in p['samples']:
            row=copy.deepcopy(sample);point=row.pop('nominal_reference_connector_lon_lat')
            row.update(projection_id=p['id'],entity_id=p['entity_id'],route_id=p['route_id'],geometry_role=p['geometry_role'],
                metric=p['metric'],vertical_datum=p['vertical_datum'],snapshot_time_utc=p['snapshot_time_utc'],
                longitude=point[0],latitude=point[1],primary_threshold_m_s=p['primary_threshold_m_s'],
                model_layer_thickness_datum=p['model_layer_thickness_datum'],source_time_basis=p['source_time_basis'],
                source_component_reference_frame=p['source_component_reference_frame'],interpolation_assumption=p['interpolation_assumption'])
            for k,v in row.items():
                if k not in columns:columns.append(k)
                if isinstance(v,(dict,list)):row[k]=json.dumps(v,separators=(',',':'))
            rows.append(row)
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows)
    return out.getvalue().encode('utf8')


def build(root=ROOT):
    read=lambda p:json.loads((root/p).read_bytes());op=read(OPERATOR)
    for file,pin in op['input_sha256'].items():
        if hashlib.sha256((root/file).read_bytes()).hexdigest()!=pin:raise ValueError('Frozen source changed: '+file)
    if any(op['eligibility'].values()):raise ValueError('No physical promotion')
    base=read(op['base_projection_file']);facts=read(op['source_facts_file'])
    chunks={p:read(p) for p in op['section_files']};projections=full_section_cases(facts,chunks,op)
    addendum={'schema':'osw.current-depth-route-projection-addendum.v1','id':'north-brazil-full-sections-hycom2022-v1',
        'base_snapshot_sha256':op['input_sha256'][op['base_projection_file']],
        'operator_file':OPERATOR,'operator_sha256':hashlib.sha256((root/OPERATOR).read_bytes()).hexdigest(),
        'input_sha256':op['input_sha256'],'projections':projections,'unresolved_reference_cases':[],
        'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}
    add_raw=encoded(addendum);csv_raw=sample_csv_bytes(projections,(root/op['base_projection_csv']).read_bytes())
    pieces={ADDENDUM:add_raw,SAMPLES_CSV:csv_raw}
    piece=lambda file,raw:{'file':file,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    logical=assemble(base,[addendum])
    manifest={'schema':'osw.current-depth-route-projection-inventory.v1','status':'PINNED_BASE_AND_ADDITIVE_REGIONAL_DEPTH_PROFILES',
        'base':{'json':piece(op['base_projection_file'],(root/op['base_projection_file']).read_bytes()),
                'csv':piece(op['base_projection_csv'],(root/op['base_projection_csv']).read_bytes()),
                'unresolved_csv':piece(op['base_unresolved_csv'],(root/op['base_unresolved_csv']).read_bytes())},
        'addenda':[{'id':addendum['id'],'json':piece(ADDENDUM,add_raw),'csv':piece(SAMPLES_CSV,csv_raw)}],
        'counts':logical['counts'],'view_metadata':{'schema':'osw.current-depth-route-projections.v15',
            'status':'REGIONAL_DEPTH_BASE_PLUS_NORTH_BRAZIL_FULL_SECTION_ADDENDUM',
            'generator_file':GENERATOR,'generator_sha256':hashlib.sha256((root/GENERATOR).read_bytes()).hexdigest(),
            'interpretation':op['interpretation'],'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False},
        'integrity_scope':'Loader checks the exact base/addendum JSON and CSV bytes, case ownership, duplicate IDs and reconstructed counts. Source-field/operator verification is retained in the pinned source/addendum reviews; loading does not rerun ocean-field validation.',
        'publication_policy':'Immutable pieces remain below fixed per-file caps;add new current addenda without rewriting the frozen base. No full expanded JSON copy is published.',
        'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}
    pieces[INVENTORY]=encoded(manifest)
    reader=lambda file:pieces[file] if file in pieces else (root/file).read_bytes()
    view=load_inventory(manifest,reader)
    return manifest,addendum,pieces,view


def main():
    manifest,addendum,pieces,view=build();out=Path('current-depth-route-projections-v15');out.mkdir(exist_ok=True)
    for path,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(SAMPLES_CSV,'samples.csv')]:
        if len(pieces[path])>=2500000:raise ValueError('Fixed per-file publication cap exceeded')
        (out/name).write_bytes(pieces[path])
    print(json.dumps(view['counts']))


if __name__=='__main__':main()
