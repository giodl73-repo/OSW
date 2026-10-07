"""Four chart profiles retain missing samples, shared season and map independence."""
import os
from playwright.sync_api import sync_playwright,expect

BASE='http://127.0.0.1:8788/almanac/reference-routes.html?atlas-layout=map&atlas-feature=current%3Akuroshio'

def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'),headless=True)
        page=browser.new_page(viewport={'width':860,'height':1100});page.emulate_media(reduced_motion='reduce')
        errors=[];direct=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.route('**/research/*.json',lambda r:(direct.append(r.request.url),r.fulfill(status=503,body='Direct reads disabled'))[-1])
        page.goto(BASE+'&atlas-width-season=spring#route-atlas',wait_until='networkidle')
        page.wait_for_function('document.querySelector(".atlas-width-season")?.disabled===false')
        assert page.locator('.atlas-width-season').input_value()=='spring'
        assert '15 of 16' in page.locator('.atlas-profile-status').inner_text()
        section=page.locator('.atlas-seasonal-width-profile')
        assert 'not measurement uncertainty or confidence' in section.inner_text()
        section.locator('summary').click()
        assert section.locator('tbody tr').count()==16
        assert section.locator('tbody').inner_text().count('missing')==1
        view=page.locator('#route-atlas-map').get_attribute('viewBox')
        page.locator('.atlas-profile-play').click()
        page.wait_for_function('document.querySelector(".atlas-width-season").value==="autumn"')
        assert page.locator('.atlas-profile-play').is_disabled()
        page.wait_for_timeout(2000);assert page.locator('.atlas-width-season').input_value()=='autumn'
        assert page.locator('#route-atlas-map').get_attribute('viewBox')==view
        share=page.locator('[data-atlas-share]').get_attribute('href');assert 'atlas-width-season=autumn' in share
        page.goto('about:blank')
        page.goto(share,wait_until='networkidle');page.wait_for_function('document.querySelector(".atlas-width-season")?.disabled===false')
        assert page.locator('.atlas-width-season').input_value()=='autumn'
        page.locator('.atlas-width-season').select_option('winter')
        if section.locator('details').get_attribute('open') is None:section.locator('summary').click()
        assert section.locator('tbody').inner_text().count('missing')==2
        section.screenshot(path='figures/kuroshio-seasonal-profile-review.png')
        page.set_viewport_size({'width':320,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('.atlas-profile-play').click();page.locator('#route-atlas-select').select_option('current:agulhas')
        url=page.url;page.wait_for_timeout(2000);assert page.url==url and 'atlas-width-season=' not in url
        assert page.locator('.atlas-seasonal-width-profile').count()==0
        # Exercise the presentation guard after verified snapshot delivery.
        page.evaluate("""async()=>{const docs=structuredClone(await window.oswAtlasSourcesReady);docs['research/kuroshio-ecs-seasonal-width-profile-extraction.json'].geographic_playback_eligible=true;window.oswAtlasSourcesReady=Promise.resolve(docs);}""")
        page.locator('#route-atlas-select').select_option('current:kuroshio')
        expect(page.locator('.atlas-profile-status')).to_contain_text('unavailable or invalid',timeout=90000)
        assert page.locator('.atlas-profile-play').is_disabled()
        assert page.locator('.atlas-width-record').count()==3
        assert not direct and not errors,(direct,errors);browser.close()
    print('OK: four profiles, missing samples, shared season, map unchanged, autoplay stop/cleanup, mobile and invalid-source fallback')

if __name__=='__main__':main()
