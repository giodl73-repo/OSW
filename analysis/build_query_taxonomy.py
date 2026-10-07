"""Expose existing editorial identities and parent assignments without inheritance."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCOPE='Existing editorial identity facets and ledger parent assignments; not flow connectivity, physical containment, equivalent identities or inherited measurements. Missing members remain unassessed.'

def build(objects,entities,read):
    ledger_file='research/ocean-current-almanac.json';vocabulary_file='research/ocean-motion-taxonomy.json'
    ledger=read(ledger_file);vocabulary=read(vocabulary_file)
    index={r['id']:r for r in objects};entity_index={r['id']:r for r in entities}
    if set(index)!={r['id'] for r in entities if r['type'] in ['named_current','named_eddy','operational_eddy_detection']}:raise ValueError('Incomplete taxonomy object inventory')
    for row in objects:
        entity=entity_index[row['id']]
        for key in ['type','identity_level','setting','time_behavior','basin','label']:
            if row.get(key)!=entity.get(key):raise ValueError('Taxonomy facet differs from canonical identity')
        if row['identity_level'] not in vocabulary['axes']['identity_level']:raise ValueError('Unknown taxonomy identity level')
    edges=[]
    for i,row in enumerate(ledger['entries']):
        if not row.get('part_of_system'):continue
        child_id='current:'+row['id'];parent_id='current:'+row['part_of_system']
        if child_id not in index or parent_id not in index or child_id==parent_id:raise ValueError('Unresolved taxonomy parent')
        parent_kind=index[parent_id]['identity_level']
        if parent_kind not in ['family','system']:raise ValueError('Unsupported taxonomy parent kind')
        edges.append({'id':'taxonomy-link:'+row['id'],'child_id':child_id,'parent_id':parent_id,
            'child_label':index[child_id]['label'],'parent_label':index[parent_id]['label'],
            'predicate':'basin_or_subfamily_member_of' if parent_kind=='family' else 'named_system_component_of',
            'status':'existing_editorial_ledger_assignment_not_new_canonical_relation',
            'source_file':ledger_file,'source_pointer':'/entries/'+str(i)+'/part_of_system',
            'evidence_role':'existing_editorial_parent_assignment','naming_source_url':ledger['sources'][row['name_source']],
            'naming_source_is_parent_relation_evidence':False,'physical_connectivity_eligible':False,
            'measurement_inheritance_eligible':False,'scope':SCOPE})
    def cycle(identifier,path):
        if identifier in path:raise ValueError('Cyclic taxonomy parent assignments')
        for edge in edges:
            if edge['child_id']==identifier:cycle(edge['parent_id'],path|{identifier})
    for identifier in index:cycle(identifier,set())
    receipts=[]
    for path in [ledger_file,vocabulary_file]:
        raw=(ROOT/path).read_bytes();receipts.append({'file':path,'sha256':hashlib.sha256(raw).hexdigest(),'source_json':raw.decode('utf-8')})
    return sorted(edges,key=lambda e:e['id']),{'schema':'osw.query-taxonomy.v1','scope':SCOPE,
        'node_count':len(objects),'link_count':len(edges),'source_receipts':receipts,
        'identity_levels':vocabulary['axes']['identity_level'],'complete_physical_taxonomy':False,
        'measurement_inheritance_eligible':False}
