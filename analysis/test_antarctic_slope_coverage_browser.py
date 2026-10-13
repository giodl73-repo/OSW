"""Observed velocity lights, accurate dates and direct dashboard-to-chart access."""
import json
import tempfile
from pathlib import Path
from antarctic_slope_guard_fixtures import prepare,wasm_rejections
import os
from playwright.sync_api import sync_playwright,expect
from test_motion_dashboard_browser import settle,native_selection
from test_rust_query_browser import ROOT


def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':320,'height':900});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/dashboard.html')
        page.wait_for_function('window.oswDashboardSnapshot',timeout=90000);settle(page)
        page.locator('#dashboard-metric').select_option('observed_velocity');settle(page)
        selection=page.evaluate('oswDashboardSelection');assert selection['result']==native_selection(selection['request'])
        assert selection['result']['covered_count']==1
        assert next(s for s in selection['result']['beck_scene']['stations'] if s['id']=='current:antarctic-slope')['covered'] is True
        page.locator('#dashboard-card-view').click()
        card=page.locator('[data-id="current:antarctic-slope"]');assert 'lit' in card.get_attribute('class')
        expect(card).to_contain_text('Observed velocity summaries: 61 records')
        card.locator('details').evaluate('(e)=>e.open=true')
        expect(card).to_contain_text('Latest dated evidence: 2021-02-13')
        expect(card).to_contain_text('current width unresolved')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        card.screenshot(path=str(ROOT/'.pytest_cache/antarctic-slope-dashboard-mobile.png'))
        card.get_by_role('link',name='M6 observed velocity · 49 monthly means / 12 seasonal composites').click()
        page.wait_for_function('window.oswLastQueryResult?.total===61',timeout=90000)
        assert page.locator('#chart-title').inner_text()=='Observed current velocity'
        with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache',prefix='m6-metadata-') as tmp:
            targets=prepare(Path(tmp),'metadata')
            results=wasm_rejections(page,targets)
            assert all(r['ok'] is False and 'M6 observed' in r['error'] for r in results),results
        assert not errors,errors;browser.close()
    print('PASS: observed velocity lights, native/WASM selection, dates, mobile, chart navigation and three coherent metadata rejections')


if __name__=='__main__':main()
