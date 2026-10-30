"""Browser verification of the exact rebuilt engine; no rebuild or installation."""
import os
from pathlib import Path
import check_atlantic_nsec_reference_browser_v1 as browser

ROOT=Path(__file__).resolve().parents[1]
REQUEST='research/current-utf8-validation-browser-request-v1.json'
PREFLIGHT='research/current-utf8-validation-browser-preflight-v1.json'
SAVED='research/current-utf8-validation-delivery-run-v1/'
OUT=ROOT/'.pytest_cache/current-utf8-validation-browser-v1'
WORK=ROOT/'.pytest_cache/current-utf8-validation-browser-work-v1'
SOURCE='fcca8e283ef9d0e868ada629b772aad93980a5c6'
RUN=41114274466
ARTIFACT={'id': 13006867096, 'bytes': 99217055, 'sha256': '7ca167a241b1ae2185372c700174708f1a349fd97269092e5d7a9d785941875d'}
BINARY='8b2f63c2c643b5c15b51865678b1a0f496a169a9c95c1b770990f47d9d760edc'
MANIFEST='75047c79e372694c63a69cf99fb57db8a89bfba7f5dd4c4d475f33d7c73f5722'
LOGICAL='09b882c97c922a0643880885a6165388bf41b19903e72a6d9ca44437da1ed41e'

def validate_candidate(result):
    expected={'status':'PASS_COMPLETE_NATIVE_WASM_CANDIDATE_BROWSER_PENDING','source_commit':SOURCE,
        'run_id':str(RUN),'run_attempt':'1','logical_sha256':LOGICAL,'logical_bytes':195361434,
        'wasm_sha256':BINARY,'rust_tests_passed':322,'historical_main_api_cases':372,'historical_source_api_cases':115,
        'new_main_api_cases':20,'new_source_api_cases':7,'ordinary_cli_equivalence_checks':2}
    for key,value in expected.items():
        if type(result.get(key)) is not type(value) or result[key]!=value:raise ValueError('Rebuilt candidate custody differs: '+key)
    files=result['generated_files']
    if len(files)!=18 or files['almanac/query-engine.manifest.json']['sha256']!=MANIFEST or files['almanac/query-engine.wasm']['sha256']!=BINARY:raise ValueError('Exact18 rebuilt engine files required')
    return files

def run():
    if os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('OSW_CURRENT_UTF8_VALIDATION_BROWSER_V1')!='1':raise ValueError('Scoped cloud strict-UTF8 browser only')
    validate_candidate(browser.read(SAVED+'result.json'))
    for name in ['REQUEST','PREFLIGHT','SAVED','OUT','WORK','SOURCE','RUN','ARTIFACT','BINARY','MANIFEST','LOGICAL']:
        setattr(browser,name,globals()[name])
    browser.main(apply_client_transport_binding=False)

if __name__=='__main__':
    try:run()
    except Exception as error:
        if os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true':
            OUT.mkdir(parents=True,exist_ok=True);browser.write(OUT/'failure.json',{'status':'FAIL','error':str(error)[:4000],'installed':False,'main_updated':False})
        raise
