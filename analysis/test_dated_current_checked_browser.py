"""Standalone dates, local section scope, checked loading and image alignment."""
import json,os,subprocess
from datetime import date
from urllib.parse import parse_qs,urlparse
from playwright.sync_api import sync_playwright,expect
from test_rust_query_browser import ROOT,CLI
from test_rust_atlas_snapshot_browser import route_atlas_bundle

BASE='http://127.0.0.1:8788/almanac/dated-current.html'
WIDTHS='research/gulf-stream-section-width-series.json'


def main():
    native=json.loads(subprocess.check_output([str(CLI),str(ROOT/'almanac/query-data.json'),'--atlas'],encoding='utf-8'))
    docs={path:json.loads(raw) for path,raw in native['sources_json'].items()}
    widths={r['date']:r for r in docs[WIDTHS]['frames']}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1200,'height':1000});errors=[];direct=[]
        page.set_default_timeout(90000)
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.route('**/research/*.json',lambda r:(direct.append(r.request.url),r.fulfill(status=503,body='Direct reads disabled'))[-1])
        page.goto(BASE+'?series=2025&date=2025-08-15')
        expect(page.locator('#dated-value')).to_contain_text('2025-08-15',timeout=90000)
        assert page.evaluate('window.oswCheckedAtlasSnapshot')==native
        for year,path in [('2025','research/ocean-current-dated-timeline-2025.json'),('2026','research/ocean-current-dated-timeline.json')]:
            page.locator('#dated-series').select_option(year)
            frames=docs[path]['frames']
            expect(page.locator('#dated-phase option')).to_have_count(len(frames))
            expect(page.locator('#dated-phase')).to_be_enabled()
            for i,frame in enumerate(frames):
                page.locator('#dated-phase').select_option(str(i))
                expect(page.locator('#dated-value')).to_contain_text(frame['date'])
                assert parse_qs(urlparse(page.url).query)=={'series':[year],'date':[frame['date']]}
                expect(page.locator('#dated-map')).to_be_visible()
                expect(page.locator('#dated-map')).to_have_attribute('data-sample-date',frame['date'])
                assert page.locator('#dated-map').get_attribute('src')=='../'+frame['figure']
                assert frame['source_algorithm'] in page.locator('#dated-version').inner_text()
                assert page.locator('#dated-source a').get_attribute('href')==frame['source_url']
                assert page.locator('#dated-scenario-rows tr').count()==len(frame['diagnostic_sensitivity']['scenarios'])
                assert [r.inner_text().split(':')[0] for r in page.locator('#dated-state-list a').all()]==[r['state_code'] for r in frame['state_relations']]
                assert str(widths[frame['date']]['approximate_section_span_km'])+' km' in page.locator('#dated-width').inner_text()
                assert 'not a whole-current length' in page.locator('#dated-value').inner_text()
                assert 'not statistical uncertainty' in page.locator('#dated-width-range').inner_text()
                assert 'not annual extrema' in page.locator('#dated-width-samples').inner_text()
                if i:
                    days=(date.fromisoformat(frame['date'])-date.fromisoformat(frames[i-1]['date'])).days
                    assert f'{days} calendar day' in page.locator('#dated-gap').inner_text()
        # A delayed old image must not replace a newer selected frame.
        frames=docs['research/ocean-current-dated-timeline.json']['frames'];held=[]
        slow=browser.new_page();slow.set_default_timeout(90000)
        slow.on('pageerror',lambda e:errors.append(str(e)))
        slow.route('**/research/*.json',lambda r:(direct.append(r.request.url),r.fulfill(status=503,body='Direct reads disabled'))[-1])
        pattern='**/'+frames[1]['figure'].split('/')[-1]
        slow.route(pattern,lambda r:held.append(r))
        slow.goto(BASE+'?series=2026&date='+frames[4]['date'])
        expect(slow.locator('#dated-map')).to_have_attribute('data-sample-date',frames[4]['date'],timeout=90000)
        slow.locator('#dated-phase').select_option('1')
        expect(slow.locator('#dated-map')).to_be_hidden()
        expect(slow.locator('#dated-map-status')).to_contain_text('Loading selected')
        assert held
        slow.locator('#dated-phase').select_option('2')
        expect(slow.locator('#dated-map')).to_have_attribute('data-sample-date',frames[2]['date'])
        held.pop().fulfill(body=(ROOT/frames[1]['figure']).read_bytes(),content_type='image/svg+xml')
        slow.unroute(pattern)
        expect(slow.locator('#dated-map')).to_have_attribute('data-sample-date',frames[2]['date'])
        slow.close()
        page.clock.install()
        page.locator('#dated-phase').select_option('0');page.locator('#dated-play').click();page.clock.run_for(2201)
        assert page.locator('#dated-phase').input_value()=='1'
        page.locator('#dated-play').click();page.clock.run_for(4400)
        assert page.locator('#dated-phase').input_value()=='1'
        page.locator('#dated-play').click();page.locator('#dated-phase').select_option('3');page.clock.run_for(4400)
        assert page.locator('#dated-phase').input_value()=='3'
        page.locator('#dated-play').click()
        page.evaluate("Object.defineProperty(document,'hidden',{configurable:true,value:true});document.dispatchEvent(new Event('visibilitychange'))")
        page.clock.run_for(4400);assert page.locator('#dated-phase').input_value()=='3'
        page.set_viewport_size({'width':320,'height':900})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        restored=browser.new_page();restored.goto(page.url)
        expect(restored.locator('#dated-value')).to_contain_text(frames[3]['date'],timeout=90000)
        assert restored.locator('#dated-series').input_value()=='2026'
        assert restored.locator('#dated-phase').input_value()=='3'
        restored.close()
        for kind in ['load_failure','missing_widths']:
            other=browser.new_page();other.on('pageerror',lambda e:errors.append(str(e)))
            if kind=='load_failure':other.route('**/query-data.json',lambda r:r.fulfill(status=503,body='Unavailable'))
            else:
                bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes())
                del bundle['manifest']['atlas_receipts'][WIDTHS];route_atlas_bundle(other,bundle)
            other.goto(BASE)
            expect(other.locator('#dated-status')).to_contain_text('HTTP 503' if kind=='load_failure' else 'Checked dated evidence unavailable',timeout=90000)
            assert other.locator('#dated-play').is_disabled() and other.locator('#dated-phase').is_disabled()
            assert other.locator('#dated-map').is_hidden() and other.locator('#dated-state-list li').count()==0
        assert not direct and not errors,(direct,errors)
        browser.close()
    print('PASS: 17 checked standalone dates, native/WASM snapshot, source widths/states/gaps, playback controls, stale image protection, mobile and unavailable data')


if __name__=='__main__':main()
