"""Verify independent seasonal regional routes without annual dimensions."""
import hashlib
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    root = Path(__file__).resolve().parents[1]
    snapshot = json.loads((root/'research/ocean-motion-dashboard.json').read_text(encoding='utf-8'))
    row = next(r for r in snapshot['entries'] if r['id'] == 'current:monsoon')
    assert row['capabilities']['reference_route'] == 2
    assert row['capabilities']['scoped_width'] == 0
    assert row['latest_observation_date'] is None
    assert hashlib.sha256((root/'research/ocean-current-almanac.json').read_bytes()).hexdigest() == '6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e'
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=os.environ.get('OSW_TEST_BROWSER', r'C:\Program Files\Google\Chrome\Application\chrome.exe'))
        page = browser.new_page(viewport={'width':1440,'height':1000})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Amonsoon#route-atlas', wait_until='networkidle')
        page.wait_for_function('document.querySelector("#route-atlas-select").value === "current:monsoon"')
        preview = page.locator('#route-atlas-preview')
        assert preview.locator('.route-map').is_visible()
        buttons = preview.locator('button')
        assert buttons.count() == 2
        buttons.nth(1).click()
        assert buttons.nth(1).get_attribute('aria-pressed') == 'true'
        assert row['scope_notes'][0]['summary'] in page.locator('.route-atlas-scope-reviews').inner_text()
        for phase in ['summer','winter']:
            card = page.locator(f'#monsoon-{phase}-sri-lanka-reference-path-candidate')
            assert card.locator('.route-map').count() == 1
            assert '77' in card.inner_text() and '83' in card.inner_text()
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=monsoon', wait_until='networkidle')
        page.wait_for_function('document.querySelector("#season-phase").options.length === 2')
        assert page.locator('#season-play').is_enabled()
        assert 'eastward' in page.locator('#season-value').inner_text()
        assert 'Width: unknown' in page.locator('#season-definition').inner_text()
        assert page.locator('#season-map').is_visible()
        assert 'annual' in page.locator('#season-range').inner_text()
        page.locator('#season-play').click()
        page.wait_for_function('document.querySelector("#season-value").textContent.includes("westward")')
        page.locator('#season-play').click()
        assert 'November' in page.locator('#season-value').inner_text()
        assert 'winter' in page.locator('#season-map').get_attribute('src')
        page.screenshot(path=str(root/'figures/monsoon-seasonal-reach-review.png'), full_page=True)
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.locator('#season-phase').select_option('0')
        assert 'eastward' in page.locator('#season-value').inner_text()
        assert not errors, errors
        browser.close()
    print('OK: two independent Monsoon phases, exact atlas cards, reversal playback, unknown widths/annual ranges, mobile reflow and unchanged ledger')


if __name__ == '__main__':
    main()
