"""A reviewed current is present across the working catalogue without invented measurements."""
import json,os
from urllib.parse import quote
from playwright.sync_api import sync_playwright,expect
from test_current_research_evidence_browser import ROOT,BASE,native

ID='southern-east-madagascar';ENTITY='current:'+ID
def main():
    out=ROOT/'.pytest_cache/current-identity-admission';out.mkdir(exist_ok=True)
    entry=json.loads((ROOT/'research/ocean-current-identity-admissions.json').read_bytes())['entries'][0]
    query={'collection':'current_identity_admissions','filters':[{'field':'entity_id','op':'eq','value':ENTITY}],'limit':1}
    errors=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1280,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(BASE+'/almanac/index.html#working-current-catalogue')
        page.wait_for_function('window.oswCurrentIdentityAdmissions',timeout=120000)
        expect(page.locator('#working-current-catalogue')).to_contain_text('101 accepted named currents')
        link=page.locator('#working-current-catalogue').get_by_role('link',name=entry['entity']['label'],exact=True)
        link.focus();page.keyboard.press('Enter')
        expect(page.locator('#object-title')).to_have_text(entry['entity']['label'],timeout=120000)
        expect(page.locator('body')).to_contain_text('Source-defined southward western boundary current',ignore_case=True)
        page.goto(BASE+'/almanac/query.html?q='+quote(json.dumps(query)))
        page.wait_for_function('window.oswLastQueryResult',timeout=120000)
        value=page.evaluate('window.oswLastQueryResult');assert value==native(query)
        assert value['total']==1 and value['rows'][0]==entry
        page.goto(BASE+'/almanac/reference-routes.html?atlas-feature='+quote(ENTITY)+'#route-atlas')
        page.wait_for_function('document.querySelectorAll("#route-atlas-select option").length===102',timeout=120000)
        expect(page.locator('#route-atlas-preview > h3')).to_have_text(entry['entity']['label'])
        assert page.locator('.route-atlas-station').count()==100
        assert page.locator('.route-atlas-station[data-current-id="'+ENTITY+'"]').count()==0
        expect(page.locator('#route-atlas-status')).to_contain_text('no source-supported map placement')
        assert page.locator('.inventory-addition-card').count()==28
        card=page.locator('#inventory-addition-'+ID)
        expect(card).to_contain_text('Current identity admitted')
        image=card.locator('.proposed-source-dimensions img');image.scroll_into_view_if_needed()
        page.wait_for_function('()=>document.querySelector("#inventory-addition-southern-east-madagascar img")?.naturalWidth>0')
        image.screenshot(path=str(out/'admitted-dimensions.png'))
        page.set_viewport_size({'width':320,'height':950});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        card.screenshot(path=str(out/'admitted-card-mobile.png'))
        page.goto(BASE+'/almanac/seasons.html?current='+ID)
        page.wait_for_function('window.oswSeasonSnapshot',timeout=120000)
        expect(page.locator('#season-current')).to_have_value(ID)
        assert page.locator('#season-current option').count()==101
        expect(page.locator('#season-play')).to_be_disabled()
        expect(page.locator('#season-range')).to_contain_text('identity admitted')
        plan=page.evaluate('window.oswSeasonSnapshot.phase_plans["southern-east-madagascar"]')
        assert plan['phases']==[] and not plan['can_play']
        page.goto(BASE+'/almanac/dashboard.html')
        page.wait_for_function('window.oswDashboardSnapshot',timeout=120000)
        snapshot=page.evaluate('window.oswDashboardSnapshot.snapshot')
        assert snapshot['counts']['named_current']==101 and len(snapshot['entries'])==241
        row=next(r for r in snapshot['entries'] if r['id']==ENTITY)
        assert row['map_features']==[] and row['latest_observation_date'] is None
        assert row['capabilities']['scoped_width']==0 and row['capabilities']['reported_length']==0
        assert not errors,errors
        browser.close()
    result={'status':'PASS','accepted_currents':101,'pending_proposals':28,'dashboard_objects':241,
        'native_wasm_admission_exact':True,'mapped_current_stations':100,'new_current_unlocated':True,
        'seasonal_index':101,'new_current_playback':False,'main_index_object_query_atlas_seasons_dashboard':True,
        'keyboard_navigation':True,'phone_reflow':True,'page_errors':errors}
    (out/'browser-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':main()
