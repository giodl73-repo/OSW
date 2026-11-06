"""Admit five field-reproduced regional fresh/component depth descriptors."""
import copy,hashlib,json
from pathlib import Path
import load_current_depth_reference_inventory_v9 as prior
from load_current_depth_reference_inventory_v10 import assemble,load_inventory,reference_csv_bytes,reference,source_context,read_bundle,reproduce,SCHEMA,CONTEXT,DIRECTORY

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-reference-inventory-operator-v10.json'
GENERATOR='analysis/build_current_depth_reference_inventory_v10.py'
INVENTORY='research/current-depth-reference-inventory-v10.json'
ADDENDUM='research/current-depth-reference-addenda/ncc-original-core-fresh-component-depth-v1.json'
CSV='research/current-depth-reference-addenda/ncc-original-core-fresh-component-depth-v1.csv'
REPORT=DIRECTORY+'source-report.json'
ORIGINAL='research/interval-core-connected-reach-source-report-v1.json'


def build(root=ROOT):
    reader=lambda f:(root/f).read_bytes();read=lambda f:json.loads(reader(f));op=read(OPERATOR)
    if any(op['eligibility'].values()):raise ValueError('No physical/annual/route/volume promotion')
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(f)).hexdigest()!=pin:raise ValueError('Frozen conditional depth input changed: '+f)
    previous=read(op['previous_inventory_file']);before=prior.load_inventory(previous,reader);parts=prior.read_parts(previous,reader)
    encode=lambda v:(json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode();piece=lambda f,raw:{'file':f,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    addendum={'schema':SCHEMA,'id':'ncc-original-core-fresh-component-depth-v1','base_snapshot_sha256':previous['base']['json']['sha256'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256(reader(OPERATOR)).hexdigest(),'input_sha256':op['input_sha256'],'derived_source_report':piece(REPORT,reader(REPORT)),'original_velocity_audit_report':piece(ORIGINAL,reader(ORIGINAL)),'source_contexts':{CONTEXT:source_context()},'runtime_changed':False,'full_goal_complete':False}
    bundle=read_bundle(addendum,reader);records=reproduce(bundle);addendum['evidence']=[reference(r,i,{**bundle['report']['profiles'][i],'file':DIRECTORY+bundle['report']['profiles'][i]['file']},addendum['derived_source_report']) for i,r in enumerate(records)]
    assembled=assemble(*parts,[(addendum,bundle)]);add_raw=encode(addendum);csv_raw=reference_csv_bytes(addendum['evidence']);inventory=copy.deepcopy(previous);inventory.update(schema='osw.current-depth-reference-inventory.v10',status='PINNED_REFERENCES_WITH_REPRODUCED_CONDITIONAL_FRESH_COMPONENT_DEPTHS',counts=assembled['counts'],metric_counts=assembled['metric_counts']);inventory['addenda'].append({'id':addendum['id'],'json':piece(ADDENDUM,add_raw),'csv':piece(CSV,csv_raw)});inventory['view_metadata'].update(schema='osw.current-depth-reference-view.v10',status=inventory['status'],generator_file=GENERATOR,generator_sha256=hashlib.sha256(reader(GENERATOR)).hexdigest(),interpretation=op['interpretation'])
    pieces={INVENTORY:encode(inventory),ADDENDUM:add_raw,CSV:csv_raw}
    if any(len(raw)>=2500000 for raw in pieces.values()) or sum(map(len,pieces.values()))>=3000000:raise ValueError('Fixed publication caps exceeded')
    view=load_inventory(inventory,lambda f:pieces[f] if f in pieces else reader(f))
    if view['evidence'][:len(before['evidence'])]!=before['evidence']:raise ValueError('Every prior reference must remain unchanged')
    return inventory,addendum,bundle,pieces,view


def main():
    inventory,addendum,bundle,pieces,view=build();out=Path('current-depth-reference-inventory-v10');out.mkdir(exist_ok=True)
    for f,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv')]: (out/name).write_bytes(pieces[f])
    print(json.dumps({'counts':view['counts'],'reproduced_native_field_descriptors':len(addendum['evidence']),'new_ocean_field_requests':0,'physical_current_bottom_established':False}))


if __name__=='__main__':main()
