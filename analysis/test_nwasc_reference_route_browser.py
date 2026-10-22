"""The added regional route is queryable, mapped and navigable without playback."""
import json
import os
from urllib.parse import quote
from playwright.sync_api import sync_playwright, expect
import nwasc_source_anchor_route as n
from test_current_research_evidence_browser import BASE, native
from browser_inventory_expectations import CURRENT_COUNT, MOTION_COUNT


def main():
    doc,_=n.verify_inputs()
    out=n.ROOT/'.pytest_cache/nwasc-anchor-route/browser';out.mkdir(exist_ok=True)
    queries=[
        {'collection':'objects','filters':[{'field':'id','op':'eq','value':'current:'+n.CURRENT}],'limit':1},
        {'collection':'reference_routes','filters':[{'field':'current_id','op':'eq','value':n.CURRENT}],'limit':1},
        {'collection':'route_decisions','filters':[{'field':'current_id','op':'eq','value':n.CURRENT}],'limit':1},
        {'collection':'objects','filters':[{'field':'type','op':'eq','value':'named_current'}],'limit':200},
        {'collection':'reference_routes','limit':200},
    ]
    errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page=browser.new_page(viewport={'width':1280,'height':900})
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto(BASE+'/almanac/query.html?q='+quote(json.dumps(queries[0])))
        page.wait_for_function('window.oswLastQueryResult',timeout=180000)
        page.locator('#query-advanced > summary').click()
        for i,q in enumerate(queries):
            if i:
                page.locator('#query-json').fill(json.dumps(q));page.evaluate('window.oswLastQueryResult=null')
                page.locator('#query-run-json').click();page.wait_for_function('window.oswLastQueryResult',timeout=120000)
            result=page.evaluate('window.oswLastQueryResult');assert result==native(q)
            assert result['total']==(78 if i==4 else CURRENT_COUNT if i==3 else 1)
            if i==0:
                row=result['rows'][0];assert row['route_ids']==[n.ROUTE]
                assert row['published_length_km']==3500 and row['capabilities']['scoped_width']==8
                assert row['map_features'][0]['geometry']['coordinates']==n.ANCHORS
                assert row['map_features'][0]['physical_state_join_eligible'] is False
                assert result['map_scene']['mapped_objects']==1 and result['map_scene']['unmapped_objects']==0
            if i==1:
                assert result['rows']==[n.route_record(doc)]
                assert result['map_scene']['mapped_objects']==1
            if i==2:
                assert result['rows'][0]['source_decision']==doc['planning_decision']
                assert result['rows'][0]['source_catalog_file']==n.FILE
            if i==3:
                assert result['map_scene']['mapped_objects']==CURRENT_COUNT and result['map_scene']['unmapped_objects']==0
                actual=set(page.locator('#query-map-features').evaluate('(e)=>[...e.children].map(n=>n.dataset.entity)'))
                assert actual=={r['id'] for r in result['rows']}
            if i==4:
                scene=result['map_scene']
                assert scene['inspection_collection']=='reference_routes'
                assert scene['mapped_objects']==78 and scene['unmapped_objects']==0
                assert {f['entity_id'] for f in scene['features']}=={r['id'] for r in result['rows']}
                assert all(f['role']=='editorial_reference_route' for f in scene['features'])
                mark=page.locator('#query-map-features [data-entity="'+n.ROUTE+'"]')
                mark.focus();page.keyboard.press('Enter')
                expect(page.locator('#query-detail')).to_contain_text(n.ROUTE)
            print('PASS actual native/WASM route and map',i,flush=True)
        page.goto(BASE+'/almanac/reference-routes.html?atlas-feature=current%3Anorwegian-atlantic-slope#route-atlas')
        page.wait_for_function('window.oswAtlasSnapshot',timeout=180000)
        expect(page.locator('#route-atlas-preview > h3')).to_have_text('Norwegian Atlantic Slope Current',timeout=120000)
        assert page.locator('.route-atlas-station').count()==CURRENT_COUNT
        snap=page.evaluate('window.oswAtlasSnapshot')
        frozen=json.loads((n.ROOT/n.BASE).read_bytes())
        assert snap['working_reference_routes']==n.extend_catalogue(frozen,doc)
        assert snap['sources_json'][n.BASE].encode('utf8')==(n.ROOT/n.BASE).read_bytes()
        assert snap['sources_json'][n.FILE].encode('utf8')==(n.ROOT/n.FILE).read_bytes()
        assert len(frozen['candidates'])==77 and len(snap['working_reference_routes']['candidates'])==78
        link=page.locator('#route-atlas-preview').get_by_role('link',name='Full route card, measurements and sources ↓',exact=True)
        link.focus();page.keyboard.press('Enter')
        card=page.locator('#'+n.ROUTE);expect(card).to_be_focused()
        expect(card).to_contain_text('260 km')
        expect(card).to_contain_text('Source-reference connection only')
        assert 'undefined' not in card.inner_text()
        page.set_viewport_size({'width':320,'height':900})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        card.get_by_role('link',name='Open route map at full size',exact=True).focus();page.keyboard.press('Enter')
        expect(page.locator('svg[role=img]')).to_have_attribute('role','img')
        expect(page.locator('#desc')).to_contain_text('not physical uncertainty')
        page.set_viewport_size({'width':1000,'height':660});page.screenshot(path=str(out/'regional-reference.png'))
        page.goto(BASE+'/almanac/seasons.html?current='+n.CURRENT)
        page.wait_for_function('window.oswSeasonSnapshot',timeout=180000)
        expect(page.locator('#season-play')).to_be_disabled()
        plan=page.evaluate('window.oswSeasonSnapshot.phase_plans["norwegian-atlantic-slope"]')
        assert not plan['can_play'] and plan['eligible_indices']==[]
        assert not errors,errors
        browser.close()
    receipt={'status':'PASS','actual_native_wasm_queries':5,'mapped_named_currents':CURRENT_COUNT,
        'dashboard_objects':MOTION_COUNT,'reference_routes':78,'route_owners':72,'frozen_catalogue_addresses_exact':True,
        'keyboard_current_to_route_card_to_map':True,'mobile_320px':True,'seasonal_playback_disabled':True}
    (out/'result.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8');print(json.dumps(receipt),flush=True)


if __name__=='__main__':
    main()
