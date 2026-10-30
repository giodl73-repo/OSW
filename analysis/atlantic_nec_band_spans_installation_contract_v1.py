"""Exact reviewed evidence gates for two regional latitude-band spans, not whole currents."""
import copy
from collections import Counter

ENGINE_SOURCE='f674bb458f14e9e2e53c85dea8f321d2640d9589'
ENGINE_RUN=40985592814
ENGINE_ARTIFACT={'id':12946918054,'bytes':98884702,'sha256':'a2feb207e07ff254b651f3eacb37a46f43bb99c1c9f4d106b4327e47a50275b9'}
BROWSER_SOURCE='c04d079480dd19abf9099f880844f2208219c533'
BROWSER_RUN=40987922897
BROWSER_ARTIFACT={'id':12948019297,'bytes':1204269,'sha256':'fd3c8e3e8f6b387e96939c5565ccc0b48cf5997cd0e9510f073a99e345a29c25'}
LOGICAL='404de2dee8ca4fc4968f24a23f892b336bd5392d8b44a3556206a8944e2b2e3a'
LOGICAL_BYTES=195287491
BINARY='d72dbe2d7c4c2200b104237428a3fa49a7b0dd05b2fce4fbf2ce9358c33c9e22'
FINAL_MANIFEST='0d6f469fe5849cd95f447280eee842f158711dc0b7016102319d3fef316dd54b'
MAIN='19148702de6433253dbf412a0a28c0cb4f8e409e'
QUERY_CONTRACT='research/atlantic-nec-stramma-2005-query-contract-v1.json'

def require(value,message):
    if not value:raise ValueError(message)

def verify_evidence(engine,parities,result,observed,review,final,final_manifest_bytes):
    require(engine['status']=='PASS_COMPLETE_NATIVE_WASM_CANDIDATE_BROWSER_PENDING'
        and engine['source_commit']==ENGINE_SOURCE and engine['run_id']==str(ENGINE_RUN)
        and engine['run_attempt']=='1' and engine['query_contract_file']==QUERY_CONTRACT,'Wrong corrected candidate custody')
    require(engine['logical_sha256']==LOGICAL and engine['logical_bytes']==LOGICAL_BYTES
        and engine['wasm_sha256']==BINARY and engine['rust_tests_passed']==301,'Wrong bytes or native tests')
    require(engine['source_index_audit']['original_source_strings_preserved']==660
        and engine['source_index_audit']['replaced_source_paths']==[]
        and len(engine['source_index_audit']['added_source_paths'])==4,'Historical sources changed')
    require(engine['packet_comparison']=={'historical_collections_checked':77,'existing_measurement_rows_changed':0,
        'width_records_added':2,'sources_added':1,'owner_objects_updated':1},'Unexpected data admission')
    files=copy.deepcopy(engine['generated_files'])
    require(len(files)==18 and files['almanac/query-engine.manifest.json']=={'sha256':FINAL_MANIFEST,'bytes':final_manifest_bytes},'Exact 18 saved engine files required')
    for mode,count in [('main',309),('index',101)]:
        report=parities[mode]
        require(report['status']=='PASS' and report['mode']=='compare-'+mode and len(report['checks'])==count
            and report['wasm_sha256']==BINARY and report['complete_initialization_equal'] is True,'Incomplete native/WASM comparison')
        require(all(row['entire_response_equal'] is True and row['comparison']=='exact original JSON bytes'
            for row in report['checks']),'Partial response comparison')
    require(parities['main']['payload_sha256']==LOGICAL
        and Counter(r['kind'] for r in parities['main']['checks'])=={'query':288,'snapshot':9,'object':12},'Incomplete main API inventory')
    require(Counter(r['name'] for r in parities['main']['checks'] if r['kind']=='snapshot')=={'atlas':3,'seasons':3,'dashboard':3},'Missing complete snapshots')
    require(parities['index']['mismatched_corpus_refused'] is True,'Mismatched index not refused')
    require(result['status']=='PASS_BROWSER_OBSERVATION_VISUAL_REVIEW_PENDING' and result['source_commit']==BROWSER_SOURCE
        and result['run_id']==str(BROWSER_RUN) and result['run_attempt']=='1','Wrong browser custody')
    require(result['saved_artifact']==ENGINE_ARTIFACT and result['logical_sha256']==LOGICAL
        and result['wasm_sha256']==BINARY and result['engine_manifest_sha256']==FINAL_MANIFEST
        and result['native_or_wasm_rebuild'] is False and result['installed'] is False,'Browser changed saved candidate')
    require(result['screenshots']==22 and result['browser_checks']==14,'Incomplete browser result')
    require(observed['status']=='PASS_BROWSER_OBSERVATION_VISUAL_REVIEW_PENDING'
        and not observed['page_errors'] and not observed['missing_assets'] and not observed['original_science_downloads'],'Browser errors or original science download')
    require(len(observed['checks'])==14 and Counter(r['width'] for r in observed['checks'])=={1100:7,320:7},'Both full viewport check groups required')
    screenshots=observed['screenshots']
    require(len(screenshots)==len({r['path'] for r in screenshots})==22,'Exact 22 unique screenshots required')
    require(observed['legibility'] and all(r['minimum_font_px']>=11 and r['all_text_inside_card'] is True
        for r in observed['legibility']),'Unreadable card text')
    require(review['status']=='PASS_ALL_22_ACTUAL_IMAGES_INDIVIDUALLY_INSPECTED'
        and review['independent_visual_review_complete'] is True and review['actual_images_individually_inspected']==22,'Actual visual review required')
    require(review['source_commit']==BROWSER_SOURCE and review['run_id']==BROWSER_RUN and review['run_attempt']==1
        and review['screenshots']==screenshots and review['blocking_issues']==[] and review['installed'] is False,'Visual review custody or blockers differ')
    marker=final['published_atlantic_nec_band_spans_engine_v1']
    require(marker['logical_sha256']==LOGICAL and marker['matching_binary_sha256']==BINARY
        and marker['source_documents_after']==664 and marker['publication_source_rows_after']==227
        and marker['scoped_width_records_after']==187 and marker['whole_current_dimensions_added']==0
        and marker['annual_ranges_added']==0,'Wrong compiled data scope')
    return files
