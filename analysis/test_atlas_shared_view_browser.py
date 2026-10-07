"""Shared atlas URLs preserve bounded display framing and selected evidence."""
import os
from urllib.parse import parse_qs,urlparse
from playwright.sync_api import sync_playwright

BASE='http://127.0.0.1:8788/almanac/reference-routes.html'


def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'),headless=True)
        page=browser.new_page(viewport={'width':1200,'height':950});page.emulate_media(reduced_motion='reduce')
        errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
        def ready():page.wait_for_function('document.querySelectorAll(".atlas-directory-item").length===240')
        def view():return list(map(float,page.locator('#route-atlas-map').get_attribute('viewBox').split()))
        def same(expected):assert all(abs(a-b)<.000002 for a,b in zip(expected,view())),(expected,view())
        page.goto(BASE+'#route-atlas',wait_until='networkidle');ready()
        page.locator('#route-atlas-select').select_option('current:agulhas')
        page.locator('#route-atlas-in').click();page.locator('#route-atlas-map').focus();page.keyboard.press('ArrowRight')
        expected=view();share=page.locator('[data-atlas-share]').get_attribute('href')
        assert parse_qs(urlparse(share).query)['atlas-feature']==['current:agulhas']
        same(list(map(float,parse_qs(urlparse(share).query)['atlas-view'][0].split(','))))
        page.goto(share,wait_until='networkidle');ready();same(expected)
        assert page.locator('#route-atlas-preview h3').inner_text()=='Agulhas Current'
        page.reload(wait_until='networkidle');ready();same(expected)
        # New selection gets its own fit, not the previous current's framing.
        page.locator('#route-atlas-select').select_option('current:ligurian');assert view()!=expected
        page.locator('#route-atlas-world').click();assert 'atlas-view=' not in page.url
        assert view()==[60,90,1480,740]
        # An unselected global map also preserves a manually explored region.
        page.locator('#route-atlas-in').click();expected=view();url=page.url
        page.goto(url,wait_until='networkidle');ready();same(expected)
        assert page.locator('#route-atlas-preview').is_hidden()
        # Late section data must not overwrite a restored display frame.
        scoped=BASE+'?atlas-feature=current%3Apacific-north-equatorial-countercurrent&atlas-section=oscar-necc-140w-2013-05&atlas-view=180,250,320,160#route-atlas'
        page.goto(scoped,wait_until='networkidle');ready()
        page.wait_for_function('document.querySelector(".atlas-monthly-chart")!==null')
        same([180,250,320,160]);assert 'atlas-section=oscar-necc-140w-2013-05' in page.url
        # Corrupt frames fall back to the current's ordinary fit.
        for bad in ['NaN,90,20,10','60,90,0,0','60,90,20,20','59,90,20,10','60,90,1481,740.5','60,829,20,10',',90,20,10','60,90,20,10,1']:
            page.goto(BASE+'?atlas-feature=current%3Aagulhas&atlas-view='+bad+'#route-atlas',wait_until='networkidle');ready()
            assert view()[2]>20
            assert parse_qs(urlparse(page.url).query)['atlas-view'][0]!=bad
        assert not errors,errors;browser.close()
    print('OK: shared zoom/pan, reload, new selection, reset, unselected view, asynchronous monthly section and invalid frame fallback')


if __name__=='__main__':main()
