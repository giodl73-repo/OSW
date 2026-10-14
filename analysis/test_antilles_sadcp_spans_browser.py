"""Layer profiles: native/WASM parity, source navigation and missing depths."""
import json
import os
from urllib.parse import quote
from playwright.sync_api import sync_playwright
from test_rust_query_browser import native, browser_query, BASE

def main():
    query={'collection':'observed_section_spans','filters':[{'field':'depth_m','op':'eq','value':95}],'limit':20}
    expected=native(query)
    assert expected['total']==2
    assert [r['half_peak_span_km'] for r in expected['rows']]==[50,80]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1280,'height':1000})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(BASE+'?q='+quote(json.dumps(query)))
        page.wait_for_function('window.oswLastQueryResult',timeout=90000)
        assert page.evaluate('window.oswLastQueryResult')==expected
        assert page.locator('.observed-section-span svg').count()==2
        assert '40–130 km' in page.locator('#query-chart-panels').inner_text()
        assert 'incomplete' in page.locator('.observed-section-span').nth(1).inner_text()
        page.locator('.observed-section-span button').first.click()
        page.locator('.observed-section-span a').first.click()
        page.wait_for_function('window.oswSourceQueryResult',timeout=90000)
        assert page.evaluate('window.oswSourceQueryResult.document')=='research/antilles-ab0505-sadcp-layer-span-diagnostics.json'
        page.goto(BASE+'?q='+quote(json.dumps(query)))
        page.wait_for_function('window.oswLastQueryResult',timeout=90000)
        empty={'collection':'observed_section_spans','filters':[{'field':'depth_m','op':'eq','value':895}],'limit':20}
        actual=browser_query(page,empty)
        assert actual==native(empty)
        assert all(r['half_peak_span_km'] is None for r in actual['rows'])
        assert 'Paired span unresolved; not zero' in page.locator('#query-chart-panels').inner_text()
        page.set_viewport_size({'width':320,'height':800})
        assert page.locator('.observed-section-span svg').first.bounding_box()['width']<=320
        assert not errors,errors
        browser.close()
    print('Shipboard profiles: native/WASM, source navigation, missing depths and mobile passed')

if __name__=='__main__':main()
