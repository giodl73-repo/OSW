"""Existing WSC comparison and proposed slope records never inherit aliases."""
import copy
import json
import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote
from playwright.sync_api import sync_playwright, expect
from test_rust_query_browser import ROOT, CLI, BASE, native, browser_query
from check_nordic_section_widths import NOR, WSC, SOURCES, records

def main():
    out=ROOT/'.pytest_cache/nordic-width-review';out.mkdir(parents=True,exist_ok=True)
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    assert len(bundle['collections']['widths'])==141
    assert len(bundle['collections']['proposed_widths'])==5
    for alias in ['norwegian','spitsbergen-atlantic']:
        assert native({'collection':'widths','filters':[{'field':'current_id','op':'eq','value':alias}]})['total']==0
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1280,'height':1000})
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        for owner,collection in [(WSC,'widths'),(NOR,'proposed_widths')]:
            query={'collection':collection,'filters':[{'field':'current_id' if owner==WSC else 'id','op':'eq','value':WSC if owner==WSC else records(NOR)[0]['id']}],'limit':20}
            page.goto(BASE+'?q='+quote(json.dumps(query)))
            page.wait_for_function('window.oswLastQueryResult || document.querySelector("#query-status").classList.contains("error")',timeout=90000)
            actual=page.evaluate('window.oswLastQueryResult')
            assert actual is not None,page.locator('#query-status').inner_text()
            assert actual==native(query)
            assert actual['map_scene'] is None
            assert actual['total']==(6 if owner==WSC else 1)
            expect(page.locator('.nordic-section-width svg')).to_be_visible()
            expect(page.locator('.nordic-section-width')).to_contain_text('Vertical support:')
            if owner==WSC:
                assert page.locator('.nordic-section-width svg circle').count()==3
                assert '21 km [11–24]' in page.locator('.nordic-section-width svg').text_content()
                query={'collection':'widths','filters':[{'field':'id','op':'eq','value':records(WSC)[2]['id']}],'limit':20}
                actual=browser_query(page,query)
                assert actual==native(query)
                assert len(actual['chart_scene']['panels'][0]['rows'])==6
                assert sum(r['matching'] for r in actual['chart_scene']['panels'][0]['rows'])==1
                page.locator('.nordic-section-width button').first.click()
                expect(page.locator('#query-detail h3')).to_have_text('West Spitsbergen Current')
                expect(page.locator('#query-detail')).to_contain_text(records(WSC)[0]['id'])
            else:
                assert actual['rows'][0]['width_range_km']==[25,30]
                assert 'current_id' not in actual['rows'][0]
                expect(page.locator('.nordic-section-width')).to_contain_text('Proposed identity only')
                page.locator('.nordic-section-width button').first.click()
                expect(page.locator('#query-detail h3')).to_have_text('Norwegian Atlantic Slope Current')
            page.set_viewport_size({'width':320,'height':900})
            assert page.locator('.nordic-section-width svg').bounding_box()['width']<=320
            page.locator('.nordic-section-width').screenshot(path=str(out/(owner+'-correct-owner-mobile.png')))
            page.set_viewport_size({'width':1280,'height':1000})
            page.locator('.nordic-section-width a').first.click()
            page.wait_for_function('window.oswSourceQueryResult',timeout=90000)
            assert page.evaluate('window.oswSourceQueryResult.document')==SOURCES[owner][0]
        page.goto(BASE+'?q='+quote(json.dumps({'collection':'proposed_widths','limit':20})))
        page.wait_for_function('window.oswLastQueryResult',timeout=90000)
        assert page.evaluate('window.oswLastQueryResult.total')==5
        assert 'undefined' not in page.locator('#query-rows').inner_text()
        page.locator('#query-rows tr button').first.click()
        expect(page.locator('#query-detail h3')).to_be_visible()
        page.get_by_role('link',name='Inspect exact source width record',exact=True).click()
        page.wait_for_function('window.oswSourceQueryResult',timeout=90000)
        assert page.evaluate('window.oswSourceQueryResult.document')=='research/norwegian-atlantic-branch-width-scope-audit.json'
        page.route('**/nordic-guard.html',lambda r:r.fulfill(body='<title>Proposed branch guard</title>',content_type='text/html'))
        page.goto('http://127.0.0.1:8788/nordic-guard.html')
        for mode in ['reassigned','midpoint','width_error','layer','annual','missing','canonical_transfer','forged_pin']:
            bad=copy.deepcopy(bundle)
            row=next(r for r in bad['collections']['proposed_widths'] if r['id']==records(NOR)[0]['id'])
            if mode=='reassigned':row['proposed_current_id']='norwegian'
            if mode=='midpoint':row['approximate_width_km']=27.5
            if mode=='width_error':row['uncertainty_km']=4
            if mode=='layer':row['fixed_layer_bounds_m']=[50,650]
            if mode=='annual':row['annual_width_range_km']=[25,30]
            if mode=='missing':bad['collections']['proposed_widths'].remove(row)
            if mode=='canonical_transfer':
                transferred=copy.deepcopy(row);transferred.pop('proposed_current_id');transferred.pop('original_regional_context');transferred['current_id']='norwegian'
                bad['collections']['widths'].append(transferred)
            if mode=='forged_pin':bad['manifest']['input_sha256'][SOURCES[NOR][0]]='0'*64
            with TemporaryDirectory(dir=out) as directory:
                path=Path(directory)/'bad.json';path.write_text(json.dumps(bad,ensure_ascii=False),encoding='utf8')
                run=subprocess.run([str(CLI),str(path),'-'],input='{}',capture_output=True,text=True,encoding='utf8')
                assert run.returncode==2 and not run.stdout,(mode,run.stderr)
                result=page.evaluate('''async path=>{
                  const {instance}=await WebAssembly.instantiate(await(await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports;
                  const b=new Uint8Array(await(await fetch(path)).arrayBuffer()),p=e.osw_alloc(b.length);
                  try{new Uint8Array(e.memory.buffer,p,b.length).set(b);e.osw_load(p,b.length);
                    return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));
                  }finally{e.osw_dealloc(p,b.length);}
                }''','/'+path.relative_to(ROOT).as_posix())
                assert result['ok'] is False,(mode,result)
        assert not errors,errors
        browser.close()
    print('PASS: existing WSC comparison, proposed-only Gimsøy records, real inspectors/source/mobile, eight native/WASM rejection cases and no alias transfer')

if __name__=='__main__':main()
