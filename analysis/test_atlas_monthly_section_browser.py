"""Saved monthly profiles preserve selected identity, source scope and cleanup."""
import copy,json,os
from pathlib import Path
from urllib.parse import parse_qs,urlparse
from playwright.sync_api import sync_playwright,expect

ROOT=Path(__file__).resolve().parents[1]
BASE='http://127.0.0.1:8788/almanac/reference-routes.html'


def main():
    document=json.loads((ROOT/'research/pacific-necc-oscar-2013-section-diagnostic.json').read_bytes())
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1440,'height':1000});errors=[];direct=[]
        page.set_default_timeout(90000)
        def block_direct(route):
            if 'reference-routes.html' in route.request.frame.url:
                direct.append(route.request.url);route.fulfill(status=503,body='Direct reads disabled')
            else:route.continue_()
        page.route('**/research/*.json',block_direct)
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.clock.install()
        page.goto(BASE+'?atlas-feature=current%3Apacific-north-equatorial-countercurrent#route-atlas',wait_until='networkidle')
        expect(page.locator('.route-card')).to_have_count(64,timeout=90000)
        expect(page.locator('.inventory-addition-card')).to_have_count(28,timeout=90000)
        page.clock.run_for(100)
        page.wait_for_function('document.querySelector(".atlas-monthly-select")?.disabled===false')
        select=page.locator('.atlas-monthly-select')
        assert select.locator('option').count()==12
        atlas=page.locator('#route-atlas-map');cardmap=page.locator('.atlas-monthly-map')
        fixed=cardmap.get_attribute('viewBox')
        assert page.locator('#route-atlas-map .atlas-monthly-station').count()==37
        assert page.locator('#route-atlas-map .atlas-monthly-boundary').count()==2
        assert atlas.get_attribute('viewBox')!='60 90 1480 740'
        for month in document['months']:
            select.select_option(month['id'])
            assert month['label'] in page.locator('.atlas-monthly-status').inner_text()
            assert f"about {round(month['zero_crossing']['span_km']/10)*10} km" in page.locator('.atlas-monthly-status').inner_text()
            assert parse_qs(urlparse(page.url).query)['atlas-section']==[month['id']]
        assert page.locator('.atlas-monthly-play').is_disabled()
        select.select_option(document['months'][0]['id'])
        page.locator('.atlas-monthly-play').click();page.clock.run_for(2201)
        assert select.input_value()==document['months'][1]['id']
        page.locator('.atlas-monthly-play').click()
        page.locator('.atlas-monthly-play').click()
        page.evaluate('Object.defineProperty(document,"hidden",{configurable:true,value:true});document.dispatchEvent(new Event("visibilitychange"));delete document.hidden;')
        paused=select.input_value();page.clock.run_for(4400)
        assert select.input_value()==paused
        assert page.locator('.atlas-monthly-play').inner_text()=='Play monthly profiles'
        select.select_option(document['months'][10]['id'])
        page.locator('.atlas-monthly-play').click();page.clock.run_for(2201)
        assert select.input_value()==document['months'][11]['id']
        page.clock.run_for(4400)
        assert select.input_value()==document['months'][11]['id']
        assert page.locator('.atlas-monthly-play').inner_text()=='Play monthly profiles'
        select.select_option(document['months'][3]['id'])
        saved=page.locator('#route-atlas-preview [data-atlas-share]').get_attribute('href')
        page.reload(wait_until='networkidle');page.clock.run_for(100)
        page.wait_for_function('document.querySelector(".atlas-monthly-select")?.disabled===false')
        assert select.input_value()==document['months'][3]['id']
        assert page.url==saved
        page.locator('#route-atlas-in').click()
        assert cardmap.get_attribute('viewBox')==fixed
        station=page.locator('#route-atlas-map .atlas-monthly-station').nth(15)
        page.mouse.move(0,0);select.focus()
        assert station.locator('text').evaluate('(e)=>getComputedStyle(e).opacity')=='0'
        station.focus();page.keyboard.press('Enter')
        assert 'monthly surface-product mean' in page.locator('.atlas-monthly-sample-info').inner_text()
        assert station.locator('text').evaluate('(e)=>getComputedStyle(e).opacity')=='1'
        page.locator('.atlas-monthly-details').click()
        page.wait_for_function('document.querySelectorAll("#section-rows tr").length===12')
        assert parse_qs(urlparse(page.url).query)['month']==['2013-04']
        page.get_by_role('link',name='Return to this current on the atlas').click()
        page.wait_for_function('document.querySelector(".atlas-monthly-select")?.disabled===false')
        assert select.input_value()==document['months'][3]['id']
        page.set_viewport_size({'width':860,'height':1100})
        page.locator('.atlas-monthly-section').screenshot(path='figures/necc-monthly-atlas-card-review.png')
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert cardmap.is_visible()
        page.locator('#route-atlas-world').click()
        assert page.locator('.atlas-monthly-overlay').count()==0
        assert page.locator('#route-atlas-preview').is_hidden()
        assert 'atlas-section' not in page.url
        assert atlas.get_attribute('viewBox')=='60 90 1480 740'
        page.locator('#route-atlas-select').select_option('current:pacific-north-equatorial-countercurrent')
        page.wait_for_function('document.querySelector(".atlas-monthly-select")?.disabled===false')
        page.locator('.atlas-monthly-play').click()
        page.locator('#route-atlas-select').select_option('current:agulhas');page.clock.run_for(4400)
        assert page.locator('#route-atlas-select').input_value()=='current:agulhas'
        assert page.locator('.atlas-monthly-overlay').count()==0
        assert 'has-observed-samples' not in (atlas.get_attribute('class') or '')
        page.locator('#route-atlas-world').click()
        page.evaluate("""async()=>{window.oswTestAtlasDocuments=await window.oswAtlasSourcesReady;window.oswAtlasSourcesReady=new Promise(resolve=>setTimeout(()=>resolve(window.oswTestAtlasDocuments),300));}""")
        page.locator('#route-atlas-select').select_option('current:pacific-north-equatorial-countercurrent')
        page.locator('#route-atlas-world').click();page.clock.run_for(301)
        assert page.locator('.atlas-monthly-overlay').count()==0
        assert page.locator('#route-atlas-preview').is_hidden()
        relabeled=copy.deepcopy(document);relabeled['annual_width_range_km']=[210,640]
        reversed_edges=copy.deepcopy(document)
        reversed_edges['months'][0]['zero_crossing']['boundaries']['south']['latitude']=11
        for invalid in [None,relabeled,reversed_edges]:
            # Inject a bad presentation document after checked source delivery.
            page.evaluate("""doc=>{const docs=structuredClone(window.oswTestAtlasDocuments);if(doc===null)delete docs['research/pacific-necc-oscar-2013-section-diagnostic.json'];else docs['research/pacific-necc-oscar-2013-section-diagnostic.json']=doc;window.oswAtlasSourcesReady=Promise.resolve(docs);}""",invalid)
            page.locator('#route-atlas-select').select_option('current:pacific-north-equatorial-countercurrent')
            expect(page.locator('.atlas-monthly-status')).to_contain_text('standalone',timeout=90000)
            assert page.locator('.atlas-monthly-overlay').count()==0
            assert page.locator('.atlas-monthly-details').get_attribute('href')=='necc-section.html'
            page.locator('#route-atlas-world').click()
        assert not direct and not errors,(direct,errors)
        browser.close()
    print('OK: 12 monthly atlas profiles, 37 grid samples, boundaries, explicit playback/end stop, shared/reloaded month, detail return, keyboard values, mobile, reset and delayed/invalid fallback')


if __name__=='__main__':main()
