"""First-map and record task checks against the new display package, cloud only."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
import os
from pathlib import Path
import signal
from threading import Thread
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.pytest_cache/public-map-browser-usability-v1'


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def main():
    assert os.environ.get('GITHUB_ACTIONS') == 'true'
    assert len(os.sched_getaffinity(0)) == 1 and os.getpriority(os.PRIO_PROCESS, 0) >= 15
    assert not OUT.exists()
    OUT.mkdir(parents=True)
    started = time.monotonic()
    result = {'schema': 'osw.public-map-browser.v1', 'status': 'FAIL', 'source_commit': os.environ['GITHUB_SHA'],
              'prior_ui_diagnostic_seconds': 52.575666276, 'shared_ui_diagnostic_limit_seconds': 60,
              'page_errors': [], 'http_failures': [], 'full_research_requests': [], 'checks': [],
              'source_use_approved': False, 'public_preview_complete': False}
    server = None

    def deadline(*_args):
        raise TimeoutError('Remaining UI diagnostic budget exhausted')

    signal.signal(signal.SIGALRM, deadline)
    signal.alarm(6)
    try:
        package = ROOT / 'almanac/display-data-v1'
        build = json.loads((package / 'build.json').read_bytes())
        for row in build['files']:
            raw = (package / row['path']).read_bytes()
            assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256']
        result['checks'].append('All installed display files match cloud export receipts')
        from playwright.sync_api import sync_playwright
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT)))
        Thread(target=server.serve_forever, daemon=True).start()
        base = f'http://127.0.0.1:{server.server_port}'
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1280, 'height': 900}, reduced_motion='reduce')
            page.context.grant_permissions(['clipboard-read', 'clipboard-write'])
            page.set_default_timeout(1800)
            page.on('pageerror', lambda error: result['page_errors'].append(str(error)[:500]))
            page.on('response', lambda response: result['http_failures'].append(response.url.removeprefix(base)) if response.status >= 400 else None)
            page.on('request', lambda request: result['full_research_requests'].append(request.url.removeprefix(base)) if any(p in request.url for p in ['query-engine.wasm', 'query-data.json', 'query-parts/', 'index-data.json.gz']) else None)
            ready_start = time.monotonic()
            page.goto(base + '/almanac/public-map.html?atlas-feature=current%3Aagulhas', wait_until='domcontentloaded')
            page.wait_for_function("document.querySelector('#record-name').textContent.includes('Agulhas') && document.querySelector('#record-content a')")
            result['first_map_and_card_seconds'] = time.monotonic() - ready_start
            assert page.locator('#feature-choice option').count() == 112, 'Not all 111 current identities are available'
            assert page.locator('#ocean-features path').count() > 50, 'Routes did not render'
            assert page.locator('#ocean-map').evaluate('s => s.viewBox.baseVal.width < 1480'), 'Current selection did not zoom'
            result['checks'].append('All 111 current names, route geometry, and initial Agulhas map card render')
            page.locator('.quick-guide summary').click()
            assert page.get_by_text('Read its card.', exact=True).is_visible()
            page.locator('.quick-guide summary').click()
            assert page.get_by_role('heading', name='What this map shows', exact=True).is_visible()
            assert page.locator('.evidence-group').count() > 0
            assert page.locator('.evidence-group').first.get_attribute('open') is not None
            assert page.locator('.citation a').count() > 0
            page.get_by_role('button', name='Copy view link', exact=True).click()
            page.wait_for_function("document.querySelector('#share-status').textContent.startsWith('View link copied')")
            assert page.evaluate('navigator.clipboard.readText()') == page.locator('#share-view').get_attribute('href')
            result['checks'].append('First-visit guide, plain map meaning, expandable evidence, inline source links, and selected-view clipboard link')
            page.get_by_role('link', name='Back to the world map', exact=True).click()
            assert page.locator('#ocean-map').evaluate('s => s.viewBox.baseVal.width === 1480')
            page.get_by_role('button', name='Zoom in', exact=True).click()
            assert page.locator('#ocean-map').evaluate('s => s.viewBox.baseVal.width < 1480')
            page.locator('#ocean-map').focus()
            page.keyboard.press('Home')
            assert page.locator('#ocean-map').evaluate('s => s.viewBox.baseVal.width === 1480')
            page.locator('#feature-choice').select_option('current:kuroshio')
            page.wait_for_function("document.querySelector('#record-name').textContent.includes('Kuroshio') && document.querySelector('#record-content a')")
            assert page.evaluate("document.activeElement.id === 'record-name'"), 'Selection focus was lost'
            assert 'current%3Akuroshio' in page.url
            page.go_back(wait_until='domcontentloaded')
            page.wait_for_function("document.querySelector('#record-name').textContent.includes('Agulhas') && document.querySelector('#record-content a')")
            page.reload(wait_until='domcontentloaded')
            page.wait_for_function("document.querySelector('#record-name').textContent.includes('Agulhas') && document.querySelector('#record-content a')")
            result['checks'].append('World return, zoom controls, keyboard Home, selection focus, browser Back, and record reload')
            page.locator('#feature-search').fill('not-a-real-current-name-123')
            assert page.locator('#feature-choice option').count() == 1
            assert 'No matching names' in page.locator('#search-status').inner_text()
            page.get_by_role('button', name='Clear search', exact=True).click()
            assert page.evaluate("document.activeElement.id === 'feature-search'")
            assert page.locator('#feature-choice option').count() == 112
            page.locator('#feature-kind').select_option('named_eddy')
            assert page.locator('#feature-choice option').count() == 137
            page.locator('#feature-kind').select_option('operational_eddy_detection')
            assert page.locator('#feature-choice option').count() == 5
            page.locator('#feature-kind').select_option('named_current')
            result['checks'].append('Empty search recovery and complete current, named-eddy, and dated-detection selectors')
            page.locator('h1').evaluate("n => n.scrollIntoView({block:'start'})")
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
            page.screenshot(path=str(OUT / 'atlas-desktop.png'), animations='disabled')
            page.set_viewport_size({'width': 390, 'height': 844})
            page.locator('#feature-choice').select_option('current:kuroshio')
            page.wait_for_function("document.querySelector('#record-name').textContent.includes('Kuroshio') && document.querySelector('#record-content a')")
            assert page.locator('#record-name').bounding_box()['y'] >= 0
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
            page.screenshot(path=str(OUT / 'atlas-mobile-card.png'), animations='disabled')
            page.get_by_role('link', name='Back to the world map', exact=True).click()
            page.screenshot(path=str(OUT / 'atlas-mobile-map.png'), animations='disabled')
            result['checks'].append('Desktop and narrow layout, mobile card reveal, and return to map')
            assert not result['page_errors'] and not result['http_failures'] and not result['full_research_requests']
            browser.close()
        result['status'] = 'PASS_FAST_MAP_TASKS_ONLY'
    except Exception as error:
        result['error'] = type(error).__name__ + ': ' + str(error)[:1200]
    finally:
        signal.alarm(0)
        if server:
            server.shutdown()
        result['active_seconds'] = time.monotonic() - started
        result['cumulative_ui_diagnostic_seconds'] = result['prior_ui_diagnostic_seconds'] + result['active_seconds']
        if result['cumulative_ui_diagnostic_seconds'] > result['shared_ui_diagnostic_limit_seconds']:
            result['status'] = 'FAIL'
            result['error'] = 'Cumulative UI budget exceeded'
        (OUT / 'result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
        assert sum(p.stat().st_size for p in OUT.iterdir()) < 1_400_000
        print(json.dumps(result))
    if result['status'] != 'PASS_FAST_MAP_TASKS_ONLY':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
