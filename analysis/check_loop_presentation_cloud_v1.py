"""Review the two small static-page assets in one cloud-only browser case."""
import argparse
import hashlib
import http.server
import json
import os
from pathlib import Path
import subprocess
import threading

ROOT = Path(__file__).resolve().parents[1]
REQUEST = 'research/loop-presentation-browser-request-v1.json'
PREFLIGHT = 'research/loop-presentation-browser-preflight-v1.json'
OUTPUT = ROOT / '.pytest_cache/loop-presentation-browser-v1'


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def read(path):
    return json.loads((ROOT / path).read_bytes())


def controls():
    if (os.environ.get('GITHUB_ACTIONS') != 'true' or os.environ.get('RUNNER_OS') != 'Linux'
            or os.environ.get('GITHUB_REPOSITORY') != 'giodl73-repo/OSW'
            or os.environ.get('GITHUB_REF') != 'refs/heads/codex/current-measurement-gaps'
            or os.environ.get('GITHUB_EVENT_NAME') != 'push'):
        raise ValueError('Exact working-branch cloud case required; local browser work refused')
    assert len(os.sched_getaffinity(0)) == 1
    assert os.getpriority(os.PRIO_PROCESS, 0) >= 15
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    assert head == os.environ['GITHUB_SHA']
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT).strip()
    request = read(REQUEST)
    assert request['schema'] == 'osw.loop-presentation-browser-request.v1'
    assert request['execution_permitted'] is True
    assert request['browser_only'] is True
    for key in ['native_build_permitted', 'wasm_build_permitted', 'packet_load_permitted',
                'source_index_load_permitted', 'scientific_processing_permitted',
                'installation_permitted', 'main_merge_permitted']:
        assert request[key] is False, key
    assert digest(PREFLIGHT) == request['preflight_sha256']
    preflight = read(PREFLIGHT)
    for path, sha in preflight['input_sha256'].items():
        assert digest(path) == sha, path
    for name in preflight['preserve_inventories']:
        for path, sha in read(name)['input_sha256'].items():
            assert digest(path) == sha, path
    for name in preflight['disabled_requests']:
        assert read(name)['execution_permitted'] is False, name
    assert read('research/current-gap-delivery-phase.json')['heavy_work_permitted'] is False
    return head


def main():
    head = controls()  # Refuse before importing Playwright or reading page contents locally.
    from playwright.sync_api import sync_playwright

    OUTPUT.mkdir(parents=True, exist_ok=False)
    revision = read('research/loop-published-metrics-presentation-revision-v1.json')
    page_path = revision['candidate_path']
    assert digest(page_path) == revision['candidate_sha256']
    assert digest(revision['original_path']) == revision['original_sha256']
    figure = 'figures/loop-manta-2023-published-metrics-v1.svg'
    assets = {'/' + page_path, '/' + figure}
    errors, forbidden, requested, screenshots, layouts = [], [], [], [], []

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path not in assets:
                self.send_error(404)
                return
            data = (ROOT / self.path[1:]).read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8' if self.path.endswith('.html') else 'image/svg+xml')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *_):
            pass

    server = http.server.HTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = 'http://127.0.0.1:' + str(server.server_port)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--disable-dev-shm-usage'])
            context = browser.new_context(viewport={'width': 320, 'height': 900}, device_scale_factor=1)
            page = context.new_page()
            page.on('pageerror', lambda error: errors.append(str(error)))

            def route_request(route):
                url = route.request.url
                requested.append(url.removeprefix(origin))
                if url in {origin + a for a in assets}:
                    route.continue_()
                else:
                    forbidden.append(url)
                    route.abort()

            page.route('**/*', route_request)
            for width in [320, 390]:
                page.set_viewport_size({'width': width, 'height': 900})
                response = page.goto(origin + '/' + page_path, wait_until='networkidle')
                assert response.status == 200
                assert page.locator('time').count() == 12
                assert page.locator('.length-summary tbody tr').count() == 2
                assert page.locator('.length-summary tbody td').all_text_contents() == ['1,449 km', '487 km', '1,495 km', '466 km']
                assert 'integration pending' not in page.locator('.status').inner_text()
                assert page.locator('img').evaluate('(img)=>img.complete && img.naturalWidth>0')
                layout = page.evaluate('''() => ({viewport: innerWidth,
                    scrollWidth: document.documentElement.scrollWidth,
                    rows: Array.from(document.querySelectorAll('.length-summary tbody tr')).map(r=>({
                        display:getComputedStyle(r).display,
                        methodWidth:r.querySelector('th').getBoundingClientRect().width,
                        rowWidth:r.getBoundingClientRect().width,
                        labels:Array.from(r.querySelectorAll('td')).map(c=>getComputedStyle(c,'::before').content)
                    }))})''')
                assert layout['scrollWidth'] <= width
                assert all(r['display'] == 'grid' and abs(r['methodWidth'] - r['rowWidth']) < 1
                           and r['labels'] == ['"Mean"', '"Temporal SD"'] for r in layout['rows'])
                layouts.append(layout)
                file = OUTPUT / f'loop-presentation-{width}px.png'
                page.screenshot(path=str(file), full_page=True)
                raw = file.read_bytes()
                screenshots.append({'path': file.name, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
            context.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    assert not errors and not forbidden
    result = {'schema': 'osw.loop-presentation-browser-result.v1', 'status': 'PASS',
              'source_commit': head, 'run_id': os.environ['GITHUB_RUN_ID'],
              'run_attempt': os.environ['GITHUB_RUN_ATTEMPT'], 'page_sha256': revision['candidate_sha256'],
              'original_page_unchanged': True, 'layouts': layouts, 'screenshots': screenshots,
              'requested_assets': requested, 'page_errors': errors, 'forbidden_requests': forbidden,
              'browser_verified': True, 'visual_review_complete': False,
              'packet_or_index_loaded': False, 'compiled': False, 'installed': False}
    (OUTPUT / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'screenshots': len(screenshots)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cloud-browser', action='store_true', required=True)
    parser.parse_args()
    main()
