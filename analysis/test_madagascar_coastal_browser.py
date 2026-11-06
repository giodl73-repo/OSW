"""The new geographic reference connects atlas, card, state, query and survey UI."""
from browser_inventory_expectations import CURRENT_COUNT

import json,os
from urllib.parse import quote
from playwright.sync_api import sync_playwright,expect
from test_current_research_evidence_browser import ROOT,BASE,native
import madagascar_reference_curve as curve
import madagascar_coastline_comparison as coast

ENTITY='current:southern-east-madagascar'

def main():
    doc,catalog,_=curve.verify_inputs();out=ROOT/'.pytest_cache/madagascar-coastal-browser';out.mkdir(exist_ok=True)
    query={'collection':'reference_routes','filters':[{'field':'id','op':'eq','value':curve.ROUTE_ID}],'limit':1}
    source_query={'document':curve.FILE,'pointer':'/scenarios','limit':100}
    errors=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1380,'height':1100});page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(BASE+'/almanac/query.html?q='+quote(json.dumps(query)))
        page.wait_for_function('window.oswLastQueryResult',timeout=120000)
        result=page.evaluate('window.oswLastQueryResult');assert result==native(query)
        assert result['total']==1 and result['rows'][0]==curve.catalogue_row(doc)
        owner=native({'collection':'objects','filters':[{'field':'id','op':'eq','value':ENTITY}],'limit':1})['rows'][0]
        assert owner['route_ids']==[curve.ROUTE_ID] and owner['published_length_km']==650
        assert owner['latest_observation_date'] is None and len(owner['map_features'])==1
        assert owner['source_ids']==curve.catalogue_row(doc)['source_ids']
        states=native({'collection':'state_links','filters':[{'field':'entity_id','op':'eq','value':ENTITY}],'limit':100})
        assert states['total']==1 and states['rows'][0]['state_code']=='EAFR'
        assert states['rows'][0]['kind']=='editorial_coastal_reference_curve' and states['rows'][0]['observation_date'] is None
        url=BASE+'/almanac/reference-routes.html?atlas-layout=map&atlas-feature='+quote(ENTITY)+'&atlas-route='+curve.ROUTE_ID+'#route-atlas'
        page.goto(url)
        page.wait_for_function('window.oswAtlasSnapshot',timeout=120000)
        page.wait_for_function('document.querySelectorAll(".route-atlas-station").length==='+str(CURRENT_COUNT),timeout=120000)
        assert page.locator('.route-card').count()==77
        assert page.locator('.route-atlas-station[data-current-id="'+ENTITY+'"]').count()==1
        assert page.locator('.route-atlas-station[data-current-id="'+ENTITY+'"]').get_attribute('data-placement-role')=='editorial_reference_route_vertex'
        expect(page.locator('#route-atlas-preview > h3')).to_have_text('Southern East Madagascar Current')
        raw=page.evaluate('(p)=>window.oswAtlasSnapshot.sources_json[p]',curve.FILE)
        assert json.loads(raw)==doc
        joined=json.loads(page.evaluate('(p)=>window.oswAtlasSnapshot.sources_json[p]',curve.WORKING_JOIN))
        link=next(r for r in joined['states']['EAFR']['route_candidates'] if r['candidate_id']==curve.ROUTE_ID)
        assert link['crossing_scenario_count']==27 and link['comparison_group']=='osw_offshore_coastal_reference_curves'
        page.locator('#route-atlas-card-link').focus();page.keyboard.press('Enter')
        card=page.locator('#'+curve.ROUTE_ID)
        expect(card).to_contain_text('Coast-following geographic reference only.')
        expect(card).to_contain_text('700–900 km')
        image=card.locator('img.route-map');image.scroll_into_view_if_needed()
        page.wait_for_function('(id)=>document.querySelector("#"+id+" img.route-map")?.naturalWidth>0',arg=curve.ROUTE_ID)
        image.screenshot(path=str(out/'coastal-reference-desktop.png'))
        card.get_by_role('link',name='Back to global current map ↑',exact=True).focus();page.keyboard.press('Enter')
        assert page.url.endswith('#route-atlas')
        page.set_viewport_size({'width':320,'height':1000})
        page.goto(BASE+'/almanac/reference-routes.html#'+curve.ROUTE_ID)
        expect(card).to_contain_text('Projected offsets are not current widths',timeout=120000)
        image.scroll_into_view_if_needed();page.wait_for_function('(id)=>document.querySelector("#"+id+" img.route-map")?.naturalWidth>0',arg=curve.ROUTE_ID)
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        card.screenshot(path=str(out/'coastal-reference-mobile.png'))
        page.goto(BASE+'/almanac/seasons.html?current=southern-east-madagascar')
        page.wait_for_function('window.oswSeasonSnapshot',timeout=120000)
        assert len(page.evaluate('window.oswSeasonSnapshot.phase_plans["southern-east-madagascar"].phases'))==1
        expect(page.locator('#season-play')).to_be_disabled();expect(page.locator('#season-value')).to_contain_text('120')
        assert page.locator('#season-bar').evaluate('(n)=>n.parentElement.hidden')
        assert not errors,errors;browser.close()
    receipt={'status':'PASS','native_wasm_route_exact':True,'all_27_curves_retained':True,'route_candidates':77,
        'mapped_currents':CURRENT_COUNT,'navigation_state':'EAFR','state_scenarios':27,'no_dated_axis':True,
        'published_length_km_unchanged':650,'survey_width_km_unchanged':120,'no_seasonal_playback':True,
        'keyboard_map_card_return':True,'phone_reflow':True,'page_errors':errors}
    (out/'browser-result.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))

if __name__=='__main__':main()
