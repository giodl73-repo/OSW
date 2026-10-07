"""Agulhas mean-section source support survives cards, sharing and Rust queries."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from test_rust_query_browser import native,browser_query
ROOT=Path(__file__).resolve().parents[1]
ID='agulhas-act-eulerian-mean-section-width'

def main():
    query={'collection':'widths','filters':[{'field':'id','op':'eq','value':ID}]}
    expected=native(query);assert expected['ok'] and expected['total']==1
    row=expected['rows'][0];assert row['approximate_width_km']==219 and row['width_range_km'] is None
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER']);page=browser.new_page(viewport={'width':860,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=agulhas&phase='+ID)
        expect(page.locator('#season-title')).to_have_text('Eulerian mean section span')
        expect(page.locator('#season-value')).to_contain_text('219 km')
        expect(page.locator('#season-definition')).to_contain_text('no fixed width measurement layer')
        expect(page.locator('#season-definition')).to_contain_text('time-mean zero-velocity isotach')
        assert page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
        expect(page.locator('#season-section-locator')).to_be_hidden();expect(page.locator('#season-play')).to_be_disabled()
        expect(page.locator('#season-range')).to_contain_text('seasonal width range and uncertainty remain unknown')
        share=page.locator('#season-share').get_attribute('href');page.goto(share)
        expect(page.locator('#season-title')).to_have_text('Eulerian mean section span')
        page.locator('#season-atlas').click()
        record=page.locator('.atlas-width-record[data-measurement-id="'+ID+'"]');record.locator('summary').click()
        expect(record).to_contain_text('219 km');expect(record).to_contain_text('HTTP 403')
        expect(record).to_contain_text('April 2010-February 2013')
        record.screenshot(path=str(ROOT/'figures/agulhas-mean-section-width-review.png'))
        page.set_viewport_size({'width':320,'height':800});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        page.goto('http://127.0.0.1:8788/almanac/query.html');page.wait_for_function('window.oswLastQueryResult',timeout=60000)
        assert browser_query(page,query)==expected
        page.locator('#query-rows button').first.click()
        expect(page.locator('#query-detail')).to_contain_text('coast_to_author_reported_mean_zero_isotach')
        assert not errors,errors;browser.close()
    print('PASS: Agulhas source scalar, mean boundary/period, no fabricated annual range/layer/edges, atlas cards/share/mobile and native/WASM')
if __name__=='__main__':main()
