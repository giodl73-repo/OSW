"""Expose a complete source inventory while Angola identity admission is pending."""
import hashlib
import json
from urllib.parse import quote
from angola_nansen_native_sections import ROOT
from angola_nansen_portable_sections_v2 import REPORT, verify as build, encoded
from build_angola_nansen_sections_view import DIRECTORY, TEMPLATE, OPERATOR as VIEW_BUILDER
from prepare_angola_query_sources import verify as query_sources, MANIFEST as QUERY_MANIFEST, OPERATOR as QUERY_BUILDER

ID='diagnostic:angola-nansen-native-source-sections'
ADAPTER='analysis/angola_nansen_source_query.py'


def evidence():
    document=build()
    if (ROOT/REPORT).read_bytes()!=encoded(document):raise ValueError('Changed complete native section report')
    view_path=DIRECTORY+'view.json';view=json.loads((ROOT/view_path).read_bytes())
    query=query_sources()
    mirror_hashes={row['source_file']:row['source_sha256'] for row in query['documents']}
    expected={s['field_file']:s['field_sha256'] for s in document['sections']}
    if view['report']!=REPORT or view['field_sha256']!=expected or view['physical_width_admitted'] is not False:
        raise ValueError('Changed native observation view scope')
    for path,sha in view['input_sha256'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=sha:raise ValueError('Changed native source view dependency: '+path)
    if hashlib.sha256((ROOT/(DIRECTORY+'index.html')).read_bytes()).hexdigest()!=view['html_sha256']:
        raise ValueError('Changed native observation HTML binding')
    if view['query_source_sha256']!=mirror_hashes:raise ValueError('Changed native query-source view binding')
    paths=set(document['input_sha256'])|set(expected)|set(view['input_sha256'])|{REPORT,view_path,DIRECTORY+'index.html',TEMPLATE,VIEW_BUILDER,ADAPTER,'analysis/angola_nansen_reproduction.py'}
    paths.update(mirror_hashes);paths.update([QUERY_MANIFEST,QUERY_BUILDER])
    inputs={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(paths)}
    row={'id':ID,'label':'Angola proposed current: eleven native Nansen velocity sections',
         'kind':'native_observed_source_section_inventory','proposed_current_id':'angola',
         'entity_id':None,'current_id':None,'canonical_current_identity_admitted':False,
         'document':document,'source_file':REPORT,'source_file_sha256':inputs[REPORT],
         'native_query_documents':query['documents'],
         'figure':DIRECTORY+'index.html','rank_eligible':False,'physical_width_admitted':False}
    return document,row,inputs


def dashboard_link():
    query={'collection':'diagnostics','filters':[{'field':'id','op':'eq','value':ID}],'limit':1}
    return {'id':ID,'label':'Angola · 11 native ship sections / 6,148 profiles',
            'status':'Proposed current; source samples available; widths and identity admission pending.',
            'url':'../'+DIRECTORY,'query_url':'query.html?q='+quote(json.dumps(query,separators=(',',':')),safe='')}
