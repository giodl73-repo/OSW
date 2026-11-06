"""Independent whole-packet and API preservation model; no installed payload reads."""
import copy
import hashlib
import json
import re
import equatorial_basin_identity_runtime_v3 as basin
import pacific_nec_nominal_width_query_v1 as query
import pacific_nec_nominal_width_index_v1 as index

SCOPE='research/pacific-nec-nominal-width-runtime-scope-v3.json'
PARENT_MANIFEST='6aa85f9d22abbb45d5bd75ecf709afa117578de18588a40de647f657a045cd8c'
PARENT_WASM='038d7e9d72e5a9116e7ba346c8520dba3339242506a285253e8655e7baaaf985'
PROJECTION='published_pacific_nec_nominal_width_projection_v1'
DIMENSION_STATUS=('Separately sourced nominal regional width evidence is linked for the Pacific NEC. Family and sibling '
    'measurements are not inherited; lengths, annual ranges and physical edges remain unresolved.')


def contract():
    c=query.build_contract()
    if query.encoded(c)!=(query.ROOT/query.FILE).read_bytes():raise ValueError('Frozen nominal-width contract differs')
    return c


def scopes():
    scope=query.read(SCOPE)
    if query.sha(scope['parent_engine_manifest_file'])!=PARENT_MANIFEST:raise ValueError('Installed source receipt differs')
    for p,row in scope['runtime_source_changes'].items():
        if query.sha(p)!=row['candidate_sha256'] or query.sha(row['archive_path'])!=row['historical_sha256']:
            raise ValueError('Changed runtime source or history: '+p)
    for p,h in {**scope['added_source_sha256'],**scope['source_dependencies_sha256'],**scope['candidate_rust_source_sha256']}.items():
        if query.sha(p)!=h:raise ValueError('Changed frozen source: '+p)
    return scope


def verify_collections(parent,child):
    c=contract()
    if set(child)!=set(parent) or any(child[k]!=parent[k] for k in parent if k not in {'collections','manifest'}):
        raise ValueError('Historical packet envelope changed')
    before,after=parent['collections'],child['collections']
    if {k:len(v) for k,v in before.items()}!=c['parent_collection_counts'] or set(after)!=set(before):
        raise ValueError('Exact complete parent collection inventory required')
    for name,rows in before.items():
        if name=='widths':expected=rows+[c['width_record']]
        elif name=='sources':expected=rows+c['new_sources']
        elif name=='objects':expected=[c['final_owner'] if r['id']==query.OWNER else r for r in rows]
        else:expected=rows
        if after[name]!=expected:raise ValueError('Historical rows/order or declared width extension differs: '+name)
    old,new=parent['manifest'],child['manifest']
    if set(new)!=set(old)|{query.KEY,index.KEY}:raise ValueError('Unexpected manifest namespace')
    if any(new[k]!=v for k,v in old.items() if k!='input_sha256'):raise ValueError('Historical manifest changed')
    if new[query.KEY]!=query.marker(c):raise ValueError('Width receipt differs')
    index.verify_audit(new[index.KEY])
    added={**c['input_sha256'],query.FILE:query.sha(query.FILE)}
    if set(new['input_sha256'])!=set(old['input_sha256'])|set(added)|index.INDEX:raise ValueError('Input pin inventory differs')
    if any(new['input_sha256'][p]!=h for p,h in old['input_sha256'].items() if p not in index.INDEX):raise ValueError('Historical scientific input rebound')
    if any(new['input_sha256'].get(p)!=h for p,h in added.items()):raise ValueError('New source binding differs')
    if any(not isinstance(new['input_sha256'].get(p),str) or not re.fullmatch('[0-9a-f]{64}',new['input_sha256'][p]) for p in index.INDEX):raise ValueError('Missing index hash')


def member_context():
    return {'label':'Nominal regional width: about 1,000 km','query_url':contract()['width_query_after_installation'],
        'scope':'Near-surface regional summary; annual range and physical edges unknown.'}


def membership_scene(rows,owner=None):
    result=basin.membership_scene(rows,owner)
    if result is not None:
        for member in result['members']:
            if member['entity_id']==query.OWNER:member['nominal_width_evidence']=member_context()
        if any('nominal_width_evidence' in member for member in result['members']):result['dimension_status']=DIMENSION_STATUS
    return result


def scenes():
    old=basin.scenes()
    return {owner:membership_scene([m['membership_record'] for m in scene['members']],owner) for owner,scene in old.items()}


