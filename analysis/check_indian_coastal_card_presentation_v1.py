"""Cloud-only display check using a saved candidate and its unchanged WASM."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from urllib.parse import quote
import urllib.request

import indian_coastal_card_presentation_v1 as presentation
import indian_coastal_delivery_receipts_v1 as delivery

OUTPUT = Path(__file__).resolve().parents[1] / '.pytest_cache/indian-coastal-card-presentation-v1'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', type=Path)
    parser.add_argument('--audit', type=Path)
    args = parser.parse_args()
    if (os.environ.get('GITHUB_ACTIONS') != 'true' or args.site is None or args.audit is None
            or os.environ.get('GITHUB_REF') != 'refs/heads/' + delivery.BRANCH):
        parser.error('Explicit saved-site cloud check required; no files or browser opened')
    if hasattr(os, 'sched_getaffinity'):
        os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
        os.nice(5)
    site, audit = args.site.resolve(), args.audit.resolve()
    load = lambda path: json.loads((audit / path).read_bytes())
    delivery.verify_run(load('run.json'), load('jobs.json'))
    sys.path.insert(0, str(site / 'analysis'))
    import indian_coastal_dimension_context_v1 as context
    contract, contract_sha = context.evidence()
    hashes = {path: context.pin(path) for path in contract['source_documents']}
    delivery.verify_receipts(load('source/result.json'), load('browser/result.json'),
                             load('prior-cards/result.json'), hashes)
    engine_path = presentation.local_path(site, presentation.MANIFEST)
    engine_raw = engine_path.read_bytes()
    parent_engine = json.loads(engine_raw)
    presentation.verify_files(site, parent_engine)
    control = Path(__file__).resolve().parents[1]
    ui_raw = (control / presentation.UI).read_bytes()
    updated = presentation.overlay_manifest(parent_engine, ui_raw,
        parent_manifest_sha=presentation.digest(engine_raw), source_run_id=delivery.SOURCE_RUN,
        control_commit=os.environ['GITHUB_SHA'])
    (site / presentation.UI).write_bytes(ui_raw)
    engine_path.write_bytes(presentation.encoded(updated))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    receipt = {'schema': 'osw.indian-coastal-card-presentation.result.v1', 'status': 'RUNNING',
               'source_run_id': delivery.SOURCE_RUN, 'source_commit': delivery.SOURCE_COMMIT,
               'presentation_control_commit': os.environ['GITHUB_SHA'],
               'presentation_run_id': int(os.environ['GITHUB_RUN_ID']),
               'bundle_sha256': delivery.PACKET, 'contract_sha256': contract_sha,
               'parent_engine_manifest_sha256': presentation.digest(engine_raw),
               'presentation_engine_manifest_sha256': presentation.digest(engine_path.read_bytes()),
               'wasm_sha256': updated['sha256']['almanac/query-engine.wasm'],
               'display_sha256': presentation.digest(ui_raw), 'wasm_cards': [],
               'phone_viewports': [], 'record_queries': 0, 'source_documents': [], 'keyboard_queries': [],
               'native_validation_inherited_from_source_run': delivery.SOURCE_RUN,
               'native_rebuild': False, 'wasm_rebuild': False, 'scientific_source_recomputation': False,
               'packet_or_index_modified': False, 'working_packet_installed': False}
    def checkpoint(phase):
        receipt['phase'] = phase
        (OUTPUT / 'result.json').write_bytes(presentation.encoded(receipt))
        print(phase, flush=True)
    checkpoint('saved-engine-and-upstream-native-proof-verified')
    from playwright.sync_api import expect, sync_playwright
    from test_rust_query_browser import browser_query
    server = subprocess.Popen([sys.executable, '-m', 'http.server', '8788', '--bind', '127.0.0.1',
                               '--directory', str(site)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    errors, originals = [], []
    try:
        base = 'http://127.0.0.1:8788'
        for attempt in range(100):
            if server.poll() is not None:raise RuntimeError('Dedicated saved-site server exited')
            try:
                with urllib.request.urlopen(base + '/almanac/object.html', timeout=2) as response:
                    assert response.read() == (site / 'almanac/object.html').read_bytes()
                break
            except (OSError, TimeoutError):time.sleep(0.1)
        else:raise RuntimeError('Dedicated saved-site server did not become ready')
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(viewport={'width': 1100, 'height': 950})
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('request', lambda request: originals.append(request.url)
                if request.url.split('?')[0].endswith(('.pdf', '.zip', '.nc', '.npz')) else None)
            try:
                for entity, collection, section_id in [
                    (context.EACC, 'current_regional_reaches', '#current-regional-reach'),
                    (context.SJC, 'current_cross_shore_context', '#current-cross-shore-context'),
                ]:
                    checkpoint('card-' + entity)
                    row = contract['additions'][collection][0]
                    page.goto(base + '/almanac/object.html?id=' + quote(entity))
                    page.wait_for_function('window.oswObjectView?.id === ' + json.dumps(entity), timeout=180000)
                    view = page.evaluate('window.oswObjectView')
                    assert view['ok'] and view['bundle_sha256'] == delivery.PACKET
                    assert [r for r in view['collections'][collection] if r['id'] == row['id']] == [row]
                    section = page.locator(section_id)
                    if entity == context.EACC:
                        texts = ['About 1000 km', 'near 11°S', 'near 3°S', 'theoretical-transit', 'unranked',
                                 'Printed/PDF page 27, left column, final paragraph before section 9']
                    else:
                        texts = ['10–15 km', 'SST-associated coastal confinement', row['geographic_scope'],
                                 row['proxy_note'], '2004, 2005, 2006', '1986-2008', 'describes 22 years',
                                 'Abstract, printed 140/PDF 2', 'Section 4, printed 150/PDF 12',
                                 'Figure 10 and discussion, printed 152/PDF 14']
                    for text in texts:expect(section).to_contain_text(text)
                    source = next(item for item in contract['additions']['sources'] if item['id'] == row['source_id'])
                    expect(section.locator('a').filter(has_text=source['title'])).to_have_attribute('href', source['url'])
                    assert section.inner_text().count(source['title']) == 1
                    for width in [320, 390]:
                        checkpoint(entity + '-phone-' + str(width))
                        page.set_viewport_size({'width': width, 'height': 844})
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                        assert section.evaluate('node => node.scrollWidth <= node.clientWidth + 1')
                        section.screenshot(path=str(OUTPUT / (entity.split(':')[1] + '-' + str(width) + 'px.png')))
                        receipt['phone_viewports'].append({'entity_id': entity, 'width_px': width})
                    link = section.get_by_role('link', name='Evidence and source details', exact=True)
                    link.focus()
                    assert link.evaluate('node => document.activeElement === node')
                    page.keyboard.press('Enter')
                    page.wait_for_function('window.oswLastQueryResult', timeout=180000)
                    assert page.evaluate('window.oswLastQueryResult.rows') == [row]
                    receipt['keyboard_queries'].append(entity)
                    receipt['wasm_cards'].append(entity)
                for collection, rows in contract['additions'].items():
                    for row in rows:
                        checkpoint('record-' + row['id'])
                        query = {'collection': collection, 'filters': [{'field': 'id', 'op': 'eq', 'value': row['id']}], 'limit': 1}
                        actual = browser_query(page, query)
                        assert actual['total'] == 1 and actual['rows'] == [row]
                        receipt['record_queries'] += 1
                checkpoint('current-coverage-catalogue-from-exact-saved-candidate')
                actual = browser_query(page, {'collection': 'objects', 'record_type': 'named_current', 'limit': 500})
                assert actual['total'] == 106 and len(actual['rows']) == 106
                assert len({row['id'] for row in actual['rows']}) == 106
                coverage = {'schema': 'osw.current-coverage-catalogue.snapshot.v1',
                            'source_run_id': delivery.SOURCE_RUN, 'bundle_sha256': delivery.PACKET,
                            'scope': 'Query metadata only; capabilities and record IDs are not whole-current measurement completeness.',
                            'currents': 106, 'new_measurements': 0,
                            'records': [{key: row.get(key) for key in presentation.COVERAGE_FIELDS} for row in actual['rows']]}
                coverage_raw = presentation.encoded(coverage)
                (OUTPUT / 'current-coverage-catalogue.json').write_bytes(coverage_raw)
                receipt['current_coverage_catalogue_sha256'] = presentation.digest(coverage_raw)
                receipt['current_coverage_catalogue_records'] = 106
                for index, path in enumerate(contract['source_documents']):
                    checkpoint('source-' + path)
                    query = {'document': path, 'pointer': '', 'limit': 500, 'offset': 0}
                    if index == 0:
                        page.goto(base + '/almanac/query.html?source-q=' + quote(json.dumps(query)))
                    else:
                        page.locator('#source-query-panel details').first.evaluate('node => node.open = true')
                        page.locator('#source-query-json').fill(json.dumps(query))
                        page.evaluate('window.oswSourceQueryResult = null')
                        page.locator('#source-query-run-json').click()
                    page.wait_for_function('window.oswSourceQueryResult', timeout=180000)
                    actual = page.evaluate('window.oswSourceQueryResult')
                    assert {r['source_key']: r['record'] for r in actual['rows']} == json.loads((site / path).read_bytes())
                    receipt['source_documents'].append({'path': path, 'sha256': hashes[path]})
                assert not errors, errors
                assert not originals, originals
            finally:
                browser.close()
        checkpoint('verify-unchanged-data-and-wasm-after-render')
        presentation.validate_overlay(parent_engine, updated)
        assert json.loads(engine_path.read_bytes()) == updated
        presentation.verify_files(site, updated)
        for path in [presentation.UI, presentation.MANIFEST]:
            target = OUTPUT / 'overlay' / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(site / path, target)
        receipt.update(status='PASS', errors=errors, original_downloads=originals)
        checkpoint('presentation-verified-not-installed')
    except Exception as error:
        receipt.update(status='FAIL', error=str(error), errors=errors, original_downloads=originals)
        checkpoint(receipt.get('phase', 'preflight'))
        raise
    finally:
        server.terminate()
        try:server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill();server.wait(timeout=5)


if __name__ == '__main__':
    main()
