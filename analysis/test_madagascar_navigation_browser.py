"""Exact queryable failures, current-card figure and keyboard/phone access."""
import json,os
from urllib.parse import quote
from playwright.sync_api import sync_playwright,expect
from test_current_research_evidence_browser import ROOT,BASE,native
import madagascar_navigation_diagnostic as m

def main():
    doc,_=m.verify_inputs();out=ROOT/'.pytest_cache/madagascar-navigation-browser';out.mkdir(exist_ok=True)
    query={'collection':'diagnostics','filters':[{'field':'id','op':'eq','value':m.ID}],'limit':1}
    errors=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1280,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(BASE+'/almanac/query.html?q='+quote(json.dumps(query)))
        page.wait_for_function('window.oswLastQueryResult',timeout=120000)
        result=page.evaluate('window.oswLastQueryResult');assert result==native(query)
        assert result['total']==1 and result['rows'][0]['document']==doc
        routes=native({'collection':'reference_routes','limit':100});assert routes['total']==76
        assert not any(r['current_id']=='southern-east-madagascar' for r in routes['rows'])
        owner=native({'collection':'objects','filters':[{'field':'id','op':'eq','value':doc['entity_id']}],'limit':1})['rows'][0]
        assert owner['map_features']==[] and m.ID in owner['diagnostic_ids']
        page.goto(BASE+'/almanac/reference-routes.html#southern-east-madagascar-route-definition')
        card=page.locator('#southern-east-madagascar-route-definition')
        expect(card).to_contain_text('No current route or map feature admitted.',timeout=120000)
        image=card.locator('img');image.scroll_into_view_if_needed()
        page.wait_for_function('()=>document.querySelector("#southern-east-madagascar-route-definition img")?.naturalWidth>0')
        image.screenshot(path=str(out/'route-definition-desktop.png'))
        link=card.get_by_role('link',name='Query all route experiments and unresolved definitions',exact=True)
        link.focus();page.keyboard.press('Enter');page.wait_for_function('window.oswLastQueryResult',timeout=120000)
        assert page.evaluate('window.oswLastQueryResult')==native(query)
        page.set_viewport_size({'width':320,'height':1000})
        page.goto(BASE+'/almanac/reference-routes.html#southern-east-madagascar-route-definition')
        expect(card).to_contain_text('All 27 initial coastal scenarios',timeout=120000)
        image.scroll_into_view_if_needed();page.wait_for_function('()=>document.querySelector("#southern-east-madagascar-route-definition img")?.naturalWidth>0')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        card.screenshot(path=str(out/'route-definition-mobile.png'))
        assert not errors,errors;browser.close()
    receipt={'status':'PASS','native_wasm_exact':True,'v1_rejected_retained':27,'v2_scenarios_retained':27,'new_current_routes':0,'new_map_features':0,'keyboard_link':True,'phone_reflow':True,'page_errors':errors}
    (out/'browser-result.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))

if __name__=='__main__':main()
