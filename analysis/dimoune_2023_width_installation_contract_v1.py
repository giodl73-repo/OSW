"""Exact reviewed evidence gates for six regional section widths, not whole currents."""
import copy
from collections import Counter

ENGINE_SOURCE='d8be4d6b6113bef967ed92d7da5efffdc86b4ea5'
ENGINE_RUN=40969801784
ENGINE_ARTIFACT={'id':12940630989,'bytes':98846921,'sha256':'adc0faec299a0e94fb8d32207b34f8b21fb69533333c06bffa9972b179fc81b3'}
BROWSER_SOURCE='2fb820265f2363947997227d11bba9848e04f0a9'
BROWSER_RUN=40971781314
BROWSER_ARTIFACT={'id':12941507932,'bytes':2326314,'sha256':'b733bbf548fcad6d944712d5ba9481d800b9b3e86ec4d2c1c6200d8553a296dc'}
LOGICAL='6bbbb4ddcc3f7eb73468a81305b03f30c593c8f004a15b3dd7ad95e312792bac'
LOGICAL_BYTES=195276935
BINARY='c29ca8a11f3a21c555af3410217330385b7e6d315af08aeacbaa754b42ee2d4f'
FINAL_MANIFEST='b976e1b8c745be46313fef9dc2696f5961813b7317fb9189f52d63bd1dc66b82'
MAIN='19148702de6433253dbf412a0a28c0cb4f8e409e'
QUERY_CONTRACT='research/dimoune-2023-width-query-contract-v2.json'

def require(value,message):
    if not value:raise ValueError(message)

def verify_evidence(engine,parities,result,observed,review,final,final_manifest_bytes):
    require(engine['status']=='PASS_COMPLETE_NATIVE_WASM_CANDIDATE_BROWSER_PENDING'
        and engine['source_commit']==ENGINE_SOURCE and engine['run_id']==str(ENGINE_RUN)
        and engine['run_attempt']=='1' and engine['query_contract_file']==QUERY_CONTRACT,'Wrong corrected candidate custody')
    require(engine['logical_sha256']==LOGICAL and engine['logical_bytes']==LOGICAL_BYTES
        and engine['wasm_sha256']==BINARY and engine['rust_tests_passed']==298,'Wrong bytes or native tests')
    require(engine['source_index_audit']['original_source_strings_preserved']==656
        and engine['source_index_audit']['replaced_source_paths']==[]
        and len(engine['source_index_audit']['added_source_paths'])==4,'Historical sources changed')
    require(engine['packet_comparison']=={'historical_collections_checked':77,'existing_measurement_rows_changed':0,
        'width_records_added':6,'sources_added':1,'owner_objects_updated':4},'Unexpected data admission')
    files=copy.deepcopy(engine['generated_files'])
    require(len(files)==18 and files['almanac/query-engine.manifest.json']=={'sha256':FINAL_MANIFEST,'bytes':final_manifest_bytes},'Exact 18 saved engine files required')
    for mode,count in [('main',299),('index',97)]:
        report=parities[mode]
        require(report['status']=='PASS' and report['mode']=='compare-'+mode and len(report['checks'])==count
            and report['wasm_sha256']==BINARY and report['complete_initialization_equal'] is True,'Incomplete native/WASM comparison')
        require(all(row['entire_response_equal'] is True and row['comparison']=='exact original JSON bytes'
            for row in report['checks']),'Partial response comparison')
    require(parities['main']['payload_sha256']==LOGICAL
        and Counter(r['kind'] for r in parities['main']['checks'])=={'query':282,'snapshot':6,'object':11},'Incomplete main API inventory')
    require(Counter(r['name'] for r in parities['main']['checks'] if r['kind']=='snapshot')=={'atlas':2,'seasons':2,'dashboard':2},'Missing complete snapshots')
    require(parities['index']['mismatched_corpus_refused'] is True,'Mismatched index not refused')
    require(result['status']=='PASS_BROWSER_OBSERVATION_VISUAL_REVIEW_PENDING' and result['source_commit']==BROWSER_SOURCE
        and result['run_id']==str(BROWSER_RUN) and result['run_attempt']=='1','Wrong browser custody')
    require(result['saved_artifact']==ENGINE_ARTIFACT and result['logical_sha256']==LOGICAL
        and result['wasm_sha256']==BINARY and result['engine_manifest_sha256']==FINAL_MANIFEST
        and result['native_or_wasm_rebuild'] is False and result['installed'] is False,'Browser changed saved candidate')
    require(result['screenshots']==30 and result['browser_checks']==14,'Incomplete browser result')
    require(observed['status']=='PASS_BROWSER_OBSERVATION_VISUAL_REVIEW_PENDING'
        and not observed['page_errors'] and not observed['missing_assets'] and not observed['original_science_downloads'],'Browser errors or original science download')
    require(len(observed['checks'])==14 and Counter(r['width'] for r in observed['checks'])=={1100:7,320:7},'Both full viewport check groups required')
    screenshots=observed['screenshots']
    require(len(screenshots)==len({r['path'] for r in screenshots})==30,'Exact 30 unique screenshots required')
    require(observed['legibility'] and all(r['minimum_font_px']>=11 and r['all_text_inside_card'] is True
        for r in observed['legibility']),'Unreadable card text')
    require(review['status']=='PASS_ALL_30_ACTUAL_IMAGES_INDIVIDUALLY_INSPECTED'
        and review['independent_visual_review_complete'] is True and review['actual_images_individually_inspected']==30,'Actual visual review required')
    require(review['source_commit']==BROWSER_SOURCE and review['run_id']==BROWSER_RUN and review['run_attempt']==1
        and review['screenshots']==screenshots and review['blocking_issues']==[] and review['installed'] is False,'Visual review custody or blockers differ')
    marker=final['published_dimoune_2023_section_width_engine_v1']
    require(marker['logical_sha256']==LOGICAL and marker['matching_binary_sha256']==BINARY
        and marker['source_documents_after']==660 and marker['publication_source_rows_after']==226
        and marker['scoped_width_records_after']==185 and marker['whole_current_dimensions_added']==0
        and marker['annual_ranges_added']==0,'Wrong compiled data scope')
    return files
