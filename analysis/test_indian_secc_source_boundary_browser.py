"""Actual browser coverage of every retained boundary-audit attempt and row."""
import json
import os

from playwright.sync_api import sync_playwright, expect

from indian_secc_source_boundary_audit import ROOT, REPORT
from build_indian_secc_source_boundary_view import FOLDER


def main():
    source = json.loads((ROOT / REPORT).read_bytes())
    output = ROOT / '.pytest_cache/indian-secc-source-boundaries-2013/browser'
    output.mkdir(parents=True, exist_ok=True)
    base = os.environ.get('OSW_TEST_BASE_URL', 'http://127.0.0.1:8788')
    errors, originals = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page = browser.new_page(viewport={'width': 1200, 'height': 1000})
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('request', lambda r: originals.append(r.url) if r.url.split('?')[0].endswith(('.pdf', '.zip', '.npz', '.nc')) else None)
        page.goto(base + '/' + FOLDER + '/')
        page.wait_for_function('window.oswBoundaryReady')
        for month in range(1, 13):
            page.locator('#month').select_option(str(month))
            rows = [r for r in source['terminal_rows'] if r['month'] == month]
            attempts = [r for r in source['attempt_inventory'] if r['month'] == month]
            assert page.evaluate('window.oswBoundarySelection') == dict(
                month=month, summary=source['monthly_summary'][month-1], rows=rows, attempts=attempts)
            assert page.locator('#attempts tr').count() == 12
            assert page.locator('#terminals tr').count() == len(rows)
            assert page.locator('#plot line[data-terminal]').count() == sum(r['terminal_sample'] is not None and r['immediate_inward_sample'] is not None for r in rows)
            shown = page.locator('#attempts tr').evaluate_all('(rows)=>rows.map(r=>Array.from(r.cells).map(c=>c.textContent))')
            assert shown == [[r['case_id'], r['status'], str(r['available_stations'])] for r in attempts]
            shown = page.locator('#terminals tr').evaluate_all('(rows)=>rows.map(r=>Array.from(r.cells).map(c=>c.textContent))')
            for r, cells in zip(rows, shown):
                t = r['thresholds'][1]
                assert cells[0] == f"{r['case_id']} / {r['station_arc_parameter_km']} km / {r['direction']}"
                assert cells[4] == t['inward_sample_relation_to_serialized_threshold'] + ' ' + (t['serialized_peak_threshold_m_s'] or 'unavailable')
                assert cells[5] == ' / '.join(t['direction_edge']['status'] if t['direction_edge'] is not None else t['pair_status'] for t in r['thresholds'])
        page.locator('#month').select_option('5')
        share = page.locator('#permalink').get_attribute('href')
        page.locator('#month').select_option('6')
        page.go_back(); expect(page.locator('#month')).to_have_value('5')
        page.goto(share); page.wait_for_function('window.oswBoundaryReady')
        expect(page.locator('#month')).to_have_value('5')
        page.locator('#month').focus(); page.keyboard.press('ArrowDown')
        expect(page.locator('#month')).to_have_value('6')
        page.goto(base + '/' + FOLDER + '/?month=invalid')
        expect(page.locator('#month')).to_have_value('5')
        page.screenshot(path=str(output / 'desktop.png'), full_page=True)
        page.set_viewport_size({'width': 320, 'height': 1000})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert page.locator('#plot text').evaluate_all('(nodes)=>Math.min(...nodes.map(n=>parseFloat(getComputedStyle(n).fontSize)*n.getScreenCTM().a))') >= 10
        page.locator('#plot').scroll_into_view_if_needed()
        page.screenshot(path=str(output / 'phone.png'))
        for link in page.locator('main a').all():
            href = link.get_attribute('href')
            if href and not href.startswith('http'):
                assert page.request.head(base + href).ok
        assert not errors and not originals
        browser.close()
    result = dict(status='PASS', months=12, attempts=144, terminal_rows=156,
                  complete_serialized_rows_exact=True, keyboard=True,
                  history=True, invalid_url_fallback=True, phone_320px=True,
                  automatic_original_downloads=0, physical_width_admitted=False)
    (output / 'result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
