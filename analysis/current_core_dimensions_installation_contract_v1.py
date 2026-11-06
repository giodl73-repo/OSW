"""Exact custody for one regional reach and one cited width plus bounded atlas loading."""
import copy
import hashlib
import current_core_dimensions_atlas_presentation_v1 as presentation
from collections import Counter

ENGINE_SOURCE='ab9cc0118e56fa752065ee68d552405280db276b'
ENGINE_RUN=41043869467
ENGINE_ARTIFACT={'id':12971394522,'bytes':99173291,'sha256':'2a63ae309295e34f99c50a7c23993b46c850442e2d56aefdb20b37459bdd3610'}
BROWSER_SOURCE='7c7cc5c651b73d3ece0a9db9a49d85fbad7c93e0'
BROWSER_RUN=41046858721
BROWSER_ARTIFACT={'id':12975465077,'bytes':1889514,'sha256':'829d1a5c1c9230182420395fe5255d8bbb18116ba69adf2af50490342706ce01'}
LOGICAL='191874b005d09c9680e13e5f1fd037a4045a47bbc709782318c3a3d5561d5127'
LOGICAL_BYTES=195343885
BINARY='208ae406cc8b49094885f3015a6e3ff601d5bac395374682b53ec4703e2da82e'
FINAL_MANIFEST='fd57024ad29cacd4614d6667dfe061e39e290ddfe6c8dd53cbb8ee91a4fcbcba'
MAIN='19148702de6433253dbf412a0a28c0cb4f8e409e'
ORIGINAL_MANIFEST='06d618d3daed9d3aabfa51cb5bfd67d13b0ab36a6d0ee6290161b3840c48462a'
FOCUSED_SOURCE='17cd6a8ce347dbd966c5c52a1030d64522ac7ccc'
FOCUSED_RUN=41054770321
FOCUSED_ARTIFACT={'id':12976886234,'bytes':601670,'sha256':'1aa1e8693e8d4e833c0a4a1d1f8e88b793548c9353d2a0c129390cf3f17d4bfc'}
QUERY_CONTRACT='research/current-core-dimensions-query-contract-v1.json'

def require(value,message):
    if not value:raise ValueError(message)

