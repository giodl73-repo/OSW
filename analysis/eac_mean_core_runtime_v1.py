"""Exact extension checks for the cloud runtime; no builds or installed reads."""
import copy
import hashlib
import json
import eac_mean_core_query_v1 as query
import eac_mean_core_index_v1 as index

ROOT=query.ROOT
SCOPE='research/eac-mean-core-runtime-scope-v1.json'
PARENT_MANIFEST='e46482690f30265911ae96b100c7687c81f30d1771235431f652683cd4ce6f18'
PARENT_WASM='2615829d6e60536aedc78c07bf6b6c30e7137013eb85baec0b281036a1cf6f74'
MANIFEST='almanac/query-engine.manifest.json'
WASM='almanac/query-engine.wasm'

def scopes():
    scope=query.read(SCOPE)
    if query.sha(scope['parent_engine_manifest_file'])!=PARENT_MANIFEST:raise ValueError('Installed source receipt differs')
    for path,row in scope['runtime_source_changes'].items():
        if query.sha(path)!=row['candidate_sha256'] or query.sha(row['archive_path'])!=row['historical_sha256']:
            raise ValueError('Runtime source/history differs: '+path)
    for path,pin in {**scope['added_source_sha256'],**scope['source_dependencies_sha256']}.items():
        if query.sha(path)!=pin:raise ValueError('Frozen source differs: '+path)
    return scope

def verify_collections(parent,child):
    contract=query.build_contract()
    if child['schema']!=parent['schema'] or set(child['collections'])!=set(parent['collections'])|{query.COLLECTION}:
        raise ValueError('Collection/schema inventory differs')
    for name,old in parent['collections'].items():
        expected=(old+[contract['new_source']] if name=='sources' else
            [contract['final_owner'] if r['id']==query.OWNER else r for r in old] if name=='objects' else old)
        if child['collections'][name]!=expected:raise ValueError('Unexpected scientific collection change: '+name)
    if child['collections'][query.COLLECTION]!=contract['records']:raise ValueError('Mean-core section records differ')
    before=parent['manifest'];after=child['manifest']
    if set(after)!=set(before)|{query.KEY,index.KEY}:raise ValueError('Unexpected manifest namespace')
    if any(after[k]!=v for k,v in before.items() if k!='input_sha256'):raise ValueError('Historical manifest namespace changed')
    if after[query.KEY]!=query.marker(contract):raise ValueError('Mean-core receipt differs')
    index.verify_audit(after[index.KEY])
    oldpins=before['input_sha256'];newpins=after['input_sha256']
    allowed=set(contract['input_sha256'])|{query.FILE}|index.INDEX
    if set(newpins)!=set(oldpins)|allowed:raise ValueError('Input pin inventory differs')
    if any(newpins[p]!=pin for p,pin in oldpins.items() if p not in index.INDEX):raise ValueError('Historical scientific input changed')
    for p,pin in {**contract['input_sha256'],query.FILE:query.fingerprint(contract)}.items():
        if newpins.get(p)!=pin:raise ValueError('New source pin differs: '+p)

def dashboard_document(original):
    doc=copy.deepcopy(original);contract=query.build_contract()
    rows=[r for r in doc['entries'] if r['id']==query.OWNER]
    if rows!=[contract['dashboard_before']]:raise ValueError('Exact preceding EAC dashboard required')
    doc['entries']=[copy.deepcopy(contract['dashboard_after']) if r['id']==query.OWNER else r for r in doc['entries']]
    doc['snapshot_fingerprint']=hashlib.sha256(
        ('osw.mean-core-sections.v1\n'+doc['snapshot_fingerprint']+'\n'+query.sha(query.FILE)+'\n').encode()).hexdigest()
    doc['published_mean_core_sections_projection_v1']={'contract_file':query.FILE,'contract_sha256':query.sha(query.FILE),
        'scope':'Five regional model-mean sections; no seasonal dimensions or physical footprint.'}
    return doc


def verify_snapshot(name, old, new):
    """Permit the EAC scene/dashboard addition only; compare every other API field."""
    if name not in {'dashboard', 'atlas', 'seasons'}:
        raise ValueError('Unknown complete API snapshot')
    expected=copy.deepcopy(old)
    if not isinstance(new.get('bundle_sha256'),str) or len(new['bundle_sha256'])!=64:
        raise ValueError('Missing candidate bundle identity')
    expected['bundle_sha256']=new['bundle_sha256']
    if name=='dashboard':
        if json.loads(new['snapshot_json'])!=dashboard_document(json.loads(old['snapshot_json'])):
            raise ValueError('Complete dashboard projection differs')
        expected['snapshot_json']=new['snapshot_json']
    else:
        scenes=new.get('mean_core_section_scenes')
        if not isinstance(scenes,dict) or set(scenes)!={query.CURRENT}:
            raise ValueError('Unexpected current scene inventory')
        scene=scenes[query.CURRENT]
        contract=query.build_contract()
        if (scene.get('kind')!='published_mean_core_sections' or scene.get('records')!=contract['records']
            or scene.get('source_file')!=contract['records'][0]['source_file']
            or scene.get('source_url')!=contract['new_source']['url']
            or scene.get('figure')!='figures/eac-kerry-2020-mean-core-dimensions-v2.svg'
            or scene.get('compact_figure')!='figures/eac-kerry-2020-mean-core-dimensions-compact-v2.svg'):
            raise ValueError('Mean-core scene source/records differ')
        for key in ['scope','boundary','definition','labeling_note']:
            if not isinstance(scene.get(key),str) or not scene[key].strip():
                raise ValueError('Mean-core scene disclosure absent: '+key)
        expected['mean_core_section_scenes']=scenes
        if name=='atlas':
            path='research/ocean-motion-dashboard.json'
            if json.loads(new['sources_json'][path])!=dashboard_document(json.loads(old['sources_json'][path])):
                raise ValueError('Atlas dashboard projection differs')
            expected['sources_json'][path]=new['sources_json'][path]
    if expected!=new:
        raise ValueError('Complete '+name+' changed outside the declared EAC addition')
