"""Cloud-only UI diagnostic of the checked-in candidate, without rebuilding data."""
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
OUT = ROOT / '.pytest_cache/public-preview-ui-v3'


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def main():
    assert os.environ.get('GITHUB_ACTIONS') == 'true', 'Cloud only'
    assert len(os.sched_getaffinity(0)) == 1 and os.getpriority(os.PRIO_PROCESS, 0) >= 15
    assert not OUT.exists(), 'Fresh output required; preserve prior diagnostics'
    OUT.mkdir(parents=True)
    result = {'schema': 'osw.public-preview-ui-review.v3', 'status': 'INCOMPLETE',
              'source_commit': os.environ['GITHUB_SHA'], 'scientific_pipeline_run': False,
              'data_rebuilt': False, 'publication_approved': False, 'pages': [], 'failures': [], 'prior_active_seconds': 45.587, 'shared_question_limit_seconds': 60}
    start = time.monotonic()
    server = None

    class SharedDeadline(Exception):
        pass

    def deadline(*_args):
        raise SharedDeadline('Remaining 13-second shared UI diagnostic budget exhausted')

    signal.signal(signal.SIGALRM, deadline)
    signal.alarm(13)
    try:
        # Custody only: hash bytes, do not decode scientific collections.
        bundle = ROOT / 'site-review/ocean-motion-screened'
        manifest = json.loads((bundle / 'site-manifest.json').read_bytes())
        for name in ('index.html', 'styles.css', 'app.js', 'footprint-view.js'):
            assert (ROOT / 'almanac/screened-atlas' / name).read_bytes() == (bundle / name).read_bytes(), name
        expected = {r['path'] for r in manifest['files']} | {'site-manifest.json'}
        actual = {p.relative_to(bundle).as_posix() for p in bundle.rglob('*') if p.is_file()}
        assert actual == expected, 'Bundle membership differs from manifest'
        for row in manifest['files']:
            with (bundle / row['path']).open('rb') as stream:
                assert hashlib.file_digest(stream, 'sha256').hexdigest() == row['sha256'], row['path']
        result['screened_bundle_byte_integrity'] = 'PASS'

        from playwright.sync_api import sync_playwright
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
        Thread(target=server.serve_forever, daemon=True).start()
        base = f'http://127.0.0.1:{server.server_port}'
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(reduced_motion='reduce', viewport={'width': 1280, 'height': 900})
            # Do not contact source providers during a UI check.
            context.route('**/*', lambda route: route.continue_() if route.request.url.startswith(base + '/') else route.abort())
            page = context.new_page()
            specs = [
                ('screened', '/site-review/ocean-motion-screened/', '#object-rows tr', '#objects'),
            ]
            for name, path, ready, focus in specs:
                row = {'name': name, 'route': path, 'errors': [], 'http_failures': [], 'request_failures': []}
                result['pages'].append(row)
                on_error = lambda error, row=row: row['errors'].append(str(error)[:400])
                on_response = lambda response, row=row: row['http_failures'].append(response.url.removeprefix(base)[:200]) if response.status >= 400 else None
                on_request_failure = lambda request, row=row: row['request_failures'].append({'url':request.url.removeprefix(base)[:140], 'failure':str(request.failure)[:160]}) if len(row['request_failures']) < 12 else None
                page.on('requestfailed', on_request_failure)
                page.on('pageerror', on_error)
                page.on('response', on_response)
                try:
                    response = page.goto(base + path, wait_until='domcontentloaded', timeout=3000)
                    assert response and response.ok, 'Page unavailable'
                    page.locator(ready).first.wait_for(state='attached', timeout=3000)
                    assert page.get_by_role('main').count() == 1, 'Missing or duplicate main landmark'
                    assert page.get_by_role('heading', level=1).count() == 1, 'Missing or duplicate page title'
                    if name == 'screened':
                        page.locator('#search').fill('Gulf Stream')
                        page.locator('#object-rows a').first.click(timeout=3000)
                        row['selected_label'] = page.locator('#record-title').inner_text()
                        assert 'Gulf Stream' in row['selected_label'], 'Wrong search result opened: ' + row['selected_label']
                        assert page.evaluate("document.activeElement.id === 'record-title'"), 'Record focus was lost'
                        assert 'id=' in page.url, 'Record does not have a shareable URL'
                        row['record_deep_link_and_focus'] = 'PASS'
                        page.reload(wait_until='domcontentloaded')
                        page.locator('#record-title').filter(has_text='Gulf Stream').wait_for(timeout=5000)
                        row['record_reload'] = 'PASS'
                    for width in (1280, 390):
                        page.set_viewport_size({'width': width, 'height': 900 if width == 1280 else 844})
                        page.locator('#objects-title').evaluate("node => node.scrollIntoView({block:'start'})")
                        if width == 390:
                            assert page.locator('#object-rows tr').first.evaluate("node => getComputedStyle(node).display === 'grid'"), 'Mobile directory is not stacked'
                            assert page.locator('#object-rows td a').first.bounding_box()['height'] >= 44, 'Current link touch target too small'
                            assert page.get_by_role('table', name='Source-set object directory').count() == 1, 'Table semantics missing'
                            row['mobile_stacked_records_and_touch_target'] = 'PASS'
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), f'Page overflow at {width}px'
                        page.screenshot(path=str(OUT / f'{name}-{width}.png'), animations='disabled', timeout=3000)
                    row['desktop_and_narrow_no_page_overflow'] = 'PASS'
                    row['status'] = 'PASS' if not row['errors'] and not row['http_failures'] else 'FAIL'
                except SharedDeadline:
                    raise
                except Exception as error:
                    row['status'] = 'FAIL'
                    row['failure'] = type(error).__name__ + ': ' + str(error)[:600]
                finally:
                    row['visible_status'] = page.locator('#coverage, #route-atlas-status, #dashboard-status, #query-inventory, #query-status').evaluate_all('(nodes) => nodes.map(n => ({id:n.id,text:n.innerText.slice(0,500)}))')
                    if row.get('status') == 'FAIL':
                        try:
                            page.screenshot(path=str(OUT / f'{name}-failure.png'), animations='disabled', timeout=1500)
                        except Exception:
                            pass
                    page.remove_listener('requestfailed', on_request_failure)
                    page.remove_listener('pageerror', on_error)
                    page.remove_listener('response', on_response)
            browser.close()
        assert len(result['pages']) == 1 and all(r['status'] == 'PASS' for r in result['pages']), 'Candidate UI checks need fixes'
        result['status'] = 'PASS_UI_DIAGNOSTIC_ONLY'
    except Exception as error:
        result['failures'].append(str(error)[:800])
        result['status'] = 'FAIL'
    finally:
        signal.alarm(0)
        if server:
            server.shutdown()
        result['active_seconds'] = round(time.monotonic() - start, 3)
        result['remaining_reviews'] = ['public source-use reconciliation', 'full navigation and accessibility',
                                       'first-time visitor comprehension', 'selected deployment bundle and hosted target']
        for image in sorted(OUT.glob('*.png')):
            if sum(p.stat().st_size for p in OUT.iterdir() if p.is_file()) > 2300000:
                image.unlink()  # Do not publish an oversized evidence packet.
        (OUT / 'result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
        print(json.dumps({'status': result['status'], 'pages': len(result['pages']), 'active_seconds': result['active_seconds']}))
    if result['status'] != 'PASS_UI_DIAGNOSTIC_ONLY':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
