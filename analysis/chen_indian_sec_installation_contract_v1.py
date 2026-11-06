"""Pure evidence gates for installing the exact reviewed Indian SEC artifacts."""
import copy
from collections import Counter
import chen_indian_sec_browser_contract_v2 as browser_contract

ENGINE_SOURCE=browser_contract.SOURCE
ENGINE_RUN=browser_contract.RUN
ENGINE_ARTIFACT=browser_contract.ARTIFACT
LOGICAL=browser_contract.LOGICAL
BINARY=browser_contract.BINARY
LOGICAL_BYTES=191109635
BROWSER_SOURCE='c0e6675c309e962f9ff471b496b15935570b0a20'
BROWSER_RUN=40879243518
BROWSER_ARTIFACT={'id':12899544869,'bytes':2093851,'sha256':'df533876b9598efcee8bc67a9968e8fcf9e31e5d6248267d9d578b0efcddd3e4'}
FINAL_MANIFEST='157ae1b610588ac1e8c58dba524cc4e6a60361be05bba8c1b68ca767fe6366ac'
MAIN='19148702de6433253dbf412a0a28c0cb4f8e409e'


def require(condition,message):
    if not condition:raise ValueError(message)


def verify_evidence(engine,parities,result,observed,review,original,final,scope,final_manifest_bytes):
    files=copy.deepcopy(browser_contract.verify_saved_result(engine))
    for mode,count in [('main',234),('index',86)]:
        report=parities[mode]
        require(report['status']=='PASS' and len(report['checks'])==count,'Incomplete native/WASM parity')
        require(report['wasm_sha256']==BINARY and report['complete_initialization_equal'] is True,'Wrong parity engine or metadata')
        require(all(c['entire_response_equal'] is True for c in report['checks']),'Partial response comparison')
    require(parities['main']['payload_sha256']==LOGICAL,'Wrong logical bundle')
    require(parities['index']['mismatched_corpus_refused'] is True,'Mismatched source corpus not refused')
    require(Counter(c['kind'] for c in parities['main']['checks'])=={'query':224,'snapshot':3,'object':7},'Missing complete API cases')
    require({c['name'] for c in parities['main']['checks'] if c['kind']=='snapshot'}=={'atlas','seasons','dashboard'},'Missing snapshots')
    require(result['status']=='PASS_BROWSER_OBSERVATION_VISUAL_REVIEW_PENDING' and result['source_commit']==BROWSER_SOURCE,'Wrong saved browser result')
    require(str(result['run_id'])==str(BROWSER_RUN) and str(result['run_attempt'])=='2','Wrong browser run')
    require(result['saved_artifact']==ENGINE_ARTIFACT and result['logical_sha256']==LOGICAL and result['wasm_sha256']==BINARY,'Browser used another engine')
    require(result['presentation_manifest_sha256']==FINAL_MANIFEST and result['native_or_wasm_rebuild'] is False,'Wrong browser presentation manifest')
    require(result['screenshots']==32 and result['browser_checks']==12 and result['installed'] is False,'Incomplete browser delivery')
    require(observed['status']=='PASS_BROWSER_OBSERVATION_VISUAL_REVIEW_PENDING','Browser observation failed')
    require(not observed['page_errors'] and not observed['missing_assets'] and not observed['original_science_downloads'],'Browser errors or source downloads')
    require(len(observed['checks'])==12 and {c['width'] for c in observed['checks']}=={1100,320},'Both viewports required')
    require(observed['resize_reflow_verified'] is True,'Responsive reflow not checked')
    screenshots=observed['screenshots']
    require(len(screenshots)==len({r['path'] for r in screenshots})==32,'Exact32 unique captures required')
    require(all(r['geometry']['width']>0 and r['geometry']['height']>0 and not r['geometry']['clipped_axes'] for r in screenshots),'Clipped or empty images')
    metrics=observed['legibility'];axes=[m for m in metrics if 'minimum_font_css_px' in m]
    require(len(axes)==10 and all(m['minimum_font_css_px']>=11 and m['visible_labels']>=7 for m in axes),'Unreadable plot axes')
    tables={(m['width'],m['kind']):m for m in metrics if 'cells' in m}
    require(len(tables)==6,'Missing table layouts or widths')
    for width in (1100,320):
        for kind,rows,cells in [('reading cells',75,300),('sensitivity cells',120,600),('coverage cells',25,75)]:
            m=tables[(width,kind)]
            require(m['rows']==rows and m['cells']==cells and m['invalid_cells']==0 and m['undersized_grid_cells']==0 and m['table_overflow'] is False,'Hidden or squeezed table values')
            require(m['grid_rows']==(rows if width==320 else 0),'Wrong responsive table structure')
            if width==320:require(m['minimum_grid_cell_ratio']>=.4,'Narrow cells remain squeezed')
    require(review['status']=='PASS_ALL_32_ACTUAL_IMAGES_INDIVIDUALLY_INSPECTED' and review['independent_visual_review_complete'] is True,'Actual visual review incomplete')
    require(review['source_commit']==BROWSER_SOURCE and review['run_id']==BROWSER_RUN and review['run_attempt']==2,'Visual review custody differs')
    require(review['blocking_issues']==[] and review['screenshots']==screenshots and review['installed'] is False,'Visual blockers remain')
    require(review['actual_images_individually_inspected']==32 and review['new_images_individually_viewed']==4 and review['previously_inspected_byte_identical_images']==28,'Image review incomplete')
    require(browser_contract.presentation_manifest(original,scope,BROWSER_SOURCE)==final,'Presentation changed outside exact five-source/one-style overlay')
    files['almanac/query-engine.manifest.json']={'sha256':FINAL_MANIFEST,'bytes':final_manifest_bytes}
    return files
