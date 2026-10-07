"""Actual index uses checked documents and Rust projection for every sample date."""
import json
import mimetypes
import os
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, expect
from test_rust_query_browser import ROOT

BASE = 'http://127.0.0.1:8788/almanac/index.html?state=CAMR'


def main():
    manifest = json.loads((ROOT/'research/noaa-munster-eddy-seasonal-manifest-2021-2023.json').read_bytes())
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page = browser.new_page(viewport={'width':1440,'height':1000})
        requests, errors = [], []
        page.on('request', lambda r: requests.append(r.url))
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(BASE)
        page.wait_for_function("window.oswIndexPageReady",timeout=90000)
        assert page.locator('#current-rows tr').count() == 100
        assert page.evaluate('oswIndexMetadata.source_count') == 65
        assert page.locator('#eddy-date-select option').count() == 12
        assert page.locator('#state-select option').count() == 57
        assert page.locator('#state-select').input_value() == 'CAMR'
        page.locator('#current-search').fill('Agulhas')
        expect(page.locator('#current-rows')).to_contain_text('Agulhas')
        page.wait_for_function("oswIndexCurrentView && oswIndexCurrentView.rows.every(r=>r.record.name.includes('Agulhas'))")
        page.locator('#current-search').fill('')
        expect(page.locator('#current-rows tr')).to_have_count(100)
        page.locator('#all-eddy-search').fill('Kraken')
        expect(page.locator('#all-eddy-results')).to_contain_text('Kraken')
        page.locator('#show-state-eddies').check()
        for snapshot in manifest['snapshots']:
            date = snapshot['date']
            page.locator('#eddy-date-select').select_option(date)
            page.wait_for_function("!document.querySelector('#eddy-date-select').disabled",timeout=90000)
            assert page.locator('#eddy-date-select').input_value() == date
            data = json.loads((ROOT/'almanac'/snapshot['path']).read_bytes())
            relation = data['states']['CAMR']
            lookup = {r['id']:r for r in data['entries']}
            points = [lookup[i]['center'] for kind in ['contained','intersected'] for i in relation[kind]
                      if all(v is not None for v in lookup[i]['center'])]
            marks = page.locator('#detected-eddy-markers circle').evaluate_all(
                '(nodes)=>nodes.map(n=>[Number(n.getAttribute("cx")),Number(n.getAttribute("cy"))])')
            assert len(marks) == len(points), date
            for actual, (lon,lat) in zip(marks, points):
                assert abs(actual[0]-(60+(lon+180)/360*1480)) < .000001
                assert abs(actual[1]-(90+(90-lat)/180*740)) < .000001
        page.locator('#state-select').select_option('GFST')
        page.wait_for_function("oswIndexStateMembershipView?.state_code==='GFST'",timeout=90000)
        page.wait_for_function("document.querySelector('.state-dated-samples summary')?.textContent.includes('in GFST') && !document.querySelector('.state-dated-samples summary').textContent.includes('loading')",timeout=90000)
        assert page.locator('.state-dated-samples li[data-sample-date]').count() > 0
        assert not any('/research/' in url or 'query-data.json' in url or '/release/' in url and url.endswith('.json')
                       for url in requests), requests
        assert not errors, errors
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.close()
        failed = browser.new_page()
        failed.route('**/index-data.json.gz',lambda r:r.fulfill(status=503,body='Unavailable'))
        failed.goto(BASE)
        expect(failed.locator('#current-count')).to_have_text('Data unavailable',timeout=90000)
        assert failed.locator('#current-rows tr').count() == 0
        assert failed.locator('#state-select option').count() == 1
        assert failed.locator('#detected-eddy-markers circle').count() == 0
        failed.close()
        # GitHub Pages/project-root prefixes must resolve the same catalog keys.
        prefixed = browser.new_page()
        def serve_project(route):
            path = urlparse(route.request.url).path.removeprefix('/OSW/')
            file = ROOT/path
            route.fulfill(body=file.read_bytes(), content_type=mimetypes.guess_type(str(file))[0] or 'application/octet-stream')
        prefixed.route('**/OSW/**',serve_project)
        prefixed.goto(BASE.replace('/almanac/','/OSW/almanac/'))
        prefixed.wait_for_function("window.oswIndexPageReady",timeout=90000)
        assert prefixed.locator('#current-rows tr').count() == 100
        assert prefixed.evaluate('oswIndexMetadata.source_count') == 65
        prefixed.close()
        browser.close()
    print('PASS: checked index page, 100 currents, all 12 dated NOAA map inventories, source projection, saved state, diagnostic links, mobile and unavailable corpus')


if __name__ == '__main__':
    main()
