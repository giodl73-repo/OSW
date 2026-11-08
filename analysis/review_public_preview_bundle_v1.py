"""Bounded first-visitor tasks against only the selected website, cloud only."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
import os
from pathlib import Path
import re
import signal
from threading import Thread
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.pytest_cache/public-preview-bundle-v1'
PRIOR_UI_SECONDS = 55.364067036


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def main():
    assert os.environ.get('GITHUB_ACTIONS') == 'true'
    assert len(os.sched_getaffinity(0)) == 1 and os.getpriority(os.PRIO_PROCESS, 0) >= 15
    assert not (OUT / 'delivery/browser-result.json').exists()
    started = time.monotonic()
    result = {'schema': 'osw.public-preview-bundle-browser.v1', 'status': 'FAIL',
              'source_commit': os.environ['GITHUB_SHA'], 'prior_ui_seconds': PRIOR_UI_SECONDS,
              'ui_limit_seconds': 60, 'page_errors': [], 'http_failures': [],
              'external_requests': [], 'unreviewed_data_requests': [], 'checks': [], 'publication_approved': False}
    server = None

    def deadline(*_args):
        raise TimeoutError('Carried public-preview UI budget reached')

    signal.signal(signal.SIGALRM, deadline)
    signal.setitimer(signal.ITIMER_REAL, 4.2)
    try:
        from playwright.sync_api import sync_playwright
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(OUT / 'site')))
        server.daemon_threads = True
        Thread(target=lambda: server.serve_forever(poll_interval=.01), daemon=True).start()
        base = f'http://127.0.0.1:{server.server_port}'
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1280, 'height': 900}, reduced_motion='reduce',
                                          permissions=['clipboard-read', 'clipboard-write'], accept_downloads=True)
            page = context.new_page()
            page.set_default_timeout(700)
            page.on('pageerror', lambda error: result['page_errors'].append(str(error)[:500]))
            page.on('response', lambda response: result['http_failures'].append(response.url.removeprefix(base)) if response.status >= 400 else None)

            def request(req):
                if req.url.startswith(('http://', 'https://')) and not req.url.startswith(base):
                    result['external_requests'].append(req.url)
                if any(p in req.url for p in ['query-engine.wasm', 'query-data.json', 'query-parts/', 'display-data-v1/', 'preview-data-candidate-v1/', '/research/']):
                    result['unreviewed_data_requests'].append(req.url.removeprefix(base))

            page.on('request', request)
            page.goto(base + '/', wait_until='domcontentloaded')
            assert page.get_by_role('heading', name='An atlas of the moving ocean.', exact=True).is_visible()
            page.get_by_role('link', name='Start with the Agulhas Current', exact=True).click()
            page.wait_for_function("document.querySelector('#record-name').textContent.includes('Agulhas') && document.querySelector('#record-content a')")
            assert page.locator('#feature-choice option').count() == 112
            assert page.locator('#ocean-features path').count() > 50
            assert page.evaluate("document.querySelector('#ocean-map').viewBox.baseVal.width < 1480")
            page.locator('#ocean-map').focus()
            page.keyboard.press('Home')
            assert page.evaluate("document.querySelector('#ocean-map').viewBox.baseVal.width === 1480")
            page.get_by_role('button', name='Copy view link', exact=True).click()
            page.wait_for_function("document.querySelector('#share-status').textContent.startsWith('View link copied')")
            with page.expect_download() as pending:
                page.get_by_role('button', name='Download record JSON', exact=True).click()
            raw = Path(pending.value.path()).read_bytes()
            assert re.search(rb'^\{\s*"schema":\s*"osw.preview-record.v1",\s*"id":\s*"current:agulhas"', raw)
            result['download'] = {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'identity_checked_without_numerical_parsing': True}
            metadata_role = page.evaluate("async()=> (await OSWPreview.edition()).contexts['agulhas-i06s-2019-native-uv-local-cutoffs'].context_role")
            assert metadata_role == 'OSW_admission_and_method_context_not_independent_measurement'
            page.screenshot(path=str(OUT / 'delivery/atlas-desktop.png'), animations='disabled')
            result['checks'].append('Home entrance, all 111 current names, drawn routes, Agulhas card, keyboard world return, share link, scoped JSON download, and supplemented method context')
            page.get_by_role('link', name='Explore this feature’s evidence', exact=True).click()
            page.wait_for_function("document.querySelector('#load-status').textContent.includes('references are ready')")
            assert page.locator('#results article').count() > 0
            page.locator('#collection').select_option('depth')
            page.get_by_role('button', name='Find references', exact=True).click()
            page.wait_for_function("document.querySelector('#load-status').textContent.includes('references are ready')")
            assert page.locator('#results article').count() > 0
            assert page.locator('#comparison-note').is_visible()
            result['checks'].append('Map-to-explorer identity link, current length and depth queries, comparison scope, and reference cards')
            page.get_by_role('link', name='Eddy references', exact=True).click()
            page.wait_for_function("document.querySelector('#result-count').textContent.startsWith('331 reference records')")
            assert page.locator('#results article').count() == 30
            assert page.locator('#results article').first.inner_text().find('registry identity join unverified') >= 0
            result['checks'].append('All 331 separate eddy references are queryable, paginated, and identity-qualified')
            page.get_by_role('link', name='NASA views', exact=True).click()
            page.wait_for_function("document.querySelector('#load-status').textContent.startsWith('70 NASA')")
            assert page.get_by_role('link', name='Watch at NASA', exact=True).count() == 70
            assert page.locator('#state option').count() == 57
            page.get_by_role('link', name='Ocean states', exact=True).click()
            page.wait_for_function("document.querySelector('#state').options.length===57")
            page.locator('#state').select_option(index=1)
            page.get_by_role('button', name='Find associated feature references', exact=True).click()
            page.wait_for_function("document.querySelector('#load-status').textContent.includes('retained association evidence')")
            result['checks'].append('70 NASA-hosted navigation links, 56 state names, and qualified state-association lookup')
            page.goto(base + '/almanac/atlas.html?atlas-feature=current%3Akuroshio', wait_until='domcontentloaded')
            page.wait_for_function("document.querySelector('#record-name').textContent.includes('Kuroshio') && document.querySelector('#record-content a')")
            page.set_viewport_size({'width': 390, 'height': 844})
            page.locator('#feature-choice').select_option('current:agulhas')
            page.wait_for_function("document.querySelector('#record-name').textContent.includes('Agulhas') && document.querySelector('#record-content a')")
            assert page.evaluate("document.activeElement.id==='record-name' && document.documentElement.scrollWidth<=innerWidth+1")
            page.screenshot(path=str(OUT / 'delivery/atlas-mobile.png'), animations='disabled')
            page.get_by_role('link', name='Back to the world map', exact=True).click()
            assert page.evaluate("document.querySelector('#ocean-map').viewBox.baseVal.width===1480")
            result['checks'].append('Deep-linked Kuroshio, narrow layout, selection focus, mobile card reveal and world return, reduced-motion context')
            assert not any(result[k] for k in ['page_errors', 'http_failures', 'external_requests', 'unreviewed_data_requests'])
            browser.close()
        result['status'] = 'PASS_SELECTED_BUNDLE_TASKS_ONLY'
    except Exception as error:
        result['error'] = type(error).__name__ + ': ' + str(error)[:1200]
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        if server:
            server.shutdown()
            server.server_close()
        result['active_seconds'] = time.monotonic() - started
        result['cumulative_ui_seconds'] = PRIOR_UI_SECONDS + result['active_seconds']
        if result['cumulative_ui_seconds'] > 60:
            result['status'] = 'FAIL'
            result['error'] = 'Cumulative UI budget exceeded'
        (OUT / 'delivery/browser-result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
        assert sum(p.stat().st_size for p in (OUT / 'delivery').iterdir()) < 2_400_000
        print(json.dumps(result))
    if result['status'] != 'PASS_SELECTED_BUNDLE_TASKS_ONLY':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
