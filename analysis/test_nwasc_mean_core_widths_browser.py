"""Actual native/WASM rows, section card, source links and phone layout."""
import copy,hashlib,json,os,subprocess
from tempfile import TemporaryDirectory
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright,expect
from test_current_research_evidence_browser import ROOT,BASE,CLI,native
from query_packet import load_bundle
import nwasc_mean_core_widths as n

def main():
    doc,_=n.verify_inputs();out=ROOT/'.pytest_cache/nwasc-mean-core-browser';out.mkdir(exist_ok=True)
    q={'collection':'proposed_widths','filters':[{'field':'measurement_type','op':'eq','value':'published_mean_field_transport_core_extent'}],'limit':10}
    expected=native(q);wanted={r['id']:r for r in n.records()}
    assert expected['total']==2 and {r['id']:r for r in expected['rows']}==wanted
    assert expected['map_scene'] is None
    errors=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1360,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(BASE+'/almanac/query.html?q='+quote(json.dumps(q)))
        page.wait_for_function('window.oswLastQueryResult',timeout=120000)
        assert page.evaluate('window.oswLastQueryResult')==expected
        panel=page.locator('.nordic-section-width');expect(panel).to_contain_text('Gimsøy horizontal projection')
        expect(panel).to_contain_text('not mean widths')
        expect(panel.get_by_role('link',name='Retained original PDF · CC BY 4.0')).to_have_attribute('href','../'+n.DIRECTORY+'article.pdf')
        panel.screenshot(path=str(out/'query-desktop.png'))
        panel.get_by_role('link',name='Source record').first.focus();page.keyboard.press('Enter')
        page.wait_for_function('window.oswSourceQueryResult',timeout=120000)
        assert page.evaluate('window.oswSourceQueryResult.document')==n.FILE
        page.goto(BASE+'/almanac/reference-routes.html#inventory-addition-norwegian-atlantic-slope')
        card=page.locator('#inventory-addition-norwegian-atlantic-slope .nwasc-mean-core')
        expect(card.get_by_role('link',name='Query both static mean-core spans')).to_be_visible(timeout=120000)
        assert json.loads(page.evaluate('(p)=>window.oswAtlasSnapshot.sources_json[p]',n.FILE))==doc
        page.wait_for_function('document.querySelector(".nwasc-mean-core img")?.naturalWidth>0')
        details=card.locator('details');assert details.count()==2
        details.first.locator('summary').focus();page.keyboard.press('Enter')
        assert details.first.get_attribute('open') is not None
        expect(details.first).to_contain_text('Svinøy paragraph')
        page.set_viewport_size({'width':320,'height':1000});card.screenshot(path=str(out/'card-mobile.png'))
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        card.get_by_role('link',name='Query both static mean-core spans').focus();page.keyboard.press('Enter')
        page.wait_for_function('window.oswLastQueryResult',timeout=120000)
        actual=page.evaluate('window.oswLastQueryResult');assert {r['id']:r for r in actual['rows']}==wanted
        assert actual['chart_scene']==expected['chart_scene'] and actual['map_scene'] is None
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        assert not errors,errors
        # Test the shipped ABI as well as the native loader against mutations
        # of the actual packet; no mocked measurements or parser substitutes.
        bundle=load_bundle(ROOT/'almanac/query-data.json')
        page.route('**/nwasc-guard.html',lambda r:r.fulfill(body='<title>Mean-core source guard</title>',content_type='text/html'))
        page.goto(BASE+'/nwasc-guard.html')
        for mode in ['depth_support','source_rebinding','canonical_transfer']:
            bad=copy.deepcopy(bundle)
            row=next(r for r in bad['collections']['proposed_widths'] if r['id']==n.records()[1]['id'])
            if mode=='depth_support':row['fixed_layer_bounds_m']=[50,530]
            elif mode=='source_rebinding':bad['manifest']['input_sha256'][n.FILE]='0'*64
            else:
                transferred=copy.deepcopy(row);transferred.pop('proposed_current_id');transferred['current_id']='norwegian'
                bad['collections']['widths'].append(transferred)
            with TemporaryDirectory(dir=out) as directory:
                path=Path(directory)/'invalid.json';path.write_text(json.dumps(bad,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
                result=subprocess.run([str(CLI),str(path),'-'],input='{}',capture_output=True,text=True,encoding='utf-8')
                assert result.returncode==2 and not result.stdout,(mode,result.stderr)
                result=page.evaluate('''async path=>{
                    const {instance}=await WebAssembly.instantiate(await(await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports;
                    const b=new Uint8Array(await(await fetch(path)).arrayBuffer()),p=e.osw_alloc(b.length);
                    try{new Uint8Array(e.memory.buffer,p,b.length).set(b);e.osw_load(p,b.length);
                        return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));
                    }finally{e.osw_dealloc(p,b.length);}
                }''','/'+path.relative_to(ROOT).as_posix())
                assert result['ok'] is False,(mode,result)
        assert not errors,errors;browser.close()
    receipt={'status':'PASS','native_wasm_exact':True,'source_exact':True,'keyboard_source_and_card_links':True,
        'phone_320px':True,'paired_edges_not_inferred':True,'canonical_widths_not_changed':True,'actual_native_wasm_rejections':3,
        'report_sha256':n.digest(n.FILE),'wasm_sha256':hashlib.sha256((ROOT/'almanac/query-engine.wasm').read_bytes()).hexdigest(),'page_errors':errors}
    (out/'browser-result.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))

if __name__=='__main__':main()
