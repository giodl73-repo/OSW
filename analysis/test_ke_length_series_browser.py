"""Full regional series/reading parity, followed by accessible map-card access."""
import json
import os
from urllib.parse import quote

from playwright.sync_api import sync_playwright, expect
from ke_length_series_query import ROOT, ENTITY, SOURCE_ID, evidence, links, reading_rows
from test_current_research_evidence_browser import BASE, native
from test_rust_query_browser import browser_query


def main():
    header, _ = evidence()
    output = ROOT / '.pytest_cache/ke-qiu-delivery/browser'
    output.mkdir(parents=True, exist_ok=True)
    header_query = {'collection': 'current_length_series', 'filters': [{'field': 'id', 'op': 'eq', 'value': header['id']}], 'limit': 1}
    pages = [{'collection': 'current_length_readings',
              'filters': [{'field': 'series_id', 'op': 'eq', 'value': header['id']}],
              'sort': {'field': 'graph_reading_order', 'direction': 'asc'}, 'offset': offset, 'limit': 500}
             for offset in range(0, header['graph_reading_count'], 500)]
    # All native bundle loads terminate before Chromium is started.
    expected_header = native(header_query)
    assert expected_header['rows'] == [header] and expected_header['total'] == 1
    expected_pages = [native(query) for query in pages]
    rows = [row for result in expected_pages for row in result['rows']]
    assert rows == reading_rows(header) and len(rows) == 1612
    assert all(result['total'] == 1612 for result in expected_pages)
    errors, originals = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'], args=['--disable-features=BackForwardCache'])
        page = browser.new_page(viewport={'width': 1100, 'height': 950})
        page.set_default_timeout(180000)
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda request: originals.append(request.url) if request.url.split('?')[0].endswith(('.pdf', '.nc', '.zip', '.xml')) else None)
        page.goto(BASE + '/almanac/query.html?q=' + quote(json.dumps(header_query)))
        page.wait_for_function('window.oswLastQueryResult', timeout=180000)
        assert page.evaluate('window.oswLastQueryResult') == expected_header
        assert page.locator('#query-export').is_enabled()
        for query, expected in zip(pages, expected_pages):
            actual = browser_query(page, query)
            assert actual == expected
            assert page.locator('#query-export').is_enabled()
        assert len({r['id'] for r in rows}) == 1612
        for collection, field, value, record in [
            ('length_assessments', 'entity_id', ENTITY, header['length_assessment']),
            ('measurements', 'id', header['measurement']['id'], header['measurement']),
            ('claims', 'id', header['claim']['id'], header['claim']),
            ('sources', 'id', SOURCE_ID, header['source_record']),
        ]:
            result = browser_query(page, {'collection': collection, 'filters': [{'field': field, 'op': 'eq', 'value': value}], 'limit': 1})
            assert result['total'] == 1 and result['rows'] == [record]
        ranked = browser_query(page, {'collection': 'length_assessments', 'filters': [{'field': 'rank_eligible', 'op': 'eq', 'value': True}], 'limit': 100})
        assert ranked['total'] == 13 and all(r['entity_id'] != ENTITY for r in ranked['rows'])
        page.set_viewport_size({'width': 320, 'height': 1000})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.goto(BASE + '/almanac/reference-routes.html?atlas-feature=current%3Akuroshio-extension#route-atlas')
        panel = page.locator('.route-atlas-evidence-links')
        panel.wait_for(state='attached', timeout=180000)
        if not panel.evaluate('(element)=>element.open'):
            panel.locator('summary').focus()
            page.keyboard.press('Enter')
        for link in links(header):
            expect(panel.get_by_role('link', name=link['label'], exact=True)).to_have_attribute('href', link['url'])
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        panel.screenshot(path=str(output / 'card-phone.png'))
        figure = panel.get_by_role('link', name=links(header)[0]['label'], exact=True)
        figure.focus()
        page.keyboard.press('Enter')
        expect(page.locator('svg')).to_have_attribute('role', 'img')
        expect(page.locator('#desc')).to_contain_text('1,120 to4,660km')
        expect(page.locator('#desc')).to_contain_text('not observations')
        page.set_viewport_size({'width': 1100, 'height': 650})
        page.screenshot(path=str(output / 'figure.png'))
        assert not errors and not originals, (errors, originals)
        browser.close()
    receipt = {'status': 'PASS', 'complete_native_wasm_series_headers': 1,
               'complete_native_wasm_graph_readings': len(rows), 'query_pages': len(pages),
               'individual_wasm_records': 4, 'qualified_ranked_lengths': 13,
               'ke_whole_current_ranked': False, 'native_cli_closed_before_browser': True,
               'one_query_and_one_atlas_workspace': True, 'keyboard_card_to_figure': True,
               'phone_320px': True, 'automatic_original_downloads': 0}
    (output / 'result.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf8')
    print('PASS: complete KE series, all1612 readings, provenance, scoped assessment, keyboard/phone card and chart')


if __name__ == '__main__':
    main()
