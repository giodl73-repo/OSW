"""Admit a reviewed reported episodic water-mass scale, not a current bottom."""
import copy,hashlib,json
from pathlib import Path
import load_current_depth_reference_inventory_v8 as prior
from load_current_depth_reference_inventory_v9 import assemble,load_inventory,reference_csv_bytes,reference,source_context,validate_facts,SCHEMA,CONTEXT

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-reference-inventory-operator-v9.json'
GENERATOR='analysis/build_current_depth_reference_inventory_v9.py'
INVENTORY='research/current-depth-reference-inventory-v9.json'
ADDENDUM='research/current-depth-reference-addenda/jutland-nielsen2000-episodic-gbw-layer-v1.json'
CSV='research/current-depth-reference-addenda/jutland-nielsen2000-episodic-gbw-layer-v1.csv'
FACTS='research/jutland-nielsen2000-depth-profile-source-facts-v1.json'


def build(root=ROOT):
    reader=lambda f:(root/f).read_bytes();read=lambda f:json.loads(reader(f));op=read(OPERATOR)
    if any(op['eligibility'].values()):raise ValueError('No physical bottom, thickness, annual or volume promotion')
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(f)).hexdigest()!=pin:raise ValueError('Frozen episodic source admission input changed: '+f)
    previous=read(op['previous_inventory_file']);before=prior.load_inventory(previous,reader);parts=prior.read_parts(previous,reader);facts=read(FACTS);validate_facts(facts);review=read(op['source_review_file']);acquisition=read(facts['acquisition_file'])
    if review['facts_file']!=FACTS or review['facts_sha256']!=hashlib.sha256(reader(FACTS)).hexdigest() or review['original_pdf_pages_visually_reviewed']!=[74,75] or review['source_file']!=facts['source_pdf_file'] or review['source_sha256']!=facts['source_pdf_sha256'] or acquisition['sha256']!=facts['source_pdf_sha256'] or acquisition['bytes']!=facts['source_pdf_bytes']:raise ValueError('Exact original page-review and source custody metadata required')
    encode=lambda v:(json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode();piece=lambda f,raw:{'file':f,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)};source=piece(FACTS,reader(FACTS))
    addendum={'schema':SCHEMA,'id':'jutland-nielsen2000-episodic-gbw-layer-v1','base_snapshot_sha256':previous['base']['json']['sha256'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256(reader(OPERATOR)).hexdigest(),'input_sha256':op['input_sha256'],'reviewed_source_facts':source,'source_contexts':{CONTEXT:source_context(facts)},'evidence':[reference(facts,source)],'source_pdf_rehashed_in_cloud':False,'runtime_changed':False,'full_goal_complete':False}
    assembled=assemble(*parts,[(addendum,facts)]);add_raw=encode(addendum);csv_raw=reference_csv_bytes(addendum['evidence']);inventory=copy.deepcopy(previous);inventory.update(schema='osw.current-depth-reference-inventory.v9',status='PINNED_REFERENCES_WITH_REPORTED_EPISODIC_WATER_MASS_LAYER_SCALE',counts=assembled['counts'],metric_counts=assembled['metric_counts']);inventory['addenda'].append({'id':addendum['id'],'json':piece(ADDENDUM,add_raw),'csv':piece(CSV,csv_raw)});inventory['view_metadata'].update(schema='osw.current-depth-reference-view.v9',status=inventory['status'],generator_file=GENERATOR,generator_sha256=hashlib.sha256(reader(GENERATOR)).hexdigest(),interpretation=op['interpretation'])
    pieces={INVENTORY:encode(inventory),ADDENDUM:add_raw,CSV:csv_raw}
    if any(len(raw)>=2500000 for raw in pieces.values()) or sum(map(len,pieces.values()))>=3000000:raise ValueError('Fixed publication caps exceeded')
    view=load_inventory(inventory,lambda f:pieces[f] if f in pieces else reader(f))
    if view['evidence'][:len(before['evidence'])]!=before['evidence']:raise ValueError('All prior references must remain unchanged')
    return inventory,addendum,facts,pieces,view


def main():
    inventory,addendum,facts,pieces,view=build();out=Path('current-depth-reference-inventory-v9');out.mkdir(exist_ok=True)
    for f,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv')]: (out/name).write_bytes(pieces[f])
    print(json.dumps({'counts':view['counts'],'new_episodic_water_mass_scales':1,'supporting_composition_profile_rows':len(facts['source_profile']['rows']),'new_ocean_field_requests':0,'physical_current_bottom_established':False,'source_pdf_rehashed_in_cloud':False}))


if __name__=='__main__':main()
