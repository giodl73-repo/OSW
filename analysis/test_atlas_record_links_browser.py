"""Check dashboard and record links preserve atlas feature identity."""
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from playwright.sync_api import sync_playwright


def main():
    snapshot = json.loads(Path('research/ocean-motion-dashboard.json').read_text(encoding='utf-8'))
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
        page = browser.new_page(viewport={'width':1280,'height':900})
        page.goto('http://127.0.0.1:8788/almanac/dashboard.html',wait_until='networkidle')
        cards = page.locator('.motion-card')
        assert cards.count() == len(snapshot['entries'])
        page.locator('#dashboard-card-view').click()
        for row in snapshot['entries']:
            href = page.locator(f'.motion-card[data-id="{row["id"]}"]').get_by_role('link',name='Explore atlas',exact=True).get_attribute('href')
            assert parse_qs(urlparse(href).query)['atlas-feature'] == [row['id']]
        card = page.locator('.motion-card[data-id="current:agulhas"]')
        card.get_by_role('link',name='Explore atlas',exact=True).click()
        page.wait_for_function('document.querySelector("#route-atlas-select").value === "current:agulhas"')
        assert page.locator('#route-atlas-preview .route-map').is_visible()
        page.locator('#route-atlas-preview').get_by_role('link',name='Current record',exact=False).click()
        page.get_by_role('link',name='Explore on the current atlas').click()
        page.wait_for_function('document.querySelector("#route-atlas-select").value === "current:agulhas"')
        # A pending current and a regional eddy retain their actual scope on arrival.
        examples = [next(r for r in snapshot['entries'] if r['id']=='current:west-australian'),
                    next(r for r in snapshot['entries'] if r['type']=='named_eddy' and any(f['role']=='shared_regional_gateway' for f in r['map_features']))]
        for row in examples:
            page.goto('http://127.0.0.1:8788/almanac/'+row['object_url'],wait_until='networkidle')
            page.get_by_role('link',name='Explore on the current atlas').click()
            selector = '#route-atlas-select' if row['type']=='named_current' else '#route-atlas-eddy-select'
            page.wait_for_function('(args)=>document.querySelector(args[0]).value===args[1]',arg=[selector,row['id']])
            status=page.locator('#route-atlas-status').inner_text()
            assert ('no reference-route card yet' if row['type']=='named_current' else 'no individual center or footprint') in status
        browser.close()
    print('OK: all dashboard atlas addresses, current card/record round trip, pending route and shared eddy gateway')


if __name__=='__main__':
    main()
