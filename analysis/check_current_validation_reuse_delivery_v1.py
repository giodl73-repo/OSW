"""Reverify unchanged pending current data and a scoped-validation native/WASM engine."""
import os
from pathlib import Path
import check_atlantic_nsec_reference_delivery_v1 as delivery
import current_validation_reuse_engine_v1 as binding

ROOT=Path(__file__).resolve().parents[1]
REQUEST='research/current-validation-reuse-delivery-request-v1.json'
PREFLIGHT='research/current-validation-reuse-delivery-preflight-v1.json'
OUT=ROOT/'.pytest_cache/current-validation-reuse-delivery-v1'
WORK=ROOT/'.pytest_cache/current-validation-reuse-delivery-work-v1'

def run():
    if os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('OSW_CURRENT_VALIDATION_REUSE_DELIVERY_V1')!='1':raise ValueError('Scoped cloud validation-reuse delivery only')
    delivery.REQUEST=REQUEST;delivery.PREFLIGHT=PREFLIGHT;delivery.OUT=OUT;delivery.WORK=WORK
    delivery.run(engine_binding=binding.engine_manifest,expected_rust_tests=320)
    result=delivery.read(OUT/'result.json')
    if result['logical_sha256']!=binding.LOGICAL or result['logical_bytes']!=195361434 or result['rust_tests_passed']!=320:raise ValueError('Candidate data or test scope changed')
    for mode,count in [('main',392),('index',122)]:
        report=delivery.read(OUT/('compare-'+mode+'.json'))
        if report['status']!='PASS' or len(report['checks'])!=count:raise ValueError('Complete514 API inventory required')

if __name__=='__main__':
    try:run()
    except Exception as error:
        if os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true':
            OUT.mkdir(parents=True,exist_ok=True);delivery.write(OUT/'failure.json',delivery.failure_report(error,os.environ.get('GITHUB_SHA')))
        raise
