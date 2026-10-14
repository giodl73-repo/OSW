"""Local descriptors stay distinct and static in atlas, inspector and WASM."""
import gzip
import json
import os
import subprocess
import tempfile
from urllib.parse import quote

from playwright.sync_api import sync_playwright, expect
from test_rust_query_browser import ROOT, CLI
from test_hiri_east_adriatic_local_widths import records, coherent_packet

def main():
    rows=records(); errors=[]
    (ROOT/'.pytest_cache/local-widths-review').mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1200,'height':900})
        page.on('pageerror',lambda error:errors.append(str(error)))
        for owner,number,words in [('hiri-current',2,['50 km','75 km','decay scale','different years']),
                                   ('east-adriatic',1,['10 km','coastal','C1','pycnocline'])]:
            page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature='+quote('current:'+owner)+'#route-atlas',wait_until='networkidle')
            charts=page.locator('#route-atlas-preview .original-regional-width')
            expect(charts).to_have_count(number,timeout=90000)
            text=' '.join(charts.all_inner_texts())
            for word in words:
                assert word in text,(word,text)
            assert charts.locator('svg circle').count()==number
            page.set_viewport_size({'width':320,'height':850})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.locator('#route-atlas-preview').screenshot(path=str(ROOT/'.pytest_cache/local-widths-review'/f'{owner}-mobile.png'))
            page.set_viewport_size({'width':1200,'height':900})
        for row in rows:
            page.goto('http://127.0.0.1:8788/almanac/seasons.html?current='+row['current_id']+'&phase='+row['id'],wait_until='networkidle')
            expect(page.locator('#season-title')).to_have_text(row['phase_label'],timeout=90000)
            assert row['width_metric_label'] in page.locator('#season-value').inner_text()
            assert page.locator('#season-play').is_disabled()
            assert page.evaluate('oswSeasonPlan.eligible_indices')==[]
            assert page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
        for owner in ['hiri-current','east-adriatic']:
            row=next(r for r in rows if r['current_id']==owner)
            request={'document':row['original_regional_context']['audit_file'],'pointer':'/measurements','limit':10}
            page.goto('http://127.0.0.1:8788/almanac/query.html?source-q='+quote(json.dumps(request)),wait_until='networkidle')
            page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
            with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as folder:
                index=ROOT/folder/'index.json';index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
                native=json.loads(subprocess.check_output([str(CLI),'--index',str(index),'-'],input=json.dumps(request),encoding='utf8'))
                assert page.evaluate('oswSourceQueryResult')==native
        packet=json.loads((ROOT/'almanac/query-data.json').read_bytes())
        page.route('**/local-width-guard.html',lambda route:route.fulfill(body='<title>Local descriptors</title>',content_type='text/html'))
        page.goto('http://127.0.0.1:8788/local-width-guard.html')
        for row in rows:
            key,value=('approximate_width_km',row['approximate_width_km']*2) if row['current_id']=='hiri-current' else ('fixed_layer_bounds_m',[10,70])
            with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as folder:
                file=ROOT/folder/'bad.json';file.write_text(json.dumps(coherent_packet(packet,row['id'],key,value)),encoding='utf8')
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
    print('PASS: two Hiri scales, local EAC extent, static inspectors, source/native parity, mobile and three WASM scope rejections')

if __name__=='__main__':
    main()
