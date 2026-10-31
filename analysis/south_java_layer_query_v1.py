"""Prepare source-qualified model context without admitting physical dimensions."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
FACTS = 'research/south-java-iskandar-2006-layer-source-facts-v1.json'
FIGURE = 'figures/south-java-iskandar-2006-layer-context-v1.svg'
MANIFEST = 'research/south-java-iskandar-2006-layer-figure-v1.json'
PROTOCOL = 'plans/published-model-layer-context-protocol-v1.md'
FILE = 'research/south-java-model-layer-query-contract-v1.json'
TARGET = 'current:south-java'
PAPER = 'source:iskandar-south-java-ofes-2006'
METHOD = 'source:published-model-layer-context-v1'
LAYERS = 'current_model_analysis_layers'
DEPTHS = 'current_model_depth_context'
OWNER_FIELDS = {LAYERS:('model_analysis_layer_ids','model_analysis_layers'),
                DEPTHS:('model_depth_context_ids','model_depth_context')}
PINS = {
    FACTS:'681304b3ac36350c16d7c96539c77781021763fc3e8d04c53fab044f3eeaabd8',
    FIGURE:'7dd86336579eca491354d9bd4d7847616eaa50ac0d6c3b405bd74b754f945d65',
    MANIFEST:'53d8095b61da2454a8a59a10efb61344db84db2f40d0eda7f5dc8dcae37beb42',
    'analysis/render_south_java_layer_context_v1.py':'0da26bed3c7c37622934d38625f06781787d6b46fce1d5ba47597a8d5f10c0ca',
    'signals/roles/check/south-java-layer-evidence-v1-roles-check-2026-10-24.md':'1041e21dacf7083ad61e992104e41afa116f0839875cdfc6808d9895c713d17f',
    'research/indian-coastal-context-installed-execution-review-v1.json':'0e5cfb3c7bb3ba7065bc1d5eff5db32121644dd7cec039d6ca0938253f141fe0',
}


def encoded(value):
    return (json.dumps(value,sort_keys=True,ensure_ascii=True,allow_nan=False,indent=2)+'\n').encode()


def fingerprint(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=True,allow_nan=False,separators=(',',':')).encode()).hexdigest()


def build_contract(root=ROOT):
    root = Path(root)
    for name,expected in PINS.items():
        if hashlib.sha256((root/name).read_bytes()).hexdigest() != expected:
            raise ValueError('Changed reviewed model context: '+name)
    facts = json.loads((root/FACTS).read_bytes())
    figure = json.loads((root/MANIFEST).read_bytes())
    if (figure['visual_review_complete'] is not True or figure['source_sha256'] != PINS[FACTS]
            or figure['figure_sha256'] != PINS[FIGURE]):
        raise ValueError('Unreviewed model context diagram')
    source = facts['source']
    common = {
        'related_current_id':TARGET,'source_id':PAPER,'method_source_id':METHOD,'source_ids':[PAPER,METHOD],
        'source_file':FACTS,'source_file_sha256':PINS[FACTS],
        'figure_file':FIGURE,'figure_sha256':PINS[FIGURE],
        'model_support':copy.deepcopy(facts['model_support']),
        'depth_unit':'m','is_observation':False,'independent_observation_count':0,
        'physical_width_km':None,'physical_current_thickness_m':None,
        'physical_annual_depth_range_m':None,'physical_uncertainty_m':None,
        'geometry':None,'sample_date':None,'rank_eligible':False,
        'physical_state_join_eligible':False,'geographic_seasonal_playback_eligible':False,
    }
    rows = {LAYERS:[],DEPTHS:[], 'sources':[
        {'id':PAPER,'kind':'external','title':source['title'],'label':'Iskandar et al.2006 South Java model study',
         'doi':source['doi'],'url':source['url'],'publication_year':source['year'],
         'access_scope':source['access_mode'],'selected_prose_sections_reviewed':source['reviewed_sections'],
         'original_asset_retained':False,'original_file_sha256':None,'full_paper_reviewed':False,
         'source_figures_visually_reviewed':[],'provider_asset_redistributed':False,'rights_note':source['rights']},
        {'id':METHOD,'kind':'internal','title':'Published model layer and depth context protocol v1',
         'label':'Model context classification and admission limits','path':PROTOCOL,'url':'../'+PROTOCOL,
         'provider_asset_redistributed':False},
    ]}
    for name,items,record_type in [(LAYERS,facts['layer_definitions'],'model_analysis_layer_definition'),
                                   (DEPTHS,facts['reported_model_depth_context'],'reported_model_mean_depth_context')]:
        for original in items:
            row = {**copy.deepcopy(common),**copy.deepcopy(original),'record_type':record_type}
            row['entity_id'] = TARGET if row['source_feature']=='SJCC' else None
            row['association_kind'] = 'surface_feature_model_context' if row['entity_id'] else 'related_undercurrent_context_without_catalogue_identity'
            rows[name].append(row)
    dependencies = {**PINS, **{name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in
        (PROTOCOL,'analysis/south_java_layer_query_v1.py')}}
    return {'schema':'osw.current-model-layer-context-query.v1','version':'south-java-iskandar-2006-v1',
        'status':'PREPARED_WORKING_CONTEXT_NOT_INSTALLED_PACKET','input_sha256':dependencies,
        'owner_id':TARGET,'collections':rows,
        'manifest_fields':{'south_java_model_context_version':'iskandar-2006-v1'},
        'example_queries':[
            {'collection':LAYERS,'filters':[{'field':'related_current_id','op':'eq','value':TARGET}],'limit':100},
            {'collection':DEPTHS,'filters':[{'field':'entity_id','op':'eq','value':TARGET}],'limit':100},
            {'collection':DEPTHS,'filters':[{'field':'source_feature','op':'eq','value':'SJCU'}],'limit':100},
            {'collection':DEPTHS,'filters':[{'field':'depth_cap_m','op':'exists','value':True}],'limit':100},
        ],
        'counts':{'model_analysis_layer_definitions':2,'model_depth_context_records':3,
                  'surface_owned_records':3,'related_undercurrent_records':2,
                  'publication_sources':1,'internal_method_sources':1},
        'admission':{'new_current_identities':0,'physical_widths':0,'physical_current_thicknesses':0,
                     'ranked_lengths':0,'physical_state_joins':0,'observed_velocity_samples':0,
                     'annual_dimension_ranges':0,'independent_observations':0}}


def checked_ids(rows, label):
    if not isinstance(rows,list) or any(not isinstance(row,dict) or not isinstance(row.get('id'),str) or not row['id'] for row in rows):
        raise ValueError('Invalid record list: '+label)
    ids = [row['id'] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate existing IDs: '+label)
    return set(ids)


def query_url(collection):
    query = {'collection':collection,'filters':[{'field':'related_current_id','op':'eq','value':TARGET}],
             'sort':{'field':'id','direction':'asc'},'limit':100}
    return 'query.html?q='+quote(json.dumps(query,separators=(',',':')))


def append(collections, document):
    """Validate fully, prepare small replacements, then update the mapping once."""
    if type(collections) is not dict or encoded(document) != encoded(build_contract()):
        raise ValueError('Changed reviewed model query contract')
    rows = document['collections']
    for name,additions in rows.items():
        existing = checked_ids(collections.get(name,[]),name)
        if existing & checked_ids(additions,'new '+name):
            raise ValueError('Model context collision in '+name)
    objects = collections.get('objects',[])
    entities = collections.get('entities',[])
    checked_ids(objects,'objects'); checked_ids(entities,'entities')
    owners = [row for row in objects if row['id']==TARGET]
    if len(owners)!=1 or owners[0].get('type')!='named_current' or sum(row['id']==TARGET for row in entities)!=1:
        raise ValueError('Accepted South Java owner/entity required')
    sources = [*collections.get('sources',[]),*rows['sources']]
    prior_registry = {row['id'] for row in collections.get('sources',[])}
    registry = checked_ids(sources,'combined sources')
    doi = '10.1029/2006jc003486'
    if any(str(row.get('doi','')).lower().removeprefix('https://doi.org/')==doi and row['id']!=PAPER for row in collections.get('sources',[])):
        raise ValueError('Existing publication DOI requires explicit source-registry reconciliation')
    owner = copy.deepcopy(owners[0])
    refs = owner.get('source_ids')
    if (not isinstance(refs,list) or any(not isinstance(ref,str) for ref in refs)
            or len(refs)!=len(set(refs)) or set(refs)-prior_registry
            or type(owner.get('linked_source_count')) is not int or owner['linked_source_count']!=len(refs)):
        raise ValueError('Invalid prior South Java source references/count')
    if (not isinstance(owner.get('capabilities'),dict) or not isinstance(owner.get('evidence_links'),list)
            or not isinstance(owner.get('section_fingerprints'),dict)):
        raise ValueError('Invalid South Java evidence containers')
    owned = []
    for name,(field,capability) in OWNER_FIELDS.items():
        additions = [row for row in rows[name] if row['entity_id']==TARGET]
        prior = owner.get(field,[])
        if (not isinstance(prior,list) or any(not isinstance(value,str) for value in prior)
                or len(prior)!=len(set(prior)) or set(prior)&{row['id'] for row in additions}):
            raise ValueError('Invalid prior model-context owner references')
        available = {row['id']:row for row in collections.get(name,[])}
        if any(value not in available or available[value].get('entity_id')!=TARGET for value in prior):
            raise ValueError('Unresolved prior model-context owner reference')
        for value in prior:
            record = available[value]
            references = record.get('source_ids')
            if (not isinstance(references,list) or any(not isinstance(ref,str) for ref in references)
                    or len(references)!=len(set(references)) or set(references)-prior_registry
                    or record.get('source_id') not in references or record.get('method_source_id') not in references):
                raise ValueError('Unresolved prior model-context provenance')
        if capability in owner['capabilities'] and (type(owner['capabilities'][capability]) is not int
                or owner['capabilities'][capability]!=len(prior)):
            raise ValueError('Prior model-context capability/count mismatch')
        owner[field] = prior+[row['id'] for row in additions]
        owner['capabilities'][capability] = len(owner[field])
        owner['evidence_links'].append({'label':'Query related model '+capability.replace('_',' ')+' (includes separate undercurrent context)',
                                        'url':query_url(name)})
        owned.extend(additions)
    for name in OWNER_FIELDS:
        for row in rows[name]:
            if set(row['source_ids'])-registry or row['source_id'] not in registry or row['method_source_id'] not in registry:
                raise ValueError('Unresolved model context source')
    owner['source_ids'] = sorted(set(refs)|{PAPER,METHOD})
    owner['linked_source_count'] = len(owner['source_ids'])
    owner['evidence_links'].append({'label':'Model study layer/depth context, not current thickness','url':'../'+FIGURE})
    owner['section_fingerprints']['model_layer_context'] = fingerprint(owned)
    owner['fingerprint'] = fingerprint({key:value for key,value in owner.items() if key!='fingerprint'})
    updates = {name:[*collections.get(name,[]),*copy.deepcopy(additions)] for name,additions in rows.items()}
    updates['objects'] = [owner if row['id']==TARGET else row for row in objects]
    collections.update(updates)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['build','check'])
    args = parser.parse_args()
    document = build_contract()
    if args.action=='build':
        (ROOT/FILE).write_bytes(encoded(document))
    elif (ROOT/FILE).read_bytes()!=encoded(document):
        raise ValueError('Prepared model context contract differs from reviewed projection')
    print(json.dumps({'status':'PASS','action':args.action,'counts':document['counts'],'admission':document['admission']}))


if __name__=='__main__':
    main()
