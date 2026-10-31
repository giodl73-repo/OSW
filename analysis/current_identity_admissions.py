"""Versioned name admissions extend the historical package without reassigning IDs."""
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parents[1]
PATH='research/ocean-current-identity-admissions.json'
CATALOGUE='research/ocean-current-working-catalogue.json'
PROTOCOL='plans/current-identity-admission-protocol-v1.md'
OPERATOR='analysis/current_identity_admissions.py'
PROPOSALS='research/ocean-current-inventory-expansion-candidates.json'
BASE='almanac/release/v0.1.0/'
ID='southern-east-madagascar'
ENTITY='current:'+ID

def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def encoded(value):return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def read(path):return json.loads((ROOT/path).read_bytes())

def validate(doc):
    if doc['schema']!='osw.current-identity-admissions.v1' or doc['version']!='0.2.0-draft':raise ValueError('Unknown identity admission edition')
    for path,pin in doc['input_sha256'].items():
        if digest(path)!=pin:raise ValueError('Changed current admission input: '+path)
    row,=doc['entries']
    proposal,=[r for r in read(PROPOSALS)['entries'] if r['proposed_id']==ID]
    if row['id']!='current_admission:'+ID or row['entity']['id']!=ENTITY or row['proposal_id']!=ID:
        raise ValueError('Current admission identity mismatch')
    if row['entity']['label']!=proposal['name'] or row['source_dimensions']!=proposal['source_dimensions']:
        raise ValueError('Current admission source identity or dimensions changed')
    if row['status']!='editorial_identity_admitted_measurements_separately_gated' or row['canonical_measurements_admitted'] is not False:
        raise ValueError('Current identity admission is not a measurement admission')
    if any(row[k] is not False for k in ['rank_eligible','physical_edges_admitted','seasonal_playback_eligible','external_scientific_review_claimed']):
        raise ValueError('Current identity admission scope promoted')
    if row['annual_width_range_km'] is not None or row['annual_length_range_km'] is not None:
        raise ValueError('Current identity admission invented annual dimensions')
    if row['geometry'] is not None or row['entity']['source_record_id']!=ID:
        raise ValueError('Current identity admission invented geometry or owner')
    if row['entity']['setting']!='western_boundary' or row['entity']['identity_level']!='current' or row['entity']['time_behavior']!='persistent_variable':
        raise ValueError('Current identity classification changed')
    if row['source']['url']!=proposal['source_dimensions']['source_url'] or row['source']['provider_asset_redistributed'] is not False:
        raise ValueError('Current identity source or factual-use scope changed')
    baseline=read(BASE+'entities.json')
    if any(r['id']==ENTITY for r in baseline):raise ValueError('Admission duplicates base current')
    if row['entity']['source_id']!=row['source']['id']:raise ValueError('Current identity source join changed')
    planning=row['route_planning_decision']
    required=['current_id','name','existing_length_evidence_status','existing_scope','name_source_url','candidate_ids',
              'reference_path_decision','published_length_rank_eligible','ledger_kind','route_strategy_id',
              'route_strategy_label','planning_status','planning_basis','next_action','strategy_next_action',
              'known_component_currents','component_inventory_status']
    if any(k not in planning for k in required):raise ValueError('Incomplete current identity route worklist')
    if planning['current_id']!=ID or planning['candidate_ids']!=[] or planning['published_length_rank_eligible'] is not False:
        raise ValueError('Current identity route planning scope changed')
    return doc

def verify():return validate(read(PATH))

def additions(doc=None):
    doc=verify() if doc is None else validate(doc)
    rows={'entities':[],'sources':[],'names':[],'length_assessments':[],'current_identity_admissions':[]}
    for entry in doc['entries']:
        entity=entry['entity'];ident=entity['id'];source=entry['source']['id']
        rows['entities'].append(entity);rows['sources'].append(entry['source'])
        rows['names'].append({'id':'name:current:'+entry['proposal_id'],'entity_id':ident,'label':entity['label'],'preferred':True,'source_id':source})
        rows['length_assessments'].append({'id':'length_assessment:'+entry['proposal_id'],'entity_id':ident,
            'evidence_status':'reported_contextual_extent_pending_measurement_admission','rank_eligible':False,
            'published_length_km':None,'published_rank':None,'lower_bound_km':None,'proposed_system_length_km':None,
            'source_id':source,'length_source_id':source,'length_source_locator':'Introduction paragraph2',
            'scope':'Name identity admitted. The separately retained contextual650km report has not been admitted to the canonical ranked measurements.',
            'source_dimension_file':PROPOSALS,'source_dimension_proposal_id':entry['proposal_id']})
        rows['current_identity_admissions'].append(entry)
    return rows

def append(collections,doc=None):
    for name,rows in additions(doc).items():
        current=collections.setdefault(name,[])
        if {r['id'] for r in current}&{r['id'] for r in rows}:raise ValueError('Current identity ID collision in '+name)
        current.extend(rows)

def decision_rows(doc=None):
    doc=verify() if doc is None else doc
    return [{'current_id':r['proposal_id'],'name':r['entity']['label'],'measurement_ids':[],
        'status':'identity_admitted_width_not_admitted','whole_current_width_km':None,
        'annual_width_range_km':None,'admission_id':r['id']} for r in doc['entries']]

def catalogue(doc=None):
    doc=verify() if doc is None else doc
    rows=[r for r in read(BASE+'entities.json') if r['type']=='named_current']+[r['entity'] for r in doc['entries']]
    return {'schema':'osw.working-current-catalogue.v1','version':doc['version'],
        'status':'working_identity_catalogue_not_published_scientific_release','base_release':'0.1.0',
        'base_current_count':100,'admitted_current_count':len(doc['entries']),'current_count':len(rows),
        'input_sha256':{BASE+'entities.json':digest(BASE+'entities.json'),PATH:digest(PATH),OPERATOR:digest(OPERATOR)},
        'entries':rows}

def verify_inputs():
    doc=verify();expected=catalogue(doc)
    if (ROOT/CATALOGUE).read_bytes()!=encoded(expected):raise ValueError('Stale effective current catalogue')
    inputs={**doc['input_sha256'],PATH:digest(PATH),CATALOGUE:digest(CATALOGUE),OPERATOR:digest(OPERATOR)}
    return doc,inputs

if __name__=='__main__':
    doc=verify();result=catalogue(doc);(ROOT/CATALOGUE).write_bytes(encoded(result))
    print(json.dumps({'accepted_current_identities':result['current_count'],'new_admissions':len(doc['entries'])}))
