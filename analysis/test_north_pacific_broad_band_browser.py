"""Textbook broad-band card, unknown dimensions and shipped source bindings."""
import gzip,json,os,subprocess,tempfile
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright
from test_rust_query_browser import ROOT,CLI,native
from test_north_pacific_broad_band import records,check_native_guard
def main():
    row=records()[0]
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as directory:
        directory=Path(directory);index=directory/'index.json';index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'));page=browser.new_page(viewport={'width':320,'height':800});errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Anorth-pacific#route-atlas')
            panel=page.locator('#route-atlas-preview .reported-width-constraint');panel.wait_for(state='visible',timeout=90000)
            assert panel.count()==1 and 'more than 2000 km' in panel.inner_text()
            assert 'combined' in panel.inner_text() and 'March 2005' in panel.inner_text()
            assert panel.locator('svg circle,svg line,svg path').count()==0
            assert 'representative width' in panel.locator('svg').get_attribute('aria-label')
            assert 'measured 20 km' not in panel.locator('svg').get_attribute('aria-label')
            assert panel.locator('svg text').evaluate_all('(es)=>es.every(e=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12)')
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            panel.screenshot(path=str(ROOT/'.pytest_cache/north-pacific-band-mobile.png'))
            page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=north-pacific&phase='+row['id'])
            page.wait_for_function('window.oswSeasonPlan?.current_id==="north-pacific"',timeout=90000)
            assert page.locator('#season-title').inner_text()=='Reported broad flow band'
            assert 'more than 2000 km' in page.locator('#season-value').inner_text()
            assert 'representative width unknown' in page.locator('#season-value').inner_text()
            assert page.locator('#season-play').is_disabled() and page.evaluate('oswSeasonPlan.eligible_indices')==[]
            assert page.locator('#season-section-locator').is_hidden() and page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
            page.locator('#regional-width-range .reported-width-constraint a').click();page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
            request={'document':row['original_regional_context']['audit_file'],'pointer':'/measurement','limit':50}
            expected=json.loads(subprocess.check_output([str(CLI),'--index',str(index),'-'],input=json.dumps(request),encoding='utf8'))
            assert page.evaluate('oswSourceQueryResult')==expected
            query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'north-pacific'}],'limit':100}
            page.goto('http://127.0.0.1:8788/almanac/query.html?q='+quote(json.dumps(query)));page.wait_for_function('window.oswLastQueryResult?.total===1',timeout=90000)
            assert page.evaluate('oswLastQueryResult')==native(query)
            assert not errors,errors;browser.close()
        target=check_native_guard(directory)
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'));page=browser.new_page()
            page.route('**/north-pacific-guard.html',lambda r:r.fulfill(body='<!doctype html><title>Broad-band guard</title>',content_type='text/html'))
            page.goto('http://127.0.0.1:8788/north-pacific-guard.html')
            result=page.evaluate('''async path=>{
              const {instance}=await WebAssembly.instantiate(await(await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports;
              const data=new Uint8Array(await(await fetch(path)).arrayBuffer()),ptr=e.osw_alloc(data.length);
              try{new Uint8Array(e.memory.buffer,ptr,data.length).set(data);e.osw_load(ptr,data.length);
                return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));
              }finally{e.osw_dealloc(ptr,data.length);}
            }''','/'+target.relative_to(ROOT).as_posix())
            assert result['ok'] is False and 'Original regional width' in result['error'],result;browser.close()
    print('PASS: North Pacific broad-band qualifier/definition, mobile, inspector/source/query parity and coherent native/WASM rejection')
if __name__=='__main__':main()
