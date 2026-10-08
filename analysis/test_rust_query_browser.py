"""Native/WASM parity, scientific joins, query navigation and failure handling."""
import json
import os
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
BASE = 'http://127.0.0.1:8788/almanac/query.html'
CLI = Path(os.environ.get('OSW_QUERY_CLI', str(ROOT / 'rust/osw-query/target/debug' /
                                            ('osw-query-cli.exe' if os.name == 'nt' else 'osw-query-cli'))))


def native(query):
    result = subprocess.run([str(CLI),
                             str(ROOT/'almanac/query-data.json'), '-'],
                            input=json.dumps(query), capture_output=True, text=True, encoding='utf-8')
    return json.loads(result.stdout)


def browser_query(page, query):
    page.locator('#query-advanced').evaluate('(el)=>el.open=true')
    page.locator('#query-json').fill(json.dumps(query))
    page.evaluate('window.oswLastQueryResult=null')
    page.locator('#query-run-json').click()
    page.wait_for_function('window.oswLastQueryResult || document.querySelector("#query-status").classList.contains("error")')
    return page.evaluate('window.oswLastQueryResult')


def main():
    queries = [
        {'collection':'objects','record_type':'named_current','evidence':'scoped_width','sort':{'field':'label'},'limit':100},
        {'collection':'objects','record_type':'named_current','evidence':'reported_length','sort':{'field':'published_length_km','direction':'desc'}},
        {'collection':'objects','record_type':'named_current','state_code':'KURO'},
        {'collection':'objects','record_type':'named_eddy','evidence':'geometry'},
        {'collection':'objects','sort':{'field':'published_length_km','direction':'desc'},'offset':9,'limit':5},
        {'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'kuroshio'}]},
        {'collection':'claims','text':'kuroshio','limit':12},
        {'collection':'state_links','filters':[{'field':'kind','op':'eq','value':'shared_regional_gateway'}],'limit':10},
        {'collection':'objects','spatial':{'state_code':'NADR','predicate':'intersects'},'limit':50},
        {'collection':'objects','spatial':{'state_code':'NADR','predicate':'within'},'limit':50},
        {'collection':'objects','spatial':{'state_code':'CAMR','predicate':'gateway'},'limit':50},
    ]
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page = browser.new_page(viewport={'width':1280,'height':1000})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(BASE)
        page.wait_for_function('window.oswLastQueryResult', timeout=60000)
        assert page.evaluate('window.oswLastQueryResult.total') == 100
        assert page.evaluate('window.oswLastQueryResult.map_scene.mapped_objects') == 100
        assert page.locator('#query-map-features').evaluate('(el)=>new Set([...el.children].map(n=>n.dataset.entity)).size') == 100
        assert page.locator('#query-rows tr').count() == 50
        page.locator('#query-map-in').click()
        assert float(page.locator('#query-map').get_attribute('viewBox').split()[2]) < 360
        page.locator('#query-map-world').click()
        assert page.locator('#query-map').get_attribute('viewBox') == '0 0 360 180'
        all_objects = browser_query(page, {'collection':'objects','limit':50})
        assert all_objects['total'] == 240
        assert all_objects['map_scene']['matching_objects'] == 240
        assert all_objects['map_scene']['mapped_objects'] == 240
        mark = page.locator('#query-map-features [data-entity="current:kuroshio"]').first
        mark.focus()
        expect(page.locator('#query-map-hover')).to_contain_text('Kuroshio Current')
        mark.press('Enter')
        expect(page.locator('#query-detail')).to_contain_text('Scoped width records (3)')
        assert float(page.locator('#query-map').get_attribute('viewBox').split()[2]) < 360
        page.locator('#query-map-world').click()
        for query in queries:
            actual = browser_query(page, query)
            expected = native(query)
            assert actual == expected, (query, actual, expected)
        width_currents = native(queries[0])
        assert width_currents['total'] == 39
        assert {'current:' + owner for owner in ['falkland', 'brazil', 'benguela', 'canary',
                'gulf-stream', 'north-atlantic', 'irminger', 'east-greenland', 'west-greenland', 'black-sea-rim']}.issubset(
                    {row['id'] for row in width_currents['rows']})
        lengths = native(queries[1])
        assert lengths['total'] == 11
        assert lengths['rows'][0]['published_length_km'] == 25000
        assert native(queries[5])['total'] == 3
        browser_query(page, queries[8])
        assert page.locator('#query-state-mode').input_value() == 'intersects'
        assert page.locator('#query-state').input_value() == 'NADR'
        assert page.locator('#query-map-state path').count() == 1
        assert page.locator('#query-map-features .context-only').count()>0
        assert page.locator('#query-map-features [aria-label*="matches selected state"]').count()>0
        page.get_by_role('button',name='Portugal Current',exact=True).click()
        expect(page.locator('#query-detail')).to_contain_text('Computed state relations')
        expect(page.locator('#query-detail')).to_contain_text('portugal-reference-path-candidate')
        page.locator('#query-map-section').screenshot(path=str(ROOT/'figures/rust-query-spatial-map-review.png'))
        page.locator('#query-state-mode').select_option('within')
        page.locator('#query-run').click()
        page.wait_for_function('window.oswLastQueryResult.total===2')
        missing = browser_query(page, {'collection':'objects','filters':[{'field':'published_length_km','op':'exists','value':False}],'limit':500})
        assert missing['total'] == 229
        assert all(r['published_length_km'] is None for r in missing['rows'])
        # Canonical source fields and scoped values remain available together.
        browser_query(page, {'collection':'objects','text':'current:kuroshio','record_type':'named_current','limit':50})
        page.get_by_role('button', name='Kuroshio Current', exact=True).click()
        expect(page.locator('#query-detail')).to_contain_text('Scoped width records (3)')
        expect(page.locator('#query-detail')).to_contain_text('0.1')
        expect(page.locator('#query-detail')).to_contain_text('218')
        expect(page.locator('#query-detail')).to_contain_text('207')
        expect(page.locator('#query-detail')).to_contain_text('210')
        assert 'atlas-feature=current%3Akuroshio' in page.locator('#query-detail a').filter(has_text='Open atlas card').first.get_attribute('href')
        assert page.locator('#query-detail a').filter(has_text='Published source').count() == 3
        # Selected queries restore from an independent document load.
        browser_query(page, queries[1])
        shared = page.locator('#query-share').get_attribute('href')
        page.goto('about:blank')
        page.goto(shared)
        page.wait_for_function('window.oswLastQueryResult', timeout=60000)
        assert page.evaluate('window.oswLastQueryResult') == lengths
        with page.expect_download() as download:
            page.locator('#query-export').click()
        exported = json.loads(Path(download.value.path()).read_text(encoding='utf-8'))
        assert exported['result'] == lengths and len(exported['bundle_sha256']) == 64
        # Unknown fields cannot silently change the intended query.
        invalid = {'collection':'objects','filters':[{'field':'fake','op':'eq','value':0}]}
        assert not native(invalid)['ok']
        assert browser_query(page, invalid) is None
        assert 'Unknown field' in page.locator('#query-status').inner_text()
        assert page.locator('#query-export').is_disabled()
        # Recovery, pagination and narrow layout.
        browser_query(page, {'collection':'objects','record_type':'named_current','limit':50,'offset':0})
        page.locator('#query-next').click()
        page.wait_for_function('window.oswLastQueryResult.offset===50')
        assert page.locator('#query-rows tr').count() == 50
        page.locator('#query-previous').click()
        page.wait_for_function('window.oswLastQueryResult.offset===0')
        page.locator('#query-advanced').evaluate('(el)=>el.open=false')
        page.evaluate('scrollTo(0,0)')
        page.screenshot(path=str(ROOT/'figures/rust-query-workspace-review.png'))
        page.locator('#query-map-section').screenshot(path=str(ROOT/'figures/rust-query-map-review.png'))
        page.set_viewport_size({'width':320,'height':900})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.screenshot(path=str(ROOT/'figures/rust-query-workspace-mobile-review.png'))
        assert not errors, errors
        # Corrupted artifacts visibly block loading; no alternate JS engine.
        blocked = browser.new_page()
        manifest = json.loads((ROOT/'almanac/query-engine.manifest.json').read_text(encoding='utf-8'))
        manifest['sha256']['almanac/query-data.json'] = '0'*64
        blocked.route('**/query-engine.manifest.json', lambda r:r.fulfill(json=manifest))
        blocked.goto(BASE)
        expect(blocked.locator('#query-status')).to_contain_text('Changed almanac/query-data.json',timeout=60000)
        assert blocked.locator('#query-controls').get_attribute('disabled') is not None
        assert blocked.locator('#query-run').is_disabled()
        assert blocked.locator('#query-rows tr').count() == 0
        browser.close()
    print('PASS: native/WASM parity, scoped joins, sharing/export, invalid queries, pagination, mobile and failed integrity load')


if __name__ == '__main__':
    main()
