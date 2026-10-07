"""Exercise every shipped collection through the real WASM query UI."""
import json
import os
from playwright.sync_api import sync_playwright, expect
from test_rust_query_browser import ROOT, BASE, native, browser_query


def main():
    bundle = json.loads((ROOT / 'almanac/query-data.json').read_bytes())
    for name in bundle['manifest']['canonical_collections']:
        original = json.loads((ROOT / 'almanac/release/v0.1.0' / (name + '.json')).read_bytes())
        assert bundle['collections'][name] == original, name
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page = browser.new_page(viewport={'width':1280,'height':1000})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(BASE)
        page.wait_for_function('window.oswLastQueryResult', timeout=60000)
        options = page.locator('#query-collection option').evaluate_all('(nodes)=>nodes.map(n=>n.value)')
        assert set(bundle['collections']).issubset(options)
        for name, records in bundle['collections'].items():
            ordered = sorted(records, key=lambda r:r['id'])
            # Verify both ends of every collection, including the large ledgers.
            for offset in sorted({0, max(0, len(records)-1)}):
                query = {'collection':name,'sort':{'field':'id'},'limit':7,'offset':offset}
                actual = browser_query(page, query)
                assert actual == native(query), (name, offset)
                assert actual['total'] == len(records), name
                assert [r['id'] for r in actual['rows']] == [r['id'] for r in ordered[offset:offset+7]], name
                assert page.locator('#query-collection').input_value() == name
                assert page.locator('#query-rows tr').count() == len(actual['rows'])
            if records:
                # The final record remains inspectable through the rendered table.
                page.locator('#query-rows tr button').first.click()
                expect(page.locator('#query-detail h3').first).to_be_visible()
        result = browser_query(page, {'collection':'objects','limit':7})
        assert result['total'] == 240
        assert result['map_scene']['mapped_objects'] == 240
        # These map marks include contextual gateways; they are not 240 footprints.
        assert page.locator('#query-map-features').evaluate('(el)=>new Set([...el.children].map(n=>n.dataset.entity)).size') == 240
        assert not errors, errors
        browser.close()
    print(f"PASS: all {len(bundle['collections'])} shipped collections in native/WASM UI, first/last pages, record inspection, complete canonical imports and 240 object map marks")


if __name__ == '__main__':
    main()
