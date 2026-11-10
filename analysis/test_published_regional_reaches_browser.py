"""Native first, then exact WASM rows and keyboard atlas navigation."""
import json
import os
from pathlib import Path
import subprocess
from urllib.parse import quote

from playwright.sync_api import sync_playwright, expect

import published_regional_reaches_query as admission
from test_rust_query_browser import browser_query

ROOT = admission.ROOT
BASE = 'http://127.0.0.1:8788'
CLI = ROOT/'rust/osw-query/target/debug'/('osw-query-cli.exe' if os.name == 'nt' else 'osw-query-cli')


def main():
    output = ROOT/'.pytest_cache/published-regional-reaches/browser'
    output.mkdir(parents=True, exist_ok=True)
    contract, _ = admission.evidence()
    requests = []
    for collection, record in admission.records(contract):
        query = {'collection': collection, 'filters': [{'field': 'id', 'op': 'eq', 'value': record['id']}], 'limit': 1}
        result = subprocess.run([str(CLI), 'almanac/query-data.json', '-'], cwd=ROOT,
                                input=json.dumps(query).encode(), capture_output=True, check=True)
        value = json.loads(result.stdout)
        assert value['rows'] == [record]
        requests.append((query, value))
    owner_query = {'collection': 'objects', 'filters': [{'field': 'id', 'op': 'eq', 'value': admission.ENTITY}], 'limit': 1}
    result = subprocess.run([str(CLI), 'almanac/query-data.json', '-'], cwd=ROOT,
                            input=json.dumps(owner_query).encode(), capture_output=True, check=True)
    owner = json.loads(result.stdout)['rows'][0]
    assert owner['regional_reach_ids'] == [admission.ID]
    assert owner['linked_source_count'] == len(owner['source_ids'])
    assert owner['published_length_km'] is None
    errors, original_downloads = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        try:
            page = browser.new_page(viewport={'width': 1100, 'height': 900})
            page.set_default_timeout(240000)
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('request', lambda request: original_downloads.append(request.url)
                    if request.url.split('?')[0].endswith(('.pdf', '.nc', '.zip')) else None)
            page.goto(BASE+'/almanac/query.html?q='+quote(json.dumps(requests[0][0])))
            page.wait_for_function('window.oswLastQueryResult || document.querySelector("#query-status")?.classList.contains("error")', timeout=240000)
            assert page.evaluate('window.oswLastQueryResult'), page.locator('#query-status').inner_text()
            assert page.evaluate('window.oswLastQueryResult') == requests[0][1]
            for query, expected in requests[1:]:
                assert browser_query(page, query) == expected
            assert browser_query(page, requests[0][0]) == requests[0][1]
            expect(page.locator('#query-caption')).to_contain_text('Published regional reaches')
            expect(page.locator('#query-caption')).not_to_contain_text('undefined')
            expect(page.locator('#query-rows')).to_contain_text('>300 km')
            page.locator('#query-rows').scroll_into_view_if_needed()
            page.screenshot(path=str(output/'regional-reach-table.png'))
            page.locator('#query-rows button').first.click()
            image=page.locator('.query-regional-reach-image')
            expect(image).to_be_visible()
            page.wait_for_function('document.querySelector(".query-regional-reach-image")?.naturalWidth > 0')
            image.scroll_into_view_if_needed()
            page.screenshot(path=str(output/'regional-reach-query.png'))
            page.close()
            browser.close()
            browser = pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
            page = browser.new_page(viewport={'width': 320, 'height': 900})
            page.set_default_timeout(240000)
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('request', lambda request: original_downloads.append(request.url)
                    if request.url.split('?')[0].endswith(('.pdf', '.nc', '.zip')) else None)
            page.goto(BASE+'/almanac/reference-routes.html?atlas-feature=current%3Aalgerian#route-atlas')
            evidence = page.locator('.route-atlas-evidence-links')
            evidence.wait_for(state='attached', timeout=240000)
            if not evidence.evaluate('(element) => element.open'):
                evidence.locator(':scope > summary').focus(); page.keyboard.press('Enter')
            for link in contract['card_links']:
                expect(evidence.get_by_role('link', name=link['label'], exact=True)).to_be_visible(timeout=240000)
            link = evidence.get_by_role('link', name=contract['card_links'][1]['label'], exact=True)
            link.scroll_into_view_if_needed()
            page.screenshot(path=str(output/'algerian-card-phone.png'))
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            link.focus(); page.keyboard.press('Enter')
            page.wait_for_url('**/query.html?**', timeout=240000)
            page.wait_for_function('window.oswLastQueryResult || document.querySelector("#query-status")?.classList.contains("error")', timeout=240000)
            assert page.evaluate('window.oswLastQueryResult'), page.locator('#query-status').inner_text()
            assert page.evaluate('window.oswLastQueryResult') == requests[0][1]
            row_button=page.locator('#query-rows button').first
            row_button.focus(); page.keyboard.press('Enter')
            image=page.locator('.query-regional-reach-image')
            expect(image).to_be_visible()
            page.wait_for_function('document.querySelector(".query-regional-reach-image")?.naturalWidth > 0')
            image.scroll_into_view_if_needed()
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.screenshot(path=str(output/'regional-reach-phone.png'))
            assert not errors and not original_downloads, (errors, original_downloads)
        except BaseException as error:
            diagnostic={'status':'FAIL','error':str(error),'page_errors':errors,'original_downloads':original_downloads}
            if 'page' in locals() and not page.is_closed():
                diagnostic['url']=page.url
                diagnostic['query_status']=page.locator('#query-status').inner_text() if page.locator('#query-status').count() else None
                diagnostic['body_text']=page.locator('body').inner_text()[:12000]
                page.screenshot(path=str(output/'failure.png'))
            (output/'failure.json').write_text(json.dumps(diagnostic,indent=2)+'\n',encoding='utf8')
            raise
        finally:
            browser.close()
    (output/'result.json').write_text(json.dumps({'status': 'PASS', 'native_and_wasm_exact_records': 4,
        'mobile_keyboard_atlas_query_link': True, 'readable_regional_threshold': True,
        'responsive_frozen_diagram': True, 'mobile_keyboard_inspector': True, 'new_whole_current_dimensions': 0,
        'original_downloads': original_downloads, 'errors': errors}, indent=2)+'\n', encoding='utf8')
    print('PASS four exact regional-reach records, native/WASM parity and mobile atlas navigation')


if __name__ == '__main__':
    main()
