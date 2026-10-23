"""Bind the observed native fields to a standalone, lazy source inspection view."""
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
from angola_nansen_native_sections import ROOT
from angola_nansen_portable_sections_v2 import REPORT, verify, encoded
from prepare_angola_query_sources import verify as query_sources, MANIFEST as QUERY_MANIFEST, OPERATOR as QUERY_BUILDER

TEMPLATE='analysis/angola_nansen_sections_view.html'
OPERATOR='analysis/build_angola_nansen_sections_view.py'
DIRECTORY='figures/angola-nansen-sections-2007-2014/'


def build():
    mirrors=query_sources()
    report=verify()
    raw=(ROOT/REPORT).read_bytes()
    if raw!=encoded(report):
        raise ValueError('Native source compilation is stale')
    proposals='research/ocean-current-inventory-expansion-candidates.json'
    document=json.loads((ROOT/proposals).read_bytes())
    indices=[i for i,r in enumerate(document['entries']) if r['proposed_id']=='angola']
    if len(indices)!=1:raise ValueError('Unresolved proposed Angola source identity')
    query={'document':proposals,'pointer':'/entries/'+str(indices[0]),'limit':1}
    config={'report':REPORT,'sha256':hashlib.sha256(raw).hexdigest(),
            'query_documents':{row['section_id']:row['source_file'] for row in mirrors['documents']},
            'naming_url':'../../almanac/query.html?source-q='+quote(json.dumps(query,separators=(',',':')),safe='')}
    text=(ROOT/TEMPLATE).read_text(encoding='utf8').replace('__CONFIG__',json.dumps(config).replace('<','\\u003c'))
    paths=[TEMPLATE,OPERATOR,REPORT,proposals,QUERY_MANIFEST,QUERY_BUILDER]
    manifest={'schema':'osw.angola-nansen-native-view.v2','report':REPORT,'section_count':11,
        'native_array_inventory_complete':True,'physical_width_admitted':False,
        'html_sha256':hashlib.sha256(text.encode('utf8')).hexdigest(),
        'input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
        'field_sha256':{s['field_file']:s['field_sha256'] for s in report['sections']}}
    manifest['query_source_sha256']={row['source_file']:row['source_sha256'] for row in mirrors['documents']}
    dest=ROOT/DIRECTORY;dest.mkdir(exist_ok=True)
    (dest/'index.html').write_text(text,encoding='utf8',newline='\n')
    (dest/'view.json').write_bytes(encoded(manifest))
    return manifest


if __name__=='__main__':print(json.dumps(build()))
