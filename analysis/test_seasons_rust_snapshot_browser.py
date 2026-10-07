"""Checked seasonal source parity, projection rejection and worker-only loading."""
import copy,hashlib,json,os,subprocess,tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from test_rust_query_browser import CLI,ROOT


def route_bundle(page,bundle):
    raw=json.dumps(bundle,ensure_ascii=False).encode()
    manifest=json.loads((ROOT/'almanac/query-engine.manifest.json').read_bytes())
    manifest['sha256']['almanac/query-data.json']=hashlib.sha256(raw).hexdigest()
    page.route('**/query-data.json',lambda r:r.fulfill(body=raw,content_type='application/json'))
    page.route('**/query-engine.manifest.json',lambda r:r.fulfill(json=manifest))


def replace_source(bundle,key,doc):
    receipt=bundle['manifest']['seasons_receipts'][key]
    receipt['source_json']=json.dumps(doc,ensure_ascii=False)
    receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest()
    bundle['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
    # Keep dependent planning receipts aligned before testing direction semantics.
    for record in bundle['collections']['route_decisions']:
        for review in record['scope_reviews']:
            if review['note']['audit_file']==receipt['source_file']:
                review['source_sha256']=receipt['source_sha256']
                review['document']=copy.deepcopy(doc)


def main():
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    native=json.loads(subprocess.check_output([str(CLI),str(ROOT/'almanac/query-data.json'),'--seasons'],encoding='utf-8'))
    assert native['ok']
    for key,receipt in bundle['manifest']['seasons_receipts'].items():
        assert native['sources_json'][key]==(ROOT/receipt['source_file']).read_bytes().decode()
    cases=[]
    bad=copy.deepcopy(bundle);bad['manifest']['seasons_receipts']['widths']['source_sha256']='0'*64;cases.append(bad)
    for key,field in [('widths','measurements'),('routes','candidates'),('frames','frames')]:
        bad=copy.deepcopy(bundle);doc=json.loads(bad['manifest']['seasons_receipts'][key]['source_json']);doc[field][0]['id']='missing';replace_source(bad,key,doc);cases.append(bad)
    for mode in ['duplicate','incomplete','direction','missing_exclusion']:
        bad=copy.deepcopy(bundle);key='widths' if mode in ['duplicate','incomplete'] else 'directions';doc=json.loads(bad['manifest']['seasons_receipts'][key]['source_json'])
        if mode=='duplicate':doc['current_decisions'][0]=doc['current_decisions'][1]
        if mode=='incomplete':doc['current_decisions'].pop()
        if mode=='direction':doc['phases'][2]['playback_eligible']=True
        if mode=='missing_exclusion':del doc['phases'][0]['annual_width_range_km']
        replace_source(bad,key,doc);cases.append(bad)
    with tempfile.TemporaryDirectory() as directory:
        for i,bad in enumerate(cases):
            path=Path(directory)/'bad.json';path.write_text(json.dumps(bad),encoding='utf-8')
            result=subprocess.run([str(CLI),str(path),'--seasons'],capture_output=True,text=True)
            assert result.returncode==2 and not result.stdout and result.stderr,i
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page();errors=[];raw_requests=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('request',lambda r:raw_requests.append(r.url) if '/research/' in r.url and r.url.endswith('.json') else None)
        page.route('**/research/*.json',lambda r:r.fulfill(status=503,body='Direct JSON disabled'))
        url='http://127.0.0.1:8788/almanac/seasons.html?current=florida'
        page.goto(url)
        page.wait_for_function('window.oswSeasonSnapshot',timeout=90000)
        expect(page.locator('#season-current option')).to_have_count(100,timeout=90000)
        assert page.evaluate('window.oswSeasonSnapshot')==native
        assert page.locator('#season-loading').get_attribute('data-engine')=='rust-osw-query-v1'
        assert not raw_requests,raw_requests
        assert not errors,errors
        failed=browser.new_page();failed.route('**/query-data.json',lambda r:r.fulfill(status=503,body='Unavailable'))
        failed.goto(url);expect(failed.locator('#season-loading')).to_contain_text('HTTP 503',timeout=90000)
        assert failed.locator('#season-current option').count()==0
        assert failed.evaluate('window.oswSeasonSnapshot===undefined')
        rejected=browser.new_page();route_bundle(rejected,cases[-2]);rejected.goto(url)
        expect(rejected.locator('#season-loading')).to_contain_text('Invalid local direction scope',timeout=90000)
        assert rejected.locator('#season-current option').count()==0
        browser.close()
    print('PASS: four exact source documents, eight loader rejections, native/WASM parity, 100 current phase plans/controls, no direct JSON reads, unavailable and invalid first loads')


if __name__=='__main__':main()
