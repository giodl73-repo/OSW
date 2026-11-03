"""Build northward NCC reference inventory and exact spatial admission report."""
import copy,hashlib,json
from pathlib import Path
import load_current_depth_reference_inventory_v12 as prior
import load_current_depth_reference_inventory_v13 as loader

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-reference-inventory-operator-v13.json'
GENERATOR='analysis/build_current_depth_reference_inventory_v13.py'
INVENTORY='research/current-depth-reference-inventory-v13.json'
ADDENDUM='research/current-depth-reference-addenda/ncc-north-joint-fresh-depths-v1.json'
CSV='research/current-depth-reference-addenda/ncc-north-joint-fresh-depths-v1.csv'
SPATIAL='research/ncc-north-depth-reference-spatial-admission-report-v1.json'


def build(root=ROOT):
    reader=lambda f:(root/f).read_bytes();read=lambda f:json.loads(reader(f));op=read(OPERATOR)
    if any(op['eligibility'].values()):raise ValueError('No physical bottom,annual,volume or source-query promotion')
    for file,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(file)).hexdigest()!=pin:raise ValueError('Frozen northward admission input changed: '+file)
    previous=read(op['previous_inventory_file']);before=prior.load_inventory(previous,reader);parts=prior.read_parts(previous,reader)
    encode=lambda v:(json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode();piece=lambda f,raw:{'file':f,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    addendum={'schema':loader.SCHEMA,'id':'ncc-north-joint-fresh-depths-v1','base_snapshot_sha256':previous['base']['json']['sha256'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256(reader(OPERATOR)).hexdigest(),'input_sha256':op['input_sha256'],'source_operator':piece(loader.native.OPERATOR,reader(loader.native.OPERATOR)),'derived_source_report':piece(loader.native.REPORT,reader(loader.native.REPORT)),'runtime_changed':False,'full_goal_complete':False}
    bundle=loader.native.read_bundle(reader);rows,report=loader.admission(before,bundle,addendum);addendum['evidence']=rows;addendum['source_contexts']={loader.CONTEXT:loader.source_context()};report_raw=encode(report);addendum['spatial_admission_report']=piece(SPATIAL,report_raw);bundle['spatial_admission_report']=report
    assembled=loader.assemble(*parts,[(addendum,bundle)]);add_raw=encode(addendum);csv_raw=loader.reference_csv_bytes(rows);inventory=copy.deepcopy(previous);inventory.update(schema='osw.current-depth-reference-inventory.v13',status='PINNED_REFERENCES_WITH_REPRODUCED_NORTHWARD_COASTAL_DEPTHS',counts=assembled['counts'],metric_counts=assembled['metric_counts']);inventory['addenda'].append({'id':addendum['id'],'json':piece(ADDENDUM,add_raw),'csv':piece(CSV,csv_raw)});inventory['view_metadata'].update(schema='osw.current-depth-reference-view.v13',status=inventory['status'],generator_file=GENERATOR,generator_sha256=hashlib.sha256(reader(GENERATOR)).hexdigest(),interpretation=op['interpretation'])
    pieces={INVENTORY:encode(inventory),ADDENDUM:add_raw,CSV:csv_raw,SPATIAL:report_raw}
    if any(len(raw)>=2500000 for raw in pieces.values()) or sum(map(len,pieces.values()))>=3000000:raise ValueError('Fixed publication caps exceeded')
    view=loader.load_inventory(inventory,lambda f:pieces[f] if f in pieces else reader(f))
    if view['evidence'][:len(before['evidence'])]!=before['evidence']:raise ValueError('Every prior reference must remain unchanged')
    return inventory,addendum,bundle,pieces,view


def main():
    inventory,addendum,bundle,pieces,view=build();out=Path('current-depth-reference-inventory-v13');out.mkdir(exist_ok=True)
    for file,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv'),(SPATIAL,'spatial-admission-report.json')]:(out/name).write_bytes(pieces[file])
    print(json.dumps({'counts':view['counts'],'spatial_counts':bundle['spatial_admission_report']['counts'],'new_ocean_field_requests':0}))


if __name__=='__main__':main()
