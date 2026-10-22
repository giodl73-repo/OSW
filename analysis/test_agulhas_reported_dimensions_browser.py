"""One scoped source description across native/WASM query, atlas, card and seasons."""
from browser_inventory_expectations import SCOPED_WIDTH_COUNT

import hashlib,json,os
from urllib.parse import quote
from playwright.sync_api import sync_playwright,expect
from test_current_research_evidence_browser import ROOT,BASE,native
import agulhas_reported_dimensions as a

def main():
    out=ROOT/'.pytest_cache/agulhas-reported-browser';out.mkdir(exist_ok=True)
    doc,_=a.verify_inputs();errors=[]
    q={'collection':'diagnostics','filters':[{'field':'id','op':'eq','value':a.ID}],'limit':1}
    expected=native(q);assert expected['total']==1
    width_q={'collection':'widths','filters':[{'field':'id','op':'eq','value':a.WIDTH_ID}],'limit':1}
    width=native(width_q);assert width['rows']==[doc['width_record']]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1360,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(BASE+'/almanac/query.html?q='+quote(json.dumps(q)))
        page.wait_for_function('window.oswLastQueryResult',timeout=120000)
        assert page.evaluate('window.oswLastQueryResult')==expected
        panel=page.locator('.agulhas-reported-dimensions');expect(panel).to_be_visible()
        expect(panel).to_contain_text('excluded from the whole-current length ranking')
        expect(panel).to_contain_text('do not define a 200–219 km range')
        page.wait_for_function('document.querySelector(".agulhas-reported-dimensions img")?.naturalWidth>0')
        panel.screenshot(path=str(out/'query-desktop.png'))
        original=panel.get_by_role('link',name='Original publication · CC BY 4.0');assert original.get_attribute('href')=='../'+a.DIRECTORY+'article.pdf'
        panel.get_by_role('link',name='Inspect the scoped core-width record').focus();page.keyboard.press('Enter')
        page.wait_for_function('window.oswLastQueryResult?.collection==="widths"',timeout=120000)
        assert page.evaluate('window.oswLastQueryResult')==width
        page.goto(BASE+'/almanac/reference-routes.html?atlas-layout=map&atlas-feature=current%3Aagulhas#route-atlas')
        preview=page.locator('#route-atlas-preview .agulhas-reported-dimensions');expect(preview).to_be_visible(timeout=120000)
        assert json.loads(page.evaluate('(path)=>window.oswAtlasSnapshot.sources_json[path]',a.FILE))==doc
        assert page.evaluate('window.oswAtlasSnapshot.agulhas_reported_scene')==expected['chart_scene']
        expect(page.locator('#width-'+a.WIDTH_ID)).to_contain_text('200')
        assert page.locator('#width-rows tr').count()==SCOPED_WIDTH_COUNT
        page.locator('#route-atlas-card-link').focus();page.keyboard.press('Enter')
        card=page.locator('#agulhas-reference-path-candidate .agulhas-reported-dimensions');expect(card).to_be_visible(timeout=120000)
        page.set_viewport_size({'width':320,'height':1000});card.screenshot(path=str(out/'card-mobile.png'))
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        page.goto(BASE+'/almanac/seasons.html?current=agulhas');page.wait_for_function('window.oswSeasonSnapshot',timeout=120000)
        expect(page.locator('.agulhas-reported-dimensions')).to_be_visible()
        plan=page.evaluate('window.oswSeasonSnapshot.phase_plans.agulhas')
        phase=next(p for p in plan['phases'] if p['width_id']==a.WIDTH_ID)
        assert not phase['playback_step_eligible']
        page.locator('#season-phase').select_option(str(plan['phases'].index(phase)))
        expect(page.locator('#season-value')).to_contain_text('200')
        assert page.locator('#season-bar').evaluate('(node)=>node.parentElement.hidden')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        assert not errors,errors;browser.close()
    receipt={'status':'PASS','native_wasm_exact':True,'source_exact':True,'keyboard_query_link':True,'atlas_card_seasons':True,
        'phone_320px':True,'undated_state_not_playable':True,'width_bar_hidden':True,'whole_length_rank_unchanged':True,
        'wasm_sha256':hashlib.sha256((ROOT/'almanac/query-engine.wasm').read_bytes()).hexdigest(),
        'report_sha256':a.digest(a.FILE),'page_errors':errors}
    (out/'browser-result.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))

if __name__=='__main__':main()
