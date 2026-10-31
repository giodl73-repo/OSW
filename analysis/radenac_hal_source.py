"""Verify the reviewed journal edition without rewriting regenerated HAL covers."""
import hashlib,io,json,re
from pathlib import Path
from pypdf import PdfReader
from pypdf.generic import IndirectObject, DictionaryObject, ArrayObject

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'research/source-data/radenac-ngcc-2016'
CONTRACT=ROOT/'research/radenac-ngcc-2016-journal-integrity-contract.json'
ORIGINAL_SHA='6da50667b80790752fa0189ff9cf0cdfd88c521509b0f393365de306286bacbe'
SOURCE_URL='https://hal.science/hal-01497605/document'
CURRENT_FILENAME='repository-current.pdf'
CONTRACT_SHA='e617cde1268d02fbb50bc4b1ca2266685f32886a5716b36b143b2a634745f7ae'
_verified={}

def digest(data):return hashlib.sha256(data).hexdigest()
from melet_hal_source import encode, fingerprint

def describe(data):
    reader=PdfReader(io.BytesIO(data),strict=True)
    if len(reader.pages)!=23 or reader.is_encrypted:raise ValueError('Changed Radenac page count or encryption')
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
    return {'journal_graph_sha256':fingerprint(journal),'journal_objects':len(selected),'journal_object_ids':sorted(selected),'journal_page_refs':journal['pages'],
            'object_sha256':{key:fingerprint(value) for key,value in objects.items()},
            'catalog_without_version_sha256':fingerprint(encode(DictionaryObject(catalog))),
            'metadata_without_creation_sha256':fingerprint(encode(DictionaryObject(info))),
            'catalog_version':str(reader.trailer['/Root'].get('/Version')),'creation_date':str(creation),
            'cover_text_sha256':digest(reader.pages[0].extract_text().encode())}

def verify_rendition(data,manifest):
    if len(data)>20_000_000 or not data.startswith(b'%PDF-') or not data.rstrip().endswith(b'%%EOF'):raise ValueError('Invalid bounded Radenac PDF rendition')
    if manifest.get('sha256')!=ORIGINAL_SHA or manifest.get('source_url')!=SOURCE_URL:raise ValueError('Changed reviewed Radenac receipt')
    raw_sha=digest(data)
    if raw_sha==ORIGINAL_SHA:return {'kind':'exact_reviewed_original','response_sha256':raw_sha}
    raw=CONTRACT.read_bytes()
    if digest(raw)!=CONTRACT_SHA:raise ValueError('Changed Radenac journal integrity contract')
    contract=json.loads(raw)
    if raw_sha in _verified:return dict(_verified[raw_sha])
    result=describe(data)
    for key in ['journal_graph_sha256','journal_objects','journal_object_ids','journal_page_refs','catalog_without_version_sha256','metadata_without_creation_sha256','cover_text_sha256']:
        if result[key]!=contract[key]:raise ValueError('Changed Radenac journal edition, resources or cover identity: '+key)
    if set(result['object_sha256'])!=set(contract['object_sha256']):raise ValueError('Changed Radenac PDF object inventory')
    for key,pin in contract['object_sha256'].items():
        if key not in contract['generated_cover_object_ids'] and result['object_sha256'][key]!=pin:raise ValueError('Changed Radenac protected PDF object: '+key)
    if result['catalog_version'] not in ['/1.5','/1.7'] or re.fullmatch(r"D:\d{14}[+-]\d{2}'\d{2}'",result['creation_date']) is None:raise ValueError('Unexpected Radenac repository metadata')
    answer={'kind':'verified_generated_HAL_cover_rendition','response_sha256':raw_sha,'response_bytes':len(data),'reviewed_original_sha256':ORIGINAL_SHA,'journal_graph_sha256':result['journal_graph_sha256']}
    if len(_verified)>=8:_verified.clear()
    _verified[raw_sha]=answer
    return dict(answer)

def resolve_source(directory=None):
    directory=DIRECTORY if directory is None else Path(directory)
    manifest=json.loads((directory/'acquisition.json').read_bytes())
    original=directory/'journal-article.pdf'
    if original.exists():
        if digest(original.read_bytes())!=ORIGINAL_SHA:raise ValueError('Changed retained Radenac original; no rendition fallback')
        verify_rendition(original.read_bytes(),manifest);return original
    current=directory/CURRENT_FILENAME
    verify_rendition(current.read_bytes(),manifest)
    return current

def integrity_inputs():
    resolve_source()
    return [CONTRACT.relative_to(ROOT).as_posix(),'analysis/radenac_hal_source.py']
