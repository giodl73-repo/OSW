"""Admit only new full-cohort descriptors and record exact prior-reference reuse."""
import copy,hashlib,json
from pathlib import Path
import load_current_depth_reference_inventory_v11 as prior
from load_current_depth_reference_inventory_v12 import assemble,load_inventory,reference_csv_bytes,read_bundle,admission,context_id,context,SCHEMA,DIRECTORY

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-reference-inventory-operator-v12.json'
GENERATOR='analysis/build_current_depth_reference_inventory_v12.py'
INVENTORY='research/current-depth-reference-inventory-v12.json'
ADDENDUM='research/current-depth-reference-addenda/coastal-full-section-fresh-depths-v1.json'
CSV='research/current-depth-reference-addenda/coastal-full-section-fresh-depths-v1.csv'
AUDIT='research/coastal-full-section-fresh-depth-reference-admission-report-v1.json'
REPORT=DIRECTORY+'source-report.json'
SOURCE_OPERATOR='research/coastal-full-section-salinity-operator-v1.json'
ORIGINAL='research/interval-core-connected-reach-source-report-v1.json'


def build(root=ROOT):
    reader=lambda f:(root/f).read_bytes();read=lambda f:json.loads(reader(f));op=read(OPERATOR)
    if any(op['eligibility'].values()):raise ValueError('No physical bottom,annual,volume or source-query promotion')
    for file,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(file)).hexdigest()!=pin:raise ValueError('Frozen full-cohort admission input changed: '+file)
    previous=read(op['previous_inventory_file']);before=prior.load_inventory(previous,reader);parts=prior.read_parts(previous,reader)
    encode=lambda v:(json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode();piece=lambda f,raw:{'file':f,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    addendum={'schema':SCHEMA,'id':'coastal-full-section-fresh-depths-v1','base_snapshot_sha256':previous['base']['json']['sha256'],'operator_file':OPERATOR,'operator_sha256':hashlib.sha256(reader(OPERATOR)).hexdigest(),'input_sha256':op['input_sha256'],'source_operator':piece(SOURCE_OPERATOR,reader(SOURCE_OPERATOR)),'derived_source_report':piece(REPORT,reader(REPORT)),'original_velocity_audit_report':piece(ORIGINAL,reader(ORIGINAL)),'runtime_changed':False,'full_goal_complete':False}
    bundle=read_bundle(addendum,reader);rows,audit=admission(before,bundle,addendum);addendum['evidence']=rows;addendum['source_contexts']={context_id(r['entity_id']):context(r['entity_id']) for r in rows};audit_raw=encode(audit);addendum['reference_admission_report']=piece(AUDIT,audit_raw);bundle['admission_report']=audit
    assembled=assemble(*parts,[(addendum,bundle)]);add_raw=encode(addendum);csv_raw=reference_csv_bytes(rows);inventory=copy.deepcopy(previous);inventory.update(schema='osw.current-depth-reference-inventory.v12',status='PINNED_REFERENCES_WITH_DEDUPLICATED_FULL_COASTAL_FRESH_DEPTHS',counts=assembled['counts'],metric_counts=assembled['metric_counts']);inventory['addenda'].append({'id':addendum['id'],'json':piece(ADDENDUM,add_raw),'csv':piece(CSV,csv_raw)});inventory['view_metadata'].update(schema='osw.current-depth-reference-view.v12',status=inventory['status'],generator_file=GENERATOR,generator_sha256=hashlib.sha256(reader(GENERATOR)).hexdigest(),interpretation=op['interpretation'])
    pieces={INVENTORY:encode(inventory),ADDENDUM:add_raw,CSV:csv_raw,AUDIT:audit_raw}
    if any(len(raw)>=2500000 for raw in pieces.values()) or sum(map(len,pieces.values()))>=3000000:raise ValueError('Fixed publication caps exceeded')
    view=load_inventory(inventory,lambda f:pieces[f] if f in pieces else reader(f))
    if view['evidence'][:len(before['evidence'])]!=before['evidence']:raise ValueError('Every prior reference must remain unchanged')
    return inventory,addendum,bundle,pieces,view


def main():
    inventory,addendum,bundle,pieces,view=build();out=Path('current-depth-reference-inventory-v12');out.mkdir(exist_ok=True)
    for file,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv'),(AUDIT,'admission-report.json')]: (out/name).write_bytes(pieces[file])
    audit=bundle['admission_report'];print(json.dumps({'counts':view['counts'],'original_cases_reproduced':audit['original_cases_reproduced'],'new_descriptors':len(addendum['evidence']),'existing_references_reused_unchanged':len(audit['reused_reference_ids']),'new_ocean_field_requests':0,'physical_current_bottom_established':False}))


if __name__=='__main__':main()
