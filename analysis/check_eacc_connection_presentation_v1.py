"""Cloud-only saved-engine check for the EACC regional-connection diagram."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request

import eacc_connection_presentation_v1 as method

ROOT = Path(__file__).resolve().parents[1]
REQUEST = 'research/eacc-connection-presentation-request-v1.json'
PREFLIGHT = 'research/eacc-connection-presentation-preflight-v1.json'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if (os.environ.get('GITHUB_ACTIONS') != 'true' or
            os.environ.get('GITHUB_REF') != 'refs/heads/codex/current-measurement-gaps'
            or args.site is None or args.output is None):
        parser.error('Explicit cloud site and output required; no saved data or browser opened')
    request = json.loads((ROOT/REQUEST).read_bytes())
    if (request['execute'] is not True or request['base_commit'] != method.BASE
            or request['parent_engine_manifest_sha256'] != method.PARENT_MANIFEST
            or request['native_rebuild'] is not False or request['wasm_rebuild'] is not False
            or request['new_scientific_records'] != 0 or request['max_local_heavy_jobs'] != 0
            or request['max_cloud_heavy_jobs'] != 1):
        parser.error('Presentation execution not requested within reviewed scope')
    if hasattr(os, 'sched_getaffinity'):
        os.sched_setaffinity(0, {min(os.sched_getaffinity(0))}); os.nice(10)
    pins = json.loads((ROOT/PREFLIGHT).read_bytes())['input_sha256']
    for path, digest in pins.items():
        if method.digest((ROOT/path).read_bytes()) != digest:
            raise ValueError('Changed frozen presentation input: '+path)
    site = args.site.resolve(); output = args.output.resolve()
    engine_path = site/method.MANIFEST
    raw = engine_path.read_bytes()
    if method.digest(raw) != method.PARENT_MANIFEST:
        raise ValueError('Changed installed parent engine')
    parent = json.loads(raw)
    if parent['sha256']['almanac/query-engine.wasm'] != method.WASM:
        raise ValueError('Changed inherited WASM')
    method.verify_files(site, parent)
    contract = json.loads((site/'research/indian-coastal-dimension-context-query-contract-v1.json').read_bytes())
    expected = contract['additions']['current_regional_reaches'][0]
    ui = (ROOT/method.UI).read_bytes(); figure = (ROOT/method.FIGURE).read_bytes()
    updated = method.overlay(parent, ui, figure, control_commit=os.environ['GITHUB_SHA'])
    (site/method.UI).write_bytes(ui); (site/method.FIGURE).write_bytes(figure)
    engine_path.write_bytes(method.encoded(updated))
    output.mkdir(parents=True, exist_ok=True)
    receipt = {'schema': 'osw.eacc-connection-presentation.result.v1', 'status': 'RUNNING',
               'base_commit': method.BASE, 'control_commit': os.environ['GITHUB_SHA'],
               'run_id': os.environ['GITHUB_RUN_ID'], 'parent_manifest_sha256': method.PARENT_MANIFEST,
               'packet_sha256': method.PACKET, 'wasm_sha256': method.WASM,
               'screenshots': [], 'data_or_wasm_changed': False, 'new_scientific_records': 0,
               'native_rebuild': False, 'wasm_rebuild': False, 'installed': False}
    def save(phase):
        receipt['phase'] = phase
        (output/'result.json').write_bytes(method.encoded(receipt)); print(phase, flush=True)
    save('exact-parent-verified-presentation-overlaid')
    errors = []
    server = subprocess.Popen([sys.executable, '-m', 'http.server', '8788', '--bind', '127.0.0.1',
                               '--directory', str(site)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            if server.poll() is not None: raise RuntimeError('Saved-site server exited')
            try:
                with urllib.request.urlopen('http://127.0.0.1:8788/almanac/object.html', timeout=2) as response:
                    assert response.read() == (site/'almanac/object.html').read_bytes()
                break
            except OSError: time.sleep(0.1)
        else: raise RuntimeError('Saved-site server unavailable')
        from playwright.sync_api import sync_playwright, expect
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(viewport={'width': 390, 'height': 844})
            page.on('pageerror', lambda error: errors.append(str(error)))
            try:
                page.goto('http://127.0.0.1:8788/almanac/object.html?id=current%3Aeast-african-coastal')
                page.wait_for_function('window.oswObjectView?.id === "current:east-african-coastal"', timeout=180000)
                view = page.evaluate('window.oswObjectView')
                assert view['ok'] and view['bundle_sha256'] == method.PACKET
                assert [r for r in view['collections']['current_regional_reaches'] if r['id'] == expected['id']] == [expected]
                section = page.locator('#current-regional-reach')
                image = section.locator('img')
                expect(image).to_have_count(1)
                expect(image).to_have_attribute('src', '../'+method.FIGURE)
                image.scroll_into_view_if_needed()
                page.wait_for_function('document.querySelector("#current-regional-reach img")?.naturalWidth > 0')
                expect(section).to_contain_text('no measurement or geographic route')
                for width in [320,390]:
                    page.set_viewport_size({'width': width, 'height': 844})
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                    assert section.evaluate('node => node.scrollWidth <= node.clientWidth + 1')
                    name = 'eacc-regional-connection-'+str(width)+'px.png'
                    section.screenshot(path=str(output/name))
                    receipt['screenshots'].append({'path': name, 'width': width, 'sha256': method.digest((output/name).read_bytes())})
                link = section.get_by_role('link', name='Evidence and source details', exact=True)
                link.focus(); page.keyboard.press('Enter')
                page.wait_for_function('window.oswLastQueryResult', timeout=180000)
                assert page.evaluate('window.oswLastQueryResult.rows') == [expected]
                receipt['keyboard_exact_query'] = True
                assert not errors, errors
            finally: browser.close()
    finally:
        server.terminate(); server.wait(timeout=10)
    method.validate(parent, updated)
    method.verify_files(site, updated)
    for path in [method.UI, method.FIGURE, method.MANIFEST]:
        target = output/path; target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((site/path).read_bytes())
    receipt['manifest_sha256'] = method.digest(engine_path.read_bytes())
    receipt['status'] = 'PASS'; save('browser-and-unchanged-engine-verified')


if __name__ == '__main__': main()
