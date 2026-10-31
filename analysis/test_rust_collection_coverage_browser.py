"""Exercise every shipped collection through the real WASM query UI."""
from query_packet import read_bundle_bytes
import json
import os
from playwright.sync_api import sync_playwright, expect
from test_rust_query_browser import ROOT, BASE, native, browser_query


def main():
    bundle = json.loads(read_bundle_bytes(ROOT / 'almanac/query-data.json'))
    from canonical_working_assertions import assert_canonical_imports
    assert_canonical_imports(bundle)
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
        object_count=len(bundle['collections']['objects'])
        assert result['total'] == object_count
        mapped_ids={row['id'] for row in bundle['collections']['objects'] if row['map_features']}
        assert result['map_scene']['matching_objects'] == object_count
        assert result['map_scene']['mapped_objects'] == len(mapped_ids)
        assert result['map_scene']['unmapped_objects'] == object_count-len(mapped_ids)
        # All source-located records have marks; unlocated names remain queryable.
        actual_ids=set(page.locator('#query-map-features').evaluate('(el)=>[...new Set([...el.children].map(n=>n.dataset.entity))]'))
        assert actual_ids == mapped_ids
        assert not errors, errors
        browser.close()
    print(f"PASS: all {len(bundle['collections'])} shipped collections in native/WASM UI, first/last pages, record inspection, complete canonical imports and {object_count} object map marks")


if __name__ == '__main__':
    main()
