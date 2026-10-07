"""Local width statistics retain distinct ranges, support and navigation."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from test_rust_query_browser import native,browser_query
ROOT=Path(__file__).resolve().parents[1]
ID='florida-hf-radar-width-statistics-2005-2006'

def main():
    query={'collection':'widths','filters':[{'field':'id','op':'eq','value':ID}]}
    expected=native(query);assert expected['ok'] and expected['total']==1
    row=expected['rows'][0]
    assert row['approximate_width_km']==59 and row['width_range_km']==[41,76]
    assert row['width_statistics_context']['reported_statistics']['mean_confidence_level_percent'] is None
    assert row['annual_extrema_eligible'] is False and row['seasonal_playback_eligible'] is False
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'));page=browser.new_page(viewport={'width':860,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=florida&phase='+ID)
        expect(page.locator('#season-title')).to_have_text('Local surface jet width statistics')
        expect(page.locator('#season-value')).to_contain_text('59 km mean')
        expect(page.locator('#season-value')).to_contain_text('41–76 km observed range')
        expect(page.locator('#season-definition')).to_contain_text('Standard deviation 6 km')
        expect(page.locator('#season-definition')).to_contain_text('confidence allowance +/-2 km')
        expect(page.locator('#season-definition')).to_contain_text('peak in August/September')
        assert page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
        expect(page.locator('#season-section-locator')).to_be_hidden();expect(page.locator('#season-play')).to_be_disabled()
        expect(page.locator('#season-range')).to_contain_text('not per-year or seasonal extrema')
        page.goto(page.locator('#season-share').get_attribute('href'))
        expect(page.locator('#season-value')).to_contain_text('41–76 km observed range')
        page.locator('#season-atlas').click()
        record=page.locator('.atlas-width-record[data-measurement-id="'+ID+'"]');record.locator('summary').focus();record.locator('summary').press('Enter')
        expect(record.locator('summary')).to_contain_text('59 km mean (41–76 km observed)')
        expect(record).to_contain_text('50%');expect(record).to_contain_text('2005-2006')
        record.screenshot(path=str(ROOT/'figures/florida-width-statistics-review.png'))
        page.set_viewport_size({'width':320,'height':800});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        page.goto('http://127.0.0.1:8788/almanac/query.html');page.wait_for_function('window.oswLastQueryResult',timeout=60000)
        assert browser_query(page,query)==expected
        page.locator('#query-rows button').first.click()
        expect(page.locator('#query-detail')).to_contain_text('author_reported_minimum_maximum_of_filtered_width_time_series')
        assert not errors,errors;browser.close()
    print('PASS: Florida distinct mean/range/variation/confidence, source phases, share/cards/mobile and native/WASM')
if __name__=='__main__':main()
