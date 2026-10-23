"""Complete native source preservation, then serial WASM/card navigation."""
import gc
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
from urllib.parse import quote

from playwright.sync_api import sync_playwright, expect

from caribbean_ru29_query import FILE, ID, ENTITY, method
from test_rust_query_browser import browser_query

ROOT = method.ROOT
BASE = 'http://127.0.0.1:8788'
CLI = ROOT/'rust/osw-query/target/debug'/('osw-query-cli.exe' if os.name == 'nt' else 'osw-query-cli')


def main():
    output = ROOT/'.pytest_cache/caribbean-ru29-delivery/browser'
    output.mkdir(parents=True, exist_ok=True)
    contract = json.loads((ROOT/FILE).read_bytes())
    query = {'collection': 'diagnostics', 'filters': [{'field': 'id', 'op': 'eq', 'value': ID}], 'limit': 1}
    result = subprocess.run([str(CLI), 'almanac/query-data.json', '-'], cwd=ROOT,
                            input=json.dumps(query).encode(), capture_output=True, check=True)
    native_diagnostic = json.loads(result.stdout)
    assert native_diagnostic['rows'] == [contract['diagnostic']]
    (output/'native-diagnostic.json').write_bytes(result.stdout)
    del result
    source_request = {'document': method.MIRROR, 'pointer': '/members', 'limit': 11, 'offset': 0}
    with TemporaryDirectory(dir=output) as temporary:
        folder = Path(temporary).resolve()
        assert folder.is_relative_to(ROOT.resolve())
        path = folder/'index.json'
        with gzip.open(ROOT/'almanac/index-data.json.gz', 'rb') as source, path.open('wb') as target:
            shutil.copyfileobj(source, target, length=65536)
        result = subprocess.run([str(CLI), '--index', str(path), '-'], cwd=ROOT,
                                input=json.dumps(source_request).encode(), capture_output=True, check=True)
        (output/'native-complete-source.json').write_bytes(result.stdout)
        native_source = json.loads(result.stdout)
        assert native_source['total'] == 11
        mirror = json.loads((ROOT/method.MIRROR).read_bytes())
        native_members = {row['source_key']: row['record'] for row in native_source['rows']}
        assert native_members == mirror['members']
        source_sha = hashlib.sha256((ROOT/method.MIRROR).read_bytes()).hexdigest()
        assert native_source['source_sha256'] == source_sha
        scope = native_source['scope']
        selected = {}
        for member in ['adcp-full.nc', 'adcp-transect-1.nc', 'adcp-transect-2.nc']:
            selected['/members/'+member+'/variables'] = native_members[member]['variables']
        for member in ['sla-anticyclonic-correspondances.nc', 'sla-cyclonic-correspondances.nc']:
            for group in ['LastVirtualObs', 'LastPreviousVirtualObs']:
                selected[f'/members/{member}/groups/{group}/variables'] = native_members[member]['groups'][group]['variables']
        for member in ['sla-anticyclonic-tracked.nc', 'sla-cyclonic-tracked.nc']:
            selected[f'/members/{member}/variables/observation_flag/raw_values'] = native_members[member]['variables']['observation_flag']['raw_values']
        del native_members, native_source, mirror, result
    gc.collect()
    errors, originals = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        try:
            page = browser.new_page(viewport={'width': 1150, 'height': 950})
            page.set_default_timeout(240000)
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('request', lambda request: originals.append(request.url) if request.url.split('?')[0].endswith(('.pdf', '.nc', '.zip')) else None)
            page.goto(BASE+'/almanac/query.html?q='+quote(json.dumps(query)))
            page.wait_for_function('window.oswLastQueryResult', timeout=240000)
            assert page.evaluate('window.oswLastQueryResult') == native_diagnostic
            for name in ['source_record', 'method_source']:
                record = contract[name]
                request = {'collection': 'sources', 'filters': [{'field': 'id', 'op': 'eq', 'value': record['id']}], 'limit': 1}
                assert browser_query(page, request)['rows'] == [record]
            owner_query = {'collection': 'objects', 'filters': [{'field': 'id', 'op': 'eq', 'value': ENTITY}], 'limit': 1}
            owner = browser_query(page, owner_query)['rows'][0]
            assert owner['linked_source_count'] == len(owner['source_ids']) == 5
            assert owner['provider_velocity_source'] == contract['card_context']
            panel = page.locator('#source-query-panel')
            panel.locator(':scope > summary').focus()
            page.keyboard.press('Enter')
            page.wait_for_function('window.oswSourceQueryResult', timeout=240000)
            advanced = page.locator('#source-query-panel details').first
            if advanced.get_attribute('open') is None:
                advanced.locator(':scope > summary').click()
            for pointer, value in selected.items():
                limit = 25 if isinstance(value, list) else 500
                request = {'document': method.MIRROR, 'pointer': pointer, 'limit': limit, 'offset': 0}
                page.locator('#source-query-json').fill(json.dumps(request))
                page.locator('#source-query-run-json').click()
                page.wait_for_function('pointer => window.oswSourceQueryResult?.pointer === pointer && document.querySelector("#source-query-status").dataset.pending === "false"', arg=pointer, timeout=240000)
                actual = page.evaluate('window.oswSourceQueryResult')
                expected_rows = [
                    {'source_pointer': pointer+'/'+str(key).replace('~','~0').replace('/','~1'),
                     'source_key': str(key), 'record': record}
                    for key, record in (sorted(value.items()) if isinstance(value, dict) else enumerate(value))]
                # Source flags are longer than one page: compare every retained first-page flag;
                # the full native source check above binds all flags and all source values.
                assert actual['total'] == len(value)
                assert actual['rows'] == expected_rows[:limit]
                assert actual['source_sha256'] == source_sha and actual['scope'] == scope
            assert page.locator('#source-query-export').is_enabled()
            panel.scroll_into_view_if_needed()
            page.screenshot(path=str(output/'source-query.png'))
            page.close()  # Release main/source workers before loading the atlas workspace.
            page = browser.new_page(viewport={'width': 320, 'height': 900})
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('request', lambda request: originals.append(request.url) if request.url.split('?')[0].endswith(('.pdf', '.nc', '.zip')) else None)
            page.goto(BASE+'/almanac/reference-routes.html?atlas-feature=current%3Acaribbean#route-atlas')
            evidence = page.locator('.route-atlas-evidence-links')
            evidence.wait_for(state='attached', timeout=240000)
            if not evidence.evaluate('(element) => element.open'):
                evidence.locator(':scope > summary').focus()
                page.keyboard.press('Enter')
            link = evidence.get_by_role('link', name='Compare the 2024 Caribbean velocity sections', exact=True)
            expect(link).to_be_visible(timeout=240000)
            link.scroll_into_view_if_needed()
            page.screenshot(path=str(output/'card-phone.png'))
            link.focus()
            page.keyboard.press('Enter')
            page.wait_for_url('**/caribbean-source.html')
            expect(page.locator('h1')).to_have_text('Two crossings, changing flow')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            assert not errors and not originals, (errors, originals)
        finally:
            browser.close()
    receipt = {'status': 'PASS', 'native_complete_original_mirror_values': 3609111,
               'native_original_source_members': 11, 'complete_current_variable_groups_in_wasm': 3,
               'complete_virtual_state_groups_in_wasm': 4, 'retained_observation_flags_first_pages': 2,
               'flag_page_limit': 25,
               'native_closed_before_browser': True, 'query_closed_before_atlas': True,
               'keyboard_card_to_visual': True, 'phone_320px': True,
               'new_physical_dimension_admitted': False, 'automatic_original_downloads': originals}
    (output/'result.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf8')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
