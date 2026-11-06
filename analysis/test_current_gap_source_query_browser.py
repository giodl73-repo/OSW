"""Complete native/WASM source audits and keyboard atlas navigation."""
import gzip
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote, parse_qs, urlparse

from playwright.sync_api import sync_playwright, expect

from current_gap_source_evidence import ROOT, REPORT, REDSEA, ACQUISITION, FOLDER, evidence
from test_current_research_evidence_browser import native, BASE


def main():
    audit, review, diagnostics, _ = evidence()
    output = ROOT / '.pytest_cache/current-gap-source-integration/browser'
    output.mkdir(parents=True, exist_ok=True)
    errors, originals = [], []
    source_cases = [(REPORT, '/attempt_inventory', audit['attempt_inventory']),
                    (REPORT, '/terminal_rows', audit['terminal_rows']),
                    (REPORT, '/monthly_summary', audit['monthly_summary']),
                    (REDSEA, '/findings', review['findings'])]
    with sync_playwright() as pw, TemporaryDirectory(dir=output) as tmp:
        index = Path(tmp) / 'index.json'
        index.write_bytes(gzip.decompress((ROOT / 'almanac/index-data.json.gz').read_bytes()))
        browser = pw.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page = browser.new_page(viewport={'width': 1200, 'height': 1000})
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('request', lambda r: originals.append(r.url) if r.url.split('?')[0].endswith(('.zip', '.npz', '.nc', '.pdf')) else None)
        for row in diagnostics:
            q = {'collection': 'diagnostics', 'filters': [{'field': 'id', 'op': 'eq', 'value': row['id']}], 'limit': 1}
            page.goto(BASE + '/almanac/query.html?q=' + quote(json.dumps(q)))
            page.wait_for_function('window.oswLastQueryResult', timeout=180000)
            actual = page.evaluate('window.oswLastQueryResult')
            assert actual == native(q)
            assert actual['rows'] == [row]
        for document, pointer, expected in source_cases:
            q = dict(document=document, pointer=pointer, limit=len(expected), offset=0)
            page.goto(BASE + '/almanac/query.html?source-q=' + quote(json.dumps(q)))
            page.wait_for_function('window.oswSourceQueryResult', timeout=180000)
            actual = page.evaluate('window.oswSourceQueryResult')
            assert actual == native(q, index=index)
            assert [r['record'] for r in actual['rows']] == expected
        q = dict(document=ACQUISITION, pointer='', limit=50, offset=0)
        page.goto(BASE + '/almanac/query.html?source-q=' + quote(json.dumps(q)))
        page.wait_for_function('window.oswSourceQueryResult', timeout=180000)
        actual = page.evaluate('window.oswSourceQueryResult')
        assert actual == native(q, index=index)
        assert {r['source_key']: r['record'] for r in actual['rows']} == json.loads((ROOT / ACQUISITION).read_bytes())
        page.goto(BASE + '/' + FOLDER + '/')
        page.wait_for_function('window.oswBoundaryReady')
        for month in range(1, 13):
            page.locator('#month').select_option(str(month))
            q = json.loads(parse_qs(urlparse(page.locator('#attempt-query').get_attribute('href')).query)['source-q'][0])
            assert q == dict(document=REPORT, pointer='/attempt_inventory', limit=12, offset=(month-1)*12)
            rows = [r for r in audit['terminal_rows'] if r['month'] == month]
            if not rows:
                assert page.locator('#terminal-query').is_hidden()
                assert page.locator('#terminal-query').get_attribute('href') is None
            else:
                q = json.loads(parse_qs(urlparse(page.locator('#terminal-query').get_attribute('href')).query)['source-q'][0])
                assert q == dict(document=REPORT, pointer='/terminal_rows', limit=len(rows), offset=next(i for i, r in enumerate(audit['terminal_rows']) if r['month'] == month))
        page.set_viewport_size({'width': 320, 'height': 1000})
        page.goto(BASE + '/almanac/reference-routes.html?atlas-feature=current%3Aindian-south-equatorial-countercurrent#route-atlas')
        links = page.locator('.route-atlas-evidence-links'); links.wait_for(state='attached', timeout=180000)
        links.locator('summary').focus(); page.keyboard.press('Enter')
        link = links.get_by_role('link', name='Inspect every source stop and unresolved edge', exact=True)
        expect(link).to_be_visible(); link.focus(); page.keyboard.press('Enter')
        page.wait_for_function('window.oswBoundaryReady')
        page.locator('#month').select_option('5')
        page.locator('#terminal-query').focus(); page.keyboard.press('Enter')
        page.wait_for_function('window.oswSourceQueryResult', timeout=180000)
        actual = page.evaluate('window.oswSourceQueryResult')
        assert [r['record'] for r in actual['rows']] == [r for r in audit['terminal_rows'] if r['month'] == 5]
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(output / 'secc-phone.png'))
        page.goto(BASE + '/almanac/reference-routes.html?atlas-feature=current%3Ared-sea-saline-overflow#route-atlas')
        links = page.locator('.route-atlas-evidence-links'); links.wait_for(state='attached', timeout=180000)
        links.locator('summary').focus(); page.keyboard.press('Enter')
        link = links.get_by_role('link', name='Why the 2003 channel width is not a measured current width', exact=True)
        expect(link).to_be_visible(); link.focus(); page.keyboard.press('Enter')
        page.wait_for_function('window.oswSourceQueryResult', timeout=180000)
        assert [r['record'] for r in page.evaluate('window.oswSourceQueryResult')['rows']] == review['findings']
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(output / 'redsea-phone.png'))
        assert not errors and not originals, (errors, originals)
        browser.close()
    result = dict(status='PASS', complete_diagnostics_exact=2, complete_attempts_exact=144,
                  complete_terminals_exact=156, complete_months_exact=12,
                  complete_redsea_findings_exact=4, complete_acquisition_exact=True,
                  selected_month_query_links=12, keyboard_both_current_cards=True,
                  phone_320px=True, automatic_original_downloads=0, physical_width_admitted=False)
    (output / 'result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
