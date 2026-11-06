"""The strict source qualifier survives native/WASM, source export and atlas UI."""
import hashlib
import json
import os
from urllib.parse import quote
from playwright.sync_api import sync_playwright, expect
import aleutian_onishi_width as a
from browser_inventory_expectations import SCOPED_WIDTH_COUNT
from test_current_research_evidence_browser import BASE, native


def main():
    doc, _ = a.verify_inputs()
    out = a.ROOT / '.pytest_cache/aleutian-onishi-2001/browser'
    out.mkdir(parents=True, exist_ok=True)
    queries = [
        {'collection': 'widths', 'filters': [{'field': 'current_id', 'op': 'eq', 'value': 'aleutian'}], 'limit': 10},
        {'collection': 'diagnostics', 'filters': [{'field': 'id', 'op': 'eq', 'value': a.ID}], 'limit': 1},
        {'collection': 'objects', 'filters': [{'field': 'id', 'op': 'eq', 'value': 'current:aleutian'}], 'limit': 1},
        {'collection': 'sources', 'filters': [{'field': 'id', 'op': 'eq', 'value': a.SOURCE}], 'limit': 1},
        {'collection': 'widths', 'limit': 1},
    ]
    errors, originals = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page = browser.new_page(viewport={'width': 1280, 'height': 900})
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('request', lambda r: originals.append(r.url) if r.url.lower().endswith(('.pdf', '.nc', '.zip')) else None)
        page.goto(BASE + '/almanac/query.html?q=' + quote(json.dumps(queries[0])))
        page.wait_for_function('window.oswLastQueryResult', timeout=180000)
        page.locator('#query-advanced > summary').click()
        for i, query in enumerate(queries):
            if i:
                page.locator('#query-json').fill(json.dumps(query)); page.evaluate('window.oswLastQueryResult=null')
                page.locator('#query-run-json').click(); page.wait_for_function('window.oswLastQueryResult', timeout=120000)
            result = page.evaluate('window.oswLastQueryResult')
            assert result == native(query)
            assert result['total'] == (SCOPED_WIDTH_COUNT if i == 4 else 1)
            if i == 0:
                assert result['rows'] == doc['width_records']
                assert result['chart_scene']['kind'] == 'aleutian_published_width_constraint'
                panel = page.locator('.aleutian-width-constraint-query')
                expect(panel).to_contain_text('>400 km')
                expect(panel).to_contain_text('Width epoch, layer, numeric edges and upper extent unspecified')
                button = panel.get_by_role('button', name='Inspect Aleutian width constraint', exact=True)
                button.focus(); page.keyboard.press('Enter')
                expect(page.locator('#query-detail')).to_contain_text(a.WIDTH)
                page.set_viewport_size({'width': 320, 'height': 900})
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                assert 'undefined' not in panel.inner_text()
                page.screenshot(path=str(out / 'query-320px.png'), full_page=True)
                page.set_viewport_size({'width': 1280, 'height': 900})
            if i == 1:
                assert json.loads(result['rows'][0]['source_json']) == doc
            if i == 2:
                row = result['rows'][0]
                assert row['capabilities']['scoped_width'] == 1 and row['width_ids'] == [a.WIDTH]
                assert a.SOURCE in row['source_ids'] and a.ID in row['diagnostic_ids']
                assert row['published_length_km'] is None
            if i == 3:
                assert result['rows'] == [doc['source_record']]
                assert result['rows'][0]['source_file_sha256'] == doc['width_records'][0]['source_original_sha256']
            if i == 4:
                kinds = {s['kind'] for s in result['chart_scene']['scenes']}
                assert {'aleutian_published_width_constraint', 'neuc_glider_width_ranges', 'pacific_neuc_isopycnal_breadths', 'dwbc_float_composite', 'coastal_composite_widths'} <= kinds
                expect(page.locator('.aleutian-width-constraint-query')).to_be_visible()
                expect(page.locator('#chart-title')).to_have_text('Scoped source comparisons')
            print('PASS actual native/WASM query', i, flush=True)
        # The thin Rust contract binds the downloadable exact export; it is not
        # duplicated into the main WASM just to supply a download address.
        response = page.request.get(BASE + '/' + a.EXPORT)
        assert response.ok
        raw = response.body(); contract = a.contract(doc)
        assert hashlib.sha256(raw).hexdigest() == contract['export_sha256']
        assert raw == (a.ROOT / a.EXPORT).read_bytes() and json.loads(raw) == a.export(doc)
        page.goto(BASE + '/almanac/seasons.html?current=aleutian')
        page.wait_for_function('window.oswSeasonSnapshot', timeout=180000)
        plan = page.evaluate('window.oswSeasonSnapshot.phase_plans.aleutian')
        assert not plan['can_play'] and plan['eligible_indices'] == []
        index = next(i for i, p in enumerate(plan['phases']) if p['id'] == a.WIDTH)
        page.locator('#season-phase').select_option(str(index))
        expect(page.locator('#season-title')).to_have_text('Published regional width constraint')
        expect(page.locator('#season-value')).to_contain_text('>400 km; finite width unknown')
        expect(page.locator('#season-play')).to_be_disabled()
        assert page.locator('#season-bar').locator('..').is_hidden()
        page.goto(BASE + '/almanac/reference-routes.html?atlas-feature=current%3Aaleutian#route-atlas')
        page.wait_for_function('window.oswAtlasSnapshot', timeout=180000)
        expect(page.locator('#route-atlas-preview > h3')).to_have_text('Aleutian Current', timeout=120000)
        for path in [a.FILE, a.BASE]:
            raw = page.evaluate('p=>window.oswAtlasSnapshot.sources_json[p]', path)
            assert raw.encode('utf8') == (a.ROOT / path).read_bytes()
        links = page.locator('.route-atlas-evidence-links')
        links.locator('summary').focus(); page.keyboard.press('Enter')
        link = links.get_by_role('link', name='Inspect Aleutian published width greater than400km', exact=True)
        expect(link).to_have_attribute('href', '../' + a.FIGURE)
        page.set_viewport_size({'width': 320, 'height': 900})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        link.focus(); page.keyboard.press('Enter')
        expect(page.locator('svg[role=img]')).to_contain_text('width >400km')
        expect(page.locator('#desc')).to_contain_text('strict lower constraint')
        page.set_viewport_size({'width': 1000, 'height': 560}); page.screenshot(path=str(out / 'width-constraint.png'))
        assert not errors, errors
        assert not originals, originals
        browser.close()
    receipt = {'status': 'PASS', 'actual_native_wasm_queries': 5, 'aleutian_widths': 1,
        'scoped_widths': SCOPED_WIDTH_COUNT, 'strict_operator': '>', 'value_km': 400,
        'finite_mean_not_invented': True, 'mixed_source_charts_preserved': True,
        'exact_public_export_contract': True, 'source_addresses_exact': True,
        'keyboard_current_to_figure': True, 'mobile_320px': True,
        'seasonal_playback_disabled': True, 'automatic_original_requests': 0}
    (out / 'result.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf8')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
