"""One cloud-only browser case for the dedicated, immutable evidence view."""
import functools
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import threading
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '.pytest_cache/current-local-extent-ui-v1'


def verify_sources():
    if (os.environ.get('GITHUB_ACTIONS') != 'true'
            or os.environ.get('GITHUB_REPOSITORY') != 'giodl73-repo/OSW'
            or os.environ.get('GITHUB_REF') != 'refs/heads/codex/current-measurement-gaps'
            or not hasattr(os, 'sched_getaffinity') or len(os.sched_getaffinity(0)) != 1):
        raise RuntimeError('This browser case runs on one cloud CPU only.')
    request = json.loads((ROOT / 'research/current-local-extent-ui-request-v1.json').read_bytes())
    if request.get('execution_permitted') is not True or request.get('ui_verification_only') is not True:
        raise RuntimeError('UI verification is disabled.')
    assert request['max_heavy_local_jobs'] == 0 and request['max_cloud_jobs'] == 1
    assert all(request[name] is False for name in ['provider_requests_permitted',
        'original_source_processing_permitted','measurement_admission_permitted','main_merge_permitted'])
    raw = (ROOT / 'research/current-local-extent-ui-preflight-v1.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == request['preflight_sha256']
    pref = json.loads(raw)
    assert pref['schema'] == 'osw.current-local-extent-ui-preflight.v1'
    for name, expected in pref['input_sha256'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
    for name in ['research/eacc-coastal-reference-extent-preflight-v1.json',
                 'research/current-local-extent-query-check-preflight-v2.json']:
        for path, expected in json.loads((ROOT / name).read_bytes())['input_sha256'].items():
            assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
    assert json.loads((ROOT / 'research/current-gap-delivery-phase.json').read_bytes())['heavy_work_permitted'] is False
    return pref


def main():
    pref = verify_sources()
    from playwright.sync_api import sync_playwright, expect
    OUTPUT.mkdir(parents=True, exist_ok=True)

    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f'http://127.0.0.1:{server.server_port}/almanac/local-extents.html'
    checked = []
    forbidden = ('/query-engine.wasm', '/query-data.json', '/index-data', '/query-worker.js', '/index-worker.js')
    requests, errors = [], []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=['--renderer-process-limit=1'])

            def context():
                ctx = browser.new_context(viewport={'width':1280, 'height':1000}, service_workers='block')
                ctx.on('request', lambda req: requests.append(req.url))
                ctx.on('page', lambda page: page.on('pageerror', lambda error: errors.append(str(error))))
                return ctx

            ctx = context()
            page = ctx.new_page()
            page.goto(base)
            expect(page.locator('#page-status')).to_have_text('1–12 of 12')
            assert page.locator('#result-body tr').count() == 12
            expect(page.locator('#engine-status')).to_contain_text('72 source cases · 864 attempted extents')
            page.wait_for_function('document.querySelector("#evidence-chart").naturalWidth > 0')
            checked.append('default_primary_12_rows_and_chart')
            page.locator('#result-body button').first.click()
            expect(page.locator('#record-panel')).to_be_visible()
            record = json.loads(page.locator('#record-json').inner_text())
            case = json.loads(page.locator('#case-json').inner_text())
            assert record['case_id'] == case['id']
            assert record['whole_current_width_km'] is None
            assert record['physical_state_join_eligible'] is False
            shared = page.url
            page.reload()
            expect(page.locator('#record-panel')).to_be_visible()
            assert json.loads(page.locator('#record-json').inner_text()) == record
            checked.append('record_case_context_and_shared_url_reload')
            page.locator('#case-link button').click()
            expect(page.locator('#page-status')).to_have_text('1–1 of 1')
            page.locator('[data-preset="missing"]').click()
            expect(page.locator('#page-status')).to_have_text('1–6 of 6')
            assert page.locator('#result-body tr').count() == 6
            checked.append('source_case_query_and_six_coarse_missing_cases')
            page.locator('[data-preset="all"]').click()
            expect(page.locator('#page-status')).to_have_text('1–100 of 864')
            page.locator('#next').click()
            expect(page.locator('#page-status')).to_have_text('101–200 of 864')
            page.locator('#previous').click()
            expect(page.locator('#page-status')).to_have_text('1–100 of 864')
            page.locator('[data-preset="cases"]').click()
            expect(page.locator('#page-status')).to_have_text('1–72 of 72')
            checked.append('all_attempts_pagination_and_complete_case_inventory')
            page.locator('[data-preset="primary"]').click()
            expect(page.locator('#page-status')).to_have_text('1–12 of 12')
            page.locator('#month').select_option('7')
            page.locator('#filters button[type=submit]').click()
            expect(page.locator('#page-status')).to_have_text('1–1 of 1')
            assert page.locator('#result-body tr td').nth(1).inner_text() == 'Jul'
            checked.append('month_and_primary_controls')
            page.locator('#query-controls > details > summary').click()

            def query(value, expected=None, error=None):
                page.locator('#query-json').fill(json.dumps(value))
                page.locator('#run-json').click()
                if error:
                    expect(page.locator('#query-status')).to_have_attribute('data-error', 'true')
                    expect(page.locator('#query-status')).to_contain_text(error)
                    assert page.locator('#result-body tr').count() == 0
                else:
                    expect(page.locator('#page-status')).to_have_text(expected)

            name = 'current_local_extents'
            query({'collection':name,'filters':[{'field':'whole_current_width_km','op':'eq','value':None}]}, '1–100 of 864')
            query({'collection':name,'filters':[{'field':'whole_current_width_km','op':'eq','value':0}]}, '0–0 of 0')
            query({'collection':name,'state_code':'NAT'}, error='do not support physical state')
            query({'collection':name,'filters':[{'field':'width_km','op':'eq','value':100}]}, error='Unknown')
            checked.append('null_is_not_zero_and_unsupported_joins_refused')
            page.locator('#query-json').fill('{')
            page.locator('#run-json').click()
            expect(page.locator('#query-status')).to_have_attribute('data-error', 'true')
            assert page.locator('#result-body tr').count() == 0
            page.locator('[data-preset="primary"]').focus()
            page.keyboard.press('Enter')
            expect(page.locator('#page-status')).to_have_text('1–12 of 12')
            page.locator('#result-body button').first.focus()
            page.keyboard.press('Enter')
            expect(page.locator('#record-panel')).to_be_focused()
            checked.append('malformed_json_clears_results_and_keyboard_inspection')
            assert not page.locator('#query-controls').evaluate('(node)=>node.inert')
            assert not page.locator('[id^="workspace-"]').count()
            databases = page.evaluate('async()=> (await indexedDB.databases()).map(item=>item.name)')
            assert 'osw-query-workspaces' not in databases
            page.screenshot(path=str(OUTPUT / 'desktop.png'), full_page=True)
            page.set_viewport_size({'width':390,'height':844})
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.screenshot(path=str(OUTPUT / 'mobile.png'), full_page=True)
            checked.append('workspace_isolation_and_mobile_layout')
            ctx.close()

            # A changed snapshot must fail closed; retry after restoring exact bytes.
            ctx = context()
            original = (ROOT / 'research/eacc-local-extent-evidence-bundle-v1.json').read_bytes()
            changed = bytes([original[0] ^ 1]) + original[1:]
            pattern = '**/research/eacc-local-extent-evidence-bundle-v1.json'
            ctx.route(pattern, lambda route: route.fulfill(status=200, body=changed))
            page = ctx.new_page(); page.goto(base)
            expect(page.locator('#engine-status')).to_contain_text('hash does not match')
            assert page.locator('#query-controls').evaluate('(node)=>node.inert')
            assert page.locator('#result-body tr').count() == 0
            ctx.unroute(pattern); page.locator('#reload').click()
            expect(page.locator('#page-status')).to_have_text('1–12 of 12')
            checked.append('corrupt_snapshot_refusal_and_clean_reload_recovery')
            ctx.close()

            ctx = context(); ctx.route('**/local-extents-engine.wasm', lambda route: route.fulfill(status=404))
            before = len(requests)
            page = ctx.new_page(); page.goto(base)
            expect(page.locator('#engine-status')).to_contain_text('HTTP 404')
            assert page.locator('#query-controls').evaluate('(node)=>node.inert')
            assert not any('/research/eacc-local-extent-evidence-bundle-v1.json' in url for url in requests[before:])
            checked.append('missing_engine_refusal_without_data_or_atlas_fallback')
            ctx.close(); browser.close()
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=5)
    assert not errors, errors
    assert not any(fragment in url for url in requests for fragment in forbidden)
    report = {'schema':'osw.current-local-extent-ui.browser-result.v1',
              'source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],
              'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],'checks':checked,
              'requested_paths':sorted({urlparse(url).path for url in requests}),
              'page_errors':errors,'full_atlas_assets_requested':False,
              'source_velocity_arrays_processed':False,'new_physical_widths_admitted':0,
              'scientific_inputs_unchanged':83,'runtime_inputs_unchanged':23,
              'ui_source_inputs_verified':len(pref['input_sha256']),
              'shared_record_url_path':urlparse(shared).path,
              'screenshots':['desktop.png','mobile.png']}
    (OUTPUT / 'result.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
