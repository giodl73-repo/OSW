"""Canonical admission with field-specific cross-platform arithmetic replay checks.

The v1 scientific producer, report, SVG, contract and Rust ABI remain unchanged.
"""
import copy
import hashlib
import json
import math
import re
import xml.etree.ElementTree as ET
import chen_indian_sec_ridge_query_v1 as legacy

ROOT=legacy.ROOT
FILE=legacy.FILE
PARENT=legacy.PARENT
KEY=legacy.KEY
SERIES=legacy.SERIES
READINGS=legacy.READINGS
SENSITIVITIES=legacy.SENSITIVITIES
SERIES_ID=legacy.SERIES_ID
ENTITY=legacy.ENTITY
FAMILY=legacy.FAMILY
SOURCE_IDS=legacy.SOURCE_IDS
parent=legacy.parent
read=legacy.read
fingerprint=legacy.fingerprint
encoded=legacy.encoded
science=legacy.science
display_geometry=legacy.display_geometry
CANONICAL={
    FILE:'8a2f105f06ab009fa2a859035ad3f76516aaaf97c6f4608ad413e18758011fc6',
    science.FILE:'5fc743921152f69bbd2b1c57a3172e1b020227fccb89b831ae128513c91f5252',
    science.FIGURE:'c07f3ed0a8cc71c5bd4d4fb07f7fae36bb2768c158edfb11ac93340187815e01',
    legacy.MODULE:'3f4a9fb833e3a33984f82a672fce523e8a09ce0ef4b0ab58f8d59abd9fd8c221',
}
LENGTH_PATH=re.compile(r'^/(?:rows/\d+/(?:length_km|resolution_scenarios/\d+/length_km)|cases/\d+/(?:nominal_grid_length_km|computed_method_resolution_span_km/[01]))$')
MAX_LENGTH_ROUNDOFF_KM=1e-10
MAX_LENGTH_ULPS=64
SVG_PATH_PIXEL_ROUNDOFF=.010000000001
NUMBER=re.compile(r'[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?')

def compare_report(expected,actual):
    differences=[]
    def visit(a,b,path):
        if type(a) is not type(b):raise ValueError('Replay type changed: '+path)
        if isinstance(a,dict):
            if set(a)!=set(b):raise ValueError('Replay keys changed: '+path)
            for k in a:visit(a[k],b[k],path+'/'+str(k))
        elif isinstance(a,list):
            if len(a)!=len(b):raise ValueError('Replay array length changed: '+path)
            for i,(x,y) in enumerate(zip(a,b)):visit(x,y,path+'/'+str(i))
        elif type(a) is float:
            if not math.isfinite(a) or not math.isfinite(b):raise ValueError('Nonfinite replay value: '+path)
            if a==b:return
            bound=min(MAX_LENGTH_ROUNDOFF_KM,MAX_LENGTH_ULPS*math.ulp(a))
            if not LENGTH_PATH.fullmatch(path) or a<=0 or b<=0 or abs(a-b)>bound:
                raise ValueError('Replay differs outside length-arithmetic roundoff: '+path)
            differences.append({'pointer':path,'absolute_difference_km':abs(a-b),'allowed_difference_km':bound})
        elif a!=b:raise ValueError('Replay value changed: '+path)
    visit(expected,actual,'')
    return differences

def compare_figure(expected,actual):
    """Only two-decimal coordinate rounding on the three model paths may differ."""
    left,right=ET.fromstring(expected),ET.fromstring(actual);differences=[]
    def visit(a,b,path):
        if a.tag!=b.tag or (a.text or '')!=(b.text or '') or (a.tail or '')!=(b.tail or '') or len(a)!=len(b) or set(a.attrib)!=set(b.attrib):
            raise ValueError('Replay SVG structure/text changed: '+path)
        for key,value in a.attrib.items():
            other=b.attrib[key]
            if value==other:continue
            if not (key=='d' and a.tag.endswith('}path') and a.attrib.get('stroke-width')=='2.5' and a.attrib.get('fill')=='none'):
                raise ValueError('Replay SVG attribute changed: '+path+'/'+key)
            if NUMBER.sub('#',value)!=NUMBER.sub('#',other):raise ValueError('Replay SVG path commands changed')
            x,y=NUMBER.findall(value),NUMBER.findall(other)
            if len(x)!=len(y):raise ValueError('Replay SVG vertex count changed')
            for index,(u,v) in enumerate(zip(x,y)):
                if u!=v:
                    delta=abs(float(u)-float(v))
                    if not math.isfinite(delta) or delta>SVG_PATH_PIXEL_ROUNDOFF:raise ValueError('Replay SVG exceeds coordinate serialization roundoff')
                    differences.append({'element':path,'coordinate_index':index,'expected':u,'replayed':v,'absolute_difference_px':delta})
        for i,(x,y) in enumerate(zip(a,b)):visit(x,y,path+'/'+str(i))
    visit(left,right,'')
    return differences

