"""Exact cumulative navigation/responsive source overlay; scientific engine stays fixed."""
import copy
import re
from chen_indian_sec_browser_contract_v1 import SOURCE,RUN,ARTIFACT,LOGICAL,BINARY,MANIFEST_SHA,verify_saved_result

CHANGED={'almanac/query.js','almanac/query.html','almanac/object.html',
         'almanac/reference-routes.html','almanac/regional-model-lengths.js'}
ADDED={'almanac/regional-model-lengths.css'}
KEY='indian_sec_responsive_presentation_v1'


def presentation_manifest(parent,scope,source_commit):
    if (scope.get('schema')!='osw.chen-indian-sec-responsive-source-scope.v1'
            or scope.get('saved_engine_manifest_sha256')!=MANIFEST_SHA
            or set(scope['source_changes'])!=CHANGED or set(scope['added_source_sha256'])!=ADDED
            or KEY in parent):raise ValueError('Exact responsive presentation scope required')
    for key in ('scientific_inputs_changed','matching_binary_changed','native_or_wasm_rebuild_required'):
        if scope.get(key) is not False:raise ValueError('Presentation cannot change scientific engine')
    if parent['sha256']['almanac/query-engine.wasm']!=BINARY:raise ValueError('Wrong saved binary')
    result=copy.deepcopy(parent)
    for path,row in scope['source_changes'].items():
        if (row['parent_sha256']!=parent['sha256'].get(path)
                or row['candidate_sha256']==row['parent_sha256']
                or not re.fullmatch('[0-9a-f]{64}',row['candidate_sha256'])):
            raise ValueError('Wrong responsive source binding: '+path)
        result['sha256'][path]=row['candidate_sha256']
    for path,pin in scope['added_source_sha256'].items():
        if path in parent['sha256'] or not re.fullmatch('[0-9a-f]{64}',pin):raise ValueError('Wrong added stylesheet')
        result['sha256'][path]=pin
    result[KEY]={'source_commit':source_commit,'parent_engine_source_commit':SOURCE,
        'parent_engine_manifest_sha256':MANIFEST_SHA,'matching_binary_sha256':BINARY,
        'source_changes':copy.deepcopy(scope['source_changes']),
        'added_source_sha256':copy.deepcopy(scope['added_source_sha256']),
        'preceding_navigation_scope_sha256':scope['preceding_navigation_scope_sha256'],
        'scientific_data_changed':False,'native_or_wasm_rebuild':False}
    return result
