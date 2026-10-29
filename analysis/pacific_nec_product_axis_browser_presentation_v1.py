"""Exact five-asset presentation correction; scientific candidate remains fixed."""
import copy
import re

CHANGED={'almanac/surface-product-axes.js','almanac/surface-product-axes.css','almanac/query.html','almanac/object.html','almanac/reference-routes.html'}
KEY='pacific_nec_product_axis_presentation_v1'
MANIFEST='0dc5b726c98fe3f074e15a713da5b7c42f48ea5306743ad624b8f2275db7b595'
BINARY='7507f7902eb52c43e99563c4cea27f2c1edc285a795d8cb136ca93eea6a1b427'

def presentation_manifest(parent,scope,source_commit):
    if scope.get('schema')!='osw.pacific-nec-product-axis-presentation-scope.v1' or scope.get('saved_engine_manifest_sha256')!=MANIFEST or set(scope.get('source_changes',{}))!=CHANGED or KEY in parent:raise ValueError('Exact five-asset presentation scope required')
    for key in ['scientific_inputs_changed','matching_binary_changed','native_or_wasm_rebuild_required']:
        if scope.get(key) is not False:raise ValueError('Presentation cannot alter scientific candidate')
    if parent['sha256']['almanac/query-engine.wasm']!=BINARY:raise ValueError('Exact saved binary required')
    result=copy.deepcopy(parent)
    for path,row in scope['source_changes'].items():
        if row['parent_sha256']!=parent['sha256'].get(path) or row['candidate_sha256']==row['parent_sha256'] or not re.fullmatch('[0-9a-f]{64}',row['candidate_sha256']):raise ValueError('Presentation source binding differs: '+path)
        result['sha256'][path]=row['candidate_sha256']
    result[KEY]={'source_commit':source_commit,'saved_engine_manifest_sha256':MANIFEST,'matching_binary_sha256':BINARY,'source_changes':copy.deepcopy(scope['source_changes']),'scientific_data_changed':False,'native_or_wasm_rebuild':False}
    return result
