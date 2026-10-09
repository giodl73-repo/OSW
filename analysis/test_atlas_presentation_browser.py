"""Map-first presentation retains navigation, shared views and small-screen access."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:8788/almanac/reference-routes.html'

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'], headless=True)
        page = browser.new_page(viewport={'width':1400,'height':1000})
        page.emulate_media(reduced_motion='reduce')
        errors=[]
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(BASE+'?atlas-layout=map#route-atlas', wait_until='networkidle')
        page.wait_for_function('document.querySelectorAll(".atlas-directory-item").length===240')
        assert page.locator('body').evaluate('(el)=>el.classList.contains("atlas-presentation")')
        assert page.locator('#atlas-directory').is_hidden()
        assert page.locator('#comparison-title').is_hidden()
        page.locator('#route-atlas-select').select_option('current:agulhas')
        assert page.locator('#route-atlas-preview > h3').inner_text()=='Agulhas Current'
        page.locator('#route-atlas-in').click()
        view=page.locator('#route-atlas-map').get_attribute('viewBox')
        share=page.locator('[data-atlas-share]').get_attribute('href')
        assert 'atlas-layout=map' in share
        page.goto(share, wait_until='networkidle')
        page.wait_for_function('document.querySelectorAll(".atlas-directory-item").length===240')
        assert page.locator('#route-atlas-map').get_attribute('viewBox')==view
        page.locator('#atlas-index-toggle').click()
        assert page.locator('#atlas-directory input').evaluate('(el)=>el===document.activeElement')
        assert page.locator('.atlas-directory-item').count()==240
        page.locator('#atlas-index-toggle').click()
        assert page.locator('#atlas-directory').is_hidden()
        page.locator('#route-atlas-card-link').click()
        assert page.locator('#comparison-title').is_visible()
        assert 'atlas-layout=' not in page.url
        page.locator('#atlas-presentation-toggle').click()
        page.locator('#route-atlas-world').click()
        assert 'atlas-layout=map' in page.url
        assert page.locator('#route-atlas-preview').is_hidden()
        page.locator('#atlas-presentation-toggle').click()
        assert page.locator('#comparison-title').is_visible()
        assert page.locator('#atlas-directory').is_visible()
        assert 'atlas-layout=' not in page.url
        page.set_viewport_size({'width':320,'height':850})
        page.locator('#atlas-presentation-toggle').click()
        page.locator('#route-atlas-select').select_option('current:agulhas')
        assert page.locator('#route-atlas-preview').is_visible()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'), 'Mobile overflow'
        page.set_viewport_size({'width':1400,'height':1000})
        page.locator('#route-atlas-title').scroll_into_view_if_needed()
        page.screenshot(path=str(Path('figures/atlas-map-first-review.png')),full_page=True)
        assert not errors, errors
        browser.close()
    print('OK: map-first global/card navigation, 240-entry index, shared framing, full almanac and mobile layout')

if __name__=='__main__':main()
