"""One exact five-asset display repair; no binary, data or compiler rebinding."""
import copy
import hashlib
import json
import re

KEY='dimoune_section_width_presentation_v1'
FILES={'almanac/current-dimension-evidence.js','almanac/query.html','almanac/object.html',
       'almanac/reference-routes.html','almanac/seasons.html'}
PARENT='17a45d20ac53cd91d729cec4522afa98fa3513fc4fc6073eb08ed45254e7e20a'
BINARY='628fd63dd68979d4baa168cb65b105387f9f60acae4e06ed7e57718c62621682'
LOGICAL='32b836f1015a96a5a281e082343bba81c73e2141c1f5ee438228c63f21f42607'

def presentation_manifest(parent_raw,scope,source_commit):
    if hashlib.sha256(parent_raw).hexdigest()!=PARENT:raise ValueError('Exact saved parent manifest required')
    parent=json.loads(parent_raw);rows=scope['source_changes']
    if set(rows)!=FILES or scope['parent_engine_manifest_sha256']!=PARENT or not re.fullmatch('[0-9a-f]{40}',source_commit):
        raise ValueError('Exact five display assets and source identity required')
    if KEY in parent or parent['sha256']['almanac/query-engine.wasm']!=BINARY:
        raise ValueError('Exact unapplied saved binary required')
    if parent['published_dimoune_2023_section_width_engine_v1']['logical_sha256']!=LOGICAL:
        raise ValueError('Exact saved logical packet required')
    result=copy.deepcopy(parent)
    for path,row in rows.items():
        if parent['sha256'].get(path)!=row['parent_sha256'] or not re.fullmatch('[0-9a-f]{64}',row['candidate_sha256']):
            raise ValueError('Changed parent or invalid display asset digest')
        result['sha256'][path]=row['candidate_sha256']
    result[KEY]={'schema':'osw.dimoune-section-width-presentation.v1','source_commit':source_commit,
        'parent_engine_manifest_sha256':PARENT,'logical_sha256':LOGICAL,'matching_binary_sha256':BINARY,
        'source_changes':copy.deepcopy(rows),'native_or_wasm_rebuild':False,'scientific_records_changed':0}
    if any(result[k]!=parent[k] for k in parent if k!='sha256'):raise ValueError('Historical engine namespace changed')
    return result
