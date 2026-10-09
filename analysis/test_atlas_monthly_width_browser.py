"""Historical chart months, cleanup, shared state and scope failure handling."""
import os
from playwright.sync_api import sync_playwright,expect

BASE='http://127.0.0.1:8788/almanac/reference-routes.html?atlas-layout=map&atlas-feature=current%3Aleeuwin'

def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'),headless=True)
        page=browser.new_page(viewport={'width':1200,'height':950});page.emulate_media(reduced_motion='reduce')
        errors=[];direct=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.route('**/research/*.json',lambda r:(direct.append(r.request.url),r.fulfill(status=503,body='Direct reads disabled'))[-1])
        page.goto(BASE+'&atlas-width-month=4#route-atlas',wait_until='networkidle')
        page.wait_for_function('document.querySelector(".atlas-width-month")?.disabled===false')
        assert page.locator('.atlas-width-month').input_value()=='4'
        assert '132 km' in page.locator('.atlas-width-month-status').inner_text()
        assert 'not confidence intervals' in page.locator('.atlas-monthly-width').inner_text()
        assert 'combined period is unresolved' in page.locator('.atlas-monthly-width').inner_text()
        frame=page.locator('#route-atlas-map').get_attribute('viewBox')
        page.locator('.atlas-width-month').select_option('11')
        page.locator('.atlas-width-play').click()
        page.wait_for_function('document.querySelector(".atlas-width-month").value==="12"')
        assert page.locator('.atlas-width-play').is_disabled()
        page.wait_for_timeout(2000)
        assert page.locator('.atlas-width-month').input_value()=='12'
        assert page.locator('#route-atlas-map').get_attribute('viewBox')==frame
        share=page.locator('[data-atlas-share]').get_attribute('href')
        assert 'atlas-width-month=12' in share
        page.goto(share,wait_until='networkidle')
        page.wait_for_function('document.querySelector(".atlas-width-month")?.disabled===false')
        assert page.locator('.atlas-width-month').input_value()=='12'
        page.locator('.atlas-width-month').select_option('9')
        assert '90 km' in page.locator('.atlas-width-month-status').inner_text()
        page.locator('.atlas-monthly-width summary').click()
        assert page.locator('.atlas-monthly-width tbody tr').count()==12
        page.set_viewport_size({'width':320,'height':900})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.set_viewport_size({'width':860,'height':1100})
        page.locator('.atlas-monthly-width').scroll_into_view_if_needed()
        page.locator('.atlas-monthly-width').screenshot(path='figures/leeuwin-monthly-plot-review.png')
        page.locator('.atlas-width-play').click()
        page.locator('#route-atlas-select').select_option('current:agulhas')
        url=page.url;page.wait_for_timeout(2000)
        assert page.url==url and 'atlas-width-month=' not in url
        assert page.locator('.atlas-monthly-width').count()==0
        # Invalid source scope must not turn into chart playback or geometry.
        # Exercise the presentation guard after verified snapshot delivery.
        page.evaluate("""async()=>{const docs=structuredClone(await window.oswAtlasSourcesReady);docs['research/leeuwin-a101-monthly-plot-extraction.json'].is_confidence_interval=true;window.oswAtlasSourcesReady=Promise.resolve(docs);}""")
        page.locator('#route-atlas-select').select_option('current:leeuwin')
        expect(page.locator('.atlas-width-month-status')).to_contain_text('unavailable or invalid',timeout=90000)
        assert page.locator('.atlas-width-play').is_disabled()
        assert page.locator('#route-atlas-preview > h3').inner_text()=='Leeuwin Current'
        assert not direct and not errors,(direct,errors);browser.close()
    print('OK: 12 historical readings, margins, shared month, December stop, unchanged geometry, cleanup, mobile and invalid evidence')

if __name__=='__main__':main()