def validated_contract():
    for path,pin in CANONICAL.items():
        if legacy.sha(path)!=pin:raise ValueError('Canonical bytes changed: '+path)
    contract=read(FILE)
    if encoded(contract)!=(ROOT/FILE).read_bytes():raise ValueError('Canonical contract encoding changed')
    for path,pin in contract['input_sha256'].items():
        if legacy.sha(path)!=pin:raise ValueError('Scientific contract input changed: '+path)
    report=read(science.FILE);replayed=science.build()
    lengths=compare_report(report,replayed)
    figure=compare_figure((ROOT/science.FIGURE).read_bytes(),science.figure(replayed).encode())
    proof={'schema':'osw.chen-indian-sec-canonical-replay.v2','canonical_contract_sha256':CANONICAL[FILE],
           'canonical_report_sha256':CANONICAL[science.FILE],'canonical_figure_sha256':CANONICAL[science.FIGURE],
           'length_roundoff_count':len(lengths),'maximum_length_roundoff_km':max([d['absolute_difference_km'] for d in lengths],default=0),
           'length_roundoff_details':lengths,'svg_coordinate_roundoff_details':figure,'canonical_values_modified':False}
    return contract,proof

def build_contract():
    return validated_contract()[0]

# The exact v1 parent/source/collision/row admission checks follow. Only their
# initial contract validation uses the versioned canonical replay rule above.

def prepare(collections,manifest,contract,*,parent_logical_sha256):
    if contract!=build_contract() or parent_logical_sha256!=PARENT or KEY in manifest:
        raise ValueError('Exact unapplied contract and audited parent required')
    counts=contract['parent_collection_counts']
    for name in ['objects','entities','sources','length_assessments',SERIES,READINGS,'widths','reference_routes']:
        rows=collections.get(name)
        if not isinstance(rows,list) or len(rows)!=counts[name]:raise ValueError('Parent count differs: '+name)
        ids=[r.get('id') for r in rows]
        if any(not isinstance(i,str) or not i for i in ids) or len(set(ids))!=len(ids):raise ValueError('Unique parent IDs required: '+name)
    if SENSITIVITIES in collections:raise ValueError('Unexpected existing sensitivity collection')
    for owner,audited in contract['prior_records']['identities'].items():
        for name,key in [('objects','object'),('entities','entity')]:
            if [r for r in collections[name] if r['id']==owner]!=[audited[key]]:raise ValueError('Changed audited identity: '+owner)
        for name,expected in audited['linked_records'].items():
            found=[r for r in collections.get(name,[]) if r.get('entity_id')==owner or r.get('current_id')==owner.removeprefix('current:') or r.get('family_entity_id')==owner]
            if found!=expected:raise ValueError('Changed audited owner evidence: '+owner+'/'+name)
    matches,resolutions=parent.publications(collections['sources'])
    if any(matches.values()) or any(r['status']!='MISSING' for r in resolutions.values()):raise ValueError('Source identity changed after audit')
    old_sources={r['id']:r for r in collections['sources']}
    if any(i in old_sources for i in SOURCE_IDS):raise ValueError('New source ID already exists')
    for audited in contract['prior_records']['identities'].values():
        if any(old_sources.get(r['id'])!=r for r in audited['owner_sources']):raise ValueError('Existing owner source changed')
    if any(r.get('id','').startswith(parent.PREFIXES) for rows in collections.values() for r in rows):raise ValueError('Candidate ID prefix already exists')
    pins={**contract['input_sha256'],FILE:fingerprint(contract)}
    if any(p in manifest.get('input_sha256',{}) and manifest['input_sha256'][p]!=h for p,h in pins.items()):raise ValueError('Historical source pin would change')
    after=dict(collections)
    after[SERIES]=[*collections[SERIES],copy.deepcopy(contract['series_record'])]
    after[READINGS]=[*collections[READINGS],*copy.deepcopy(contract['reading_records'])]
    after[SENSITIVITIES]=copy.deepcopy(contract['sensitivity_records'])
    after['sources']=[*collections['sources'],*copy.deepcopy(contract['new_sources'])]
    after['objects']=[copy.deepcopy(contract['final_owner']) if r['id']==ENTITY else r for r in collections['objects']]
    after['length_assessments']=[copy.deepcopy(contract['final_length_assessment']) if r['entity_id']==ENTITY else r for r in collections['length_assessments']]
    updated=dict(manifest)
    updated['input_sha256']={**manifest.get('input_sha256',{}),**pins}
    updated[KEY]={'schema':'osw.indian-sec-model-grid-length-runtime.v1','contract_file':FILE,
                  'contract_sha256':fingerprint(contract),'parent_logical_sha256':PARENT,
                  'series_added':1,'readings_added':75,'sensitivities_added':120,
                  'qualified_model_grid_lengths':8,'withheld_readings':67,'reported_lengths_added':0,
                  'reference_routes_added':0,'widths_added':0,'physical_state_joins_added':0}
    return after,updated
