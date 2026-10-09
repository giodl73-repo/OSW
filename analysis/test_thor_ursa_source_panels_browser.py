"""Original event-panel navigation, source inspection and native/WASM guards."""
import json,os,tempfile,subprocess
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright,expect
from test_thor_ursa_source_panels import ROOT,CLI,PATH,document,fixtures
from antarctic_slope_guard_fixtures import wasm_rejections
BASE='http://127.0.0.1:8788/almanac/'

def main():
    atlas=json.loads(subprocess.check_output([str(CLI),str(ROOT/'almanac/query-data.json'),'--atlas'],encoding='utf8'))
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as tmp,sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':320,'height':900});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        for event in document()['events']:
            owner=event['entity_id']
            page.goto(BASE+'reference-routes.html?atlas-feature='+quote(owner)+'#route-atlas')
            panel=page.locator('.eddy-source-panels');panel.wait_for(state='visible',timeout=90000)
            assert page.evaluate('oswAtlasSnapshot')==atlas
            select=panel.locator('select');assert select.locator('option').count()==25
            for row in event['panels']:
                select.select_option(row['id']);expect(panel.locator('[role=status]')).to_contain_text(row['observation_date'])
                assert panel.locator('svg').get_attribute('viewBox')==' '.join(map(str,row['crop_pixels_xywh']))
            assert panel.get_by_role('button',name='Next date',exact=True).is_disabled()
            panel.get_by_role('button',name='Previous date',exact=True).focus();page.keyboard.press('Enter')
            assert select.input_value()==event['panels'][-2]['id']
            select.select_option(event['panels'][13]['id'])
            panel.locator('summary').click()
            assert panel.locator('img').evaluate('(e)=>e.complete&&e.naturalWidth===2008')
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            panel.screenshot(path=str(ROOT/f'.pytest_cache/{event["name"].lower()}-source-panels-mobile.png'))
            panel.get_by_role('link',name='Inspect this panel’s source row',exact=True).click()
            page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
            assert event['panels'][13]['observation_date'] in page.locator('#source-query-results').inner_text()
            page.goto(BASE+'object.html?id='+quote(owner));panel=page.locator('.eddy-source-panels');panel.wait_for(state='visible',timeout=90000)
            assert page.evaluate('oswObjectView.source_panel_scene')==atlas['eddy_source_panel_scenes'][owner]
            assert panel.locator('select option').count()==25
            assert 'physical unit remains unresolved' in panel.inner_text()
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        results=wasm_rejections(page,fixtures(Path(tmp)))
        assert all(not r['ok'] and 'Thor/Ursa panels' in r['error'] for r in results),results
        assert not errors,errors;browser.close()
    print('PASS: 50 original source panels, atlas/object Rust parity, source inspection, keyboard/mobile, two credited original figures and nine native/WASM scientific guards')

if __name__=='__main__':main()
