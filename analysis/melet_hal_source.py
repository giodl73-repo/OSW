"""Verify the reviewed journal edition without rewriting regenerated HAL covers."""
import hashlib,io,json,re
from pathlib import Path
from pypdf import PdfReader
from pypdf.generic import (IndirectObject,StreamObject,DictionaryObject,ArrayObject,
                          ByteStringObject,TextStringObject,NameObject,BooleanObject,
                          NullObject,FloatObject,NumberObject)

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'research/source-data/melet-solomon-2010'
CONTRACT=ROOT/'research/melet-solomon-2010-journal-integrity-contract.json'
ORIGINAL_SHA='9d41af95d2ccbcee1e1469ea45d703d9cb1005ce6d1701896f4a94b5e8f1da3d'
SOURCE_URL='https://hal.science/hal-00534041v1/file/2009jpo4264_2E1.pdf'
CURRENT_FILENAME='repository-current.pdf'
CONTRACT_SHA='7ed5dbb5fb358eee0abb8f9bae177ca1e81afde85feda4d8879ff7310338c740'
_verified={}

def digest(data):return hashlib.sha256(data).hexdigest()
def encode(obj):
    if isinstance(obj,IndirectObject):return {'ref':f'{obj.idnum}:{obj.generation}'}
    if isinstance(obj,StreamObject):return {'stream':digest(obj._data),'stream_bytes':len(obj._data),'attributes':{str(k):encode(v) for k,v in sorted(obj.items())}}
    if isinstance(obj,DictionaryObject):return {'dict':{str(k):encode(v) for k,v in sorted(obj.items())}}
    if isinstance(obj,ArrayObject):return {'array':[encode(v) for v in obj]}
    if isinstance(obj,ByteStringObject):return {'bytes':bytes(obj).hex()}
    if isinstance(obj,TextStringObject):return {'text':str(obj)}
    if isinstance(obj,NameObject):return {'name':str(obj)}
    if isinstance(obj,BooleanObject):return {'bool':obj.value}
    if isinstance(obj,NullObject):return {'null':True}
    if isinstance(obj,FloatObject):return {'float':repr(float(obj))}
    if isinstance(obj,NumberObject):return {'int':int(obj)}
    raise ValueError('Unsupported scientific PDF object')

def fingerprint(value):return digest(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode())

def describe(data):
    reader=PdfReader(io.BytesIO(data),strict=True)
    if len(reader.pages)!=19 or reader.is_encrypted:raise ValueError('Changed Melet page count or encryption')
    objects={}
    for generation,entries in reader.xref.items():
        if generation==65535:continue
        for oid in entries:
            key=f'{oid}:{generation}';objects[key]=encode(reader.get_object(IndirectObject(oid,generation,reader)))
    selected=set()
    def visit(obj):
        if isinstance(obj,IndirectObject):
            key=f'{obj.idnum}:{obj.generation}'
            if key not in selected:selected.add(key);visit(obj.get_object())
        elif isinstance(obj,DictionaryObject):
            for k,v in obj.items():
                if k=='/Parent' and obj.get('/Type')=='/Page':continue
                visit(v)
        elif isinstance(obj,ArrayObject):
            for v in obj:visit(v)
    refs=[p.indirect_reference for p in reader.pages[1:]]
    for ref in refs:visit(ref)
    journal={'pages':[encode(ref) for ref in refs],'objects':{key:objects[key] for key in sorted(selected)}}
    catalog=dict(reader.trailer['/Root']);catalog.pop('/Version',None)
    info=dict(reader.metadata);creation=info.pop('/CreationDate',None)
    return {'journal_graph_sha256':fingerprint(journal),'journal_objects':len(selected),'journal_page_refs':journal['pages'],
            'object_sha256':{key:fingerprint(value) for key,value in objects.items()},
            'catalog_without_version_sha256':fingerprint(encode(DictionaryObject(catalog))),
            'metadata_without_creation_sha256':fingerprint(encode(DictionaryObject(info))),
            'catalog_version':str(reader.trailer['/Root'].get('/Version')),'creation_date':str(creation),
            'cover_text_sha256':digest(reader.pages[0].extract_text().encode())}

def verify_rendition(data,manifest):
    if len(data)>20_000_000 or not data.startswith(b'%PDF-') or not data.rstrip().endswith(b'%%EOF'):raise ValueError('Invalid bounded Melet PDF rendition')
    if manifest.get('sha256')!=ORIGINAL_SHA or manifest.get('source_url')!=SOURCE_URL:raise ValueError('Changed reviewed Melet receipt')
    raw_sha=digest(data)
    if raw_sha==ORIGINAL_SHA:return {'kind':'exact_reviewed_original','response_sha256':raw_sha}
    raw=CONTRACT.read_bytes()
    if digest(raw)!=CONTRACT_SHA:raise ValueError('Changed Melet journal integrity contract')
    contract=json.loads(raw)
    if raw_sha in _verified:return dict(_verified[raw_sha])
    result=describe(data)
    for key in ['journal_graph_sha256','journal_objects','journal_page_refs','catalog_without_version_sha256','metadata_without_creation_sha256','cover_text_sha256']:
        if result[key]!=contract[key]:raise ValueError('Changed Melet journal edition, resources or cover identity: '+key)
    if set(result['object_sha256'])!=set(contract['object_sha256']):raise ValueError('Changed Melet PDF object inventory')
    for key,pin in contract['object_sha256'].items():
        if key not in contract['generated_cover_object_ids'] and result['object_sha256'][key]!=pin:raise ValueError('Changed Melet protected PDF object: '+key)
    if result['catalog_version'] not in ['/1.5','/1.7'] or re.fullmatch(r"D:\d{14}[+-]\d{2}'\d{2}'",result['creation_date']) is None:raise ValueError('Unexpected Melet repository metadata')
    answer={'kind':'verified_generated_HAL_cover_rendition','response_sha256':raw_sha,'response_bytes':len(data),'reviewed_original_sha256':ORIGINAL_SHA,'journal_graph_sha256':result['journal_graph_sha256']}
    if len(_verified)>=8:_verified.clear()
    _verified[raw_sha]=answer
    return dict(answer)

def resolve_source(directory=None):
    directory=DIRECTORY if directory is None else Path(directory)
    manifest=json.loads((directory/'acquisition.json').read_bytes())
    original=directory/'journal-article.pdf'
    if original.exists():
        if digest(original.read_bytes())!=ORIGINAL_SHA:raise ValueError('Changed retained Melet original; no rendition fallback')
        verify_rendition(original.read_bytes(),manifest);return original
    current=directory/CURRENT_FILENAME
    verify_rendition(current.read_bytes(),manifest)
    return current

def integrity_inputs():
    resolve_source()
    return [CONTRACT.relative_to(ROOT).as_posix(),'analysis/melet_hal_source.py']
