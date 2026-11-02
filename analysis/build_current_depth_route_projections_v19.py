"""New current addendum using the frozen source-to-reference projection method."""
import copy
import hashlib
import json
from pathlib import Path
from build_current_depth_route_projections_v18 import full_section_cases,reference_placeholder,INTERIOR
from build_current_depth_route_projections_v12 import GEOD
from build_current_depth_route_projections_v15 import encoded,sample_csv_bytes
from load_current_depth_projection_inventory_v1 import read_parts,assemble,load_inventory

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-route-projection-operator-v19.json'
GENERATOR='analysis/build_current_depth_route_projections_v19.py'
INVENTORY='research/current-depth-route-projection-inventory-v5.json'
ADDENDUM='research/current-depth-route-projection-addenda/nec-subarctic-full-sections-hycom2022-v1.json'
SAMPLES_CSV='research/current-depth-route-projection-addenda/nec-subarctic-full-sections-hycom2022-v1.csv'


def build(root=ROOT):
    reader=lambda p:(root/p).read_bytes();read=lambda p:json.loads(reader(p));op=read(OPERATOR)
    for p,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(p)).hexdigest()!=pin:raise ValueError('Frozen source changed: '+p)
    if any(op['eligibility'].values()):raise ValueError('No physical promotion')
    previous=read(op['previous_inventory_file']);base,prior_addenda=read_parts(previous,reader)
    load_inventory(previous,reader)
    projections,blocked=full_section_cases(read(op['source_facts_file']),{p:read(p) for p in op['section_files']},op)
    for case in projections+blocked:case['source_surface_component_gate_m_s']=op['currents'][case['entity_id']]['surface_component_gate_m_s']
    addendum={'schema':'osw.current-depth-route-projection-addendum.v1','id':'nec-subarctic-full-sections-hycom2022-v1',
        'base_snapshot_sha256':previous['base']['json']['sha256'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256(reader(OPERATOR)).hexdigest(),
        'input_sha256':op['input_sha256'],'projections':projections,'unresolved_reference_cases':blocked,
        'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}
    add_raw=encoded(addendum);csv_raw=sample_csv_bytes(projections,reader(previous['base']['csv']['file']))
    pieces={ADDENDUM:add_raw,SAMPLES_CSV:csv_raw}
    piece=lambda f,raw:{'file':f,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    manifest=copy.deepcopy(previous);manifest['addenda'].append({'id':addendum['id'],'json':piece(ADDENDUM,add_raw),'csv':piece(SAMPLES_CSV,csv_raw)})
    manifest['counts']=assemble(base,prior_addenda+[addendum])['counts']
    manifest['view_metadata'].update(schema='osw.current-depth-route-projections.v19',status='REGIONAL_DEPTH_BASE_PLUS_PINNED_CURRENT_ADDENDA',generator_file=GENERATOR,generator_sha256=hashlib.sha256(reader(GENERATOR)).hexdigest(),interpretation=op['interpretation'])
    pieces[INVENTORY]=encoded(manifest)
    result=load_inventory(manifest,lambda p:pieces[p] if p in pieces else reader(p))
    return manifest,addendum,pieces,result


def main():
    manifest,addendum,pieces,result=build();out=Path('current-depth-route-projections-v19');out.mkdir(exist_ok=True)
    for path,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(SAMPLES_CSV,'samples.csv')]:
        if len(pieces[path])>=2500000:raise ValueError('Fixed per-file publication cap exceeded')
        (out/name).write_bytes(pieces[path])
    print(json.dumps(result['counts']))


if __name__=='__main__':main()
