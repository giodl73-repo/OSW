"""Exact reviewed evidence gates for ten historical characteristic velocity summaries."""
import copy
from collections import Counter

ENGINE_SOURCE='ffa9275c6a7271ec0974c7bbba4579de994edfd3'
ENGINE_RUN=41009487072
ENGINE_ARTIFACT={'id':12957143941,'bytes':99102487,'sha256':'3361186e72365eeceb679fee9c79c301e76780144eda8197df136e88a73738fa'}
BROWSER_SOURCE='d105ebcc2644e7d1106ccd7d0af6d4ed6df6afd0'
BROWSER_RUN=41014967906
BROWSER_ARTIFACT={'id':12959799952,'bytes':1216759,'sha256':'6a09bf78dd78f2787359ae409eda7a82739b536e5784d9eeaf4590ad9a3e50da'}
LOGICAL='d21ade39ba095192df3f4c6adef702d0d5f68570ea736f455eaf84980d9800ea'
LOGICAL_BYTES=195320893
BINARY='536521a9aca1ab106bb8cb7445786c8fb224f08cec58e1aa7141dad0b8c9604e'
FINAL_MANIFEST='1f583dfe3eb9701cdcf116b2ee5cae1190c45c413f2c360baf798d147df1d728'
MAIN='19148702de6433253dbf412a0a28c0cb4f8e409e'
QUERY_CONTRACT='research/richardson-walsh-1986-characteristic-velocity-query-contract-v1.json'

def require(value,message):
    if not value:raise ValueError(message)

def verify_evidence(engine,parities,result,observed,review,final,final_manifest_bytes):
    require(engine['status']=='PASS_COMPLETE_NATIVE_WASM_CANDIDATE_BROWSER_PENDING'
        and engine['source_commit']==ENGINE_SOURCE and engine['run_id']==str(ENGINE_RUN)
        and engine['run_attempt']=='1' and engine['query_contract_file']==QUERY_CONTRACT,'Wrong corrected candidate custody')
    require(engine['logical_sha256']==LOGICAL and engine['logical_bytes']==LOGICAL_BYTES
        and engine['wasm_sha256']==BINARY and engine['rust_tests_passed']==304,'Wrong bytes or native tests')
    require(engine['source_index_audit']['original_sources_verified']==664
        and engine['source_index_audit']['original_source_strings_preserved']==664
        and engine['source_index_audit']['replaced_source_paths']==[]
        and len(engine['source_index_audit']['added_source_paths'])==4,'Historical sources changed')
    require(engine['packet_comparison']=={'historical_collections_checked':77,'existing_measurement_rows_changed':0,'collections_added':1,
        'characteristic_velocity_records_added':10,'sources_added':1,'owner_objects_updated':8,'width_records_added':0,'length_records_added':0},'Unexpected data admission')
    files=copy.deepcopy(engine['generated_files'])
    require(len(files)==18 and files['almanac/query-engine.manifest.json']=={'sha256':FINAL_MANIFEST,'bytes':final_manifest_bytes},'Exact 18 saved engine files required')
    for mode,count in [('main',343),('index',105)]:
        report=parities[mode]
        require(report['status']=='PASS' and report['mode']=='compare-'+mode and len(report['checks'])==count
            and report['wasm_sha256']==BINARY and report['complete_initialization_equal'] is True,'Incomplete native/WASM comparison')
        require(all(row['entire_response_equal'] is True and row['comparison']=='exact original JSON bytes'
            for row in report['checks']),'Partial response comparison')
    require(parities['main']['payload_sha256']==LOGICAL
        and Counter(r['kind'] for r in parities['main']['checks'])=={'query':311,'snapshot':12,'object':20},'Incomplete main API inventory')
    require(Counter(r['name'] for r in parities['main']['checks'] if r['kind']=='snapshot')=={'atlas':4,'seasons':4,'dashboard':4},'Missing complete snapshots')
    require(parities['index']['mismatched_corpus_refused'] is True,'Mismatched index not refused')
    require(result['status']=='PASS_BROWSER_OBSERVATION_VISUAL_REVIEW_PENDING' and result['source_commit']==BROWSER_SOURCE
        and result['run_id']==str(BROWSER_RUN) and result['run_attempt']=='1','Wrong browser custody')
    require(result['saved_engine_source']==ENGINE_SOURCE and result['saved_engine_run']==ENGINE_RUN
        and result['saved_artifact']==ENGINE_ARTIFACT and result['logical_sha256']==LOGICAL
        and result['wasm_sha256']==BINARY and result['engine_manifest_sha256']==FINAL_MANIFEST
        and result['native_or_wasm_rebuild'] is False and result['installed'] is False,'Browser changed saved candidate')
    require(result['screenshots']==32 and result['browser_checks']==12,'Incomplete browser result')
    require(observed['status']=='PASS_BROWSER_OBSERVATION_VISUAL_REVIEW_PENDING'
        and not observed['page_errors'] and not observed['missing_assets'] and not observed['original_science_downloads'],'Browser errors or original science download')
    require(len(observed['checks'])==12 and Counter(r['width'] for r in observed['checks'])=={1100:6,320:6},'Both full viewport check groups required')
    screenshots=observed['screenshots']
    require(len(screenshots)==len({r['path'] for r in screenshots})==32,'Exact 32 unique screenshots required')
    require(observed['legibility'] and all(r['minimum_font_px']>=11 and r['all_text_inside_card'] is True
        for r in observed['legibility']),'Unreadable card text')
    require(review['status']=='PASS_ALL_32_ACTUAL_IMAGES_INDIVIDUALLY_INSPECTED'
        and review['independent_visual_review_complete'] is True and review['actual_images_individually_inspected']==32,'Actual visual review required')
    require(review['source_commit']==BROWSER_SOURCE and review['run_id']==BROWSER_RUN and review['run_attempt']==1
        and review['screenshots']==screenshots and review['blocking_issues']==[] and review['installed'] is False,'Visual review custody or blockers differ')
    marker=final['published_characteristic_velocities_engine_v1']
    require(marker['logical_sha256']==LOGICAL and marker['matching_binary_sha256']==BINARY
        and marker['source_documents_after']==668 and marker['publication_source_rows_after']==228
        and marker['characteristic_velocity_records_after']==10 and marker['collections_after']==78
        and marker['scoped_width_records_after']==187 and marker['whole_current_dimensions_added']==0
        and marker['annual_ranges_added']==0,'Wrong compiled data scope')
    return files
