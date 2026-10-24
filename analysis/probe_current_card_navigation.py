"""Cloud-only UI diagnostic using saved candidate data before a fresh build.

This probe cannot establish native/source parity or authorize publication.
The complete candidate build and all original gates still run after it passes.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from query_packet import descriptors

ROOT=Path(__file__).resolve().parents[1]


def digest(path):
    result=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):result.update(block)
    return result.hexdigest()


def checked_site(path):
    site=Path(path).resolve()
    cache=(ROOT/'.pytest_cache').resolve()
    if site==cache or not site.is_relative_to(cache) or (site/'almanac').resolve()==(ROOT/'almanac').resolve():
        raise ValueError('Navigation probe must use its own ignored workspace')
    return site


def verify_artifacts(site, source):
    if source.get('schema')!='osw.davidson-width-candidate.v1' or source.get('status')!='PASS' or source.get('published') is not False:
        raise ValueError('Saved candidate source audit must pass')
    engine=json.loads((site/'almanac/query-engine.manifest.json').read_bytes())
    if engine.get('engine')!='rust-osw-query-v1' or engine.get('abi_version')!=1:
        raise ValueError('Unexpected saved engine')
    packet=json.loads((site/'almanac/query-data.json').read_bytes())
    pins=engine['sha256']
    for relative in ['almanac/query-data.json','almanac/query-engine.wasm','almanac/index-catalog.json',
                     'almanac/index-sources.json','almanac/index-data.json.gz','research/ocean-motion-dashboard.json']:
        if digest(site/relative)!=pins.get(relative):raise ValueError('Saved artifact mismatch: '+relative)
    logical,size=hashlib.sha256(),0
    folder=(site/'almanac').resolve()
    for part in descriptors(packet):
        path=(folder/part['path']).resolve()
        if not path.is_relative_to(folder) or path.stat().st_size!=part['byte_length'] or digest(path)!=part['sha256']:
            raise ValueError('Saved packet part changed')
        if pins.get('almanac/'+part['path'])!=part['sha256']:raise ValueError('Saved engine omitted data part')
        with path.open('rb') as stream:
            for block in iter(lambda:stream.read(1024*1024),b''):logical.update(block);size+=len(block)
    if (logical.hexdigest()!=packet['logical_sha256'] or size!=packet['logical_byte_length']
            or source['candidate']['logical_sha256']!=packet['logical_sha256']
            or source['candidate']['logical_bytes']!=size):
        raise ValueError('Saved candidate data/engine/source cohorts disagree')
    return packet['logical_sha256']


def prepare_site(site):
    """Copy only current UI code; keep saved generated data isolated."""
    for source in (ROOT/'almanac').rglob('*'):
        if source.is_file() and source.suffix in {'.html','.js','.css','.svg'}:
            target=site/'almanac'/source.relative_to(ROOT/'almanac')
            if not target.resolve().is_relative_to(site):raise ValueError('Probe UI path leaves sandbox')
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    figures=site/'figures'
    if figures.exists() or figures.is_symlink():raise ValueError('Probe figure link already exists')
    figures.symlink_to(ROOT/'figures',target_is_directory=True)


def main():
    if os.environ.get('GITHUB_ACTIONS')!='true':
        raise RuntimeError('Navigation probe is cloud-only; local browsers/data loads are held')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site',required=True,type=Path)
    parser.add_argument('--source-audit',required=True,type=Path)
    parser.add_argument('--source-run',required=True,type=int)
    args=parser.parse_args()
    if hasattr(os,'sched_getaffinity'):
        os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});os.nice(5)
    site=checked_site(args.site)
    output=ROOT/'.pytest_cache/navigation-probe';output.mkdir(parents=True,exist_ok=True)
    receipt={'status':'RUNNING','upstream_run_id':args.source_run,
             'control_source_commit':os.environ.get('GITHUB_SHA'),
             'native_compilation_performed':False,'fresh_cohort_validation':False,'publication_authorized':False}
    server=None
    try:
        receipt['tested_bundle_sha256']=verify_artifacts(site,json.loads(args.source_audit.read_bytes()))
        prepare_site(site)
        from run_rust_query_browser_checks import check_port_available,wait_for_checkout
        check_port_available()
        server=subprocess.Popen([sys.executable,'-m','http.server','8788','--bind','127.0.0.1','--directory',str(site)],
                                stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        wait_for_checkout(server)
        environment=os.environ.copy();environment['OSW_RESEARCH_EVIDENCE_BASE']='http://127.0.0.1:8788'
        if not environment.get('OSW_TEST_BROWSER'):
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:environment['OSW_TEST_BROWSER']=p.chromium.executable_path
        subprocess.run([sys.executable,str(ROOT/'analysis/test_nwasc_working_admission_browser.py'),'--navigation-only'],
                       cwd=ROOT,env=environment,check=True,timeout=600)
        receipt.update(status='PASS_NAVIGATION_DIAGNOSTIC_ONLY',
                       tested_ui_source_sha256={name:digest(ROOT/name) for name in
                           ['almanac/reference-routes.js','almanac/reference-routes.html','analysis/test_nwasc_working_admission_browser.py']})
    except Exception as error:
        receipt.update(status='FAIL',error=type(error).__name__+': '+str(error))
        raise
    finally:
        if server is not None:
            server.terminate();server.wait(timeout=5)
        (output/'result.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    print(json.dumps(receipt))


if __name__=='__main__':main()
