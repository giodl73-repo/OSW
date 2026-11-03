"""Append original interval-core minimum reaches from the exact audited report."""
import copy,hashlib,json
from pathlib import Path
import load_current_depth_reference_inventory_v7 as prior
from load_current_depth_reference_inventory_v8 import assemble,load_inventory,reference_csv_bytes,reference,source_context,context_id,eligible_records,SCHEMA

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-reference-inventory-operator-v8.json'
GENERATOR='analysis/build_current_depth_reference_inventory_v8.py'
INVENTORY='research/current-depth-reference-inventory-v8.json'
ADDENDUM='research/current-depth-reference-addenda/interval-primary-core-connected-reach-v1.json'
CSV='research/current-depth-reference-addenda/interval-primary-core-connected-reach-v1.csv'
REPORT='research/interval-core-connected-reach-source-report-v1.json'


def build(root=ROOT):
    reader=lambda f:(root/f).read_bytes();read=lambda f:json.loads(reader(f));op=read(OPERATOR)
    if any(op['eligibility'].values()):raise ValueError('No physical depth, identity, annual or volume promotion')
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(f)).hexdigest()!=pin:raise ValueError('Frozen interval admission input changed: '+f)
    previous=read(op['previous_inventory_file']);before=prior.load_inventory(previous,reader);parts=prior.read_parts(previous,reader);report=read(REPORT)
    if report['operator_sha256']!=hashlib.sha256(reader(report['operator_file'])).hexdigest():raise ValueError('Exact audited source operator required')
    for f,pin in report['input_sha256'].items():
        if hashlib.sha256(reader(f)).hexdigest()!=pin:raise ValueError('Exact source audit input required: '+f)
    encode=lambda value:(json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode();piece=lambda f,raw:{'file':f,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)};source=piece(REPORT,reader(REPORT));eligible=eligible_records(report)
    addendum={'schema':SCHEMA,'id':'interval-primary-core-connected-reach-v1','base_snapshot_sha256':previous['base']['json']['sha256'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256(reader(OPERATOR)).hexdigest(),'input_sha256':op['input_sha256'],'derived_source_report':source,'source_contexts':{context_id(r):source_context(r) for _,r in eligible},'evidence':[reference(r,p,source) for p,r in eligible],'runtime_changed':False,'full_goal_complete':False}
    assembled=assemble(*parts,[(addendum,report)]);add_raw=encode(addendum);csv_raw=reference_csv_bytes(addendum['evidence']);inventory=copy.deepcopy(previous);inventory.update(schema='osw.current-depth-reference-inventory.v8',status='PINNED_REFERENCES_WITH_INTERVAL_PRIMARY_CORE_MINIMUM_REACHES',counts=assembled['counts'],metric_counts=assembled['metric_counts']);inventory['addenda'].append({'id':addendum['id'],'json':piece(ADDENDUM,add_raw),'csv':piece(CSV,csv_raw)});inventory['view_metadata'].update(schema='osw.current-depth-reference-view.v8',status=inventory['status'],generator_file=GENERATOR,generator_sha256=hashlib.sha256(reader(GENERATOR)).hexdigest(),interpretation=op['interpretation'])
    pieces={INVENTORY:encode(inventory),ADDENDUM:add_raw,CSV:csv_raw}
    if any(len(raw)>=2500000 for raw in pieces.values()) or sum(map(len,pieces.values()))>=3000000:raise ValueError('Fixed publication caps exceeded')
    view=load_inventory(inventory,lambda f:pieces[f] if f in pieces else reader(f))
    if view['evidence'][:len(before['evidence'])]!=before['evidence']:raise ValueError('All prior references must remain unchanged')
    return inventory,addendum,report,pieces,view


def main():
    inventory,addendum,report,pieces,view=build();out=Path('current-depth-reference-inventory-v8');out.mkdir(exist_ok=True)
    for f,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv')]: (out/name).write_bytes(pieces[f])
    print(json.dumps({'counts':view['counts'],'new_core_connected_bounds':len(addendum['evidence']),'new_ocean_field_requests':0,'physical_current_bottom_established':False}))


if __name__=='__main__':main()