def width_scene(rows):
    if not rows:return None
    if any(r!=contract()['width_record'] for r in rows):raise ValueError('Only the exact reviewed nominal width may enter this scene')
    return {'kind':'published_current_dimension_evidence','title':'Pacific NEC: nominal near-surface width',
        'current_id':query.CURRENT,'entity_id':query.OWNER,'width_records':copy.deepcopy(rows),'event_records':[],
        'scope':'About 1,000 km is a WGS84 conversion of the nominal regional 8–17°N band, rounded to 100 km. It is not a whole-current width, annual range, numerical uncertainty or diagnosed flow-normal width.',
        'definition':'The project synthesis describes a near-surface band west of the dateline. Its related JPO study describes 7–17°N in a mapped 0–100 m mean field. Keep those source descriptions separate; no paired physical edges or uniform sampling dates are established.',
        'source_file':contract()['width_record']['source_file'],'source_url':contract()['new_sources'][0]['url'],
        'source_label':'Reviewed original project synthesis','figure':'figures/pacific-nec-nominal-width-v1.svg'}


def dashboard_document(original):
    c=contract();result=copy.deepcopy(original)
    if len(original['entries'])!=251 or original['counts']['named_current']!=111 or PROJECTION in original:
        raise ValueError('Exact preceding dashboard required')
    if [r for r in original['entries'] if r['id']==query.OWNER]!=[c['dashboard_before']]:raise ValueError('Changed preceding owner row')
    result['entries']=[copy.deepcopy(c['dashboard_after']) if r['id']==query.OWNER else r for r in result['entries']]
    result['snapshot_fingerprint']=hashlib.sha256(('osw.pacific-nec-nominal-width.v1\n'+original['snapshot_fingerprint']+'\n'+query.sha(query.FILE)+'\n').encode()).hexdigest()
    result[PROJECTION]={'contract_file':query.FILE,'contract_sha256':query.sha(query.FILE),'new_width_records':1,'new_independent_observations':0}
    return result


def verify_snapshot(name,old,new):
    if name not in {'atlas','seasons','dashboard'}:raise ValueError('Unknown API snapshot')
    if not isinstance(new.get('bundle_sha256'),str) or not re.fullmatch('[0-9a-f]{64}',new['bundle_sha256']):raise ValueError('Missing bundle identity')
    expected=copy.deepcopy(old);expected['bundle_sha256']=new['bundle_sha256']
    if name=='dashboard':
        if json.loads(new['snapshot_json'])!=dashboard_document(json.loads(old['snapshot_json'])):raise ValueError('Complete dashboard projection differs')
        expected['snapshot_json']=new['snapshot_json']
    else:
        expected['basin_identity_scenes']=scenes()
        decisions=expected['admitted_current_decisions']
        matches=[r for r in decisions if r['current_id']==query.CURRENT]
        if len(matches)!=1 or matches[0]['measurement_ids']!=[] or matches[0]['status']!='identity_admitted_width_not_admitted':
            raise ValueError('Exact preceding identity-only decision required')
        matches[0]['measurement_ids']=[query.WIDTH_ID];matches[0]['status']='nominal_regional_width_admitted'
        expected['current_dimension_evidence_scenes'][query.CURRENT]=width_scene([contract()['width_record']])
        expected['supplemental_widths'] += [contract()['width_record']]
        if name=='atlas':
            path='research/ocean-motion-dashboard.json'
            if json.loads(new['sources_json'][path])!=dashboard_document(json.loads(old['sources_json'][path])):raise ValueError('Atlas dashboard projection differs')
            expected['sources_json'][path]=new['sources_json'][path]
        else:
            plan=expected['phase_plans'][query.CURRENT]
            if plan['phases']!=[] or plan['can_play'] is not False or plan['eligible_indices']!=[]:
                raise ValueError('Exact empty preceding seasonal plan required')
            plan['range_note']='Nominal regional width about 1,000 km; sampling dates, annual ranges and numerical uncertainty remain unknown.'
            plan['playback_scope']='Static nominal summary; no comparable dated states for seasonal animation.'
    if expected!=new:raise ValueError('Complete '+name+' changed outside exact width projections')


def verify_object(owner,old,new):
    c=contract()
    if (owner not in scenes() or old.get('ok') is not True or old.get('id')!=owner
            or not isinstance(new.get('bundle_sha256'),str) or not re.fullmatch('[0-9a-f]{64}',new['bundle_sha256'])
            or len(old['collections']['sources'])!=217 or 'current_dimension_evidence_scene' in old):
        raise ValueError('Exact preceding basin object API required')
    expected=copy.deepcopy(old);expected['bundle_sha256']=new['bundle_sha256']
    expected['collections']['sources'] += c['new_sources']
    expected['basin_identity_context_scene']=scenes()[owner]
    if owner==query.OWNER:
        if old['collections']['widths']!=[]:raise ValueError('Preexisting Pacific NEC width requires reconciliation')
        expected['collections']['widths']=[c['width_record']]
        expected['current_dimension_evidence_scene']=width_scene([c['width_record']])
    if expected!=new:raise ValueError('Complete object API changed outside exact width/source projections: '+owner)
