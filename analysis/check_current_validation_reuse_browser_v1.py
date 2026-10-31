"""Browser verification of the exact rebuilt engine; no rebuild or installation."""
import os
from pathlib import Path
import check_atlantic_nsec_reference_browser_v1 as browser

ROOT=Path(__file__).resolve().parents[1]
REQUEST='research/current-validation-reuse-browser-request-v1.json'
PREFLIGHT='research/current-validation-reuse-browser-preflight-v1.json'
SAVED='research/current-validation-reuse-delivery-run-v1/'
OUT=ROOT/'.pytest_cache/current-validation-reuse-browser-v1'
WORK=ROOT/'.pytest_cache/current-validation-reuse-browser-work-v1'
SOURCE='fedddc973984d776e9eef718fca306f013357199'
RUN=41097066749
ARTIFACT={'id':12999381109,'bytes':99224643,'sha256':'1533bd5a8cf995193bc1c0056cd5849431cbd418826457a4fb6d50be4d1369ee'}
BINARY='fd2288b082a81574d620b048a5c36baa63ebdee4fd9a0a9306ef162e357ab0c3'
MANIFEST='e0e71b8afeae6e5a3fbc407714eb5ccf931099136eeb7d3480f5fa47c577de0b'
LOGICAL='09b882c97c922a0643880885a6165388bf41b19903e72a6d9ca44437da1ed41e'

def validate_candidate(result):
    expected={'status':'PASS_COMPLETE_NATIVE_WASM_CANDIDATE_BROWSER_PENDING','source_commit':SOURCE,
        'run_id':str(RUN),'run_attempt':'1','logical_sha256':LOGICAL,'logical_bytes':195361434,
        'wasm_sha256':BINARY,'rust_tests_passed':320,'historical_main_api_cases':372,'historical_source_api_cases':115,
        'new_main_api_cases':20,'new_source_api_cases':7,'ordinary_cli_equivalence_checks':2}
    for key,value in expected.items():
        if type(result.get(key)) is not type(value) or result[key]!=value:raise ValueError('Rebuilt candidate custody differs: '+key)
    files=result['generated_files']
    if len(files)!=18 or files['almanac/query-engine.manifest.json']['sha256']!=MANIFEST or files['almanac/query-engine.wasm']['sha256']!=BINARY:raise ValueError('Exact18 rebuilt engine files required')
    return files

def run():
    if os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('OSW_CURRENT_VALIDATION_REUSE_BROWSER_V1')!='1':raise ValueError('Scoped cloud rebuilt-engine browser only')
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
