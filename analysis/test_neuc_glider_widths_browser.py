"""Local multi-year ranges retain source ownership in actual Rust/WASM views."""
import json
import os
from urllib.parse import quote
from playwright.sync_api import sync_playwright, expect
import neuc_glider_widths as n
from browser_inventory_expectations import SCOPED_WIDTH_COUNT
from test_current_research_evidence_browser import BASE, native


def main():
    doc, _ = n.verify_inputs()
    out = n.ROOT / '.pytest_cache/neuc-glider-widths/browser'
    out.mkdir(parents=True, exist_ok=True)
    queries = [
        {'collection': 'widths', 'filters': [{'field': 'source_id', 'op': 'eq', 'value': n.SOURCE}], 'limit': 10},
        {'collection': 'widths', 'filters': [{'field': 'current_id', 'op': 'eq', 'value': n.CURRENT}], 'limit': 10},
        {'collection': 'diagnostics', 'filters': [{'field': 'id', 'op': 'eq', 'value': n.ID}], 'limit': 1},
        {'collection': 'objects', 'filters': [{'field': 'id', 'op': 'contains', 'value': 'north-equatorial-undercurrent'}], 'limit': 10},
        {'collection': 'widths', 'limit': 1},
    ]
    errors, original_requests = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page = browser.new_page(viewport={'width': 1280, 'height': 900})
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda r: original_requests.append(r.url) if r.url.lower().endswith(('.pdf', '.nc', '.zip')) else None)
        page.goto(BASE + '/almanac/query.html?q=' + quote(json.dumps(queries[0])))
        page.wait_for_function('window.oswLastQueryResult', timeout=180000)
        page.locator('#query-advanced > summary').click()
        for i, query in enumerate(queries):
            if i:
                page.locator('#query-json').fill(json.dumps(query))
                page.evaluate('window.oswLastQueryResult=null')
                page.locator('#query-run-json').click()
                page.wait_for_function('window.oswLastQueryResult', timeout=120000)
            result = page.evaluate('window.oswLastQueryResult')
            assert result == native(query)
            assert result['total'] == [2, 4, 1, 3, SCOPED_WIDTH_COUNT][i]
            if i == 0:
                assert sorted(result['rows'], key=lambda r: r['id']) == sorted(doc['width_records'], key=lambda r: r['id'])
                assert result['chart_scene']['kind'] == 'neuc_glider_width_ranges'
                panel = page.locator('.neuc-glider-width-query')
                expect(panel).to_contain_text('0–200km')
                expect(panel).to_contain_text('100–350km')
                expect(panel).to_contain_text('original file was not retained')
                expect(panel).to_contain_text('cross-study component matching remains unresolved')
                button = panel.get_by_role('button', name='Inspect this width record', exact=True).last
                button.focus(); page.keyboard.press('Enter')
                expect(page.locator('#query-detail')).to_contain_text(doc['width_records'][1]['id'])
            if i in [1, 4]:
                assert result['chart_scene']['kind'] == 'scoped_width_comparisons'
                kinds = {s['kind'] for s in result['chart_scene']['scenes']}
                assert {'neuc_glider_width_ranges', 'pacific_neuc_isopycnal_breadths'} <= kinds
                if i == 4:
                    assert {'dwbc_float_composite', 'coastal_composite_widths'} <= kinds
                expect(page.locator('.neuc-glider-width-query')).to_be_visible()
                assert page.locator('.pacific-neuc-breadths').count() == 1
            if i == 2:
                assert json.loads(result['rows'][0]['source_json']) == doc
                assert len(result['chart_scene']['mean_breadth_comparison']['records']) == 2
                page.set_viewport_size({'width': 320, 'height': 900})
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                assert 'undefined' not in page.locator('#query-chart-panels').inner_text()
                page.screenshot(path=str(out / 'query-320px.png'), full_page=True)
                page.set_viewport_size({'width': 1280, 'height': 900})
            if i == 3:
                rows = {r['id']: r for r in result['rows']}
                assert rows['current:' + n.CURRENT]['capabilities']['scoped_width'] == 4
                family = rows['current:north-equatorial-undercurrent']
                assert family['capabilities']['scoped_width'] == 0 and family['width_ids'] == []
            print('PASS actual native/WASM query', i, flush=True)
        page.goto(BASE + '/almanac/seasons.html?current=' + n.CURRENT)
        page.wait_for_function('window.oswSeasonSnapshot', timeout=180000)
        plan = page.evaluate('window.oswSeasonSnapshot.phase_plans["' + n.CURRENT + '"]')
        assert len(plan['phases']) == 4 and not plan['can_play'] and plan['eligible_indices'] == []
        for row in doc['width_records']:
            index = next(i for i, p in enumerate(plan['phases']) if p['id'] == row['id'])
            page.locator('#season-phase').select_option(str(index))
            expect(page.locator('#season-title')).to_have_text('Local multi-year jet width range')
            expect(page.locator('#season-value')).to_contain_text('–'.join(map(str, row['width_range_km'])))
            expect(page.locator('#season-play')).to_be_disabled()
            assert page.locator('#season-bar').locator('..').is_hidden()
            expect(page.locator('#regional-width-range')).to_contain_text('original file not retained')
        page.goto(BASE + '/almanac/reference-routes.html?atlas-feature=current%3A' + n.CURRENT + '#route-atlas')
        page.wait_for_function('window.oswAtlasSnapshot', timeout=180000)
        expect(page.locator('#route-atlas-preview > h3')).to_have_text('Pacific North Equatorial Undercurrent', timeout=120000)
        for path in [n.BASE, n.FILE, n.EXPORT]:
            raw = page.evaluate('p=>window.oswAtlasSnapshot.sources_json[p]', path)
            assert raw.encode('utf8') == (n.ROOT / path).read_bytes()
        links = page.locator('.route-atlas-evidence-links')
        links.locator('summary').focus(); page.keyboard.press('Enter')
        link = links.get_by_role('link', name='Compare NEUC multi-year glider width ranges', exact=True)
        expect(link).to_have_attribute('href', '../' + n.FIGURE)
        page.set_viewport_size({'width': 320, 'height': 900})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        link.focus(); page.keyboard.press('Enter')
        expect(page.locator('svg[role=img]')).to_be_visible()
        expect(page.locator('#desc')).to_contain_text('Zero is a source lower bound')
        expect(page.locator('svg[role=img]')).to_contain_text('100–350km')
        expect(page.locator('svg[role=img]')).to_contain_text('Schönau')
        page.set_viewport_size({'width': 1000, 'height': 650})
        page.screenshot(path=str(out / 'width-ranges.png'))
        assert not errors, errors
        assert not original_requests, original_requests
        browser.close()
    receipt = {'status': 'PASS', 'actual_native_wasm_queries': 5, 'new_jet_ranges': 2,
        'pacific_neuc_widths': 4, 'cross_basin_family_widths': 0, 'scoped_widths': SCOPED_WIDTH_COUNT,
        'mixed_source_comparisons_preserved': True, 'original_file_not_claimed': True,
        'source_addresses_exact': True, 'keyboard_current_to_figure': True, 'mobile_320px': True,
        'seasonal_playback_disabled': True, 'automatic_original_requests': 0}
    (out / 'result.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf8')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
