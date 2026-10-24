"""Actual candidate: native/store parity and readable source-scoped current cards."""
import json
import os
from pathlib import Path
import subprocess
from urllib.parse import quote
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get('OSW_RESEARCH_EVIDENCE_BASE', 'http://127.0.0.1:8788')
CLI = ROOT / 'rust/osw-query/target/debug' / ('osw-query-cli.exe' if os.name == 'nt' else 'osw-query-cli')
CASES = ['west-india-coastal', 'east-india-coastal', 'east-african-coastal', 'south-java', 'brazil']


def native(*args, query=None):
    result = subprocess.run([str(CLI), 'almanac/query-data.json', *args], cwd=ROOT,
        input=json.dumps(query) if query is not None else None, capture_output=True,
        text=True, encoding='utf-8')
    assert result.returncode == 0, result.stderr
    value = json.loads(result.stdout)
    assert value['ok'], value
    return value


def main():
    output = ROOT / '.pytest_cache/current-gap-admission/browser'
    output.mkdir(parents=True, exist_ok=True)
    expected = {slug: native('--object-view', 'current:' + slug) for slug in CASES}
    query = {'collection':'objects','filters':[{'field':'type','op':'eq','value':'named_current'}],'limit':500}
    currents = native('-', query=query)
    assert len(currents['rows']) == 106
    assert all(row['linked_source_count'] == len(row['source_ids']) for row in currents['rows'])
    seasons = native('--seasons')
    decisions = {row['current_id']: row for row in seasons['admitted_current_decisions']}
    for slug in CASES[:4]:
        assert len(decisions[slug]['measurement_ids']) == (1 if slug == 'east-india-coastal' else 0)
        assert not seasons['phase_plans'][slug]['can_play']
        assert decisions[slug]['annual_width_range_km'] is None
    errors, originals = [], []
    progress = {'native_candidate':True,'native_wasm_cards':[],'keyboard_evidence_query':False,
                'dashboard_all_currents':False,'dashboard_modes':[]}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page = browser.new_page(viewport={'width':1200,'height':900})
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda request: originals.append(request.url)
                if request.url.split('?')[0].endswith(('.pdf','.zip','.npz','.nc')) else None)
        try:
            for slug in CASES:
                page.goto(BASE + '/almanac/object.html?id=' + quote('current:' + slug))
                page.wait_for_function('window.oswObjectView?.id === ' + json.dumps('current:' + slug), timeout=180000)
                assert page.evaluate('window.oswObjectView') == expected[slug]
                expect(page.locator('#object-summary')).to_have_attribute('data-engine','rust-osw-query-v1')
                if slug == 'west-india-coastal':
                    rows = page.locator('#current-direction-calendar tbody tr')
                    expect(rows).to_have_count(12)
                    expect(rows.nth(0)).to_contain_text('Northward')
                    expect(rows.nth(3)).to_contain_text('Southward')
                    for index in [2,9]: expect(rows.nth(index)).to_contain_text('Not specified by this source')
                    expect(page.locator('#current-survey-regime')).to_contain_text('1994-03-06 to 1994-03-21')
                if slug == 'east-india-coastal':
                    articles = page.locator('#current-reported-widths article')
                    expect(articles).to_have_count(3)
                    expect(articles.nth(0)).to_contain_text('Admitted as a scoped published width summary')
                    expect(articles.nth(0)).to_contain_text('2013-12-23 to 2013-12-24')
                    for index in [1,2]: expect(articles.nth(index)).to_contain_text('no separate canonical width admitted')
                    expect(page.locator('#current-reported-widths')).to_contain_text('annual minimum, maximum or uncertainty range')
                    page.set_viewport_size({'width':390,'height':844})
                    page.locator('#current-reported-widths').evaluate("element => element.scrollIntoView({block:'start'})")
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                    page.screenshot(path=str(output / 'eicc-scoped-width-phone.png'))
                    page.set_viewport_size({'width':1200,'height':900})
                if slug == 'east-african-coastal':
                    rows = page.locator('#current-direction-calendar tbody tr')
                    expect(rows).to_have_count(12)
                    for index in range(12): expect(rows.nth(index)).to_contain_text('Northward')
                    expect(page.locator('#current-cross-shore-context dt')).to_have_count(4)
                    expect(page.locator('#current-cross-shore-context')).to_contain_text('20–90 km')
                    expect(page.locator('#current-cross-shore-context')).to_contain_text('160–200 km')
                if slug == 'south-java':
                    expect(page.locator('#current-direction-calendar')).to_have_count(0)
                    expect(page.locator('#current-reported-widths')).to_have_count(0)
                    expect(page.locator('#current-cross-shore-context dt')).to_have_count(1)
                    expect(page.locator('#current-cross-shore-context')).to_contain_text('SST-associated coastal confinement')
                    expect(page.locator('#current-cross-shore-context')).to_contain_text('10–15 km')
                if slug == 'brazil':
                    expect(page.locator('#current-regional-reach')).to_contain_text('1500 km')
                    expect(page.locator('#current-regional-reach')).to_contain_text('unranked')
                progress['native_wasm_cards'].append(slug)
            # Exercise the source query from a real card with keyboard activation.
            page.goto(BASE + '/almanac/object.html?id=current%3Awest-india-coastal')
            target = page.locator('#current-direction-calendar').get_by_role('link',name='Evidence and source details')
            target.focus(); page.keyboard.press('Enter')
            page.wait_for_function('window.oswLastQueryResult', timeout=180000)
            assert page.evaluate('window.oswLastQueryResult.rows') == expected['west-india-coastal']['collections']['current_direction_calendars']
            progress['keyboard_evidence_query'] = True
            page.goto(BASE + '/almanac/dashboard.html')
            page.wait_for_function('window.oswDashboardSelection', timeout=180000)
            page.locator('#dashboard-type').select_option('named_current')
            page.wait_for_function('window.oswDashboardSelection.request.record_type === "named_current"')
            expect(page.locator('#dashboard-grid .motion-card')).to_have_count(106)
            progress['dashboard_all_currents'] = True
            page.locator('#dashboard-metric').select_option('direction_descriptions')
            page.locator('#dashboard-search').fill('WICC')
            page.wait_for_function('window.oswDashboardSelection.request.text === "WICC" && window.oswDashboardSelection.request.metric === "direction_descriptions"')
            selection = page.evaluate('window.oswDashboardSelection')
            assert selection['result'] == native('--dashboard-query', query=selection['request'])
            assert selection['result']['ids'] == ['current:west-india-coastal']
            page.locator('#dashboard-card-view').click()
            expect(page.locator('#dashboard-grid .motion-card.lit')).to_have_count(1)
            expect(page.locator('#dashboard-grid')).to_contain_text('12 records')
            page.screenshot(path=str(output / 'dashboard-source-lights.png'),full_page=True)
            page.locator('#dashboard-search').fill('')
            page.locator('#dashboard-covered').check()
            for metric, ids in [
                ('direction_descriptions', ['current:east-african-coastal','current:west-india-coastal']),
                ('reported_width_evidence', ['current:east-india-coastal']),
                ('cross_shore_context', ['current:east-african-coastal','current:south-java']),
                ('regime_context', ['current:west-india-coastal']),
            ]:
                page.locator('#dashboard-metric').select_option(metric)
                page.wait_for_function('([metric]) => window.oswDashboardSelection.request.metric === metric && window.oswDashboardSelection.request.covered_only && window.oswDashboardSelection.request.text === ""', arg=[metric])
                assert sorted(page.evaluate('window.oswDashboardSelection.result.ids')) == ids
                expect(page.locator('#dashboard-grid .motion-card.lit')).to_have_count(len(ids))
                progress['dashboard_modes'].append(metric)
            assert not errors, errors
            assert not originals, originals
        except Exception as error:
            (output / 'failure.json').write_text(json.dumps({'error':str(error),'url':page.url,
                'body':page.locator('body').inner_text()[:16000],'errors':errors,'completed':progress},indent=2)+'\n',encoding='utf-8')
            page.screenshot(path=str(output / 'failure.png'))
            raise
        finally:
            browser.close()
    (output / 'result.json').write_text(json.dumps({'status':'PASS','named_currents':106,
        'bundle_sha256':expected['east-india-coastal']['bundle_sha256'],
        'native_wasm_object_views_equal':CASES,'source_scoped_widths':3,
        'qualitative_calendar_months':24,'scoped_t24_width_records':1,
        'raw_width_samples_added':0,'annual_width_ranges_added':0,
        'keyboard_evidence_query':True,'phone_horizontal_overflow':False,
        'dashboard_all_106_currents':True,'dashboard_alias_native_wasm_parity':True,
        'source_context_coverage_modes_verified':4,
        'original_downloads':originals,'errors':errors},indent=2)+'\n',encoding='utf-8')
    print('PASS106-current candidate, five native/WASM cards, scoped widths and qualitative calendars')


if __name__ == '__main__':
    main()
