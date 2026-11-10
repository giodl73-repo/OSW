"""Cloud gate for exact coastal context, source queries and accessible cards."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from urllib.parse import quote

from playwright.sync_api import expect, sync_playwright
import indian_coastal_dimension_context_v1 as context
from test_rust_query_browser import browser_query, native
from test_current_research_evidence_browser import native as source_native

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get('OSW_RESEARCH_EVIDENCE_BASE', 'http://127.0.0.1:8788')
OUTPUT = ROOT / '.pytest_cache/indian-coastal-context-browser'


def main():
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('Cloud browser gate only; local browser automation remains held')
    document, contract_sha = context.evidence()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    errors, originals = [], []
    receipt = {'status': 'RUNNING', 'contract_sha256': contract_sha,
               'native_wasm_cards': [], 'record_queries': 0, 'source_documents': [],
               'phone_widths_verified': [], 'keyboard_queries': [], 'new_physical_measurements': 0}
    def save():
        (OUTPUT / 'result.json').write_bytes(context.encoded(receipt))
    save()
    cli = ROOT / 'rust/osw-query/target/debug/osw-query-cli'
    phase = 'native-views'
    views = {}
    for entity in [context.EACC, context.SJC]:
        result = subprocess.run([str(cli), 'almanac/query-data.json', '--object-view', entity],
                                cwd=ROOT, capture_output=True, text=True, check=True)
        view = json.loads(result.stdout)
        assert view['ok'] and view['id'] == entity
        views[entity] = view
    with sync_playwright() as pw, TemporaryDirectory(dir=OUTPUT) as folder:
        browser = pw.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page = browser.new_page(viewport={'width': 1100, 'height': 950})
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda request: originals.append(request.url)
                if request.url.split('?')[0].endswith(('.pdf', '.zip', '.nc', '.npz')) else None)
        try:
            for entity, collection, section_id, value in [
                (context.EACC, 'current_regional_reaches', '#current-regional-reach', 'About 1000 km'),
                (context.SJC, 'current_cross_shore_context', '#current-cross-shore-context', '10–15 km'),
            ]:
                phase = 'card-' + entity
                row = document['additions'][collection][0]
                page.goto(BASE + '/almanac/object.html?id=' + quote(entity))
                page.wait_for_function('window.oswObjectView?.id === ' + json.dumps(entity), timeout=180000)
                assert page.evaluate('window.oswObjectView') == views[entity]
                assert [r for r in views[entity]['collections'][collection] if r['id'] == row['id']] == [row]
                section = page.locator(section_id)
                expect(section).to_contain_text(value)
                expect(section).to_contain_text('not' if entity == context.SJC else 'unranked')
                if entity == context.EACC:
                    expect(section).to_contain_text('theoretical-transit')
                    expect(section).to_contain_text('near 11°S')
                    expect(section).to_contain_text('near 3°S')
                    expect(section).to_contain_text('Printed/PDF page 27, left column, final paragraph before section 9')
                else:
                    for text in [row['geographic_scope'], row['proxy_note'], 'SST-associated coastal confinement',
                                 '2004, 2005, 2006', 'describes 22 years',
                                 'Abstract, printed 140/PDF 2', 'Section 4, printed 150/PDF 12',
                                 'Figure 10 and discussion, printed 152/PDF 14']:
                        expect(section).to_contain_text(text)
                source = next(r for r in document['additions']['sources'] if r['id'] == row['source_id'])
                expect(section.locator('a').filter(has_text=source['title'])).to_have_attribute('href', source['url'])
                assert section.inner_text().count(source['title']) == 1
                for width in [320, 390]:
                    phase = entity + '-phone-' + str(width)
                    page.set_viewport_size({'width': width, 'height': 844})
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                    assert section.evaluate('node => node.scrollWidth <= node.clientWidth + 1')
                    section.screenshot(path=str(OUTPUT / (entity.split(':')[1] + '-' + str(width) + 'px.png')))
                    receipt['phone_widths_verified'].append({'entity_id': entity, 'width_px': width})
                phase = entity + '-keyboard-query'
                link = section.get_by_role('link', name='Evidence and source details', exact=True)
                link.focus()
                assert link.evaluate('node => document.activeElement === node')
                page.keyboard.press('Enter')
                page.wait_for_function('window.oswLastQueryResult', timeout=180000)
                assert page.evaluate('window.oswLastQueryResult.rows') == [row]
                receipt['keyboard_queries'].append(entity)
                receipt['native_wasm_cards'].append(entity)
            for collection, rows in document['additions'].items():
                for row in rows:
                    phase = 'record-' + row['id']
                    query = {'collection': collection, 'filters': [{'field': 'id', 'op': 'eq', 'value': row['id']}], 'limit': 1}
                    actual = browser_query(page, query)
                    assert actual == native(query) and actual['total'] == 1 and actual['rows'] == [row]
                    receipt['record_queries'] += 1
            phase = 'physical-inventory'
            for query, total in [
                ({'collection': 'widths', 'limit': 500}, 172),
                ({'collection': 'length_assessments', 'filters': [{'field': 'rank_eligible', 'op': 'eq', 'value': True}], 'limit': 100}, 13),
                ({'collection': 'objects', 'record_type': 'named_current', 'limit': 500}, 106),
            ]:
                actual = browser_query(page, query)
                assert actual == native(query) and actual['total'] == total
            phase = 'preserved-source-index'
            index = Path(folder) / 'index.json'
            index.write_bytes(gzip.decompress((ROOT / 'almanac/index-data.json.gz').read_bytes()))
            for path in document['source_documents']:
                phase = 'source-' + path
                raw = (ROOT / path).read_bytes()
                query = {'document': path, 'pointer': '', 'limit': 500, 'offset': 0}
                page.goto(BASE + '/almanac/query.html?source-q=' + quote(json.dumps(query)))
                page.wait_for_function('window.oswSourceQueryResult', timeout=180000)
                actual = page.evaluate('window.oswSourceQueryResult')
                assert actual == source_native(query, index=index)
                assert {r['source_key']: r['record'] for r in actual['rows']} == json.loads(raw)
                receipt['source_documents'].append({'path': path, 'sha256': hashlib.sha256(raw).hexdigest()})
            assert not errors, errors
            assert not originals, originals
            receipt.update(status='PASS', bundle_sha256=views[context.EACC]['bundle_sha256'],
                           errors=errors, original_downloads=originals)
        except Exception as error:
            receipt.update(status='FAIL', phase=phase, error=str(error), url=page.url, errors=errors, original_downloads=originals)
            raise
        finally:
            save()
            browser.close()


if __name__ == '__main__':
    main()
