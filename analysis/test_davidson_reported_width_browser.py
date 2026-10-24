"""Cloud-only delivery gate for the admitted Davidson span and actual SVG caption.

Requires the next complete candidate, its matching native/WASM engines and the
existing preview server. This script does not produce or admit source data.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from urllib.parse import quote

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get('OSW_RESEARCH_EVIDENCE_BASE', 'http://127.0.0.1:8788')
ENTITY = 'current:davidson'
WIDTH = 'davidson-wallace-2008-line67-27-59m-reported-span'
FIGURE = 'figures/davidson-wallace-2008-reported-width-v1.svg'
FIGURE_SHA = '48ad6871e4839d9c21809ea2322eac7d8d7081fec2786c0f7877e3af3dc75d67'


def main():
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('Run this delivery gate in the cloud; local browser work is held')
    cli = ROOT / 'rust/osw-query/target/debug/osw-query-cli'
    process = subprocess.run([str(cli), 'almanac/query-data.json', '--object-view', ENTITY],
                             cwd=ROOT, capture_output=True, text=True, check=True)
    native = json.loads(process.stdout)
    assert native['ok'], native
    widths = native['collections']['widths']
    assert len(widths) == 2
    old = next(row for row in widths if row['id'] == 'davidson-historical-winter-width')
    new = next(row for row in widths if row['id'] == WIDTH)
    assert old['approximate_width_km'] == 64 and old['source_publication_year'] == 1978
    assert new['approximate_width_km'] == 65
    assert new['normalized_width_km_decimal'] == '64.82'
    assert new['annual_width_range_km'] is None and not new['seasonal_playback_eligible']
    assert hashlib.sha256((ROOT / FIGURE).read_bytes()).hexdigest() == FIGURE_SHA
    output = ROOT / '.pytest_cache/davidson-reported-width-browser'
    output.mkdir(parents=True, exist_ok=True)
    errors, originals = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page = browser.new_page(viewport={'width':1200,'height':900})
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda request: originals.append(request.url)
                if request.url.split('?')[0].endswith(('.pdf','.zip','.npz','.nc')) else None)
        try:
            page.goto(BASE + '/almanac/object.html?id=' + quote(ENTITY))
            page.wait_for_function('window.oswObjectView?.id === "current:davidson"', timeout=180000)
            assert page.evaluate('window.oswObjectView') == native
            section = page.locator('#current-campaign-widths')
            expect(section.locator('article')).to_have_count(1)
            for text in ['About 65 km', '27–59 m', '2008-01-23 to 2008-01-30',
                         'Exact occupation date unknown', '35 NM', '64.82 km',
                         'Primary course cruise report', 'Peer review and publication date unverified',
                         'No whole-current width, annual range or seasonal animation']:
                expect(section).to_contain_text(text)
            image = section.locator('img')
            image.scroll_into_view_if_needed()
            expect(image).to_have_js_property('complete', True)
            assert image.evaluate('image => image.naturalWidth > 0')
            page.set_viewport_size({'width':390,'height':844})
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
            section.screenshot(path=str(output / 'card-phone.png'))
            target = section.get_by_role('link', name='Evidence and source details', exact=True)
            target.focus(); page.keyboard.press('Enter')
            page.wait_for_function('window.oswLastQueryResult', timeout=180000)
            assert page.evaluate('window.oswLastQueryResult.rows') == [new]
            # Render the immutable SVG directly: its linked caption was omitted
            # by the earlier non-browser preview renderer.
            response = page.goto(BASE + '/' + FIGURE)
            assert hashlib.sha256(response.body()).hexdigest() == FIGURE_SHA
            caption = page.locator('svg a text')
            expect(caption).to_be_visible()
            expect(caption).to_have_text('Wallace · NPS-hosted course report')
            assert page.locator('svg circle.reported-value').count() == 1
            page.screenshot(path=str(output / 'scalar-phone.png'), full_page=True)
            caption.locator('..').focus()
            assert page.evaluate('document.activeElement.localName') == 'a'
            assert not errors, errors
            assert not originals, originals
        finally:
            browser.close()
    (output / 'result.json').write_text(json.dumps({
        'status':'PASS', 'bundle_sha256':native['bundle_sha256'],
        'native_wasm_card_equal':True, 'historical_width_preserved':True,
        'source_scalar_sha256':FIGURE_SHA, 'source_caption_browser_visible':True,
        'keyboard_width_query':True, 'source_link_focusable':True,
        'phone_horizontal_overflow':False, 'original_downloads':originals,
        'errors':errors, 'scientific_release_published':False,
    }, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
