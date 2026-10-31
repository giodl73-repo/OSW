"""Native current check before one browser; source page loads no raw archive."""
import json
import os
from pathlib import Path
import subprocess

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BASE = 'http://127.0.0.1:8788'


def main():
    output = ROOT/'.pytest_cache/caribbean-ru29-2026/browser'
    output.mkdir(parents=True, exist_ok=True)
    query = {'collection': 'length_assessments',
             'filters': [{'field': 'entity_id', 'op': 'eq', 'value': 'current:caribbean'}], 'limit': 10}
    cli = ROOT/'rust/osw-query/target/debug/osw-query-cli.exe'
    if not cli.exists():
        cli = cli.with_suffix('')
    native = subprocess.run([str(cli), 'almanac/query-data.json', '-'], cwd=ROOT,
                            input=json.dumps(query), capture_output=True, text=True, encoding='utf8', check=True)
    native_result = json.loads(native.stdout)
    assert native_result['total'] == 1
    (output/'native-before-browser.json').write_text(native.stdout, encoding='utf8')
    return browser_check(output)


def browser_check(output):
    expected = json.loads((ROOT/'research/caribbean-ru29-source-inventory-v2.json').read_bytes())
    requests, errors = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        try:
            page = browser.new_page(viewport={'width': 1280, 'height': 1000})
            page.on('request', lambda request: requests.append(request.url))
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(BASE+'/almanac/caribbean-source.html')
            expect(page.locator('#inventory-status')).to_have_text('12 of 12 fields · adcp-transect-1.nc')
            assert page.locator('#member option').count() == len(expected['members']) == 11
            assert page.locator('#fields tr').count() == 12
            assert page.locator('img').evaluate('(image) => image.complete && image.naturalWidth === 1100')
            assert not any(url.endswith('caribbean-ru29-source-page-v1.json') for url in requests)
            page.locator('#cell-reader > summary').focus()
            page.keyboard.press('Enter')
            expect(page.locator('#cell-latitude option')).to_have_count(97)
            expect(page.locator('#cell-depth option')).to_have_count(100)
            source = json.loads((ROOT/'research/caribbean-ru29-source-page-v1.json').read_bytes())
            for n in [0, 1]:
                page.locator('#cell-occupation').select_option(str(n))
                page.locator('#cell-latitude').select_option('48')
                page.locator('#cell-depth').select_option('25')
                expect(page.locator('#cell-result')).to_contain_text(f'Occupation {n+1}')
                fields = source['occupations'][n]['source_group']['variables']
                text = page.locator('#cell-result').inner_text()
                import re
                values = re.findall(r'([\d.e+-]+) m/s', text)
                expected_values = [abs(fields[key]['raw_values'][25][48]) for key in ['u_grid', 'v_grid']]
                assert len(values) == 2
                for value, expected_value in zip(values, expected_values):
                    assert abs(float(value)-expected_value) <= max(expected_value*5e-7, 1e-12)
            page.screenshot(path=str(output/'desktop.png'), full_page=True)
            page.locator('#member').select_option('sla-anticyclonic-correspondances.nc')
            expect(page.locator('#fields tr')).to_have_count(55)
            page.locator('#field-filter').fill('effective_radius')
            expect(page.locator('#fields tr')).to_have_count(2)
            assert 'LastVirtualObs' in page.locator('#fields').inner_text()
            assert 'LastPreviousVirtualObs' in page.locator('#fields').inner_text()
            page.locator('#field-filter').focus()
            page.keyboard.press('Control+A')
            page.keyboard.type('no such source variable')
            expect(page.locator('#fields tr')).to_have_count(0)
            page.locator('#field-filter').fill('')
            page.locator('#member').select_option('adcp-transect-2.nc')
            expect(page.locator('#fields tr')).to_have_count(12)
            page.set_viewport_size({'width': 320, 'height': 900})
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            assert page.locator('.chart-scroll').evaluate('(element) => element.scrollWidth > element.clientWidth')
            page.locator('.chart-scroll').focus()
            page.keyboard.press('ArrowRight')
            page.screenshot(path=str(output/'phone.png'), full_page=True)
            assert not errors, errors
            assert not any(url.split('?')[0].endswith(('.nc', '.zip', '.pdf', 'caribbean-ru29-source-fields-v2.json')) for url in requests)
        finally:
            browser.close()
    receipt = {'status': 'PASS', 'native_before_browser': True, 'one_browser_page': True,
               'source_files': 11, 'nested_fields': 55, 'raw_originals_or_full_mirror_downloaded': False,
               'lazy_numeric_cell_reader_both_components_and_occupations': True,
               'desktop_and_320px_verified': True, 'page_errors': errors}
    (output/'result.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf8')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
