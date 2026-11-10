"""Preservation checks for the proposed cloud runtime; no build or bulk reads."""
import copy
import hashlib
import json
import azcc_onken_query_v1 as query
import azcc_onken_index_v1 as index

ROOT=query.ROOT
SCOPE='research/azcc-onken-runtime-scope-v1.json'
PARENT_MANIFEST='75e769027861afa121357f00b7ad125888ade3db2e12a188c0b60d0c23c7b4dd'
PARENT_WASM='d32afcbfa6de6cc3f195e3cbb9dab881196f58f36d1a2776f92963d05c10c516'

def scopes():
    scope=query.read(SCOPE)
    if query.sha(scope['parent_engine_manifest_file'])!=PARENT_MANIFEST:raise ValueError('Installed source receipt differs')
    for path,row in scope['runtime_source_changes'].items():
        if query.sha(path)!=row['candidate_sha256'] or query.sha(row['archive_path'])!=row['historical_sha256']:
            raise ValueError('Changed runtime source or history: '+path)
    for path,pin in {**scope['added_source_sha256'],**scope['source_dependencies_sha256'],**scope['candidate_rust_source_sha256']}.items():
        if query.sha(path)!=pin:raise ValueError('Changed frozen source: '+path)
    return scope

def verify_collections(parent,child):
    contract=query.build_contract()
    if child['schema']!=parent['schema'] or set(child['collections'])!=set(parent['collections']):
        raise ValueError('Collection/schema inventory differs')
    for name,old in parent['collections'].items():
        expected=(old+[contract['new_source']] if name=='sources' else
            old+[contract['width_record']] if name=='widths' else
            [contract['final_owner'] if r['id']==query.OWNER else r for r in old] if name=='objects' else old)
        if child['collections'][name]!=expected:raise ValueError('Unexpected scientific collection change: '+name)
    before=parent['manifest'];after=child['manifest']
    if set(after)!=set(before)|{query.KEY,index.KEY}:raise ValueError('Unexpected manifest namespace')
    if any(after[k]!=v for k,v in before.items() if k!='input_sha256'):raise ValueError('Historical manifest changed')
    if after[query.KEY]!=query.marker(contract):raise ValueError('Dimension evidence receipt differs')
    index.verify_audit(after[index.KEY])
    oldpins=before['input_sha256'];newpins=after['input_sha256'];allowed=set(contract['input_sha256'])|{query.FILE}|index.INDEX
    if set(newpins)!=set(oldpins)|allowed:raise ValueError('Input pin inventory differs')
    if any(newpins[p]!=pin for p,pin in oldpins.items() if p not in index.INDEX):raise ValueError('Historical scientific input changed')
    for p,pin in {**contract['input_sha256'],query.FILE:query.fingerprint(contract)}.items():
        if newpins.get(p)!=pin:raise ValueError('New source pin differs: '+p)

def dashboard_document(original):
    doc=copy.deepcopy(original);contract=query.build_contract()
    if [r for r in doc['entries'] if r['id']==query.OWNER]!=[contract['dashboard_before']]:raise ValueError('Changed prior AzCC dashboard')
    doc['entries']=[copy.deepcopy(contract['dashboard_after']) if r['id']==query.OWNER else r for r in doc['entries']]
    doc['snapshot_fingerprint']=hashlib.sha256(('osw.azcc-onken-width.v1\n'+doc['snapshot_fingerprint']+'\n'+query.sha(query.FILE)+'\n').encode()).hexdigest()
    doc['published_azcc_onken_width_projection_v1']={'contract_file':query.FILE,'contract_sha256':query.sha(query.FILE),
        'scope':'One dependent historical regional width; no seasonal dimension range or length.'}
    return doc

def verify_snapshot(name,old,new):
    if name not in {'dashboard','atlas','seasons'}:raise ValueError('Unknown API snapshot')
    expected=copy.deepcopy(old)
    if not isinstance(new.get('bundle_sha256'),str) or len(new['bundle_sha256'])!=64:raise ValueError('Missing bundle identity')
    expected['bundle_sha256']=new['bundle_sha256']
    if name=='dashboard':
        if json.loads(new['snapshot_json'])!=dashboard_document(json.loads(old['snapshot_json'])):raise ValueError('Complete dashboard projection differs')
        expected['snapshot_json']=new['snapshot_json']
    else:
        scenes=new.get('current_dimension_evidence_scenes');contract=query.build_contract()
        previous=old.get('current_dimension_evidence_scenes',{})
        if (not isinstance(scenes,dict) or set(scenes)!=set(previous)|{query.CURRENT}
                or any(scenes[k]!=v for k,v in previous.items())):raise ValueError('Unexpected dimension scene inventory or prior scene change')
        scene=scenes[query.CURRENT]
        if (scene.get('kind')!='published_current_dimension_evidence' or scene.get('entity_id')!=query.OWNER
            or scene.get('width_records')!=contract['prior_records']['widths']+[contract['width_record']]
            or scene.get('event_records')!=[] or scene.get('source_file')!=query.FACTS
            or scene.get('source_url')!=contract['new_source']['url'] or scene.get('figure')!='figures/onken-azcc-1993-evidence-compact-v1.svg'):
            raise ValueError('Dimension scene source/records differ')
        for key in ['scope','definition']:
            if not isinstance(scene.get(key),str) or not scene[key].strip():raise ValueError('Missing scope disclosure')
        expected['current_dimension_evidence_scenes']=scenes
        if not isinstance(old.get('supplemental_widths'),list):raise ValueError('Missing preceding supplemental widths')
        expected['supplemental_widths']=old['supplemental_widths']+[contract['width_record']]
        if name=='atlas':
            path='research/ocean-motion-dashboard.json'
            if json.loads(new['sources_json'][path])!=dashboard_document(json.loads(old['sources_json'][path])):raise ValueError('Atlas dashboard projection differs')
            expected['sources_json'][path]=new['sources_json'][path]
    if expected!=new:raise ValueError('Complete '+name+' changed outside the declared AzCC addition')
