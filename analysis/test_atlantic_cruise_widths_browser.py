"""Verify all new spans through checked WASM sources, cards and query UI."""
import json
import os
from playwright.sync_api import sync_playwright, expect
from test_rust_query_browser import ROOT, native, browser_query, BASE


def main():
    document = json.loads((ROOT / 'research/atlantic-cruise-section-width-extraction.json').read_bytes())
    owners = sorted({r['current_id'] for r in document['measurements']})
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page = browser.new_page(viewport={'width': 1100, 'height': 900})
        errors = []; page.on('pageerror', lambda e: errors.append(str(e)))
        page.route('**/research/*.json', lambda route: route.fulfill(status=503, body='Direct source reads disabled'))
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=brazil')
        expect(page.locator('#cruise-span-panel')).to_be_visible(timeout=90000)
        for owner in owners:
            page.locator('#season-current').select_option(owner)
            expected = [r for r in document['measurements'] if r['current_id'] == owner]
            reconciled = [r for r in expected if r['hydrographic_section_context'].get('nominal_latitude_reconciliation')]
            if reconciled:
                expect(page.locator('#cruise-span-panel')).to_contain_text('Table 1 prints 19°S')
                assert page.get_by_role('link', name='Cruise archive verifying the 2018 section label').get_attribute('href') == 'https://cchdo.ucsd.edu/cruise/740H20180228'
            bars = page.locator('.cruise-span-chart rect')
            expect(bars).to_have_count(len(expected))
            assert bars.evaluate_all('(nodes)=>nodes.map(n=>Number(n.dataset.valueKm))') == [r['approximate_width_km'] for r in expected]
            assert page.locator('.cruise-span-table tbody tr').count() == len(expected)
            assert page.locator('#season-play').is_disabled()
            assert page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
            assert page.locator('#season-section-locator').is_hidden()
            for index, row in enumerate(expected):
                context = row['hydrographic_section_context']
                cell = page.locator(f'.cruise-span-table tr[data-measurement-id="{row["id"]}"]')
                assert context['cruise_id'] in cell.inner_text()
                assert context['cruise_sampling_window']['start'] in cell.inner_text()
                assert context['cruise_sampling_window']['end'] in cell.inner_text()
                address = cell.locator('a').get_attribute('href')
                assert 'phase=' + row['id'] in address
                if index == 0:
                    cell.locator('a').click()
                else:
                    page.locator('#season-phase').select_option(str(index))
                expect(page.locator('#season-value')).to_contain_text(f'about {row["approximate_width_km"]} km')
                assert page.evaluate('new URL(location.href).searchParams.get("phase")') == row['id']
        page.set_viewport_size({'width': 320, 'height': 800})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        scroll = page.locator('.cruise-span-scroll'); scroll.focus(); page.keyboard.press('ArrowRight')
        page.wait_for_function('document.querySelector(".cruise-span-scroll").scrollLeft>0')
        page.screenshot(path=str(ROOT / '.pytest_cache/atlantic-cruise-widths-mobile.png'), full_page=True)
        page.locator('#season-current').select_option('acc')
        assert page.locator('#cruise-span-panel').is_hidden()
        assert page.locator('#cruise-span-panel').inner_text() == ''
        page.goto(BASE)
        page.wait_for_function('window.oswLastQueryResult', timeout=90000)
        query = {'collection': 'widths', 'filters': [{'field': 'phase_kind', 'op': 'eq', 'value': 'inverse_hydrographic_section_span'}], 'sort': {'field': 'id'}, 'limit': 100}
        result = browser_query(page, query)
        assert result == native(query)
        assert result['total'] == 32
        assert {r['id'] for r in result['rows']} == {r['id'] for r in document['measurements']}
        for row in result['rows']:
            expected = next(r for r in document['measurements'] if r['id'] == row['id'])
            assert {k:v for k,v in row.items() if k not in ('extraction_file', 'extraction_sha256')} == expected
        assert not errors, errors
        browser.close()
    print('PASS: all 32 cruise spans / 9 currents, source dates and layers, independent bars, direct record links, mobile keyboard scroll, hidden unsupported edges/playback, native/WASM query parity')


if __name__ == '__main__': main()
