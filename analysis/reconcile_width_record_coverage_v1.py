"""Count source-owned width rows separately from dashboard candidate capabilities.

Reads only retained source documents and compact compiler metadata, never a
query packet, source index, WASM binary or engine archive.
"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FILE='research/current-width-record-owner-reconciliation-v1.json'
BASE_SHA256='929527ad7c4a500eca26d495c59e6eadd3d62e82b3bc9b9cd1ff57084b1aacb8'
GROUPS=[
 ('research/ocean-current-width-inventory.json','/measurements'),
 ('research/southern-east-madagascar-prose-dimension-admissions.json','/width_record'),
 ('research/agulhas-krug-2012-core-widths-source-facts-v1.json','/records'),
 ('research/wicc-vinayachandran-2021-surface-width-source-facts-v1.json','/records/0'),
 ('research/eacc-dekeyzer-2012-cited-width-lower-bound-source-facts-v1.json','/records/0'),
 ('research/eicc-t24-published-width-admission-v1.json','/width_record'),
 ('research/davidson-wallace-2008-width-admission-v1.json','/width_record'),
 ('research/agulhas-vinayachandran-2021-reported-dimensions.json','/width_record'),
 ('research/norwegian-atlantic-slope-working-admission.json','/width_records'),
 ('research/hansen-2011-asar-surface-width-admissions.json','/width_records'),
 ('research/neuc-glider-2015-width-admissions.json','/width_records'),
 ('research/aleutian-onishi-2001-width-admission.json','/width_records'),
 ('research/madagascar-dimensions-query-contract-v1.json','/width_record'),
 ('research/azcc-onken-query-contract-v1.json','/width_record'),
 ('research/pacific-nec-nominal-width-query-contract-v1.json','/width_record'),
 ('research/dimoune-2023-width-query-contract-v2.json','/width_records'),
 ('research/atlantic-nec-stramma-2005-query-contract-v1.json','/width_records'),
 ('research/pacific-sec-gourdeau-2008-query-contract-v1.json','/width_records'),
 ('research/current-core-dimensions-query-contract-v1.json','/width_records'),
]

def read(path):return json.loads((ROOT/path).read_bytes())
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

def reconcile(records,decisions,dashboard_entries):
    identities={row['current_id'] for row in decisions}
    if len(identities)!=len(decisions):raise ValueError('Duplicate current identity')
    owned={current:[] for current in identities};seen=set()
    for row in records:
        if not isinstance(row.get('id'),str) or not row['id'] or row['id'] in seen:raise ValueError('Missing or duplicate width row ID')
        if row.get('current_id') not in identities:raise ValueError('Width row has no accepted owner')
        seen.add(row['id']);owned[row['current_id']].append(row['id'])
    owners={current for current,ids in owned.items() if ids}
    capability_only=sorted({row['id'].removeprefix('current:') for row in dashboard_entries if row.get('type')=='named_current'
        and row.get('capabilities',{}).get('scoped_width',0)>0}-owners)
    if any(current not in identities for current in capability_only):raise ValueError('Unknown dashboard capability owner')
    decisions=[{**row,'measurement_ids':owned[row['current_id']],
        'width_decision':'scoped_width_evidence_present' if owned[row['current_id']] else row.get('width_decision','width_not_assessed')} for row in decisions]
    return {'counts':{'current_identities':len(identities),'scoped_width_records':len(records),
        'owners_with_admitted_scoped_width_records':len(owners),'identities_without_admitted_scoped_width_records':len(identities-owners),
        'owners_with_broader_dashboard_width_capability':len(owners|set(capability_only)),
        'dashboard_capability_only_owners':len(capability_only)},
        'capability_only_current_ids':capability_only,'current_decisions':decisions}

def build():
    base=read(GROUPS[0][0]);decisions=list(base['current_decisions']);pins={}
    identity=read('research/ocean-current-identity-admissions.json')
    admissions=list(identity['entries'])+[read('research/norwegian-atlantic-slope-working-admission.json')['identity_entry']]
    admissions+=read('research/indian-current-identity-query-contract-v1.json')['additions']['current_identity_admissions']
    for row in admissions:decisions.append({'current_id':row['proposal_id'],'name':row['entity']['label'],'width_decision':'width_not_assessed'})
    for row in read('research/equatorial-basin-identity-query-contract-v3.json')['additions']['objects']:
        decisions.append({'current_id':row['id'].removeprefix('current:'),'name':row['label'],'width_decision':'width_not_assessed'})
    groups=[];records=[];inventory=read('research/current-validation-reuse-delivery-run-v1/compile-inventory.json')['compile_time_data_sha256']
    for path,pointer in GROUPS:
        value=read(path)
        for token in pointer.strip('/').split('/'):value=value[int(token)] if isinstance(value,list) else value[token]
        rows=value if isinstance(value,list) else [value]
        pins[path]=sha(path)
        # The historical base is carried as authenticated runtime source bytes,
        # rather than a Rust include_str dependency. Browser acceptance checks
        # its actual receipt hash and all190 displayed row IDs/owners as well.
        expected=BASE_SHA256 if path==GROUPS[0][0] else inventory.get(path)
        if expected!=pins[path]:raise ValueError('Width source differs from retained input: '+path)
        selected=[{'id':row['id'],'current_id':row['current_id']} for row in rows];records+=selected
        groups.append({'source_file':path,'source_sha256':pins[path],'source_pointer':pointer,'rows':selected})
    dashboard='research/ocean-motion-dashboard.json';result=reconcile(records,decisions,read(dashboard)['entries'])
    expected={'current_identities':111,'scoped_width_records':190,'owners_with_admitted_scoped_width_records':93,
        'identities_without_admitted_scoped_width_records':18,'owners_with_broader_dashboard_width_capability':94,'dashboard_capability_only_owners':1}
    if result['counts']!=expected or result['capability_only_current_ids']!=['gulf-stream-system']:raise ValueError('Source reconciliation differs')
    for path in ['research/ocean-current-identity-admissions.json','research/norwegian-atlantic-slope-working-admission.json',
        'research/indian-current-identity-query-contract-v1.json','research/equatorial-basin-identity-query-contract-v3.json',dashboard]:pins[path]=sha(path)
    return {'schema':'osw.current-width-record-owner-reconciliation.v1','status':'SOURCE_ROWS_RECONCILED_WITH_DISTINCT_DASHBOARD_CANDIDATE_CAPABILITY',
        'as_of':'2026-10-30','installed_commit':'5aecb63549b672105cb38e94701c1bacc100bf52','input_sha256':pins,
        **result,'source_width_groups':groups,
        'interpretation':'190 admitted scoped records cover93 identities. The broader dashboard metric also counts a Gulf Stream System derived-width candidate, giving94 capability owners. That candidate is not an admitted width row, whole-current width or annual range.',
        'scientific_records_changed':0,'new_measurements_added':0,'full_goal_complete':False}

if __name__=='__main__':
    (ROOT/FILE).write_bytes((json.dumps(build(),indent=2)+'\n').encode())
    print('PASS190 source width records /93 owners; dashboard94 includes one candidate-only identity')
