"""Humboldt descriptions on atlas/inspector, source queries and WASM guard."""
import gzip,json,os,subprocess,tempfile
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright
from test_rust_query_browser import ROOT,CLI,native
from test_humboldt_width_descriptions import records,check_native_guard

def main():
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as directory:
        directory=Path(directory);index=directory/'index.json';index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
            page=browser.new_page(viewport={'width':320,'height':800});errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Aperu-humboldt#route-atlas')
            diagrams=page.locator('#route-atlas-preview .original-regional-width');diagrams.first.wait_for(state='visible',timeout=90000)
            assert diagrams.count()==3
            assert page.locator('#route-atlas-preview .atlas-width-record').count()==3
            for i,row in enumerate(records()):
                assert str(row['approximate_width_km']) in diagrams.nth(i).inner_text()
                assert 'unresolved' in diagrams.nth(i).inner_text()
                assert diagrams.nth(i).locator('svg text').evaluate_all('(es)=>es.every(e=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12)')
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.locator('#route-atlas-preview .atlas-width-evidence').screenshot(path=str(ROOT/'.pytest_cache/humboldt-descriptions-mobile.png'))
            for row in records():
                page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=peru-humboldt&phase='+row['id'])
                page.wait_for_function('window.oswSeasonPlan?.current_id==="peru-humboldt"',timeout=90000)
                assert str(row['approximate_width_km']) in page.locator('#season-value').inner_text()
                assert page.locator('#season-play').is_disabled() and page.evaluate('oswSeasonPlan.eligible_indices')==[]
                assert page.locator('#season-section-locator').is_hidden() and page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
                panel=page.locator('#regional-width-range .original-regional-width')
                assert 'Primary publisher HTML' in panel.inner_text() and 'unresolved' in panel.inner_text()
                panel.locator('a').click();page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
                request={'document':row['original_regional_context']['audit_file'],'pointer':row['original_regional_context']['audit_pointer'],'limit':50}
                expected=json.loads(subprocess.check_output([str(CLI),'--index',str(index),'-'],input=json.dumps(request),encoding='utf8'))
                assert page.evaluate('oswSourceQueryResult')==expected
            query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'peru-humboldt'}],'limit':100}
            page.goto('http://127.0.0.1:8788/almanac/query.html?q='+quote(json.dumps(query)))
            page.wait_for_function('window.oswLastQueryResult?.total===3',timeout=90000)
            assert page.evaluate('oswLastQueryResult')==native(query)
            assert not errors,errors
            browser.close()
        target=check_native_guard(directory)
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'));page=browser.new_page()
            page.route('**/humboldt-guard.html',lambda r:r.fulfill(body='<!doctype html><title>Regional description guard</title>',content_type='text/html'))
            page.goto('http://127.0.0.1:8788/humboldt-guard.html')
            result=page.evaluate('''async path=>{
              const {instance}=await WebAssembly.instantiate(await(await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports;
              const data=new Uint8Array(await(await fetch(path)).arrayBuffer()),ptr=e.osw_alloc(data.length);
              try{new Uint8Array(e.memory.buffer,ptr,data.length).set(data);e.osw_load(ptr,data.length);
                return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));
              }finally{e.osw_dealloc(ptr,data.length);}
            }''','/'+target.relative_to(ROOT).as_posix())
            assert result['ok'] is False and 'Original regional width' in result['error'],result
            browser.close()
    print('PASS: three scoped Humboldt diagrams, mobile, inspector/source/query parity and coherent native/WASM rejection')

if __name__=='__main__':main()
