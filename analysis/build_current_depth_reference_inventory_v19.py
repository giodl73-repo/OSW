"""Append two PGW core-depth regimes and preserve source-named downstream context."""
import copy,hashlib,json
from pathlib import Path
import load_current_depth_reference_inventory_v18 as prior
import load_current_depth_reference_inventory_v19 as loader

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-reference-inventory-operator-v19.json'
GENERATOR='analysis/build_current_depth_reference_inventory_v19.py'
INVENTORY='research/current-depth-reference-inventory-v19.json'
ADDENDUM='research/current-depth-reference-addenda/pgw-pous-2004-core-depth-regimes-v1.json'
CSV='research/current-depth-reference-addenda/pgw-pous-2004-core-depth-regimes-v1.csv'


def build(root=ROOT):
    reader=lambda f:(root/f).read_bytes();read=lambda f:json.loads(reader(f));op=read(OPERATOR)
    if any(op['eligibility'].values()):raise ValueError('No physical/annual/volume/runtime promotion')
    for file,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(file)).hexdigest()!=pin:raise ValueError('Pinned reference input changed: '+file)
    previous=read(op['previous_inventory_file']);before=prior.load_inventory(previous,reader);parts=prior.read_parts(previous,reader);facts=read(loader.FACTS);loader.validate_facts(facts)
    encode=lambda v:(json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode();piece=lambda f,raw:{'file':f,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)};source=piece(loader.FACTS,reader(loader.FACTS))
    addendum={'schema':loader.SCHEMA,'id':'pgw-pous-2004-core-depth-regimes-v1','base_snapshot_sha256':previous['base']['json']['sha256'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256(reader(OPERATOR)).hexdigest(),'input_sha256':op['input_sha256'],'reviewed_source_facts':source,'source_contexts':{loader.context_id(owner):loader.source_context(facts,owner) for owner in [loader.OWNER]},'evidence':[loader.reference(facts,r,i,source) for i,r in enumerate(facts['records'])],'runtime_changed':False,'full_goal_complete':False}
    assembled=loader.assemble(*parts,[(addendum,facts)]);add_raw=encode(addendum);csv_raw=loader.reference_csv_bytes(addendum['evidence']);inventory=copy.deepcopy(previous);inventory.update(schema='osw.current-depth-reference-inventory.v19',status='PINNED_REFERENCES_WITH_PGW_SOURCE_NAMED_DEPTH_PROGRESSION',counts=assembled['counts'],metric_counts=assembled['metric_counts'],coordinate_unit_counts=assembled['coordinate_unit_counts']);inventory['addenda'].append({'id':addendum['id'],'json':piece(ADDENDUM,add_raw),'csv':piece(CSV,csv_raw)});inventory['view_metadata'].update(schema='osw.current-depth-reference-view.v19',status=inventory['status'],generator_file=GENERATOR,generator_sha256=hashlib.sha256(reader(GENERATOR)).hexdigest(),interpretation=op['interpretation'])
    pieces={INVENTORY:encode(inventory),ADDENDUM:add_raw,CSV:csv_raw}
    if any(len(raw)>=2500000 for raw in pieces.values()) or sum(map(len,pieces.values()))>=3000000:raise ValueError('Fixed publication caps exceeded')
    view=loader.load_inventory(inventory,lambda f:pieces[f] if f in pieces else reader(f))
    if view['evidence'][:len(before['evidence'])]!=before['evidence']:raise ValueError('Every prior reference must remain unchanged')
    return inventory,addendum,facts,pieces,view


if __name__=='__main__':
    inventory,addendum,facts,pieces,view=build();out=Path('current-depth-reference-inventory-v19');out.mkdir(exist_ok=True)
    for file,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv')]:(out/name).write_bytes(pieces[file])
    print(json.dumps({'counts':view['counts'],'new_regional_core_depth_references':len(addendum['evidence']),'physical_current_bottom_established':False,'coordinate_unit_counts':view['coordinate_unit_counts'],'primary_publisher_prose_reviewed':True,'new_ocean_field_requests':0}),flush=True)
