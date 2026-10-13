"""Separate accessible contour metrics across atlas, inspector and source queries."""
import gzip,json,os,subprocess,tempfile
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright
from test_rust_query_browser import ROOT,CLI,native
from test_acc_udintsev_breadths import records,check_native_guard

def main():
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as directory:
        directory=Path(directory);index=directory/'index.json'
        index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
            page=browser.new_page(viewport={'width':320,'height':800});errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Aacc#route-atlas')
            panels=page.locator('#route-atlas-preview .original-regional-width')
            panels.first.wait_for(state='visible',timeout=90000)
            assert panels.count()==2
            for i,row in enumerate(records()):
                panel=panels.nth(i);value=row['approximate_width_km']
                assert f'Approximately {value} km' in panel.inner_text()
                assert row['original_regional_context']['display_title'] in panel.inner_text()
                assert '1993–2012' in panel.inner_text()
                assert 'meridional MDT contour' in panel.locator('svg').get_attribute('aria-label')
                assert panel.locator('svg circle').count()==1
                assert panel.locator('svg text').evaluate_all('(es)=>es.every(e=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12)')
                panel.screenshot(path=str(ROOT/'.pytest_cache'/f'acc-{value}-breadth-mobile.png'))
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            for row in records():
                page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=acc&phase='+row['id'])
                page.wait_for_function('window.oswSeasonPlan?.current_id==="acc"',timeout=90000)
                assert page.locator('#season-title').inner_text()==row['original_regional_context']['display_title']
                assert f"approximately {row['approximate_width_km']} km" in page.locator('#season-value').inner_text()
                assert '\u00c2' not in page.locator('#season-value').inner_text()
                assert page.locator('#season-play').is_disabled() and page.evaluate('oswSeasonPlan.eligible_indices')==[]
                assert page.locator('#season-section-locator').is_hidden()
                panel=page.locator('#regional-width-range .original-regional-width')
                assert 'Numerical uncertainty unknown' in panel.inner_text()
                panel.locator('a').click();page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
                request={'document':row['original_regional_context']['audit_file'],'pointer':row['original_regional_context']['audit_pointer'],'limit':50}
                expected=json.loads(subprocess.check_output([str(CLI),'--index',str(index),'-'],input=json.dumps(request),encoding='utf8'))
                assert page.evaluate('oswSourceQueryResult')==expected
            query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'acc'}],'limit':100}
            page.goto('http://127.0.0.1:8788/almanac/query.html?q='+quote(json.dumps(query)))
            page.wait_for_function('window.oswLastQueryResult?.total===2',timeout=90000)
            assert page.evaluate('oswLastQueryResult')==native(query)
            assert not errors,errors
            targets=check_native_guard(directory)
            page.route('**/acc-guard.html',lambda r:r.fulfill(body='<!doctype html><title>ACC contour support</title>',content_type='text/html'))
            page.goto('http://127.0.0.1:8788/acc-guard.html')
            for target in targets:
                result=page.evaluate('''async path=>{
                  const {instance}=await WebAssembly.instantiate(await(await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports;
                  const data=new Uint8Array(await(await fetch(path)).arrayBuffer()),ptr=e.osw_alloc(data.length);
                  try{new Uint8Array(e.memory.buffer,ptr,data.length).set(data);e.osw_load(ptr,data.length);
                    return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));
                  }finally{e.osw_dealloc(ptr,data.length);}
                }''','/'+target.relative_to(ROOT).as_posix())
                assert result['ok'] is False and 'Original regional width' in result['error'],result
            browser.close()
    print('PASS: distinct ACC contour quantities, mobile, inspector/source/query parity and seven coherent native/WASM scope rejections')

if __name__=='__main__': main()
