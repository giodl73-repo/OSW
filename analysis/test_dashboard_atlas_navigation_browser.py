"""Dashboard identity links open the selected mapped atlas card."""
import json
import os
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from playwright.sync_api import sync_playwright
from test_motion_dashboard_browser import settle

ROOT = Path(__file__).resolve().parents[1]
BASE = 'http://127.0.0.1:8788/almanac/'


def main():
    entries = json.loads((ROOT / 'research/ocean-motion-dashboard.json').read_text(encoding='utf-8'))['entries']
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'), headless=True)
        page = browser.new_page(viewport={'width':1200, 'height':950})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(BASE + 'dashboard.html', wait_until='networkidle')
        page.wait_for_function('window.oswDashboardSnapshot',timeout=90000)
        settle(page)
        page.wait_for_function('document.querySelectorAll(".motion-card").length===240')
        links = page.locator('.motion-card').evaluate_all('''cards => cards.map(card => ({
            id:card.dataset.id, href:card.querySelector('h3 a').getAttribute('href'),
            record:card.querySelector('details > a').getAttribute('href')
        }))''')
        by_id = {entry['id']: entry for entry in entries}
        assert len(links) == len(by_id)
        for link in links:
            url = urlparse(link['href'])
            assert url.path == 'reference-routes.html' and url.fragment == 'route-atlas'
            assert parse_qs(url.query)['atlas-feature'] == [link['id']]
            assert link['record'] == by_id[link['id']]['object_url']
        for feature_id in ['current:portugal', next(entry['id'] for entry in entries if entry['type']=='operational_eddy_detection')]:
            entry = by_id[feature_id]
            page.locator('#dashboard-search').fill(entry['label'])
            settle(page)
            page.locator('#dashboard-schematic-view').click()
            if entry['type']=='named_current':
                page.locator('.beck-station').focus()
                page.keyboard.press('Enter')
                heading = page.locator('#dashboard-schematic-detail h4 a')
                assert parse_qs(urlparse(heading.get_attribute('href')).query)['atlas-feature'] == [feature_id]
            page.locator('#dashboard-card-view').click()
            page.locator(f'.motion-card[data-id="{feature_id}"] h3 a').click()
            page.wait_for_function('document.querySelectorAll(".atlas-directory-item").length===240')
            selector = '#route-atlas-select' if entry['type']=='named_current' else '#route-atlas-eddy-select'
            page.wait_for_function('(args)=>document.querySelector(args[0]).value===args[1]', arg=[selector,feature_id])
            assert entry['label'] in page.locator('#route-atlas-preview h3').inner_text()
            assert page.locator('#route-atlas-map').get_attribute('viewBox') != '60 90 1480 740'
            page.reload(wait_until='networkidle')
            page.wait_for_function('(args)=>document.querySelector(args[0]).value===args[1]', arg=[selector,feature_id])
            assert page.locator('#route-atlas-preview').is_visible()
            page.locator('#route-atlas-world').click()
            assert page.locator('#route-atlas-map').get_attribute('viewBox') == '60 90 1480 740'
            assert page.locator('#route-atlas-preview').is_hidden()
            page.goto(BASE + 'dashboard.html', wait_until='networkidle')
            page.wait_for_function('window.oswDashboardSnapshot',timeout=90000)
            settle(page)
        assert not errors, errors
        browser.close()
    print('OK: all 240 dashboard name links target atlas cards; object records retained; current and dated eddy selection, reload and World verified')


if __name__ == '__main__':
    main()
