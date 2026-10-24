"""Same scoped reports through actual native/WASM queries and atlas links."""
import json
import os
from urllib.parse import quote
from playwright.sync_api import sync_playwright, expect
import hansen_asar_widths as h
from test_current_research_evidence_browser import BASE, native


def main():
    doc, _ = h.verify_inputs()
    out = h.ROOT / '.pytest_cache/hansen-asar-2011/browser'
    out.mkdir(exist_ok=True)
    errors, originals = [], []
    queries = [
        {'collection': 'widths', 'filters': [{'field': 'source_id', 'op': 'eq', 'value': h.SOURCE}], 'limit': 10},
        {'collection': 'diagnostics', 'filters': [{'field': 'id', 'op': 'eq', 'value': h.ID}], 'limit': 1},
        {'collection': 'objects', 'filters': [{'field': 'id', 'op': 'eq', 'value': 'current:norwegian-atlantic-slope'}], 'limit': 1},
        {'collection': 'objects', 'filters': [{'field': 'id', 'op': 'eq', 'value': 'current:norwegian-coastal'}], 'limit': 1},
    ]
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page = browser.new_page(viewport={'width': 1280, 'height': 900})
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda r: originals.append(r.url) if r.url.lower().endswith(('.pdf', '.nc', '.zip', '.xml')) else None)
        page.goto(BASE + '/almanac/query.html?q=' + quote(json.dumps(queries[0])))
        page.wait_for_function('window.oswLastQueryResult', timeout=180000)
        page.locator('#query-advanced > summary').click()
        for i, query in enumerate(queries):
            if i:
                page.locator('#query-json').fill(json.dumps(query))
                page.evaluate('window.oswLastQueryResult = null')
                page.locator('#query-run-json').click()
                page.wait_for_function('window.oswLastQueryResult', timeout=120000)
            result = page.evaluate('window.oswLastQueryResult')
            assert result == native(query)
            assert result['total'] == (3 if i == 0 else 1)
            if i == 0:
                assert sorted(result['rows'], key=lambda r: r['id']) == sorted(doc['width_records'], key=lambda r: r['id'])
                assert not any(r['approximate_width_km'] == 45 for r in result['rows'])
            if i == 1:
                assert json.loads(result['rows'][0]['source_json']) == doc
                assert result['chart_scene']['kind'] == 'hansen_asar_surface_widths'
                expect(page.locator('.asar-width-query')).to_contain_text('Mixed profiles excluded')
                expect(page.locator('.asar-width-query img')).to_have_attribute('src', '../' + h.FIGURE)
                page.set_viewport_size({'width': 320, 'height': 900})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                page.set_viewport_size({'width': 1280, 'height': 900})
            if i > 1:
                assert result['rows'][0]['capabilities']['scoped_width'] == (8 if i == 2 else 2)
                assert (h.ID if i == 2 else h.ID + ':coastal') in result['rows'][0]['diagnostic_ids']
                assert h.SOURCE in result['rows'][0]['source_ids']
            assert page.locator('#query-export').is_enabled()
            print('PASS actual native/WASM', query['collection'], i, flush=True)
        page.goto(BASE + '/almanac/reference-routes.html?atlas-feature=current%3Anorwegian-atlantic-slope#route-atlas')
        page.wait_for_function('window.oswAtlasSnapshot', timeout=180000)
        expect(page.locator('#route-atlas-preview > h3')).to_have_text('Norwegian Atlantic Slope Current', timeout=120000)
        links = page.locator('.route-atlas-evidence-links')
        links.locator('summary').focus()
        page.keyboard.press('Enter')
        figure_link = links.get_by_role('link', name='Compare ASAR separate and mixed surface-width reports', exact=True)
        expect(figure_link).to_have_attribute('href', '../' + h.FIGURE)
        for path in [h.FILE, h.EXPORT, h.BASE]:
            raw = page.evaluate('p => window.oswAtlasSnapshot.sources_json[p]', path)
            assert raw.encode('utf8') == (h.ROOT / path).read_bytes()
        card = page.locator('#inventory-addition-norwegian-atlantic-slope .asar-width-admissions')
        expect(card).to_contain_text('36km')
        expect(card).to_contain_text('Mixed45km P2 and60km S1 profiles are excluded')
        assert card.get_by_role('link', name='Open ASAR local-width comparison').evaluate('(a) => a.href') == BASE + '/' + h.FIGURE
        page.set_viewport_size({'width': 320, 'height': 900})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        figure_link.focus()
        page.keyboard.press('Enter')
        expect(page.locator('svg')).to_have_attribute('role', 'img')
        expect(page.locator('#desc')).to_contain_text('No annual envelope or width error')
        page.set_viewport_size({'width': 1000, 'height': 620})
        page.screenshot(path=str(out / 'comparison.png'))
        page.goto(BASE + '/almanac/seasons.html?current=norwegian-atlantic-slope')
        page.wait_for_function('window.oswSeasonSnapshot', timeout=180000)
        expect(page.locator('#season-play')).to_be_disabled()
        plan = page.evaluate('window.oswSeasonSnapshot.phase_plans["norwegian-atlantic-slope"]')
        assert not plan['can_play'] and plan['eligible_indices'] == []
        assert len(plan['phases']) == 8
        assert all(p['playback_step_eligible'] is False and p['frame_id'] is None for p in plan['phases'])
        assert {r['id'] for r in doc['width_records'] if r['current_id'] == 'norwegian-atlantic-slope'} <= {p['width_id'] for p in plan['phases']}
        assert not errors and not originals, (errors, originals)
        browser.close()
    receipt = {'status': 'PASS', 'actual_native_wasm_queries': 4, 'width_records': 3,
               'slope_width_records': 8, 'coastal_width_records': 2, 'atlas_original_source_addresses_exact': True,
               'atlas_card_figure_keyboard_links': True, 'mobile_320px': True,
               'seasonal_animation_disabled': True, 'automatic_original_requests': 0}
    (out / 'result.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf8')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
