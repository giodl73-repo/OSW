"""Cloud-only layout check using the exact saved Baffin engine and data.

No native build, new source computation, measurement admission or publication.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('Phone layout validation is cloud-only; local browsers remain held')
    if hasattr(os, 'sched_getaffinity'):
        os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
        os.nice(5)
    from playwright.sync_api import sync_playwright, expect
    from probe_current_card_navigation import ROOT, checked_site, prepare_site, verify_artifacts
    from run_rust_query_browser_checks import check_port_available, wait_for_checkout

    output = ROOT / '.pytest_cache/baffin-phone-layout'
    site = checked_site(output / 'site')
    audit = json.loads((output / 'source/result.json').read_bytes())
    bundle = verify_artifacts(site, audit, expected_schema='osw.baffin-bound-candidate.v1')
    assert bundle == 'f1223c576250988055195202823d7f727bbaddfdfb1b6fc76eef7fcb7989f00f'
    prepare_site(site)
    admission = json.loads((ROOT / 'research/baffin-latitude-bound-admission-v1.json').read_bytes())
    scenarios = admission['scenario_records']
    assert len(scenarios) == 9
    check_port_available()
    server = subprocess.Popen([sys.executable, '-m', 'http.server', '8788', '--bind', '127.0.0.1',
                               '--directory', str(site)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    receipt = {'status': 'RUNNING', 'bundle_sha256': bundle, 'upstream_run_id': 40083318018,
               'native_build_performed': False, 'fresh_scientific_validation': False,
               'publication_authorized': False}
    errors, originals = [], []
    try:
        wait_for_checkout(server)
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(viewport={'width': 320, 'height': 844})
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('request', lambda request: originals.append(request.url)
                    if request.url.split('?')[0].endswith(('.pdf', '.zip', '.nc', '.npz')) else None)
            page.goto('http://127.0.0.1:8788/almanac/object.html?id=current%3Abaffin')
            page.wait_for_function('window.oswObjectView?.id === "current:baffin"', timeout=180000)
            section = page.locator('#current-geographic-length-bound')
            image = section.locator('img')
            image.scroll_into_view_if_needed()
            expect(image).to_have_js_property('complete', True)
            assert image.evaluate('node => node.naturalWidth > 0')
            for width in [320, 390]:
                page.set_viewport_size({'width': width, 'height': 844})
                expect(section.locator('tbody tr')).to_have_count(9)
                for row in scenarios:
                    tr = section.locator(f'tr[data-scenario-index="{row["scenario_index"]}"]')
                    expected = [str(row['scenario_index']),
                                *[f'{v:.1f}' for v in row['nominal_latitudes_degrees_north']],
                                f'{row["geographic_separation_km"]:.1f}']
                    assert tr.locator('th,td').all_text_contents() == expected
                assert section.locator('.table-wrap').evaluate(
                    'node => node.scrollWidth <= node.clientWidth + 1'), 'Scenario columns need horizontal scrolling'
                assert section.locator('th,td').evaluate_all(
                    'nodes => nodes.every(n => n.getBoundingClientRect().left >= 0 && '
                    'n.getBoundingClientRect().right <= innerWidth + 1 && n.scrollWidth <= n.clientWidth + 1)')
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                section.screenshot(path=str(output / f'card-{width}px.png'))
            link = section.get_by_role('link', name='Query all nine editorial scenarios', exact=True)
            link.focus()
            page.keyboard.press('Enter')
            page.wait_for_function('window.oswLastQueryResult', timeout=180000)
            assert page.evaluate('window.oswLastQueryResult.rows') == scenarios
            assert not errors and not originals, (errors, originals)
            browser.close()
        receipt.update(status='PASS_SAVED_COHORT_LAYOUT_ONLY', phone_widths=[320, 390],
                       complete_nine_rows_and_four_columns_visible=True, keyboard_query_verified=True,
                       object_html_sha256=hashlib.sha256((ROOT / 'almanac/object.html').read_bytes()).hexdigest())
    except Exception as error:
        receipt.update(status='FAIL', error=type(error).__name__ + ': ' + str(error))
        raise
    finally:
        server.terminate()
        server.wait(timeout=5)
        (output / 'result.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf8')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
