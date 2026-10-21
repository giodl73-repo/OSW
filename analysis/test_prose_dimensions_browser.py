"""Working ranking, local width, source qualification and unavailable geography agree."""
import json,os
from urllib.parse import quote
from playwright.sync_api import sync_playwright,expect
from test_current_research_evidence_browser import ROOT,BASE,native
import current_measurement_admissions as m

def main():
    doc=m.verify();out=ROOT/'.pytest_cache/prose-dimensions-browser';out.mkdir(exist_ok=True)
    query={'collection':'current_measurement_admissions','filters':[{'field':'entity_id','op':'eq','value':m.ENTITY}],'limit':1}
    errors=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1280,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(BASE+'/almanac/query.html?q='+quote(json.dumps(query)))
        page.wait_for_function('window.oswLastQueryResult',timeout=120000)
        result=page.evaluate('window.oswLastQueryResult');assert result==native(query)
        assert result['total']==1 and result['rows'][0]['measurement']==doc['measurement']
        ranking=native({'collection':'length_assessments','filters':[{'field':'rank_eligible','op':'eq','value':True}],'sort':{'field':'published_length_km','direction':'desc'},'limit':100})
        assert ranking['total']==12 and ranking['rows'][-1]['published_rank']==12
        assert ranking['rows'][-1]['published_length_km']==650
        width=native({'collection':'widths','filters':[{'field':'id','op':'eq','value':m.WIDTH_ID}],'limit':1})
        assert width['rows'][0]==doc['width_record']
        page.goto(BASE+'/almanac/reference-routes.html#inventory-addition-southern-east-madagascar')
        card=page.locator('#inventory-addition-southern-east-madagascar')
        expect(card).to_contain_text('working reported-length rank 12',timeout=120000)
        expect(page.locator('#width-'+m.WIDTH_ID)).to_contain_text('120')
        assert page.locator('#width-rows tr').count()==157
        assert page.locator('#width-decision-rows tr').count()==101
        image=card.locator('.proposed-source-dimensions img');image.scroll_into_view_if_needed()
        page.wait_for_function('()=>document.querySelector("#inventory-addition-southern-east-madagascar img")?.naturalWidth>0')
        image.screenshot(path=str(out/'dimensions-desktop.png'))
        link=card.get_by_role('link',name='Query the dimension admission and source definitions',exact=True)
        link.focus();page.keyboard.press('Enter');page.wait_for_function('window.oswLastQueryResult',timeout=120000)
        assert page.evaluate('window.oswLastQueryResult')==native(query)
        page.set_viewport_size({'width':320,'height':1000})
        page.goto(BASE+'/almanac/seasons.html?current=southern-east-madagascar')
        page.wait_for_function('window.oswSeasonSnapshot',timeout=120000)
        expect(page.locator('#season-value')).to_contain_text('120')
        expect(page.locator('#season-definition')).to_contain_text('not a verified width layer')
        expect(page.locator('#season-play')).to_be_disabled()
        assert page.locator('#season-bar').evaluate('(n)=>n.parentElement.hidden')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        plan=page.evaluate('window.oswSeasonPlan');assert len(plan['phases'])==1 and not plan['can_play']
        page.locator('#regional-width-range').screenshot(path=str(out/'survey-mobile.png'))
        assert not errors,errors;browser.close()
    receipt={'status':'PASS','ranked_lengths':12,'new_length_km':650,'new_length_rank':12,'scoped_width_records':157,
        'scoped_width_km':120,'single_non_playable_survey_state':True,'width_bar_hidden':True,
        'native_wasm_admission_equal':True,'keyboard_query_link':True,'phone_reflow':True,'page_errors':errors}
    (out/'browser-result.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))

if __name__=='__main__':main()
