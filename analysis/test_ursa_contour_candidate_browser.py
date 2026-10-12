"""The checked native scene must render and remain inspectable in WASM."""
import os,tempfile
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright,expect
from test_ursa_contour_candidate import ROOT,OWNER,ID,fixtures
from antarctic_slope_guard_fixtures import wasm_rejections
BASE='http://127.0.0.1:8788/almanac/'

def main():
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as tmp,sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':320,'height':900});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(BASE+'reference-routes.html?atlas-feature='+quote(OWNER)+'#route-atlas')
        overlay=page.locator('[data-source-overlay=ursa]');overlay.wait_for(state='visible',timeout=90000)
        scene=page.evaluate('oswAtlasSnapshot.footprint_views["'+OWNER+'"].plot_scene')
        assert overlay.locator('path').get_attribute('d')==scene['source_panel_overlay']['polygon_d']
        assert overlay.locator('image').evaluate("async e=>{const i=new Image();i.src=e.getAttribute('href');await i.decode();return i.naturalWidth===2008}")
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        overlay.screenshot(path=str(ROOT/'.pytest_cache/ursa-contour-mobile.png'))
        page.get_by_role('link',name='Inspect calibration and rejected cases').focus();page.keyboard.press('Enter')
        page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
        expect(page.locator('#source-query-results')).to_contain_text('Ring Self-intersection')
        assert page.evaluate('oswSourceQueryResult.rows.map(r=>r.record.status)')==['rejected_non_simple_pixel_ring']*2
        page.goto(BASE+'object.html?id='+quote(OWNER));page.locator('[data-source-overlay=ursa]').wait_for(state='visible',timeout=90000)
        assert page.evaluate('oswObjectView.footprint_plots["'+ID+'"]')==scene
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        results=wasm_rejections(page,fixtures(Path(tmp)))
        assert all(not r['ok'] and ('Ursa contour' in r['error'] or 'Thor/Ursa panels: changed original figure dependency' in r['error']) for r in results),results
        assert not errors,errors;browser.close()
    print('PASS: source overlay, source inspection, native atlas/object parity, mobile/keyboard and 11 WASM scientific mutation guards')

if __name__=='__main__':main()
