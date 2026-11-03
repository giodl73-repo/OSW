"""Refresh member discovery against v36, retaining vertical-context semantics."""
import csv,hashlib,io,json
from pathlib import Path
import build_current_depth_projection_member_index_v1 as frozen
from load_current_depth_projection_inventory_v1 import load_inventory

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/current-depth-projection-member-index-operator-v2.json'
OUT=Path('current-depth-projection-member-index-v2')
CONTEXT_KEYS=['diagnostic_context_id','vertical_contexts_are_additive','contexts_are_independent_observations']


def index_view(manifest,view,source,membership,reader):
    index,report,csv_raw=frozen.index_view(manifest,view,source,membership,reader)
    by_id={c['id']:c for c in view['projections']+view['unresolved_reference_cases']}
    for parent in index['records']:
        for member in parent['members']:
            for ref in member['regional_projection_refs']+member['unresolved_reference_case_refs']:
                original=by_id[ref['case_id']]
                ref['case_scope'].update({k:original[k] for k in CONTEXT_KEYS if k in original})
    incoming=csv.DictReader(io.StringIO(csv_raw.decode('utf8')));fields=list(incoming.fieldnames)+CONTEXT_KEYS;rows=list(incoming)
    for row in rows:row.update({k:by_id[row['case_id']].get(k) for k in CONTEXT_KEYS})
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=fields,lineterminator='\n');writer.writeheader();writer.writerows(rows)
    return index,report,out.getvalue().encode('utf8')


def build(root=ROOT):
    reader=lambda f:(root/f).read_bytes();op=json.loads(reader(OPERATOR))
    if any(op['eligibility'].values()):raise ValueError('No parent measurement/runtime promotion')
    for f,pin in op['input_sha256'].items():
        if hashlib.sha256(reader(f)).hexdigest()!=pin:raise ValueError('Pinned member refresh input changed: '+f)
    manifest=json.loads(reader(op['projection_inventory_file']));source=json.loads(reader(op['member_reference_index_file']));membership=json.loads(reader(op['membership_file']))
    if source['membership_sha256']!=op['input_sha256'][op['membership_file']] or source['depth_register_sha256']!=op['input_sha256'][source['depth_register_file']]:raise ValueError('Existing member source pins changed')
    view=load_inventory(manifest,reader);index,report,csv_raw=index_view(manifest,view,source,membership,reader)
    for data in [index,report]:data.update(revision=2,previous_discovery_index_file=op['previous_discovery_index_file'],operator_file=OPERATOR,operator_sha256=hashlib.sha256(reader(OPERATOR)).hexdigest(),input_sha256=op['input_sha256'])
    return index,report,{'member-index.json':frozen.encoded(index),'gap-audit.json':frozen.encoded(report),'member-case-links.csv':csv_raw}


def main():
    index,report,pieces=build();OUT.mkdir(exist_ok=True)
    for name,raw in pieces.items():
        if len(raw)>=2500000:raise ValueError('Fixed per-file cap exceeded')
        (OUT/name).write_bytes(raw)
    print(json.dumps({'member_counts':index['counts'],'gap_counts':report['counts']}))


if __name__=='__main__':main()
