"""Cloud-only source-inventory view gate; no build or original data access."""
import functools
import hashlib
import http.server
import json
import os
from pathlib import Path
import threading


def main():
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('Source viewer browser checks are cloud-only')
    os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
    os.nice(5)
    from playwright.sync_api import sync_playwright, expect
    root = Path(__file__).resolve().parents[1]
    output = root / '.pytest_cache/osnap-source-view-browser'
    output.mkdir(parents=True, exist_ok=True)
    raw = (root / 'research/osnap-wg-2016-2018-source-headers-v1.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == '4c21602907317e827e255a2d167e2e7b0dec2029a7ee3bd80f535ace3b5b8236'
    records = json.loads(raw)['instrument_headers']
    assert len(records) == 78
    expected_members = sorted(record['member'] for record in records)

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(QuietHandler, directory=str(root)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f'http://127.0.0.1:{server.server_port}/almanac/osnap-support.html'
    receipt = {'status': 'RUNNING', 'originals_accessed': False,
               'native_or_wasm_build_performed': False, 'physical_measurements_verified': False}
    errors, unexpected_requests = [], []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(viewport={'width': 1280, 'height': 900}, reduced_motion='reduce')
            page.on('pageerror', lambda error: errors.append(str(error)))

            def restrict(route):
                if route.request.url.startswith(f'http://127.0.0.1:{server.server_port}/'):
                    route.continue_()
                else:
                    unexpected_requests.append(route.request.url)
                    route.abort()
            page.route('**/*', restrict)
            page.goto(url)
            rows = page.locator('#support-instruments > details')
            expect(rows).to_have_count(78)
            assert sorted(rows.locator('dl dd:first-of-type').all_text_contents()) == expected_members
            expect(page.locator('#headers-stage')).to_have_text('Verified · 78 instrument headers')
            expect(page.locator('#samples-stage')).to_have_text('Audited · 78 instrument records')
            expect(page.locator('#timeline-basis')).to_contain_text('declared in file headers')
            for kind, count in [('adcp', 8), ('point', 29), ('hydro', 41), ('all', 78)]:
                page.locator('#support-kind').select_option(kind)
                expect(rows).to_have_count(count)
            for station, count in [('LS1', 3), ('LS4', 8), ('LS8', 19)]:
                page.get_by_role('button', name=f'{station} {count} files').click()
                expect(rows).to_have_count(count)
                page.get_by_role('button', name=f'{station} {count} files').click()
                expect(rows).to_have_count(78)
            for member in [name for name in expected_members if not name.endswith('.nc')]:
                page.locator('#support-search').fill(member)
                expect(rows).to_have_count(1)
                expect(rows.locator('dl dd:first-of-type')).to_have_text(member)
            page.locator('#support-search').fill('no instrument matches this phrase')
            expect(rows).to_have_count(0)
            expect(page.locator('#support-empty')).to_be_visible()
            page.locator('#support-search').fill('')
            expect(rows).to_have_count(78)
            summary = rows.first.locator('summary')
            summary.focus()
            page.keyboard.press('Enter')
            assert rows.first.evaluate('element => element.open')
            expect(rows.first.locator('h3')).to_be_visible()
            expect(rows.first.locator('table.support-months tbody tr')).to_have_count(26)
            assert summary.evaluate('element => element === document.activeElement')
            for width in [320, 390]:
                page.set_viewport_size({'width': width, 'height': 844})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                assert page.locator('#support-moorings button').evaluate_all(
                    'nodes => nodes.every(n => n.getBoundingClientRect().width >= 44 && n.getBoundingClientRect().height >= 44)')
                page.locator('#timeline-title').scroll_into_view_if_needed()
                page.screenshot(path=str(output / f'timeline-{width}px.png'))
            page.set_viewport_size({'width': 1280, 'height': 900})
            page.screenshot(path=str(output / 'overview.png'), full_page=True)

            # A checksum failure must show an error, never a partial verified inventory.
            page.route('**/osnap-wg-2016-2018-source-headers-v1.json', lambda route: route.fulfill(
                status=200, content_type='application/json', body='{}'))
            page.reload()
            expect(page.locator('#support-status')).to_contain_text('size differs')
            expect(rows).to_have_count(0)
            expect(page.locator('#headers-stage')).to_have_text('Not verified in this view')
            assert not errors and not unexpected_requests, (errors, unexpected_requests)
            browser.close()
        receipt.update(status='PASS_HEADER_INVENTORY_VIEW_ONLY', instruments=78,
                       adcp=8, point_velocity=29, hydrography=41,
                       exact_original_member_names_verified=True, extensionless_files_verified=True,
                       keyboard_expand_verified=True, phone_widths=[320, 390],
                       checksum_corruption_rejected=True, sample_audit_label='audited_availability_only')
    except Exception as error:
        receipt.update(status='FAIL', error=str(error))
        raise
    finally:
        server.shutdown();server.server_close();thread.join(timeout=5)
        (output / 'result.json').write_text(json.dumps(receipt, indent=2) + '\n')


if __name__ == '__main__':
    main()
