"""Pure saved-engine and presentation-overlay contracts for browser observation."""
import copy

SOURCE='0e4a4aa3434c30389ce7632cc9ef4c2781fd5f24'
RUN=40864421024
ARTIFACT={'id':12893571805,'bytes':96721323,'sha256':'672c4af33e19942fb2b9299777db81491a17559e178cb9de163ac7e9e362743f'}
LOGICAL='000ec593c4fd1eb597a0a7204824b5c8c8e19cd8e2683080095a46ec50609cb1'
BINARY='a4a315990572dfcf909a7bb188c80ccf97577d6f4a8b38e57f1760b31acd8245'
MANIFEST_SHA='73c20e5e4831abd201b363723c3c7b605b3c1efcbe3c0e3735c35945fc6f348d'
NAV_KEY='indian_sec_query_navigation_presentation_v1'
NAV_PATHS={'almanac/query.js','almanac/query.html'}


def verify_saved_result(result):
    required={'status':'PASS_MATCHED_NATIVE_WASM_ENGINE_BROWSER_PENDING','source_commit':SOURCE,
              'logical_sha256':LOGICAL,'logical_bytes':191109635,'wasm_sha256':BINARY,
              'rust_tests_passed':289,'historical_main_queries':215,'historical_source_queries':79,
              'new_main_queries':9,'new_source_queries':7,'complete_api_snapshots':3,'complete_object_apis':7,
              'browser_review_completed':False,'installed':False,'main_updated':False,'full_goal_complete':False}
    if any(type(result.get(k)) is not type(v) or result[k]!=v for k,v in required.items()):
        raise ValueError('Exact independently verified saved engine required')
    files=result['generated_files']
    if (len(files)!=18 or files['almanac/query-engine.manifest.json']['sha256']!=MANIFEST_SHA
            or files['almanac/query-engine.wasm']['sha256']!=BINARY
            or sum(p.startswith('almanac/query-parts/') for p in files)!=12):
        raise ValueError('Changed saved engine inventory')
    return files


def navigation_manifest(parent,scope,source_commit):
    if (scope.get('schema')!='osw.chen-indian-sec-query-navigation-source-scope.v1'
            or scope.get('saved_engine_manifest_sha256')!=MANIFEST_SHA
            or set(scope['source_changes'])!=NAV_PATHS or NAV_KEY in parent):
        raise ValueError('Exact two-file navigation scope required')
    if parent['sha256']['almanac/query-engine.wasm']!=BINARY:
        raise ValueError('Navigation overlay cannot change binary')
    result=copy.deepcopy(parent)
    for path,row in scope['source_changes'].items():
        if row['parent_sha256']!=parent['sha256'].get(path):
            raise ValueError('Wrong navigation parent source: '+path)
        if row['candidate_sha256']==row['parent_sha256']:
            raise ValueError('Navigation change must be explicit')
        result['sha256'][path]=row['candidate_sha256']
    result[NAV_KEY]={'source_commit':source_commit,'parent_engine_source_commit':SOURCE,
        'parent_engine_manifest_sha256':MANIFEST_SHA,'source_changes':copy.deepcopy(scope['source_changes']),
        'matching_binary_sha256':BINARY,'scientific_data_changed':False,'native_or_wasm_rebuild':False}
    return result
