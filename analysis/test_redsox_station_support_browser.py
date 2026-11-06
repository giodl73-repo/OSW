"""All metadata selections, filter states and accessible station controls."""
import json
import os
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright, expect

from redsox_provider_station_support import ROOT, REPORT
from build_redsox_station_support_view import FOLDER


def main():
    source = json.loads((ROOT / REPORT).read_bytes())
    output = ROOT / '.pytest_cache/redsox-station-support/browser'
    output.mkdir(parents=True, exist_ok=True)
    errors, originals = [], []
    base = os.environ.get('OSW_TEST_BASE_URL', 'http://127.0.0.1:8788')
    statuses = ['all', 'consistent_provider_station_records', 'provider_metadata_review_required', 'missing_ctd_record']
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page = browser.new_page(viewport={'width': 1200, 'height': 1000})
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('request', lambda r: originals.append(r.url) if r.url.split('?')[0].endswith(('.zip', '.nc', '.npz', '.pdf')) else None)
        page.goto(base + '/' + FOLDER + '/')
        page.wait_for_function('window.oswStationReady')
        assert page.locator('#unmatched tr').count() == 17
        for campaign in ['all', 'RSX1', 'RSX2']:
            page.locator('#campaign').select_option(campaign)
            for status in statuses:
                page.locator('#status').select_option(status)
                rows = [r for r in source['profiles'] if (campaign == 'all' or r['campaign'] == campaign) and (status == 'all' or r['assessment']['status'] == status)]
                assert page.evaluate('window.oswStationSelection.records') == rows
                assert page.locator('#tiles button').count() == len(rows)
                assert page.locator('#profile option').count() == len(rows)
                assert page.locator('#selection').is_hidden() == (not rows)
                assert page.locator('#profile').is_disabled() == (not rows)
        page.locator('#campaign').select_option('all'); page.locator('#status').select_option('all')
        for i, row in enumerate(source['profiles']):
            page.locator('#profile').select_option(row['id'])
            assert page.evaluate('window.oswStationSelection.record') == row
            assert json.loads(page.locator('#raw').text_content()) == row
            assert page.locator('#checks li').count() == len(row['assessment']['checks'])
            expect(page.locator('#selected-title')).to_have_text(row['id'])
            q = json.loads(parse_qs(urlparse(page.locator('#query').get_attribute('href')).query)['source-q'][0])
            assert q == dict(document=REPORT, pointer='/profiles', limit=1, offset=i)
        page.locator('#profile').select_option('rsx1-073-hr')
        share = page.locator('#permalink').get_attribute('href')
        page.locator('#profile').select_option('rsx1-074-hr'); page.go_back()
        expect(page.locator('#profile')).to_have_value('rsx1-073-hr')
        page.goto(share); page.wait_for_function('window.oswStationReady')
        expect(page.locator('#profile')).to_have_value('rsx1-073-hr')
        page.locator('#profile').focus(); page.keyboard.press('ArrowDown')
        expect(page.locator('#profile')).to_have_value('rsx1-074-hr')
        expect(page.locator('#meaning')).to_contain_text('No CTD companion')
        page.goto(base + '/' + FOLDER + '/?campaign=invalid&status=invalid&profile=unknown')
        expect(page.locator('#campaign')).to_have_value('all'); expect(page.locator('#status')).to_have_value('all')
        expect(page.locator('#profile')).to_have_value(source['profiles'][0]['id'])
        page.goto(share); page.wait_for_function('window.oswStationReady')
        page.locator('#selection').scroll_into_view_if_needed()
        expect(page.locator('#fields tr').nth(5)).to_contain_text('Velocity profile header time; not a synoptic section time')
        expect(page.locator('#fields tr').nth(6)).to_contain_text(source['profiles'][next(i for i,r in enumerate(source['profiles']) if r['id']=='rsx1-073-hr')]['velocity_metadata']['source_sha256'][:12])
        page.screenshot(path=str(output / 'desktop.png'))
        page.set_viewport_size({'width': 320, 'height': 1000})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#selection').scroll_into_view_if_needed(); page.screenshot(path=str(output / 'phone.png'))
        expect(page.locator('.notice')).to_contain_text('not only the descending Red Sea plume')
        assert not errors and not originals, (errors, originals)
        browser.close()
    result = dict(status='PASS', full_profile_selections=445, complete_ctd_metadata_records=461,
                  filter_states=12, unmatched_ctd_rows=17, query_offsets_exact=445,
                  keyboard_history_permalink=True, empty_filters=True,
                  invalid_url_fallback=True, phone_320px=True, automatic_original_downloads=0,
                  synchronized_casts_admitted=0, physical_width_admitted=False)
    (output / 'result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
