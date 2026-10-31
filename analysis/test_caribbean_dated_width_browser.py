"""Dated width, source limitations and compiled admission remain visible."""
from query_packet import read_bundle_bytes
import gzip,json,os,subprocess,tempfile
from urllib.parse import quote
from playwright.sync_api import sync_playwright,expect
from test_rust_query_browser import ROOT,CLI
from test_caribbean_dated_width import record,coherent_packet

def main():
    row=record();errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1200,'height':900});page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Acaribbean#route-atlas',wait_until='networkidle')
        card=page.locator('#route-atlas-preview .original-regional-width')
        expect(card).to_contain_text('410 km',timeout=90000)
        assert 'October 1974' in card.inner_text() and '0.66 m/s' in card.inner_text()
        assert 'unresolved upper unit' in card.inner_text()
        assert card.locator('svg circle').count()==1 and card.locator('svg line').count()==1
        page.set_viewport_size({'width':320,'height':850})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        card.screenshot(path=str(ROOT/'.pytest_cache/caribbean-width-mobile.png'))
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=caribbean&phase='+row['id'],wait_until='networkidle')
        expect(page.locator('#regional-width-range')).to_contain_text('October 1974',timeout=90000)
        assert page.locator('#season-play').is_disabled()
        assert page.evaluate('oswSeasonPlan.eligible_indices')==[]
        assert page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        request={'document':row['original_regional_context']['audit_file'],'pointer':'/measurement/original_regional_context/range_context','limit':50}
        page.goto('http://127.0.0.1:8788/almanac/query.html?source-q='+quote(json.dumps(request)),wait_until='networkidle')
        page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
        with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as folder:
            index=ROOT/folder/'index.json';index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
            expected=json.loads(subprocess.check_output([str(CLI),'--index',str(index),'-'],input=json.dumps(request),encoding='utf8'))
            assert page.evaluate('oswSourceQueryResult')==expected
        # Load a coherently rewritten receipt directly into the shipped WASM.
        packet=json.loads(read_bundle_bytes(ROOT/'almanac/query-data.json'))
        page.route('**/caribbean-guard.html',lambda route:route.fulfill(body='<title>Width admission</title>',content_type='text/html'))
        page.goto('http://127.0.0.1:8788/caribbean-guard.html')
        for key,value in [('width_range_km',[200,410]),('fixed_layer_bounds_m',[0,1600])]:
            bad=coherent_packet(packet,key,value)
            with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as folder:
                file=ROOT/folder/'bad.json';file.write_text(json.dumps(bad),encoding='utf8')
                result=page.evaluate('''async path=>{
                  const {instance}=await WebAssembly.instantiate(await (await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports;
                  const b=new Uint8Array(await (await fetch(path)).arrayBuffer()),p=e.osw_alloc(b.length);
                  try{new Uint8Array(e.memory.buffer,p,b.length).set(b);e.osw_load(p,b.length);
                    return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));
                  }finally{e.osw_dealloc(p,b.length);}
                }''','/'+file.relative_to(ROOT).as_posix())
                assert result['ok'] is False and 'Original regional width' in result['error'],result
        assert not errors,errors
        browser.close()
    print('PASS: Caribbean dated point/speed, unresolved range units, static phase, source/native parity, mobile and two WASM scope rejections')

if __name__=='__main__':main()