def verify_evidence(engine,parities,result,observed,review,final,final_raw,focused_result,focused_observed,original_raw):
    require(engine['status']=='PASS_COMPLETE_NATIVE_WASM_CANDIDATE_BROWSER_PENDING'
        and engine['source_commit']==ENGINE_SOURCE and engine['run_id']==str(ENGINE_RUN)
        and engine['run_attempt']=='1' and engine['query_contract_file']==QUERY_CONTRACT,'Wrong corrected candidate custody')
    require(engine['logical_sha256']==LOGICAL and engine['logical_bytes']==LOGICAL_BYTES
        and engine['wasm_sha256']==BINARY and engine['rust_tests_passed']==311,'Wrong bytes or native tests')
    require(engine['source_index_audit']['original_source_strings_preserved']==672
        and engine['source_index_audit']['replaced_source_paths']==[]
        and len(engine['source_index_audit']['added_source_paths'])==6,'Historical sources changed')
    require(engine['packet_comparison']=={'historical_collections_checked':78,'existing_measurement_rows_changed':0,
        'width_records_added':1,'regional_reaches_added':1,'sources_added':2,'owner_objects_updated':2},'Unexpected data admission')
    files=copy.deepcopy(engine['generated_files'])
    require(len(files)==18 and files['almanac/query-engine.manifest.json']=={'sha256':ORIGINAL_MANIFEST,'bytes':len(original_raw)},'Exact 18 original saved engine files required')
    require(hashlib.sha256(final_raw).hexdigest()==FINAL_MANIFEST,'Final presentation manifest bytes differ')
    updates=final[presentation.KEY]['presentation_sha256']
    require(final==presentation.overlay(original_raw,updates),'Unrelated engine namespace changed')
    files['almanac/query-engine.manifest.json']={'sha256':FINAL_MANIFEST,'bytes':len(final_raw)}
    for mode,count in [('main',372),('index',115)]:
        report=parities[mode]
        require(report['status']=='PASS' and report['mode']=='compare-'+mode and len(report['checks'])==count
            and report['wasm_sha256']==BINARY and report['complete_initialization_equal'] is True,'Incomplete native/WASM comparison')
        require(all(row['entire_response_equal'] is True and row['comparison']=='exact original JSON bytes'
            for row in report['checks']),'Partial response comparison')
    require(parities['main']['payload_sha256']==LOGICAL
        and Counter(r['kind'] for r in parities['main']['checks'])=={'query':329,'snapshot':18,'object':25},'Incomplete main API inventory')
    require(Counter(r['name'] for r in parities['main']['checks'] if r['kind']=='snapshot')=={'atlas':6,'seasons':6,'dashboard':6},'Missing complete snapshots')
    require(parities['index']['mismatched_corpus_refused'] is True,'Mismatched index not refused')
    require(result['status']=='PASS_BROWSER_OBSERVATION_VISUAL_REVIEW_PENDING' and result['source_commit']==BROWSER_SOURCE
        and result['run_id']==str(BROWSER_RUN) and result['run_attempt']=='1','Wrong browser custody')
    require(result['saved_artifact']==ENGINE_ARTIFACT and result['logical_sha256']==LOGICAL
        and result['wasm_sha256']==BINARY and result['engine_manifest_sha256']==ORIGINAL_MANIFEST
        and result['native_or_wasm_rebuild'] is False and result['installed'] is False,'Browser changed saved candidate')
    require(result['screenshots']==29 and result['browser_checks']==23,'Incomplete browser result')
    require(observed['status']=='PASS_BROWSER_OBSERVATION_VISUAL_REVIEW_PENDING'
        and not observed['page_errors'] and not observed['missing_assets'] and not observed['original_science_downloads'],'Browser errors or original science download')
    require(len(observed['checks'])==23 and Counter(r['width'] for r in observed['checks'])=={1100:12,320:11},'Both full viewport check groups required')
    screenshots=observed['screenshots']
    require(len(screenshots)==len({r['path'] for r in screenshots})==29,'Exact 29 unique screenshots required')
    require(observed['legibility'] and all(r['minimum_font_px']>=11 and r['all_text_inside_card'] is True
        for r in observed['legibility']),'Unreadable card text')
    require(review['status']=='PASS_ALL_33_ACTUAL_IMAGES_INDIVIDUALLY_INSPECTED'
        and review['independent_visual_review_complete'] is True and review['actual_images_individually_inspected']==33,'Actual visual review required')
    require(review['primary_source_commit']==BROWSER_SOURCE and review['primary_run_id']==BROWSER_RUN
        and review['primary_screenshots']==screenshots and review['blocking_issues']==[] and review['installed'] is False,'Primary visual review custody differs')
    require(focused_result['source_commit']==FOCUSED_SOURCE and focused_result['run_id']==str(FOCUSED_RUN)
        and focused_result['run_attempt']=='1' and focused_result['status']=='PASS_BROWSER_OBSERVATION_VISUAL_REVIEW_PENDING'
        and focused_result['saved_artifact']==ENGINE_ARTIFACT and focused_result['logical_sha256']==LOGICAL
        and focused_result['wasm_sha256']==BINARY and focused_result['engine_manifest_sha256']==FINAL_MANIFEST
        and focused_result['original_engine_manifest_sha256']==ORIGINAL_MANIFEST
        and focused_result['native_or_wasm_rebuild'] is False and focused_result['installed'] is False,'Focused presentation custody differs')
    require(not focused_observed['page_errors'] and not focused_observed['missing_assets']
        and not focused_observed['original_science_downloads'] and focused_observed['css_or_layout_modified_for_capture'] is False,'Focused runtime error or capture layout changed')
    expected={(owner,position) for owner in ['current:red-sea-saline-overflow','current:indian-south-equatorial'] for position in ['top','bottom']}
    require(len(focused_observed['checks'])==4 and {(r['owner'],r['position']) for r in focused_observed['checks']}==expected
        and all(r['width']==1100 and r['probe']['visible'] and r['probe']['hit'] for r in focused_observed['checks']),'Incomplete focused pane coverage')
    require(focused_result['browser_checks']==4 and focused_result['screenshots']==4
        and len(focused_observed['screenshots'])==len({r['path'] for r in focused_observed['screenshots']})==4
        and review['focused_screenshots']==focused_observed['screenshots'] and review['focused_source_commit']==FOCUSED_SOURCE
        and review['focused_run_id']==FOCUSED_RUN and review['focused_artifact']==FOCUSED_ARTIFACT,'Focused images not reviewed')
    loads=focused_observed['atlas_load_observations']
    require(len(loads)==2 and loads[0]['cold_browser_context'] is True
        and all(r['status']['phase']=='ready' and r['status']['settled'] is True
            and [p['phase'] for p in r['status']['completed_phases']]==['load','atlas']
            and all(0<=p['elapsed_ms']<=90000 for p in r['status']['completed_phases']) for r in loads),'Cold bounded atlas entry not proven')
    marker=final['published_current_core_dimensions_engine_v1']
    require(marker['logical_sha256']==LOGICAL and marker['matching_binary_sha256']==BINARY
        and marker['source_documents_after']==678 and marker['publication_source_rows_after']==231
        and marker['scoped_width_records_after']==190 and marker['whole_current_dimensions_added']==0
        and marker['annual_ranges_added']==0,'Wrong compiled data scope')
    return files
