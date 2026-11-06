"""Exact reviewed evidence gates for two published regional jet widths, not whole currents."""
import copy
from collections import Counter

ENGINE_SOURCE='354ec8b1be387e1b63b153ef38986be3adff759b'
ENGINE_RUN=41029501373
ENGINE_ARTIFACT={'id':12966141942,'bytes':99115745,'sha256':'0d53e557e3d8be582f76aca2d1b444056b9e74d43456d34dd0f1999c495673b7'}
BROWSER_SOURCE='9e8608bb1f78cca95de4cd815cee67c44f98c643'
BROWSER_RUN=41033093728
BROWSER_ARTIFACT={'id':12967572502,'bytes':921348,'sha256':'08263934e5ef4b8023ed3c483dfb75f29557e79d57e75577a736d8f9f7535c8a'}
LOGICAL='7b4b5133c915102014f93a6d838e62201b0169e1b183b1d4beae65e01972bccf'
LOGICAL_BYTES=195331266
BINARY='3308ad25494a4ea1f35a18608481a4db9fe727856e87604a048fac1fbed92a21'
FINAL_MANIFEST='59ffdc89571f4e589646f029b3cbb512952e813c1001d5fe1c49f937549faa37'
MAIN='19148702de6433253dbf412a0a28c0cb4f8e409e'
QUERY_CONTRACT='research/pacific-sec-gourdeau-2008-query-contract-v1.json'

def require(value,message):
    if not value:raise ValueError(message)

def verify_evidence(engine,parities,result,observed,review,final,final_manifest_bytes):
    require(engine['status']=='PASS_COMPLETE_NATIVE_WASM_CANDIDATE_BROWSER_PENDING'
        and engine['source_commit']==ENGINE_SOURCE and engine['run_id']==str(ENGINE_RUN)
        and engine['run_attempt']=='1' and engine['query_contract_file']==QUERY_CONTRACT,'Wrong corrected candidate custody')
    require(engine['logical_sha256']==LOGICAL and engine['logical_bytes']==LOGICAL_BYTES
        and engine['wasm_sha256']==BINARY and engine['rust_tests_passed']==308,'Wrong bytes or native tests')
    require(engine['source_index_audit']['original_source_strings_preserved']==668
        and engine['source_index_audit']['replaced_source_paths']==[]
        and len(engine['source_index_audit']['added_source_paths'])==4,'Historical sources changed')
    require(engine['packet_comparison']=={'historical_collections_checked':78,'existing_measurement_rows_changed':0,
        'width_records_added':2,'sources_added':1,'owner_objects_updated':1},'Unexpected data admission')
    files=copy.deepcopy(engine['generated_files'])
    require(len(files)==18 and files['almanac/query-engine.manifest.json']=={'sha256':FINAL_MANIFEST,'bytes':final_manifest_bytes},'Exact 18 saved engine files required')
    for mode,count in [('main',354),('index',109)]:
        report=parities[mode]
        require(report['status']=='PASS' and report['mode']=='compare-'+mode and len(report['checks'])==count
            and report['wasm_sha256']==BINARY and report['complete_initialization_equal'] is True,'Incomplete native/WASM comparison')
        require(all(row['entire_response_equal'] is True and row['comparison']=='exact original JSON bytes'
            for row in report['checks']),'Partial response comparison')
    require(parities['main']['payload_sha256']==LOGICAL
        and Counter(r['kind'] for r in parities['main']['checks'])=={'query':317,'snapshot':15,'object':22},'Incomplete main API inventory')
    require(Counter(r['name'] for r in parities['main']['checks'] if r['kind']=='snapshot')=={'atlas':5,'seasons':5,'dashboard':5},'Missing complete snapshots')
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
    marker=final['published_pacific_sec_jet_widths_engine_v1']
    require(marker['logical_sha256']==LOGICAL and marker['matching_binary_sha256']==BINARY
        and marker['source_documents_after']==672 and marker['publication_source_rows_after']==229
        and marker['scoped_width_records_after']==189 and marker['whole_current_dimensions_added']==0
        and marker['annual_ranges_added']==0,'Wrong compiled data scope')
    return files
