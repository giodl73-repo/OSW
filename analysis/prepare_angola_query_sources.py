"""Lossless decoded mirrors for the Rust source index; no new measurements."""
import gzip
import hashlib
import json
from angola_nansen_native_sections import ROOT, REPORT, reserve

DIRECTORY='research/angola-nansen-query-fields-v1'
MANIFEST='research/angola-nansen-query-source-manifest-v1.json'
OPERATOR='analysis/prepare_angola_query_sources.py'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def source_documents():
    report=json.loads((ROOT/REPORT).read_bytes())
    return [{'section_id':row['id'],'source_file':DIRECTORY+'/'+row['id'].split(':')[1]+'.json',
             'source_sha256':row['decoded_sha256'],'source_bytes':row['decoded_bytes'],
             'compressed_source_file':row['field_file'],'compressed_source_sha256':row['field_sha256']}
            for row in report['sections']]


def expected_manifest():
    return {'schema':'osw.angola-nansen-query-mirrors.v1','source_report':REPORT,
            'source_report_sha256':sha((ROOT/REPORT).read_bytes()),
            'scope':'Exact decoded JSON mirrors of frozen native fields for Rust/WASM queries; no numeric transformation or measurement admission.',
            'documents':source_documents(),'physical_width_admitted':False,
            'canonical_current_identity_admitted':False}


def encoded(doc):return (json.dumps(doc,ensure_ascii=False,indent=2)+'\n').encode('utf8')


def verify():
    expected=expected_manifest()
    if (ROOT/MANIFEST).read_bytes()!=encoded(expected):raise ValueError('Changed native query-source mirror manifest')
    for row in expected['documents']:
        raw=(ROOT/row['source_file']).read_bytes()
        if len(raw)!=row['source_bytes'] or sha(raw)!=row['source_sha256']:
            raise ValueError('Changed exact native query-source mirror: '+row['source_file'])
    return expected


def prepare():
    reserve();directory=ROOT/DIRECTORY;directory.mkdir(exist_ok=True)
    for row in source_documents():
        packed=(ROOT/row['compressed_source_file']).read_bytes()
        if sha(packed)!=row['compressed_source_sha256']:raise ValueError('Changed frozen compressed native field')
        raw=gzip.decompress(packed)
        if len(raw)!=row['source_bytes'] or sha(raw)!=row['source_sha256']:raise ValueError('Changed frozen decoded native field')
        target=ROOT/row['source_file']
        if target.exists():
            if target.read_bytes()!=raw:raise ValueError('Retain differing query mirror; do not overwrite: '+str(target))
        else:target.write_bytes(raw)
    target=ROOT/MANIFEST;raw=encoded(expected_manifest())
    if target.exists():
        if target.read_bytes()!=raw:raise ValueError('Retain differing query mirror manifest')
    else:target.write_bytes(raw)
    return verify()


if __name__=='__main__':
    doc=prepare();print('Verified exact decoded source mirrors:',len(doc['documents']))
