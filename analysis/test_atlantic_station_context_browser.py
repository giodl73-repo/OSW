"""Exercise every station map, explicit gaps, checked source joins and mobile UI."""
import gzip
import json
import os
from pathlib import Path
import subprocess
import tempfile
from urllib.parse import parse_qs, urlparse
from playwright.sync_api import sync_playwright, expect
from test_rust_query_browser import ROOT, CLI


def main():
    audit = json.loads((ROOT / 'research/atlantic-cruise-station-context.json').read_bytes())
    groups = {}
    for row in audit['measurement_contexts']:
        groups.setdefault(row['current_id'], []).append(row)
    with tempfile.TemporaryDirectory(dir=ROOT / '.pytest_cache') as directory:
        packet = Path(directory) / 'index.json'
        packet.write_bytes(gzip.decompress((ROOT / 'almanac/index-data.json.gz').read_bytes()))
        source_request = {'document': 'research/atlantic-cruise-station-context.json', 'pointer': '/measurement_contexts', 'limit': 100}
        response = subprocess.run([str(CLI), '--index', str(packet), '-'], input=json.dumps(source_request), text=True, encoding='utf-8', capture_output=True, check=True)
        native = json.loads(response.stdout)
        assert native['total'] == 30
        assert [r['record'] for r in native['rows']] == audit['measurement_contexts']
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
            page = browser.new_page(viewport={'width': 1100, 'height': 900})
            errors = []; page.on('pageerror', lambda error: errors.append(str(error)))
            page.route('**/research/*.json', lambda route: route.fulfill(status=503, body='Direct source reads disabled'))
            page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=brazil')
            expect(page.locator('#cruise-span-panel')).to_be_visible(timeout=90000)
            for owner, contexts in groups.items():
                page.locator('#season-current').select_option(owner)
                panel = page.locator('.cruise-station-context')
                panel.locator('summary').click()
                for context in contexts:
                    panel.locator('select').select_option(context['measurement_id'])
                    page.wait_for_function('(id)=>window.oswAtlanticStationContext?.measurement_id===id', arg=context['measurement_id'], timeout=90000)
                    assert page.evaluate('window.oswAtlanticStationContext') == context
                    expect(panel.locator('circle')).to_have_count(context['point_count'])
                    if context['points']:
                        expect(panel.locator('[role=status]')).to_contain_text('no current boundary or width')
                        assert panel.locator('path').count() == 0
                        assert panel.locator('circle').evaluate_all('(nodes)=>nodes.map(n=>Number(n.dataset.sourceLine))') == [r['source_line'] for r in context['points']]
                    else:
                        expect(panel.locator('[role=status]')).to_contain_text('Map unavailable')
                        if context['status'] == 'source_date_conflict':
                            expect(panel.locator('[role=status]')).to_contain_text('2005 dates for this 2007 cruise')
                    address = panel.get_by_role('link', name='Inspect and download exact station records').get_attribute('href')
                    request = json.loads(parse_qs(urlparse(address).query)['source-q'][0])
                    assert request == {**source_request, 'limit': 25, 'filters': [{'field': 'record.measurement_id', 'op': 'eq', 'value': context['measurement_id']}]}
            page.set_viewport_size({'width': 320, 'height': 800})
            panel.get_by_text('Station coordinates and source lines', exact=True).click()
            expect(panel.locator('tbody tr')).to_have_count(context['point_count'])
            scroll = panel.locator('.cruise-span-scroll'); scroll.focus(); page.keyboard.press('ArrowRight')
            page.wait_for_function('document.querySelector(".cruise-station-context .cruise-span-scroll").scrollLeft>0')
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.screenshot(path=str(ROOT / '.pytest_cache/atlantic-station-context-mobile.png'), full_page=True)
            inspect = browser.new_page()
            inspect.goto('http://127.0.0.1:8788/almanac/' + address)
            inspect.wait_for_function('window.oswSourceQueryResult', timeout=90000)
            result = inspect.evaluate('window.oswSourceQueryResult')
            assert result['total'] == 1 and result['rows'][0]['record'] == context
            page.locator('#season-current').select_option('acc')
            assert page.locator('.cruise-station-context').count() == 0
            assert page.evaluate('window.oswAtlanticStationContext') is None
            assert not errors, errors
            # Failure to verify the corpus must never display unverified locations.
            bad = browser.new_page()
            bad.route('**/index-data.json.gz', lambda route: route.fulfill(status=200, body=b'changed source bytes'))
            bad.goto('http://127.0.0.1:8788/almanac/seasons.html?current=brazil')
            expect(bad.locator('.cruise-station-context')).to_be_visible(timeout=90000)
            bad.locator('.cruise-station-context summary').click()
            expect(bad.locator('.cruise-station-context [role=status]')).to_contain_text('Station context unavailable', timeout=90000)
            assert bad.locator('.cruise-station-context svg').count() == 0
            browser.close()
    print('PASS: 30 exact station-context joins, 26 Rust-projected maps, 4 explicit gaps, source-query/native parity, mobile containment, changed-source rejection')


if __name__ == '__main__': main()
