"""Pure evidence gates for the exact reviewed Pacific NEC diagnostic candidate."""
import copy
from collections import Counter
from pacific_nec_product_axis_browser_presentation_v1 import presentation_manifest

ENGINE_SOURCE='6c24a0db510599df803fad9516033c48c2ba520e'
ENGINE_RUN=40909369948
ENGINE_ARTIFACT={'id':12913028078,'bytes':98658436,'sha256':'4578a31d981826b7de3f3f8e2d6c46d899083bfe0d123cf2810f1d988cade696'}
BROWSER_SOURCE='0961ba6938d043d93c58e0ccf5729a62aaaf46ac'
BROWSER_RUN=40914032525
BROWSER_ARTIFACT={'id':12916716378,'bytes':2172858,'sha256':'1a023739373b69272251d5293132eb8065f52e83f488698cf0f9b2710a286dec'}
LOGICAL='dc671a2af236089e37c02489e0cba6bea52e81298879abf0ea809f8d9552a936'
LOGICAL_BYTES=195248051
BINARY='7507f7902eb52c43e99563c4cea27f2c1edc285a795d8cb136ca93eea6a1b427'
FINAL_MANIFEST='f3a5008f7a1f30a386ec27825e46bab337f0aa6857275fb0c3e56a96ce55a967'
MAIN='19148702de6433253dbf412a0a28c0cb4f8e409e'

def require(value,message):
    if not value:raise ValueError(message)

def verify_evidence(engine,parities,result,observed,review,original,final,scope,final_manifest_bytes):
    require(engine['status']=='PASS_COMPLETE_NATIVE_WASM_CANDIDATE_BROWSER_PENDING' and engine['source_commit']==ENGINE_SOURCE and engine['run_id']==str(ENGINE_RUN) and engine['run_attempt']=='1','Wrong candidate custody')
    require(engine['logical_sha256']==LOGICAL and engine['logical_bytes']==LOGICAL_BYTES and engine['wasm_sha256']==BINARY and engine['rust_tests_passed']==295,'Wrong candidate bytes or tests')
    require(engine['source_index_audit']['original_source_strings_preserved']==649 and engine['source_index_audit']['replaced_source_paths']==[] and engine['packet_comparison']['canonical_measurement_rows_changed']==0,'Historical evidence changed')
    files=copy.deepcopy(engine['generated_files']);require(len(files)==18,'Exact 18 candidate files required')
    for mode,count in [('main',276),('index',93)]:
        report=parities[mode]
        require(report['status']=='PASS' and len(report['checks'])==count and report['wasm_sha256']==BINARY and report['complete_initialization_equal'] is True,'Incomplete matching native/WASM comparison')
        require(all(row['entire_response_equal'] is True for row in report['checks']),'Partial response comparison')
    require(parities['main']['payload_sha256']==LOGICAL and Counter(r['kind'] for r in parities['main']['checks'])=={'query':266,'snapshot':3,'object':7},'Incomplete main API inventory')
    require({r['name'] for r in parities['main']['checks'] if r['kind']=='snapshot'}=={'atlas','seasons','dashboard'},'Missing complete snapshots')
    require(parities['index']['mismatched_corpus_refused'] is True,'Mismatched index not refused')
    require(result['status']=='PASS_BROWSER_OBSERVATION_VISUAL_REVIEW_PENDING' and result['source_commit']==BROWSER_SOURCE and result['run_id']==str(BROWSER_RUN) and result['run_attempt']=='1','Wrong browser custody')
    require(result['saved_artifact']==ENGINE_ARTIFACT and result['logical_sha256']==LOGICAL and result['wasm_sha256']==BINARY and result['presentation_manifest_sha256']==FINAL_MANIFEST and result['native_or_wasm_rebuild'] is False,'Browser changed saved candidate')
    require(result['screenshots']==26 and result['browser_checks']==12 and result['installed'] is False,'Incomplete browser result')
    require(observed['status']=='PASS_BROWSER_OBSERVATION_VISUAL_REVIEW_PENDING' and not observed['page_errors'] and not observed['missing_assets'] and not observed['original_science_downloads'],'Browser errors or science download')
    require(len(observed['checks'])==12 and Counter(r['width'] for r in observed['checks'])=={1100:6,320:6},'Both complete viewport check groups required')
    screenshots=observed['screenshots'];require(len(screenshots)==len({r['path'] for r in screenshots})==26,'Exact 26 unique screenshots required')
    axes=[r for r in observed['legibility'] if r['kind']=='plot text'];require(len(axes)==6 and all(t['font_css_px']>=11 and t['inside'] is True for r in axes for t in r['metrics']),'Clipped or unreadable labels')
    tables=[r for r in observed['legibility'] if r['kind']=='table cells'];require(len(tables)==4 and all(r['minimum_cell_width']>=120 for r in tables if r['width']==320),'Unreadable narrow table cells')
    require(review['status']=='PASS_ALL_26_ACTUAL_IMAGES_INDIVIDUALLY_INSPECTED' and review['independent_visual_review_complete'] is True and review['actual_images_individually_inspected']==26,'Actual visual review required')
    require(review['source_commit']==BROWSER_SOURCE and review['run_id']==BROWSER_RUN and review['run_attempt']==1 and review['screenshots']==screenshots and review['blocking_issues']==[] and review['installed'] is False,'Visual review custody or blockers differ')
    require(presentation_manifest(original,scope,BROWSER_SOURCE)==final,'Presentation outside exact five-asset scope')
    files['almanac/query-engine.manifest.json']={'sha256':FINAL_MANIFEST,'bytes':final_manifest_bytes}
    return files
