"""Append four provisional Alaska Coastal Current mean-flow reaches."""
import copy,hashlib,json
from pathlib import Path
import load_current_depth_reference_inventory_v17 as prior
import load_current_depth_reference_inventory_v18 as loader

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-reference-inventory-operator-v18.json'
GENERATOR='analysis/build_current_depth_reference_inventory_v18.py'
INVENTORY='research/current-depth-reference-inventory-v18.json'
ADDENDUM='research/current-depth-reference-addenda/alaska-jarosz2017-winter-mean-flow-reach-v1.json'
CSV='research/current-depth-reference-addenda/alaska-jarosz2017-winter-mean-flow-reach-v1.csv'


def build(root=ROOT):
    reader=lambda f:(root/f).read_bytes();read=lambda f:json.loads(reader(f));op=read(OPERATOR)
    if any(op['eligibility'].values()):raise ValueError('No physical/annual/volume/runtime promotion')
    for file,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(file)).hexdigest()!=pin:raise ValueError('Pinned reference input changed: '+file)
    previous=read(op['previous_inventory_file']);before=prior.load_inventory(previous,reader);parts=prior.read_parts(previous,reader);facts=read(loader.FACTS);loader.validate_facts(facts);review=read(op['source_review_file']);acquisition=read(facts['acquisition_result_file'])
    if review['facts_file']!=loader.FACTS or review['facts_sha256']!=hashlib.sha256(reader(loader.FACTS)).hexdigest() or review['primary_indexed_text_reviewed'] is not True or review['source_review_tier']!=loader.TIER or acquisition['status']!='FAILED_NOT_RETRIED' or acquisition['http_status']!=403 or acquisition['full_article_obtained'] is not False:raise ValueError('Honest provisional indexed-text review and original403 custody failure required')
    encode=lambda v:(json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode();piece=lambda f,raw:{'file':f,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)};source=piece(loader.FACTS,reader(loader.FACTS))
    addendum={'schema':loader.SCHEMA,'id':'alaska-jarosz2017-winter-mean-flow-reach-v1','base_snapshot_sha256':previous['base']['json']['sha256'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256(reader(OPERATOR)).hexdigest(),'input_sha256':op['input_sha256'],'reviewed_source_facts':source,'source_contexts':{loader.context_id(owner):loader.source_context(facts,owner) for owner in ['current:alaska-coastal-gulf']},'evidence':[loader.reference(facts,r,i,source) for i,r in enumerate(facts['records'])],'runtime_changed':False,'full_goal_complete':False}
    assembled=loader.assemble(*parts,[(addendum,facts)]);add_raw=encode(addendum);csv_raw=loader.reference_csv_bytes(addendum['evidence']);inventory=copy.deepcopy(previous);inventory.update(schema='osw.current-depth-reference-inventory.v18',status='PINNED_REFERENCES_WITH_PROVISIONAL_ALASKA_WINTER_MEAN_FLOW_REACHES',counts=assembled['counts'],metric_counts=assembled['metric_counts'],coordinate_unit_counts=assembled['coordinate_unit_counts']);inventory['addenda'].append({'id':addendum['id'],'json':piece(ADDENDUM,add_raw),'csv':piece(CSV,csv_raw)});inventory['view_metadata'].update(schema='osw.current-depth-reference-view.v18',status=inventory['status'],generator_file=GENERATOR,generator_sha256=hashlib.sha256(reader(GENERATOR)).hexdigest(),interpretation=op['interpretation'])
    pieces={INVENTORY:encode(inventory),ADDENDUM:add_raw,CSV:csv_raw}
    if any(len(raw)>=2500000 for raw in pieces.values()) or sum(map(len,pieces.values()))>=3000000:raise ValueError('Fixed publication caps exceeded')
    view=loader.load_inventory(inventory,lambda f:pieces[f] if f in pieces else reader(f))
    if view['evidence'][:len(before['evidence'])]!=before['evidence']:raise ValueError('Every prior reference must remain unchanged')
    return inventory,addendum,facts,pieces,view


if __name__=='__main__':
    inventory,addendum,facts,pieces,view=build();out=Path('current-depth-reference-inventory-v18');out.mkdir(exist_ok=True)
    for file,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv')]:(out/name).write_bytes(pieces[file])
    print(json.dumps({'counts':view['counts'],'new_provisional_mean_flow_reach_references':len(addendum['evidence']),'physical_current_bottom_established':False,'coordinate_unit_counts':view['coordinate_unit_counts'],'primary_indexed_text_reviewed':True,'new_ocean_field_requests':0}),flush=True)
