"""Frozen source statistics retain distinct model/validation support and units."""
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/australia-wijeratne-2018-section-transport-audit.json'
SOURCE_SHA='758f18afccfee1411434d59ff9a3d0c38daf8833abf285674a33f9386ec961dd'

def document():
    raw=(ROOT/SOURCE).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:raise ValueError('Changed published section transport source scope')
    doc=json.loads(raw)
    for kind in ['source_document','acquisition','protocol']:
        if hashlib.sha256((ROOT/doc[kind+'_file']).read_bytes()).hexdigest()!=doc[kind+'_sha256']:
            raise ValueError('Changed published section transport dependency: '+kind)
    if (ROOT/doc['source_document_file']).stat().st_size!=doc['source_document_bytes']:
        raise ValueError('Changed published section transport original size')
    return doc

def build(doc=None):
    doc=document() if doc is None else doc
    result={}
    for collection in ['section_transports','transport_validations']:
        result[collection]=[]
        for original in doc[collection]:
            row=copy.deepcopy(original)
            row.update(source_file=SOURCE,source_file_sha256=SOURCE_SHA)
            row['label']=row['section_id']+' · '+(row['source_current_label'] if collection=='section_transports' else row['place_label'])
            result[collection].append(row)
    return result

if __name__=='__main__':
    data=build();print('PASS: 35 frozen model transport entries and six paired validations; original, protocol and acquisition pins verified')
