"""Verify source-derived section table and atlas navigation on desktop and mobile."""
import os
from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ['OSW_TEST_BROWSER'])
        page=browser.new_page(viewport={'width':1440,'height':1100});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Apacific-north-equatorial-countercurrent#route-atlas',wait_until='networkidle')
        panel=page.locator('#route-atlas-preview')
        panel.get_by_role('link',name='2013 monthly surface-section diagnostics (not climatology) →',exact=True).click()
        page.wait_for_function('document.querySelectorAll("#section-rows tr").length===12')
        assert page.locator('#section-status').inner_text().startswith('12 resolved')
        assert 'about 640 km' in page.locator('#section-rows').inner_text()
        assert 'about 210 km' in page.locator('#section-rows').inner_text()
        assert 'not whole-current dimensions' in page.locator('.status').inner_text()
        assert page.locator('.profile-grid').evaluate('(e)=>e.complete&&e.naturalWidth>0')
        page.locator('.profile-grid').screenshot(path='figures/pacific-necc-monthly-profiles-review.png')
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert page.get_by_role('link',name='Calculation records and brackets').get_attribute('href').endswith('section-diagnostic.json')
        page.get_by_role('link',name='Return to this current on the atlas').click()
        page.wait_for_function('document.querySelector("#route-atlas-select").value==="current:pacific-north-equatorial-countercurrent"')
        assert panel.get_by_role('link',name='2013 monthly surface-section diagnostics (not climatology) →',exact=True).is_visible()
        row=page.locator('#width-decision-pacific-north-equatorial-countercurrent')
        page.wait_for_function('document.querySelector("#width-decision-pacific-north-equatorial-countercurrent").textContent.includes("derived width candidate requires review")')
        page.locator('summary').filter(has_text='Width coverage for all 100 names').click()
        assert 'derived width candidate requires review' in row.inner_text()
        row.get_by_role('link',name='Inspect derived section-width candidate').click()
        page.wait_for_function('document.querySelectorAll("#section-rows tr").length===12')
        assert not errors,errors
        browser.close()
    print('OK: twelve monthly profiles/table, 140 W atlas round trip, pending-width inventory link, source/method access and 320 px reflow')


if __name__=='__main__':main()
