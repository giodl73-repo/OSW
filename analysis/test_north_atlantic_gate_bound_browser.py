"""Working nominal bound is queryable in native/WASM and from the atlas card."""
import json
import os
from urllib.parse import quote

from playwright.sync_api import sync_playwright, expect
from north_atlantic_gate_bound import ROOT, ENTITY, verify_inputs
from test_current_research_evidence_browser import BASE, native


def main():
    doc, _ = verify_inputs()
    out = ROOT / '.pytest_cache/nac-bound-browser'
    out.mkdir(exist_ok=True)
    errors, original_requests = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page = browser.new_page(viewport={'width': 1360, 'height': 1000})
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('request', lambda r: original_requests.append(r.url) if r.url.lower().endswith(('.pdf', '.xml', '.nc', '.zip')) else None)
        queries = [
            {'collection': 'length_assessments', 'filters': [{'field': 'entity_id', 'op': 'eq', 'value': ENTITY}], 'limit': 1},
            {'collection': 'measurements', 'filters': [{'field': 'id', 'op': 'eq', 'value': doc['measurement']['id']}], 'limit': 1},
            {'collection': 'current_length_bound_admissions', 'limit': 1},
            {'collection': 'length_assessments', 'filters': [{'field': 'rank_eligible', 'op': 'eq', 'value': True}], 'limit': 100},
        ]
        for query in queries:
            page.goto(BASE + '/almanac/query.html?q=' + quote(json.dumps(query)))
            page.wait_for_function('window.oswLastQueryResult', timeout=120000)
            result = page.evaluate('oswLastQueryResult')
            assert result == native(query)
            assert result['total'] == (12 if query is queries[-1] else 1)
            if query is queries[0]:
                assert result['rows'] == [doc['length_assessment']]
            if query is queries[1]:
                assert result['rows'] == [doc['measurement']]
            assert page.locator('#query-export').is_enabled()
            page.set_viewport_size({'width': 320, 'height': 1000})
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            print('PASS native/WASM', query['collection'], result['total'], flush=True)
        page.goto(BASE + '/almanac/reference-routes.html?atlas-feature=current%3Anorth-atlantic#route-atlas')
        links = page.locator('.route-atlas-evidence-links')
        links.wait_for(state='attached', timeout=120000)
        links.locator('summary').focus()
        page.keyboard.press('Enter')
        figure = links.get_by_role('link', name='Inspect the nominal-section geographic bound', exact=True)
        expect(figure).to_be_visible()
        expect(figure).to_have_attribute('href', '../' + doc['figure_file'])
        assert links.get_by_role('link', name='Query the working North Atlantic length assessment', exact=True).count() == 1
        assert links.get_by_role('link', name='Audit all nine geographic gate scenarios', exact=True).count() == 1
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        links.screenshot(path=str(out / 'card-mobile.png'))
        figure.focus()
        page.keyboard.press('Enter')
        expect(page.locator('svg')).to_have_attribute('role', 'img')
        expect(page.locator('#desc')).to_contain_text('Not a mapped current route or whole-current length')
        page.set_viewport_size({'width': 1100, 'height': 650})
        page.screenshot(path=str(out / 'figure.png'))
        assert not errors and not original_requests, (errors, original_requests)
        browser.close()
    receipt = {'status': 'PASS', 'native_actual_wasm_queries': 4, 'qualified_ranked_lengths': 12,
               'conditional_floor_km': 1200, 'keyboard_mapped_card_figure': True,
               'mobile_320px': True, 'accessible_scalar_svg': True, 'automatic_original_requests': 0}
    (out / 'result.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
